# Workspace contract discovery outcome evidence

The preserved `original-ci.yml` is byte-identical to Git blob
`0d57f8e2b6bf468dcee1fbc12eed9e0026834914` in Workspace commit
`5ee815d60d5e11cb590b2a3b274fd13104bd915d`. Its contract step ran ordinary
`unittest` discovery and required only a positive count. Python's standard
`unittest` exits zero for skipped tests and expected failures, so that step
accepted each of those synthetic adverse outcomes in both Python modes.
Empty discovery and an ordinary failure were refused in the original local
experiment. These fixtures do not claim an actual historical hosted skip.

`original-red-reproducer.py.txt` and `original-red-*.log` preserve the first
CPython 3.12.14 experiment; its original script used a scratch path and PyYAML.
`candidate-test-red-*.log` preserve the candidate tests failing against the
same original step. `reproduce_original.py` is a standalone version using the
retained original workflow bytes and standard-library modules. These commands
intentionally return nonzero with two assertion failures:

```sh
python3 -B -S evidence/contract-outcome-20261110/reproduce_original.py
python3 -B -O -S evidence/contract-outcome-20261110/reproduce_original.py
```

`control-normal.log` and `control-optimized.log` retain the 14 focused local
controls per parent mode for the candidate. They exercise the actual workflow
block on passing, empty, failing, skipped, expected-failure and output-spoof
fixtures, including mode-specific and fixture-lifecycle cases. Three actual
runner mutations remove the skip, expected-failure and empty-run guards; each
reopens its matching false accept in both child modes. The candidate tool
checks the in-process result of the suite that `unittest` discovers. It does
not establish that discovery selected every intended test and does not defend
against hostile test code replacing or falsifying the runner's result.

The separate pin workflow uses the original count-only approach and is not
repaired here. A read-only experiment executed its exact original negative-
controls block against normal-mode passing, skipped and expected-failure
fixtures; all three returned zero. `original-pins.yml`,
`original-pin-observer.py.txt` and `pin-workflow-observation.json` retain the
source and observation. This does not imply the actual earlier pin job skipped
anything. Exact-head hosted outcomes, full federation regression and CBZ-0 are
not established by this local evidence.
