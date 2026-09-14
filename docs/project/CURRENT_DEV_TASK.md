# CURRENT DEV TASK — ISSUE #69 LOCAL MAINTENANCE

最終同期: 2026-09-14

## Routing status

- **Active lane: Issue #69 — [MAINT][LOCAL][FINAL] One-pass local workspace cleanup.** This is an explicitly user-prioritized local-maintenance pass, not product-code implementation.
- Latest DEV routing override: comment `5665797636`. Complete this one-pass cleanup before returning to Stage10.
- Issue #68 is completed at live main closeout commit `0fe636319e90947e0813388cbe7251e0057f7a9d`. Its Phase 2E result was a safe no-op; the old #64 primary checkout still needs a unique-material preservation check before normalization.
- Stage10 learning Issue #65 is paused by current priority until #69 completes. It remains a user learning lane, not a Codex implementation task.

## One-pass objective

Inventory the actual primary checkout and registered worktrees, preserve unique local-only evidence before retiring anything, normalize the primary checkout to current live `main`, retire only stale worktrees/material proven safe, keep required protected assets in place, and validate the current WPF shortcut/catalog/UserData flow. Finish and close #69 in this pass if no concrete unsafe path remains.

## Preserve boundaries

- Preserve protected/local source data and accepted #56/#63/#64 assets, Japanese overlay data, audit provenance, current production catalog, real `UserData`, local `artifacts/current/`, and root `DanbooruTagTool.lnk`.
- Do not delete unrecoverable or unique local-only evidence. If it cannot remain at its current path during normalization, preserve it in a clearly named ignored location with a hash manifest where practical.
- Do not duplicate multi-gigabyte protected datasets for appearance.
- Never use `git clean -fdx` or `git clean -fdX`.
- The current user-facing launcher remains WPF; do not restore the legacy Python/Tk launcher.
