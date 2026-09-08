# Issue #36 machine-translation convergence

- Campaign: `issue36-machine-translation-convergence-20260909-v1`
- Start point: `8054ea159bd99b3531678048b5453aedd902e4ed`
- Current unresolved input: **542** (prior 14 READY carried forward separately)
- Auto-filled by lightweight route: **379**
- Lightweight rejected: **163**
- Strict review: **26**
- English fallback: **137**
- Obvious mistranslation: **0**
- Carry-forward strict accepted: **14**
- Replay: **PASS**; protected boundary: **PASS**
- `production_modified: NO`

## Decision model

Machine candidate → lightweight safety audit → strict review for flagged/high-risk rows → English canonical fallback for unresolved rows. The canonical English remains visible and authoritative; no candidate is promoted to production.

## Review output

- `translation_table.csv` / `translation_table.md`: all 556 rows including carry-forward.
- `human_review.csv`: every strict-review and English-fallback row.
- `machine_candidates.jsonl`, `lightweight_audit.jsonl`, `strict_review.jsonl`: complete machine/audit trace.

## Boundaries

No production data, `data/**`, #32 bridge, #35 UI, `CURRENT_DEV_TASK.md`, `main`, or Stage10 A/B state was modified. Promotion is `NOT_AUTHORIZED`.
