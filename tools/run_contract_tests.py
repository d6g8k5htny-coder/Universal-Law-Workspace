"""Run Workspace unittest discovery and refuse incomplete result categories.

This checks the result of ordinary unittest discovery. It is not a census of
all possible tests and does not defend against test code that replaces the
runner or falsifies unittest's in-process result.
"""
import sys
import unittest


def main():
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
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
