# Python 3.11 vector-origin observation

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

Original diagnostic bundle `workspace-vector-python311-20261110.zip`:
211,181 bytes, 15 members, SHA-256
`cc09876e292f93e8185f501ae32f8bad8e650615ba2589cce94b7a0ebf6ea399`. All listed member hashes and ZIP CRCs were checked
locally. It contains both failed hosted logs, the original 106-member contract
artifact, the original 14-member observer artifact and log, the observer
source, local focused logs, and the candidate test source. It does not turn the
failed hosted result into a passing result.

The follow-up local campaign archive `workspace-vector-followup-campaign-20261110.zip` has 216 members, 525,783 bytes, SHA-256 `139f825582374abe011ba52ba72b3c60decec28f9506bd4699269a97b6daa721`. Its per-member hashes and CRCs were checked. It is bounded local evidence, not hosted or federation qualification.
