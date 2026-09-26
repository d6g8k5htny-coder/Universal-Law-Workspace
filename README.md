# Universal Law Workspace

**Federation, conformance, and reproducibility surface for the Universal Law research program.**

This repository is the system-level front door for a multi-repository mathematical research workspace. It exists to make the repository topology, source identities, agent routing, and engineering checks easy to inspect without creating another scientific source of truth.

## What this repository owns

- workspace navigation and repository-role documentation;
- observed, byte-addressed pointers to canonical cross-repository control inputs;
- structural conformance checks for the federation contract;
- reproducibility/workspace snapshots added in later reviewed changes;
- engineering coordination between participating models.

## What this repository does not own

It does **not** decide theorem correctness, claim grade, terminal classification, review disposition, lemma closure, independence credit, or promotion. Green CI, a hash match, a merge, or model agreement is not mathematical acceptance.

The current machine-readable boundary is [workspace/repositories.json](workspace/repositories.json). Its validator deliberately rejects scientific-state fields so this repository cannot silently grow into a second promotion engine.

## Repository map

| Repository | Role |
|---|---|
| [main](https://github.com/d6g8k5htny-coder/main) | Research campaign, public reading path, reviews, discussion, and integration |
| [Math-](https://github.com/d6g8k5htny-coder/Math-) | Candidate proofs, mathematical programs, reproducible enclosures, and existing downstream gate surfaces |
| [meta-framework](https://github.com/d6g8k5htny-coder/meta-framework) | Machine-readable artifact routing and byte identities |
| [query-](https://github.com/d6g8k5htny-coder/query-) | Read-only exact-key lookup and local artifact verification |
| [google-drive](https://github.com/d6g8k5htny-coder/google-drive) | Selected public Drive replicas with source custody |
| [trial](https://github.com/d6g8k5htny-coder/trial) | Cross-repository engineering integration tests |
| [governance-](https://github.com/d6g8k5htny-coder/governance-) | Cross-repository working practices |
| [sandbox](https://github.com/d6g8k5htny-coder/sandbox) | Private exploratory experiments outside canonical public routing |
| **Universal-Law-Workspace** | Federation navigation, conformance, snapshots, and agent routing |

Role prose here is navigation. Canonical identity/status ownership remains in the referenced repositories; see the observed source pins in the manifest rather than treating this table as a status register.

## Verify the bootstrap

The bootstrap uses only Python's standard library:

```sh
python3 tools/check_workspace.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The checker validates the local federation contract. It does not contact GitHub or verify mathematics.

## Collaboration

Engineering coordination for the initial bootstrap is [issue #1](https://github.com/d6g8k5htny-coder/Universal-Law-Workspace/issues/1). Work on isolated branches, preserve exact external identities, and review overlap before editing shared surfaces.

For the design rationale, read [the federation design](docs/superpowers/specs/2026-09-26-federation-workspace-design.md).