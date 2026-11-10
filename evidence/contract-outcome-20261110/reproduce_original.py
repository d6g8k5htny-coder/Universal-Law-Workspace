"""Reproduce finite red outcomes using the preserved original workflow block."""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
raw = (ROOT / 'original-ci.yml').read_bytes()
if hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() != '0d57f8e2b6bf468dcee1fbc12eed9e0026834914':
    raise ValueError('preserved original workflow blob mismatch')
text = raw.decode('utf-8')
marker = '      - name: Run contract tests\n'
if text.count(marker) != 1:
    raise ValueError('original contract step is not unique')
step = text.split(marker, 1)[1].split('      - name:', 1)[0]
lines = step.split('        run: |\n', 1)[1].splitlines()
if not lines or any(line and not line.startswith('          ') for line in lines):
    raise ValueError('unexpected original block indentation')
block = '\n'.join(line[10:] if line else '' for line in lines) + '\n'


def run(source):
    with tempfile.TemporaryDirectory(prefix='workspace-contract-original-') as directory:
        root = Path(directory)
        (root / 'tests').mkdir()
        (root / 'runner-temp').mkdir()
        (root / 'tests/test_fixture.py').write_text(source)
        env = dict(os.environ, RUNNER_TEMP=str(root / 'runner-temp'), PYTHONDONTWRITEBYTECODE='1')
        for name in ('PYTHONHOME', 'PYTHONOPTIMIZE', 'PYTHONPATH'):
            env.pop(name, None)
        result = subprocess.run(['bash', '-c', block], cwd=root, env=env,
                                capture_output=True, text=True, timeout=30)
        return result, [(root / 'runner-temp' / name).read_text() for name in
                        ('discovery.log', 'discovery-optimized.log')
                        if (root / 'runner-temp' / name).exists()]


class OriginalWorkflowRed(unittest.TestCase):
    def test_skip_should_refuse(self):
        source = "import unittest\nclass T(unittest.TestCase):\n @unittest.skip('adverse')\n def test_x(self): pass\n"
        result, logs = run(source)
        self.assertEqual(len(logs), 2)
        self.assertTrue(all('skipped=1' in log for log in logs))
        self.assertNotEqual(result.returncode, 0, 'original workflow accepted a skipped test')

    def test_expected_failure_should_refuse(self):
        source = 'import unittest\nclass T(unittest.TestCase):\n @unittest.expectedFailure\n def test_x(self): self.fail("adverse")\n'
        result, logs = run(source)
        self.assertEqual(len(logs), 2)
        self.assertTrue(all('expected failures=1' in log for log in logs))
        self.assertNotEqual(result.returncode, 0, 'original workflow accepted an expected failure')


if __name__ == '__main__':
    unittest.main(verbosity=2)
