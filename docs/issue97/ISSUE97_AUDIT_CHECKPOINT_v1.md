# Issue #97 audit checkpoint v1

## Scope

Issue #97 audits the post-#96 Special population after promotion from 2,788 to 2,983 identities and verifies that accepted Browse v2 production boundaries still hold. This checkpoint is intentionally read-only with respect to production data. It does not modify Issue #70 data/UI, General taxonomy, canonical Special identity, or `UserData/user.db`.

Base restored from live `main` after PR #98:

- main merge: `c383db19bbbe57bc20033b1deb82b9a1a2281984`
- audit branch: `audit/issue97-special-quality-browse-v2`
- Special target: 2,983 identities, IDs `1..2983`
- promotion interval: IDs `2789..2983` (195 rows)

## Evidence hierarchy

This checkpoint distinguishes three levels of evidence rather than treating source inspection as an executed production audit:

1. **GitHub/source invariant confirmed** — current source has an explicit hard-fail or accepted authority proving the condition structurally.
2. **Repository read-only audit implemented** — `scripts/maintenance/issue97_special_audit.py` checks the committed authority/sidecars without modifying them.
3. **Built catalog verification pending local run** — complete Japanese/search/Browse v2/collision verification for all 2,983 requires the protected local production `catalog.db`, which is intentionally not committed to GitHub.

The current execution environment cannot clone GitHub directly and does not contain the protected production catalog, so this checkpoint does **not** claim a local `catalog.db` run that did not occur.

## Phase A status

| Requirement | Current result | Evidence / gate |
|---|---|---|
| accepted 2,983 / IDs 1..2983 | source invariant confirmed; built-catalog run pending | `AcceptedAssetImporter.ExpandedSpecialCount = 2983`; production tests assert 2,983 Special; Issue97 audit requires exact ID set |
| promotion 195 rows / 2789..2983 contiguous | PASS by source invariant | `ValidatePromotion` requires exact contiguous range and count |
| canonical/alias duplicate 0 | #96 promotion gate PASS; stronger built-catalog cross-check pending | Issue97 audit checks promoted surfaces against base 1..2788 and against other promoted rows |
| Japanese display/search 2983/2983 | promoted 195 confirmed; full built-catalog run pending | base Japanese authority is protected/local; Issue97 production test checks every built row |
| Browse v2 2983/2983 | source invariant confirmed; built-catalog run pending | `SpecialBrowseV2Overlay.Load` requires exact IDs 1..2983; `FromCatalog` requires baked classification on all Special rows |
| generation profile 2983/2983 | authority expanded through ID 2983; exact-set audit implemented | Issue97 audit requires exact generation-profile IDs 1..2983 and validates promoted tag/evidence identity |
| product fit 2983/2983 | PASS by importer exact-set invariant | importer requires exact product-fit IDs 1..2983; Issue97 audit independently requires exact set/nonblank verdict |
| no stale live 2788-total assumption | no active total-count defect found in reviewed production path | `BaseSpecialCount = 2788` is an intentional pre-promotion boundary; legacy `special2788` paths are compatibility/authority names, not live cardinality assertions |
| bounded human audit only | PASS in audit design | machine checks emit only detected anomalies as `human_audit_candidates`; no 2,983-row manual rereview |

Important interpretation for duplicate checks: existing Special can legitimately contain ambiguous aliases/identity relationships, and current tests explicitly preserve such behavior. Therefore #97 does not impose a new global “all aliases across 2,983 must be unique” rule. It checks whether the **195 promoted identities introduce collisions against the previous 2,788 population or each other**.

## Phase B status — Browse v2 after expansion

Issue #76 is already completed and merged into production. Its accepted architecture is:

- accepted v2 evidence is consumed only during explicit catalog build;
- `SpecialBrowseV2Overlay.Bake` serializes the accepted classification into `CatalogEntry.SpecialBrowseV2`;
- normal startup uses `SpecialBrowseV2Overlay.FromCatalog` and does not rebuild taxonomy from audit CSVs;
- old Issue #56 evidence remains provenance, not the normal runtime classification engine.

