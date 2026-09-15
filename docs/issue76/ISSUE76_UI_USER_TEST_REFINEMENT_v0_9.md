# Issue #76 UI user-test refinement v0.9

Date: 2026-09-15
Status: user-feedback refinement candidate; not merged to main

## User feedback from integrated MainWindow test

The current MainWindow/card/detail/Prompt layout is preferred over the isolated prototype. Keep that UI and import only the Special v2 browse behavior.

Two concrete usability changes were requested after hands-on testing:

1. `種類から探す` / `部位から探す` / `テーマから探す` contain few enough entries that they should stay expanded while `◆ Special` is open. Only the top `◆ Special` node should be used to open/close the Special browse block.
2. The wide `すべて解除` control in the compact facet bar is too large. Replace it with small right-aligned controls: `1つ戻す` for removing the most recently applied filter condition, and `全解除` for resetting all Special facets.

## Implemented behavior on feature branch

- Current MainWindow, two-column cards, detail pane, Prompt pane, search, sort, presets, Forge integration remain intact.
- Special v2 axis headings are fixed-expanded when the Special root is open and are not treated as browse destinations.
- `1つ戻す` walks facet state backward one applied condition at a time.
- `全解除` clears the facet history and returns to the Special root.
- Existing SearchEngine result order is still intersected, not re-ranked.
- Canonical browse deduplication remains active.

## Validation

Validated on Windows GitHub Actions before recording this note:

- Release build: 0 warnings / 0 errors
- Tests: 125 total / 120 passed / 5 skipped / 0 failed
- New regression coverage includes fixed axis-heading behavior and one-step facet undo.
- `git diff --check`: pass

Validated implementation commit before this note:
`5a0691ceb64f5c626e013cde3287065066feead9`

This remains a user-test candidate. Final production/main implementation remains a separate Codex implementation/review step after user approval.
