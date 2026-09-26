# IDENTITY_LEDGER — exact bytes for everything this proposal touches
**Scientific effect: NONE.** A matching byte identity is *custody*: evidence that a file is the file it claims to be. It is not correctness, not currentness, and not acceptance of any theorem, lemma, prize or bound.

## Nothing is copied into this repository
Every package is a **submodule gitlink** (`mode 160000`) pinned at an exact commit. No proof body, stub, register or checker is duplicated here, so there is no second copy that can silently drift from its source. The rows below therefore record identities *in their home repositories* — what this proposal points at, and what it changed in `query-` — rather than a manifest of vendored files.

If a future revision does vendor bytes, every copied file must gain a row here with its origin repository, origin path, git blob and SHA-256 before the copy lands.

## Rows
| repository | ref | path | bytes | sha256 | git blob | role |
|---|---|---|---|---|---|---|
| `query-` | `integration/public-src-20260926` | `portable/FEDERATION_IDENTITY_TRANSITION.json` | 4373 | `d25a850f5459144b8e9d2f88…` | `14549e51fcd8…` | identity transition record authored for PR #16 |
| `query-` | `integration/public-src-20260926` | `tests/test_federation_identity.py` | 4547 | `d35ecfbe9e7c9c2304956419…` | `6c6328780e32…` | replacement control for the deleted pinned_federation_match step |
| `query-` | `integration/public-src-20260926` | `research_query.py` | 541 | `b49d32fed78ee78f688fee8e…` | `0a89183d0499…` | compatibility wrapper (CURRENT identity) |
| `query-` | `main` | `research_query.py` | 5577 | `54105dcd723e71b19263afc8…` | `c2dd46a24ed9…` | canonical implementation (SUPERSEDED identity) |
| `query-` | `integration/public-src-20260926` | `portable/CANDIDATE_DOWNSTREAM_GATE_STUBS.json` | 4180 | `a88c7982053b60108fe19a84…` | `2bd2dec9d2c0…` | downstream gate stub bundle, refreshed to the Math- default tip |
| `Math-` | `10e1f191c7d9…` | `frontiers/downstream_gate_20260925/README.md` | 3559 | `574ed537cf8992bb3f86fae1…` | `7f07316b733a…` | downstream hard-gate artifact pinned by query-'s stub bundle |
| `Math-` | `10e1f191c7d9…` | `frontiers/downstream_gate_20260925/SCOPE.md` | 2218 | `c7b5bb0ec34f53395b96ae24…` | `ed8c56a88c48…` | downstream hard-gate artifact pinned by query-'s stub bundle |
| `Math-` | `10e1f191c7d9…` | `frontiers/downstream_gate_20260925/hard_gate.py` | 26557 | `1954723d143a3d68cbf3834b…` | `52ec0030579a…` | downstream hard-gate artifact pinned by query-'s stub bundle |
| `Math-` | `10e1f191c7d9…` | `frontiers/downstream_gate_20260925/test_hard_gate.py` | 18920 | `24bf0ae39c3b36ff253ee7db…` | `62c5e249b207…` | downstream hard-gate artifact pinned by query-'s stub bundle |
| `Math-` | `10e1f191c7d9…` | `frontiers/downstream_gate_20260925/RESULTS.json` | 6509 | `2fd874894334f65b57bbab43…` | `869d7170e46d…` | downstream hard-gate artifact pinned by query-'s stub bundle |
| `Math-` | `10e1f191c7d9…` | `frontiers/downstream_gate_20260925/run_validation.py` | 7517 | `2f71b34d5a241402e26c0e00…` | `d0607468b92f…` | downstream hard-gate artifact pinned by query-'s stub bundle |
| `Math-` | `10e1f191c7d9…` | `frontiers/downstream_gate_20260925/GRAPH.json` | 15375 | `065e6a756060097bcef35055…` | `23a6759eb0e8…` | downstream hard-gate artifact pinned by query-'s stub bundle |

## The one identity that changed, and why it is recorded rather than restored
`query-/research_query.py` appears twice above. On `main` it is the canonical implementation; on the src-migration line it is a compatibility wrapper, so its bytes differ. The pre-migration workflow asserted the old byte count inline and that assertion was deleted in the same change that invalidated it. Re-asserting the old count would be false, so both identities are on record and the current one is pinned by a test. `trial/federation/replay.py` pins the superseded bytes at an immutable commit and is unaffected.
