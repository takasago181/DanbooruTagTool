# CURRENT STATE

最終更新: 2026-09-13

## Current Stage

**Stage9 completed / beginner-first v1 product narrowing active as management direction / current core DEV is Issue #64.**

Issue #63 product-fit verdict sidecar integration is **ACCEPTED / MERGED / CLOSED**.

**Stage10 has been redefined and is now ACTIVE as a parallel practical image-generation learning lane under Issue #65.**
The old meaning of Stage10 as broad Special Core Dictionary production A/B validation is retired as the current Stage10 definition. Old A/B/evaluator assets remain historical/testing evidence.

Stage10 learning is **not a v1 completion blocker** and does not replace the current core DEV route.

Current Stage10 authority:
- `docs/stages/STAGE_10_LEARNING.md`
- Issue #65 `[STAGE10][LEARNING][ACTIVE] Practical image-generation mastery with NoobAI`

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

## Stage10 learning direction

Stage10 is now a **hands-on image-generation skill-acquisition stage**.

Primary learning model:
- **NoobAI XL 1.1 EPS + Forge Neo**

Secondary lanes:
- Anima — relation-heavy / multi-character / tag + natural-language comparison/fallback
- WAI Illustrious v17 — historical/comparison lane
- NoobAI V-Pred — separate advanced comparison profile; never pooled with EPS

Target outcome:

`日本語の意図 -> Prompt設計 -> 生成 -> 観察 -> 原因分解 -> 修正 -> 必要ならLoRA/修復/領域制御 -> 仕上げ -> 再現可能な保存`

The learner should become able to independently create difficult/niche adult fictional 2D illustrations, including hard relation/body-site/count-sensitive targets, while understanding why a result succeeded or failed.

Curriculum:
- 10.0 environment / reproducibility basics
- 10.1 Prompt fundamentals
- 10.2 composition / camera / visibility
- 10.3 hard/niche structural generation
- 10.4 failure diagnosis / controlled iteration
- 10.5 seed / Negative / weights / LoRA
- 10.6 Hires / ADetailer / img2img / inpaint finishing
- 10.7 regional / Control escalation
- 10.8 efficient daily workflow
- 10.9 independent capstone generation

Current start point:
- **Stage10.0 -> 10.1 with NoobAI XL 1.1 EPS**

## Current Core DEV

**Issue #64 — General 30,629 practical browse taxonomy sidecar**

Goal:
- turn the exact production Japanese-overlay population into a shallow, practical Japanese-first browse dictionary
- keep taxonomy separate from canonical identity and `japanese_overlay.json`
- validate the taxonomy against real data before full rollout

Required process:
1. reproduce/materialize exact 30,629 target population
2. inspect distribution and representative samples
3. freeze a small practical taxonomy
4. run a reproducible pilot
5. audit boundary/error patterns
6. expand only after pilot acceptance
7. validate full reachability or explicit unresolved accounting

Current continuation:
`ISSUE64_GENERAL_30629_PRACTICAL_TAXONOMY`

Do not implement #34 ranking redesign or #42 broad UI/product-scope work inside #64.
Do not expand to the full 100k+ Danbooru universe.

## Next required product route

After #64 is accepted/merged:

1. **Issue #34** — bilingual search relevance/noise
2. **Issue #42** — reconcile current code/UI against the new v1 scope and lock `V1_SCOPE_LOCKED`
3. **v1 UI integration** — `understand -> discover -> choose -> copy`
4. focused regression + real Windows UI acceptance
5. v1 baseline

Stage10 learning runs in parallel and does not block or replace this route.

Generation-effectiveness / Prompt knowledge supporting Stage10 is owned by **KNOWLEDGE #44**. Former PROMPT Issue #5 remains retired/closed and historical only.

## Workstreams Registry

| TEAM_ID | Status | Scope | Restore anchor |
| --- | --- | --- | --- |
| `GENERAL-DICT:#64` | **CURRENT CORE DEV / OPEN** | 30,629 General practical taxonomy | Issue #64 body + latest checkpoint |
| `STAGE10-LEARNING:#65` | **ACTIVE / PARALLEL / NON-BLOCKING** | practical image-generation mastery, NoobAI-first | Issue #65 + `docs/stages/STAGE_10_LEARNING.md` |
| `PRODUCT-FIT:#63` | **COMPLETED / MERGED** | product-fit verdict sidecar | Issue #63 acceptance comment + `docs/issue63/IMPLEMENTATION_REPORT.md` |
| `UIJA-PARENT:#34` | **AFTER #64** | bilingual search relevance/noise | Issue #34 |
| `PRODUCT:#42` | **AFTER #34 / V1 SCOPE OWNER** | beginner-first v1 narrowing | Issue #42 + `PRODUCT_GOAL_LOCK.md` |
| `KNOWLEDGE:#44` | **ONGOING / V1 NON-BLOCKING / STAGE10 KNOWLEDGE SUPPLIER** | knowledge corpus + Prompt/generation knowledge + Stage10 practical evidence support | Issue #44 + `knowledge/generation-corpus` |
| `MAINT:#24` | OPEN / SAFETY DEBT | local protected data backup/restore | Issue #24 |

