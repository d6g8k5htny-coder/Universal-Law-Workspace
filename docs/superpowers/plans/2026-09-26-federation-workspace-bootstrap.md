# Federation Workspace Bootstrap Implementation Plan

> **Execution:** inline on `chatgpt/federation-bootstrap-20260926`; Claude provides the fresh cross-model review.

**Goal:** Establish the smallest testable federation workspace that cannot silently become a second scientific-status or repository-role store.

**Architecture:** Keep the workspace dependency-light and read-only with respect to other repositories. A JSON manifest records topology and observed blob pins; a standard-library checker enforces the local boundary. Machine repository roles stay in `meta-framework/registry.json`.

**Tech Stack:** JSON, Python 3.11 standard library, unittest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-26-federation-workspace-design.md`

## Global Constraints

- Scientific effect NONE.
- No proof-body migration.
- No cross-repository writes in this slice.
- No mathematical promotion/status authority.
- No duplicate machine repository-role registry.
- Exact external observations use git blob SHA.
- CI uses read-only contents permission.

## Review Focus

- Any path by which a scientific-state key can enter the manifest unnoticed.
- Any wording or field that turns an observed pointer into a new canonical owner.
- Any stale-branch assumption presented as permanent authority.
- Any accidental public disclosure of private sandbox content.
- Any future repository addition that bypasses explicit contract review.

### Task 1: Federation contract and negative controls

**Files:** `workspace/repositories.json`, `tests/test_workspace_contract.py`, `tools/check_workspace.py`

- [x] Write the initial contract tests before the checker.
- [x] Run the tests and observe failure because the checker does not exist.
- [x] Implement the minimal fail-closed checker.
- [x] Run the initial test suite and checker to green.
- [x] Add regression tests preventing duplicate machine role metadata and out-of-federation canonical inputs.
- [x] Observe GitHub Actions run 36250945742 fail in exactly those new paths before changing the checker.
- [x] Remove role duplication and enforce canonical-input federation membership.

### Task 2: Human/agent entry points and CI

**Files:** `README.md`, `AGENTS.md`, `.github/workflows/ci.yml`

- [x] Explain the federation role and non-authority boundary.
- [x] Point role lookup to the canonical meta-framework registry rather than duplicating machine roles.
- [x] Provide the local verification commands.
- [x] Run the same checker/tests in read-only CI.

### Task 3: Cross-model review handoff

- [x] Open a PR from the isolated branch.
- [x] Ask Claude on both the workspace PR/issue context and `main#129` to review duplicate authority, proof identity, cross-repo coupling, privacy/publication leakage, and stale ref assumptions.
- [ ] Fix any Critical/Important review findings with a new failing test first.
- [ ] Merge only after the reviewed head is green.
