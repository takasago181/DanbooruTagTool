# Japanese Overlay Translation Quarantine

Issue: #36 `[UI-JA][DATA] Japanese overlay coverage audit + priority expansion (quarantine)`

Branch: `ui-ja/japanese-overlay-quarantine`

## Purpose

Measure Japanese display/search coverage for canonical tags actually surfaced by the tool, then prepare reviewed translation candidates without editing production data.

## Hard boundaries

- Production `data/runtime/japanese_overlay.json` is read-only during baseline and candidate generation.
- Do not edit #32 `validation_quarantine/**`.
- Do not edit #35 UI implementation files.
- Canonical English identity and final Prompt syntax are unchanged.
- Japanese `display` and `search` remain separate concepts.
- Search-ranking/noise fixes are outside this branch.

## Durable outputs

- `COVERAGE_RULES.md` — measurement and prioritization contract
- `coverage_summary.json` — reproducible aggregate coverage numbers
- `missing_candidates.csv` — deterministic missing-translation queue
- `handoff.md` — restart point, evidence, limitations, next action

Protected/raw local datasets must not be copied into this directory or committed to GitHub.
