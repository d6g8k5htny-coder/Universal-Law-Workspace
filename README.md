# Universal Law Workspace

**Federation, conformance, and reproducibility surface for the Universal Law research program.**

This repository is the system-level front door for a multi-repository mathematical research workspace. It exists to make repository topology, source identities, agent routing, and engineering checks easy to inspect without creating another scientific source of truth.

## What this repository owns

- workspace navigation and links to the canonical repository-role registry;
- observed, byte-addressed pointers to canonical cross-repository control inputs;
- structural conformance checks for the federation contract;
- reproducibility/workspace snapshots added in later reviewed changes;
- engineering coordination between participating models.

## What this repository does not own

It does **not** decide theorem correctness, claim grade, terminal classification, review disposition, lemma closure, independence credit, or promotion. Green CI, a hash match, a merge, or model agreement is not mathematical acceptance.

It also does not own the machine repository-role map. Roles for the pre-existing federation are authored in `meta-framework/registry.json`; the workspace manifest deliberately lists repository identities only.

The current machine-readable boundary is [workspace/repositories.json](workspace/repositories.json). Its validator rejects scientific-state fields and duplicate machine role metadata so this repository cannot silently grow into a second promotion or role-authority engine.

## Federation set

- [main](https://github.com/d6g8k5htny-coder/main)
- [Math-](https://github.com/d6g8k5htny-coder/Math-)
- [meta-framework](https://github.com/d6g8k5htny-coder/meta-framework)
- [query-](https://github.com/d6g8k5htny-coder/query-)
- [google-drive](https://github.com/d6g8k5htny-coder/google-drive)
- [trial](https://github.com/d6g8k5htny-coder/trial)
- [governance-](https://github.com/d6g8k5htny-coder/governance-)
- [sandbox](https://github.com/d6g8k5htny-coder/sandbox)
- **Universal-Law-Workspace**

For machine repository roles and public/private routing metadata, consult the pinned `repository_registry` source in the workspace manifest rather than copying its fields here.

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