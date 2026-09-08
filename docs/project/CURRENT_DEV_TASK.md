# CURRENT DEV TASK

最終同期: 2026-09-08

## Mirror Metadata

- Source Issue: #35 `[UI][DEV] Japanese-first desktop UI pass (dictionary frozen)`
- Parent: #34 `[UI-JA][CROSS] Tool UI / Japanese translation quality improvement`
- State: active
- Branch: `ui-ja/issue35-ui-only`
- Purpose: Codexがprivate GitHub Issue APIへ追加認証せず、現行DEV作業内容をrepository内から読むための同期ミラー。

## Scope

**UI / presentation only.**

辞書本体は別の自動改善処理が進行中なので、このIssueでは辞書内容を変更しない。

### Allowed

- `danbooru_tag_tool/ui.py`
- presentation-only helpers/tests required for UI labeling/layout
- UI-facing text/chrome
- bilingual rendering logic using already-loaded Japanese values
- layout / sizing / grouping / state readability

### Forbidden

- `data/**` dictionary edits
- Japanese overlay content edits
- Special2788 content edits
- canonical/alias/semantic/generation-profile data edits
- recommendation/search ranking changes in this pass
- Stage9 composition semantics changes
- protected-data/hash weakening

## Required behavior

### 1. Japanese-first everywhere except final Prompt payload

All user-facing tag/candidate areas must show Japanese plus canonical English where available:

- Special search results
- Other Danbooru tag results
- selected Special
- selected/manual auxiliary tags
- related candidates (`よく使われる` / `珍しい関連`)
- semantic support candidates (`意味から補助`)
- warnings/reasons/labels/status chrome

Display pattern:

`日本語表示  /  canonical_english_tag`

If a canonical has no currently loaded Japanese display value, do not invent a translation. Show:

`日本語未登録  /  canonical_english_tag`

The final Prompt preview / clipboard payload remains canonical Prompt syntax and is not translated.

### 2. Japanese UI chrome

Use Japanese-first wording for visible controls/sections.

- `Prompt preview` -> `完成Prompt`
- window title should not expose `Special-first` as a development label
- retain `Special` as a product/domain term only where useful, with Japanese explanation nearby when needed

### 3. Selected-item state clarity

Make these visually distinguishable without changing data semantics:

- selected Special
- manually added auxiliary tag
- automatically included/core-support auxiliary if currently surfaced by the session

At minimum, row label/prefix/badge must make the source understandable.

### 4. Recommendation readability

Without changing recommendation scoring/ordering:

- tag identity first
- short reason/hint second
- raw statistics tertiary
- `＋追加` remains obvious
- normal Windows desktop scaling should not force the user to decipher dense tiny text

### 5. Layout

Preserve the single-window flow:

`検索 -> Special選択 -> 補助/関連候補 -> 完成Prompt`

Improve spacing, hierarchy, and resizing behavior without splitting into multiple windows.

## Acceptance tests

1. Search result row with Japanese available renders `日本語 / canonical`.
2. General/recommendation/auxiliary row without Japanese renders `日本語未登録 / canonical`, never silent English-only fallback.
3. Selected auxiliary tags always expose canonical English even when Japanese exists.
4. Related and semantic-support candidate rows always expose canonical English.
5. Final Prompt preview remains English/canonical Prompt syntax.
6. No files under `data/**` are modified.
7. No search/recommendation ranking semantics are modified.
8. Existing Stage9C/9D tests and protected-integrity checks continue to pass.
9. Add focused UI/presenter tests for bilingual/fallback rendering rules where practical.
10. After implementation, real Windows Tk screenshot/manual inspection is required; automated E2E alone is not sufficient.

## Completion report required

- remote branch
- commit SHA
- changed files
- focused tests
- regression/full-suite possible range
- confirmation `data/**` unchanged
- real desktop screenshot/manual inspection notes

## Codex Gate

Issue #35 / `CURRENT_STATE.md` / this file are synchronized. Codex may implement **only Issue #35** on branch `ui-ja/issue35-ui-only`.

Do not begin unrelated Stage10 production work from this mirror.
