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

## Decision record

Use `DECISIONS.md` for Phase 1 observations and subsequent source changes. No
previous test is removed to obtain a passing result. A real failing test or
incomplete audit remains visible until fixed or precisely isolated.
