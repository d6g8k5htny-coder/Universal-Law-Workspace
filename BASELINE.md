# CBZ baseline observations

No CBZ-0 baseline or final baseline tag has been declared. This is an
intermediate discovery record, not a certification.

Source cut used for this stage:

- Workspace predecessor: `45a80ab01504936b46d035c2de1f92c73ed273de`.
- Main: `4ef1867175dbe1072a54a02e95f80c4e2c70a4ff`.
- Math-: `8151f592918a845bf19eb8eafaf8444540a32734`.
- The other observed submodule source identities are in `pins.json` and
  `PIN_REFRESH_OBSERVATION.json`. Default branches were observed sequentially.

| Gate | Observed state at this stage |
|---|---|
| G0–G1 Layer A auditor and full audit | Not established. The lexical Lean-source discovery is not a verified auditor. |
| G2 axiom audit | Not established for the complete federation. |
| G3 Lean build | Local formal-core execution failed because `lake` was absent; a separate hosted formal-core build at Math- `8151f592` passed. Full federation build is not established. |
| G4 kernel audit | The same hosted formal-core run timed out during `leanchecker` after 900 seconds; the complete federation audit is not established. |
| G5 full regression | Not run federation-wide. Workspace and Math- formal-core Python controls are scoped observations in STATUS.md. Workspace hosted contract run 40918511097 failed on an unexpected gitlink in `e347db7`; run 40918788940 passed on corrected commit `66019e4`. |
| G6 mutation | Strict pin-checker mutations are bounded engineering controls, not a full Layer A mutation result. |
| G7 pin sync | Candidate pins and three control blobs were rebound to a source cut. Run 40918510771 failed on an unexpected gitlink in `e347db7`; run 40918789181 rejected Main drift on `66019e4`; run 40919435108 rejected meta-framework drift on `a4b0168`. This candidate refreshes that pin and adds a source-blob check. Verify the actual candidate and all transitive cross-repo bindings separately. The authority-map source is historical. |
| G8 status truth | Partial; several inventories and source-authority boundaries remain incomplete. |
| G9 cold start | Not run. STATUS is not yet sufficient for a complete cold-start acceptance. |
| G10 Git hygiene | Not met at discovery: many branches and open PRs remain. Other agents' worktrees and stashes were not observed. |
| G11 tooling | The changed pin checker is documented in GOVERNANCE; the full federation tool/stub inventory is incomplete. |

No proof was newly declared CLOSED or QUARANTINED. Do not use this file as a
replacement for Math-'s existing proof records or as scientific acceptance.
