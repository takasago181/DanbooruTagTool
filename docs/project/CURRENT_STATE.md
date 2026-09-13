# CURRENT STATE

最終更新: 2026-09-13

## Current Stage

**Stage9 completed / beginner-first v1 product direction locked / two active DEV lanes run in parallel: Issue #64 data taxonomy + Issue #66 app/search/UI completion. Issue #66 first UI/interaction baseline and clean WPF/portable architecture baseline are user-accepted; Phase B implementation is ready to start.**

Current active implementation owners:
- **Issue #64** — General 30,629 practical browse taxonomy
- **Issue #66** — beginner-first app completion, bilingual search quality, final v1 acceptance

Issue #66 first implementation authorities:
- UI / interaction: `docs/product/V1_UI_FIRST_IMPLEMENTATION_BASELINE.md`
- architecture / migration / portable distribution: `docs/product/V1_WPF_ARCHITECTURE_BASELINE.md`

Design provenance only:
- `docs/product/V1_UI_DESIGN_DISCUSSION_DRAFT.md`

Retired/superseded:
- Issue #42 — retired/closed; product-scope Gate absorbed into `PRODUCT_GOAL_LOCK.md` + #66 acceptance
- Issue #34 — retired/closed; bilingual-search relevance requirements absorbed into #66

Current Stage10 definition remains Issue #65 / `docs/stages/STAGE_10_LEARNING.md`, but by explicit user priority it is **PAUSED UNTIL THE CURRENT APP REACHES A PRACTICAL v1 BASELINE**.

This file is the routing state. Executable task details belong to the corresponding live GitHub Issue.

## Product goal

Canonical authority:
- `docs/PRODUCT_GOAL_LOCK.md`

v1 core:

`理解 -> 発見 -> 選択 -> 出力`

A beginner with limited English/Danbooru-tag knowledge should be able to:
- paste/read an existing Prompt in Japanese-first form
- preserve unknown/ambiguous raw text rather than silently rewrite it
- search in Japanese, English, or mixed input
- discover Special through deep genre/subgenre browsing
- discover General through shallow practical genre browsing
- manually add/remove/reorder tags
- preview/copy the final canonical-English Prompt

There is no separate product-scope or search-quality Gate after this. Final scope/search acceptance is part of #66.

## Parallel DEV model

### Lane A — Issue #64 General 30,629 taxonomy

#64 solely owns:
- exact production General 30,629 target population
- practical shallow taxonomy classification
- taxonomy sidecar data/audit
- unresolved accounting

#64 does not own UI/search implementation.
#66 must not edit/fork #64 classifications or invent a competing production taxonomy.

Current #64 recovery must use its live Issue latest checkpoint plus:
- `docs/issue64/full_rollout/PROGRESS.md`
- `docs/issue64/full_rollout/MANIFEST.json`

Do not restart already persisted rows.

### Lane B — Issue #66 app/search/UI completion

#66 owns:
- live UI/code/data audit against the current v1 goal
- beginner-first information architecture
- new WPF app foundation
- existing-Prompt understanding/workspace UI
- Japanese/English/mixed bilingual search quality and ranking/noise fixes
- Special deep browse integration from completed #56 assets
- General browse UI shell/provider boundary while waiting for #64
- explicit add/remove/reorder
- canonical-English preview/copy
- removal/de-emphasis of obsolete Stage-first/recommendation-first default UI
- visible-state vs actual-Prompt consistency, including hidden automatic insertion checks
- portable self-contained Windows x64 packaging
- final ADOPT/HOLD/REJECT reconciliation against `PRODUCT_GOAL_LOCK.md`
- focused regression and real Windows acceptance

The first interaction-design discussion is complete enough for implementation. Phase B must use:
- `docs/product/V1_UI_FIRST_IMPLEMENTATION_BASELINE.md`
- `docs/product/V1_WPF_ARCHITECTURE_BASELINE.md`

Do not keep expanding pre-implementation UX scope merely because additional ideas are possible. Build the accepted baseline first; revise after real generation use.

Search requirements inherited from retired #34 include:
- exact canonical / exact English / exact approved Alias / strong Japanese intent outrank incidental fuzzy/substring matches
- Japanese, English and mixed input share one coherent discovery workflow
- relevant Special/General results are not swamped by unrelated General noise
- known regression such as `anal -> piano / analog...` is fixed and tested
- canonical/protected data is not mutated to hide ranking defects

## Architecture / migration decision

The current shipped/dev app is Python + Tkinter and remains as **legacy/reference during the first WPF implementation**.

The new v1 app is a clean C#/.NET/WPF implementation under a new `src/` tree. It must not require Python/Tcl/Tk at runtime.

First-build migration rules:
- do not refactor the existing Python package into the new app
- do not make WPF call Python as a required runtime dependency
- reuse accepted data, taxonomy, identity, search rules, regression evidence and useful behavior
- keep existing `data/` and legacy Python paths in place while #64 and the WPF first build are active
- do not perform a broad legacy/data move before WPF baseline acceptance
- build/read a runtime `catalog.db` from accepted source assets
- keep user-specific state separate in `user.db` / `UserData`

