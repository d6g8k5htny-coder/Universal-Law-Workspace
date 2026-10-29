"""Mutation result classifier; retained legacy behavior for its adverse RED."""
def intended_failure(process, test, nonce, event):
    output = process.stdout + process.stderr
    return (process.returncode == 1 and "FAIL: " + test in output
            and "FAILED (failures=1)" in output and "ERROR:" not in output)
