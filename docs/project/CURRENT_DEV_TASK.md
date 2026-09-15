# CURRENT DEV TASK — ISSUE #79 GENERATION PRESETS

最終同期: 2026-09-15

## Routing status

- **Issue #79 — Generation presets (reusable Positive sets + Negative copy) is ACTIVE DEV.**
- Activation authority: live Issue #79 and comment `5674972661`.
- Branch: `codex/issue79-generation-presets`.
- Activation baseline: `a8c1411eb1c89bff8b0f32ff66c6413dce6fe2b5`.
- First pass stops at `READY_FOR_DEV_REVIEW`; do not merge to main or close #79.
- #70 and #76 remain separate lanes; no taxonomy or translation data changes.

## Scope

Add a compact `生成プリセット` dialog using the existing WPF App/Core/Data/Tests structure. A user-local preset contains a stable id, name, description, canonical/internal-safe Positive Prompt, and byte-for-byte opaque Negative Prompt. Provide direct `Positive追加` and `Negativeコピー`, plus new/edit/capture-from-current/save/delete controls.

## Safety boundaries

- Reuse the existing `UserData/user.db` payload/versioning boundary; do not create a second user-data store.
- Positive uses the existing conservative Prompt parser and canonicalizes only recognized tag cores on save; preserve order, weight, raw/unresolved, LoRA, BREAK, and control surfaces.
- Applying Positive appends in preset order, skips only recognized canonical identities already present, and does not rewrite existing items. One apply is one Undo action.
- Negative is never parsed, normalized, profile-formatted, reordered, or deduplicated.
- Preserve #72/#73/#74/#75/#77 behavior, including output-profile preview/copy equality.
- No new top-level folders, artifacts, WPF copy, #70/#76 data, taxonomy, canonical data, or protected data changes.

## Required validation

- Release build.
- All .NET tests.
- Focused #79 preset/persistence/apply/Negative tests.
- #72/#73/#74/#75/#77 regression tests.
- `git diff --check`.
- Practical Windows/WQHD launch and dialog check if available.

## Completion

Commit and push the feature branch with a `READY_FOR_DEV_REVIEW` report. Main integration and Issue close require a later explicit acceptance.
