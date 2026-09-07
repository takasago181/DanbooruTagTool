# Model Auxiliary Full Crossmatch — v2.9 CANONICAL SPEC

This file supersedes every older pt20-first/addendum execution plan.
Source-vocabulary evidence, model-observed recommendation, Special Prompt ownership, statistics and LoRA remain separate layers.

## e621 / NoobAI — FINAL audit source

Use a complete same-date official e621 DB-export pair:
- `tags-YYYY-MM-DD.csv.gz`
- `tag_aliases-YYYY-MM-DD.csv.gz`

FINAL-mode requirements:
1. both files are mandatory
2. filenames must exactly use the canonical patterns above and dates must match
3. record absolute `https://...e621.net/...` provenance URLs
4. provide the published SHA-256 for both exports
5. each SHA must be 64 hex characters and equal the locally computed SHA-256
6. record row counts
7. no date-mismatch, unpinned-source or final-gate override

### e621 matching order

For every one of 2811 normalized input terms:
1. exact non-invalid raw tag
2. otherwise unique active alias whose target exists and is non-invalid
3. invalid exact remains audit-visible but cannot suppress a valid active alias
4. multiple active targets -> ambiguous
5. pending alias -> discovery only
6. deleted/retired alias -> history only
7. unknown alias status -> discovery only
8. category 6 exact/target -> audit-visible only
9. no fuzzy final mapping

A valid exact/active-alias hit may populate `e621_source_candidate_form`.
It must **not** populate `recommended_noob_eps_form` or `recommended_noob_vpred_form` merely from current-source presence. Those recommendation fields require separate exact-model evidence or controlled model tests.

### e621 fallback

Processed `pt20 ia-ed` autocomplete lists are fallback/cross-check only.
- exact hit = provisional source candidate
- no hit = NOT absence proof
- alias-cell hit = discovery only because active/deleted provenance is merged
- no processed hit may establish model familiarity

## Gelbooru / Anima — frozen source

Source: `DraconicDragon/Gelbooru-Tags-Full_2026-06-11`
File: `gelbooru_tags_2026-06-11.parquet`
Expected rows: `1,393,773`
Expected SHA-256: `7329c1e4b4d037e27bd10b90751ba850fa1a42ff43bfc80a96f0bb235aa174cc`

Rules:
1. verify SHA and row count
2. exact normalized tag-name match only
3. category 2 Invalid/Unused -> audit-only
4. category 6 Deprecated -> audit-only
5. `is_ambiguous=true` -> audit-only
6. no alias table in this frozen source; no exact match means do not guess
7. eligible exact presence may populate `anima_gelbooru_source_candidate_form`
8. current Gelbooru presence never by itself populates `anima_recommended_form`

## Required outputs

- `e621_source_form_audit.csv`
- `gelbooru_source_form_audit.csv`
- `model_aux_cross_source_audit.csv`
- `model_aux_crossmatch_summary.json`

Each source audit must contain exactly 2811 rows or stop with explicit retrieval/verification failure.
Model-aux never silently replaces the current Special Prompt owner.
