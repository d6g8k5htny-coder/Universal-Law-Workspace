# CBZ status — work in progress

This repository maps the Universal Law federation and its pinned sources.
Clean Baseline Zero is not established. The current discovery is recorded in
`INVENTORY.md` and `INVENTORY.json`; it is incomplete and is not a full proof,
branch-custody, workflow or local-worktree inventory.

Federation coordination and integration are tracked in
[`main#684`](https://github.com/d6g8k5htny-coder/main/issues/684) and
[`main#685`](https://github.com/d6g8k5htny-coder/main/pull/685). This file
records this workspace contribution and does not replace their shared record.

## Verified so far

- A reconstructed snapshot of the pre-change workspace was checked locally:
  its structural map and offline pin checks passed, as did 66 Python tests.
- At the inspected Math- source, the formal-core source identity check and
  244 Python tests passed in each of normal and optimized modes. This is not a
  Lean build, kernel recheck, complete axiom audit or proof acceptance.
- The strict current-tip pin checker candidate passed the complete workspace
  suite of 84 tests in each of normal and optimized Python on the reconstructed
  local candidate. The suite detected all 15 named pin-checker mutations in
  both modes. This is scoped engineering evidence, not a full Layer A audit.
  Current hosted/federation-wide gates must be run against the actual committed
  state before they can be reported green.
- Hosted runs 40918510771 and 40918511097 on Workspace commit `e347db7`
  failed: the published Git tree accidentally contained an extra gitlink
  `repos/Universal-Law-Workspace` absent from the tested local candidate.
  The correction removes that gitlink; hosted verification of the corrected
  tree is still required. See `evidence/hosted_validation_20261029.json`.

## Remaining

The 12 CBZ criteria remain unmet or not yet verified as a single final pass.
Open work includes the complete obligation and branch inventory, verified
Layer A auditor and full-tree audit, full Lean/kernel/axiom checks, complete
regression/mutation runs, all cross-repository control-source consistency,
precise proof quarantine, and cold-start qualification. Current peer work and
existing history have not been disposed of by this status file.

## How to verify this repository

```sh
python3 tools/check_workspace.py
python3 tools/verify_pins.py
python3 tools/verify_pins.py --network
python3 tools/verify_pins.py --require-current
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -O -m unittest discover -s tests -p 'test_*.py' -v
```

Strict pin verification needs network access to the listed public Git remotes.
It tests observed tips sequentially, not an atomic cross-repository snapshot.
The exact scope of these tools and their self-checks is in `GOVERNANCE.md`;
decisions are in `DECISIONS.md`. The canonical mathematical proof inventory
currently remains in `Math-/PROOF_INDEX.md`; no closed/quarantine conversion
has been asserted here. No quarantines were created by this initial stage.

Layer A: no sorry/admit closures, unverified axiom injection, floating-point
certification, weakened mathematical bounds or silently disabled failing
tests; disclose vacuity; report actual verification and auditor limitations.
