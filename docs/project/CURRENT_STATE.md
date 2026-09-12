# CURRENT STATE

最終更新: 2026-09-13

## Current Stage

**Stage9 completed / beginner-first v1 product direction locked / two active DEV lanes run in parallel: Issue #64 data taxonomy + Issue #66 app/search/UI completion.**

Current active implementation owners:
- **Issue #64** — General 30,629 practical browse taxonomy
- **Issue #66** — beginner-first app completion, bilingual search quality, final v1 acceptance

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
- live UI/code audit against the current v1 goal
- beginner-first information architecture
- existing-Prompt understanding/workspace UI
- Japanese/English/mixed bilingual search quality and ranking/noise fixes
- Special deep browse integration from completed #56 assets
- General browse UI shell/provider boundary while waiting for #64
- explicit add/remove/reorder
- canonical-English preview/copy
- removal/de-emphasis of obsolete Stage-first/recommendation-first default UI
- visible-state vs actual-Prompt consistency, including hidden automatic insertion checks
- final ADOPT/HOLD/REJECT reconciliation against `PRODUCT_GOAL_LOCK.md`
- focused regression and real Windows/Tk acceptance

Search requirements inherited from retired #34 include:
- exact canonical / exact English / exact approved Alias / strong Japanese intent outrank incidental fuzzy/substring matches
- Japanese, English and mixed input share one coherent discovery workflow
- relevant Special/General results are not swamped by unrelated General noise
- known regression such as `anal -> piano / analog...` is fixed and tested
- canonical/protected data is not mutated to hide ranking defects

## Current route

Parallel now:
- **#64** — General 30,629 full taxonomy candidate/audit
- **#66 Phase A/B** — app/UI/search audit, design and dependency-independent implementation

After #64 acceptance:
1. #66 consumes accepted General taxonomy sidecar
2. #66 reruns search relevance against the final product-facing General population
3. #66 performs final scope reconciliation, cleanup, regression and real Windows UI acceptance
4. practical v1 baseline
5. resume Stage10 #65 unless the user changes priority

Short form:

`#64 + #66 in parallel -> #66 consumes #64 -> #66 final acceptance -> Windows acceptance -> v1 baseline -> Stage10 resume`

## Workstreams Registry

| TEAM_ID | Status | Scope | Restore anchor |
| --- | --- | --- | --- |
| `GENERAL-DICT:#64` | **ACTIVE DEV / PARALLEL** | 30,629 General practical taxonomy | Issue #64 + latest checkpoint + rollout PROGRESS |
| `V1-APP:#66` | **ACTIVE DEV / PARALLEL / APP+SEARCH+FINAL ACCEPTANCE OWNER** | beginner-first desktop app/search/UI completion | Issue #66 body + latest checkpoint |
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

Existing assets may remain internally; do not delete evidence merely because a v1 feature is deferred.

## Important current code delta owned by #66

1. UI is still primarily `Specialを探す` / Special-first and lacks the final existing-Prompt-understanding + General-browse entry flow.
2. Recommendation UI still exposes `よく使われる / 珍しい関連 / 意味から補助` too prominently.
3. `PromptComposer` may allow hidden default support insertion while the visible session reports none; v1 must make copied Prompt match explicit visible state.
4. Search has known incidental substring/fuzzy false-positive behavior.
5. General 30,629 browse taxonomy is not yet accepted; #64 owns the data, #66 owns eventual UI consumption.

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

Permanent workflow/safety:
- `docs/project/PERMANENT_RULES.md`

Stage10 definition, while paused:
- Issue #65 + `docs/stages/STAGE_10_LEARNING.md`

Issues #42 and #34 are historical only and must not be reactivated as required Gates.

## Next Actions

1. Continue #64 from its latest live checkpoint/PROGRESS without restarting persisted rows.
2. Start/continue #66 from latest live main: audit current UI/search/code and implement the simplest coherent v1 interaction design.
3. Fix dependency-independent bilingual search relevance/noise inside #66, including representative substring/fuzzy regressions.
4. Keep #66 General browse behind a clean provider/interface until #64 output is accepted.
5. After #64 acceptance, wire accepted General taxonomy into #66 and rerun product-facing search/browse checks.
6. In #66, perform final scope reconciliation against `PRODUCT_GOAL_LOCK.md`, focused regression, real Windows UI acceptance and establish v1 baseline.
7. Resume Stage10 #65 after the app baseline unless the user changes priority.
