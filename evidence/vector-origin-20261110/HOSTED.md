# Source-bound hosted vector evidence

## Source-bound hosted observation — 10 November 2026, 09:11 UTC

For PR #78 head `64b4b360575b482432eb8f052d268ddcfbfca8c4` and base
`344f81f5cb1e7040dfedb2c752b9a3514775b257`, GitHub tested merge
`3ed8493993c18e5752398f5f7f655ff7898ed2f5` with tree
`a92e5876d2366ba06a085506546672be42604069`. Contract run `42787699084`,
job `129732985197`, passed 258 tests per mode without skips on CPython 3.11.
Its original artifact `13750121464`, SHA-256
`fef8bdc1bb7cfd7d71fda34b0fd0b1a150e4d2888d41773ce8781fd4fdd4629c`,
has 212 unique CRC-valid members. Independent verification matched all 13
declared baseline/mutant pairs per mode, their 52 source-bound events,
candidate bytes, stderr hashes and nonces. The PR and push pin jobs also
passed 258 normal-mode tests and their eight public pin checks. These results
are bound to their actual tested sources and do not qualify a later head.

The one-off artifact verifier refused missing evidence, altered source and an
inserted skip in both modes. Two source mutations of that verifier separately
reopened the matching false accepts; the synthetic adverse archives are
explicitly labeled. Original job logs, artifact bytes, verifier source,
controls and local 258-test-per-mode observations are retained in the linked
evidence bundle. None establishes final federation G0–G11 or scientific review.

Bundle `workspace-vector-hosted-20261110.zip`: 1,209,336 bytes,
98 members, SHA-256 `cf78bbf3afad769f78f8c04ee207cfc99b51c2494d8cbda3539fbff8f0680a4b`. All member
hashes and ZIP CRCs were checked locally. The original hosted artifact is
retained byte-for-byte inside; synthetic adverse ZIPs are separately labeled.

```sh
EVIDENCE_DIR="$(mktemp -d)"
python3 -B -S -m zipfile -e evidence/vector-origin-20261110/workspace-vector-hosted-20261110.zip "$EVIDENCE_DIR"
python3 -B -S "$EVIDENCE_DIR/verify_workspace78_contract.py" "$EVIDENCE_DIR/hosted-v2/contract-artifact-13750121464.zip" fef8bdc1bb7cfd7d71fda34b0fd0b1a150e4d2888d41773ce8781fd4fdd4629c "$EVIDENCE_DIR/verification.json"
python3 -B -S "$EVIDENCE_DIR/test_workspace78_contract_verifier.py" "$EVIDENCE_DIR/hosted-v2/contract-artifact-13750121464.zip" fef8bdc1bb7cfd7d71fda34b0fd0b1a150e4d2888d41773ce8781fd4fdd4629c "$EVIDENCE_DIR/new-adverse"
```

This fixed-scope verifier checks the named historical artifact and candidate
source bytes. It does not authenticate future runs, prove mathematical claims or
certify the federation. The adverse test creates explicitly synthetic copies
in the new directory; original files are left intact.
