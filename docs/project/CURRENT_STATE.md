# CURRENT STATE

最終更新: 2026-09-13

## Current Stage

**Stage9 completed / beginner-first v1 product narrowing active / two DEV lanes now run in parallel: Issue #64 data taxonomy + Issue #66 app/UI completion.**

Issue #63 product-fit verdict sidecar integration is **ACCEPTED / MERGED / CLOSED**.

Current app-completion owner:
- Issue #66 `[V1-APP][UI][PARALLEL-WITH-64] Beginner-first app completion and UI integration`

Current Stage10 definition remains Issue #65 / `docs/stages/STAGE_10_LEARNING.md`, but by explicit user priority on 2026-09-13 it is **PAUSED UNTIL THE CURRENT APP REACHES A PRACTICAL v1 BASELINE**.
The old meaning of Stage10 as broad Special Core Dictionary production A/B validation remains retired. Old A/B/evaluator assets remain historical/testing evidence.

Stage10 is not deleted or redefined again; it is simply lower priority than finishing the app.

This file is the routing state. Task scope/completion/evidence belongs to the corresponding live GitHub Issue.

## Current product direction

Canonical product goal: `docs/PRODUCT_GOAL_LOCK.md`

v1 core:

`理解 -> 発見 -> 選択 -> 出力`

A beginner with limited English/Danbooru-tag knowledge should be able to:
- paste/read an existing Prompt in Japanese-first form
- search in Japanese or English
- discover Special through deep genre/subgenre browsing
- discover General through shallow practical genre browsing
- manually add/remove/reorder tags
- copy the final canonical-English Prompt

Current product-scope owner:
- Issue #42 `[PRODUCT][V1-NARROWING][AFTER-34] Beginner-first product scope and implementation path`

Current implementation owner for the actual desktop app:
- Issue #66

## Current parallel DEV model

### Lane A — Issue #64 General 30,629 taxonomy

Issue #64 remains the sole owner of:
- exact production General 30,629 target population
- practical shallow taxonomy classification
- taxonomy sidecar data/audit
- unresolved accounting

Current full-rollout work is independent of UI implementation.
#66 must not edit or fork #64 classifications.

### Lane B — Issue #66 app/UI completion

Issue #66 may proceed now in parallel with #64 and owns:
- live UI/code audit against the current v1 goal
- beginner-first information architecture
- existing-Prompt understanding/workspace UI
- Japanese/English search interaction using the existing search contract
- Special deep browse integration from completed #56 assets
- General browse UI shell/provider boundary while waiting for #64
- explicit add/remove/reorder
- canonical-English preview/copy
- removal/de-emphasis of obsolete Stage-first/recommendation-first default UI
- visible-state vs actual-Prompt consistency, including hidden automatic insertion checks
- Windows/Tk usability and final app acceptance after dependencies converge

Issue #66 does **not** own:
- #64 taxonomy classification
- #34 search ranking semantics
- #42 final v1 scope-lock decision

## Stage10 learning direction — PAUSED BY PRIORITY

Stage10 remains a **hands-on image-generation skill-acquisition stage**.

Primary learning model:
- **NoobAI XL 1.1 EPS + Forge Neo**

Secondary lanes:
- Anima — relation-heavy / multi-character / tag + natural-language comparison/fallback
- WAI Illustrious v17 — historical/comparison lane
- NoobAI V-Pred — separate advanced comparison profile; never pooled with EPS

Target outcome remains:

`日本語の意図 -> Prompt設計 -> 生成 -> 観察 -> 原因分解 -> 修正 -> 必要ならLoRA/修復/領域制御 -> 仕上げ -> 再現可能な保存`

Curriculum remains 10.0–10.9 in `docs/stages/STAGE_10_LEARNING.md`.

Resume point after app completion:
- **Stage10.0 -> 10.1 with NoobAI XL 1.1 EPS**

Do not spend the current primary work slot on Stage10 while #66 app completion is active unless the user explicitly resumes it.

## Current Core DEV — Issue #64

**Issue #64 — General 30,629 practical browse taxonomy sidecar**

Goal:
- turn the exact production Japanese-overlay population into a shallow, practical Japanese-first browse dictionary
- keep taxonomy separate from canonical identity and `japanese_overlay.json`
- validate the taxonomy against real data before production acceptance

Current continuation is the accepted-pilot full rollout on its live working branch/checkpoints.
Always read Issue #64 latest comment and branch `docs/issue64/full_rollout/PROGRESS.md` before continuing; do not restart completed rows.

Do not implement #34 ranking redesign, #42 scope work, or #66 UI work inside #64.
Do not expand to the full 100k+ Danbooru universe.

## Current V1 App DEV — Issue #66

**Issue #66 — beginner-first app completion / UI integration**

