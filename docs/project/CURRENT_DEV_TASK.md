# CURRENT DEV TASK — LIVE ISSUE MIRROR / FALLBACK DIAGNOSTIC ONLY

> The live GitHub Issue is the executable task authority. Read `CURRENT_STATE.md`, then fetch Issue #55 and its latest checkpoint before implementation. If this mirror differs from the live Issue, fail closed and use neither stale content nor chat history to guess the contract.

最終同期: 2026-09-11

## Source

- Source Issue: **#55**
- Issue title: **[UI-JA][PRODUCTION][DEV] Promote audited Issue #36 V5 Japanese overlay**
- Issue state: **OPEN / ACTIVE**
- DEV state: **PRODUCTION_PROMOTION_IMPLEMENTATION_COMPLETE / AWAITING_INDEPENDENT_POST_WRITE_AUDIT**
- Working branch: `codex/issue55-ui-ja-production-promotion`
- Production base: live `main` `4ccf87cbe461779b9296d115fce19fc169b84a66`
- Audited input branch: `ui-ja/issue36-relaxed-v5-chatgpt-repair`
- Audited input HEAD at activation: `c221b3bcf97ad117482b4e8c411cf2edf419b5df`
- Independent audit checkpoint: Issue #36 comment `5633982018`, verdict `PROMOTION_AUDIT_PASS`
- Stop point: exactly `READY_FOR_POST_WRITE_AUDIT` or `HOLD_PRODUCTION_PROMOTION`
- Stage10 production A/B: **NOT STARTED**

## Scope

1. Identify the actual local Windows repo/runtime used to launch DanbooruTagTool.
2. Establish `LOCAL_ISSUE49_SYNC_PASS` before any Japanese-overlay write.
3. Confirm audited V5 artifacts are unchanged after the independent audit.
4. Back up the protected production overlay and record hashes/counts.
5. Materialize and fully validate a temporary format-version-1 overlay.
6. Atomically replace the actual production overlay.
7. Run deterministic post-write checks and relevant tests.
8. Perform focused real Windows UI acceptance against the same runtime.
9. Commit only non-protected evidence and stop for a fresh independent post-write audit.

## Hard boundaries

- Do not merge the quarantine branch into `main`.
- Do not re-audit or rewrite 30,629 Japanese translations.
- Do not change #34 ranking, #35 UI, #32/#49 generation data, semantic support, recommendation behavior, Prompt syntax, or Stage10 state.
- Do not commit protected `data/runtime/japanese_overlay.json` or its contents.
- Do not use `git clean -fdx` or `git clean -fdX`.
- No partial production write and no write without a rollback copy.
- Do not close Issue #36, merge the promotion branch to `main`, activate #42, or start Stage10 before the independent post-write audit PASS.

Implementation completion evidence is recorded in `docs/project/ISSUE55_PRODUCTION_PROMOTION_REPORT.md` and `docs/testing/ISSUE55_PRODUCTION_PROMOTION_MANIFEST.json`. Stop for a fresh independent post-write audit; the full contract remains the live Issue #55 body and latest checkpoint.
