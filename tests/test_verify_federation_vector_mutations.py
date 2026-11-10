"""Thirteen finite weakening controls; native selected-body failures only earn kills."""
from __future__ import annotations

import ast
import dis
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
import unittest.mock

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


def unittest_code_objects(container, module, seen=None):
    """Collect actual unittest function code; filenames are not authority."""
    seen = set() if seen is None else seen
    if id(container) in seen:
        return []
    seen.add(id(container))
    result = []
    for value in vars(container).values():
        if isinstance(value, (staticmethod, classmethod)):
            value = value.__func__
        wrapped = set()
        while inspect.isfunction(value) and id(value) not in wrapped:
            wrapped.add(id(value))
            result.append(value.__code__)
            value = getattr(value, '__wrapped__', None)
        if inspect.isclass(value) and value.__module__ == module:
            result.extend(unittest_code_objects(value, module, seen))
    return result


UNITTEST_CODES = (unittest_code_objects(unittest.case, unittest.case.__name__) +
                  unittest_code_objects(unittest.mock, unittest.mock.__name__))
DISPATCH_CODE = unittest.TestCase._callTestMethod.__code__
LIFECYCLE_CODES = tuple(getattr(unittest.TestCase, name).__code__ for name in
                        ('_callSetUp', '_callTearDown', '_callCleanup', 'doCleanups'))


def authorized_oracle(selected_code, lasti, following):
    """Admit only observed assertion call sites and their exact oracle paths.

    The source position is an additional restriction on the selected code
    identity, never a replacement for that identity or for the live traceback.
    Unsupported methods, bytecode positions and oracle paths fail closed.
    """
    paths = {
        'assertEqual': (
            (unittest.TestCase.assertEqual.__code__, unittest.TestCase._baseAssertEqual.__code__),
            (unittest.TestCase.assertEqual.__code__, unittest.TestCase.assertMultiLineEqual.__code__,
             unittest.TestCase.fail.__code__),
        ),
        'assertRaisesRegex': (
            (unittest.case._AssertRaisesContext.__exit__.__code__,
             unittest.case._BaseTestCaseContext._raiseFailure.__code__),
        ),
    }
    try:
        source = Path(selected_code.co_filename).read_text(encoding='utf-8')
        parsed = ast.parse(source)
        compiled = compile(source, selected_code.co_filename, 'exec', dont_inherit=True,
                           optimize=sys.flags.optimize)
        pending, matches = [compiled], []
        while pending:
            current = pending.pop()
            if (current.co_qualname == selected_code.co_qualname
                    and current.co_firstlineno == selected_code.co_firstlineno):
                matches.append(current)
            pending.extend(item for item in current.co_consts if isinstance(item, types.CodeType))
        if (len(matches) != 1 or matches[0] != selected_code
                or matches[0].co_linetable != selected_code.co_linetable
                or matches[0].co_exceptiontable != selected_code.co_exceptiontable):
            return False
        methods = [node for node in ast.walk(parsed)
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                   and node.name == selected_code.co_name and node.lineno == selected_code.co_firstlineno]
        if len(methods) != 1:
            return False
        ins = next(i for i in dis.get_instructions(selected_code, show_caches=True) if i.offset == lasti)
        pos = ins.positions
        if pos is None:
            return False
        observed = (pos.lineno, pos.end_lineno, pos.col_offset, pos.end_col_offset)
        for call in ast.walk(methods[0]):
            if (not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute)
                    or not isinstance(call.func.value, ast.Name) or call.func.value.id != 'self'
                    or call.func.attr not in paths):
                continue
            positions = {(call.lineno, call.end_lineno, call.col_offset, call.end_col_offset)}
            if call.func.attr == 'assertRaisesRegex':
                for context in ast.walk(methods[0]):
                    if (isinstance(context, ast.With) and len(context.items) == 1
                            and context.items[0].context_expr is call):
                        positions.add((context.lineno, context.end_lineno,
                                       context.col_offset, context.end_col_offset))
            if observed not in positions:
                continue
            for path in paths[call.func.attr]:
                if len(path) == len(following) and all(left is right for left, right in zip(path, following)):
                    return True
    except (OSError, UnicodeError, SyntaxError, ValueError, TypeError, StopIteration):
        return False
    return False


