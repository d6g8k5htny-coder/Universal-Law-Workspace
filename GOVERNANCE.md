# CBZ working rules and tool registry

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
