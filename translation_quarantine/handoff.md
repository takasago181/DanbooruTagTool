# Issue #36 Handoff

## Status

- Phase: baseline coverage inventory
- Rule: R1
- Branch: `ui-ja/japanese-overlay-quarantine`
- Production modified: NO
- Baseline run: NOT STARTED

## Start point

Use an isolated worktree for this branch and a read-only reference to the real protected-data root.

Before any measurement:
1. Confirm current branch is `ui-ja/japanese-overlay-quarantine`.
2. Confirm #35 worktree/UI files and #32 `validation_quarantine/**` are not being modified.
3. Confirm production Japanese overlay is read-only.
4. Read Issue #36 and `COVERAGE_RULES.md`.

## First required output

Populate `coverage_summary.json` and `missing_candidates.csv` from a reproducible baseline run. Report the exact measurable universe/proxy and limitations.

## Known manual evidence

Real #35 UI screenshot for query `anal` showed many missing Japanese labels including basic recommendation tags such as `1girl`, `penis`, `sex`, `blush`, and `nipples`.

The same screenshot also showed unrelated General results such as `piano` / `analog_clock` / `analogous_colors`; that retrieval defect belongs to #34 search relevance and must not be fixed in this branch.

## Parallel overlap

#32 may inspect some of the same canonical tags in semantic/generation context. #36 must treat those tags only as Japanese display/search coverage records and must not reuse wording as evidence for #32 generation verdicts.
