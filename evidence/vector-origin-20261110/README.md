# Workspace vector mutation-origin evidence — 10 November 2026

## Source-bound hosted observation — 10 November 2026, 09:11 UTC

For PR #78 head `64b4b360575b482432eb8f052d268ddcfbfca8c4` and base
`344f81f5cb1e7040dfedb2c752b9a3514775b257`, GitHub tested merge
`3ed8493993c18e5752398f5f7f655ff7898ed2f5` with tree
`a92e5876d2366ba06a085506546672be42604069`. Contract run `42787699084`,
job `129732985197`, passed 258 tests per mode without skips on CPython 3.11.
Its original artifact `13750121464`, SHA-256
`fef8bdc1bb7cfd7d71fda34b0fd0b1a150e4d2888d41773ce8781fd4fdd4629c`,
has 212 unique CRC-valid members. Independent verification matched all 13
declared baseline/mutant pairs per mode, their 52 source-bound events,
candidate bytes, stderr hashes and nonces. The PR and push pin jobs also
passed 258 normal-mode tests and their eight public pin checks. These results
are bound to their actual tested sources and do not qualify a later head.

The one-off artifact verifier refused missing evidence, altered source and an
inserted skip in both modes. Two source mutations of that verifier separately
reopened the matching false accepts; the synthetic adverse archives are
explicitly labeled. Original job logs, artifact bytes, verifier source,
controls and local 258-test-per-mode observations are retained in the linked
evidence bundle. None establishes final federation G0–G11 or scientific review.

## Python 3.11 context-exit follow-up — 10 November 2026

The first candidate at Workspace PR #78 head
`0e4162c8f0fc9c61d13ed75c3ef91407c22c236d` passed its bounded local
CPython 3.12.14 controls, but both hosted CPython 3.11.18 jobs failed: their
normal 257-test discoveries each rejected nine intended `assertRaisesRegex`
mutant failures. The contract artifact retained 13 baselines and four admitted
mutants in its summary; the other nine were refused. Optimized hosted discovery
was not reached. The original job logs, artifact and failures remain retained.

An instrumented copy of the exact candidate showed why: in Python 3.11 the
implicit context exit is attributed to the complete `with` statement span;
Python 3.12 attributed it to the assertion-call span. The follow-up source
SHA-256 is `90abecc6c203ce98614938d24b0c2f21f2a8431ff6c784680c5f6ad63c10e95d`.
It permits either observed position only for a single-item `with` whose
context is the selected test's direct `self.assertRaisesRegex` call, while
still requiring the exact selected code identity and supported oracle path.
Unknown positions and source changes fail closed. Local CPython 3.12.14 ran
five focused controls in both parent modes, including both child modes for the
context exit and four adverse origins, plus actual callsite and oracle-path
guard removals. The 13-test mutation module passed locally in normal and optimized modes; all
52 retained baseline/mutant events and their source and stderr hashes were
checked. A source-bound hosted observation is recorded in the 10 November evidence; future heads require their own platform checks. The earlier
257-test local success was for the first candidate source and does not qualify
this new source. No federation-wide gate or scientific acceptance is inferred.

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

The first candidate had mutation-test file SHA-256
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
