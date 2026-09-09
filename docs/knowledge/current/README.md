# KNOWLEDGE Current Management Layer

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `CLAIM_LEVEL_CURRENT_V1`

This directory is the **current management layer** for DanbooruTagTool KNOWLEDGE. It does not replace the existing topic catalog or research originals.

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

## Canonical restore order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 latest comments
4. `docs/knowledge/KNOWLEDGE_HANDOFF_CURRENT_20260909.md`
5. `docs/knowledge/current/CURRENT_QUICK_REFERENCE.md`
6. `docs/knowledge/current/CLAIM_REGISTRY.csv`
7. relevant `docs/knowledge/catalog/*.md`
8. `docs/knowledge/current/HOLD_CONFLICT_REGISTER.md` and `VERSION_FRESHNESS_LEDGER.csv` when uncertainty/version matters
9. `docs/knowledge/research/*` only for evidence/provenance
10. `GENERATION_KNOWLEDGE_CORPUS.md` / `GENERATION_KNOWLEDGE_SOURCES.md` for cross-topic/source detail
11. `GENERATION_KNOWLEDGE_INDEX.md` only for historical coverage/backlog

## Conflict rule

If a current Claim Registry row conflicts with an older catalog/corpus/research statement:
- **current verdict = `CLAIM_REGISTRY.csv`**
- older document = evidence/history until the conflict is explicitly reconciled

A registry row does **not** change production behavior by itself.

## Update workflow

`research -> source registration -> Claim review -> Registry update -> category explanation update -> HOLD/CONFLICT update -> version/freshness update -> downstream handoff when authorized -> Issue #44 checkpoint`

Do not copy the same conclusion into every file. Each layer has one job.

## Hard invariants

- GitHub is source of truth; chat history is not.
- No automatic promotion from official/author statement to project production optimum.
- No automatic promotion from community/practical evidence to semantic truth.
- Canonical semantics and generation effectiveness are separate.
- Exact model/version/profile scope is part of the claim.
- HOLD/CONFLICT/REJECTED/HISTORICAL are preserved, not hidden.
- `data/**`, DEV/PROMPT/AUDIT authority, #32 verdicts, and Stage10 production authorization are outside this layer's authority.

Latest organization checkpoint: Issue #44 comment `5600550931`.
