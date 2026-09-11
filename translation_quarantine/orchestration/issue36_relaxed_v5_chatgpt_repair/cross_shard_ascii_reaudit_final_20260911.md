# Issue #36 V5 cross-shard ASCII re-audit final checkpoint

- Branch: `ui-ja/issue36-relaxed-v5-chatgpt-repair`
- Source rows reviewed: 30,629 / 30,629
- Shards complete: 31 / 31
- Override rows: 10,691
- Materialization: PASS
- Canonical uniqueness/order/identity: preserved
- `old_display_ja` vs frozen V4: PASS
- Duplicate override canonicals: 0
- HANGUL: 0
- RAW_ENGLISH_WRAPPER: 0
- CONTROL_CHAR: 0
- ASCII_SUSPICIOUS: 433

## Final ASCII re-audit disposition

The remaining `ASCII_SUSPICIOUS` rows were bulk human-triaged under the Issue #36 contract. ASCII presence alone is not a defect. Proper names, acronyms, product/model identifiers, official/romanized titles, platform names, and legitimate mixed Japanese/ASCII labels remain unchanged unless there is a clear semantic mismatch.

Final continuation repairs in this pass: 10 rows across `cross_shard_ascii_reaudit_continuation_0006.csv` through `0008.csv`.

No further row was changed merely to reduce the ASCII count. Residual 433 rows are accepted as non-blocking review-detector hits for this V5 repair pass.

## Gate

- Production modified: **NO**
- Production promotion authorized: **NO**
- Issue #36 closure: **NO**
- Next gate: separate independent promotion audit against the frozen V5 quarantine artifact.
