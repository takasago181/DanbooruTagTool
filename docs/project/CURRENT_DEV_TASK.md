# CURRENT DEV TASK — ISSUE #75 WQHD VISUAL POLISH (ACTIVE)

最終同期: 2026-09-15

## Routing status

- **Issue #75 is the active DEV implementation lane** — `[DEV][POST-V1] WQHD visual polish pass`.
- Activation authority: live Issue #75 comment **`5674584468`**.
- Working branch: `codex/issue75-wqhd-visual-polish`.
- Creation-time live main: `28fdbe4ff47d2c22ba1e6e4b876cd98b79cb4cbb`.
- Issue #74 is completed and integrated into `main`; its WQHD two-column layout and maximized launch baseline remain intact.
- Issue #73 safe `＋ / ✓` toggle and Issue #72 Prompt category view remain accepted regression invariants.
- Issue #70 translation/data work remains separate. #75 must not modify #70 outputs, canonical/protected data, or taxonomy.
- No main merge or Issue close is authorized by this task; return to DEV visual review first.

## Task summary

Apply one compact, coherent light-theme visual language across the accepted WQHD UI:

1. Strengthen Prompt chip/card separation in dictionary Current Prompt, Prompt Edit ordered view, and category view while preserving selected/matched/raw states and item-level delete clarity.
2. Improve hierarchy between app background, panels, work surfaces, selected dictionary cards, and the simultaneous Tag Details/Current Prompt sections.
3. Make Japanese labels primary, canonical English muted/smaller, and metadata/helper text secondary.
4. Clarify left navigation parent/child hierarchy and selected category state.
5. Clarify common-action priority while preserving all existing commands and semantics.

Do not change Prompt semantics, serialization, copied-English invariant, search order/ranking, taxonomy, translations, canonical data, or #72/#73/#74 behavior. Do not add heavy shadows, gradients, icon/font dependencies, or large cards.

## Repository hygiene

- No new top-level folders, parallel WPF app, prototype/temp/tmp/output/build directories, or versioned artifact/screenshot folders.
- Keep changes in existing `src/...` and existing project docs/tests only; avoid new source files unless clearly justified.
- Do not run `git clean -fdx` or `git clean -fdX`.

## Completion / return

- Run Release build, all .NET tests, applicable focused regression tests, and `git diff --check`.
- Launch the existing WPF runtime and attempt WQHD/maximized inspection of Dictionary, Prompt Edit ordered view, and Prompt Edit category view; return updated screenshots if the Windows bridge permits.
- Return `READY_FOR_VISUAL_REVIEW`; do not merge to main or close Issue #75 in this task.
