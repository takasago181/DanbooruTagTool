# Issue #199 implementation handoff

## Authority and branch

- Live main at preflight: `807f33909aeb4203979e95b0d7d9f6e34856a246`
- Implementation branch: `dev/unified-general-facets`
- Frozen #132 read-only provenance: `de450958eb598a2c7c3a34b112f139dfba617c6e`
- No #132 history was merged, cherry-picked, or used as the branch base.

## Deterministic extraction and eligibility

`scripts/issue199/rebuild_facet_candidates.py` extracts only `GENERAL_ONLY` identities and the frozen `missing_body_sites` / `missing_themes` from the #132 reconciliation ledger. It verifies the ledger and semantic-ledger blob hashes, verifies every facet against the existing #76 vocabulary, confirms the corresponding frozen semantic row names each facet, and accepts only finalized `CHECKED` / `RESEARCHED` rows.

| Stage | Identities | Assignments |
|---|---:|---:|
| Frozen extraction | 359 | 370 |
| Live-main eligible before focused semantic QA | 353 | 364 |
| Shipped static asset | 346 | 355 |

Frozen assignment counts: BODY 257, THEME 113. The extraction reproduced all facet counts recorded by Issue #132. The production asset is sorted and contains no duplicate identity/axis/facet rows.

Six live-ineligible assignments were excluded because their General rows are not both `BrowseClassification == Proposed` and `CanBrowse == true`: `heart-shaped_boob_challenge`, `tawawa_challenge`, `kanchou`, `instance_domination`, `leather_daddy`, and `slave_gear_(tsmg_nao!)`.

Focused QA excluded nine mismatched assignments: `forked_hair`, `perineum_peek`, `torn_bike_shorts` from BREAST_NIPPLE; `bruise_on_leg` from BUTTOCK_ANAL; `covered_navel` from FEMALE_GENITAL; `large_pectorals` from MALE_GENITAL; `shark_fin` from MOUTH_ORAL; `implied_cannibalism` from BDSM_RESTRAINT; and `swaddled` from REPRO_PREGNANCY_LACTATION. Reasons are recorded per row in `candidate_disposition_v1.csv`. No unresolved row was force-added.

Shipped assignments by facet:

| Axis / facet | Assignments |
|---|---:|
| BODY / BREAST_NIPPLE | 72 |
| BODY / BUTTOCK_ANAL | 30 |
| BODY / FEMALE_GENITAL | 10 |
| BODY / MALE_GENITAL | 19 |
| BODY / MOUTH_ORAL | 116 |
| THEME / BDSM_RESTRAINT | 20 |
| THEME / INJURY_R18G | 82 |
| THEME / REPRO_PREGNANCY_LACTATION | 6 |

## Implementation

- Added one embedded static General facet CSV with 346 identities / 355 assignments.
- Added nullable `CatalogEntry.UnifiedBrowseFacets`; null is omitted from JSON, so unaffected catalog rows do not grow.
- Added an explicit catalog-build overlay after the accepted #118 intent bake. It validates exact canonical identity resolution, General-only membership, existing browse authority, existing facet absence, unique rows, and existing #76 facet IDs.
- `UnifiedBrowseIndex` unions the pre-baked metadata only for its existing directly browseable General identities. Special metadata, routes, #118 intent, query ranking, prompt output, and UI controls retain their existing owners and behavior.
- No visible UI redesign was needed.
- Updated the production `--build-catalog` path and the #132 rebuild/regression harness to run the #199 bake. Added #118 staging assertions for the new metadata.

## Validation

- Release solution build: passed, 0 warnings / 0 errors.
- Full Release tests: 217 passed, 17 skipped, 0 failed. Skips are existing opt-in protected-data/production tests plus the dedicated performance test when its two isolated catalog paths are absent.
- Focused #199 functional tests: 5 passed. They cover frozen extraction and exclusions, deterministic asset/IDs, current-index browse, Special behavior, deduplication, Japanese/English/mixed search with facets, both #118 content filters, neutral/deep-only browse, Prompt output, JSON compatibility, and persisted UI body/theme filters.
- Dedicated isolated performance gate: passed over three alternating baseline/candidate runs per side. See `performance_gate_report.json`.
- Protected ordinary-catalog staging validation: passed (1 test); production full-catalog population and source-integrity validation: passed (1 test), including the new repo-relative asset provenance path.
- Issue #132 production-gate harness Release build: passed, 0 warnings / 0 errors.
- Full catalog build from live-main and candidate source, using the same protected inputs, succeeded. Candidate catalog: 124,895 entries; import report records 346 identities / 355 assignments (BODY 247, THEME 108).
- Catalog comparison: after removing the new facet property, all 124,895 serialized rows are identical. `UnifiedBrowseRouteIds`, #118 sexual-intent fields, and all Special Browse V2 classifications are identical. This preserves all existing #132 route additions and changes no non-facet catalog metadata. See `catalog_diff_validation.json`.
- UserData and `C:\Codex\DanbooruTagTool-App` were not modified. Production apply was not performed.

## Isolated performance comparison

Fresh Release catalogs were built from live main and this branch using the same protected source inputs. Both catalog files were warmed in the OS file cache before timed load measurements; baseline/candidate order was alternated. Full-catalog build timings are medians of two explicit `--build-catalog` process runs per side, with the order reversed for the second pair.

| Metric | Live-main baseline | Candidate | Delta |
|---|---:|---:|---:|
| Full catalog build median (two alternating-order runs) | 7,287.3 ms | 8,213.8 ms | +926.5 ms |
| catalog.db size | 131,063,808 bytes | 131,072,000 bytes | +8,192 bytes |
| Catalog open/load median | 1,224.4 ms | 1,252.4 ms | +28.0 ms |
| UnifiedBrowseIndex build median | 92.6 ms | 92.0 ms | -0.6 ms |
| Index allocated bytes | 78,258,136 | 78,308,680 | +50,544 |
| Index retained bytes | 22,371,248 | 22,410,560 | +39,312 |
| Combined retained managed memory | 199,856,784 bytes | 199,935,856 bytes | +79,072 bytes |

Search medians (English / Japanese / mixed) were 59.0 / 40.4 / 59.7 ms baseline and 57.8 / 39.2 / 60.3 ms candidate. `FilterSearchHits` alone, over precomputed hits, was 0.0144 / 0.0158 ms. Browse medians for neutral, large route, body, theme, Sexual+body/theme, and GeneralPurpose+body/theme were 0.884 / 0.584 / 0.779 / 1.073 / 0.783 / 0.775 ms baseline and 0.924 / 0.595 / 0.762 / 1.060 / 0.737 / 0.776 ms candidate. All passed the Issue #199 / #132 regression thresholds. The retained-memory increase was below 1 MB. Full catalog build wall time increased by 926.5 ms (12.7%) in this two-run comparison; no catalog-build time threshold is specified by the Issue, and the query, browse, and memory gates all passed.

## Protected data, residuals, and next gate

- Canonical identities and protected source inputs were read-only; no protected files were changed or committed.
- No unresolved semantic holds remain in the shipped asset. The 15 exclusions are documented above and in the row-level disposition CSV.
- No UI validation or runtime promotion was needed because the existing controls and UI code are unchanged.
- Stop point: implementation branch is ready for independent DEV/AUDIT review. Do not merge or production-apply in this handoff.
