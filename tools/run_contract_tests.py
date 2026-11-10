"""Run Workspace unittest discovery and refuse incomplete result categories.

This checks the result of ordinary unittest discovery. It is not a census of
all possible tests and does not defend against test code that replaces the
runner, forges its pipe receipt or falsifies unittest's in-process result.
"""
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import unittest


def run_child(receipt_fd, nonce):
    # Match ``python -m unittest``'s repository-root import path even though
    # the isolated child is launched by this script's absolute filename.
    sys.path.insert(0, os.getcwd())
    suite = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    reasons = []
    if result.testsRun == 0:
        reasons.append('no tests ran')
    if result.skipped:
        reasons.append(f'{len(result.skipped)} skipped')
    if result.expectedFailures:
        reasons.append(f'{len(result.expectedFailures)} expected failures')
    if not result.wasSuccessful():
        reasons.append('failures, errors, or unexpected successes')
    if reasons:
        print('contract tests refused: ' + '; '.join(reasons), file=sys.stderr)
        return 1
    os.write(receipt_fd, ('CBZ_CONTRACT_PASS:' + nonce + '\n').encode('ascii'))
    os.close(receipt_fd)
    return 0


def main():
    if len(sys.argv) == 4 and sys.argv[1] == '--internal-child':
        if not sys.argv[2].isdigit() or not re.fullmatch('[0-9a-f]{32}', sys.argv[3]):
            print('contract tests refused: invalid child receipt context', file=sys.stderr)
            return 1
        return run_child(int(sys.argv[2]), sys.argv[3])
    if len(sys.argv) != 1 or os.name != 'posix':
        print('contract tests refused: unsupported arguments or platform', file=sys.stderr)
        return 1

    read_fd, write_fd = os.pipe()
    nonce = secrets.token_hex(16)
    flags = (['-B'] if sys.dont_write_bytecode else [])
    flags += (['-' + 'O' * sys.flags.optimize] if sys.flags.optimize else [])
    flags += (['-S'] if sys.flags.no_site else [])
    try:
        process = subprocess.Popen([sys.executable, *flags, str(Path(__file__).resolve()),
                                    '--internal-child', str(write_fd), nonce], pass_fds=(write_fd,))
    except OSError as error:
        os.close(read_fd)
        os.close(write_fd)
        print('contract tests refused: child launch failed: ' + type(error).__name__, file=sys.stderr)
        return 1
    os.close(write_fd)
    process.wait()
    os.set_blocking(read_fd, False)
    try:
        try:
            receipt = os.read(read_fd, 4096)
        except BlockingIOError:
            receipt = b''
        try:
            trailing = os.read(read_fd, 1)
        except BlockingIOError:
            trailing = b'PIPE_STILL_OPEN'
        receipt += trailing
    finally:
        os.close(read_fd)
    expected = ('CBZ_CONTRACT_PASS:' + nonce + '\n').encode('ascii')
    if process.returncode != 0 or receipt != expected:
        print('contract tests refused: child failed or did not complete its result receipt', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
