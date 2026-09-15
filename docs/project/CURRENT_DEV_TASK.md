# CURRENT DEV TASK — ISSUE #74 WQHD DICTIONARY REDESIGN (ACTIVE)

最終同期: 2026-09-15

## Routing status

- **Issue #74 is the active DEV implementation lane** — `[DEV][POST-V1] WQHD-first dictionary workspace redesign`.
- Activation authority: live Issue #74 comment **`5674415910`**.
- Working branch: `codex/issue74-wqhd-dictionary-redesign`.
- Creation-time live main: `c42a7a61214c3acd5ea0160ef3206fc98f5c58db`.
- Issue #73 is completed and integrated into `main`; its English pane and safe `＋ / ✓` toggle are the accepted baseline for this work.
- Issue #72 is completed and integrated into `main`; its Prompt category view is a regression invariant.
- Issue #70 translation/data work remains separate. #74 must not modify #70 outputs, canonical/protected data, or translation lane state.
- Stage10 learning Issue #65 remains a separate user-learning route and is not part of #74.

## Task summary

1. Use a WQHD-first three-column dictionary workspace: practical 280–320px navigation, denser two-column results, and a practical 360–420px right pane.
2. Keep the existing Results order, search/ranking semantics, Prompt serialization, taxonomy, and #72/#73 behavior unchanged.
3. Show Tag Details above Current Prompt simultaneously in the right pane, retaining safe item-level Prompt operations and the Prompt Edit route.
4. Fall back to one result column at narrower widths without clipping Japanese labels or controls.

## Repository hygiene

- No new top-level folders, parallel WPF app, prototype/temp/tmp/output/build directories, or versioned artifact/screenshot folders.
- Keep implementation within the existing `src/DanbooruTagTool.App`, `Core`, `Data`, and `Tests` architecture.
- Do not change #70 translation data, canonical/protected data, taxonomy classification, or legacy data paths.
- Do not run `git clean -fdx` or `git clean -fdX`.

## Completion / return

- Validate Release build, all .NET tests, #74 focused tests, and `git diff --check`.
- If all validation passes, integrate into live `main` using fast-forward when possible (force push prohibited), push, synchronize this document and `CURRENT_STATE.md` to completed/merged with no successor active DEV selected, and close Issue #74.
- Final report must include branch, commit, changed files, WQHD widths/layout and fallback behavior, tests, UI confirmation, merge method/final main HEAD, docs sync, Issue close, protected-data check, hygiene, and clean working tree.