def failure_origin(error, selected_code):
    frames = []
    offsets = []
    trace = error[2]
    while trace:
        frames.append(trace.tb_frame.f_code)
        offsets.append(trace.tb_lasti)
        trace = trace.tb_next
    selected = [index for index, code in enumerate(frames) if code is selected_code]
    if len(selected) != 1 or type(error[1]) is not AssertionError:
        return False
    position = selected[0]
    dispatch = any(code is DISPATCH_CODE for code in frames[:position])
    lifecycle = any(any(code is lifecycle_code for lifecycle_code in LIFECYCLE_CODES)
                    for code in frames)
    return bool(dispatch and not lifecycle and
                all(any(code is oracle for oracle in UNITTEST_CODES)
                    for code in frames[position + 1:]) and
                authorized_oracle(selected_code, offsets[position], frames[position + 1:]))


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
    def test_deferred_subject_assertions_in_unittest_code_are_not_kills(self):
        source = TOOL.read_text()
        request_anchor = 'def required_remote_commits(snapshot: dict, workspace: dict, locks: dict) -> list[dict]:\n'
        fetch_anchor = 'def fetch_exact_commit(request: dict, storage: Path) -> dict:\n'
        self.assertEqual(source.count(request_anchor), 1)
        self.assertEqual(source.count(fetch_anchor), 1)
        cases = (
            ('mock-len', request_anchor,
             "    import unittest.mock\n"
             "    result = unittest.mock.MagicMock()\n"
             "    result.__len__.side_effect = AssertionError('21 != 22')\n"
             "    return result\n",
             'NetworkControls.test_network_includes_canonical_historical_commit', '21 != 22'),
            ('case-len', request_anchor,
             "    import unittest\n"
             "    class DeferredLength:\n"
             "        __len__ = unittest.TestCase.fail\n"
             "        @staticmethod\n"
             "        def failureException(message):\n"
             "            return AssertionError('21 != 22')\n"
             "    return DeferredLength()\n",
             'NetworkControls.test_network_includes_canonical_historical_commit', '21 != 22'),
            ('partial-len', request_anchor,
             "    import functools, unittest\n"
             "    class DeferredLength:\n"
             "        __len__ = functools.partial(unittest.TestCase().assertEqual, 21, 22)\n"
             "    return DeferredLength()\n",
             'NetworkControls.test_network_includes_canonical_historical_commit', '21 != 22'),
            ('case-equality', fetch_anchor,
             "    import unittest\n"
             "    class DeferredEquality:\n"
             "        __eq__ = unittest.TestCase.fail\n"
             "        @staticmethod\n"
             "        def failureException(message):\n"
             "            return AssertionError(\"'FETCHED_COMMIT' != 'IDENTITY_MISMATCH'\")\n"
             "    return {'status': DeferredEquality()}\n",
             'NetworkControls.test_wrong_fetched_commit_refused', "'FETCHED_COMMIT' != 'IDENTITY_MISMATCH'"),
        )
        with tempfile.TemporaryDirectory(prefix='vector-deferred-origin-') as tmp:
            folder = Path(tmp)
            for label, anchor, body, test, reason in cases:
                candidate = folder / (label + '.py')
                candidate.write_text(source.replace(anchor, anchor + body, 1))
                for optimized in (False, True):
                    with self.subTest(case=label, optimized=optimized):
                        event_path = folder / (label + '-' + str(optimized) + '.json')
                        nonce = secrets.token_hex(16)
                        env = dict(os.environ, CBZ_VECTOR_UNDER_TEST=str(candidate),
                                   CBZ_VECTOR_EVENT=str(event_path), CBZ_VECTOR_NONCE=nonce)
                        child = subprocess.run([sys.executable, '-B', *(['-O'] if optimized else []),
                                                '-S', str(Path(__file__).resolve()), '--child', test],
                                               env=env, text=True, capture_output=True, timeout=180)
                        self.assertEqual(child.returncode, 1, child.stderr)
                        event = json.loads(event_path.read_text())
                        self.assertEqual(event['tests_run'], 1)
                        self.assertEqual(event['errors'] + event['skipped'], 0)
                        self.assertFalse(event['failures'][0]['selected_body'], child.stderr)
                        self.assertFalse(intended_failure(child, event, test, nonce, digest(candidate), reason))

    def test_subject_assertion_from_unittest_named_path_is_not_a_kill(self):
        source = TOOL.read_text()
        anchor = 'def load_vector(path: Path) -> dict[str, str]:\n'
        self.assertEqual(source.count(anchor), 1)
        changed = source.replace(anchor, anchor + "    raise AssertionError('ValueError not raised')\n", 1)
        selected = 'VectorSources.test_vector_omission_rejected'
        for optimized in (False, True):
            with self.subTest(optimized=optimized), tempfile.TemporaryDirectory(prefix='vector-origin-adverse-') as tmp:
                folder = Path(tmp)/'unittest'
                folder.mkdir()
                candidate = folder/'subject.py'
                candidate.write_text(changed)
                event_path = Path(tmp)/'event.json'
                nonce = secrets.token_hex(16)
                env = dict(os.environ, CBZ_VECTOR_UNDER_TEST=str(candidate),
                           CBZ_VECTOR_EVENT=str(event_path), CBZ_VECTOR_NONCE=nonce)
                child = subprocess.run([sys.executable, '-B', *(['-O'] if optimized else []),
                                        '-S', str(Path(__file__).resolve()), '--child', selected],
                                       env=env, text=True, capture_output=True, timeout=180)
                event = json.loads(event_path.read_text())
                self.assertEqual(child.returncode, 1)
                self.assertFalse(event['failures'][0]['selected_body'])
                self.assertFalse(intended_failure(child, event, selected, nonce, digest(candidate),
                                                  'ValueError not raised'))

    def test_origin_guard_removal_reopens_real_spoofed_subject(self):
        harness = Path(__file__).read_text()
        guard = ('all(any(code is oracle for oracle in ' +
                 'UNITTEST_CODES)\n                    for code in frames[position + 1:])')
        self.assertEqual(harness.count(guard), 1)
        mutant = harness.replace(guard, 'all(True for code in frames[position + 1:])', 1)
        callsite = ('authorized_' + 'oracle(selected_code, offsets[position], frames[position + 1:])')
        self.assertEqual(mutant.count(callsite), 1)
        mutant = mutant.replace(callsite, 'True', 1)
        source = TOOL.read_text()
        anchor = 'def load_vector(path: Path) -> dict[str, str]:\n'
        self.assertEqual(source.count(anchor), 1)
        subject = source.replace(anchor, anchor + "    raise AssertionError('ValueError not raised')\n", 1)
        selected = 'VectorSources.test_vector_omission_rejected'
        for optimized in (False, True):
            with self.subTest(optimized=optimized), tempfile.TemporaryDirectory(prefix='vector-origin-self-') as tmp:
                base = Path(tmp)
                (base/'tests').mkdir(); (base/'tools').mkdir(); (base/'unittest').mkdir()
                shutil.copy2(ROOT/'tests/test_verify_federation_vector.py', base/'tests')
                for name in ('check_workspace.py', 'verify_pins.py', 'verify_canonical_inputs.py'):
                    shutil.copy2(ROOT/'tools'/name, base/'tools'/name)
                candidate = base/'unittest/subject.py'; candidate.write_text(subject)
                for label, code, expected in (('baseline', harness, False), ('mutant', mutant, True)):
                    with self.subTest(version=label):
                        runner = base/'tests/vector_harness.py'; runner.write_text(code)
                        event_path = base/(label+'.json'); nonce = secrets.token_hex(16)
                        env = dict(os.environ, CBZ_VECTOR_UNDER_TEST=str(candidate),
                                   CBZ_VECTOR_EVENT=str(event_path), CBZ_VECTOR_NONCE=nonce)
                        child = subprocess.run([sys.executable, '-B', *(['-O'] if optimized else []),
                                                '-S', str(runner), '--child', selected], env=env,
                                               text=True, capture_output=True, timeout=180)
                        event = json.loads(event_path.read_text())
                        self.assertEqual(child.returncode, 1)
                        self.assertEqual(intended_failure(child, event, selected, nonce, digest(candidate),
                                                          'ValueError not raised'), expected)

    def test_callsite_and_oracle_path_removals_reopen_deferred_failures(self):
        harness = Path(__file__).read_text()
        callsite_guard = ('if observed not in ' + 'positions:')
        path_guard = ('if len(path) == len(following) and '
                      + 'all(left is right for left, right in zip(path, following)):')
        self.assertEqual(harness.count(callsite_guard), 1)
        self.assertEqual(harness.count(path_guard), 1)
        source = TOOL.read_text()
        request_anchor = 'def required_remote_commits(snapshot: dict, workspace: dict, locks: dict) -> list[dict]:\n'
        fetch_anchor = 'def fetch_exact_commit(request: dict, storage: Path) -> dict:\n'
        self.assertEqual(source.count(request_anchor), 1)
        self.assertEqual(source.count(fetch_anchor), 1)
        cases = (
            ('callsite', harness.replace(callsite_guard, 'if False:', 1), request_anchor,
             "    import functools, unittest\n"
             "    class DeferredLength:\n"
             "        __len__ = functools.partial(unittest.TestCase().assertEqual, 21, 22)\n"
             "    return DeferredLength()\n",
             'NetworkControls.test_network_includes_canonical_historical_commit', '21 != 22'),
            ('path', harness.replace(path_guard, 'if True:', 1), fetch_anchor,
             "    import unittest\n"
             "    class DeferredEquality:\n"
             "        __eq__ = unittest.TestCase.fail\n"
             "        @staticmethod\n"
             "        def failureException(message):\n"
             "            return AssertionError(\"'FETCHED_COMMIT' != 'IDENTITY_MISMATCH'\")\n"
             "    return {'status': DeferredEquality()}\n",
             'NetworkControls.test_wrong_fetched_commit_refused', "'FETCHED_COMMIT' != 'IDENTITY_MISMATCH'"),
        )
        with tempfile.TemporaryDirectory(prefix='vector-deferred-self-') as tmp:
            base = Path(tmp)
            (base/'tests').mkdir(); (base/'tools').mkdir(); (base/'subjects').mkdir()
            shutil.copy2(ROOT/'tests/test_verify_federation_vector.py', base/'tests')
            for name in ('check_workspace.py', 'verify_pins.py', 'verify_canonical_inputs.py'):
                shutil.copy2(ROOT/'tools'/name, base/'tools'/name)
            for label, mutant, anchor, body, selected, reason in cases:
                candidate = base/'subjects'/(label + '.py')
                candidate.write_text(source.replace(anchor, anchor + body, 1))
                for optimized in (False, True):
                    for version, code, expected in (('baseline', harness, False), ('mutant', mutant, True)):
                        with self.subTest(guard=label, optimized=optimized, version=version):
                            runner = base/'tests/vector_harness.py'; runner.write_text(code)
                            event_path = base/(label + '-' + str(optimized) + '-' + version + '.json')
                            nonce = secrets.token_hex(16)
                            env = dict(os.environ, CBZ_VECTOR_UNDER_TEST=str(candidate),
                                       CBZ_VECTOR_EVENT=str(event_path), CBZ_VECTOR_NONCE=nonce)
                            child = subprocess.run([sys.executable, '-B', *(['-O'] if optimized else []),
                                                    '-S', str(runner), '--child', selected], env=env,
                                                   text=True, capture_output=True, timeout=180)
                            self.assertEqual(child.returncode, 1, child.stderr)
                            event = json.loads(event_path.read_text())
                            self.assertEqual(intended_failure(child, event, selected, nonce, digest(candidate), reason),
                                             expected, child.stderr)

    def test_oracle_positions_refuse_changed_or_missing_selected_source(self):
        original = (ROOT/'tests/test_verify_federation_vector.py').read_text()
        before = 'self.assertEqual(len(requests), 22)'
        self.assertEqual(original.count(before), 1)
        with tempfile.TemporaryDirectory(prefix='vector-oracle-source-') as tmp:
            path = Path(tmp)/'selected_controls.py'
            path.write_text(original)
            spec = importlib.util.spec_from_file_location('vector_selected_source_control', path)
            controls = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(controls)
            code = controls.NetworkControls.test_network_includes_canonical_historical_commit.__code__
            methods = [node for node in ast.walk(ast.parse(original))
                       if isinstance(node, ast.FunctionDef) and node.name == code.co_name
                       and node.lineno == code.co_firstlineno]
            self.assertEqual(len(methods), 1)
            calls = [node for node in ast.walk(methods[0]) if isinstance(node, ast.Call)
                     and isinstance(node.func, ast.Attribute) and node.func.attr == 'assertEqual']
            self.assertEqual(len(calls), 1)
            call = calls[0]
            expected = (call.lineno, call.end_lineno, call.col_offset, call.end_col_offset)
            offsets = [ins.offset for ins in dis.get_instructions(code, show_caches=True)
                       if ins.positions is not None and
                       (ins.positions.lineno, ins.positions.end_lineno, ins.positions.col_offset,
                        ins.positions.end_col_offset) == expected]
            self.assertTrue(offsets)
            oracle = (unittest.TestCase.assertEqual.__code__, unittest.TestCase._baseAssertEqual.__code__)
            self.assertTrue(authorized_oracle(code, offsets[-1], oracle))
            self.assertFalse(authorized_oracle(code, -1, oracle))
            path.write_text(original.replace(before, 'self.assertEqual(22, len(requests))', 1))
            self.assertFalse(authorized_oracle(code, offsets[-1], oracle))
            path.unlink()
            self.assertFalse(authorized_oracle(code, offsets[-1], oracle))

    def test_assert_raises_exit_is_authorized_on_current_python(self):
        source = TOOL.read_text()
        anchor = 'set(values) == set(REPOSITORIES)'
        self.assertEqual(source.count(anchor), 1)
        selected = 'VectorSources.test_vector_omission_rejected'
        with tempfile.TemporaryDirectory(prefix='vector-context-exit-') as tmp:
            folder = Path(tmp)
            candidate = folder/'subject.py'
            candidate.write_text(source.replace(anchor, 'True', 1))
            for optimized in (False, True):
                with self.subTest(optimized=optimized):
                    event_path = folder/(str(optimized) + '.json')
                    nonce = secrets.token_hex(16)
                    env = dict(os.environ, CBZ_VECTOR_UNDER_TEST=str(candidate),
                               CBZ_VECTOR_EVENT=str(event_path), CBZ_VECTOR_NONCE=nonce)
                    child = subprocess.run([sys.executable, '-B', *(['-O'] if optimized else []),
                                            '-S', str(Path(__file__).resolve()), '--child', selected],
                                           env=env, text=True, capture_output=True, timeout=180)
                    event = json.loads(event_path.read_text())
                    self.assertTrue(intended_failure(child, event, selected, nonce, digest(candidate),
                                                     'ValueError not raised'), child.stderr)

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
