# Issue #36 post-#41 bulk automation canary execution

Date: 2026-09-09 (Asia/Tokyo)
Branch: `ui-ja/issue36-r3-bulk-canary`
Validated R3 base/head: `53f02d9b3419db8fd9099b38204c29eed289ee8e` / `1c5a2cba7f8a0c5cd7c15ad510317c75d07d8851`

## Result

- Canary: 200 previously unseen P0 rows.
- Eligible unseen P0 pool: 825 rows.
- Canary membership hash: `e21529e18a3bf40701ac554c93dc67a9763dad41d93fb413ec61a339752ae6a6`
- Campaign state: `APPROVAL_EVIDENCE_AVAILABLE`.
- #32 bridge guard: official v2, required 7, resolved 7, blocked 0.
- Approval-capable frozen semantic evidence: 32; frozen identity-only rows: 200; frozen wording candidates: 32.
- R3 row states: `READY 32`; `REVIEW 168`; `STALE_REVIEW 0`; `CONTRADICTION 0`.
- Effective risk: LOW 168, MEDIUM 30, CRITICAL 2, HIGH_POSE_ACTION 0, HIGH_ANATOMY_ADULT 0.
- Eligible-pool risk: LOW 691, MEDIUM 122, CRITICAL 12, HIGH_POSE_ACTION 0, HIGH_ANATOMY_ADULT 0.
- No manual membership tuning was applied.

## Official #32 v2 bridge

- Source ref: `origin/dict-validation/quarantine:validation_quarantine/bridge_snapshots/ui_ja_issue41_overlap7_v2.json`
- Blob: `974bb9c971caf632f8ec73dff39fe4c55e60efaa`
- Snapshot version: `ui-ja-issue41-overlap7-v2`; content identity: `sha256:7e46f7f3655846a4f6ea2d1990e015701cbff5b123bdf8ef1809668f8a375ef5`.
- Snapshot rows: 7; `meaning_relevant_status=RESOLVED`: 7/7; frozen/pinned/immutable: 7/7; conflicts: 0.
- Canary bridge counts: `NOT_REQUIRED 200`; `AVAILABLE 0`; `BLOCKED_BRIDGE 0`.
- The exact raw snapshot is materialized only below this quarantine output and reused by replay.

## Determinism and leakage

- `original_vs_rerun1`: PASS
- `rerun1_vs_rerun2`: PASS
- `original_vs_rerun2`: PASS
- Replay mismatches: none.
- Masked audit20: 20 rows.
- Leakage check: PASS; masked fields, key values, and forbidden state literals leaked: none.
- `self_grade`: `NOT_PERFORMED`.

## Source identity correction

The historical raw-byte hashes differ because of line endings, so they remain provenance only. Both current Git blobs equal the validated-base blobs, and the normalized parsed-row content identities match. A focused test confirms LF and CRLF produce the same portable identity while a field/value change does not.

- Queue raw hash: `cbb280869707576cbac80a472f372a0becd80d80fbbd99a8d59220f74d331be7`
- Queue portable identity: `1196c44ae87bfd39684d2976ff0211f13bfbefebd7c747a237a61cf0f3c8a71d`
- Exclusion-set hash: `8f8ce1de330b84aec8b0c7f7439775a48ae27d2c27d8079a84f3e809e49f56b8`

The replay verifier reuses the original campaign's frozen evidence manifest and the exact materialized #32 v2 snapshot; no live evidence is re-fetched.

## Boundary and tests

- Production data modified: NO.
- `validation_quarantine` / #32-owned data modified: NO.
- #35 UI and `CURRENT_DEV_TASK.md` modified: NO.
- `main` modified or merged: NO.
- Remaining full P0 processed: NO.
- Stage10 production A/B started: NO.
- Semantic rule change required: NO.
- `tests/test_r3_bulk_canary.py`: 5 passed.
- Bridge guard tests were attempted, but pytest could not create/read its Windows temp root due an existing ACL (`PermissionError`); this was an environment setup failure before the test bodies. The runner's existing v2-object loader and fail-closed `meaning_relevant_status` guard were used unchanged.

## Stop point

This execution stops here. The separate `masked_audit20_key.json` is committed for independent review, but no blind20/audit20 self-scoring was performed.
