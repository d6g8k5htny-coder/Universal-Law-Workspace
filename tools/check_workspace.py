#!/usr/bin/env python3
"""Fail-closed structural checks for the Universal Law federation manifest.

This checker validates only workspace topology and authority boundaries. It does
not contact GitHub, inspect proofs, or decide scientific status.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

WORKSPACE = "d6g8k5htny-coder/Universal-Law-Workspace"
REQUIRED_REPOSITORIES = {
    WORKSPACE,
    "d6g8k5htny-coder/main",
    "d6g8k5htny-coder/Math-",
    "d6g8k5htny-coder/meta-framework",
    "d6g8k5htny-coder/query-",
    "d6g8k5htny-coder/google-drive",
    "d6g8k5htny-coder/trial",
    "d6g8k5htny-coder/governance-",
    "d6g8k5htny-coder/sandbox",
}
REQUIRED_INPUTS = {
    "repository_registry",
    "scientific_authority_map",
    "downstream_gate",
    "landing_claims",
}
FORBIDDEN_STATE_KEYS = {
    "classification",
    "controlling",
    "terminality",
    "grade",
    "status",
    "disposition",
    "lemma_closed",
    "prizes_solved",
    "independence_credit",
    "promotion_permission",
}
BLOB_RE = re.compile(r"^[0-9a-f]{40}$")


class DuplicateJSONMemberError(ValueError):
    """A decoded JSON object repeats a member name."""


def _unique_json_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build one object without discarding repeated decoded member names."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            # Keep arbitrary names on one printable diagnostic line.
            name = json.dumps(key, ensure_ascii=True)
            raise DuplicateJSONMemberError(f"duplicate JSON member: {name}")
        result[key] = value
    return result


def _walk_forbidden_keys(value: Any, path: str = "$") -> list[str]:
    problems: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_STATE_KEYS:
                problems.append(
                    f"forbidden scientific-state key at {child_path}: {key}"
                )
            if key == "scientific_status_authority" and child is not False:
                problems.append(
                    f"authority asserted away from the single checked field "
                    f"at {child_path}"
                )
            problems.extend(_walk_forbidden_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            problems.extend(_walk_forbidden_keys(child, f"{path}[{index}]"))
    return problems


def check_manifest(data: Any) -> list[str]:
    problems: list[str] = []
    if not isinstance(data, dict):
        return ["manifest root must be an object"]

    if data.get("schema_version") != 1:
        problems.append("schema_version must equal 1")
    if data.get("workspace") != WORKSPACE:
        problems.append(f"workspace must equal {WORKSPACE}")
    if data.get("scientific_effect") != "NONE":
        problems.append("scientific_effect must equal NONE")
    if data.get("scientific_status_authority") is not False:
        problems.append("scientific_status_authority must be false")

    for key, value in data.items():
        if key == "scientific_status_authority":
            continue
        if key in FORBIDDEN_STATE_KEYS:
            problems.append(f"forbidden scientific-state key at $.{key}: {key}")
        problems.extend(_walk_forbidden_keys(value, f"$.{key}"))

    canonical_inputs = data.get("canonical_inputs")
    if not isinstance(canonical_inputs, dict):
        problems.append("canonical_inputs must be an object")
        canonical_inputs = {}
    for key in sorted(REQUIRED_INPUTS - set(canonical_inputs)):
        problems.append(f"missing required canonical input: {key}")
    for key, item in canonical_inputs.items():
        if not isinstance(item, dict):
            problems.append(f"canonical input {key} must be an object")
            continue
        for field in ("repository", "path", "observed_blob", "meaning"):
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                problems.append(
                    f"canonical input {key} missing non-empty {field}"
                )
        blob = item.get("observed_blob")
        if isinstance(blob, str) and blob and not BLOB_RE.fullmatch(blob):
            problems.append(
                f"canonical input {key} observed_blob must be a "
                "40-character lowercase git blob SHA"
            )

    repositories = data.get("repositories")
    if not isinstance(repositories, list):
        problems.append("repositories must be an array")
        repositories = []
    seen: set[str] = set()
    for index, item in enumerate(repositories):
        if not isinstance(item, dict):
            problems.append(f"repository entry {index} must be an object")
            continue
        full_name = item.get("full_name")
        if not isinstance(full_name, str) or not full_name:
            problems.append(f"repository entry {index} missing full_name")
            continue
        if full_name in seen:
            problems.append(f"duplicate repository: {full_name}")
        seen.add(full_name)

        if "role" in item:
            problems.append(
                "repository role metadata belongs to repository_registry: "
                f"{full_name}"
            )
        unsupported = sorted(set(item) - {"full_name", "role"})
        if unsupported:
            problems.append(
                f"repository {full_name} has unsupported keys: "
                + ", ".join(unsupported)
            )

    for full_name in sorted(REQUIRED_REPOSITORIES - seen):
        problems.append(f"missing required repository: {full_name}")
    for full_name in sorted(seen - REQUIRED_REPOSITORIES):
        problems.append(
            f"unexpected repository without contract update: {full_name}"
        )

    for key, item in canonical_inputs.items():
        if not isinstance(item, dict):
            continue
        source_repo = item.get("repository")
        if isinstance(source_repo, str) and source_repo not in seen:
            problems.append(
                f"canonical input {key} repository is not in federation: "
                f"{source_repo}"
            )

    return problems


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parents[1]
    path = Path(args[0]) if args else root / "workspace" / "repositories.json"
    try:
        data = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=_unique_json_members
        )
    except (OSError, json.JSONDecodeError, DuplicateJSONMemberError) as exc:
        print(f"problem: cannot read manifest {path}: {exc}")
        print("repositories=0 canonical_inputs=0 problems=1")
        return 1

    problems = check_manifest(data)
    for problem in problems:
        print(f"problem: {problem}")
    repositories = data.get("repositories") if isinstance(data, dict) else []
    canonical_inputs = data.get("canonical_inputs") if isinstance(data, dict) else {}
    repo_count = len(repositories) if isinstance(repositories, list) else 0
    input_count = len(canonical_inputs) if isinstance(canonical_inputs, dict) else 0
    print(
        f"repositories={repo_count} canonical_inputs={input_count} "
        f"problems={len(problems)}"
    )
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
