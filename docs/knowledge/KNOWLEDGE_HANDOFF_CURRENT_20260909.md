# KNOWLEDGE Current Handoff

Owner: Issue #44 `KNOWLEDGE:#44`

Updated: 2026-09-12

Status: `HANDOFF_READY_V5 / PROMPT_MERGED / V1_GOAL_SYNCED`

## Purpose

Compact restart point for the persistent DanbooruTagTool KNOWLEDGE lane. A future chat must recover current knowledge from GitHub without conversational memory.

The former PROMPT team/lane was retired on 2026-09-12 and merged into KNOWLEDGE. This lane now owns both the knowledge corpus and future Prompt/generation-effectiveness knowledge work.

## Restore order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 latest comments/body
4. `docs/PRODUCT_GOAL_LOCK.md`
5. `docs/knowledge/KNOWLEDGE_HANDOFF_CURRENT_20260909.md` (this file)
6. `docs/knowledge/current/CURRENT_QUICK_REFERENCE.md`
7. `docs/knowledge/current/CLAIM_REGISTRY.csv`
8. `docs/knowledge/KNOWLEDGE_CATALOG.md`
9. relevant `docs/knowledge/catalog/*.md`
10. `docs/knowledge/current/HOLD_CONFLICT_REGISTER.md` and `VERSION_FRESHNESS_LEDGER.csv` when uncertainty/version matters
11. detailed `docs/knowledge/research/*` only when evidence/provenance is needed
12. corpus/sources/index for broad historical context

## Current source-of-truth layering

- project/product routing = main `CURRENT_STATE.md` / `PRODUCT_GOAL_LOCK.md`
- lane state / restart = Issue #44 + this handoff
- **claim-level current verdict = `current/CLAIM_REGISTRY.csv`**
- current uncertainty detail = `current/HOLD_CONFLICT_REGISTER.md`
- version/freshness = `current/VERSION_FRESHNESS_LEDGER.csv`
- readable topic explanation = `KNOWLEDGE_CATALOG.md` + `catalog/*.md`
- evidence/provenance/history = `GENERATION_KNOWLEDGE_SOURCES.md` + `research/*`
- broad synthesis/history = corpus/index

Old document wording never overrides a newer Claim Registry row or current main product goal.

## Team identity / boundaries

- TEAM_ID: `KNOWLEDGE:#44`
- branch: `knowledge/generation-corpus`
- lane: ongoing persistent knowledge + former PROMPT responsibilities
- separate PROMPT team: **retired**
- historical Issue #5: evidence/provenance only
- runtime remains local and non-LLM
- KNOWLEDGE does not directly rewrite production dictionary data
- KNOWLEDGE does not own production/spec adoption
- KNOWLEDGE does not own #32 validation verdicts
- unresolved behavior stays `HOLD`
- other teams receive handoffs only when requested/required by project flow

## Current product goal

Canonical current v1 goal:

`Promptを日本語で理解 -> 日本語/英語検索・ジャンル閲覧でタグを発見 -> 自分で選択 -> canonical-English Promptを出力`

Shorthand:

`理解 -> 発見 -> 選択 -> 出力`

This supersedes the older Special-first knowledge-lane product wording as the **current product goal**.

The older advanced generation target remains useful as a future knowledge horizon, not as v1 routing:

`intent -> tag/Special candidate(s) -> evidence-aware support/structure -> model-family-appropriate Prompt guidance -> controlled failure diagnosis`

## Two knowledge horizons

### v1-supporting knowledge

Directly supports beginner-first understanding/discovery without requiring image-effectiveness claims:
- canonical meaning / Alias / implication boundaries
- Japanese understanding/search support
- source authority
- browse/discovery explanations
- terminology/traceability
- avoiding misleading search/UI claims

### future/advanced generation knowledge

Preserved and expanded, but non-blocking for v1:
- Prompt composition/support/anti-support
- minimum-sufficient Prompt
- model-family-specific guidance
- relation/binding/body-site/count/topology behavior
- Negative interactions
- LoRA/control/postprocess boundaries
- evaluator/tagger limits
- generation-effectiveness questions
- narrow controlled A/B when a concrete adopted feature/research question requires evidence

These are not separate teams. Product relevance, scope and validation state distinguish them.

## Claim-level organization

Current management lives under `docs/knowledge/current/`.

Registry fields separate:
- `SOURCE_CLASS`
- `STATUS`
- `SCOPE`
- `VALIDATION_STATE`

Legacy `PROMPT` strings in older evidence/metadata do not identify an active team after 2026-09-12; new routing goes through KNOWLEDGE #44.

## Canonical topic catalog

The one topic taxonomy remains `catalog/00–10`. The current management layer is cross-topic metadata, not a replacement taxonomy.

0 foundations/authority
1 model families
2 Prompt/support/composition
3 failure/testing/evaluation
4 tools/postprocess/LoRA
5 hard/niche generation
6 semantics/Alias/trigger
7 WAI17 local test profile
8 source/site audits
9 open questions/HOLD explanation
10 file map

## Core durable knowledge

- model family/version/profile is part of every generation claim
- canonical identity, Alias, implication, UI Japanese, trigger and generation support are separate
- presence is not relation success
- minimum sufficient is not shortest
- support can become anti-support
- Negative Prompt is active semantic conditioning
- one seed is case evidence, not reliability
- postprocess/control/LoRA-assisted success differs from Prompt-only capability
- evaluator vocabulary/calibration/OOD/semantic class must be checked
- unsupported cases remain HOLD/REVIEW

Current Claim IDs and status are authoritative in Registry.

## Current first empirical target — only when image testing is justified

WAI Illustrious v17 + Forge Neo remains the current local first-test lane unless a newer explicit decision changes it.

Current isolation baseline remains evidence context, not a product requirement or proven optimum:
- Euler a
- Steps 25
- CFG 5
- 1024×1344 portrait when appropriate
- fixed paired seeds
- Hires/ADetailer/LoRA/regional/ControlNet OFF

Do not run broad Stage10/image sweeps merely to complete v1 or exhaust HOLD items.

## Maintenance workflow

For new meaningful knowledge:

`research/source evidence -> existing Claim check -> Registry update -> category explanation if needed -> HOLD/CONFLICT update -> version ledger update -> narrow validation only if required -> downstream DEV/product handoff when authorized -> #44 checkpoint`

Do not duplicate the same verdict text into every summary.

## Handoff readiness

A future KNOWLEDGE chat is ready when it can recover:
- current v1 product goal
- the distinction between v1-supporting and future/advanced generation knowledge
- claim status/source/scope/validation
- current HOLD/freshness
- legacy provenance
- former PROMPT work under #44 ownership

without relying on chat history.
