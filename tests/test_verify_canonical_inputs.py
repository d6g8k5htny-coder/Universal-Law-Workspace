"""End-to-end controls for source-bound canonical input identities."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


CHECKER = Path(os.environ.get("CBZ_CANONICAL_CHECKER", Path(__file__).resolve().parents[1] / "tools/verify_canonical_inputs.py"))


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip()


class CanonicalInputControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="canonical-input-control-")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.source = root / "source"
        self.source.mkdir()
        git(self.source, "init", "-q")
        git(self.source, "config", "user.name", "Fixture")
        git(self.source, "config", "user.email", "fixture@example.invalid")
        git(self.source, "branch", "-M", "main")
        (self.source / "records").mkdir()
        (self.source / "records/current.json").write_text('{"value":1}\n')
        git(self.source, "add", ".")
        git(self.source, "commit", "-qm", "historical source")
        self.old = git(self.source, "rev-parse", "HEAD")
        self.old_blob = git(self.source, "rev-parse", "HEAD:records/current.json")
        (self.source / "records/current.json").write_text('{"value":2}\n')
        git(self.source, "add", ".")
        git(self.source, "commit", "-qm", "current source")
        self.tip = git(self.source, "rev-parse", "HEAD")
        self.blob = git(self.source, "rev-parse", "HEAD:records/current.json")
        remote_parent = root / "remote" / "acme"
        remote_parent.mkdir(parents=True)
        self.remote = remote_parent / "example.git"
        git(root, "clone", "-q", "--bare", str(self.source), str(self.remote))
        self.workspace = root / "workspace"
        self.workspace.mkdir()
        git(self.workspace, "init", "-q")
        git(self.workspace, "config", "user.name", "Fixture")
        git(self.workspace, "config", "user.email", "fixture@example.invalid")
        (self.workspace / "workspace").mkdir()
        (self.workspace / ".gitmodules").write_text(
            '[submodule "repos/example"]\n'
            '\tpath = repos/example\n'
            '\turl = https://github.com/acme/example.git\n'
            '\tbranch = main\n')
        self.pins = {"schema": "ulw.pins.v1", "repos": [{
            "name": "example", "path": "repos/example",
            "url": "https://github.com/acme/example.git",
            "default_branch": "main", "pinned_sha": self.tip,
            "public": True, "opt_in": False, "note": "fixture"}]}
        self.doc = {"repositories": [{"full_name": "acme/example"}],
                    "canonical_inputs": {
                        "current": {"repository": "acme/example",
                                    "path": "records/current.json",
                                    "observed_blob": self.blob},
                        "historical": {"repository": "acme/example",
                                       "path": "records/current.json",
                                       "ref": self.old,
                                       "observed_blob": self.old_blob}}}
        self.save_commit()
        self.env = os.environ.copy()
        self.env["GIT_CONFIG_COUNT"] = "1"
        self.env["GIT_CONFIG_KEY_0"] = "url." + (root / "remote").as_uri() + "/.insteadOf"
        self.env["GIT_CONFIG_VALUE_0"] = "https://github.com/"
        self.env["GIT_TERMINAL_PROMPT"] = "0"

    def save_commit(self, raw_manifest=None, gitlink=None):
        (self.workspace / "pins.json").write_text(json.dumps(self.pins) + "\n")
        (self.workspace / "workspace/repositories.json").write_text(
            raw_manifest if raw_manifest is not None else json.dumps(self.doc) + "\n")
        git(self.workspace, "add", ".gitmodules", "pins.json", "workspace/repositories.json")
        git(self.workspace, "update-index", "--add", "--cacheinfo",
            "160000," + (gitlink or self.tip) + ",repos/example")
        git(self.workspace, "commit", "-qm", "source identities")

    def check(self, env=None):
        flags = ["-O"] if sys.flags.optimize else []
        return subprocess.run([sys.executable, *flags, str(CHECKER), "--workspace", str(self.workspace)],
                              env=env or self.env, text=True, capture_output=True)

    def rejected(self, proc, diagnostic):
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        failures = [line for line in (proc.stdout + proc.stderr).splitlines()
                    if line.startswith("FAIL: ")]
        self.assertTrue(any(diagnostic in line for line in failures),
                        proc.stdout + proc.stderr)

    def test_current_and_explicit_historical_sources_pass(self):
        proc = self.check()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("historical", proc.stdout.lower())
        self.assertIn("2 canonical", proc.stdout.lower())

    def test_wrong_current_blob_fails(self):
        self.doc["canonical_inputs"]["current"]["observed_blob"] = self.old_blob
        self.save_commit()
        self.rejected(self.check(), "blob")

    def test_missing_path_fails(self):
        self.doc["canonical_inputs"]["current"]["path"] = "records/missing.json"
        self.save_commit()
        self.rejected(self.check(), "path")

    def test_unfetchable_historical_commit_fails(self):
        self.doc["canonical_inputs"]["historical"]["ref"] = "1" * 40
        self.save_commit()
        self.rejected(self.check(), "fetch")

    def test_mutable_historical_ref_fails(self):
        self.doc["canonical_inputs"]["historical"]["ref"] = "main"
        self.save_commit()
        self.rejected(self.check(), "ref")

    def test_unmapped_repository_fails(self):
        self.doc["canonical_inputs"]["current"]["repository"] = "acme/other"
        self.save_commit()
        self.rejected(self.check(), "repository")

    def test_pinned_repository_must_be_listed_in_workspace(self):
        self.doc["repositories"] = []
        self.save_commit()
        self.rejected(self.check(), "repository")

    def test_nonpublic_source_cannot_be_skipped(self):
        self.pins["repos"][0]["public"] = False
        self.save_commit()
        self.rejected(self.check(), "not public")

    def test_duplicate_manifest_members_fail(self):
        raw = '{"canonical_inputs":{},"canonical_inputs":{},"repositories":[]}\n'
        self.save_commit(raw_manifest=raw)
        self.rejected(self.check(), "duplicate")

    def test_dirty_workspace_manifest_fails(self):
        path = self.workspace / "workspace/repositories.json"
        path.write_text(path.read_text() + " ")
        self.rejected(self.check(), "differs")

    def test_dirty_pins_manifest_fails(self):
        path = self.workspace / "pins.json"
        path.write_text(path.read_text() + " ")
        self.rejected(self.check(), "differs")

    def test_identical_symlinked_workspace_manifest_fails(self):
        path = self.workspace / "workspace/repositories.json"
        copy = Path(self.temp.name) / "manifest-copy"
        copy.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(copy)
        self.rejected(self.check(), "symlink")

    def test_gitmodules_change_fails(self):
        path = self.workspace / ".gitmodules"
        path.write_text(path.read_text() + "\n")
        self.rejected(self.check(), "differs")

    def test_gitlink_mismatch_fails(self):
        self.save_commit(gitlink=self.old)
        self.rejected(self.check(), "gitlink")

    def test_symlinked_source_is_not_accepted_as_a_blob(self):
        (self.source / "records/current.json").unlink()
        (self.source / "records/current.json").symlink_to("somewhere")
        git(self.source, "add", "records/current.json")
        git(self.source, "commit", "-qm", "symlink source")
        self.tip = git(self.source, "rev-parse", "HEAD")
        self.blob = git(self.source, "rev-parse", "HEAD:records/current.json")
        git(self.source, "push", "-q", str(self.remote), "HEAD:refs/heads/main")
        self.pins["repos"][0]["pinned_sha"] = self.tip
        self.doc["canonical_inputs"]["current"]["observed_blob"] = self.blob
        self.save_commit()
        self.rejected(self.check(), "mode")

    def test_empty_canonical_inputs_fails(self):
        self.doc["canonical_inputs"] = {}
        self.save_commit()
        self.rejected(self.check(), "canonical_inputs")

    def test_unavailable_remote_fails(self):
        shutil.rmtree(self.remote)
        self.rejected(self.check(), "fetch")

    def git_fetch_shim(self, body):
        directory = Path(self.temp.name) / "bin"
        directory.mkdir()
        shim = directory / "git"
        shim.write_text('#!/bin/sh\nif [ "$1" = fetch ]; then\n' + body +
                        '\nfi\nexec "$CBZ_REAL_GIT" "$@"\n')
        shim.chmod(0o755)
        env = dict(self.env)
        env["CBZ_REAL_GIT"] = shutil.which("git")
        env["CBZ_TARGET_WS"] = str(self.workspace)
        env["PATH"] = str(directory) + os.pathsep + env["PATH"]
        return env

    def test_workspace_head_change_during_fetch_fails(self):
        body = ('"$CBZ_REAL_GIT" -C "$CBZ_TARGET_WS" -c user.name=t '
                '-c user.email=t@x -c commit.gpgsign=false commit -q '
                '--allow-empty -m changed')
        self.rejected(self.check(self.git_fetch_shim(body)), "HEAD changed")

    def test_manifest_change_during_fetch_fails(self):
        body = 'printf " " >> "$CBZ_TARGET_WS/workspace/repositories.json"'
        self.rejected(self.check(self.git_fetch_shim(body)), "differs")

    def test_fetched_commit_identity_mismatch_fails(self):
        directory = Path(self.temp.name) / "bin"
        directory.mkdir()
        shim = directory / "git"
        shim.write_text('#!/bin/sh\n'
                        'if [ "$1" = rev-parse ] && [ "$3" = "FETCH_HEAD^{commit}" ]; then\n'
                        '  printf "%040d\\n" 1; exit 0\nfi\n'
                        'exec "$CBZ_REAL_GIT" "$@"\n')
        shim.chmod(0o755)
        env = dict(self.env)
        env["CBZ_REAL_GIT"] = shutil.which("git")
        env["PATH"] = str(directory) + os.pathsep + env["PATH"]
        self.rejected(self.check(env), "fetched commit differs")


if __name__ == "__main__":
    unittest.main()
