# universal-law-workspace

A **public map** of the Universal Law research packages. Seven public repositories,
pinned by exact commit, with a branch map and three ledgers.

> ## This is not theorem acceptance
>
> Nothing in this repository accepts, promotes, closes or discharges any theorem,
> lemma, prize, bound or claim. It records **where code and proofs live and which exact
> bytes are being referred to** — custody, not correctness.
>
> A green check in any package is a *run*. A matching SHA-256 is *custody*. A catalog
> hit is *a lookup*. None of those is acceptance, and no document here upgrades one
> into another. Scientific effect of this repository: **NONE**.

## What this is, and what it deliberately is not

It is a map, not a merge. Every package below is a **submodule gitlink** pinned at an
exact commit, so:

- **no bytes are copied**, and there is no second copy that can drift from its source;
- the pin *is* the byte identity — a gitlink records a commit, so exactness is
  structural rather than a promise;
- no package's default branch is changed, moved or merged by anything here.

It is **not** a blind union of every historical ref. Of `Math-`'s 21 open pull
requests, four are included — the four that were named. Every omission is written down
in [`BRANCH_MAP.md`](BRANCH_MAP.md) as a decision, because an unrecorded omission is
indistinguishable from an oversight.

`sandbox` is **private and out of scope**. It was never cloned, read, copied or
referenced by content here, and [`scripts/verify_workspace.py`](scripts/verify_workspace.py)
fails if it is mentioned anywhere except as a declared exclusion.

## The packages

