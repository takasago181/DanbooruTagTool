# CURRENT DEV TASK — ISSUE #77 PROMPT OUTPUT PROFILES (COMPLETED / MERGED)

最終同期: 2026-09-15

## Completion

- **Issue #77 is completed and integrated into `main` at `60b15d8fef877c70eac5e4f0f5d67ebd358904d7`.**
- Feature branch: `codex/issue77-prompt-output-profiles`.
- Activation baseline: `da3726f966e88876d101d9c23086cf8e44550574`.
- Integration: live main was unchanged after implementation, so `main` advanced by fast-forward; no force push.
- Issue #77 was user-approved through main integration and closed after post-merge validation.

## Delivered scope

- Added generic profile selector labels `生成向け` and `原形優先` near the common one-click operations.
- Persisted the selected profile through the existing `UiState` / `UserData/user.db` boundary; old state defaults to `原形優先`.
- Kept the internal `PromptWorkspace` canonical serialization, item identity, order, duplicate/raw/LoRA/BREAK/weight behavior unchanged.
- `生成向け` transforms recognized canonical Normal/Weighted tag cores only: `_` to spaces, literal parentheses to escaped `\\(` / `\\)`, and preserves weighted numeric text/wrappers and surrounding whitespace.
- Raw, unresolved, LoRA, BREAK, and unsupported syntax remain unchanged.
- Import tries the existing exact canonical/English/alias resolver first, then only for unresolved tokens tries escaped-parenthesis removal and a space-to-underscore lookup candidate; non-unique or non-matching candidates remain raw with their original surface.
- English preview and one-click copy both use the selected profile output.
- Direct English edit uses the same tolerant parser.

## Validation

- Release build: PASS, 0 warnings / 0 errors.
- All .NET tests: PASS, **92 passed / 5 skipped / 97 total**.
- Issue #77 focused tests: PASS, **9 passed**.
- #72/#73/#74/#75 regression tests: PASS, **20 total / 19 passed / 1 existing production skip**.
- `git diff --check`: PASS.
- Windows launch: PASS. Existing root shortcut launched `DanbooruTagTool v1` from `artifacts/current/DanbooruTagTool.exe`; the fixed local catalog and UserData were retained.

## Repository safety

- Only existing `src/...` and project management docs were changed.
- No #70 translation data, canonical/protected data, taxonomy, legacy data path, or new top-level/artifact folder was changed.
- No successor Active DEV issue is selected. #70 and #65 remain separate lanes.
