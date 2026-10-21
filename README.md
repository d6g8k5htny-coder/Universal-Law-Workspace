[![Universal Law — mathematics, evidence and verification](.github/brand-banner.svg)](https://d6g8k5htny-coder.github.io/main/site/)

# Universal Law Workspace

**Supporting federation map and conformance surface for the Universal Law research program.**

The **only public front door is [d6g8k5htny-coder/main](https://github.com/d6g8k5htny-coder/main)**. This repository is deliberately narrower: it maps the repository set, pins observed cross-repository control inputs, and runs fail-closed structural checks. It is not a second research home and it is not a scientific-status authority.


## Start with the map

```text
                         main
                  PUBLIC FRONT DOOR
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
        Math-          query-      meta-framework
     PROOF VAULT       LOOKUP          CATALOG
          │              │              │
          └──────────────┼──────────────┘
                         ▼
              CUSTODY / CONFORMANCE
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
        google-drive    trial      governance-
          custody    integration    protocols

        sandbox = bounded experimentation
        this repo = federation map + pinned topology
```

**New here?** Read [main](https://github.com/d6g8k5htny-coder/main) first.  
**Reading mathematics?** Go to [Math-](https://github.com/d6g8k5htny-coder/Math-).  
**Looking for an exact artifact?** Use [query-](https://github.com/d6g8k5htny-coder/query-).

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
- [google-drive](https://github.com/d6g8k5htny-coder/google-drive) (archived)
- [trial](https://github.com/d6g8k5htny-coder/trial) (archived)
- [governance-](https://github.com/d6g8k5htny-coder/governance-)
- [sandbox](https://github.com/d6g8k5htny-coder/sandbox) (archived)
- **Universal-Law-Workspace**

For canonical repository roles and public/private routing metadata, consult the pinned `repository_registry` source in [workspace/repositories.json](workspace/repositories.json).

## Pinned submodules

Beside the map, this repository pins each federation repository's default
branch tip as a git submodule under `repos/`. A pin is a gitlink: a pointer to
one commit, recorded in `.gitmodules` and in [`pins.json`](pins.json). No tree
is copied here and no branch is merged here; the research repositories stay
where they are and keep their own status records.

## Pinned repositories

| repository | path | default branch | pinned commit | note |
|---|---|---|---|---|
| main | `repos/main` | main | [b120e705654a773ac4ba04c324e5f85087e61ab4](https://github.com/d6g8k5htny-coder/main/commit/b120e705654a773ac4ba04c324e5f85087e61ab4) | default tip at generation time |
| Math- | `repos/Math-` | main | [10e1f191c7d9f2755ca971ddbba87874d2475619](https://github.com/d6g8k5htny-coder/Math-/commit/10e1f191c7d9f2755ca971ddbba87874d2475619) | default tip at generation time |
| meta-framework | `repos/meta-framework` | main | [14f6836e7ccf6a463ef6da745602debfea4d15ee](https://github.com/d6g8k5htny-coder/meta-framework/commit/14f6836e7ccf6a463ef6da745602debfea4d15ee) | default tip at generation time |
| query- | `repos/query-` | main | [76e1ca09a4838f84f20e28daa51eb024c0781dc1](https://github.com/d6g8k5htny-coder/query-/commit/76e1ca09a4838f84f20e28daa51eb024c0781dc1) | pinned by owner instruction |
| google-drive | `repos/google-drive` | main | [ea55c6e76edb31c48da5ce5aa0c3761d3ee49146](https://github.com/d6g8k5htny-coder/google-drive/commit/ea55c6e76edb31c48da5ce5aa0c3761d3ee49146) (archived) | default tip at generation time |
| trial | `repos/trial` | main | [f6c8a854bf083ccc737983dbfbf9195a6f8b75b3](https://github.com/d6g8k5htny-coder/trial/commit/f6c8a854bf083ccc737983dbfbf9195a6f8b75b3) (archived) | default tip at generation time; under active push during the import, re-measured immediately before commit |
| governance- | `repos/governance-` | main | [7476e29c65ce82d23e0b39e7f7d98741a875a8ff](https://github.com/d6g8k5htny-coder/governance-/commit/7476e29c65ce82d23e0b39e7f7d98741a875a8ff) | default tip at generation time |
| sandbox | `repos/sandbox` | main | [ea66efb6074b529adc5a09b2feb8a1e106a1520b](https://github.com/d6g8k5htny-coder/sandbox/commit/ea66efb6074b529adc5a09b2feb8a1e106a1520b) (archived) | opt-in (`update = none`); made public 2026-09-26 during the import, see below |

`pins.json` is the authoritative list; this table is a manually maintained
rendering of it. Keep the matching table row synchronized whenever a pin changes.
`tools/verify_pins.py` checks `pins.json` against the committed `HEAD` gitlinks
and `.gitmodules`; it does not read or validate this README table. With
`--network`, it also checks that public pinned commits exist on their remotes.
The test suite separately checks this README's full commit links and SHA set.

## Cloning

Fresh clone with the public submodules, shallow:

```sh
git clone --recurse-submodules --shallow-submodules https://github.com/d6g8k5htny-coder/universal-law-workspace
```

Existing clone:

```sh
git submodule update --init --depth 1
```

Neither command touches `repos/sandbox` (see below), so both work without
credentials.

## sandbox

`repos/sandbox` is committed as a gitlink like the others, but `.gitmodules`
marks it `update = none`, so `--recurse-submodules` and `submodule update
--init` skip it. The repository was private when this workspace was first
measured (2026-09-26T15:16Z) and was made public at 2026-09-26T15:19:20Z
while the import was running; the opt-in marking was kept so that a clone
never fails if the visibility changes again. Those with access initialise it
explicitly with `--checkout`, which overrides `update = none` for that one
command (without `--checkout` git prints "Skipping submodule 'repos/sandbox'"
and leaves the directory empty):

```sh
git submodule update --init --checkout --depth 1 repos/sandbox
```

Dropping the opt-in is a one-line pull request that removes `update = none`
from `.gitmodules` and sets `opt_in` to `false` in `pins.json`.

## Updating a pin

Start from a clean working tree on an isolated branch. Move the gitlink and
the matching `pins.json` entry together, manually update the table above, then
commit the local candidate before checking it (replace the placeholders):

```sh
git update-index --add --cacheinfo 160000,<full-sha>,repos/<name>
# edit pins.json: pinned_sha for repos/<name>
# update the matching README table row to the same full SHA
git add pins.json README.md
git diff --cached --check
git diff --cached --submodule=short
git commit -m "Update <name> pin"
python3 tools/verify_pins.py --network
```

Review the staged diff before committing. The checker reads gitlinks from
`HEAD`, not the index, so checking before the commit would compare the edited
`pins.json` with the old committed gitlink. Run verification from the clean
candidate checkout; a local commit does not push or merge anything. After the
checks pass, open the candidate pull request for review.

CI (`.github/workflows/pins.yml`) runs the same checker: the gitlink, `.gitmodules`
and `pins.json` must agree exactly (full SHA, never a prefix), and for public
entries the pinned commit must exist on the remote. A pin that is behind the
remote default tip is reported, not rejected. The negative controls in
`tests/` show the checker fails when any of these is broken:

```sh
python3 -m unittest discover -s tests -v
```

## What a pin is not

A pin is a pointer to a commit. It is not a review of that commit, not an
endorsement, and not a status. Status words for the program's claims live in
the registers in `repos/main`; nothing in this repository reads, sets or
implies them. The scientific effect of this repository is NONE: no proof is
held here, no original prize problem is solved here, and moving a pin changes
no claim's grade anywhere.

## License and citation

MIT, see [LICENSE](LICENSE). Cite via [CITATION.cff](CITATION.cff).

## Verify the map

```sh
python3 tools/check_workspace.py
python3 tools/verify_pins.py --network
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

A green run means the local federation contract is structurally valid and the
submodule pins agree with `pins.json` and exist on their remotes. It does not
verify mathematics.

## Collaboration

For contributor work, read [main's agent entry](https://github.com/d6g8k5htny-coder/main/blob/main/AGENTS.md) and the [current workflow](https://github.com/d6g8k5htny-coder/main/blob/main/governance/OP-WORKFLOW-20260930.md). Use the [active Agent Message Board #475](https://github.com/d6g8k5htny-coder/main/issues/475) for NEW coordination; [#419](https://github.com/d6g8k5htny-coder/main/issues/419), [#307](https://github.com/d6g8k5htny-coder/main/issues/307) and [#229](https://github.com/d6g8k5htny-coder/main/issues/229) remain readable history and do not transfer, renew or release earlier claims. Keep [#275](https://github.com/d6g8k5htny-coder/main/issues/275) for task and architecture discussion. Read the latest exact scope and current claims before pickup; follow an explicit successor pointer if either discussion moves.

The completed bootstrap record remains in [issue #1](https://github.com/d6g8k5htny-coder/Universal-Law-Workspace/issues/1). Keep this repository map-sized: no proof-body migration, no duplicate status database, and no attempt to flatten the research repositories into this tree.
