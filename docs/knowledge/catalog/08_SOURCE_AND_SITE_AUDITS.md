# 08 — Source Authority / Site Audits

## Rule

Do not trust a site as one block. Assign authority by claim type.

### Canonical meaning
1. current Danbooru Wiki
2. active Alias / Implication records
3. project canonical data

### Exact model behavior
1. exact model author card
2. author statement/reply
3. controlled exact-model practical evidence

### Tool behavior
1. official README/docs
2. official issues/version-specific reports

### General mechanism
1. primary papers/research
2. controlled studies

### Practical failure discovery
- AIArtRecipe
- としあきdiffusion Wiki
- Civitai/Tensor.Art creator reports
- Hugging Face community discussions
- Reddit/general community

These are hypothesis/failure sources, not canonical truth.

## AIArtRecipe

Decision:
`ADOPT AS PRACTICAL OBSERVATION CORPUS / REJECT AS CANONICAL AUTHORITY`

High value:
- niche/adult generation failure examples
- wrong-site / wrong-source / wrong-count
- practical WAI/Illustrious/Anima behavior

Risks:
- canonical/Alias/free phrase/typo mixed
- model version/seed/sample counts often incomplete
- typo-driven false conclusions found

Originals:
- `../research/AIARTRECIPE_SITE_AUDIT_20260909.md`
- `../research/AIARTRECIPE_PRACTICAL_FINDINGS_20260909.md`

## としあきdiffusion Wiki

Decision:
`ADOPT AS JAPANESE COMMUNITY PRACTICAL / OPERATIONS CORPUS`

High value:
- Forge Neo / ComfyUI / Prompt / Negative / Hires / Control / LoRA / troubleshooting
- Japanese practical failure knowledge

Risks:
- 2022–2023 legacy and 2026 current guidance coexist
- community heuristic and exact author fact can mix
- old universal Negative guidance must not override WAI17 exact author guidance

Originals:
- `../research/TOSHIAKI_WIKI_SITE_AUDIT_20260909.md`
- `../research/TOSHIAKI_WIKI_PRACTICAL_FINDINGS_20260909.md`
- `../research/TOSHIAKI_WIKI_COVERAGE_MAP_20260909.md`

## Hugging Face

Model card / author statement > author discussion reply > community discussion.

- WAI17: exact settings / short quality+Negative / Hires
- NoobAI: corpus / caption order / inference regime
- Anima: tag+NL / formatting / tag dropout / Gelbooru / multi-character

Community discussions are strong failure-discovery evidence but not automatic success-rate FACT.

Original: `../research/HF_MODEL_DISCUSSIONS_AUDIT_20260909.md`

## Danbooru / e621

- Danbooru = primary Danbooru semantic identity source
- e621 = secondary vocabulary/training-surface source, especially relevant to NoobAI
- e621 never silently overwrites Danbooru canonical identity

Originals:
- `../research/DANBOORU_WIKI_SEMANTIC_AUDIT_20260909.md`
- `../research/E621_WIKI_SEMANTIC_TRIGGER_AUDIT_20260909.md`

## Multilingual rule

Language is not evidence rank. Japanese, English, Chinese, Korean and other useful sources are judged by authority, version match and experimental control.

## Full authority matrix

`../research/SOURCE_AUTHORITY_MATRIX_20260909.md`