# CURRENT STATE

最終更新: 2026-09-12

## Current Stage

**Stage9 completed / beginner-first v1 product narrowing active as management direction / current core DEV remains Issue #63 until its implementation is retrieved, accepted and merged.**

Stage10 production A/B is **not started and is no longer a v1 completion blocker**.

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
- Issue #42 `[PRODUCT][V1-NARROWING][RESERVED] Beginner-first product scope and implementation path`

New General taxonomy lane:
- Issue #64 `[GENERAL-DICT][UI-TAXONOMY][RESERVED] Practical genre browsing for 30,629 Japanese-overlay entries`

## Current Core DEV

**Issue #63 — product-fit verdict sidecar integration**

Live GitHub still owns acceptance/routing for #63.
Do not advance the core DEV state merely from chat/Codex self-report.
Retrieve and verify the reviewable branch/commit/report/tests first.

Authoritative product-fit audit counts:
- KEEP 1,618
- KEEP_REFERENCE_ONLY 1,133
- OUT_OF_SCOPE_PRODUCT 12
- REVIEW 25
- total 2,788

Required behavior remains as defined by Issue #63:
- ID-keyed sidecar
- no canonical/Special ID/Alias/provenance mutation
- centralized product-facing eligibility
- #34 search ranking remains out of scope for #63

Current continuation:
`ISSUE63_PRODUCT_FIT_VERDICT_INTEGRATION`

## Next required route

After #63 is accepted/merged:

1. **Issue #34** — bilingual search relevance/noise
2. **Issue #42** — reconcile current code/UI against the new v1 scope and lock `V1_SCOPE_LOCKED`
3. **Issue #64** — General 30,629 practical browse taxonomy sidecar
4. **v1 UI integration** — `understand -> discover -> choose -> copy`
5. focused regression + real Windows UI acceptance
6. v1 baseline

Issue #5 / Stage10 is outside this required route unless a future adopted feature needs generation-effectiveness evidence.

## Workstreams Registry

| TEAM_ID | Status | Scope | Restore anchor |
| --- | --- | --- | --- |
| `PRODUCT-FIT:#63` | **CURRENT CORE DEV / OPEN** | product-fit verdict sidecar | Issue #63 body + latest checkpoint |
| `UIJA-PARENT:#34` | **NEXT AFTER #63** | bilingual search relevance/noise | Issue #34 |
| `PRODUCT:#42` | **RESERVED / V1 SCOPE OWNER** | beginner-first v1 narrowing | Issue #42 + `PRODUCT_GOAL_LOCK.md` |
| `GENERAL-DICT:#64` | **RESERVED** | 30,629 General practical taxonomy | Issue #64 |
| `KNOWLEDGE:#44` | ONGOING / V1 NON-BLOCKING | generation knowledge corpus | Issue #44 |
| `PROMPT:#5` | GATED / FUTURE | generation-effectiveness / Stage10 handoff only when needed | Issue #5 |
| `MAINT:#24` | OPEN / SAFETY DEBT | local protected data backup/restore | Issue #24 |

## Completed / frozen foundations

- Stage9 overall Gate — PASS / completed
- automated E2E #28 — PASS / completed
- Special validation/promotion/freeze #32 -> #48 -> #49 -> #43 — completed
- Special Core Dictionary practical taxonomy #56 — completed / Final Audit PASS / PR #62 merged
  - 2,788 / 2,788 browse mapping
  - old `その他・文脈` 1,404 / 1,404
  - unmapped 0 / Alias pending 0
- Special product-fit full audit — completed 2,788 / 2,788
- Japanese overlay #36/#55 — completed / production 30,629 entries
- Japanese-first presentation pass #35 — completed
- evaluator/calibration #30 — completed / evidence retained
- generation knowledge desk coverage #44 — coverage ready; corpus remains ongoing

Do not restart completed #32/#43/#56 work wholesale.

## Frozen terminology

- formal dictionary: **Special Core Dictionary**
- historical compatibility identifier: `Special2788`
- selected Special group: `Core Tag Set` where that subsystem is used
- final Prompt payload: canonical English
- Japanese labels: understanding/search/display assistance, not canonical authority

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

## Important current code delta for #42

Known current implementation mismatches to reconcile later, not during #63/#34 unless explicitly in scope:

1. UI is still primarily `Specialを探す` / Special-first and lacks the final existing-Prompt-understanding + General-browse entry flow.
2. Recommendation UI still exposes `よく使われる / 珍しい関連 / 意味から補助` as prominent product surfaces.
3. `PromptComposer` currently allows `CORE_SUPPORT + ADDITIVE` semantic supports to become default-on internally while `Stage9ComposerSession.automatic_injections` exposes no automatic items. For v1, hidden automatic insertion should be removed/disabled or made explicitly user-selected.
4. General 30,629 browse taxonomy does not yet exist; #64 owns it.

## Data boundaries

### Special
- frozen 2,788 identities
- #56 taxonomy sidecar
- #63 product-fit sidecar

### General
- production Japanese overlay: 30,629 canonical entries
- runtime overlay normally local protected `data/runtime/japanese_overlay.json`
- #64 taxonomy must be a separate canonical-tag keyed sidecar
- do not expand #64 silently to the full 100k+ universe

### Statistics / generation evidence
- full Stage5 index / co-occurrence / Generation Profile / evaluator evidence remain preserved optional assets
- they are not v1 core runtime dependencies

## Source-of-Truth Rule

Current core DEV:
- Issue #63

Current route:
- `#63 acceptance -> #34 -> #42 -> #64 -> v1 UI integration/Windows acceptance`

Future generation-effectiveness lane:
- Issue #5 / Stage10 only when a concrete adopted feature requires empirical image evidence

Management authority:
- `CURRENT_STATE.md` = routing
- live Issue = executable task contract
- `PERMANENT_RULES.md` = permanent workflow/safety
- `PRODUCT_GOAL_LOCK.md` = product goal
- `DECISIONS.md` = durable design decisions

## Next Actions

1. Retrieve/verify the Codex #63 branch/commit/report/tests.
2. If reviewable and correct, perform required DEV/AUDIT acceptance and merge #63.
3. Move current core DEV to #34 and fix bilingual relevance/noise.
4. Activate #42 only after #34, compare actual current code against the v1 ADOPT/HOLD/REJECT list, and lock v1 scope.
5. Route to #64 for General 30,629 practical taxonomy.
6. Integrate the final beginner-first UI and perform real Windows acceptance.

Parallel safety debt:
- #24 protected-data backup/restore verification.
