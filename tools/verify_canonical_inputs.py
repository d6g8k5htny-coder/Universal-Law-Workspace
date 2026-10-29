#!/usr/bin/env python3
"""Verify canonical input blob identities at the workspace's pinned sources.

Current inputs are checked at their repository gitlink pin. An explicit full
commit ref is checked as a historical source and is never called current.
Remote default-tip currency is a separate check: run verify_pins.py
--require-current. This tool does not evaluate the meaning of the source.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit

from verify_pins import FULL_SHA, check_tree_and_modules, load_pins, run_git


INPUTS = ("pins.json", ".gitmodules", "workspace/repositories.json")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def unique_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member " + ascii(key))
        result[key] = value
    return result


def tree_entry(repo, commit, path):
    result = run_git(["--literal-pathspecs", "ls-tree", "-z", commit, "--", path], cwd=repo)
    records = [part for part in result.stdout.split("\0") if part]
    if len(records) != 1:
        raise ValueError("source path %r is missing or ambiguous" % path)
    metadata, actual_path = records[0].split("\t", 1)
    mode, kind, sha = metadata.split(" ")
    if actual_path != path:
        raise ValueError("source path mismatch for %r" % path)
    if mode not in ("100644", "100755") or kind != "blob":
        raise ValueError("source path %r has non-regular mode %s" % (path, mode))
    return sha


def committed_input(repo, commit, relative):
    path = repo / relative
    # Reject both a symlinked file and a symlinked parent directory.
    if path.resolve() != path or not path.is_file():
        raise ValueError("working %s is missing or has a symlink" % relative)
    expected = tree_entry(repo, commit, relative)
    data = path.read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
    if expected != actual:
        raise ValueError("working %s differs from committed input" % relative)
    return data


def remote_repository(url):
    if not isinstance(url, str):
        raise ValueError("repository URL must be a string")
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.netloc != "github.com" or
            parsed.query or parsed.fragment or not parsed.path.startswith("/")):
        raise ValueError("repository URL must be a public GitHub HTTPS URL")
    name = parsed.path[1:]
    if name.endswith(".git"):
        name = name[:-4]
    if not REPOSITORY.fullmatch(name):
        raise ValueError("repository URL has an invalid owner/name")
    return name


def valid_path(path):
    return (isinstance(path, str) and bool(path) and not path.startswith("/")
            and "\\" not in path and not any(ord(c) < 32 for c in path)
            and all(part not in ("", ".", "..") for part in path.split("/")))


def full_sha(value):
    return isinstance(value, str) and FULL_SHA.fullmatch(value) is not None


def source_specs(doc, pins):
    if not isinstance(doc, dict):
        raise ValueError("workspace manifest must be an object")
    inputs = doc.get("canonical_inputs")
    if not isinstance(inputs, dict) or not inputs:
        raise ValueError("canonical_inputs must be a nonempty object")
    listed = doc.get("repositories")
    if not isinstance(listed, list):
        raise ValueError("repositories must be a list")
    names = [x.get("full_name") for x in listed if isinstance(x, dict)]
    remote_map = {}
    for pin in pins:
        name = remote_repository(pin.get("url"))
        if name in remote_map:
            raise ValueError("duplicate pinned repository " + name)
        if not pin.get("public"):
            raise ValueError("repository %s is not public; cannot skip it" % name)
        remote_map[name] = pin
    specs = []
    for key, item in inputs.items():
        if not isinstance(item, dict):
            raise ValueError("canonical input %s must be an object" % key)
        name = item.get("repository")
        if not isinstance(name, str) or name not in names or name not in remote_map:
            raise ValueError("canonical input %s repository is not pinned and listed" % key)
        path = item.get("path")
        if not valid_path(path):
            raise ValueError("canonical input %s path is invalid" % key)
        blob = item.get("observed_blob")
        if not full_sha(blob):
            raise ValueError("canonical input %s blob must be a full SHA" % key)
        ref = item.get("ref", remote_map[name]["pinned_sha"])
        if not full_sha(ref):
            raise ValueError("canonical input %s ref must be an immutable full SHA" % key)
        specs.append((key, name, remote_map[name]["url"], path, ref, blob,
                      "historical" if "ref" in item and ref != remote_map[name]["pinned_sha"] else "pinned"))
    return specs


def check_sources(specs):
    with tempfile.TemporaryDirectory(prefix="ulw-canonical-") as tmp:
        fetched = {}
        for key, name, url, path, commit, blob, status in specs:
            identity = (url, commit)
            if identity not in fetched:
                bare = os.path.join(tmp, str(len(fetched)) + ".git")
                run_git(["init", "-q", "--bare", bare])
                result = run_git(["fetch", "-q", "--depth", "1", url, commit], cwd=bare, check=False)
                if result.returncode:
                    raise ValueError("%s: cannot fetch source commit %s: %s" %
                                     (key, commit, result.stderr.strip()))
                got = run_git(["rev-parse", "--verify", "FETCH_HEAD^{commit}"], cwd=bare).stdout.strip()
                if got != commit:
                    raise ValueError("%s: fetched commit differs from source ref" % key)
                fetched[identity] = bare
            actual = tree_entry(fetched[identity], commit, path)
            if actual != blob:
                raise ValueError("%s: source blob %s != observed blob %s" % (key, actual, blob))
            print("OK: %s: %s %s %s at %s" % (key, status, name, path, commit))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args(argv)
    repo = Path(args.workspace).resolve()
    try:
        head = run_git(["rev-parse", "--verify", "HEAD^{commit}"], cwd=repo).stdout.strip()
        snapshot = {name: committed_input(repo, head, name) for name in INPUTS}
        doc = json.loads(snapshot["workspace/repositories.json"], object_pairs_hook=unique_members)
        # Parse the exact bytes that were checked against HEAD, rather than a
        # second, potentially different read of the working manifest.
        with tempfile.NamedTemporaryFile(mode="wb") as pins_file:
            pins_file.write(snapshot["pins.json"])
            pins_file.flush()
            pins, errors = load_pins(pins_file.name)
        if errors:
            raise ValueError("; ".join(errors))
        errors.extend(check_tree_and_modules(repo, pins, head))
        if errors:
            raise ValueError("; ".join(errors))
        specs = source_specs(doc, pins)
        check_sources(specs)
        end_head = run_git(["rev-parse", "--verify", "HEAD^{commit}"], cwd=repo).stdout.strip()
        if end_head != head:
            raise ValueError("workspace HEAD changed during source verification")
        for name in INPUTS:
            if committed_input(repo, head, name) != snapshot[name]:
                raise ValueError("working %s changed during verification" % name)
        print("verify_canonical_inputs: OK (%d canonical inputs; default-tip currency is separate)" % len(specs))
        return 0
    except (ValueError, RuntimeError, OSError, UnicodeError) as exc:
        print("FAIL: %s" % exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
