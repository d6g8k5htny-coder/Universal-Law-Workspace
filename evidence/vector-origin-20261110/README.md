# Workspace vector mutation-origin evidence — 10 November 2026

On Workspace source `344f81f5cb1e7040dfedb2c752b9a3514775b257`, the earlier
vector mutation grader's test file SHA-256 was
`e7630a0642101e2070d73f0bcb84b22e301cfbfac5a0ed66847ee7048d23d3a4`.
Four adversarial subject-return cases, each run in normal and optimized child
mode against real fixture tests, produced `AssertionError` from deferred
runtime behavior and were incorrectly classified as selected-oracle kills.
They included mock side effects, a deferred `unittest.case` failure, a
partial bound assertion and equality evaluated during an assertion. These
are deliberately adverse cases, not proof that every historical mutation
result was false. Earlier reports and original outcomes remain preserved;
their selected-body flag alone is insufficient to establish origin against
these cases.

This source contains a candidate correction whose mutation-test file SHA-256 is
`c88d938ab224140495153305ce8e187cadb158465cdbf74d11d2c2425e08cf3d`.
It uses the live traceback, selected code identity, selected instruction source
position bound back to the compiled selected code, and an exact supported
oracle-code path. Unsupported positions, changed or missing selected source,
and unlisted paths fail closed. The finite supported oracles are the observed
`assertEqual` and `assertRaisesRegex` paths used by the 13 declared controls;
this is not a universal Python assertion-origin proof. Local CPython 3.12.14
ran the mutation-test module in both modes: 12 tests per mode with no skips,
including 13 retained source-mutant/baseline pairs per mode, the four adverse
cases and actual removals of the callsite and oracle-path guards. Each removal
reopened its matching real false kill. The retained local archive contains
original red/green logs, candidates, events and source hashes. These observations
do not replace exact-head hosted qualification or the final federation G6.

Archive `workspace-vector-origin-20261110.zip`: 797,027 bytes,
316 members, SHA-256 `805b7e284ae1660fd356ccb8fa3c3e696cf7e7bfd53ce14646496454688fbf2d`. Its `SHA256.json`
binds every data member; all member hashes and CRCs were checked locally before
publication. The source manifest records native Git blob IDs; the diagnostic
instrumentation is separate from the unmodified original harness and is not
itself the original result. The two red logs record six failing subcases each;
the partial-bound case was separately run in both child modes. The local green
logs and 52 event records cover the corrected candidate.

```sh
python3 -B -S -m unittest discover -s tests -p 'test_verify_federation_vector*.py' -v
python3 -B -O -S -m unittest discover -s tests -p 'test_verify_federation_vector*.py' -v
```

The tool verifies finite source-bound mutation outcomes for the structural
federation vector checker. The cited local controls exercise its selected
assertion-origin grading, not all mathematical claims or all repository refs.
