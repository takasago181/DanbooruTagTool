# Issue #36 Independent Promotion Audit Handoff

## Purpose
This handoff is for a fresh, independent audit chat. The auditor must decide whether the current UI-JA V5 quarantine artifact is ready for production promotion.

Independence is required, but **the audit must also be time-efficient**. Do not repeat the full translation/re-audit campaign and do not manually reread all 30,629 rows.

Do not treat the previous translation/re-audit chat's PASS conclusion as authoritative. Reconstruct current state from GitHub canonical sources and make an independent judgment.

## Read order
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #36 latest comments
4. this file
5. `translation_quarantine/orchestration/issue36_relaxed_v5_chatgpt_repair/progress.json`
6. `translation_quarantine/orchestration/issue36_relaxed_v5_chatgpt_repair/materialized/materialization_report.json`
7. `translation_quarantine/orchestration/issue36_relaxed_v5_chatgpt_repair/materialized/language_sanity_report.json`
8. latest GitHub Actions result for `.github/workflows/ui-ja-v5-materialize.yml`
9. recent override files, especially the final cross-shard re-audit continuation/closeout batches
10. `materialized/final_translation_table_v5.csv` only as needed for targeted spot checks

## Branch / artifact
- branch: `ui-ja/issue36-relaxed-v5-chatgpt-repair`
- artifact root: `translation_quarantine/orchestration/issue36_relaxed_v5_chatgpt_repair/`
- production must remain unchanged during this audit
- resolve live branch HEAD at audit start; do not trust a stale SHA from chat history

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
- ASCII suspicious rows remain only a heuristic review bucket; ASCII presence itself is not a defect
- progress status: `SOURCE_REVIEW_COMPLETE_CROSS_SHARD_REAUDIT_COMPLETE_AWAITING_INDEPENDENT_PROMOTION_AUDIT`
- production_modified=false

These are claims to verify, not assumptions to inherit.

## Speed-first audit strategy
Use the following order. The goal is maximum confidence per unit time.

### Phase 1 — deterministic gate first
Verify from existing reports / live GitHub state:
- 30,629 source/materialized rows
- override count matches progress
- duplicate override canonicals = 0
- canonical identity/order preserved
- non-display columns preserved
- display_ja nonempty
- old_display_ja matches frozen V4
- hard-fail language checks = 0
- latest Actions run succeeded for the relevant live state
- production_modified=false

If any deterministic gate fails, return HOLD/FAIL immediately. Do not spend time on broad semantic sampling first.

### Phase 2 — targeted semantic spot audit only
Do **not** reread every row or every ASCII-suspicious row.

Use risk-based sampling, prioritizing:
1. all very recent cross-shard repair rows / final continuation batches
2. rows previously fixed for wrong entity, scope narrowing/broadening, actor-target inversion, template/meme confusion
3. adult / relation / action semantics
4. meme / style / cosplay qualifiers
5. uniforms / organizations / products / weapons / vehicles
6. proper nouns / brands / acronyms / official titles as a sanity control
7. a small random/representative sample of ordinary labels

Target roughly **30–60 semantic rows total**, unless a defect pattern requires expansion.

If one defect suggests a reusable pattern-wide problem, expand only that affected class. Do not restart a 30,629-row audit.

### Phase 3 — residual heuristic review
Do not manually re-audit all remaining ASCII-suspicious rows.

Check only:
- representative samples from the residual bucket
- suspicious rows with obvious machine-composition seams
- rows whose canonical/display mismatch looks semantically risky

Proper names, acronyms, products, model identifiers, official titles, romanization, and intentional English are valid reasons for ASCII to remain.

### Phase 4 — decision
Once deterministic gates pass and targeted semantic checks show no blocker/pattern drift, issue the verdict. Do not continue sampling just to increase volume.

## Efficiency rules
- Prefer batch reads / grouped comparisons over one-row-at-a-time work.
- Reuse deterministic reports when their generating workflow is current and verified; do not manually recompute information already enforced by the materializer unless inconsistency is suspected.
- Do not browse the web for routine labels. Use external verification only when a sampled row is materially ambiguous and the answer affects PASS/HOLD/FAIL.
- Do not polish mildly unnatural but semantically correct Japanese.
- Do not chase ASCII count toward zero.
- Do not inspect unrelated Issue #34 search ranking behavior.
- Stop early on a confirmed high-severity blocker and report it precisely.
- Keep progress updates brief; avoid narrating each row.

## Independence rules
- Do not reuse the previous chat's semantic decisions merely because they were marked repaired.
- Do not repair rows during this audit.
- If a defect is found, return HOLD/FAIL with exact canonical(s), current display_ja, evidence, severity, and recommended next repair step.
- Do not weaken criteria just to obtain PASS.
- Canonical English remains semantic source of truth; Japanese is UI/search support.
- Slightly awkward but semantically correct/readable Japanese is not a defect by itself.

## Scope contamination check
Confirm no unauthorized changes from this V5 quarantine work to:
- production `data/**`
- main
- #32 data/verdicts
- #35 UI code
- `CURRENT_DEV_TASK.md`
- Stage10 production A/B

Do this through targeted Git/commit/path evidence; do not manually inspect unrelated project history.

## Final decision
Return exactly one readiness verdict:
- `PROMOTION_AUDIT_PASS`
- `PROMOTION_AUDIT_HOLD`
- `PROMOTION_AUDIT_FAIL`

For PASS, summarize the deterministic gates, semantic sample coverage, and confirmation that production remains unchanged. PASS authorizes a later promotion step; it does not itself modify production.

For HOLD/FAIL, list blockers precisely and stop. Do not promote and do not repair in the same audit.

## Output record
After finishing, post the independent audit result to Issue #36 and, if useful, save a quarantine-only audit report under this orchestration root. Do not modify production in the same audit operation.
