#!/usr/bin/env python3
"""Verify that the workspace's submodule pins agree with pins.json.

Checks, for every entry in pins.json:
  (a) the gitlink at <path> in the HEAD tree is mode 160000 and its SHA equals
      pinned_sha exactly (never a prefix match);
  (b) .gitmodules has a submodule whose path is <path>, with the recorded url
      and branch, and "update = none" if and only if opt_in;
  (c) with --network, for public entries: the pinned commit can be fetched
      from the remote (git fetch --depth 1 <url> <sha> into a temporary bare
      repository), and an informational line says whether the remote default
      tip still equals the pin ("behind tip" is reported, not failed).
Also fails if the HEAD tree contains a gitlink that pins.json does not list.

Prints a one-line summary and exits nonzero on failure. Standard library only.
This checker is a consistency check on pointers; it does not grade, review or
move the status of anything in the pinned repositories.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

SCHEMA = "ulw.pins.v1"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def run_git(args, cwd=None, check=True):
    proc = subprocess.run(
        ["git"] + list(args), cwd=cwd, capture_output=True, text=True,
        env=dict(os.environ, GIT_TERMINAL_PROMPT="0"),
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            "git %s failed (%d): %s" % (" ".join(args), proc.returncode,
                                         proc.stderr.strip()))
    return proc


def unique_json_object(pairs):
    """Reject ambiguous members after JSON has decoded key escapes."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("pins.json: duplicate JSON member %r" % key)
        result[key] = value
    return result


def load_pins(pins_path):
    with open(pins_path, "r", encoding="utf-8") as fh:
        doc = json.load(fh, object_pairs_hook=unique_json_object)
    errors = []
    if doc.get("schema") != SCHEMA:
        errors.append("pins.json: schema is %r, expected %r"
                      % (doc.get("schema"), SCHEMA))
    repos = doc.get("repos")
    if not isinstance(repos, list) or not repos:
        errors.append("pins.json: 'repos' must be a non-empty list")
        repos = []
    required = ("name", "path", "url", "default_branch", "pinned_sha",
                "public", "opt_in", "note")
    seen_paths = set()
    for i, entry in enumerate(repos):
        for key in required:
            if key not in entry:
                errors.append("pins.json: entry %d missing %r" % (i, key))
        sha = entry.get("pinned_sha", "")
        if not isinstance(sha, str) or not FULL_SHA.match(sha):
            errors.append("pins.json: %s: pinned_sha %r is not a full "
                          "lowercase 40-hex SHA" % (entry.get("path"), sha))
        for key in ("public", "opt_in"):
            if not isinstance(entry.get(key), bool):
                errors.append("pins.json: %s: %r must be a boolean"
                              % (entry.get("path"), key))
        path = entry.get("path")
        if path in seen_paths:
            errors.append("pins.json: duplicate path %r" % path)
        seen_paths.add(path)
    return repos, errors


def head_gitlinks(repo):
    """Map path -> sha for every mode-160000 entry in the HEAD tree."""
    out = run_git(["ls-tree", "-r", "-z", "HEAD"], cwd=repo).stdout
    links = {}
    for rec in out.split("\0"):
        if not rec:
            continue
        meta, path = rec.split("\t", 1)
        mode, otype, sha = meta.split(" ")
        if mode == "160000" and otype == "commit":
            links[path] = sha
    return links


def read_gitmodules(repo):
    """Map submodule path -> {name, url, branch, update} from .gitmodules."""
    gm = os.path.join(repo, ".gitmodules")
    if not os.path.isfile(gm):
        return {}, [".gitmodules is missing"]
    proc = run_git(["config", "-f", gm, "--list", "-z"], cwd=repo)
    sections = {}
    for rec in proc.stdout.split("\0"):
        if not rec:
            continue
        key, _, value = rec.partition("\n")
        if not key.startswith("submodule."):
            continue
        name, _, field = key[len("submodule."):].rpartition(".")
        sections.setdefault(name, {})[field] = value
    by_path = {}
    errors = []
    for name, fields in sections.items():
        path = fields.get("path")
        if path is None:
            errors.append(".gitmodules: submodule %r has no path" % name)
            continue
        if path in by_path:
            errors.append(".gitmodules: path %r declared twice" % path)
        by_path[path] = dict(fields, name=name)
    return by_path, errors


