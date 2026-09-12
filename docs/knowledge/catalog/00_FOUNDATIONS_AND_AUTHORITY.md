# Foundations and Authority

## Current product goal

The current DanbooruTagTool v1 product goal is beginner-first:

`Promptを日本語で理解 -> 日本語/英語検索・ジャンル閲覧でタグを発見 -> 自分で選択 -> canonical-English Promptを出力`

Shorthand:

`理解 -> 発見 -> 選択 -> 出力`

This supersedes the older Special-first wording as the **current product goal**.

Special remains the deep/niche discovery surface, but the v1 product is not defined as `Special -> support -> optimized Prompt`.

Runtime remains local and non-LLM. KNOWLEDGE is evidence/reference and does not directly rewrite production dictionary data or another team's verdict.

## Organization update — 2026-09-12

The separate PROMPT team/lane is retired and merged into KNOWLEDGE #44.

KNOWLEDGE now owns:
- knowledge corpus/research
- Prompt composition knowledge
- support / anti-support / minimum-sufficient Prompt research
- model-specific Prompt guidance
- generation-effectiveness research
- narrow controlled validation design when justified

KNOWLEDGE does **not** gain production/spec authority from this merge.
Historical Issue #5 and old PROMPT documents remain provenance/evidence only.

## Two knowledge horizons

### v1-supporting knowledge

Knowledge directly useful to current beginner-first behavior without generation-effectiveness claims:
- canonical meaning
- Alias/implication boundaries
- Japanese understanding/search support
- source authority
- browse/discovery explanations
- terminology traceability

### future/advanced generation knowledge

Knowledge preserved for later assistance/research and only used in product when explicitly adopted:
- model/version generation behavior
- Prompt composition/support
- relation/binding/count/topology behavior
- Negative interactions
- LoRA/control/postprocess boundaries
- evaluator/tagger limits
- image-dependent effectiveness evidence

Both horizons share the same KNOWLEDGE system and Claim Registry. They are distinguished by scope/product relevance/validation, not separate teams.

## Current claim metadata system

Current claim verdicts are recorded in:
`../current/CLAIM_REGISTRY.csv`

Every current Claim separates four dimensions:

- `SOURCE_CLASS` — what kind of evidence/source supports the claim
- `STATUS` — how KNOWLEDGE currently treats the claim
- `SCOPE` — where the claim applies
- `VALIDATION_STATE` — whether additional validation is required

Definitions and allowed values:
`../current/KNOWLEDGE_GOVERNANCE.md`

This supersedes using one mixed label such as `FACT_EXACT_MODEL` or `TEST_REQUIRED` as if it simultaneously described authority, acceptance, scope and validation.

## Legacy evidence labels

Existing research/corpus files may use:
- `FACT_EXACT_MODEL`
- `FACT_GENERAL`
- `CONTROLLED_PRACTICAL`
- `PRACTICAL`
- `COMMUNITY`
- `HOLD`
- `REJECT`

They remain valid historical shorthand in those files. They do **not** replace the current source/status/scope/validation fields.

Read old labels through:
`../current/LABEL_MIGRATION_MAP.md`

## Authority by question

### Canonical Danbooru meaning
Prefer current Danbooru Wiki + active Alias/Implication records.

### Model trigger / exact generation settings
Prefer exact author model card / author statement for that checkpoint/version.

### Tool behavior
Prefer official GitHub README/docs and version-specific issues.

### General mechanism
Prefer primary papers/research.

### Practical failure modes
Use controlled/practical reports, AIArtRecipe, Toshiaki Wiki, HF discussions, creator reports and community evidence as hypothesis/failure sources, not canonical truth.

### Product adoption
Knowledge evidence is input. Current product behavior is owned by product/DEV routing and `PRODUCT_GOAL_LOCK.md`, not by the mere existence of a claim.

## Identity layers that must stay separate

1. canonical tag identity
2. Alias identity
3. implication/hierarchy
4. related/co-occurrence/semantic-near concept
5. model-specific trigger surface
6. generation support
7. UI Japanese/search wording
8. evaluator representation
9. Prompt-only capability
10. assisted-control/postprocess capability
11. product/runtime adoption

## Author guidance is not production optimum

Example:
- `WAI v17 author recommends Steps 15–30` can be `SOURCE_CLASS=AUTHOR_GUIDE`, `STATUS=ACCEPTED`, `SCOPE=MODEL_VERSION:WAI-v17`.
- `Steps 25 is the hard-target optimum` is a different project-performance claim and remains `CANDIDATE/HOLD` until controlled evidence exists.
- `Steps 25 is the current local isolation baseline` can be `PROJECT_FACT/ACCEPTED` without claiming optimality.

## Durable authority rules

- Alias can establish semantic identity within its source system; implication does not mean synonym.
- A model-preferring an old/alternate spelling does not authorize canonical rewrite.
- Current Danbooru post_count is not direct training-exposure probability.
- Generation success does not redefine canonical meaning.
- A practical Prompt bundle may reveal support hypotheses but is not the definition of the Special.
- Official-source truth and production-optimum truth are separate claims.
- Future generation research does not become a v1 requirement solely because evidence exists.

## Primary originals

Current product authority lives on main in `docs/PRODUCT_GOAL_LOCK.md` and project routing docs.

Historical/research context:
- `../CURRENT_PRODUCT_GOAL_20260909.md`
- `../PRODUCT_GOAL_EVOLUTION_20260909.md`
- `../KNOWLEDGE_REASSESSMENT_20260909.md`
- `../research/SOURCE_AUTHORITY_MATRIX_20260909.md`
- `../research/DANBOORU_WIKI_SEMANTIC_AUDIT_20260909.md`
- `../research/E621_WIKI_SEMANTIC_TRIGGER_AUDIT_20260909.md`
- `../research/HF_MODEL_DISCUSSIONS_AUDIT_20260909.md`
