# Python 3.11 vector-origin observation

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
checked. Exact-head hosted follow-up qualification remains pending. The earlier
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
