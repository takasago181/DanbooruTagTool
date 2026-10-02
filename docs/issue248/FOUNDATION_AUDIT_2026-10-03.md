# Issue #248 — Foundation Audit Final Report

Date: 2026-10-03 JST  
Status: **COMPLETE — audit only / implementation STOP**

## 1. Baseline

Gate-open repository main:
`2603f506044574704653f140366bdedadc0ba83b`

Promoted production source:
`b3f48c359a8473c8bbf02347487cba5d8dacf96c`

Production authority:
- `docs/project/LAST_KNOWN_GOOD.json`
- `docs/issue245/PRODUCTION_CHECKPOINT_2026-10-03.json`

Production validation:
- Release: **364 PASS / 4 SKIP / 0 FAIL**
- focused: **112 PASS / 1 SKIP / 0 FAIL**
- real Create -> Forge -> PNG -> Library metadata/model-hash round-trip: **PASS**
- UserData / existing Library / LoRA / catalog / protected semantic authority: preserved
- native pixel capture remains white; final appearance is not pixel-verified, while actual UI operations/status, WPF render/tree and generation workflow passed.

The post-anchor production code delta relevant to architecture is narrow: Forge model-name compatibility handling plus tests. It does not invalidate the pre-LKG Foundation findings.

## 2. Current repository shape

Current main census:
- tracked files: **3,974**
- tracked bytes: **323,765,880**
- docs: **3,516 files / 319,704,386 bytes**
- scripts: **196**
- workflows: **23**
- Core: **16 C# / 0 Issue-named**
- Data: **20 C# / 10 Issue-named**
- App: **33 C# / 0 Issue-named**
- C# tests: **54 / 44 Issue-named**
- remote branches: **209**

Docs are about **98.7%** of the tracked tree by bytes.

Four historical evidence families alone:
- issue70: 2,493 files / 150,609,551 bytes
- issue216: 284 / 65,322,096
- issue180: 156 / 43,186,679
- issue118: 13 / 31,257,865

Combined: **2,946 files / 290,376,191 bytes**.

Historical execution code is similarly concentrated:
- scripts/issue180: **98**
- scripts/issue216: **32**
- tests/issue180: **8**
- tests/issue216: **11**

Conclusion: active product-code debt is not repository-wide. It is concentrated mainly in **Data/catalog authority construction**, while historical bulk dominates the active tree.

## 3. Production authority / ownership findings

### Healthy current owners — KEEP

The following remain well-bounded and production-proven:

- PromptWorkspace / NegativeWorkspace
- UserStateStore / user.db
- GenerationLibraryStore / generation-library.db
- LoraLibraryStore / lora-library.db
- RuntimeCatalogIndex
- current Forge API / Recipe execution boundary
- current SpecialBrowseV2 semantic/index layer
- UnifiedBrowse runtime semantics

User-owned stores already:
- refuse newer schema/payloads;
- back up before migration;
- use bounded migrations;
- remain separate rather than sharing one global DB.

No Foundation redesign is justified for these owners.

### Catalog authority construction — REWRITE

Current catalog build still embeds historical Issue chronology directly in executable code.

`App.xaml.cs` currently sequences:

`AcceptedAssetImporter -> SpecialBrowseV2Overlay -> UnifiedBrowseOverlay -> Issue132RouteOverlay -> Issue118SexualIntentV2Overlay -> Issue199GeneralFacetOverlay -> catalog.db`

The WPF executable therefore owns maintenance/catalog compilation.

`AcceptedAssetImporter` still hard-codes:
- accepted counts;
- hashes;
- historical promotion paths;
- Issue-named authority paths;
- production Special membership through `special2788_generation_profile.csv`.

Current Data code still contains **10 Issue-named C# owners**.

Current accepted inputs include historical paths such as:
- docs/issue56
- docs/issue64
- docs/issue70
- docs/issue96
- docs/issue107
- docs/issue118
- docs/issue179
- docs/issue216
- docs/issue223

This is the strongest confirmed Foundation debt.

Target property:
> a newly accepted semantic snapshot using the same schema should normally be promotable by changing authority/manifest inputs and running a maintenance compiler, without editing C# merely for Issue names, hashes, counts or promotion chronology.

Exact implementation shape is intentionally left to Codex.

## 4. Browse / adult-hard-niche protection

Adult/sexual/fetish/hard-niche discovery is a first-class product pressure.

The current SpecialBrowseV2 layer must remain protected.

Important finding:
- the old **Special-only facet ViewModel state** still exists;
- `SpecialKindOptions / SpecialBodyOptions / SpecialThemeOptions`
- `ToggleSpecialFacet / UndoSpecialFacet / ClearSpecialFacets`
- `specialFilter` + history