Standard user distribution target:
- Windows x64
- .NET self-contained
- portable folder
- no separate Python installation
- no separate .NET Desktop Runtime installation
- no installer required for ordinary use
- relative/local paths rather than machine-specific absolute paths
- folder copy to another Windows PC/location should remain usable

A single-file executable is not required. One portable folder with EXE/runtime files/catalog/user-data boundaries is preferred.

## Current route

Parallel now:
- **#64** — General 30,629 full taxonomy candidate/audit
- **#66 Phase B** — clean WPF first implementation from the accepted UI + architecture baselines

First #66 build route:
`new WPF solution -> App/Core/Data/Tests boundaries -> catalog import/read -> Prompt workspace -> conservative Prompt import -> Special browse -> bilingual search -> add/edit/reorder -> actual English preview/copy -> autosave/recovery -> General provider boundary -> self-contained portable publish`

After #64 acceptance:
1. #66 consumes accepted General taxonomy sidecar
2. rebuild/refresh product catalog from accepted data
3. #66 reruns search relevance against the final product-facing General population
4. #66 performs final scope reconciliation, cleanup, regression and real Windows UI acceptance
5. verify portable folder copy/start behavior
6. practical v1 baseline
7. resume Stage10 #65 unless the user changes priority

Short form:

`#64 + #66 WPF in parallel -> #66 consumes #64 -> #66 final acceptance -> Windows + portable acceptance -> v1 baseline -> Stage10 resume`

## Workstreams Registry

| TEAM_ID | Status | Scope | Restore anchor |
| --- | --- | --- | --- |
| `GENERAL-DICT:#64` | **ACTIVE DEV / PARALLEL** | 30,629 General practical taxonomy | Issue #64 + latest checkpoint + rollout PROGRESS |
| `V1-APP:#66` | **ACTIVE DEV / PHASE B CLEAN WPF FIRST IMPLEMENTATION / APP+SEARCH+FINAL ACCEPTANCE OWNER** | beginner-first WPF desktop app/search/UI completion | Issue #66 body + latest checkpoint + UI baseline + WPF architecture baseline |
| `STAGE10-LEARNING:#65` | **PAUSED BY USER PRIORITY / RESUME AFTER APP BASELINE** | practical image-generation mastery, NoobAI-first | Issue #65 + `docs/stages/STAGE_10_LEARNING.md` |
| `KNOWLEDGE:#44` | **ONGOING / V1 NON-BLOCKING** | knowledge corpus + Prompt/generation knowledge | Issue #44 + `knowledge/generation-corpus` |
| `MAINT:#24` | OPEN / SAFETY DEBT | local protected data backup/restore | Issue #24 |

Historical only:
- `PRODUCT:#42` — retired/closed; scope authority consolidated into `PRODUCT_GOAL_LOCK.md` + #66
- `UIJA-PARENT:#34` — retired/closed; remaining search-quality requirements consolidated into #66
- `PROMPT:#5` — retired/closed; responsibilities merged into `KNOWLEDGE:#44`
- old Stage10 production A/B definition — historical/testing evidence only

## Completed / frozen foundations

- Stage9 overall Gate — PASS / completed
- automated E2E #28 — PASS / completed
- Special validation/promotion/freeze #32 -> #48 -> #49 -> #43 — completed
- Special Core Dictionary practical taxonomy #56 — completed / Final Audit PASS / PR #62 merged
- Special product-fit full audit + Issue #63 sidecar — completed / merged
- Japanese overlay #36/#55 — completed / production 30,629 entries
- Japanese-first presentation pass #35 — completed
- evaluator/calibration #30 — completed / evidence retained

Do not restart completed #32/#43/#56/#63 work wholesale.

## Known test debt

Issue #63 acceptance review confirmed:
- focused product-fit suite: 122 passed
- full suite on refreshed main base before acceptance: 360 passed / 10 failed
- 9 failures matched the pre-existing task-start baseline
- product-goal wording mismatch in `tests/test_final_spec.py` was synchronized on main in commit `390528bdf884f5394ae9465e0f38f9143b2b1661`

The remaining historical 9 failures are not silently reclassified as PASS.

## v1 ADOPT

- existing Prompt understanding
- Japanese + English + mixed search
- Special deep genre browsing
- General 30,629 shallow practical genre browsing
- manual add/remove/reorder
- final Prompt preview/copy
- local/non-LLM runtime
- clean WPF implementation
- self-contained portable Windows x64 distribution

## v1 HOLD / optional

- co-occurrence suggestions
- usage-count/detail views beyond the accepted first-implementation list/detail presentation
- Semantic Bridge beyond search needs
- Prompt history/favorites
- advanced hints
- direct Forge/ComfyUI adapters
- post-v1 legacy tree cleanup/reorganization