Current first phase:
1. inspect live `ui.py` and current presenter/session/search/composer APIs
2. map existing widgets/behavior to v1 ADOPT/HOLD/REJECT
3. design the smallest coherent beginner-first flow
4. implement dependency-independent UI foundation on a dedicated branch from latest main
5. keep a clean provider boundary for later #64 General taxonomy integration

Expected main flow:

`Prompt入力/読解 -> タグ発見（検索 / Special browse / General browse） -> 選択・並べ替え -> canonical-English preview/copy`

Do not wait idly for #64 before implementing all dependency-independent UI work.
Do not invent production General taxonomy while waiting for #64.

## Product convergence route

Parallel now:

- **#64** — General 30,629 full taxonomy candidate/audit
- **#66 Phase A/B** — app/UI audit, design and dependency-independent implementation

Then:
1. after #64 acceptance, **#34** resolves bilingual search relevance/noise
2. #66 consumes accepted #64 General taxonomy and later accepted #34 search behavior
3. **#42** performs final v1 scope reconciliation / `V1_SCOPE_LOCKED`
4. #66 performs final cleanup/integration, focused regression and real Windows UI acceptance
5. practical v1 baseline
6. after that, resume Stage10 #65 unless the user changes priority

#66 may make substantial progress before #42, but #42 remains the final product-scope Gate and may require final deltas.

## Workstreams Registry

| TEAM_ID | Status | Scope | Restore anchor |
| --- | --- | --- | --- |
| `GENERAL-DICT:#64` | **ACTIVE DEV / PARALLEL** | 30,629 General practical taxonomy | Issue #64 body + latest checkpoint + rollout PROGRESS |
| `V1-APP:#66` | **ACTIVE DEV / PARALLEL / APP COMPLETION OWNER** | beginner-first desktop UI/app completion | Issue #66 body + latest checkpoint |
| `STAGE10-LEARNING:#65` | **PAUSED BY USER PRIORITY / RESUME AFTER APP BASELINE** | practical image-generation mastery, NoobAI-first | Issue #65 + `docs/stages/STAGE_10_LEARNING.md` |
| `PRODUCT-FIT:#63` | **COMPLETED / MERGED** | product-fit verdict sidecar | Issue #63 acceptance comment + `docs/issue63/IMPLEMENTATION_REPORT.md` |
| `UIJA-PARENT:#34` | **AFTER #64** | bilingual search relevance/noise | Issue #34 |
| `PRODUCT:#42` | **AFTER #34 / FINAL V1 SCOPE OWNER** | final beginner-first v1 scope reconciliation | Issue #42 + `PRODUCT_GOAL_LOCK.md` |
| `KNOWLEDGE:#44` | **ONGOING / V1 NON-BLOCKING / STAGE10 KNOWLEDGE SUPPLIER** | knowledge corpus + Prompt/generation knowledge | Issue #44 + `knowledge/generation-corpus` |
| `MAINT:#24` | OPEN / SAFETY DEBT | local protected data backup/restore | Issue #24 |

Historical only:
- `PROMPT:#5` — retired/closed; responsibilities merged into `KNOWLEDGE:#44`; comments/evidence preserved for provenance.
- old Stage10 production A/B definition — superseded by Issue #65 / `STAGE_10_LEARNING.md`; old evaluator/A/B artifacts remain teaching/testing evidence.

## Completed / frozen foundations

- Stage9 overall Gate — PASS / completed
- automated E2E #28 — PASS / completed
- Special validation/promotion/freeze #32 -> #48 -> #49 -> #43 — completed
- Special Core Dictionary practical taxonomy #56 — completed / Final Audit PASS / PR #62 merged
  - 2,788 / 2,788 browse mapping
  - old `その他・文脈` 1,404 / 1,404
  - unmapped 0 / Alias pending 0
- Special product-fit full audit — completed 2,788 / 2,788
- Issue #63 product-fit sidecar — accepted/merged
  - KEEP 1,618
  - KEEP_REFERENCE_ONLY 1,133
  - OUT_OF_SCOPE_PRODUCT 12
  - REVIEW 25
  - CSV SHA-256 `357427dfd542a4e582f6fe57bc966539210e794796e9ad93d6350950e1f61f68`
- Japanese overlay #36/#55 — completed / production 30,629 entries
- Japanese-first presentation pass #35 — completed
- evaluator/calibration #30 — completed / evidence retained
- generation knowledge desk coverage #44 — coverage ready; corpus remains ongoing
- former PROMPT #5 work — preserved as historical evidence under KNOWLEDGE #44 ownership

Do not restart completed #32/#43/#56/#63 work wholesale.

## Known test debt

