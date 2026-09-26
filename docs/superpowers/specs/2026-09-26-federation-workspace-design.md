# Universal Law Federation Workspace Design

**Date:** 2026-09-26  
**Repository:** `d6g8k5htny-coder/Universal-Law-Workspace`  
**Coordination:** issue #1  
**Scientific effect:** NONE

## Goal

Create a small federation/control surface above the existing Universal Law repositories so humans and models can discover where work belongs, record exact observed source identities, and run structural conformance checks without introducing another scientific-status or repository-role authority.

## Context

The existing program is deliberately federated. `main` is the public/integration surface; `Math-` carries proofs, calculations, and existing downstream gate artifacts; `meta-framework` carries artifact routing/byte identities and the existing machine repository-role record; `query-` is read-only lookup; `google-drive` carries selected replicas; `trial` carries cross-repository engineering tests; `governance-` carries working practices; and `sandbox` is noncanonical experimentation.

The prior cross-repository design review identified two related failure modes: duplicating promotion/status authority and duplicating the machine repository-role/identity record. This design makes both failures mechanically harder.

## Authority boundary

This repository owns only:

1. federation navigation;
2. observed source pins used to explain what external objects were consulted;
3. local conformance rules for the federation manifest;
4. later reproducibility snapshots and agent-routing metadata, after review.

It never owns or writes mathematical status, grade, classification, controlling/terminal state, review disposition, lemma closure, prize closure, promotion permission, or independence credit.

It also never authors machine role metadata for the pre-existing repositories. That remains in `meta-framework/registry.json`.

The bootstrap consumes four observed external objects:

- `meta-framework/registry.json` for the sole machine repository-role record, artifact routing, and byte identities;
- `main:architecture/scientific_state/v1/AUTHORITY_MAP.json` on the currently active hardening branch for ownership boundaries;
- `Math-/frontiers/downstream_gate_20260925/GRAPH.json` for the existing downstream gate surface;
- `Math-/claims/LANDING_CLAIMS.json` for the existing landing projection.

Their git blob SHAs are observations, not transfers of ownership.

## Components

### `workspace/repositories.json`

A small, hand-readable federation manifest. Its repository entries contain identity only. Repository roles are intentionally absent and must be read from the pinned `repository_registry` source. The manifest also records exact observed git blob identities for the canonical inputs above.

The manifest carries `scientific_status_authority: false` and `scientific_effect: NONE`.

### `tools/check_workspace.py`

A standard-library fail-closed structural checker. It rejects:

- changing the workspace into a scientific-status authority;
- adding scientific-state fields anywhere else in the manifest;
- adding repository-role metadata to the workspace manifest;
- removing a required repository;
- silently adding an unreviewed repository;
- duplicate repository rows;
- canonical inputs whose source repository is outside the federation;
- unpinned canonical inputs.

It does not call GitHub and cannot certify mathematics.

### Tests and CI

The test suite exercises the positive manifest plus negative controls for each load-bearing rule. GitHub Actions runs the same checker and tests with read-only contents permission.

## Data flow

External authority records → human-reviewed observed blob pins in this repository → local structural checker → navigation/conformance result.

There is no reverse edge from this repository into scientific status or canonical role ownership.

## Error handling

The checker exits nonzero on malformed JSON, missing required data, forbidden state keys, duplicate role metadata, topology drift, an out-of-federation source, or an authority-boundary violation. It prints the failures explicitly. Unknown repositories fail until the contract is intentionally amended.

## Scope exclusions

This bootstrap does not:

- migrate proof bodies or mathematical packages;
- merge or close any existing research PR;
- change branch protection, repository visibility, or releases;
- mutate Drive;
- add a promotion engine;
- create automated cross-repository writes;
- create a second machine repository-role registry;
- assert that any mathematical claim is proved, reviewed, controlling, or closed.

## Next reviewed slices

1. Claude adversarial review of this bootstrap and the authority boundary.
2. A read-only cross-repository conformance snapshot that checks current refs against the manifest without mutating them.
3. Only after those are stable, a navigation link from `main` to this workspace.

Each later slice must preserve the one-way observer relation unless the owning repositories explicitly redesign their own authority contracts.
