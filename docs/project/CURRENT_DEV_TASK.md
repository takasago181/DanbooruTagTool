# CURRENT DEV TASK — ISSUE #73 PANE TOGGLE REFINEMENT

最終同期: 2026-09-15

## Routing status

- **Active DEV implementation issue: #73** — `[DEV][POST-V1] English Prompt pane density + dictionary add/remove toggle`.
- This is a narrow post-v1 refinement on the accepted #72 main baseline. It does not reopen completed Issue #66 foundations.
- Roadmap parent: Issue #71.
- Prepared branch: `codex/issue73-pane-toggle-refinement`.
- Creation-time live main: `67c582504797dbda27dec41ea582d88e15a7d54c`.
- Issue #72 remains completed and integrated into `main` at `174fee90b23e4a350ffe71d7b60aa834b8cb1296`.
- Issue #70 translation/data work is separate. #73 must not modify #70 outputs, canonical/protected data, or translation lane state.
- Stage10 learning Issue #65 remains a separate user-learning route and is not part of #73.

## Task summary

1. Narrow the shared right-side `実際のEnglish Prompt` pane toward a 75:25 left:right layout while retaining a readable minimum width and preserving English content, copy, and direct-edit behavior.
2. Make dictionary `＋ / ✓` a safe add/remove toggle using exact recognized Prompt item identity:
   - absent canonical: `＋` appends;
   - exactly one recognized match: `✓` removes that exact item and supports Undo/re-add;
   - duplicate canonical matches: keep duplicates, do not guess or bulk-delete, and guide the user to Prompt editing;
   - raw/unresolved lookalikes remain untouched;
   - dictionary rows and Tag Details use the same behavior.

## Repository hygiene

The user explicitly requires a clean folder structure.

- No new top-level folders.
- No parallel/prototype app copy.
- No `prototype/`, `temp/`, `tmp/`, `output/`, `build/`, versioned artifact or screenshot directories.
- Keep code changes within the existing `src/DanbooruTagTool.App`, `Core`, `Data`, and `Tests` architecture.
- Prefer existing ViewModel/provider structures and accepted catalog/taxonomy metadata.
- Do not duplicate the #64 30,629 taxonomy into a new runtime data file.
- Do not run broad cleanup commands; `git clean -fdx` / `git clean -fdX` remain forbidden.

## Authority

Detailed scope, invariants, validation, and return contract are owned by live Issue #73. Codex must read the live Issue body and latest comments before implementation.

## Completion / return

Run Release build, all .NET tests, #73 focused tests, and `git diff --check`. If all pass, integrate to `main` without force-push, synchronize this file and `CURRENT_STATE.md` to completed/merged without selecting a successor active DEV issue, and close Issue #73. Keep #70 and #65 as separate lanes.