Issue #63 acceptance review confirmed:
- focused product-fit suite: 122 passed (reported by implementation handoff)
- full suite on refreshed main base before acceptance: 360 passed / 10 failed
- 9 failures matched the pre-existing task-start baseline
- the additional product-goal wording mismatch in `tests/test_final_spec.py` was synchronized to current terminology on main in commit `390528bdf884f5394ae9465e0f38f9143b2b1661`

The remaining historical 9 failures are not silently reclassified as PASS. They remain separate maintenance/evidence debt and do not reopen #63 unless a direct regression is demonstrated.

## Frozen terminology

- formal dictionary: **Special Core Dictionary**
- historical compatibility identifier: `Special2788`
- selected Special group: `Core Tag Set` where that subsystem is used
- final Prompt payload: canonical English
- Japanese labels: understanding/search/display assistance, not canonical authority
- current Stage10 definition: **practical image-generation learning stage** (currently paused by priority)
- old Stage10 production A/B: **legacy Stage10 validation evidence**

## v1 ADOPT

- existing Prompt understanding
- Japanese + English search
- Special deep genre browsing
- General 30,629 shallow practical genre browsing
- manual add/remove/reorder
- final Prompt preview/copy
- local/non-LLM runtime

## v1 HOLD / optional

- co-occurrence suggestions
- usage-count/detail views
- Semantic Bridge beyond search needs
- Prompt history/favorites
- advanced hints
- direct Forge/ComfyUI adapters

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

Existing assets may remain internally. Do not delete evidence merely because a v1 feature is deferred.

## Important current code delta now owned operationally by #66

1. UI is still primarily `Specialを探す` / Special-first and lacks the final existing-Prompt-understanding + General-browse entry flow.
2. Recommendation UI still exposes `よく使われる / 珍しい関連 / 意味から補助` as prominent product surfaces.
3. `PromptComposer` currently allows `CORE_SUPPORT + ADDITIVE` semantic supports to become default-on internally while `Stage9ComposerSession.automatic_injections` exposes no automatic items. For v1, hidden automatic insertion should be removed/disabled or made explicitly user-selected.
4. General 30,629 browse taxonomy does not yet exist; #64 owns the data, #66 owns the eventual UI consumption.

#66 may address 1–3 now while preserving #34/#42 authority boundaries.

## Data boundaries

### Special
- frozen 2,788 identities
- #56 taxonomy sidecar
- #63 product-fit sidecar merged to production

### General
- production Japanese overlay: 30,629 canonical entries
- runtime overlay normally local protected `data/runtime/japanese_overlay.json`
- #64 taxonomy must be a separate canonical-tag keyed sidecar
- #66 must consume the accepted sidecar rather than create a competing production taxonomy
- do not expand #64/#66 silently to the full 100k+ universe

### Statistics / generation evidence
- full Stage5 index / co-occurrence / Generation Profile / evaluator evidence remain preserved optional assets
- Prompt/generation knowledge is owned by #44
- these assets are not v1 core runtime dependencies

## Source-of-Truth Rule

Current active DEV lanes:
- **Issue #64** — General taxonomy data
- **Issue #66** — app/UI completion

Current product convergence:
- `#64 + #66 foundation -> #34 -> #42 -> #66 final integration/Windows acceptance -> v1 baseline`

Current Stage10:
- Issue #65 + `docs/stages/STAGE_10_LEARNING.md`
- **paused until app baseline by current user priority**

Generation/Prompt knowledge:
- **Issue #44 KNOWLEDGE**
- Issue #5 is historical/retired and must not be reactivated as an independent team

Management authority:
- `CURRENT_STATE.md` = routing
- live Issue = executable task/learning contract
- `PERMANENT_RULES.md` = permanent workflow/safety
- `PRODUCT_GOAL_LOCK.md` = product goal
- `DECISIONS.md` = durable design decisions
- `STAGE_10_LEARNING.md` = Stage10 definition, even while paused

## Next Actions

Parallel product work:
1. Continue #64 from its latest live checkpoint/PROGRESS without restarting persisted rows.
2. Start #66 from latest live main: audit current UI/code and produce the simplest coherent v1 interaction design.
3. Implement #66 dependency-independent Phase B on its own branch; do not use the #64 rollout branch as an app branch.
4. Keep General browse behind a clean provider/interface until #64 output is accepted.
5. After #64 acceptance, run #34 bilingual search relevance/noise and wire accepted General taxonomy into #66.
6. Activate #42 for final ADOPT/HOLD/REJECT reconciliation.
7. Finish #66 final integration, focused regression, real Windows UI acceptance and establish v1 baseline.
8. Resume Stage10 #65 after the app baseline unless the user changes priority.

Other non-blocking lanes:
- #44 may maintain knowledge, but broad Stage10 learning is currently not the primary task.
- #24 protected-data backup/restore verification.
