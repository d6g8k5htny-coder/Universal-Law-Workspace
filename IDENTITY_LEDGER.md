# IDENTITY_LEDGER — exact bytes for everything this proposal touches
**Scientific effect: NONE.** A matching byte identity is *custody*: evidence that a file is the file it claims to be. It is not correctness, not currentness, and not acceptance of any theorem, lemma, prize or bound.

## Nothing is copied into this repository
Every package is a **submodule gitlink** (`mode 160000`) pinned at an exact commit. No proof body, stub, register or checker is duplicated here, so there is no second copy that can silently drift from its source. The rows below therefore record identities *in their home repositories* — what this proposal points at, and what it changed in `query-` — rather than a manifest of vendored files.

If a future revision does vendor bytes, every copied file must gain a row here with its origin repository, origin path, git blob and SHA-256 before the copy lands.

## Rows
| repository | ref | path | bytes | sha256 | git blob | role |
|---|---|---|---|---|---|---|
| `query-` | `6c8389bf8566…` | `portable/FEDERATION_IDENTITY_TRANSITION.json` | 4373 | `d25a850f5459144b8e9d2f88…` | `14549e51fcd8…` | identity transition record; exists ONLY at this sha, on the branch of closed PR #16, and is recoverable from it |
| `query-` | `6c8389bf8566…` | `tests/test_federation_identity.py` | 4547 | `d35ecfbe9e7c9c2304956419…` | `6c6328780e32…` | the 7 controls written for that record; also only at this sha |
| `query-` | `76e1ca09a483…` | `research_query.py` | 541 | `b49d32fed78ee78f688fee8e…` | `0a89183d0499…` | compatibility wrapper, now on the DEFAULT branch (CURRENT identity) |
| `query-` | `a61656fc7cbe…` | `research_query.py` | 5577 | `54105dcd723e71b19263afc8…` | `c2dd46a24ed9…` | canonical implementation at the PREVIOUS default tip (SUPERSEDED identity, still reachable there; trial/federation/replay.py pins it at an immutable commit) |
| `query-` | `76e1ca09a483…` | `tests/test_wrapper_parity.py` | 2029 | `492129ead5277e8f59c64a1f…` | `fb88e325b173…` | the control that actually guards the cross-repository interface on the default branch: test_wrapper_reexports_legacy_api asserts the names trial imports |
| `query-` | `76e1ca09a483…` | `portable/CANDIDATE_DOWNSTREAM_GATE_STUBS.json` | 4180 | `a88c7982053b60108fe19a84…` | `2bd2dec9d2c0…` | downstream gate stub bundle at the Math- default tip, now on the default branch |
| `universal-law-workspace` | `fcd1d01ed87b…` | `README.md` | 25 | `d17ad4a96b30b8965cfde2dc…` | `b4bb1f6da58b…` | auto-init stub present when the repository was created (SUPERSEDED by this branch, still reachable at that commit) |
| `Math-` | `10e1f191c7d9…` | `frontiers/downstream_gate_20260925/README.md` | 3559 | `574ed537cf8992bb3f86fae1…` | `7f07316b733a…` | downstream hard-gate artifact pinned by query-'s stub bundle |
| `Math-` | `10e1f191c7d9…` | `frontiers/downstream_gate_20260925/SCOPE.md` | 2218 | `c7b5bb0ec34f53395b96ae24…` | `ed8c56a88c48…` | downstream hard-gate artifact pinned by query-'s stub bundle |
| `Math-` | `10e1f191c7d9…` | `frontiers/downstream_gate_20260925/hard_gate.py` | 26557 | `1954723d143a3d68cbf3834b…` | `52ec0030579a…` | downstream hard-gate artifact pinned by query-'s stub bundle |
| `Math-` | `10e1f191c7d9…` | `frontiers/downstream_gate_20260925/test_hard_gate.py` | 18920 | `24bf0ae39c3b36ff253ee7db…` | `62c5e249b207…` | downstream hard-gate artifact pinned by query-'s stub bundle |
| `Math-` | `10e1f191c7d9…` | `frontiers/downstream_gate_20260925/RESULTS.json` | 6509 | `2fd874894334f65b57bbab43…` | `869d7170e46d…` | downstream hard-gate artifact pinned by query-'s stub bundle |
| `Math-` | `10e1f191c7d9…` | `frontiers/downstream_gate_20260925/run_validation.py` | 7517 | `2f71b34d5a241402e26c0e00…` | `d0607468b92f…` | downstream hard-gate artifact pinned by query-'s stub bundle |
| `Math-` | `10e1f191c7d9…` | `frontiers/downstream_gate_20260925/GRAPH.json` | 15375 | `065e6a756060097bcef35055…` | `23a6759eb0e8…` | downstream hard-gate artifact pinned by query-'s stub bundle |

## The two identities that changed, and why they are recorded rather than restored
`query-/research_query.py` appears twice above, at two immutable shas. At `a61656fc7cbe` -- the default tip until 2026-09-26T15:08Z -- it is the canonical implementation at 5577 bytes. At `76e1ca09a483`, the default tip after PRs #13 and #14 merged, it is a 541-byte compatibility wrapper, so the transition has landed on the default branch rather than sitting on a proposal. The pre-migration workflow asserted the old byte count inline and that assertion was deleted in the same change that invalidated it; re-asserting the old count would be false, so both identities stay on record. The live interface is guarded on the default branch by `tests/test_wrapper_parity.py`, and `trial/federation/replay.py` pins the superseded bytes at an immutable commit, so it was never at risk.

`universal-law-workspace/README.md` is the second. The repository was created with a 25-byte GitHub auto-init stub and this branch replaces it with the map. The stub is not deleted: `fcd1d01ed87b…` is a parent of this branch, so `git show fcd1d01:README.md` returns those bytes verbatim. `CONFLICT_LEDGER.md` C5 records why it was replaced rather than kept at a second path.