## v1 REJECT from default core

- automatic support insertion
- automatic minimum-sufficient Prompt construction
- automatic conflict removal / Negative generation
- automatic model-family rewrite
- Prompt-only automatic failure diagnosis
- model verification-status UI
- dedicated similar-tag comparison UI
- A/B Prompt manager
- local generation success/failure DB
- evaluator success probability UI
- Raw Lift / ranking methodology main UI
- always-on Generation Profile / knowledge dashboard
- runtime tagger stack requirement
- full 11M-post / ~3GB statistics index requirement
- direct generation integration requirement
- Python/Tk runtime dependency for the new WPF app

Existing assets may remain internally; do not delete evidence merely because a v1 feature is deferred.

## Important current code delta owned by #66

1. Current `danbooru_tag_tool/ui.py` is still Python/Tk Stage7A/Special-first and is now legacy/reference for the new v1 implementation.
2. Existing-Prompt understanding is not the current Python main entry flow.
3. General browsing is not yet a current Python product flow.
4. Old recommendation surfaces (`よく使われる / 珍しい関連 / 意味から補助`) are too prominent for the narrowed v1 goal and are not to be ported by default.
5. `PromptComposer` may allow hidden default support insertion while the visible session reports none; new v1 must make copied Prompt match explicit visible state.
6. Search has known incidental substring/fuzzy false-positive behavior; accepted behavior/regressions should be reimplemented/tested in the new core.
7. General 30,629 browse taxonomy is not yet accepted; #64 owns the data, #66 owns eventual UI consumption.
8. Existing Python/Tk code/data/tests remain available for comparison and evidence during the first WPF build; do not reorganize them first.

## Data boundaries

### Special
- frozen 2,788 identities
- #56 taxonomy sidecar
- #63 product-fit sidecar merged to production

### General
- production Japanese overlay: 30,629 canonical entries
- runtime overlay normally local protected `data/runtime/japanese_overlay.json`
- #64 taxonomy is a separate canonical-tag keyed sidecar
- #66 consumes accepted #64 output rather than creating another taxonomy
- do not expand silently to the full 100k+ Danbooru universe

### New WPF runtime data
- existing accepted CSV/JSON/sidecars remain source assets during migration
- `catalog.db` is rebuildable runtime catalog knowledge
- `user.db` / `UserData` contains user-specific state
- runtime startup does not perform taxonomy/audit rebuilds

### Statistics / generation evidence
- full Stage5 index / co-occurrence / Generation Profile / evaluator evidence remain optional assets
- Prompt/generation knowledge is owned by #44
- these assets are not v1 core runtime dependencies

## Source-of-Truth Rule

Product goal:
- `docs/PRODUCT_GOAL_LOCK.md`

Routing:
- `docs/project/CURRENT_STATE.md`

Active executable work:
- Issue #64 — General taxonomy
- Issue #66 — app/search/UI completion and final acceptance

Issue #66 first implementation UI/interaction baseline:
- `docs/product/V1_UI_FIRST_IMPLEMENTATION_BASELINE.md`

Issue #66 architecture/migration/portable baseline:
- `docs/product/V1_WPF_ARCHITECTURE_BASELINE.md`

Permanent workflow/safety:
- `docs/project/PERMANENT_RULES.md`

Stage10 definition, while paused:
- Issue #65 + `docs/stages/STAGE_10_LEARNING.md`

Issues #42 and #34 are historical only and must not be reactivated as required Gates.

## Next Actions

1. Continue #64 from its latest live checkpoint/PROGRESS without restarting persisted rows.
2. Start #66 Phase B from latest live main using both first-implementation baseline docs as contracts.
3. Create a clean WPF solution under a new `src/` tree; keep current Python/Tk code and existing data paths intact as legacy/reference during the first build.
4. Implement App/Core/Data/Tests boundaries and catalog import/read path without introducing a required Python runtime dependency.
5. Implement Prompt workspace / conservative import / Special browse / bilingual search / explicit add-edit-reorder / actual English preview-copy / autosave-recovery / General provider boundary without waiting for #64 completion.
6. Fix dependency-independent bilingual search relevance/noise inside #66, including representative substring/fuzzy regressions.
7. Publish a `win-x64` self-contained portable folder and verify it does not require Python or separate .NET Desktop Runtime installation.
8. Codex/DEV returns branch / commit / changed files / tests / validation and does not self-merge the broad first implementation.
9. DEV reviews against both accepted baselines, then performs real Windows/generation-workflow use before expanding UX scope.
10. After #64 acceptance, wire accepted General taxonomy into the catalog and rerun product-facing search/browse checks.
11. Perform final scope reconciliation, focused regression, real Windows UI acceptance, and a portable folder-copy launch/state test.
12. Only after WPF baseline acceptance, consider separate cleanup/migration of legacy Python paths.
13. Resume Stage10 #65 after the app baseline unless the user changes priority.
