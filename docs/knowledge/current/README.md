# KNOWLEDGE Current Management Layer

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `CLAIM_LEVEL_CURRENT_V2 / PROMPT_MERGED`

This directory is the **current management layer** for DanbooruTagTool KNOWLEDGE. It does not replace the topic catalog or research originals.

The separate PROMPT team/lane was retired on 2026-09-12. Prompt/generation-effectiveness knowledge is now part of KNOWLEDGE #44.

## Source-of-truth roles

- `CLAIM_REGISTRY.csv` — **current verdict source of truth at claim level**
- `KNOWLEDGE_GOVERNANCE.md` — field meanings, label rules, promotion rules, authority boundaries
- `HOLD_CONFLICT_REGISTER.md` — current unresolved/contested claims and resolution path
- `VERSION_FRESHNESS_LEDGER.csv` — model/runtime/evaluator/source freshness and version applicability
- `CURRENT_QUICK_REFERENCE.md` — 30–60 second overview; never overrides the Claim Registry
- `READING_ROUTES.md` — task-specific 3–5 file restore routes
- `ASSET_INVENTORY.md` — what knowledge exists and where
- `LEGACY_MAP.md` — old/current evidence documents -> category + Claim IDs
- `LABEL_MIGRATION_MAP.md` — old mixed labels -> new SOURCE_CLASS / STATUS / VALIDATION interpretation

Existing layers remain:
- `../KNOWLEDGE_CATALOG.md` + `../catalog/*.md` = readable current explanation by topic
- `../GENERATION_KNOWLEDGE_CORPUS.md` = durable cross-topic synthesis
- `../GENERATION_KNOWLEDGE_SOURCES.md` = source/evidence registry
- `../research/*` = detailed evidence, limitations, audit and historical reasoning
- `../GENERATION_KNOWLEDGE_INDEX.md` = broad historical coverage/backlog context only

## Current product relationship

Current v1 product goal is owned by main `docs/PRODUCT_GOAL_LOCK.md`:

`理解 -> 発見 -> 選択 -> 出力`

KNOWLEDGE contains two horizons:

- **v1-supporting knowledge** — meaning/search/discovery/source authority/traceability that can support the beginner-first product without image-effectiveness claims
- **future/advanced generation knowledge** — Prompt composition, model behavior, support/anti-support, failure diagnosis, evaluator/tool knowledge, and narrow controlled validation when justified

These are one knowledge system, not separate teams.

## Canonical restore order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 latest body/comments
4. `docs/PRODUCT_GOAL_LOCK.md`
5. `docs/knowledge/KNOWLEDGE_HANDOFF_CURRENT_20260909.md`
6. `docs/knowledge/current/CURRENT_QUICK_REFERENCE.md`
7. `docs/knowledge/current/CLAIM_REGISTRY.csv`
8. relevant `docs/knowledge/catalog/*.md`
9. `docs/knowledge/current/HOLD_CONFLICT_REGISTER.md` and `VERSION_FRESHNESS_LEDGER.csv` when uncertainty/version matters
10. `docs/knowledge/research/*` only for evidence/provenance
11. corpus/sources/index for broader historical context

## Conflict rule

If a current Claim Registry row conflicts with an older catalog/corpus/research statement:
- **current verdict = `CLAIM_REGISTRY.csv`**
- older document = evidence/history until explicitly reconciled

If branch-local product wording conflicts with current main `PRODUCT_GOAL_LOCK.md`, main product authority wins.

A Registry row does **not** change production behavior by itself.

## Update workflow

`research -> source registration -> Claim review -> Registry update -> category explanation update -> HOLD/CONFLICT update -> version/freshness update -> narrow validation only if needed -> downstream DEV/product handoff when authorized -> Issue #44 checkpoint`

Do not copy the same conclusion into every file. Each layer has one job.

## Legacy PROMPT references

Historical documents and current Registry metadata may still contain strings such as `PROMPT`, `PROMPT:#5`, or downstream relevance `PROMPT`.

After 2026-09-12:
- they do **not** identify an active independent team;
- they mean historical Prompt/generation-guidance provenance or a knowledge-consumption domain;
- new work is routed through KNOWLEDGE #44;
- Issue #5 is historical/retired and must not be reactivated as a separate lane.

A later cleanup may normalize legacy metadata labels, but label cleanup must not alter claim meaning/evidence.

## Hard invariants

- GitHub is source of truth; chat history is not.
- No automatic promotion from official/author statement to project production optimum.
- No automatic promotion from community/practical evidence to semantic truth.
- Canonical semantics and generation effectiveness are separate.
- Exact model/version/profile scope is part of the claim.
- HOLD/CONFLICT/REJECTED/HISTORICAL are preserved, not hidden.
- KNOWLEDGE may own Prompt/generation evidence but does not own product/spec adoption.
- `data/**`, current DEV authority, #32 verdicts, and broad Stage10 production authorization remain outside this layer's independent authority.

Latest organization decision: Issue #44 current body, 2026-09-12 PROMPT merge.