Historical only:
- `PROMPT:#5` — retired/closed on 2026-09-12; responsibilities merged into `KNOWLEDGE:#44`; comments/evidence preserved for provenance.
- old Stage10 production A/B definition — superseded by Issue #65 / `STAGE_10_LEARNING.md`; old evaluator/A/B artifacts remain usable as teaching/testing evidence.

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

The remaining historical 9 failures are not silently reclassified as PASS. They remain separate maintenance/evidence debt and do not reopen #63 unless a direct #63 regression is demonstrated.

## Frozen terminology

- formal dictionary: **Special Core Dictionary**
- historical compatibility identifier: `Special2788`
- selected Special group: `Core Tag Set` where that subsystem is used
- final Prompt payload: canonical English
- Japanese labels: understanding/search/display assistance, not canonical authority
- current Stage10: **practical image-generation learning stage**
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
Stage10 may use these assets as learning/testing tools without making them v1 product requirements.

## Important current code delta for #42

Known current implementation mismatches to reconcile later, not during #64/#34 unless explicitly in scope:

1. UI is still primarily `Specialを探す` / Special-first and lacks the final existing-Prompt-understanding + General-browse entry flow.
2. Recommendation UI still exposes `よく使われる / 珍しい関連 / 意味から補助` as prominent product surfaces.
3. `PromptComposer` currently allows `CORE_SUPPORT + ADDITIVE` semantic supports to become default-on internally while `Stage9ComposerSession.automatic_injections` exposes no automatic items. For v1, hidden automatic insertion should be removed/disabled or made explicitly user-selected.
4. General 30,629 browse taxonomy does not yet exist; #64 owns it.

## Data boundaries

### Special
- frozen 2,788 identities
- #56 taxonomy sidecar
- #63 product-fit sidecar merged to production

### General
- production Japanese overlay: 30,629 canonical entries
- runtime overlay normally local protected `data/runtime/japanese_overlay.json`
- #64 taxonomy must be a separate canonical-tag keyed sidecar
- do not expand #64 silently to the full 100k+ universe

### Statistics / generation evidence
- full Stage5 index / co-occurrence / Generation Profile / evaluator evidence remain preserved optional assets
- Prompt/generation knowledge is owned by #44
- Stage10 may consume these assets as learning/testing support
- these assets are not v1 core runtime dependencies

## Source-of-Truth Rule

Current core DEV:
- Issue #64

Current product route:
- `#64 -> #34 -> #42 -> v1 UI integration/Windows acceptance`

Current Stage10 learning route:
- Issue #65 + `docs/stages/STAGE_10_LEARNING.md`
- initial lesson `10.0 -> 10.1`, NoobAI XL 1.1 EPS

Generation/Prompt knowledge:
- **Issue #44 KNOWLEDGE**
- Issue #5 is historical/retired and must not be reactivated as an independent team

Management authority:
- `CURRENT_STATE.md` = routing
- live Issue = executable task/learning contract
- `PERMANENT_RULES.md` = permanent workflow/safety
- `PRODUCT_GOAL_LOCK.md` = product goal
- `DECISIONS.md` = durable design decisions
- `STAGE_10_LEARNING.md` = current Stage10 learning definition

## Next Actions

Product route:
1. Continue #64 from latest live main according to its live Issue/checkpoint.
2. Reproduce/classify the exact 30,629 General target population without mutating protected overlay data.
3. Inspect/audit real distribution and representative examples according to #64 before full rollout.
4. After #64 acceptance, move to #34 and fix bilingual relevance/noise.
5. Activate #42 only after #34, compare actual current code against the v1 ADOPT/HOLD/REJECT list, and lock v1 scope.
6. Integrate the final beginner-first UI and perform real Windows acceptance.

Parallel Stage10 learning:
1. Start Stage10.0 with exact NoobAI XL 1.1 EPS + Forge Neo.
2. Create a baseline preset and preserve infotext/metadata.
3. Generate a simple tagged target across exploratory seeds.
4. Lock one seed and change one meaningful variable.
5. Explain the visible difference before moving to relation/body-site-sensitive targets.

Other parallel non-blocking lanes:
- #44 may continue expanding/organizing knowledge and ingest durable Stage10 lessons without making them a v1 Gate.
- #24 protected-data backup/restore verification.
