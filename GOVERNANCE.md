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