| path | repository | pinned at | role |
|---|---|---|---|
| `repos/main/` | [`main`](https://github.com/d6g8k5htny-coder/main) | `99f8c2b7db3c…` | q0 / SIDE24 program: registers, claim graph, engine, Drive source map, checkers |
| `repos/Math-/` | [`Math-`](https://github.com/d6g8k5htny-coder/Math-) | `10e1f191c7d9…` | frontiers, coefficients, downstream hard gate; 21 of the 22 public catalog artifacts |
| `repos/query-/` | [`query-`](https://github.com/d6g8k5htny-coder/query-) | `a61656fc7cbe…` | read-only exact-source lookup CLI and portable stub verifier |
| `repos/trial/` | [`trial`](https://github.com/d6g8k5htny-coder/trial) | `ff373ea56dfd…` | cross-repository federation controls, bounded public replay |
| `repos/governance-/` | [`governance-`](https://github.com/d6g8k5htny-coder/governance-) | `7476e29c65ce…` | operator protocols and governance records |
| `repos/meta-framework/` | [`meta-framework`](https://github.com/d6g8k5htny-coder/meta-framework) | `14f6836e7ccf…` | the curated public catalog (`registry.json`, 22 artifacts) |
| `repos/google-drive/` | [`google-drive`](https://github.com/d6g8k5htny-coder/google-drive) | `ea55c6e76edb…` | Drive-side public surface; 1 of the 22 catalog artifacts |

Each pin is the repository's **public reviewed default tip**. The other refs worth
reading — including `main`'s active research tree
`chatgpt/drive-github-hardening-20260919`, which is **named as a research tree and is
not presented as default `main`** — are listed in [`BRANCH_MAP.md`](BRANCH_MAP.md) with
their exact SHAs.

## Clone it

```bash
git clone --recurse-submodules https://github.com/d6g8k5htny-coder/universal-law-workspace
cd universal-law-workspace
```

Already cloned without submodules?

```bash
git submodule update --init --recursive
```

Want the named branches as real, checkout-able refs rather than SHAs in a document?

```bash
scripts/fetch_named_branches.sh      # fetches every ref BRANCH_MAP.md names, copies nothing
```

Check that this repository describes itself truthfully:

```bash
python3 scripts/verify_workspace.py  # gitlinks vs manifest, public URLs, no secrets, vacuity floor
```

## See the source

```bash
PYTHONPATH=src python3 -c "import universal_law_workspace as w; print(w.entry_points())"
```

`src/` holds **re-exports and documented entry points only** — no implementation. It
points into the submodules; it does not fork or vendor them. If a submodule is not
initialised, every accessor raises `WorkspaceNotInitialised` carrying the exact command
to fix it.

One thing to know before you look for the query package: **`query-`'s default branch has
no `src/` tree.** That is what [query- PR #16](https://github.com/d6g8k5htny-coder/query-/pull/16)
publishes, and it is green but unmerged, so the pin here is the reviewed tip without it.
`BRANCH_MAP.md` records both.

## Run the documented checks

Each check below says what it does **not** prove. `w.documented_checks()` returns the
same list programmatically.

```bash
# query- : legacy compatibility controls (38 tests)
cd repos/query- && python3 -B -S -m unittest \
    test_research_query.py test_catalog_entry_helper.py test_verify_portable_stubs.py
#   does not prove: that the catalog is current, or that any artifact is accepted

# query- : portable stub identities, and drift against Math-'s default tip
cd repos/query- && python3 -B -S verify_portable_stubs.py --check-math-tip
#   needs outbound access to raw.githubusercontent.com
#   does not prove: that the gate those bytes implement is sound — it compares bytes

# trial : cross-repository federation controls (20 tests)
cd repos/trial/federation && FEDERATION_WORKSPACE="$PWD/../../.." \
    python3 -B -S -m unittest test_federation
#   needs sibling checkouts named exactly Math-, query-, meta-framework, google-drive
#   does not prove: acceptance of any catalog artifact

# Math- : the downstream hard gate's own tests
cd repos/Math-/frontiers/downstream_gate_20260925 && python3 -B -S -m unittest test_hard_gate
#   does not prove: that a passing gate accepts anything
```

The `query-` **package** suite (`unittest discover -s tests`) needs the `src/` tree, so
it runs against PR #16's ref rather than the pinned default — see `BRANCH_MAP.md`.

## The ledgers

| file | what it records |
|---|---|
| [`BRANCH_MAP.md`](BRANCH_MAP.md) | every included ref, its exact SHA and why; plus every open ref deliberately **not** imported, and why not |
| [`MERGE_LEDGER.md`](MERGE_LEDGER.md) | every merge performed — base, head, conflicts, resolution, scientific effect; and every merge deliberately not performed |
| [`IDENTITY_LEDGER.md`](IDENTITY_LEDGER.md) | bytes, SHA-256 and git blob for everything this proposal touches, computed from real bytes rather than typed |
| [`CONFLICT_LEDGER.md`](CONFLICT_LEDGER.md) | four places where two trees disagree. **Both sides kept. No winner picked.** |

[`WORKSPACE.json`](WORKSPACE.json) is the machine-readable source for the first of
those; `BRANCH_MAP.md` is generated from it so a SHA is never retyped.

## What this repository does not establish

- **No mathematics.** Not one bound, lemma, theorem or prize disposition is asserted,
  verified or changed here.
- **No status movement.** No `lemma_closed` flag, `LANDING_CLAIMS` entry or
  `PROOF_INDEX` disposition is touched in any package.
- **No proof was rewritten** to fit this layout. Nothing was reshaped for tidiness.
- **A pin is custody, not currency.** A pinned commit is exactly those bytes; it says
  nothing about whether a newer commit supersedes it, and a package's default branch may
  have moved since. `scripts/fetch_named_branches.sh` reports drift rather than hiding it.
- **`verify_workspace.py` passing is a documentation-consistency fact** — the gitlinks
  match the manifest and no secret is present. It verifies no mathematics.
- **Review obligations are unaffected.** Nothing here discharges a review, and no
  same-provider review earns organizational independence credit by appearing in a map.

## A note for anyone editing this repository

The `repos/*` entries are **gitlinks with no working directory** in a fresh clone
(`git ls-files -s repos/` shows `mode 160000`). That means **`git add -A` will delete
them** — git sees a missing directory as a removal. It happened once while this
repository was being built, and `scripts/verify_workspace.py` caught it by reporting
`gitlinks=0`. Stage explicit paths, run the verifier before committing, and if you did
lose them, re-apply from the manifest:

```bash
python3 - <<'PY'
import json, pathlib, subprocess
m = json.loads(pathlib.Path('WORKSPACE.json').read_text())
for p in m['packages']:
    subprocess.run(['git','update-index','--add','--cacheinfo',
                    f"160000,{p['default_tip']},repos/{p['name']}"], check=True)
PY
```
