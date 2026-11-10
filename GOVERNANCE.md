# CBZ working rules and tool registry

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

## Vector mutation-origin controls — 10 November 2026

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

```sh
python3 -B -S -m unittest discover -s tests -p 'test_verify_federation_vector*.py' -v
python3 -B -O -S -m unittest discover -s tests -p 'test_verify_federation_vector*.py' -v
```

The tool verifies finite source-bound mutation outcomes for the structural
federation vector checker. The cited local controls exercise its selected
assertion-origin grading, not all mathematical claims or all repository refs.

The owner-directed Clean Baseline Zero protocol governs the current work. This
document records operational choices for this repository; it is not proof of
CBZ-0. Preserve the Layer A invariants: no logical placeholders presented as
closed, no unverified axiom injection, no floating-point certification of
bounds, no weakened mathematical bounds, no silently deleted/disabled failing
tests, disclose vacuity, truthful verification/status, and verified auditors.

## Baseline protocol

CBZ-0 requires clean in-scope Git state; no open PRs or dangling branches;
every proof obligation kernel-closed or precisely isolated; a verified Layer A
audit; complete regression, Lean, kernel, axiom and declared mutation gates;
consistent cross-repository pins; documented and verified mission tools; and
consistent STATUS, proof index, governance and baseline records. A cold-start
agent must be able to identify the state and run the gates from STATUS alone.
The current inventory is explicitly incomplete.

Work proceeds through discovery, close-or-quarantine, verification, and a
source-bound handoff. A quarantine records the exact unproved boundary,
reason, prior attempts, isolation and estimated resumption cost; it cannot
feed a closed claim. Never call a lexical scan a complete Layer A audit.
Record changes and conflicts in DECISIONS.md; preserve pre-operation states
before destructive operations. An absent tool is either built and verified
when it is on the shortest path, or the specific unmet check remains visible.
No current record grants a theorem or an unexecuted gate a passing result.

## Repository tools

### `tools/verify_pins.py`

- Purpose: check the committed gitlinks against `pins.json` and `.gitmodules`.
- `python3 tools/verify_pins.py`: local structural pin agreement.
- `python3 tools/verify_pins.py --network`: additionally fetch public pins;
  a different or unavailable default tip is informational.
- `python3 tools/verify_pins.py --require-current`: require every configured
  public pin to match the observed remote default branch and HEAD; fail on
  skipped private entries, failed lookups, missing/duplicate/inconsistent refs
  and differing tips. Bind the gitlinks, `pins.json` and `.gitmodules` to one
  committed HEAD, with input and HEAD rechecks after remote observations. It
  implies `--network` and is run by `.github/workflows/pins.yml`.
- Verify: `python3 -m unittest discover -s tests -p 'test_verify_pins_strict.py' -v`,
  `python3 -m unittest discover -s tests -p 'test_verify_pins_mutations.py' -v`,
  and the same commands with `python3 -O`; then run the full suite in both
  modes. The mutation test requires all 15 named guard/data mutations to be
  caught. It is a bounded engineering check, not a Layer A auditor.
- Limits: observations of repositories are sequential and can race remote
  changes. The checker does not compare the canonical-input blobs in
  `workspace/repositories.json`, audit math, or guarantee an atomic snapshot.
  Non-public entries fail the strict mode rather than being silently skipped.

### `tools/check_workspace.py`

`python3 tools/check_workspace.py` checks the workspace manifest's structural
contract. It does not check the remote contents of canonical inputs or certify
scientific claims. Its existing tests are included in the full suite.

### `tools/verify_canonical_inputs.py`

- Purpose: fetch the exact source commits in the workspace map and compare
  every canonical input's regular-file Git blob identity to its recorded blob.
  An input with no explicit `ref` is bound to that repository's gitlink pin;
  a different, explicit full commit is reported as a separate ref without
  inferring ancestry or age. It checks the
  workspace manifest, pin file and `.gitmodules` against one committed HEAD,
  rechecks them after the fetch, and fails on missing or unlisted sources.
- Run: `python3 tools/verify_canonical_inputs.py`. Network access to the
  configured public GitHub repositories is required. The pin workflow runs it
  after `python3 tools/verify_pins.py --require-current`.
