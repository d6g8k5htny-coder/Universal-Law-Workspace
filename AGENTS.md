# Agent entry

Start with [README.md](README.md), then read [workspace/repositories.json](workspace/repositories.json) and the current engineering coordination issue.

## Hard boundary

This repository is a federation observer/router/checker. It is not a scientific-status authority.

Do not add fields that decide or restate theorem status, classification, grade, disposition, controlling state, lemma closure, promotion permission, prize closure, or independence credit. The validator is intentionally fail-closed on those keys.

Do not move proof bodies here merely to make the workspace look complete. Reference canonical objects where they already live, using exact repository/path/blob identity when a snapshot requires it.

## Working method

- Work on isolated branches and coordinate overlapping paths through issues/PRs.
- Treat source-role prose here as navigation, not as a substitute for the owning repository.
- Preserve the distinction between engineering verification and mathematical review.
- A green check means the local federation contract is structurally valid; it does not promote or close mathematical work.
- If an observed external pin changes, review why before refreshing it. A refresh records a new observation; it does not transfer authority here.

Owner authorization permits participating models to collaborate and improve the workspace without renewed per-change permission. That authorization does not change the scientific-effect boundary above.