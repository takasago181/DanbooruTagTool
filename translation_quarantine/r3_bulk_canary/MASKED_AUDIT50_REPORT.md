# Issue #36 final masked review input

Date: 2026-09-09 (Asia/Tokyo)
Branch: `ui-ja/issue36-r3-bulk-canary`

The existing 200-row canary artifacts were consumed as-is. The canary selector,
R3 evaluator, and replay were not run again.

## Composition

- Existing normal masked audit20: 20 rows, preserved by canonical membership.
- Hard adult semantic challenge: 10 rows.
- Additional sexual semantic challenge: 20 rows.
- Total masked reviewer input: 50 rows.
- Additional 30 rows are unique relative to the existing audit20 and each
  exists in the current canary or the frozen eligible P0 queue.
- Selection is deterministic under the separate audit50 seed in
  `masked_audit50_key.json`.

Challenge rows without frozen semantic or wording evidence remain blank in the
reviewer-facing fields. No semantic or Japanese wording evidence was guessed.

## Leakage and stop point

- `masked_audit50_leakage_check.json`: PASS.
- Reviewer input contains no state, risk, reason, key, selection category,
  source-membership marker, or prior verdict field.
- The separate audit50 key is retained for the independent reviewer context.
- Self-grading was not performed.