- Self-verification: run the commands below. The controls use real disposable
  Git repositories; the mutation test checks 13 named weakened implementations
  and rejects stale mutants.

  ```sh
  python3 -m unittest discover -s tests -p 'test_verify_canonical_inputs*.py' -v
  python3 -O -m unittest discover -s tests -p 'test_verify_canonical_inputs*.py' -v
  ```
- Limits: this checks byte identities, not semantic correctness, mathematical
  status or all transitive cross-repository dependencies. It does not itself
  check current remote tips, nor provide an atomic federation snapshot; the
  separate strict pin check reports the sequential tip observations.

## Decision record

Use `DECISIONS.md` for Phase 1 observations and subsequent source changes. No
previous test is removed to obtain a passing result. A real failing test or
incomplete audit remains visible until fixed or precisely isolated.


### Canonical checker mutation evidence

The canonical-input checker retains all 13 behavioral source mutations. Its
controls now emit a fresh per-run nonce, exact test method and intended policy
bypass only after a valid checker result. Checker children do not receive the
observation path or nonce. An outer assertion failure alone earns no mutation
credit. Silent exits, traceback crashes, unrelated refusal diagnostics, missing
or stale observations, wrong test names and zero-test runs fail qualification.
Four actual mutations of the evidence classifier must themselves be rejected.
Run the existing normal and optimized canonical-control commands above, or the
full repository suite in both modes; the contract workflow now runs both modes.
The tool is bounded source-identity engineering and certifies no mathematics.

An actual hosted regression at d4ae729871d17332f9adc705cc55e082897bc5ed
ran 107 tests and failed exactly the newly added silent-exit adverse control
(run 40942797333, job 123690270511). That RED evidence is preserved. The
repair at 8397f29669ba213dcc6e678dd9f8015033f1e5af then passed 110 tests
in each of normal and optimized Python (run 40943291131/job 123691959826),
including all 13 canonical source mutants, four classifier mutants and the
15 retained strict pin mutants. Its tested PR merge has exactly the same Git
tree as that head. Exact source identities and raw job logs are preserved in
`evidence/canonical-harness/`. Current pins failed separately on Main and
Math drift. No current federation pin or CBZ gate is asserted by this change.

Raw hosted logs under `evidence/canonical-harness/hosted-*-job.log` retain their
exact bytes via scoped Git attributes; this does not relax source formatting.


### Strict-pin mutation evidence and `tests/pin_mutation_receipts.py`

The retained strict-pin mutation harness had the same outer-failure-only
weakness. Its source is repaired without changing `tools/verify_pins.py`
or deleting any of the fifteen mutants or existing assertions. The test-owned
helper validates the checker result protocol and requires a fresh nonce,
exact method and intended policy outcome before a failure earns mutation
credit. Most scored cases require actual acceptance of an invalid source.
Unverified-source remote contact and an unsupported ancestry label are
separate policy outcomes. The missing-default and missing-configured-branch
controls instead require the specific diagnostic to be demoted to information,
even if another guard still refuses; they measure that diagnostic contract,
not complete invalid-source acceptance. Each of these two cases requires its
exact `expected-policy-demoted` observation, and an unrelated diagnostic earns
no credit. Checker children receive neither observation path nor nonce. Four
actual classifier source mutations and five real adverse checker behaviors
test the evidence boundary itself.

Run `python3 -m unittest discover -s tests -p 'test_verify_pins_mutations.py' -v`
and its `python3 -O` equivalent, then the full suite in both modes. The
strict-RED source is 0f0f7f4bf5cec63caaaed16894e9196c1e296e9b; its hosted
contract run 40945946596 was queued at this source update, so no hosted RED
result is invented. Automatic review 4417369636 independently corroborated
the deterministic silent-crash failure. Qualification of the repaired source
is pending actual execution. Maintenance owner: none; self-contained tests.
This tool serves G6/A8 and supports G7; it certifies no mathematics or current
remote pin agreement.

## Immutable federation vector candidate — qualification pending

