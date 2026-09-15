# CURRENT DEV TASK — ISSUE #77 PROMPT OUTPUT PROFILES

最終同期: 2026-09-15

## Routing status

- **Issue #77 — Prompt output profile switch + tolerant one-click import is ACTIVE DEV.**
- Activation authority: live Issue #77 and comment `5674780449`.
- Branch: `codex/issue77-prompt-output-profiles`.
- Activation baseline: `da3726f966e88876d101d9c23086cf8e44550574`.
- User approved implementation through main integration if all validation passes.
- No successor should be selected by Codex after completion; #70 and #65 remain separate lanes.

## Scope

Add the generic user-facing profiles `生成向け` and `原形優先` with persistent selection, one-click copy/import, profile-specific English preview, and conservative recognition of generation-style tokens. Keep canonical/internal Prompt identity, order, duplicates, raw/unresolved, LoRA, BREAK, weights, Undo/Redo, autosave, and accepted #72/#73/#74/#75 behavior intact.

## Safety boundaries

- Do not expose NoobAI, WAI, Danbooru, or implementation-facing profile names in normal UI.
- Do not rewrite arbitrary raw/natural-language text or modify #70 translation data, taxonomy, canonical data, or protected data.
- Work only inside the existing `src/App`, `src/Core`, `src/Data`, and `src/Tests` structure plus this routing document.
- Do not add top-level folders or versioned artifact/screenshot/build directories.

## Required validation

- Release build.
- All .NET tests.
- Focused #77 profile/import tests.
- #72/#73/#74/#75 regression tests.
- `git diff --check`.
- Practical Windows launch/UI check if available.

## Integration gate

If all validation passes, re-fetch live main, reconcile safely without force if main advanced, integrate with fast-forward where possible, push main, sync this document and `CURRENT_STATE.md` to completed/merged, then close Issue #77. Do not select a successor Active DEV lane.
