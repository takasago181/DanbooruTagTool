# Issue #36 Handoff

## Status

- Phase: baseline coverage inventory COMPLETE
- Rule: R1
- Branch: `ui-ja/japanese-overlay-quarantine`
- Production modified: NO
- Baseline run: COMPLETE (read-only protected-data run)

## Start point

Use an isolated worktree for this branch and a read-only reference to the real protected-data root.

Before any measurement:
1. Confirm current branch is `ui-ja/japanese-overlay-quarantine`.
2. Confirm #35 worktree/UI files and #32 `validation_quarantine/**` are not being modified.
3. Confirm production Japanese overlay is read-only.
4. Read Issue #36 and `COVERAGE_RULES.md`.

## Phase 0 result

`coverage_summary.json` and `missing_candidates.csv` are populated from a reproducible
read-only run. The exact measurable universes, proxies, lane memberships, rates,
ranking separation, #32 overlap, and protected input hashes are recorded in the
JSON artifact.

- Protected root: `C:\Codex\DanbooruTagTool`
- Overlay: display canonical entries `0`; search canonical entries `15,228`
  (`25,140` search terms)
- General runtime/canonical proxy: `30,629`; display Japanese `0/30,629`,
  search Japanese `4,641/30,629`
- Documented recommendation probe `anal AND butt_plug`: base `3,735`, full
  candidate pool `5,918`; common surface `8`, rare surface `5`
- Semantic-support reachable union: `41` canonical candidates
- Deduplicated missing union: `30,629`; queue `P0 1,025 / P1 4,910 / P2 24,694`
- No translation wording was generated; proposal columns remain blank.

The recommendation pool is a documented production parity probe, not an exhaustive
all-Core recommendation universe. General is a runtime/canonical proxy, not an
exhaustive search reachability claim for all raw runtime tags. Lane totals report
display coverage as Japaneseあり/なし and search coverage separately.

## Known manual evidence

Real #35 UI screenshot for query `anal` showed many missing Japanese labels including basic recommendation tags such as `1girl`, `penis`, `sex`, `blush`, and `nipples`.

The same screenshot also showed unrelated General results such as `piano` / `analog_clock` / `analogous_colors`; that retrieval defect belongs to #34 search relevance and must not be fixed in this branch.

## Parallel overlap

#32 may inspect some of the same canonical tags in semantic/generation context. #36 must treat those tags only as Japanese display/search coverage records and must not reuse wording as evidence for #32 generation verdicts.

Phase 0 is complete and must STOP here. Do not generate translation wording or
promote any row to production from this branch.
