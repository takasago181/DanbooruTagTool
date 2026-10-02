# CURRENT STATE

最終更新: 2026-10-03 — #247 P0 + Batch A IMPLEMENTED / PR REVIEW STOP

## Current status

Production:
- #245 COMPLETE / CLOSED
- production source: `b3f48c359a8473c8bbf02347487cba5d8dacf96c`
- new LKG recorded
- Release 364 PASS / 4 SKIP / 0 FAIL
- real Create -> Forge -> PNG -> Library round-trip PASS
- UserData / Library / LoRA / catalog / protected authority preserved

Foundation:
- #248 COMPLETE / CLOSED
- report: `docs/issue248/FOUNDATION_AUDIT_2026-10-03.md`
- P0 + Batch A implemented after explicit user authorization; branch `foundation/batch-a`
- implementation checkpoint: `77899c9a`
- report: `docs/foundation/BATCH_A_CHECKPOINT_2026-10-03.md`
- worktree recurrence audit/remediation included by additional user instruction
- production not applied; Batch B not started

## Selected implementation / deferred scope

P0:
- archive/disable two Issue70 workflows that still write directly to main.

Batch A:
- semantic authority + catalog compiler cutover
- combine #249 + narrow #253
- preserve current semantic parity, especially adult/sexual/fetish/hard-niche Special discovery
- remove confirmed-dead old Special-only facet UI state

Batch B:
- active-tree evidence/tool/workflow/branch hygiene
- combine useful #250/#251/#252
- only after production dependencies are removed

Skipped now:
- broad #253 rewrite
- #254 performance/storage project
- #255 history rewrite

## Review stop

P0 + Batch A are stopped for PR review. Do not self-merge or start Batch B/new features.
Foundation Epic #247 remains open; installed production/LKG are unchanged.
