"""Real-Git controls for structural federation vectors; fixtures certify no math."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
TOOL = Path(os.environ.get('CBZ_VECTOR_UNDER_TEST', ROOT / 'tools/verify_federation_vector.py'))
NAMES = ('main', 'Math-', 'governance-', 'Universal-Law-Workspace', 'meta-framework',
         'query-', 'google-drive', 'trial', 'sandbox', 'd6g8k5htny-coder',
         'openclaw-custodian-validation', 'research-hosted-qualification')
CHILDREN = ('main', 'Math-', 'meta-framework', 'query-', 'google-drive', 'trial',
            'governance-', 'sandbox')
MATH_PACKAGES = ('formal', 'frontiers/cap_first_exit_lean_20261002',
    'frontiers/determinant_moment_20261025', 'frontiers/source_derivative_gaussian_20261025',
    'frontiers/source_lifetime_realization_20261017', 'frontiers/source_smooth_realization_20261011',
    'specifications/lean_statement_proofs_20261011', 'specifications/lean_statements_20261010')


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
               GIT_TERMINAL_PROMPT='0')
    return subprocess.check_output(['git', '-c', 'core.hooksPath=' + os.devnull,
                                    '-C', str(repo), *args], env=env, stderr=subprocess.PIPE)


def write(repo, path, value):
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(value if isinstance(value, bytes) else value.encode())


def commit(repo):
    git(repo, 'add', '--all')
    git(repo, 'commit', '-qm', 'fixture')
    return git(repo, 'rev-parse', 'HEAD').decode().strip()


class TransportCleanupControl(unittest.TestCase):
    def test_cleanup_error_code_survives_sanitization_without_git(self):
        sys.path.insert(0,str(ROOT/'tools'))
        self.addCleanup(lambda:sys.path.remove(str(ROOT/'tools')))
        spec=importlib.util.spec_from_file_location('vector_cleanup_control',TOOL)
        tool=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool)
        url='https://github.com/fixture/cleanup'
        with tempfile.TemporaryDirectory(prefix='vector-cleanup-control-') as folder:
            storage=Path(folder)
            (storage/hashlib.sha256(url.encode()).hexdigest()[:32]).mkdir()
            with mock.patch.object(tool,'_network_process',side_effect=ValueError('NETWORK_CLEANUP_ERROR')):
                result=tool.fetch_exact_commit(dict(url=url,commit='a'*40,roles=['fixture']),storage)
        self.assertEqual(result['status'],'CLEANUP_ERROR')
        self.assertEqual(result.get('error_code'),'NETWORK_CLEANUP_ERROR')


class Fixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = tempfile.TemporaryDirectory(prefix='vector-fixture-template-')
        base = Path(cls.template.name)
        seed = base / 'seed'
        seed.mkdir()
        git(seed, 'init', '-q', '--object-format=sha1')
        for key, value in [('user.name', 'Fixture'), ('user.email', 'fixture@example.invalid'),
                           ('commit.gpgsign', 'false')]:
            git(seed, 'config', key, value)
        write(seed, 'source.txt', 'source\n')
        cls.dependency = commit(seed)
        cls.base = base / 'repos'
        cls.base.mkdir()
        for name in NAMES:
            shutil.copytree(seed, cls.base / name)
        main = cls.base / 'main'
        write(main, 'authority.json', '{"historical":true}\n')
        cls.historical = commit(main)
        (main / 'authority.json').unlink()
        for name, roots in [('main', ('formal',)), ('Math-', MATH_PACKAGES)]:
            repo = cls.base / name
            for package in roots:
                package_name = ('universal_law_specifications' if package.endswith('lean_statements_20261010')
                                else 'fixture_package')
                packages = [] if name == 'main' else [dict(type='git', name='dep' + str(i),
                    scope='', url='https://github.com/fixture/dep' + str(i), rev=cls.dependency,
                    inputRev='main', inherited=True, subDir=None, configFile='lakefile.toml',
                    manifestFile='lake-manifest.json') for i in range(9)]
                if package.endswith('lean_statement_proofs_20261011'):
                    packages.append(dict(type='path', name='universal_law_specifications',
                        dir='../lean_statements_20261010', inherited=False,
                        configFile='lakefile.toml', manifestFile='lake-manifest.json'))
                lock = dict(version='1.2.0', packagesDir='.lake/packages', packages=packages,
                            name=package_name, lakeDir='.lake', fixedToolchain=name != 'main')
                write(repo, package + '/lake-manifest.json', json.dumps(lock))
                write(repo, package + '/lean-toolchain', 'leanprover/lean4:v4.34.1\n')
                write(repo, package + '/lakefile.toml', 'name = "' + package_name + '"\n')
            if name == 'Math-':
                write(repo, 'graph.json', '{}\n')
                write(repo, 'landing.json', '{}\n')
            commit(repo)
        meta = cls.base / 'meta-framework'
        write(meta, 'registry.json', '{}\n')
        commit(meta)
        vector = {name: git(cls.base / name, 'rev-parse', 'HEAD').decode().strip() for name in NAMES}
        pins = [dict(name=n, path='repos/' + n, url='https://github.com/d6g8k5htny-coder/' + n + '.git',
                     default_branch='main', pinned_sha=vector[n], public=True, opt_in=n == 'sandbox',
                     note='fixture') for n in CHILDREN]
        canonical = {}
        for key, name, path, ref in [('repository_registry', 'meta-framework', 'registry.json', None),
            ('scientific_authority_map', 'main', 'authority.json', cls.historical),
            ('downstream_gate', 'Math-', 'graph.json', None),
            ('landing_claims', 'Math-', 'landing.json', None)]:
            item = dict(repository='d6g8k5htny-coder/' + name, path=path,
                        observed_blob=git(cls.base/name, 'rev-parse', (ref or vector[name]) + ':' + path).decode().strip(),
                        meaning='Fixture byte binding only')
            if ref:
                item['ref'] = ref
            canonical[key] = item
        workspace = cls.base / 'Universal-Law-Workspace'
        doc = dict(schema_version=1, workspace='d6g8k5htny-coder/Universal-Law-Workspace',
                   scientific_effect='NONE', scientific_status_authority=False,
                   purpose='Fixture', canonical_inputs=canonical,
                   repositories=[dict(full_name='d6g8k5htny-coder/' + n)
                                 for n in (*CHILDREN, 'Universal-Law-Workspace')])
        write(workspace, 'pins.json', json.dumps(dict(schema='ulw.pins.v1', generated_utc='fixture', repos=pins)))
        write(workspace, 'workspace/repositories.json', json.dumps(doc))
        modules = ''
        for p in pins:
            modules += ('[submodule "' + p['path'] + '"]\npath = ' + p['path'] + '\nurl = ' +
                        p['url'] + '\nbranch = main\n' + ('update = none\n' if p['opt_in'] else ''))
        write(workspace, '.gitmodules', modules)
        git(workspace, 'add', '--all')
        for p in pins:
            git(workspace, 'update-index', '--add', '--cacheinfo', '160000,' + p['pinned_sha'] + ',' + p['path'])
        git(workspace, 'commit', '-qm', 'workspace fixture')
        cls.vector = {name: git(cls.base/name, 'rev-parse', 'HEAD').decode().strip() for name in NAMES}

    @classmethod
    def tearDownClass(cls):
        cls.template.cleanup()

    def setUp(self):
        self.assertTrue(TOOL.is_file(), 'strict vector implementation is not supplied')
        sys.path.insert(0, str(ROOT / 'tools'))
        self.addCleanup(lambda: sys.path.remove(str(ROOT / 'tools')))
        spec = importlib.util.spec_from_file_location('vector_under_test', TOOL)
        self.tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.tool)
        self.temp = tempfile.TemporaryDirectory(prefix='vector-control-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repos'
        shutil.copytree(self.base, self.root)
        self.vector = dict(self.__class__.vector)
        self.vector_file = Path(self.temp.name) / 'vector.json'
        self.save_vector()

    def save_vector(self):
        self.vector_file.write_text(json.dumps(dict(schema='cbz.federation-vector.v1', repositories=self.vector)))

    def refresh(self, name):
        if name == 'Universal-Law-Workspace':
            git(self.root/name, 'add', 'pins.json', '.gitmodules', 'workspace/repositories.json')
            git(self.root/name, 'commit', '-qm', 'fixture metadata')
            self.vector[name] = git(self.root/name, 'rev-parse', 'HEAD').decode().strip()
        else:
            self.vector[name] = commit(self.root / name)
        self.save_vector()

    def capture(self):
        return self.tool.capture_sources(self.root, self.tool.load_vector(self.vector_file))

    def workspace_doc(self, mutate):
        path = self.root/'Universal-Law-Workspace/workspace/repositories.json'
        doc = json.loads(path.read_text())
        mutate(doc)
        path.write_text(json.dumps(doc))
        self.refresh('Universal-Law-Workspace')


class WorkspaceControls(Fixture):
    def setUp(self):
        super().setUp()
        self.assertTrue(hasattr(self.tool, 'verify_workspace'), 'workspace composition is not supplied')

    def check(self):
        return self.tool.verify_workspace(self.capture())

    def test_exact_workspace_and_four_sources_pass(self):
        result = self.check()
        self.assertEqual(len(result['pointers']), 8)
        self.assertEqual(len(result['canonical']), 4)

    def test_sandbox_pin_skew_rejected(self):
        repo = self.root/'Universal-Law-Workspace'
        git(repo, 'update-index', '--cacheinfo', '160000,' + 'f'*40 + ',repos/sandbox')
        git(repo, 'commit', '-qm', 'bad pointer')
        self.vector['Universal-Law-Workspace'] = git(repo, 'rev-parse', 'HEAD').decode().strip()
        self.save_vector()
        with self.assertRaisesRegex(ValueError, 'WORKSPACE_PIN_IDENTITY'):
            self.check()

    def test_extra_gitlink_refused(self):
        repo = self.root/'Universal-Law-Workspace'
        git(repo, 'update-index', '--add', '--cacheinfo', '160000,' + 'f'*40 + ',extra')
        git(repo, 'commit', '-qm', 'extra pointer')
        self.vector['Universal-Law-Workspace'] = git(repo, 'rev-parse', 'HEAD').decode().strip()
        self.save_vector()
        with self.assertRaisesRegex(ValueError, 'WORKSPACE_GITLINK_SET'):
            self.check()

    def test_missing_or_extra_canonical_key_refused(self):
        self.workspace_doc(lambda d: d['canonical_inputs'].pop('landing_claims'))
        with self.assertRaisesRegex(ValueError, 'CANONICAL_SET'):
            self.check()

    def test_canonical_wrong_blob_refused(self):
        self.workspace_doc(lambda d: d['canonical_inputs']['downstream_gate'].update(observed_blob='f'*40))
        with self.assertRaisesRegex(ValueError, 'CANONICAL_BLOB'):
            self.check()

    def test_canonical_unlisted_repository_refused(self):
        self.workspace_doc(lambda d: d['canonical_inputs']['downstream_gate'].update(repository='d6g8k5htny-coder/unknown'))
        with self.assertRaisesRegex(ValueError, 'WORKSPACE_MANIFEST'):
            self.check()

    def test_explicit_separate_canonical_ref_supported(self):
        row = next(x for x in self.check()['canonical'] if x['key'] == 'scientific_authority_map')
        self.assertEqual(row['commit'], self.historical)
        self.assertEqual(row['binding'], 'separate-ref')
        self.assertFalse((self.root/'main/authority.json').exists())

    def test_explicit_canonical_tree_oid_refused(self):
        repo = self.root/'main'
        tree = git(repo, 'rev-parse', self.historical + '^{tree}').decode().strip()
        self.assertEqual(git(repo, 'cat-file', '-t', tree).strip(), b'tree')
        self.workspace_doc(lambda d: d['canonical_inputs']['scientific_authority_map'].update(ref=tree))
        with self.assertRaisesRegex(ValueError, 'CANONICAL_COMMIT'):
            self.check()

    def test_explicit_canonical_annotated_tag_oid_refused(self):
        repo = self.root/'main'
        git(repo, '-c', 'tag.gpgsign=false', 'tag', '-a', 'canonical-fixture',
            '-m', 'fixture tag object', self.historical)
        tag = git(repo, 'rev-parse', 'refs/tags/canonical-fixture').decode().strip()
        self.assertEqual(git(repo, 'cat-file', '-t', tag).strip(), b'tag')
        self.workspace_doc(lambda d: d['canonical_inputs']['scientific_authority_map'].update(ref=tag))
        with self.assertRaisesRegex(ValueError, 'CANONICAL_COMMIT'):
            self.check()

    def test_source_blob_symlink_refused(self):
        p = self.root/'meta-framework/registry.json'
        p.unlink(); p.symlink_to('source.txt')
        self.refresh('meta-framework')
        repo = self.root/'Universal-Law-Workspace'
        pins = json.loads((repo/'pins.json').read_text())
        next(x for x in pins['repos'] if x['name']=='meta-framework')['pinned_sha'] = self.vector['meta-framework']
        (repo/'pins.json').write_text(json.dumps(pins))
        git(repo,'update-index','--cacheinfo','160000,'+self.vector['meta-framework']+',repos/meta-framework')
        self.refresh('Universal-Law-Workspace')
        with self.assertRaisesRegex(ValueError, 'SOURCE_BLOB_REGULAR'):
            self.check()


class LockControls(Fixture):
    def setUp(self):
        super().setUp()
        self.assertTrue(hasattr(self.tool, 'verify_locks'), 'native lock composition is not supplied')

    def check(self):
        return self.tool.verify_locks(self.capture())

    def change_lock(self, mutate, package='formal', name='Math-'):
        path = self.root/name/package/'lake-manifest.json'
        data = json.loads(path.read_text())
        mutate(data)
        path.write_text(json.dumps(data))
        self.refresh(name)

    def test_all_nine_native_locks_pass(self):
        result = self.check()
        self.assertEqual(len(result['packages']), 9)
        self.assertEqual(len(result['git_dependencies']), 72)
        self.assertEqual(result['toolchain'], 'leanprover/lean4:v4.34.1')

    def test_path_dependency_sibling_same_tree_passes(self):
        result = self.check()
        self.assertEqual(len(result['path_dependencies']), 1)
        self.assertEqual(result['path_dependencies'][0]['target'], 'specifications/lean_statements_20261010')

    def test_floating_resolved_revision_refused(self):
        for package in MATH_PACKAGES:
            path = self.root/'Math-'/package/'lake-manifest.json'
            data = json.loads(path.read_text())
            data['packages'][0]['rev'] = 'main'
            path.write_text(json.dumps(data))
        self.refresh('Math-')
        with self.assertRaisesRegex(ValueError, 'LOCK_COMMIT'):
            self.check()

    def test_duplicate_dependency_name_refused(self):
        self.change_lock(lambda d: d['packages'].append(copy.deepcopy(d['packages'][0])))
        with self.assertRaisesRegex(ValueError, 'LOCK_DEPENDENCY_DUPLICATE'):
            self.check()

    def test_dependency_revision_drift_refused(self):
        self.change_lock(lambda d: d['packages'][0].update(rev='f'*40))
        with self.assertRaisesRegex(ValueError, 'LOCK_DEPENDENCY_DRIFT'):
            self.check()

    def test_lock_schema_or_unknown_entry_refused(self):
        self.change_lock(lambda d: d.update(version='9.0'))
        with self.assertRaisesRegex(ValueError, 'LOCK_SCHEMA'):
            self.check()

    def test_unknown_dependency_type_refused(self):
        self.change_lock(lambda d: d['packages'][0].update(type='executable'))
        with self.assertRaisesRegex(ValueError, 'LOCK_DEPENDENCY_TYPE'):
            self.check()

    def test_toolchain_disagreement_refused(self):
        write(self.root/'Math-', 'formal/lean-toolchain', 'leanprover/lean4:v4.99.0\n')
        self.refresh('Math-')
        with self.assertRaisesRegex(ValueError, 'LOCK_TOOLCHAIN_DRIFT'):
            self.check()

    def test_path_dependency_outside_math_refused(self):
        self.change_lock(lambda d: d['packages'][-1].update(dir='../../../main/formal'),
                         package='specifications/lean_statement_proofs_20261011')
        with self.assertRaisesRegex(ValueError, 'LOCK_PATH_TARGET'):
            self.check()

    def test_noncanonical_path_dependency_aliases_refused(self):
        package = 'specifications/lean_statement_proofs_20261011'
        math = self.root/'Math-'
        alias = math/'specifications/path-alias'
        alias.symlink_to('../frontiers', target_is_directory=True)
        self.refresh('Math-')
        self.assertFalse((math/'specifications/missing').exists())
        self.assertEqual(alias.resolve(), math/'frontiers')
        for relative in ('../missing/../lean_statements_20261010',
                         '../path-alias/../lean_statements_20261010',
                         '.././lean_statements_20261010',
                         '..//lean_statements_20261010'):
            with self.subTest(relative=relative):
                self.change_lock(lambda d: d['packages'][-1].update(dir=relative), package=package)
                with self.assertRaisesRegex(ValueError, 'LOCK_PATH_TARGET'):
                    self.check()

    def test_path_target_name_mismatch_refused(self):
        self.change_lock(lambda d: d['packages'][-1].update(name='other'),
                         package='specifications/lean_statement_proofs_20261011')
        with self.assertRaisesRegex(ValueError, 'LOCK_PATH_NAME'):
            self.check()

    def test_path_target_configuration_name_mismatch_refused(self):
        write(self.root/'Math-', 'specifications/lean_statements_20261010/lakefile.toml', 'name = "wrong_target"\n')
        self.refresh('Math-')
        with self.assertRaisesRegex(ValueError, 'LOCK_PATH_CONFIG_NAME'):
            self.check()

    def test_dependency_url_credentials_refused(self):
        self.change_lock(lambda d: d['packages'][0].update(url='https://secret@github.com/fixture/dep0'))
        with self.assertRaises(ValueError):
            self.check()

    def test_lock_working_drift_refused(self):
        write(self.root/'Math-', 'formal/lake-manifest.json', '{}')
        with self.assertRaisesRegex(ValueError, 'SELECTED_INPUT_MISMATCH'):
            self.check()


class NetworkControls(Fixture):
    def setUp(self):
        super().setUp()
        self.assertTrue(hasattr(self.tool, 'fetch_exact_commit'), 'commit availability observer is not supplied')

    def request(self, commit=None):
        return dict(url='https://github.com/fixture/remote', commit=commit or self.vector['main'], roles=['fixture'])

    def translated(self):
        original = self.tool._network_process
        def run(command, env, **kwargs):
            command = [str(self.root/'main') if x == 'https://github.com/fixture/remote' else x for x in command]
            return original(command, dict(env, GIT_ALLOW_PROTOCOL='file'), **kwargs)
        return run

    def test_network_includes_canonical_historical_commit(self):
        snapshot = self.capture()
        requests = self.tool.required_remote_commits(snapshot, self.tool.verify_workspace(snapshot),
                                                      self.tool.verify_locks(snapshot))
        self.assertEqual(len(requests), 22)
        self.assertIn(('https://github.com/d6g8k5htny-coder/main', self.historical),
                      {(r['url'], r['commit']) for r in requests})
        self.assertIn('https://github.com/d6g8k5htny-coder/openclaw-custodian-validation',
                      {r['url'] for r in requests})

    def test_unadvertised_exact_commit_fetch_passes(self):
        repo = self.root/'main'
        original = self.vector['main']
        git(repo, 'commit', '--allow-empty', '-qm', 'unadvertised commit')
        wanted = git(repo, 'rev-parse', 'HEAD').decode().strip()
        git(repo, 'update-ref', 'HEAD', original)
        with mock.patch.object(self.tool, '_network_process', self.translated()):
            result = self.tool.fetch_exact_commit(self.request(wanted), Path(self.temp.name)/'stores')
        self.assertEqual(result['status'], 'FETCHED_COMMIT')
        self.assertEqual(result['commit'], wanted)

    def test_fetch_nonzero_cannot_pass(self):
        original = self.tool._network_process
        def failed(command, env, **kwargs):
            return (subprocess.CompletedProcess(command, 128, b'', b'private auth diagnostic')
                    if 'fetch' in command else original(command, env, **kwargs))
        with mock.patch.object(self.tool, '_network_process', failed):
            result = self.tool.fetch_exact_commit(self.request(), Path(self.temp.name)/'stores')
        self.assertEqual(result['status'], 'FETCH_FAILED')
        self.assertEqual(result['exit_code'], 128)

    def test_wrong_fetched_commit_refused(self):
        original = self.tool._network_process
        def empty_success(command, env, **kwargs):
            return (subprocess.CompletedProcess(command, 0, b'', b'')
                    if 'fetch' in command else original(command, env, **kwargs))
        with mock.patch.object(self.tool, '_network_process', empty_success):
            result = self.tool.fetch_exact_commit(self.request(), Path(self.temp.name)/'stores')
        self.assertEqual(result['status'], 'IDENTITY_MISMATCH')

    def test_transport_secrets_are_not_serialized(self):
        secret = 'SENTINEL_CREDENTIAL_DO_NOT_PUBLISH'
        original = self.tool._network_process
        def failed(command, env, **kwargs):
            return (subprocess.CompletedProcess(command, 128, secret.encode(), secret.encode())
                    if 'fetch' in command else original(command, env, **kwargs))
        with mock.patch.object(self.tool, '_network_process', failed):
            result = self.tool.fetch_exact_commit(self.request(), Path(self.temp.name)/'stores')
        self.assertNotIn(secret, json.dumps(result))
        self.assertEqual(result['status'], 'FETCH_FAILED')

    def test_credentialed_or_nonhttps_url_refused(self):
        for url in ('https://secret@github.com/fixture/remote', 'ext::touch /tmp/unwanted',
                    'file:///tmp/source', 'ssh://git@github.com/fixture/remote'):
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, 'REMOTE_URL'):
                self.tool.fetch_exact_commit(dict(self.request(), url=url), Path(self.temp.name)/'stores')

    def test_transport_does_not_change_source_refs_or_config(self):
        before = git(self.root/'main', 'show-ref'), (self.root/'main/.git/config').read_bytes()
        with mock.patch.object(self.tool, '_network_process', self.translated()):
            result = self.tool.fetch_exact_commit(self.request(), Path(self.temp.name)/'stores')
        self.assertEqual(result['status'], 'FETCHED_COMMIT')
        self.assertEqual(before, (git(self.root/'main', 'show-ref'), (self.root/'main/.git/config').read_bytes()))

    def test_timeout_reaps_child(self):
        pid_file = Path(self.temp.name)/'child.pid'
        command = [sys.executable, '-c', 'import os,time,pathlib;pathlib.Path(' + repr(str(pid_file)) +
                   ').write_text(str(os.getpid()));time.sleep(30)']
        with self.assertRaises(subprocess.TimeoutExpired):
            self.tool._network_process(command, self.tool._read_env(), timeout=0.2)
        pid = int(pid_file.read_text())
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)

    def test_cleanup_failure_has_explicit_status(self):
        original = self.tool._network_process
        def failed(command, env, **kwargs):
            if 'fetch' in command:
                raise ValueError('NETWORK_CLEANUP_ERROR')
            return original(command, env, **kwargs)
        with mock.patch.object(self.tool, '_network_process', failed):
            result = self.tool.fetch_exact_commit(self.request(), Path(self.temp.name)/'stores')
        self.assertEqual(result['status'], 'CLEANUP_ERROR')


class CliControls(Fixture):
    def setUp(self):
        super().setUp()
        self.assertTrue(hasattr(self.tool, 'verify'), 'composed verifier is not supplied')

    @staticmethod
    def available(request, storage):
        return dict(request, status='FETCHED_COMMIT', exit_code=0)

    def test_offline_report_keeps_scope_and_no_network_claim(self):
        result = self.tool.verify(self.root, self.vector_file)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['network']['status'], 'NOT_REQUESTED')
        self.assertFalse(result['cbz_green'])
        self.assertFalse(result['semantic_claim_completeness'])
        self.assertEqual(result['git_hygiene'], 'NOT_ASSESSED')
        self.assertEqual(result['full_tracked_working_parity'], 'NOT_ASSESSED')

    def test_network_failure_blocks_aggregate(self):
        def failed(request, storage):
            return dict(request, status='FETCH_FAILED', exit_code=128)
        result = self.tool.verify(self.root, self.vector_file, network=True, fetcher=failed)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['network']['status'], 'FAIL')
        self.assertEqual(len(result['network']['observations']), 22)

    def test_cleanup_failure_stops_more_requests(self):
        observed=[]
        def failed(request, storage):
            observed.append(request)
            return dict(request,status='CLEANUP_ERROR',exit_code=None)
        result=self.tool.verify(self.root,self.vector_file,network=True,fetcher=failed)
        self.assertEqual(result['status'],'FAIL')
        self.assertEqual(len(observed),1)

    def test_local_failure_does_not_contact_network(self):
        self.vector.pop('sandbox'); self.save_vector()
        def forbidden(request, storage):
            self.fail('invalid local sources must not start transport')
        result = self.tool.verify(self.root, self.vector_file, network=True, fetcher=forbidden)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['network']['observations'], [])

    def test_midrun_head_drift_refused(self):
        changed = False
        def racing(request, storage):
            nonlocal changed
            if not changed:
                changed = True
                git(self.root/'main', 'commit', '--allow-empty', '-qm', 'race')
            return self.available(request, storage)
        result = self.tool.verify(self.root, self.vector_file, network=True, fetcher=racing)
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('HEAD_MISMATCH', result['errors'])

    def test_selected_input_change_during_network_refused(self):
        def racing(request, storage):
            write(self.root/'main', 'formal/lean-toolchain', 'changed\n')
            return self.available(request, storage)
        result = self.tool.verify(self.root, self.vector_file, network=True, fetcher=racing)
        self.assertEqual(result['status'], 'FAIL')

    def test_no_default_tip_equality_requirement(self):
        result = self.tool.verify(self.root, self.vector_file, network=True, fetcher=self.available)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['network']['status'], 'PASS')

    def test_cli_new_output_and_overwrite_refusal(self):
        output = Path(self.temp.name)/'result.json'
        argv = ['--root', str(self.root), '--vector', str(self.vector_file), '--output', str(output)]
        self.assertEqual(self.tool.main(argv), 0)
        raw = output.read_bytes()
        self.assertEqual(json.loads(raw)['status'], 'PASS')
        self.assertEqual(output.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.tool.main(argv), 2)
        self.assertEqual(output.read_bytes(), raw)

    def test_cli_source_output_and_symlink_refused(self):
        args = ['--root', str(self.root), '--vector', str(self.vector_file), '--output']
        self.assertEqual(self.tool.main(args + [str(self.root/'main/result.json')]), 2)
        link = Path(self.temp.name)/'output-link'
        link.symlink_to(self.vector_file)
        self.assertEqual(self.tool.main(args + [str(link)]), 2)

    def test_raw_transport_secret_never_enters_report(self):
        secret = 'PRIVATE_TRANSPORT_SENTINEL'
        def failed(request, storage):
            raise OSError(secret)
        result = self.tool.verify(self.root, self.vector_file, network=True, fetcher=failed)
        self.assertNotIn(secret, json.dumps(result))
        self.assertEqual(result['status'], 'FAIL')


class VectorSources(Fixture):
    def test_exact_twelve_sources_and_index_parity(self):
        data = self.capture()
        self.assertEqual(set(data['repositories']), set(NAMES))
        self.assertEqual(data['repositories']['main']['commit'], self.vector['main'])
        self.assertEqual(data['full_tracked_working_parity'], 'NOT_ASSESSED')
        self.assertEqual(data['git_hygiene'], 'NOT_ASSESSED')

    def test_vector_omission_rejected(self):
        self.vector.pop('sandbox'); self.save_vector()
        with self.assertRaisesRegex(ValueError, 'VECTOR_REPOSITORIES'):
            self.tool.load_vector(self.vector_file)

    def test_vector_extra_or_duplicate_key_refused(self):
        self.vector['extra'] = 'a' * 40; self.save_vector()
        with self.assertRaisesRegex(ValueError, 'VECTOR_REPOSITORIES'):
            self.tool.load_vector(self.vector_file)
        self.vector_file.write_text('{"schema":"x","schema":"y","repositories":{}}')
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_JSON'):
            self.tool.load_vector(self.vector_file)

    def test_noncommit_or_floating_revision_refused(self):
        for value in ('main', 'a' * 39, True, 1.0):
            self.vector['main'] = value; self.save_vector()
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.capture()

    def test_wrong_checkout_head_refused(self):
        git(self.root/'main', 'commit', '--allow-empty', '-qm', 'changed head')
        with self.assertRaisesRegex(ValueError, 'HEAD_MISMATCH'):
            self.capture()

    def test_staged_change_refused(self):
        write(self.root/'main', 'source.txt', 'staged\n')
        git(self.root/'main', 'add', 'source.txt')
        with self.assertRaisesRegex(ValueError, 'INDEX_TREE_MISMATCH'):
            self.capture()

    def test_linked_worktree_uses_its_own_index(self):
        repo = self.root/'main'
        (self.root/'main').rename(self.root/'storage')
        git(self.root/'storage', 'worktree', 'add', '--detach', str(repo), self.vector['main'])
        write(self.root/'storage', 'source.txt', 'staged elsewhere\n')
        git(self.root/'storage', 'add', 'source.txt')
        self.assertEqual(self.capture()['repositories']['main']['commit'], self.vector['main'])

    def test_selected_input_working_substitution_refused(self):
        write(self.root/'main', 'formal/lean-toolchain', 'substituted\n')
        with self.assertRaisesRegex(ValueError, 'SELECTED_INPUT_MISMATCH'):
            self.capture()

    def test_selected_input_symlink_refused(self):
        p = self.root/'main/formal/lean-toolchain'
        p.rename(p.with_name('original'))
        p.symlink_to('original')
        with self.assertRaisesRegex(ValueError, 'SELECTED_INPUT'):
            self.capture()

    def test_selected_input_executable_mode_drift_refused(self):
        path=self.root/'main/formal/lean-toolchain'
        path.chmod(path.stat().st_mode | 0o100)
        with self.assertRaisesRegex(ValueError,'SELECTED_INPUT_MODE'):
            self.capture()

    def test_ambient_git_override_cannot_substitute_source(self):
        with mock.patch.dict(os.environ, {'GIT_DIR': str(self.root/'Math-/.git'),
                                          'GIT_WORK_TREE': str(self.root/'Math-')}):
            self.assertEqual(self.capture()['repositories']['main']['commit'], self.vector['main'])

    def test_no_git_status_or_filter_execution(self):
        marker = Path(self.temp.name)/'executed'
        command = 'touch ' + str(marker)
        for name in ('main', 'Universal-Law-Workspace'):
            git(self.root/name, 'config', 'filter.probe.clean', command)
            git(self.root/name, 'config', 'core.fsmonitor', command)
        original = subprocess.run
        def guarded(args, *a, **kw):
            self.assertNotIn('status', args, 'selected source Git status is forbidden')
            return original(args, *a, **kw)
        with mock.patch.object(self.tool.subprocess, 'run', guarded):
            self.capture()
        self.assertFalse(marker.exists())

    def test_oversized_control_refused(self):
        with mock.patch.object(self.tool, 'CONTROL_LIMIT', 8):
            with self.assertRaisesRegex(ValueError, 'CONTROL_SIZE'):
                self.tool.load_vector(self.vector_file)

    def test_full_working_parity_is_not_inferred(self):
        write(self.root/'main', 'source.txt', 'unstaged outside selected scope\n')
        self.assertEqual(self.capture()['full_tracked_working_parity'], 'NOT_ASSESSED')


if __name__ == '__main__':
    unittest.main()
