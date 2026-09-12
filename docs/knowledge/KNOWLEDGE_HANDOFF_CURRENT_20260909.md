# KNOWLEDGE Current Handoff

Owner: Issue #44 `KNOWLEDGE:#44`

Updated: 2026-09-13

Status: `HANDOFF_READY_V6 / PROMPT_MERGED / V1_GOAL_SYNCED / STAGE10_NOOB_ACTIVE`

## Purpose

Compact restart point for the persistent DanbooruTagTool KNOWLEDGE lane. A future chat must recover current knowledge from GitHub without conversational memory.

The former PROMPT team/lane was retired on 2026-09-12 and merged into KNOWLEDGE. This lane now owns both the knowledge corpus and Prompt/generation-effectiveness knowledge work, and supplies evidence/guidance to the current Stage10 learning lane.

## Restore order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 latest comments/body
4. `docs/PRODUCT_GOAL_LOCK.md`
5. for current Stage10 work: Issue #65 + `docs/stages/STAGE_10_LEARNING.md`
6. `docs/knowledge/KNOWLEDGE_HANDOFF_CURRENT_20260909.md` (this file)
7. `docs/knowledge/current/CURRENT_QUICK_REFERENCE.md`
8. `docs/knowledge/current/PRACTICAL_GENERATION_NOOB_ANIMA.md`
9. `docs/knowledge/current/CLAIM_REGISTRY.csv`
10. `docs/knowledge/KNOWLEDGE_CATALOG.md`
11. relevant `docs/knowledge/catalog/*.md`
12. `docs/knowledge/current/HOLD_CONFLICT_REGISTER.md` and `VERSION_FRESHNESS_LEDGER.csv` when uncertainty/version matters
13. detailed `docs/knowledge/research/*` only when evidence/provenance is needed
14. corpus/sources/index for broad historical context

## Current source-of-truth layering

- project/product routing = main `CURRENT_STATE.md` / `PRODUCT_GOAL_LOCK.md`
- current Stage10 definition = Issue #65 + main `docs/stages/STAGE_10_LEARNING.md`
- lane state / restart = Issue #44 + this handoff
- **claim-level current verdict = `current/CLAIM_REGISTRY.csv`**
- current uncertainty detail = `current/HOLD_CONFLICT_REGISTER.md`
- version/freshness = `current/VERSION_FRESHNESS_LEDGER.csv`
- practical Noob/Anima operation = `current/PRACTICAL_GENERATION_NOOB_ANIMA.md`
- readable topic explanation = `KNOWLEDGE_CATALOG.md` + `catalog/*.md`
- evidence/provenance/history = `GENERATION_KNOWLEDGE_SOURCES.md` + `research/*`
- broad synthesis/history = corpus/index

Old document wording never overrides a newer Claim Registry row, current main product goal, or the current Stage10 definition.

## Team identity / boundaries

- TEAM_ID: `KNOWLEDGE:#44`
- branch: `knowledge/generation-corpus`
- lane: ongoing persistent knowledge + former PROMPT responsibilities + Stage10 knowledge supplier
- separate PROMPT team: **retired**
- historical Issue #5: evidence/provenance only
- runtime remains local and non-LLM
- KNOWLEDGE does not directly rewrite production dictionary data
- KNOWLEDGE does not own production/spec adoption
- KNOWLEDGE does not own #32 validation verdicts
- unresolved behavior stays `HOLD`
- Stage10 local learning evidence is not automatically a global Claim

## Current product goal

Canonical current v1 goal:

`Promptを日本語で理解 -> 日本語/英語検索・ジャンル閲覧でタグを発見 -> 自分で選択 -> canonical-English Promptを出力`

Shorthand:

`理解 -> 発見 -> 選択 -> 出力`

This is the **current product goal**.

Stage10 is separate and parallel. Its current skill goal is:

`意図 -> Prompt -> 生成 -> 観察 -> 原因分解 -> 修正 -> 必要な補助 -> 仕上げ -> 再現可能な保存`

Stage10 completion is not a v1 product Gate, and v1 completion does not mean Stage10 learning is complete.

## Two knowledge horizons

### v1-supporting knowledge

Directly supports beginner-first understanding/discovery without requiring image-effectiveness claims:
- canonical meaning / Alias / implication boundaries
- Japanese understanding/search support
- source authority
- browse/discovery explanations
- terminology/traceability
- avoiding misleading search/UI claims

### practical/advanced generation knowledge

Preserved and expanded as Stage10 learning support and future product evidence, but non-blocking for v1:
- NoobAI / Anima / WAI / Illustrious exact-profile behavior
- Prompt composition/support/anti-support
- minimum-sufficient Prompt
- relation/binding/body-site/count/topology behavior
- Negative interactions
- Seed / weight / Prompt-density behavior
- LoRA/control/postprocess boundaries
- Hires/ADetailer/img2img/inpaint workflows
- regional/Forge Couple/control escalation
- evaluator/tagger limits
- controlled image comparison when a concrete learning/research claim benefits from it

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
7 WAI17 local test profile — retained historical/comparison profile
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

## Current practical / empirical target

Current Stage10 primary learning and practical-image lane:

**NoobAI XL 1.1 EPS + Forge Neo**

Initial author-baseline context:
- Euler a
- Steps 25–30
- CFG 5–6
- around SDXL 1MP
- caption organization `count -> character -> series -> artist -> special -> general -> other`

Secondary lanes:
- Anima — relation-heavy / multi-character / tag + concise natural-language comparison/fallback
- WAI Illustrious v17 — historical/comparison lane and preserved prior controlled evidence
- NoobAI V-Pred — separate advanced profile; never pool with EPS

High-value unresolved local comparisons include:
- Noob canonical/Alias/historical trigger response
- Noob actor-target/body-site/count ceiling
- Noob EPS vs V-Pred practical delta
- Illustrious-family LoRA -> Noob reliability
- Anima tag-only vs concise hybrid relation delta
- Prompt-only -> regional/control escalation threshold

Do not run a broad 2,788-entry sweep merely because old Stage10 infrastructure exists.

## Maintenance workflow

For new meaningful knowledge:

`research/source evidence -> existing Claim check -> Registry update -> category explanation if needed -> HOLD/CONFLICT update -> version ledger update -> controlled image validation only when useful -> Stage10/local evidence kept scoped -> downstream DEV/product handoff only when authorized -> #44 checkpoint`

Do not duplicate the same verdict text into every summary.

## Handoff readiness

A future KNOWLEDGE / Stage10 chat is ready when it can recover:
- current v1 product goal
- current Stage10 NoobAI-first learning definition
- #64 product work remains separate/parallel
- the distinction between source facts, Claims, HOLD, and local Stage10 evidence
- current Noob/Anima practical guidance
- current HOLD/freshness
- legacy WAI/old Stage10 provenance
- former PROMPT work under #44 ownership

without relying on chat history.