After #96 expansion, current Browse v2 validation expects:

- `AutoCandidate`: 2,745
- `HumanResolved`: 210 (15 existing + 195 promoted)
- `ReferenceOnlyNoDirectBrowse`: 21
- `DeferProductFitReview`: 6
- `OutOfScopeNoBrowse`: 1
- total: 2,983

The promoted 195 rows enter with accepted #96 `kind_id`, `body_site_ids`, and `theme_ids` and `HumanResolved` status. They do not need to be force-routed back through the legacy v1 category remap. For the original 2,788 rows, the accepted #76 v1-to-v2 derivation/patch path remains the build-time source and `Validate` still checks route/status integrity.

Thus the Issue #97 `source_category remap` requirement maps to two separate production paths:

- IDs `1..2788`: accepted #76 v1 source/category -> v2 kind/body/theme mapping and patches;
- IDs `2789..2983`: accepted #96 v2 fields are already explicit and are preserved directly.

No new taxonomy redesign is required in #97 unless the production audit produces a concrete mismatch.

## New regression assets

### `scripts/maintenance/issue97_special_audit.py`

Read-only audit that checks:

- #96 promotion/JA/taxonomy/duplicate authority exact ID sets;
- generation profile exact IDs `1..2983`;
- product-fit exact IDs `1..2983`;
- promoted authority consistency;
- active-code stale literal candidates while allowing the intentional `BaseSpecialCount = 2788` boundary;
- optional built `catalog.db` validation using SQLite read-only/immutable mode;
- full catalog Japanese display/search, ProductFit, Browse v2 route/status, promoted-vs-base surface collision checks;
- never opens `UserData/user.db`.

Repository-only invocation:

```powershell
python scripts/maintenance/issue97_special_audit.py
```

Full production-catalog invocation:

```powershell
python scripts/maintenance/issue97_special_audit.py --catalog .\src\artifacts\current\Data\catalog.db
```

Use the actual current production catalog path if different.

### `Issue97SpecialAuditTests.cs`

Adds an opt-in `[ProductionFact]` contract test for the built catalog. With `DTT_PRODUCTION_CATALOG` set, it verifies:

- exact Special IDs `1..2983`;
- Japanese display/search and ProductFit coverage for every Special row;
- Browse v2 classification on every row;
- status distribution `2745 / 210 / 21 / 6 / 1`;
- browsable/non-browse route consistency;
- exact promoted IDs `2789..2983`, all `HumanResolved`;
- no promoted canonical/alias surface overlaps with base IDs `1..2788` or another promoted identity.

Without `DTT_PRODUCTION_CATALOG`, this production test remains skipped like the repository's existing protected-production tests.

## Validation state

Completed in this lane:

- GitHub live-state/preflight reconstruction: PASS
- Issue #94 -> #96 promotion provenance reconstruction: PASS
- Issue #76 final production Browse v2 architecture reconstruction: PASS
- Python audit script syntax check: PASS before commit
- protected-boundary review: PASS (`#70` untouched, `UserData/user.db` untouched)

Still required before merge/Issue completion:

1. Run repository audit on an actual checkout.
2. Rebuild/use the current post-#96 `catalog.db` if the local catalog predates PR #98.
3. Run `issue97_special_audit.py --catalog ...`.
4. Run Release tests with the production catalog available, including `Issue97SpecialAuditTests`.
5. Human-review only rows emitted as anomalies, if any.
6. If no anomalies remain, record final Phase A/B PASS and then integrate the audit/regression assets.

## Current verdict

`AUDIT_MECHANISM_READY / SOURCE_INVARIANTS_RESTORED / FULL_LOCAL_CATALOG_GATE_PENDING`

Do not merge this branch solely on source inspection. The final #97 verdict should be based on the read-only production-catalog run because the protected base Japanese metadata is intentionally outside GitHub.
