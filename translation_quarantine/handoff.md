# Issue #36 Handoff

## Status

- Phase: Phase 1A full independent revalidation COMPLETE
- Rule: R1
- Branch: `ui-ja/japanese-overlay-quarantine`
- Production modified: NO
- Protected-data run: read-only
- Revalidation gate: PASS_WITH_REVIEW_ROWS

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

Phase 0 remains the fixed baseline. Its protected input hashes and coverage
definitions are unchanged by Phase 1A and this revalidation.

## Phase 1A result

Exactly 100 unique P0 canonicals were selected in the contract order:

1. all documented common recommendation surface rows, in Phase 0 order;
2. all documented rare recommendation surface rows, in Phase 0 order;
3. all semantic-support reachable rows, deduplicated in the Phase 0 queue order;
4. forced screenshot rows `1girl`, `penis`, `sex`, `blush`, `nipples`;
5. P0 high-usage General rows, sorted by protected `post_count` descending and
   canonical ascending tie-break, until the count reached 100.

The last selected canonical is `collarbone`. The candidate wording and QA
ledger are in `phase1a_review.csv`; the reproducible generator is
`phase1a_generate.py`.

- Initial Phase 1A state: `READY_FOR_AUDIT` 92 / `REVIEW` 8
- Proposal source: `EXISTING_SEARCH` 67 / `LOCAL_EXACT` 31 / `GENERATED` 2
- Risk: `HIGH` 50 / `MEDIUM` 6 / `LOW` 44
- Previous self-QA was not accepted as the independent gate.
- #32 label-only overlap in pilot: 8 (`feet`, `footjob`, `handjob`,
  `kneeling`, `on_back`, `penis`, `sitting`, `solo`)
- Existing search terms were retained as evidence; no search term was deleted
  or replaced.
- `piano`, `analog_clock`, `analogous_colors`, and `canal` remain outside the
  pilot as search-ranking examples, not translation candidates.

`REVIEW` means a human wording decision is still required and is not a
production approval. Do not promote these candidates, do not continue to the
remaining 925 P0 rows, and do not modify production data from this branch.

## Independent full revalidation

All 100 existing Phase 1A rows were revalidated independently for semantic
width and UI-JA naturalness. Proposal-source fields were not used as approval
evidence.

- Rows revalidated: 100/100
- Final state: `READY_FOR_AUDIT` 91 / `REVIEW` 9
- Existing 8 `REVIEW` rows preserved; no automatic approval
- New `REVIEW`: `multiple_penetration`
- False approvals found: 7
- Root causes: semantic-width narrowing 3; semantic scope underspecified 1;
  state reduced to substance 1; UI naturalness/state scope 1; community
  shorthand UI naturalness 1
- Corrected: `cuffs`, `straddling`, `lactation`, `vaginal`, `gaping`,
  `medium_breasts`
- Corrected and moved to `REVIEW`: `multiple_penetration`
- Full revalidation result: `PASS_WITH_REVIEW_ROWS`

The detailed before/after audit is in `phase1a_review.csv`; the reproducible
re-audit implementation is `phase1a_reaudit.py`. No production data or
remaining-P0 work was changed.