but **all 11 current XAML files contain zero bindings to these properties/commands**, and current `RefreshResults()` does not apply `specialFilter`.

Current discovery instead flows through Unified Browse state.

Disposition:
- old Special-only **UI state: DELETE**
- SpecialBrowseV2 **semantic/index data: KEEP**
- adult deep-discovery routes and stable Special IDs: protected parity requirement

This cleanup must not be confused with removing Special semantics.

## 5. App coupling

### CreateViewModel -> MainViewModel

Confirmed coupling remains:
- shared Positive/Negative
- Forge
- Presets
- status/navigation/editability

There is no duplicate editable P/N state.

Disposition: **KEEP now / WRAP only at a real feature seam**.

Reason:
- the dependency is broad, but current production behavior is coherent;
- introducing interfaces/services solely to make the graph look cleaner would be overengineering;
- GenerationRecipe/Model Profile/lineage work may later expose a natural smaller boundary.

Do not make this a mandatory Foundation rewrite.

### CatalogEntry

CatalogEntry currently carries identity/search, browse, HOME/group, unified facets and sexual-intent projection data.

Disposition: **KEEP / WRAP later if a real seam appears**.

Do not split it merely because it is broad. A compiler cutover should first remove historical build ownership; runtime data-shape splitting can wait for measured feature pressure.

## 6. GitHub / automation findings

Two completed Issue70 workflows remain especially problematic:

- `.github/workflows/issue70_build_compact_shards.yml`
- `.github/workflows/issue70_publish_local_batch.yml`

Both:
- trigger from main;
- have `contents: write`;
- explicitly run `git push origin HEAD:main`.

Disposition: **ARCHIVE/DISABLE — P0 hygiene**.

Other completed Issue workflows may be archived later, but mass workflow deletion is not required before dependency review.

Remote branches increased from the pre-LKG 206 to **209**.

Disposition: classify/cleanup later; not a product blocker.

## 7. Historical evidence / scripts

The active tree is dominated by historical research/evidence, but deleting it before the catalog authority cutover would be backwards.

Disposition:
- accepted/provenance evidence: **ARCHIVE, not destroy**
- issue180/216 one-off scripts: **ARCHIVE after dependency confirmation**
- Issue-named regression tests: **KEEP until equivalent semantic protection exists**

After the semantic compiler no longer depends on Issue-era paths, move cold historical evidence out of the normal active tree/search surface while keeping a clear recovery locator.

No Git history rewrite is justified.

## 8. External reuse

#256 remains a reuse input, not a Foundation feature list.

Foundation should not rebuild commodity functionality merely to own it, but no external adoption is currently required for the Foundation core.

Current guidance:
- metadata parsers may later wrap/borrow `sd-parsers` for ComfyUI coverage;
- autocomplete/library UX may borrow existing OSS patterns;
- current Prompt, Library, LoRA, search and safe image-envelope ownership remain DTT-native unless a concrete replacement proves better.

No future feature should be pulled into Foundation just to adopt a dependency.

## 9. Performance / Artist projection

Current catalog:
- total: **124,895**
- Artist: **48,313**

Artist is intentionally hidden from ordinary UI/search surfaces.

Pre-LKG disposition was “needs runtime measurement”.

Final #248 disposition: **KEEP for now; no optimization work selected**.

Reason:
- no current performance regression is blocking the user;
- production generation/search/UI gates pass;
- excluding Artist would change build/runtime projection for an unproven benefit;
- #248 only measures performance where the result changes a Foundation decision.

If startup/search memory becomes a real issue, benchmark a throwaway Artist-excluded projection then. Do not create #254 work now.

The same applies to category-target broad-search-then-filter: keep until measured evidence shows a problem.

## 10. Distribution/personal-use overhead

Current product is a private single-user workstation tool.

Final disposition:
- second-PC validation as universal gate: **DELETE**
- arbitrary folder-copy portability gate: **DELETE**
- single-file/no-PDB/no-DLL package shape as permanent requirement: **DELETE**
- machine-independent path as universal requirement: **DELETE**
- universal offline operation: **DELETE**
- PR/reviewer ceremony for every trivial edit: **DELETE**
- formal license/provenance audit for every private experiment: **DELETE**

Keep:
- actual workstation startup/workflow validation;
- UserData protection;
- rollback/recovery;
- known source/runtime provenance;
- relevant regression tests;
- credentials out of Git.

The existing conservative runtime pipeline may stay until replaced; its packaging details are no longer product invariants.

## 11. Final disposition table

