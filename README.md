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
git clone --recurse-submodules https://github.com/d6g8k5htny-coder/Universal-Law-Workspace
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

## Checking this repository itself

```bash
python3 scripts/verify_workspace.py              # refuses if the map misdescribes itself
python3 -m unittest discover -s tests -v         # 26 negative controls, standard library only
python3 scripts/generate_ledgers.py              # BRANCH_MAP.md must come back unchanged
```

`scripts/verify_workspace.py` enforces nine things: the gitlink SHAs equal the recorded
tips; `.gitmodules` carries public clonable URLs; no package is missing and none has
appeared; no **tracked** file carries a credential, a private relay address or a mention
of the excluded private package; every named ref has a 40-hex SHA and a stated reason;
`BRANCH_MAP.md` carries every recorded SHA **and** branch name; the host repository's own
refs — including the other bootstrap lane's — are recorded and mapped; `HEAD` descends
from the owner's root commit; and every category — packages, named refs, omissions, host
refs, scanned files — must be non-empty, so a run that checked nothing in one of them is
a failure for that category rather than a pass.

The controls in `tests/` are the deliverable, not decoration. Each one weakens exactly one
of those facts and asserts the verifier then **refuses**. Writing them found four real
defects in the verifier they were written for — two of them fail-open, meaning the checker
reported success on a tree it was supposed to refuse:

1. it scanned raw disk rather than tracked files, so compiled `__pycache__` bytecode —
   ignored, untracked, in no clone — failed the tree, because Python folds `'a' + 'b'` at
   compile time and the `.pyc` carried the very literals its source assembles at runtime
   in order not to carry them;
2. it compared SHAs but not branch names, so when two refs shared a SHA a ref could vanish
   from `BRANCH_MAP.md` while a sibling row kept the check satisfied — the failure mode
   that would have hidden the other lane's branch;
3. its vacuity floor was a single total, `compared < 30`, and a single total is propped
   up by growth in an unrelated category: adding two files to the tree lifted the
   tracked-file scan's contribution over the constant on its own, and the control that
   empties the entire manifest silently stopped failing. Each category now carries its own
   floor, with the total kept only as a coarse backstop behind them;
4. the harness's own `git mktree` and `git hash-object --stdin` inherited the runner's
   standard input and blocked forever instead of failing, so the suite hung rather than
   reported.

Every control runs against a real recursive copy, and one control asserts the copy's
inodes differ from the original — an earlier harness in a sibling package used `cp -al`
and wrote straight through into the live checkout.

## The ledgers

| file | what it records |
|---|---|
| [`BRANCH_MAP.md`](BRANCH_MAP.md) | every included ref, its exact SHA and why; plus every open ref deliberately **not** imported, and why not |
| [`MERGE_LEDGER.md`](MERGE_LEDGER.md) | every merge performed — base, head, conflicts, resolution, scientific effect; and every merge deliberately not performed |
| [`IDENTITY_LEDGER.md`](IDENTITY_LEDGER.md) | bytes, SHA-256 and git blob for everything this proposal touches, computed from real bytes rather than typed |
| [`CONFLICT_LEDGER.md`](CONFLICT_LEDGER.md) | five places where two trees disagreed — three still live, two **resolved by the owner** and marked so in place rather than deleted. **Both sides kept. No winner picked here.** |

[`WORKSPACE.json`](WORKSPACE.json) is the machine-readable source for the first of
those; `BRANCH_MAP.md` is generated from it so a SHA is never retyped.

## Two lanes are bootstrapping this repository

[Issue #1](https://github.com/d6g8k5htny-coder/Universal-Law-Workspace/issues/1) divides
the bootstrap between two lanes and assigns the repository map, the validator, the
negative controls and CI to the other one. This branch built a map and a validator
before that issue existed, so the slices overlap. Nothing was resolved by pushing first:

- `main` is untouched. This branch descends from the owner's root commit
  `fcd1d01ed87b…` by an ordinary merge — no force-push, no rebase of anyone's history,
  no orphan tree. `scripts/verify_workspace.py` checks that descent mechanically and
  refuses if it is ever broken.
- `chatgpt/federation-bootstrap-20260926` is untouched. It is now open as PR #2 with a
  real tree — a federation contract, a fail-closed validator, contract tests and CI — so
  the overlap is byte-level, not hypothetical. Colliding paths are `README.md`, `tests/`
  and `.github/workflows/`; everything else is disjoint.
- The exact branch and paths are posted on issue #1 and on PR #2, which is what that issue
  asks for, so the other lane can yield the slice, keep it, or land both.
- That PR asked for a review and got one: **AMEND**, with one blocking fail-open in its
  authority boundary and a verified patch, delivered as a comment and **not** pushed to its
  branch. The review declares the conflict of interest — it comes from the author of the
  competing proposal — and carries **zero organizational independence credit**, so the
  independence-requiring gate stays open.
- `CONFLICT_LEDGER.md` **C5** records the overlap as live and unresolved, including the
  real hazard: two validators and two repository maps in one repository. Neither can
  promote anything — both fail closed and assert only documentation facts — but the
  duplication is a review question, not a merge question.

Whether this proposal, the other lane's, or a reconciliation of the two becomes the
workspace is the owner's decision. This is a proposal on a branch, not a replacement of
anything.

## What this repository does not establish

- **No mathematics.** Not one bound, lemma, theorem or prize disposition is asserted,
  verified or changed here.
- **No status movement.** No `lemma_closed` flag, `LANDING_CLAIMS` entry or
  `PROOF_INDEX` disposition is touched in any package.
- **No proof was rewritten** to fit this layout. Nothing was reshaped for tidiness.
- **A pin is custody, not currency.** A pinned commit is exactly those bytes; it says
  nothing about whether a newer commit supersedes it, and a package's default branch may
  have moved since. This is not hypothetical: **three of the seven defaults moved within
  about an hour** of this map's first publication. `scripts/report_tip_drift.py` compares
  every pin against the live default tip and prints the difference; it **exits 0 when it
  finds drift**, because drift is the normal life of a repository and a reporter that
  failed the build would push whoever hit it toward deleting the pin rather than recording
  the change. It exits nonzero only when it could not read a default branch at all, so
  "I could not look" never prints as "nothing has changed". Its first real run after the
  pins were refreshed immediately found `trial` had moved **again**, within minutes. That
  pin was deliberately not chased — the reporter's job is to show the difference, not to
  keep the map on a treadmill.
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
