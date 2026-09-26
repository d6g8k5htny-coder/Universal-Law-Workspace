# Universal Law Workspace

**Supporting federation map and conformance surface for the Universal Law research program.**

The **only public front door is [d6g8k5htny-coder/main](https://github.com/d6g8k5htny-coder/main)**. This repository is deliberately narrower: it maps the repository set, pins observed cross-repository control inputs, and runs fail-closed structural checks. It is not a second research home and it is not a scientific-status authority.

## What this repository owns

- the supporting federation map;
- observed, byte-addressed pointers to canonical cross-repository control inputs;
- structural conformance checks for that map;
- engineering coordination for cross-repository navigation.

## What this repository does not own

It does **not** decide theorem correctness, claim grade, terminal classification, review disposition, lemma closure, independence credit, or promotion. It also does not own the machine repository-role map; existing repository roles remain in `meta-framework/registry.json`.

The machine-readable boundary is [workspace/repositories.json](workspace/repositories.json). Its validator rejects scientific-state fields and duplicate machine role metadata.

## Federation set

- [main](https://github.com/d6g8k5htny-coder/main) — canonical public front door
- [Math-](https://github.com/d6g8k5htny-coder/Math-)
- [meta-framework](https://github.com/d6g8k5htny-coder/meta-framework)
- [query-](https://github.com/d6g8k5htny-coder/query-)
- [google-drive](https://github.com/d6g8k5htny-coder/google-drive)
- [trial](https://github.com/d6g8k5htny-coder/trial)
- [governance-](https://github.com/d6g8k5htny-coder/governance-)
- [sandbox](https://github.com/d6g8k5htny-coder/sandbox)
- **Universal-Law-Workspace**

For canonical repository roles and public/private routing metadata, consult the pinned `repository_registry` source in [workspace/repositories.json](workspace/repositories.json).

## Verify the map

```sh
python3 tools/check_workspace.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

A green run means the local federation contract is structurally valid. It does not verify mathematics.

## Collaboration

Initial bootstrap coordination is [issue #1](https://github.com/d6g8k5htny-coder/Universal-Law-Workspace/issues/1). Keep this repository map-sized: no proof-body migration, no duplicate status database, and no attempt to flatten the research repositories into this tree.
