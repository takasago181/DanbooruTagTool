# 00 — Foundations and Authority

## Current product goal

DanbooruTagTool remains Special-first. Current success criterion is broader than the original search/dictionary goal:

`short Japanese/English intent -> correct Special candidate(s) -> minimum useful support/structure -> model-family-appropriate canonical-English Prompt -> safe failure diagnosis -> fewer unnecessary generation iterations`

The runtime remains local and non-LLM. KNOWLEDGE is evidence/reference and does not directly rewrite production dictionary data or another team's verdict.

## Evidence classes

- `FACT_EXACT_MODEL` — exact model/version author evidence or equally strong exact-version controlled evidence
- `FACT_GENERAL` — primary/general mechanism evidence
- `CONTROLLED_PRACTICAL` — controlled practical comparison
- `PRACTICAL` — useful but less controlled real-world evidence
- `COMMUNITY` — hypothesis/failure-discovery evidence
- `HOLD / TEST_REQUIRED / IMAGE_TEST_REQUIRED` — unresolved, conflicting, or test-required
- `REJECT` — contradicted/overgeneralized/unsafe as a default

Language does not determine rank. Japanese, English, Chinese, Korean and other sources are valid when evidence quality is high.

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
Use controlled/practical reports, AIArtRecipe, Toshiaki Wiki, HF discussions, creator reports and community evidence — but do not promote them into canonical truth without independent support.

## Identity layers that must stay separate

1. canonical tag identity
2. Alias identity
3. implication/hierarchy
4. related/co-occurrence/semantic-near concept
5. model-specific trigger surface
6. generation support
7. UI Japanese/search wording
8. evaluator representation

## Durable authority rules

- Alias can establish semantic identity within its source system; implication does not mean synonym.
- A model-preferring an old/alternate spelling does not authorize canonical rewrite.
- Current Danbooru post_count is not direct training-exposure probability.
- Generation success does not redefine canonical meaning.
- A practical Prompt bundle may reveal useful support hypotheses but is not the definition of the Special.
- Prompt-only, LoRA/control-assisted, and postprocess-rescued outputs are separate evidence lanes.
- Unknown behavior stays HOLD rather than being filled with another family/version's habits.

## Primary originals

- `../CURRENT_PRODUCT_GOAL_20260909.md`
- `../PRODUCT_GOAL_EVOLUTION_20260909.md`
- `../KNOWLEDGE_REASSESSMENT_20260909.md`
- `../research/SOURCE_AUTHORITY_MATRIX_20260909.md`
- `../research/DANBOORU_WIKI_SEMANTIC_AUDIT_20260909.md`
- `../research/E621_WIKI_SEMANTIC_TRIGGER_AUDIT_20260909.md`
- `../research/HF_MODEL_DISCUSSIONS_AUDIT_20260909.md`