def check_tree_and_modules(repo, repos):
    errors = []
    links = head_gitlinks(repo)
    modules, merrors = read_gitmodules(repo)
    errors.extend(merrors)
    listed = set()
    for entry in repos:
        path = entry.get("path")
        listed.add(path)
        pinned = entry.get("pinned_sha")
        # (a) gitlink present, mode 160000, exact SHA.
        actual = links.get(path)
        if actual is None:
            errors.append("%s: no mode-160000 gitlink in HEAD tree" % path)
        elif actual != pinned:
            errors.append("%s: gitlink %s != pinned_sha %s"
                          % (path, actual, pinned))
        # (b) .gitmodules agreement.
        mod = modules.get(path)
        if mod is None:
            errors.append("%s: not declared in .gitmodules" % path)
            continue
        if mod.get("url") != entry.get("url"):
            errors.append("%s: .gitmodules url %r != pins url %r"
                          % (path, mod.get("url"), entry.get("url")))
        if mod.get("branch") != entry.get("default_branch"):
            errors.append("%s: .gitmodules branch %r != default_branch %r"
                          % (path, mod.get("branch"),
                             entry.get("default_branch")))
        update_none = mod.get("update") == "none"
        opt_in = bool(entry.get("opt_in"))
        if opt_in and not update_none:
            errors.append("%s: opt_in but .gitmodules lacks 'update = none'"
                          % path)
        if update_none and not opt_in:
            errors.append("%s: .gitmodules has 'update = none' but pins "
                          "opt_in is false" % path)
    for path in sorted(set(links) - listed):
        errors.append("%s: gitlink in HEAD tree is not listed in pins.json"
                      % path)
    for path in sorted(set(modules) - listed):
        errors.append("%s: declared in .gitmodules but not in pins.json"
                      % path)
    return errors


def check_network(repos):
    """(c) Pinned commits of public entries are fetchable; report tip drift."""
    errors = []
    info = []
    with tempfile.TemporaryDirectory(prefix="ulw-pins-") as tmp:
        for entry in repos:
            path, url, sha = entry["path"], entry["url"], entry["pinned_sha"]
            branch = entry["default_branch"]
            if not entry.get("public"):
                info.append("%s: not public; network check skipped" % path)
                continue
            bare = os.path.join(tmp, path.replace("/", "_") + ".git")
            run_git(["init", "-q", "--bare", bare])
            proc = run_git(["fetch", "-q", "--depth", "1", url, sha],
                           cwd=bare, check=False)
            if proc.returncode != 0:
                errors.append("%s: cannot fetch %s from %s: %s"
                              % (path, sha, url, proc.stderr.strip()))
                continue
            got = run_git(["rev-parse", "--verify", "FETCH_HEAD^{commit}"],
                          cwd=bare, check=False).stdout.strip()
            if got != sha:
                errors.append("%s: fetched %s but expected %s"
                              % (path, got, sha))
                continue
            proc = run_git(["ls-remote", "--symref", url, "HEAD",
                            "refs/heads/" + branch], check=False)
            if proc.returncode != 0:
                info.append("%s: pin exists on remote; ls-remote failed: %s"
                            % (path, proc.stderr.strip()))
                continue
            default_ref = None
            tips = {}
            for line in proc.stdout.splitlines():
                if line.startswith("ref: "):
                    default_ref = line[len("ref: "):].split("\t")[0]
                elif "\t" in line:
                    tsha, ref = line.split("\t", 1)
                    tips[ref] = tsha
            if default_ref is not None and default_ref != "refs/heads/" + branch:
                info.append("%s: remote default branch is %s, pins say %s"
                            % (path, default_ref, branch))
            tip = tips.get("refs/heads/" + branch)
            if tip is None:
                info.append("%s: pin exists on remote; configured branch %s "
                            "tip unknown (informational)" % (path, branch))
            elif tip == sha:
                info.append("%s: pin equals remote %s tip" % (path, branch))
            else:
                info.append("%s: pin %s is behind tip %s of %s (informational)"
                            % (path, sha, tip, branch))
    return errors, info


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=os.getcwd(),
                        help="workspace checkout to verify (default: cwd)")
    parser.add_argument("--pins", default=None,
                        help="pins.json to read (default: <repo>/pins.json)")
    parser.add_argument("--network", action="store_true",
                        help="also verify pinned commits exist on remotes")
    args = parser.parse_args(argv)
    repo = os.path.abspath(args.repo)
    pins_path = os.path.abspath(args.pins or os.path.join(repo, "pins.json"))

    errors = []
    try:
        repos, perrors = load_pins(pins_path)
        errors.extend(perrors)
        if not perrors:
            errors.extend(check_tree_and_modules(repo, repos))
            if args.network:
                nerrors, info = check_network(repos)
                errors.extend(nerrors)
                for line in info:
                    print("info: " + line)
    except (OSError, RuntimeError, ValueError) as exc:
        errors.append(str(exc))
        repos = []

    for err in errors:
        print("FAIL: " + err)
    n = len(repos)
    if errors:
        print("verify_pins: FAIL (%d error(s) across %d pin(s))"
              % (len(errors), n))
        return 1
    print("verify_pins: OK (%d pin(s) agree with tree and .gitmodules%s)"
          % (n, "; remotes checked" if args.network else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
