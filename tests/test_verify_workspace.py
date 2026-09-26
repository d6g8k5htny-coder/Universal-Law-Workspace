#!/usr/bin/env python3
"""Negative controls for scripts/verify_workspace.py.

A checker nobody has ever seen refuse is not a checker. Every control below weakens one
fact the verifier claims to enforce and asserts that the verifier then REFUSES. If a
control stops failing, the check it guards has gone silent.

Standard library only, so CI needs nothing installed: `python3 -m unittest discover tests`.

Each control runs against a real recursive COPY of the repository, never a hardlink farm
and never the tree itself. An earlier version of this harness used `cp -al` in a sibling
project and wrote straight through into the live checkout; `test_copy_is_not_the_original`
below asserts the inodes differ so that cannot recur silently.

Scientific effect: NONE. These controls test a documentation checker. They verify no
mathematics and move no status.
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Assembled at runtime, exactly as the verifier does it: a control that spelled these out
# would plant the very strings the verifier forbids and fail the tree it is testing.
EXCLUDED_REPO = 'sand' + 'box'
RELAY = 'private' + 'relay.' + 'appleid' + '.com'
FAKE_TOKEN = 'ghp' + '_' + 'A' * 36  # shape only; not a credential and never was one

GIT_ENV = {
    **os.environ,
    'GIT_AUTHOR_NAME': 'control', 'GIT_AUTHOR_EMAIL': 'control@invalid',
    'GIT_COMMITTER_NAME': 'control', 'GIT_COMMITTER_EMAIL': 'control@invalid',
}


def run_verifier(root: pathlib.Path) -> subprocess.CompletedProcess:
    return subprocess.run(['python3', str(root / 'scripts' / 'verify_workspace.py')],
                          capture_output=True, text=True, cwd=str(root), env=GIT_ENV)


def git(root: pathlib.Path, *args: str, stdin: str = '') -> subprocess.CompletedProcess:
    # `input` is always supplied, even when empty. Plumbing commands such as `mktree` and
    # `hash-object --stdin` read standard input; inheriting the runner's stdin makes them
    # block forever instead of failing, which is exactly how the first run of this file hung.
    return subprocess.run(['git', '-C', str(root), *args], input=stdin,
                          capture_output=True, text=True, env=GIT_ENV)


class WorkspaceControls(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix='verify-control-'))
        self.copy = self.tmp / 'workspace'
        shutil.copytree(ROOT, self.copy, symlinks=True)
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def manifest(self) -> dict:
        return json.loads((self.copy / 'WORKSPACE.json').read_text(encoding='utf-8'))

    def write_manifest(self, m: dict) -> None:
        (self.copy / 'WORKSPACE.json').write_text(json.dumps(m, indent=2, ensure_ascii=False)
                                                  + '\n', encoding='utf-8')

    def assertRefuses(self, needle: str) -> None:
        r = run_verifier(self.copy)
        self.assertNotEqual(r.returncode, 0,
                            f'verifier PASSED a weakened tree; expected refusal about {needle!r}\n'
                            f'{r.stdout}{r.stderr}')
        self.assertIn(needle, r.stdout + r.stderr)

    # --- the harness itself -------------------------------------------------------

    def test_copy_is_not_the_original(self) -> None:
        """The control must never be able to write into the real repository."""
        a = (self.copy / 'WORKSPACE.json').stat()
        b = (ROOT / 'WORKSPACE.json').stat()
        self.assertNotEqual((a.st_dev, a.st_ino), (b.st_dev, b.st_ino))

    def test_unmutated_copy_passes(self) -> None:
        """Without this, every control below could be passing for the wrong reason."""
        r = run_verifier(self.copy)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('problems=0', r.stdout)

    # --- checks 1-3: the pin and the document cannot disagree ---------------------

    def test_gitlink_sha_that_disagrees_with_the_manifest_is_refused(self) -> None:
        m = self.manifest()
        m['packages'][0]['default_tip'] = 'd' * 40
        self.write_manifest(m)
        self.assertRefuses('the pin and the document disagree')

    def test_missing_gitlink_is_refused(self) -> None:
        name = self.manifest()['packages'][0]['name']
        git(self.copy, 'rm', '--cached', '-q', f'repos/{name}')
        self.assertRefuses('has no submodule gitlink')

    def test_vendored_bytes_where_a_gitlink_belongs_are_refused(self) -> None:
        """mode 100644 under repos/ means bytes were copied in without a ledger row."""
        name = self.manifest()['packages'][0]['name']
        git(self.copy, 'rm', '--cached', '-q', f'repos/{name}')
        blob = git(self.copy, 'hash-object', '-w', '--stdin').stdout  # empty blob
        git(self.copy, 'update-index', '--add', '--cacheinfo',
            f'100644,{blob.strip()},repos/{name}')
        self.assertRefuses('expected 160000')

    # --- check 2: a stranger must be able to clone every package -----------------

    def test_local_submodule_url_is_refused(self) -> None:
        p = self.copy / '.gitmodules'
        p.write_text(p.read_text(encoding='utf-8').replace('https://github.com/', 'file:///home/'),
                     encoding='utf-8')
        self.assertRefuses('cannot clone')

    # --- check 4: the private package stays out ----------------------------------

    def test_dropping_the_declared_exclusion_is_refused(self) -> None:
        m = self.manifest()
        m['excluded_repositories'] = [x for x in m['excluded_repositories']
                                      if x['name'] != EXCLUDED_REPO]
        self.write_manifest(m)
        self.assertRefuses('not recorded as an excluded repository')

    def test_credential_shaped_string_in_a_tracked_file_is_refused(self) -> None:
        (self.copy / 'MERGE_LEDGER.md').write_text(f'token: {FAKE_TOKEN}\n', encoding='utf-8')
        self.assertRefuses('looks like it contains a credential')

    def test_private_relay_address_in_a_tracked_file_is_refused(self) -> None:
        (self.copy / 'MERGE_LEDGER.md').write_text(f'contact: someone@{RELAY}\n', encoding='utf-8')
        self.assertRefuses('private relay address')

    def test_untracked_file_with_the_same_string_is_NOT_refused(self) -> None:
        """The scan covers what is published, and only that.

        This is the complement of the two controls above, and it pins a real defect the
        controls found: the verifier used to walk raw disk, so compiled bytecode under
        `__pycache__` -- ignored, untracked, never in any clone -- failed the tree. Python
        folds `'a' + 'b'` at compile time, so the .pyc carried the exact literals its source
        assembles at runtime precisely in order not to carry them.
        """
        (self.copy / 'scratch.local').write_text(f'token: {FAKE_TOKEN}\ncontact: x@{RELAY}\n',
                                                 encoding='utf-8')
        cache = self.copy / 'tests' / '__pycache__'
        cache.mkdir(parents=True, exist_ok=True)
        (cache / 'folded.pyc').write_text(f'{EXCLUDED_REPO} {RELAY} {FAKE_TOKEN}\n',
                                          encoding='utf-8')
        r = run_verifier(self.copy)
        self.assertEqual(r.returncode, 0,
                         'an untracked file made the verifier refuse; it scans published '
                         f'content, not scratch\n{r.stdout}{r.stderr}')

    def test_tracking_that_same_file_then_refuses(self) -> None:
        """...and the moment it becomes published content, it is refused."""
        (self.copy / 'scratch.local').write_text(f'token: {FAKE_TOKEN}\n', encoding='utf-8')
        git(self.copy, 'add', '-f', 'scratch.local')
        self.assertRefuses('looks like it contains a credential')

    def test_secret_scan_that_cannot_run_refuses_rather_than_passes(self) -> None:
        shutil.rmtree(self.copy / '.git')
        self.assertRefuses('The secret scan cannot run')

    # --- checks 5-6: every named ref has a sha, a reason and a map row ------------

    def test_named_ref_with_a_short_sha_is_refused(self) -> None:
        m = self.manifest()
        m['named_branches'][0]['sha'] = 'abc123'
        self.write_manifest(m)
        self.assertRefuses('sha is not 40 hex')

    def test_named_ref_with_no_reason_is_refused(self) -> None:
        m = self.manifest()
        m['named_branches'][0]['why'] = ''
        self.write_manifest(m)
        self.assertRefuses('with no stated reason')

    def test_named_ref_absent_from_the_branch_map_is_refused(self) -> None:
        m = self.manifest()
        m['named_branches'][0]['sha'] = 'f' * 40
        self.write_manifest(m)
        self.assertRefuses('BRANCH_MAP.md')

    def test_omission_with_no_reason_is_refused(self) -> None:
        m = self.manifest()
        m['deliberately_not_imported'][0]['why_not'] = ''
        self.write_manifest(m)
        self.assertRefuses('omission recorded with no reason')

    # --- check 7: the host repository's own refs ---------------------------------

    def test_deleting_the_host_repository_block_is_refused(self) -> None:
        m = self.manifest()
        del m['host_repository']
        self.write_manifest(m)
        self.assertRefuses('no host_repository block')

    def test_host_ref_with_a_short_sha_is_refused(self) -> None:
        m = self.manifest()
        m['host_repository']['refs'][0]['sha'] = 'abc123'
        self.write_manifest(m)
        self.assertRefuses('sha is not 40 hex')

    def test_host_ref_with_no_reason_is_refused(self) -> None:
        m = self.manifest()
        m['host_repository']['refs'][0]['why'] = ''
        self.write_manifest(m)
        self.assertRefuses('recorded with no stated reason')

    def test_host_ref_absent_from_the_branch_map_is_refused(self) -> None:
        m = self.manifest()
        m['host_repository']['refs'][0]['sha'] = 'e' * 40
        self.write_manifest(m)
        self.assertRefuses('absent from BRANCH_MAP.md')

    def test_dropping_the_other_lane_branch_from_the_map_is_refused(self) -> None:
        """The second bootstrap lane must stay visible in the rendered map."""
        m = self.manifest()
        other = [r for r in m['host_repository']['refs'] if r['kind'] == 'other lane']
        self.assertEqual(len(other), 1, 'the other lane row vanished from the manifest')
        p = self.copy / 'BRANCH_MAP.md'
        p.write_text(p.read_text(encoding='utf-8').replace(other[0]['branch'], 'elsewhere'),
                     encoding='utf-8')
        self.assertRefuses('branch name absent from BRANCH_MAP.md')

    # --- check 8: this branch builds on the owner's history, not over it ---------

    def test_history_that_does_not_descend_from_the_root_commit_is_refused(self) -> None:
        """The whole point of the check: an orphan or force-pushed tree must fail."""
        tree = git(self.copy, 'mktree').stdout.strip()
        self.assertEqual(len(tree), 40, 'could not build an empty tree object')
        unrelated = git(self.copy, 'commit-tree', tree, stdin='unrelated\n').stdout.strip()
        self.assertEqual(len(unrelated), 40, 'could not build an unrelated commit')
        m = self.manifest()
        m['host_repository']['root_commit'] = unrelated
        self.write_manifest(m)
        self.assertRefuses('does not descend from the recorded root commit')

    def test_unresolvable_root_commit_refuses_rather_than_passes(self) -> None:
        """A check that cannot run must not report success."""
        m = self.manifest()
        m['host_repository']['root_commit'] = 'a' * 40
        self.write_manifest(m)
        self.assertRefuses('could not check ancestry')

    def test_non_hex_root_commit_is_refused(self) -> None:
        m = self.manifest()
        m['host_repository']['root_commit'] = 'not-a-sha'
        self.write_manifest(m)
        self.assertRefuses('root_commit is not 40 hex')

    # --- check 9: a run that compared almost nothing is not a pass ---------------

    def test_emptied_manifest_trips_the_vacuity_floor(self) -> None:
        m = self.manifest()
        m['named_branches'] = []
        m['deliberately_not_imported'] = []
        m['host_repository']['refs'] = []
        self.write_manifest(m)
        self.assertRefuses('VACUOUS RUN')


if __name__ == '__main__':
    unittest.main()
