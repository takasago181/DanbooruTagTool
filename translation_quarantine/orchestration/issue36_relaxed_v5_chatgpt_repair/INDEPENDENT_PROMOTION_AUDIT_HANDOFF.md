# Issue #36 Independent Promotion Audit Handoff

## Purpose
This handoff is for a fresh, independent audit chat. The auditor must decide whether the current UI-JA V5 quarantine artifact is ready to be promoted to production.

Do not treat the previous translation/re-audit chat's PASS conclusion as authoritative. Reconstruct the current state from GitHub canonical sources and make an independent judgment.

## Read order
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #36 latest comments
4. this file
5. `translation_quarantine/orchestration/issue36_relaxed_v5_chatgpt_repair/progress.json`
6. `translation_quarantine/orchestration/issue36_relaxed_v5_chatgpt_repair/materialized/materialization_report.json`
7. `translation_quarantine/orchestration/issue36_relaxed_v5_chatgpt_repair/materialized/language_sanity_report.json`
8. `translation_quarantine/orchestration/issue36_relaxed_v5_chatgpt_repair/materialized/final_translation_table_v5.csv`
9. recent override files under `translation_quarantine/orchestration/issue36_relaxed_v5_chatgpt_repair/overrides/`, especially cross-shard ASCII re-audit continuation/closeout batches
10. latest GitHub Actions result for `.github/workflows/ui-ja-v5-materialize.yml`

## Branch / artifact
- branch: `ui-ja/issue36-relaxed-v5-chatgpt-repair`
- artifact root: `translation_quarantine/orchestration/issue36_relaxed_v5_chatgpt_repair/`
- production must remain unchanged during this audit
- resolve the live branch HEAD at audit start; do not trust a stale SHA from chat history

## Current checkpoint to verify independently
At handoff creation time the quarantine state reports:
- source rows: 30,629
- completed shards: 31 / 31
- override rows: 10,691
- materialization: PASS
- canonical unique: true
- canonical identity/order preserved: true
- non-display columns preserved: true
- old_display_ja matches frozen V4 baseline: true
- duplicate override canonicals: 0
- language sanity hard-fail counts: HANGUL=0 / RAW_ENGLISH_WRAPPER=0 / CONTROL_CHAR=0
- ASCII suspicious rows remain as a review-only heuristic bucket; ASCII presence by itself is not a defect
- progress status: `SOURCE_REVIEW_COMPLETE_CROSS_SHARD_REAUDIT_COMPLETE_AWAITING_INDEPENDENT_PROMOTION_AUDIT`
- production_modified=false

These are claims to verify, not assumptions to inherit.

## Audit scope
Perform an independent promotion-readiness audit, not another translation campaign.

Required checks:
1. Verify deterministic integrity from source V4 -> overrides -> V5 materialized output.
2. Verify no duplicate canonical overrides and no chained override contract violations.
3. Verify 30,629 row count, canonical identity/order, non-display columns, non-empty display_ja, and frozen-V4 old_display contract.
4. Verify latest Actions materialize/sanity run is successful and corresponds to the live branch state.
5. Review the remaining language-sanity buckets as heuristics, not automatic failures.
6. Perform risk-based semantic spot checks across:
   - ordinary Japanese labels
   - proper nouns / brands / acronyms / official titles
   - meme / style / cosplay qualifiers
   - uniforms / organizations / products / weapons / vehicles
   - adult / relation / action terms where present
   - recent cross-shard repair batches
7. Pay special attention to recent repairs that corrected scope narrowing, wrong-entity substitutions, or template/meme confusion.
8. Confirm production `data/**`, main, #32 data, #35 UI code, CURRENT_DEV_TASK, and Stage10 production A/B were not modified by this V5 quarantine work.
9. Check for any evidence of branch drift or concurrent writes after this handoff; if found, audit the live state, not the stale checkpoint.

## Independence rules
- Do not reuse the previous chat's semantic decisions merely because they were marked repaired.
- Do not repair rows during the audit itself.
- If a defect is found, return HOLD/FAIL with exact canonical(s), evidence, severity, and recommended next repair step.
- Do not weaken criteria just to obtain PASS.
- Slightly awkward but semantically correct/readable Japanese is not a defect by itself.
- Do not 'fix' proper nouns, acronyms, product names, official titles, or intentional romanization merely because ASCII remains.
- Canonical English remains semantic source of truth; Japanese is UI/search support.
- Do not mix Issue #34 search-ranking behavior into Issue #36 translation-quality judgment.

## Final decision
Return exactly one readiness verdict:
- `PROMOTION_AUDIT_PASS`
- `PROMOTION_AUDIT_HOLD`
- `PROMOTION_AUDIT_FAIL`

For PASS, summarize evidence and confirm production is still unchanged. PASS authorizes a later promotion step; it does not itself modify production.

For HOLD/FAIL, list blockers precisely and stop. Do not promote.

## Output record
After finishing, post the independent audit result to Issue #36 and, if useful, save a quarantine-only audit report under this orchestration root. Do not modify production in the same audit operation.
