# Issue #210 pipeline authority map

Inventory from live main `e4c758d6ff4a52b4defefd25c8f3334ff0c6ff1d`.

| Path | Classification | Current role / disposition |
| --- | --- | --- |
| `src/DanbooruTagTool.App/App.xaml.cs` | CANONICAL | Explicit full catalog build; writes database and source import report. |
| `src/DanbooruTagTool.Data/Storage.cs` | CANONICAL | Runtime catalog reader, SQLite schema, and isolated UserState store. |
| `src/DanbooruTagTool.Data/AcceptedAssetImporter.cs` | CANONICAL | Accepted source set and ordinary/Special importer contract. |
| `src/DanbooruTagTool.Data/SpecialBrowseV2Overlay.cs` | CANONICAL | #76 Special browse semantics. |
| `src/DanbooruTagTool.Data/Issue118SexualIntentV2Overlay.cs` | CANONICAL | #118 intent semantics and accepted source inputs. |
| `src/DanbooruTagTool.Data/Issue132RouteOverlay.cs` | CANONICAL | #132 route overlay. |
| `src/DanbooruTagTool.Data/Issue199GeneralFacetOverlay.cs` | CANONICAL | #199 General body/theme facets. |
| `src/DanbooruTagTool.Data/Issue70CatalogOverlayImporter.cs` | CANONICAL | Character/Copyright/Artist source loader and fixed source authority. |
| `src/DanbooruTagTool.Tests/ProductionTests.cs` | SPECIALIZED | Opt-in full production population, search, and source-integrity contract. Its ordinary-only test is a separate profile test. |
| `src/DanbooruTagTool.Tests/Issue76MainUiIntegrationTests.cs` | TEST_ONLY | #76 reader/UI production integration coverage. |
| `src/DanbooruTagTool.Tests/Issue118*Tests.cs` | TEST_ONLY | #118 source, runtime identity, and intent coverage; `Issue118OrdinaryStagingValidationTests.cs` is ordinary staging only. |
| `src/DanbooruTagTool.Tests/Issue132ProductionDeltaTests.cs` | TEST_ONLY | #132 route regression coverage. |
| `src/DanbooruTagTool.Tests/Issue199*Tests.cs` | TEST_ONLY | #199 facets/performance gates. |
| `src/DanbooruTagTool.Tests/Issue201PracticalScenarioTests.cs` | TEST_ONLY | #201 practical discovery scenarios. |
| `src/DanbooruTagTool.Tests/Issue204UnifiedRefreshTests.cs` | TEST_ONLY | #204 UI refresh regression. |
| `src/DanbooruTagTool.Tests/TechnicalFixTests.cs`, `UxRefinementTests.cs`, `Issue97SpecialAuditTests.cs`, `Issue117NoSafeSearchRegressionTests.cs` | TEST_ONLY | Existing production/source/category/search/identity regression owners. |
| `scripts/maintenance/issue97_special_audit.py` | SPECIALIZED | Read-only historical Special expansion audit; not a full-catalog default validator. |
| `scripts/issue132/production_gate/*` | SPECIALIZED | #132 evidence gate, separate from the live catalog structural pipeline. |
| `scripts/issue107/apply_production_promotion.py`, `materialize_promotion_preflight.py` | SPECIALIZED | Historical #107 taxonomy promotion authority, not runtime publishing or runtime apply. |
| `scripts/performance/run_targeted_smoke.ps1`, `run_leak_cycles.ps1` | SPECIALIZED | Explicit isolated performance harnesses; not canonical release or production promotion. Their seed input is outside this pipeline. |
| `scripts/maintenance/check_local_health.ps1` | SPECIALIZED | Developer diagnostics now call the separate catalog, UserData, and manifest validators. |
| `scripts/maintenance/catalog_health.py` | LEGACY_TO_REPLACE | Mixed read-only catalog + UserData checker with 33,688 ordinary-profile and #76 snapshot assumptions. It is not a valid full-runtime default. Retain only as compatibility CLI delegating to separate validators. |
| `scripts/maintenance/catalog_structural_health.py` | CANONICAL | New generic structural validator; observes population rather than pinning snapshot counts. |
| `scripts/maintenance/userdata_health.py` | CANONICAL | New read-only UserData SQLite health/inventory checker, independent of catalog health. |
| `scripts/maintenance/validate_runtime_manifest.ps1` | CANONICAL | New manifest hash/metadata validation. |
| `scripts/maintenance/check_runtime_shape.ps1` | CANONICAL | New non-mutating candidate/installed runtime shape guard. |
| `scripts/maintenance/publish_portable_runtime.ps1` | CANONICAL | Sole publish implementation; explicit source HEAD, single-file, disposable UserData only. |
| `src/publish-portable.ps1` | WRAPPER | Delegates to canonical publish script; no independent MSBuild flags. |
| `src/DanbooruTagTool.App/Properties/PublishProfiles/Portable.pubxml` | SPECIALIZED | IDE profile aligned with canonical single-file defaults. |
| `scripts/maintenance/promote_portable_runtime.ps1` | CANONICAL | New bounded file-list promotion with runtime-only rollback and UserData byte-identity checks. |
| `scripts/maintenance/refresh_current_runtime.ps1` | LEGACY_TO_REPLACE | Old `artifacts/current` mutator copies UserData and prunes outputs; retired from production promotion use, left in place as historical script. |
| `scripts/maintenance/check_local_health.ps1` | SPECIALIZED | Developer diagnostic; migrated to separated health and manifest validators. |
| `src/README.md` | SPECIALIZED | Portable publish usage; points to wrapper and canonical safety contract. |
| `scripts/maintenance/test_catalog_structural_health.py` | TEST_ONLY | Structural fixture and drift regression suite. |
| `scripts/maintenance/test_runtime_pipeline.py` | TEST_ONLY | Manifest and publish/shape contract regression suite. |
| PR #205 `scripts/maintenance/check_runtime_shape.ps1` | PROVENANCE_ONLY | Reusable shape-check idea; reimplemented with strict candidate/installed modes and no mutation. |
| PR #205 `scripts/maintenance/check_workspace_size.ps1` | SPECIALIZED | Workspace inventory concept; unrelated to catalog/publish/runtime authority and preserved only in PR history. |
| PR #205 `scripts/maintenance/check_workspace_size.ps1` | SPECIALIZED | Workspace diagnostic idea retained as PR history; unrelated to runtime authority and no new duplicate script is required here. |
| PR #205 `src/publish-portable.ps1` and publish-profile changes | PROVENANCE_ONLY | Single-file intent reused; superseded by the sole canonical entry point and thin wrapper. |

## Conflicting assumptions found

- The old `catalog_health.py` accepts only ordinary-profile 33,688 rows, omits full Character/Copyright/Artist populations, and hard-codes #76 status counts. The installed full runtime catalog has a different contract.
- Full catalog semantic/source authority already belongs to the .NET importer and opt-in `ProductionTests` plus issue-specific tests; it must not be duplicated in Python.
- The old canonical publisher required and copied real `UserDataPath`; the wrapper and `Portable.pubxml` independently selected loose DLL output.
- The old manifest v1 injected fixed sexual/identity population numbers and mixed checker metadata with an ordinary-only contract.
- `refresh_current_runtime.ps1` copies protected UserData into an isolated runtime and removes files from `artifacts/current`; it is not safe as production apply authority.
- No current-main runtime-shape validator existed. PR #205 proposed one but removed health validation without replacing semantic/source-integrity authority.

No protected source, catalog, UserData, or historical evidence was modified to create this inventory.
