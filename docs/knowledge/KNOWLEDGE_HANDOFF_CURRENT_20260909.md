# KNOWLEDGE Current Handoff

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-09

Status: `HANDOFF_READY_V4 / CLAIM_LEVEL_CURRENT`

## Purpose

Compact restart point for the persistent DanbooruTagTool KNOWLEDGE lane. A future chat must recover current knowledge from GitHub without conversational memory.

## Restore order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 latest comments
4. `docs/knowledge/KNOWLEDGE_HANDOFF_CURRENT_20260909.md` (this file)
5. `docs/knowledge/current/CURRENT_QUICK_REFERENCE.md`
6. `docs/knowledge/current/CLAIM_REGISTRY.csv`
7. `docs/knowledge/KNOWLEDGE_CATALOG.md`
8. relevant `docs/knowledge/catalog/*.md`
9. `docs/knowledge/current/HOLD_CONFLICT_REGISTER.md` and `VERSION_FRESHNESS_LEDGER.csv` when uncertainty/version matters
10. detailed `docs/knowledge/research/*` only when evidence/provenance is needed
11. `docs/knowledge/GENERATION_KNOWLEDGE_CORPUS.md`
12. `docs/knowledge/GENERATION_KNOWLEDGE_SOURCES.md`
13. `docs/knowledge/GENERATION_KNOWLEDGE_INDEX.md` only for broad historical coverage/backlog context

## Current source-of-truth layering

- lane state / restart: Issue #44 latest comments + this handoff
- **claim-level current verdict: `current/CLAIM_REGISTRY.csv`**
- current uncertainty detail: `current/HOLD_CONFLICT_REGISTER.md`
- version/freshness: `current/VERSION_FRESHNESS_LEDGER.csv`
- readable topic explanation: `KNOWLEDGE_CATALOG.md` + `catalog/*.md`
- evidence/provenance/history: `GENERATION_KNOWLEDGE_SOURCES.md` + `research/*`
- broad synthesis/history: corpus/index

Old document wording never overrides a newer Claim Registry row.

## Team identity / boundaries

- TEAM_ID: `KNOWLEDGE:#44`
- branch: `knowledge/generation-corpus`
- lane: ongoing persistent corpus
- runtime remains local and non-LLM
- KNOWLEDGE does not directly rewrite production dictionary data
- KNOWLEDGE does not own #32 validation verdicts
- KNOWLEDGE does not authorize Stage10 production A/B
- KNOWLEDGE does not change DEV/PROMPT/AUDIT authority
- unresolved behavior stays `HOLD`
- other teams receive handoffs only when requested/required by project flow

## Current product goal

`short Japanese/English intent -> correct Special Core Dictionary candidate(s) -> minimum useful support/structure -> model-family-appropriate canonical-English Prompt -> safe failure diagnosis -> fewer unnecessary generation iterations`

Primary value: reduce manual trial-and-error while preserving semantic correctness, model/version scope, traceability and uncertainty.

## Claim-level organization

Current management lives under:
`docs/knowledge/current/`

Initial Registry contains **73 important current claims**:
- 49 `ACCEPTED`
- 4 `CANDIDATE`
- 8 `HOLD`
- 10 `REJECTED`
- 2 `HISTORICAL`

Each row separates `SOURCE_CLASS`, `STATUS`, `SCOPE` and `VALIDATION_STATE`.
This prevents author recommendations, project baselines and production-optimum hypotheses from being conflated.

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

## Current first empirical target — WAI Illustrious v17

Exact author guidance:
- Forge Neo recommended
- Euler a
- Steps 15–30
- CFG 5–7
- integrated VAE
- >1024×1024-area recommendation; 1024×1344 examples
- short quality/Negative examples
- excessive quality/aesthetic and long Negative warning
- Hires may repair limbs

Current local **isolation baseline, not optimum claim**:
- Forge Neo
- WAI Illustrious v17
- Euler a
- Steps 25
- CFG 5
- 1024×1344 portrait first candidate when appropriate
- fixed paired seeds
- Hires/ADetailer/LoRA/regional/ControlNet OFF

See Registry `K-MODEL-WAI-*` and HOLD register for unresolved activation/binding/topology/count/Negative/LoRA/control questions.

## Evaluator state

Accepted:
- unary taggers are side signals, not relation ground truth
- WD EVA02 has structural rare-tail coverage limitations
- Kagami/CL are broader-vocabulary candidates, not automatically validated ground truth

HOLD:
- final Special coverage/routing comparison after final dictionary freeze.

## Legacy and labels

- old research/corpus files are preserved
- `current/LEGACY_MAP.md` says where their content is represented now
- `current/LABEL_MIGRATION_MAP.md` explains old mixed labels
- historical/rejected claims stay visible rather than being deleted

## Maintenance workflow

For new meaningful knowledge:

`research/source evidence -> existing Claim check -> Registry update -> category explanation if needed -> HOLD/CONFLICT update -> version ledger update -> downstream handoff when required -> #44 checkpoint`

Do not duplicate the same verdict text into every summary.

## Current checkpoint

Issue #44 organization checkpoint: `5600550931`.

## Handoff readiness

A future KNOWLEDGE chat is ready when it can use GitHub to identify:
claim status, source class, model/version scope, validation requirement, current HOLD, freshness and legacy provenance without relying on chat history.
