# Model-Aux Source Policy v2.9

`13_MODEL_AUX_FULL_CROSSMATCH_SPEC.md` is canonical.

- FINAL e621 source audit = official same-date raw `tags` + `tag_aliases`.
- Final gate verifies canonical filenames, e621.net provenance URLs, published SHA-256 and local hash equality.
- pt20 ia-ed is fallback/discovery only.
- valid exact / unique valid active alias may populate **source candidate** only.
- pending/deleted/retired/unknown/ambiguous aliases never become source candidates or model recommendations.
- category 6 is invalid; invalid exact evidence cannot suppress a valid active alias.
- Gelbooru frozen 2026-06-11 remains SHA/row pinned; category 2/6 and ambiguous rows are audit-only.
- e621/Gelbooru presence is source-vocabulary evidence, never automatic MODEL_OBSERVED or model recommendation.
- Prompt owner / alias / statistics / semantic routing / source form / model recommendation / Practical / LoRA are separate roles.