The earlier vector mutation grader's filename-based attribution was shown to
credit a subject assertion from a `unittest`-named path as an oracle failure.
The successor uses pre-cleanup live code identity for the selected body,
dispatch and permitted unittest helpers, with actual assertion type and
lifecycle guards. Its supported domain is selected synchronous unittest bodies
and standard unittest assertion helpers, not arbitrary helpers or hostile code.
At test-source SHA-256
`e7630a0642101e2070d73f0bcb84b22e301cfbfac5a0ed66847ee7048d23d3a4`,
67 focused tests passed per Python mode, including 13 real source mutants per
mode and a guard-removal self-mutation of the origin classifier. Earlier
observations retain their source boundaries; full current-source and hosted
qualification remain pending. See STATUS for the actual offline cut and the
preserved first failure. The same cut's network run fetched 20 of 22 requested
commits and failed on the two private Git transports; it is not a network pass.
None of these observations establishes a final G7.
The pre-pin-refresh candidate also ran the full 254-test Workspace suite in
each Python mode without skips. The subsequent Main pin composition requires
its own exact-source pin checks and hosted qualification.

`tools/verify_federation_vector.py` composes twelve selected immutable
commit/tree/index relationships, selected structural working inputs, eight
Workspace pointers, four canonical byte bindings and nine native Lean locks.
Optional exact-commit HTTPS availability is a separate observation; immutable
vectors need not equal moving default tips. Existing pure validators are reused.

Run and self-verify using [the exact guide](docs/cbz/FEDERATION_VECTOR.md).
The source and two test files were recovered from preserved inputs and matched
their original native Git blob and SHA-256 identities. The original 62 declared controls
still require final-source hosted execution and fresh engineering review.
Earlier source-bound component passes and later resource failures retain their
separate outcomes; no final gate is inferred.

Full tracked working parity and Git hygiene remain `NOT_ASSESSED`. General
configuration semantics are unassessed; the actual sibling TOML target has a
strict name check. No proof/build execution or selected-source Git status
occurs. Cleanup uncertainty preserves `NETWORK_CLEANUP_ERROR` and blocks more
requests. Maintenance owner: none; standard library only. No Layer A, G7,
CBZ criterion or scientific independence is awarded.

The initial hosted revision adds three reviewed counterexamples (65 controls
total) against the unchanged tool. Canonical object-type and noncanonical
path gaps remain open until observed RED, repaired and requalified. This
candidate is not an admitted certifier.

The initial `be512430` hosted draft ran 252 normal Workspace tests with six
intended test-body failures and no errors/skips; optimized execution was not
reached. The two minimal guards and strengthened cleanup/filter controls now
await complete current-source qualification. The finite mutation population
is thirteen, retaining the original twelve tuples. Safe normalized traversal
and target membership are checked without requiring shortest-relative spelling.

### Source-bound self-verification observed at 7ee77666

The complete 65 vector controls plus 187 retained Workspace controls passed
normally and optimized:252 per mode, zero failures/errors/skips. Thirteen
clean baselines and thirteen intended selected-body mutant failures per mode
were observed in original runner-printed events; the original twelve tuples
remain unchanged. Scoped static review confirmed the two production guards,
owned descendant cleanup and CI evidence handling. See the guide for exact
run/source identities and original artifact limits. The bounded engineering
tool is self-tested; a passing actual current/final vector and global G7
remain unobserved. The retained local attempt failed before repository checks
and a later launch was refused with errno11. No failure is promoted to PASS.


### Verify the historical vector contract artifact

```sh
EVIDENCE_DIR="$(mktemp -d)"
python3 -B -S -m zipfile -e evidence/vector-origin-20261110/workspace-vector-hosted-20261110.zip "$EVIDENCE_DIR"
python3 -B -S "$EVIDENCE_DIR/verify_workspace78_contract.py" "$EVIDENCE_DIR/hosted-v2/contract-artifact-13750121464.zip" fef8bdc1bb7cfd7d71fda34b0fd0b1a150e4d2888d41773ce8781fd4fdd4629c "$EVIDENCE_DIR/verification.json"
python3 -B -S "$EVIDENCE_DIR/test_workspace78_contract_verifier.py" "$EVIDENCE_DIR/hosted-v2/contract-artifact-13750121464.zip" fef8bdc1bb7cfd7d71fda34b0fd0b1a150e4d2888d41773ce8781fd4fdd4629c "$EVIDENCE_DIR/new-adverse"
```

This fixed-scope verifier checks the named historical artifact and candidate
source bytes. It does not authenticate future runs, prove mathematical claims or
certify the federation. The adverse test creates explicitly synthetic copies
in the new directory; original files are left intact.