| Candidate | Status | Disposition | Foundation priority |
|---|---|---|---|
| Prompt / Negative workspace ownership | CONFIRMED healthy | KEEP | none |
| UserStateStore | CONFIRMED healthy + live migration PASS | KEEP | none |
| Generation Library store | CONFIRMED healthy + production round-trip PASS | KEEP | none |
| LoRA Library store | CONFIRMED healthy | KEEP | none |
| RuntimeCatalogIndex | CONFIRMED healthy | KEEP | none |
| SpecialBrowseV2 semantics | CONFIRMED critical | KEEP | protected |
| Old Special-only facet VM state | CONFIRMED unreachable from XAML/current results | DELETE | small cleanup |
| AcceptedAssetImporter / Issue build chronology | CONFIRMED debt | REWRITE | **mandatory** |
| Issue-named Data importers | CONFIRMED debt | ARCHIVE after cutover | **mandatory with compiler cutover** |
| WPF-owned catalog build | CONFIRMED debt | REWRITE / move to maintenance boundary | **mandatory** |
| special2788 profile as membership/build coupling | CONFIRMED debt | WRAP/REWRITE within authority contract | **mandatory within cutover** |
| Browse v1/v2/Unified build adapters | CONFIRMED historical chain | REWRITE only at compiler boundary; runtime semantics KEEP | selected with cutover |
| CatalogEntry broad projection | CONFIRMED but not harmful enough | KEEP / later WRAP | defer |
| CreateViewModel -> MainViewModel | CONFIRMED coupling | KEEP / later WRAP | defer |
| semantic_bridge_v1 | no current build dependency observed | ARCHIVE after dependency sweep | low |
| Issue70 write-to-main workflows | CONFIRMED active risk | ARCHIVE/DISABLE | **P0** |
| issue180/216 one-off scripts | CONFIRMED cold historical tooling | ARCHIVE after dependency sweep | selected in hygiene batch |
| large historical evidence families | CONFIRMED active-tree bulk | ARCHIVE/separate after cutover | selected in hygiene batch |
| 209 remote branches | CONFIRMED clutter | classify / archive merged/superseded | optional hygiene |
| Artist runtime population | no measured user problem | KEEP | skip performance project |
| category-target search implementation | no measured user problem | KEEP | skip performance project |
| portable/distribution gates | no longer match product | DELETE as universal requirements | policy already corrected |
| Git history rewrite | no measured value | KEEP history | **SKIP** |

## 12. Smallest recommended Foundation implementation set

Do **not** execute #249–#255 as seven separate projects.

### P0 micro-fix
Disable/archive the two Issue70 workflows that still write directly to main.

### Foundation Batch A — Semantic Authority + Catalog Compiler Cutover
Combine the useful scope of:
- #249 Semantic Data Authority v2
- narrow parts of #253 Core/Data/App architecture renewal

Required outcome:
- accepted semantic inputs have current semantic ownership rather than Issue chronology;
- catalog compilation is outside normal WPF startup ownership;
- compiler/build authority comes from explicit accepted inputs/manifest/schema;
- current 124,895-row production semantics are parity-protected;
- stable Special IDs, deep adult/fetish discovery, SexualIntent, Unified routes/facets, HOME/groups and reviewed quality projections remain equivalent;
- Issue-named C# importers cease to own the production build after cutover.

Also remove the dead Special-only facet VM state when parity confirms Unified owns the current UI.

### Foundation Batch B — Active-tree Hygiene / Archive
Combine the useful scope of:
- #250 Research/Evidence separation
- #251 toolchain/scripts consolidation
- #252 GitHub/branch/workflow hygiene

Only after Batch A removes production dependencies:
- archive cold Issue-era research/evidence from the active main tree/search surface;
- archive one-off issue180/216 scripts;
- retain only maintenance tooling with a current reusable purpose;
- archive/disable obsolete completed Issue workflows;
- classify and remove clearly merged/superseded branches;
- keep provenance/recovery locators.

Do not rewrite Git history.

## 13. Children explicitly skipped/deferred

### #253 broad architecture renewal
**SHRINK**. Only catalog-build ownership and dead-state cleanup belong in Foundation. No broad Core/App rewrite.

### #254 performance/storage optimization
**SKIP for now**. No decision-relevant performance problem is established.

### #255 history compaction
**SKIP**. No history rewrite.

## 14. Post-Foundation enablement

The selected cutover should make later work easier without pre-implementing it:
- Japanese intent bridge/autocomplete can consume stable semantic authority;
- metadata adapter/ComfyUI work can remain an adapter;
- Recipe v2 / Model Profile / lineage can use current stores without inheriting Issue-era catalog build ownership;
- adult/hard-niche discovery remains a protected product capability rather than becoming generic tag search.

## 15. STOP

#248 audit is complete.

No #249–#255 implementation was started in this audit.

Next action requires review/approval of the two-batch Foundation recommendation above.
