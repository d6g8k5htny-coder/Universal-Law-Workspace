# Immutable federation vector checks

This bounded structural verifier is undergoing hosted qualification. The
initial unchanged source at `be512430997757f415c5463ccfa9ad3056a504c5`
ran 252 normal Workspace tests and produced six intended test-body assertion
failures: tree/tag canonical refs and four path detours. There were no errors
or skips; optimized execution was not reached. Those failures remain evidence.

The current candidate adds two minimal guards, strengthens the existing real
descendant/filter controls and adds a thirteenth finite source mutant. It has
65 declared controls. Complete current-source normal/optimized qualification
and fresh fix review remain pending; no previous source or static inspection
is a passing substitute.

## Run and self-verify

Use CPython 3.11+ and Git 2.31+ on Linux/POSIX:

```sh
python3 -B -S tools/verify_federation_vector.py --root /absolute/siblings --vector /outside/vector.json --output /outside/new-offline.json
python3 -B -S tools/verify_federation_vector.py --root /absolute/siblings --vector /outside/vector.json --network --output /outside/new-network.json
python3 -B -S -m unittest discover -s tests -p 'test_verify_federation_vector*.py' -v
python3 -B -O -S -m unittest discover -s tests -p 'test_verify_federation_vector*.py' -v
```

Outputs must be new, nonsymlink files outside all selected checkouts; they are
created mode 0600. Without `--output`, the final receipt is JSON on stdout.
Exit 0 means all requested structural checks succeeded, 1 means a recorded
check/transport/drift failure, and 2 means a control/usage/output-setup error.
Offline success explicitly records network `NOT_REQUESTED`.

## Exact structural scope

The external JSON has exactly `schema: "cbz.federation-vector.v1"` and
`repositories`. Its map has exactly twelve full lowercase 40-hex commits:
`main`, `Math-`, `governance-`, `Universal-Law-Workspace`, `meta-framework`,
`query-`, `google-drive`, `trial`, `sandbox`, `d6g8k5htny-coder`,
`openclaw-custodian-validation` and `research-hosted-qualification`.
Choose immutable commits explicitly; moving defaults are not a final vector.

Each real sibling checkout must have the expected toplevel, selected HEAD/tree
and matching stage-zero index entries. The selected structural working inputs
must match their committed regular-file bytes and executable mode. The tool
checks eight Workspace gitlinks/pins/modules, including opt-in sandbox, and
four canonical byte bindings. An explicit canonical ref must identify a
native commit object and remains a separate immutable source; no age, ancestry, current authority or default-tip equality is inferred.
The native nine-public-repository navigation map remains distinct from the
twelve-repository vector.

The nine lock roots are Main `formal`; Math `formal`,
`frontiers/cap_first_exit_lean_20261002`,
`frontiers/determinant_moment_20261025`,
`frontiers/source_derivative_gaussian_20261025`,
`frontiers/source_lifetime_realization_20261017`,
`frontiers/source_smooth_realization_20261011`,
`specifications/lean_statement_proofs_20261011` and
`specifications/lean_statements_20261010`.

Native Lake schema 1.2.0 is checked without evaluating Lake code. Resolved Git
`rev` must be immutable; floating `inputRev` metadata, empty scope, null
subdirectory and Main's empty dependency list are legitimate. Repeated
dependency identities must agree. Path dependencies reject non-normalized detours and resolve inside the same
selected Git tree to declared package roots. Safe leading-parent traversal
through captured real ancestors is permitted; literal shortest-relative
spelling is not required. The actual sibling TOML target
has a strict dependency-name/target-lock/TOML-name agreement check; unsupported
path-target configuration formats fail closed.

General package records use `recorded_lock_name` and leave configuration
semantics `NOT_ASSESSED`. In the inspected Math source `f532c3e2`, SDGA's lock
records `source_smooth_realization` while its TOML configuration declares
`source_derivative_gaussian`. The tool preserves this metadata, does not
repair Math and does not claim general package-name consistency. Build/replay
drivers must select the intended package rather than trust that stale name.

## Network availability and execution limits

Only after local structural success, `--network` fetches every distinct required
source/canonical/dependency commit into private temporary bare metadata and
verifies its exact identity and commit type. `ls-remote` alone cannot prove
availability of arbitrary exact commits. There is no default-tip equality
requirement for an immutable vector. Missing private access is a required
failure, never a successful skip. An unpublished candidate can pass offline
structure and fail its own remote-availability observation.

Success observes commit availability then; it does not establish complete
history/blob hydration, installed dependency identity, future availability or
global G7. Network transport trusts the caller's authentication/proxy/TLS
setup. Source configuration cannot supply hooks, filters, fsmonitor,
replacement objects, implicit fetching or non-HTTPS execution paths. Raw
network diagnostics, environment values, credentials and private source
contents are not serialized.

Each Git child has a 60-second limit. Control/selected blobs are bounded at
16 MiB and listings at 128 MiB. These acceptance bounds are not a memory/disk
sandbox. Timeout kills/reaps the child group; cleanup uncertainty stops further
requests and preserves `status: CLEANUP_ERROR` with
`error_code: NETWORK_CLEANUP_ERROR`. Transport failures are never silently
retried or replaced by an earlier success.

No selected-repository Git status, Lean, Lake, build or project Python is run.
HEAD/index and selected-input endpoint checks leave other tracked working
bytes, index flags/extensions, untracked/ignored files, stashes, worktrees and
ref administration unassessed. Reports permanently retain
`full_tracked_working_parity: NOT_ASSESSED`, `git_hygiene: NOT_ASSESSED`,
`cbz_green: false` and `semantic_claim_completeness: false`. The qualified Main
inventory is the separate full tracked-byte component. Restored-state malicious
writers, hostile runtimes and fabricated internally consistent receipts are
outside this bounded trust model.

## Evidence and remaining obligations

The thirteen declared source mutants require a copied-source baseline and one
designated selected-body assertion failure per mutant. Nonce/source bindings
and classifier controls reject malformed populations, errors, skips,
subject/lifecycle-origin assertions, silent exits and forged transcript text.
This finite campaign is not universal grader soundness or execution
authentication. An external `CBZ_VECTOR_MUTATION_EVIDENCE` directory retains
child transcripts when requested.

Earlier development passes remain bound to their tested sources. Final local
focused attempts hit process-creation exhaustion and receive no passing credit.
Only six final-source Git-free cleanup/classifier controls and static
syntax/anchor checks completed after that incident. Source recovery matched
the three original code/test Git blobs and SHA-256 identities; it did not run
the full final population. Hosted qualification and fresh review must precede
admission.

The final vector/tag, full source inventory, proof/classification reconciliation,
complete quarantine/isolation, actual G0–G11, canonical semantic truth,
cold-start and Git/ref administration remain outstanding. This component awards
no Layer A result, global gate, CBZ criterion, scientific independence or CBZ-0.

## Hosted experiment retention

The ordinary federation-contract workflow records normal and optimized finite
campaigns separately under runner-temporary storage through
`CBZ_VECTOR_MUTATION_EVIDENCE`. It prints original summary/event observations
and hashes, and always uploads the original logs, candidate copies, events and
child stdout/stderr. Missing or malformed evidence remains explicit. The
reporter adds visibility and does not regrade tests or turn failed execution
into success. Artifact metadata or printed fields alone do not establish that
a reviewer downloaded and hashed every original ZIP member.
