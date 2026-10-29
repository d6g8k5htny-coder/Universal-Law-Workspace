# CBZ Phase 1 inventory — partial source observation

Generated 2026-10-29T17:00:06.326Z. This is an intermediate observation, not CBZ-0 or a complete inventory. All figures are as observed by sequential API calls; active work may move during the sweep. Full branch and issue identifiers are in [INVENTORY.json](INVENTORY.json).

| Public repository | State | Branches | Open PRs | Open issues | Workflow files |
|---|---:|---:|---:|---:|---:|
| main | active | 276 | 41 | 9 | 30 |
| Math- | active | 149 | 25 | 4 | 182 |
| Universal-Law-Workspace | active | 6 | 0 | 1 | 2 |
| meta-framework | active | 44 | 0 | 1 | 2 |
| query- | active | 22 | 0 | 2 | 2 |
| governance- | active | 36 | 0 | 1 | 1 |
| trial | archived | 1559 | 0 | 1 | 6 |
| sandbox | archived | 5 | 0 | 0 | 0 |
| google-drive | archived | 8 | 0 | 0 | 1 |
| d6g8k5htny-coder | active | 4 | 1 | 4 | 0 |

Across these 10 public repositories: 2109 branch references, 67 open pull requests, 23 open issues and 226 workflow source files. The latest run was observed in the recent sample for 36 workflow paths. Other workflow histories were not completely inspected. Private-repository details and other agents' local worktrees/stashes are not published here.

## Proof and verification discovery

- 166 Lean source files from the exact inspected Main and Math- commits were captured and byte-checked against their Git blobs. A lexical search was exploratory only; it is not a verified Layer A audit and does not establish absence of proof holes, unsafe axioms, vacuity or unsound bounds.
- Math- formal-core source identity passed on a reconstructed source snapshot; its 244 Python tests passed in each of normal and optimized modes. The executable local gate failed because Lake was absent. A separately initiated hosted formal-core run is pending; its result must be observed before recording any build, kernel or axiom gate.
- Workspace pin/map tests passed in a reconstructed snapshot. The original pin checker deliberately treats remote tip differences as informational. The strict currentness candidate and its mutation controls are separate changes; see GOVERNANCE.md and DECISIONS.md for actual status.
- The eight workspace submodule pins at the initial cut were all behind their observed tips. Three canonical control blobs also differ from their current-source versions. The historical authority map is explicitly on a non-default branch and is absent from the inspected Main default tree; its historical identity is preserved.

## Remaining discovery

This inventory does not yet enumerate proof obligations, all comments/handoffs, every historical workflow outcome, private source trees, local worktrees/stashes, every changed branch tree, all dependency pins or all test suites. It therefore cannot satisfy Phase 1's zero-unknown exit criterion. No deletion, proof quarantine or scientific promotion is inferred from this inventory.
