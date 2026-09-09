# Foundations and Authority

## Current product goal

DanbooruTagTool remains Special-first:

`short Japanese/English intent -> correct Special candidate(s) -> minimum useful support/structure -> model-family-appropriate canonical-English Prompt -> safe failure diagnosis -> fewer unnecessary generation iterations`

Runtime remains local and non-LLM. KNOWLEDGE is evidence/reference and does not directly rewrite production dictionary data or another team's verdict.

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

They remain valid historical shorthand in those files. They do **not** replace the current two-axis-plus-scope/validation fields.

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

## Primary originals

- `../CURRENT_PRODUCT_GOAL_20260909.md`
- `../PRODUCT_GOAL_EVOLUTION_20260909.md`
- `../KNOWLEDGE_REASSESSMENT_20260909.md`
- `../research/SOURCE_AUTHORITY_MATRIX_20260909.md`
- `../research/DANBOORU_WIKI_SEMANTIC_AUDIT_20260909.md`
- `../research/E621_WIKI_SEMANTIC_TRIGGER_AUDIT_20260909.md`
- `../research/HF_MODEL_DISCUSSIONS_AUDIT_20260909.md`
