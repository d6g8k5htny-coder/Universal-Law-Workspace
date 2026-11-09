"""Thirteen finite weakening controls; native selected-body failures only earn kills."""
from __future__ import annotations

import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT/'tools/verify_federation_vector.py'
MUTANTS = (
    ('vector-set', 'set(values) == set(REPOSITORIES)', 'True',
     'VectorSources.test_vector_omission_rejected', 'ValueError not raised'),
    ('head-match', "require(head == vector[name], 'HEAD_MISMATCH')", 'None',
     'VectorSources.test_wrong_checkout_head_refused', 'ValueError not raised'),
    ('index-parity', "require(index == tree, 'INDEX_TREE_MISMATCH')", 'None',
     'VectorSources.test_staged_change_refused', 'ValueError not raised'),
    ('selected-input', "require(raw == binding['_raw'], 'SELECTED_INPUT_MISMATCH')", 'None',
     'VectorSources.test_selected_input_working_substitution_refused', 'ValueError not raised'),
    ('sandbox-pin', "require(pin['path'] == path and links[path] == pin['pinned_sha'] == snapshot['_vector'][child],",
     'require(True,', 'WorkspaceControls.test_sandbox_pin_skew_rejected', 'ValueError not raised'),
    ('canonical-blob', "require(actual['blob'] == blob, 'CANONICAL_BLOB')", 'None',
     'WorkspaceControls.test_canonical_wrong_blob_refused', 'ValueError not raised'),
    ('lock-commit', "require(type(dependency['rev']) is str and HEX40.fullmatch(dependency['rev']), 'LOCK_COMMIT')", 'None',
     'LockControls.test_floating_resolved_revision_refused', 'ValueError not raised'),
    ('path-resolution', "target = posixpath.normpath(package + '/' + relative)",
     "target = 'specifications/lean_statements_20261010'",
     'LockControls.test_path_dependency_outside_math_refused', 'ValueError not raised'),
    ('network-failure', "require(all(row['status'] == 'FETCHED_COMMIT' for row in report['network']['observations']),",
     'require(True,', 'CliControls.test_network_failure_blocks_aggregate', "'PASS' != 'FAIL'"),
    ('canonical-request', "for row in workspace['canonical']:", 'for row in ():',
     'NetworkControls.test_network_includes_canonical_historical_commit', '21 != 22'),
    ('fetched-identity', "result['status'] = 'FETCHED_COMMIT' if actual == commit else 'IDENTITY_MISMATCH'",
     "result['status'] = 'FETCHED_COMMIT'", 'NetworkControls.test_wrong_fetched_commit_refused',
     "'FETCHED_COMMIT' != 'IDENTITY_MISMATCH'"),
    ('final-recheck', '                recheck_sources(snapshot)', '                None',
     'CliControls.test_midrun_head_drift_refused', "'PASS' != 'FAIL'"),
    ('canonical-kind',
     "require(read_git(snapshot['repositories'][short]['_path'],\n"
     "                         ('cat-file', '-t', commit)).strip() == b'commit', 'CANONICAL_COMMIT')",
     'None', 'WorkspaceControls.test_explicit_canonical_tree_oid_refused', 'ValueError not raised'),
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def failure_origin(error, selected_code):
    frames = []
    trace = error[2]
    while trace:
        frames.append(trace.tb_frame.f_code)
        trace = trace.tb_next
    outside = [code for code in frames if '/unittest/' not in code.co_filename.replace('\\', '/')]
    dispatch = any(code.co_name == '_callTestMethod' and '/unittest/' in code.co_filename.replace('\\', '/')
                   for code in frames)
    lifecycle = any(code.co_name in ('_callSetUp', '_callTearDown', '_callCleanup') and
                    '/unittest/' in code.co_filename.replace('\\', '/') for code in frames)
    return bool(issubclass(error[0], AssertionError) and outside and outside[-1] is selected_code
                and dispatch and not lifecycle)


def intended_failure(process, event, test, nonce, source_hash, reason):
    if type(event) is not dict:
        return False
    failures = event.get('failures')
    counts = ('tests_run', 'errors', 'skipped', 'expected_failures', 'unexpected_successes')
    if (any(type(event.get(key)) is not int for key in counts) or type(failures) is not list
            or len(failures) != 1 or type(failures[0]) is not dict
            or set(failures[0]) != {'selected_body', 'message'}
            or failures[0]['selected_body'] is not True or type(failures[0]['message']) is not str):
        return False
    return (process.returncode == 1 and type(event) is dict
        and event.get('test') == test and event.get('nonce') == nonce
        and event.get('source_before') == event.get('source_after') == source_hash
        and event.get('tests_run') == 1 and event.get('errors') == event.get('skipped') == 0
        and event.get('expected_failures') == event.get('unexpected_successes') == 0
        and reason in event['failures'][0]['message']
        and re.search(r'^Ran 1 test in ', process.stderr, re.M) is not None
        and process.stderr.count('FAIL: ') == 1
        and re.search(r'^FAIL: ' + re.escape(test.split('.')[-1]) + r' ', process.stderr, re.M) is not None
        and process.stderr.rstrip().endswith('FAILED (failures=1)')
        and process.stderr.count('Traceback (most recent call last)') == 1
        and 'ERROR:' not in process.stderr and 'skipped' not in process.stderr)


def run_child(test):
    import test_verify_federation_vector as controls
    cls, method = test.split('.')
    selected = inspect.getattr_static(getattr(controls, cls), method).__code__
    record = dict(test=test, nonce=os.environ['CBZ_VECTOR_NONCE'],
                  source_before=digest(controls.TOOL), failures=[])
    class Observed(unittest.TextTestResult):
        def addFailure(self, case, error):
            record['failures'].append(dict(selected_body=failure_origin(error, selected), message=str(error[1])))
            super().addFailure(case, error)
    suite = unittest.defaultTestLoader.loadTestsFromName(test, controls)
    result = unittest.TextTestRunner(verbosity=2, resultclass=Observed).run(suite)
    record.update(source_after=digest(controls.TOOL), tests_run=result.testsRun,
        errors=len(result.errors), skipped=len(result.skipped), expected_failures=len(result.expectedFailures),
        unexpected_successes=len(result.unexpectedSuccesses))
    Path(os.environ['CBZ_VECTOR_EVENT']).write_text(json.dumps(record))
    return 0 if result.wasSuccessful() else 1


class MutationControls(unittest.TestCase):
    def test_actual_subject_crash_skip_syntax_and_silent_exit_are_not_kills(self):
        source = TOOL.read_text()
        anchor = 'def capture_sources(root: Path, vector: dict[str, str]) -> dict:\n'
        cases = {'subject': source.replace(anchor, anchor + "    raise AssertionError('subject failure')\n", 1),
                 'skip': source.replace(anchor, anchor + "    raise __import__('unittest').SkipTest('subject skip')\n", 1),
                 'silent': source.replace(anchor, anchor + '    os._exit(86)\n', 1),
                 'syntax': 'not valid Python !\n'}
        test = 'VectorSources.test_exact_twelve_sources_and_index_parity'
        with tempfile.TemporaryDirectory(prefix='vector-grader-adverse-') as temporary:
            folder = Path(temporary)
            for label, content in cases.items():
                candidate = folder/(label+'.py'); candidate.write_text(content)
                event_path = folder/(label+'.json'); nonce = secrets.token_hex(16)
                env = dict(os.environ, CBZ_VECTOR_UNDER_TEST=str(candidate),
                    CBZ_VECTOR_EVENT=str(event_path), CBZ_VECTOR_NONCE=nonce)
                flags = ['-O'] if sys.flags.optimize else []
                child = subprocess.run([sys.executable,'-B',*flags,'-S',str(Path(__file__).resolve()),
                    '--child',test],env=env,text=True,capture_output=True,timeout=180)
                event = json.loads(event_path.read_text()) if event_path.exists() else None
                with self.subTest(adverse=label):
                    self.assertFalse(intended_failure(child,event,test,nonce,digest(candidate),''))
                    if label == 'subject':
                        self.assertEqual(event['failures'][0]['selected_body'], False)

    def test_malformed_counts_nonce_and_origin_cannot_qualify(self):
        test='X.test_x'; nonce='0'*32; source_hash='a'*64
        event=dict(test=test,nonce=nonce,source_before=source_hash,source_after=source_hash,
            tests_run=1,errors=0,skipped=0,expected_failures=0,unexpected_successes=0,
            failures=[dict(selected_body=True,message='reason')])
        process=subprocess.CompletedProcess([],1,'',
            'FAIL: test_x (X)\nTraceback (most recent call last)\nAssertionError: reason\n'
            'Ran 1 test in 1s\nFAILED (failures=1)')
        self.assertTrue(intended_failure(process,event,test,nonce,source_hash,'reason'))
        for changes in (dict(tests_run=0),dict(tests_run=2),dict(tests_run=True),dict(errors=1),
                        dict(errors=False),dict(skipped=1),dict(nonce='f'*32),dict(source_after='b'*64),
                        dict(failures=[dict(selected_body=False,message='reason')])):
            with self.subTest(changes=changes):
                self.assertFalse(intended_failure(process,dict(event,**changes),test,nonce,source_hash,'reason'))

    def test_empty_failure_event_is_refused_without_crash(self):
        event = dict(test='X.test_x',nonce='0'*32,source_before='a'*64,source_after='a'*64,
            tests_run=1,errors=0,skipped=0,expected_failures=0,unexpected_successes=0,failures=[])
        process = subprocess.CompletedProcess([],1,'','FAIL: test_x (X)\nRan 1 test in 1s\nFAILED (failures=1)')
        try:
            result = intended_failure(process,event,'X.test_x','0'*32,'a'*64,'reason')
        except (IndexError, KeyError, TypeError):
            result = 'classifier crashed'
        self.assertIs(result, False)

    def test_thirteen_source_mutants_are_killed_by_designated_body_assertions(self):
        source = TOOL.read_text()
        parent = os.environ.get('CBZ_VECTOR_MUTATION_EVIDENCE')
        if parent:
            Path(parent).mkdir(parents=True, exist_ok=True, mode=0o700)
            directory = Path(tempfile.mkdtemp(prefix='campaign-', dir=parent))
        else:
            temporary = tempfile.TemporaryDirectory(prefix='vector-mutants-')
            self.addCleanup(temporary.cleanup)
            directory = Path(temporary.name)
        results = []
        for label, before, after, test, reason in MUTANTS:
            with self.subTest(mutation=label):
                self.assertEqual(source.count(before), 1, 'source mutation anchor must be unique')
                for kind, content in [('baseline', source), ('mutant', source.replace(before, after, 1))]:
                    compile(content, label, 'exec')
                    candidate = directory/(label + '-' + kind + '.py')
                    candidate.write_text(content)
                    event_path = directory/(label + '-' + kind + '.json')
                    nonce = secrets.token_hex(16)
                    env = dict(os.environ, CBZ_VECTOR_UNDER_TEST=str(candidate),
                               CBZ_VECTOR_EVENT=str(event_path), CBZ_VECTOR_NONCE=nonce)
                    flags = ['-O'] if sys.flags.optimize else []
                    process = subprocess.run([sys.executable, '-B', *flags, '-S', str(Path(__file__).resolve()),
                        '--child', test], env=env, text=True, capture_output=True, timeout=180)
                    (directory/(label+'-'+kind+'.stdout')).write_text(process.stdout)
                    (directory/(label+'-'+kind+'.stderr')).write_text(process.stderr)
                    event = json.loads(event_path.read_text()) if event_path.exists() else None
                    if kind == 'baseline':
                        self.assertEqual(process.returncode, 0, process.stderr)
                        self.assertEqual(event['tests_run'], 1)
                        self.assertEqual(event['failures'], [])
                        self.assertEqual(event['errors'] + event['skipped'], 0)
                        self.assertTrue(process.stderr.rstrip().endswith('OK'))
                    else:
                        self.assertTrue(intended_failure(process,event,test,nonce,digest(candidate),reason), process.stderr)
                    results.append(dict(mutation=label, kind=kind, test=test, source_sha256=digest(candidate),
                        exit_code=process.returncode, stderr_sha256=hashlib.sha256(process.stderr.encode()).hexdigest()))
        (directory/'summary.json').write_text(json.dumps(results,indent=2)+'\n')

    def test_subject_assertion_is_not_selected_body_failure(self):
        case = unittest.TestCase()
        def subject():
            raise AssertionError('subject-origin crash')
        def selected():
            subject()
        try:
            selected()
        except AssertionError:
            self.assertFalse(failure_origin(sys.exc_info(), selected.__code__))

    def test_forged_transcript_without_native_event_is_not_kill(self):
        process = subprocess.CompletedProcess([], 1, '', 'FAIL: test_x (X)\nRan 1 test in 1s\nFAILED (failures=1)')
        self.assertFalse(intended_failure(process, None, 'X.test_x', '0'*32, 'a'*64, 'reason'))

    def test_lifecycle_assertion_is_not_selected_dispatch(self):
        def selected():
            raise AssertionError('called by fixture')
        try:
            selected()
        except AssertionError:
            self.assertFalse(failure_origin(sys.exc_info(), selected.__code__))


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--child':
        raise SystemExit(run_child(sys.argv[2]))
    unittest.main()
