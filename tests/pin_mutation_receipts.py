"""Test-owned strict-pin mutation observations and fail-closed classifier."""
import json
import os
from pathlib import Path
import re


def record_event(case, event="invalid-source-accepted"):
    path = os.environ.get("CBZ_PIN_EVENT")
    if path is None:
        return
    nonce = os.environ.get("CBZ_PIN_NONCE")
    if nonce is None:
        raise RuntimeError("pin mutation observation has no run identity")
    Path(path).write_text(json.dumps({"test": case._testMethodName, "event": event, "nonce": nonce}))


def pin_protocol(process):
    output = process.stdout + process.stderr
    if "Traceback (most recent call last)" in output or "SyntaxError:" in output:
        raise RuntimeError("pin checker crashed rather than reporting a result")
    lines = process.stdout.splitlines()
    if process.returncode == 0 and any(line.startswith("verify_pins: OK (") for line in lines):
        return "accepted"
    if (process.returncode == 1 and any(line.startswith("FAIL: ") for line in lines)
            and any(line.startswith("verify_pins: FAIL (") for line in lines)):
        return "refused"
    raise RuntimeError("unexpected pin checker exit or missing result diagnostic")


def read_event(path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (ValueError, OSError):
        return None


def intended_failure(process, test, nonce, event):
    output = process.stdout + process.stderr
    kind = {"test_legacy_tip_difference_does_not_claim_ancestry": "unsupported-ancestry-claim",
            "test_initial_manifest_mismatch_does_not_start_remote_lookup": "unverified-source-contact",
            "test_missing_default_branch_is_rejected": "expected-policy-demoted",
            "test_missing_configured_branch_is_rejected": "expected-policy-demoted"}.get(
                test, "invalid-source-accepted")
    expected = {"test": test, "event": kind, "nonce": nonce}
    return (process.returncode == 1
            and type(nonce) is str and re.fullmatch(r"[0-9a-f]{32}", nonce) is not None
            and type(event) is dict and event == expected
            and re.search(r"^Ran 1 test in ", output, re.M) is not None
            and re.search(r"^FAIL: " + re.escape(test) + r"[ (]", output, re.M) is not None
            and re.search(r"^FAILED \(failures=1\)$", output, re.M) is not None
            and "ERROR:" not in output and "SyntaxError:" not in output
            and output.count("Traceback (most recent call last)") == 1)
