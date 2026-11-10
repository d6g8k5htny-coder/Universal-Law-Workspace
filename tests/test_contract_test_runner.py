"""Adverse controls for the Workspace contract workflow's test outcome gate."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/ci.yml'
RUNNER = ROOT / 'tools/run_contract_tests.py'


def contract_block():
    raw = WORKFLOW.read_text(encoding='utf-8')
    marker = '      - name: Run contract tests\n'
    if raw.count(marker) != 1:
        raise ValueError('contract step is not unique')
    step = raw.split(marker, 1)[1].split('      - name:', 1)[0]
    if step.count('        run: |\n') != 1:
        raise ValueError('contract run block is not unique')
    lines = step.split('        run: |\n', 1)[1].splitlines()
    if not lines or any(line and not line.startswith('          ') for line in lines):
        raise ValueError('unexpected contract block indentation')
    return '\n'.join(line[10:] if line else '' for line in lines) + '\n'


def fixture(source, *, block=None, runner_source=None, optimized=False):
    with tempfile.TemporaryDirectory(prefix='workspace-contract-gate-') as directory:
        root = Path(directory)
        (root / 'tests').mkdir()
        (root / 'runner-temp').mkdir()
        (root / 'tests/test_fixture.py').write_text(source, encoding='utf-8')
        env = dict(os.environ)
        for key in ('PYTHONHOME', 'PYTHONOPTIMIZE', 'PYTHONSTARTUP'):
            env.pop(key, None)
        env.update(RUNNER_TEMP=str(root / 'runner-temp'), PYTHONPATH=str(ROOT),
                   PYTHONDONTWRITEBYTECODE='1')
        if runner_source is None:
            command = ['bash', '-c', contract_block() if block is None else block]
        else:
            path = root / 'mutated_runner.py'
            path.write_text(runner_source, encoding='utf-8')
            command = [sys.executable, '-B'] + (['-O'] if optimized else []) + [str(path)]
        result = subprocess.run(command, cwd=root, env=env, stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, encoding='utf-8', timeout=30)
        logs = []
        for name in ('discovery.log', 'discovery-optimized.log'):
            path = root / 'runner-temp' / name
            logs.append(path.read_text(encoding='utf-8') if path.exists() else '')
        return result, logs


PASS = 'import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertEqual(1, 1)\n'
SKIP_NORMAL = "import unittest\nclass T(unittest.TestCase):\n @unittest.skipIf(__debug__, 'normal adverse')\n def test_skip(self): pass\n"
SKIP_OPTIMIZED = "import unittest\nclass T(unittest.TestCase):\n @unittest.skipUnless(__debug__, 'optimized adverse')\n def test_skip(self): pass\n"
EXPECTED = 'import unittest\nclass T(unittest.TestCase):\n @unittest.expectedFailure\n def test_expected(self): self.fail("adverse")\n'


class ContractWorkflowControls(unittest.TestCase):
    def test_passing_fixture_runs_both_modes(self):
        result, logs = fixture(PASS)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(all('Ran 1 test' in log and '\nOK\n' in log for log in logs))

    def test_normal_skip_refuses(self):
        result, logs = fixture(SKIP_NORMAL)
        self.assertIn('skipped=1', logs[0])
        self.assertNotEqual(result.returncode, 0, 'normal skip was accepted')

    def test_optimized_skip_refuses(self):
        result, logs = fixture(SKIP_OPTIMIZED)
        self.assertIn('skipped=1', logs[1])
        self.assertNotEqual(result.returncode, 0, 'optimized skip was accepted')

    def test_expected_failure_refuses(self):
        result, logs = fixture(EXPECTED)
        self.assertIn('expected failures=1', logs[0])
        self.assertNotEqual(result.returncode, 0, 'expected failure was accepted')

    def test_skipped_class_refuses(self):
        source = "import unittest\nclass T(unittest.TestCase):\n @classmethod\n def setUpClass(cls): raise unittest.SkipTest('class skip')\n def test_x(self): pass\n"
        result, logs = fixture(source)
        self.assertIn('skipped=1', logs[0])
        self.assertNotEqual(result.returncode, 0)

    def test_skipped_subtest_refuses(self):
        source = "import unittest\nclass T(unittest.TestCase):\n def test_x(self):\n  with self.subTest(value=1): self.skipTest('subtest skip')\n"
        result, logs = fixture(source)
        self.assertIn('skipped=1', logs[0])
        self.assertNotEqual(result.returncode, 0)

    def test_import_error_refuses(self):
        result, logs = fixture('raise RuntimeError("adverse import failure")\n')
        self.assertIn('FAILED (errors=1)', logs[0])
        self.assertNotEqual(result.returncode, 0)

    def test_unexpected_success_refuses(self):
        source = 'import unittest\nclass T(unittest.TestCase):\n @unittest.expectedFailure\n def test_x(self): pass\n'
        result, logs = fixture(source)
        self.assertIn('unexpected successes=1', logs[0])
        self.assertNotEqual(result.returncode, 0)

    def test_empty_discovery_refuses(self):
        result, logs = fixture('import unittest\n')
        self.assertIn('Ran 0 tests', logs[0])
        self.assertNotEqual(result.returncode, 0)

    def test_failure_refuses(self):
        source = 'import unittest\nclass T(unittest.TestCase):\n def test_x(self): self.fail("adverse")\n'
        result, logs = fixture(source)
        self.assertIn('FAILED (failures=1)', logs[0])
        self.assertNotEqual(result.returncode, 0)

    def test_printed_ok_does_not_hide_skip(self):
        source = "import unittest\nclass T(unittest.TestCase):\n def test_x(self):\n  print('OK', flush=True)\n  self.skipTest('adverse')\n"
        result, logs = fixture(source)
        self.assertIn('skipped=1', logs[0])
        self.assertNotEqual(result.returncode, 0)

    def test_removing_skip_guard_reopens_skip(self):
        source = RUNNER.read_text(encoding='utf-8')
        anchor = 'if result.skipped:'
        self.assertEqual(source.count(anchor), 1)
        mutated = source.replace(anchor, 'if False:', 1)
        for optimized in (False, True):
            result, _ = fixture(SKIP_NORMAL if not optimized else SKIP_OPTIMIZED,
                                runner_source=mutated, optimized=optimized)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_removing_expected_failure_guard_reopens_failure(self):
        source = RUNNER.read_text(encoding='utf-8')
        anchor = 'if result.expectedFailures:'
        self.assertEqual(source.count(anchor), 1)
        mutated = source.replace(anchor, 'if False:', 1)
        for optimized in (False, True):
            result, _ = fixture(EXPECTED, runner_source=mutated, optimized=optimized)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_removing_empty_guard_reopens_empty_discovery(self):
        source = RUNNER.read_text(encoding='utf-8')
        anchor = 'if result.testsRun == 0:'
        self.assertEqual(source.count(anchor), 1)
        mutated = source.replace(anchor, 'if False:', 1)
        for optimized in (False, True):
            result, _ = fixture('import unittest\n', runner_source=mutated, optimized=optimized)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
