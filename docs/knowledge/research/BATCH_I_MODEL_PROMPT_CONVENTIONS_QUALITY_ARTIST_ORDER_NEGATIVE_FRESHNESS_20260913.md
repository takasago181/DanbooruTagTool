# Batch I — Model Prompt Conventions: Quality / Artist / Order / Negative / Freshness

Owner: Issue #44 `KNOWLEDGE:#44`
Date: 2026-09-13
Status: `P1_SOURCE_RESEARCH_COMPLETE`

Covers backlog themes:
- K-RB-07 quality / rating / aesthetic / score-like token families
- K-RB-08 artist/style tag and trigger semantics
- K-RB-10 prompt ordering/grouping by exact model family
- K-RB-11 Negative Prompt semantics vs model convention
- K-RB-12 source freshness/model-card recheck

This is KNOWLEDGE evidence only. It does not change runtime/product behavior.

## 1. Core conclusion

Quality-like, score-like, rating/safety, artist, meta, date, and Negative surfaces must be interpreted as **model/version-scoped Prompt conventions unless independent semantic authority says otherwise**.

Do not collapse these into ordinary Danbooru General tags merely because they are comma-separated Prompt tokens.

Particularly important distinctions:

1. Danbooru post metadata/search metatags such as `score:` / `rating:`
2. Danbooru tag categories such as Artist / Meta / General
3. checkpoint-specific learned Prompt surfaces such as `score_7`
4. author-recommended quality prefixes such as `masterpiece, best quality`
5. safety/rating-like Prompt surfaces such as `safe`, `nsfw`, `explicit`
6. exact model artist-trigger conventions such as Anima `@artist`

These may look similar but have different authority and runtime meaning.

## 2. Danbooru authority boundary

Current Danbooru help identifies five tag categories:
- Artist
- Character
- Copyright
- General
- Meta

General tags objectively describe image contents; Meta tags generally describe information beyond image content.

Danbooru also exposes `score:` and `rating:` as **search metatags/post metadata**, not ordinary content-tag identity. `highres` / `absurdres` are site-side automatically-derived resolution tags.

Therefore:

- Danbooru `score:100` is not the same semantic object as an image-generation token `score_7`.
- Danbooru rating/search metadata must not be treated as proof that a checkpoint's `safe/nsfw/explicit` Prompt surfaces use identical semantics.
- `highres` / `absurdres` can have Danbooru site semantics and also be learned Prompt surfaces in a model; those are separate claims.

Primary sources checked 2026-09-13:
- https://safebooru.donmai.us/wiki_pages/help%3Atags
- https://safebooru.donmai.us/wiki_pages/help%3Aposts
- https://safebooru.donmai.us/wiki_pages/help%3Aautotags
- https://safebooru.donmai.us/wiki_pages/help%3Anumber_syntax

## 3. WAI Illustrious v17

Current official/author card checked:
- https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md

Author guidance currently states:
- positive baseline: `masterpiece, best quality, amazing quality`
- Negative baseline: `bad quality, worst quality, worst detail, sketch, censor`
- safety-rating Prompt surfaces: `general`, `sensitive`, `nsfw`, `explicit`
- author recommends adding `nsfw` to Negative when filtering inappropriate content

Interpretation rule:
- these are accepted **WAI17 author Prompt conventions**;
- do not reinterpret them as canonical Danbooru semantic identity;
- the card does not establish a universal Prompt ordering grammar for WAI/Illustrious descendants;
- exact effect size or necessity is a generation-effectiveness question and remains separate from author guidance.

## 4. Illustrious XL early/base

Current official model card checked:
- https://huggingface.co/OnomaAIResearch/Illustrious-xl-early-release-v0/blob/main/README.md

The base card explicitly supports quality surfaces:
- `worst quality`
- `bad quality`
- `average quality`
- `good quality`
- `best quality`
- `masterpiece (quality)`

It also warns against stacking conflicting composition tags and states the base model has no default style.

Interpretation rule:
- quality surfaces are family/model Prompt vocabulary;
- absence of a default style in the base is not evidence that artist/style Prompt effects do not exist in derivatives;
- no universal tag-order rule should be invented from example Prompts.

## 5. NoobAI XL 1.1 EPS / V-Pred

Current cards checked:
- https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- https://huggingface.co/Laxhar/noobai-XL-Vpred-1.0/blob/main/README.md

Both document a structured caption order:
`count -> character -> series -> artists -> special -> general -> other`

Both recommend a prefix including:
`masterpiece, best quality, newest, absurdres, highres, safe`

and a model-family Negative recipe containing quality/date/resolution/artifact/anatomy surfaces.

Quality labels are not simply Danbooru post score copied verbatim. The model card describes a project-defined popularity/recency ranking process that maps percentile bands to:
- masterpiece
- best quality
- good quality
- normal quality
- worst quality

Interpretation rule:
- NoobAI quality tags are exact-model training/Prompt convention evidence;
- the documented caption order is strong exact-model structural evidence;
- EPS and V-Pred inference regimes remain separate even where Prompt conventions overlap;
- these conventions must not be promoted to WAI/Anima universal grammar.

## 6. Anima

Current author card checked:
- https://huggingface.co/circlestone-labs/Anima/blob/main/README.md

Current documented order:
`[quality/meta/year/safety] [count] [character] [series] [artist] [general]`

Current quality systems are explicitly separated:
- human-score-style labels: `masterpiece` through `worst quality`
- PonyV7-derived aesthetic labels: `score_9` through `score_1`

Current recommended base-style prefix includes:
`masterpiece, best quality, score_7, safe`

Anima-Aesthetic is a critical exception:
- trained only on high-quality images with quality tags stripped from captions;
- positive quality tags are not required;
- author specifically recommends avoiding `score_*` in positive and Negative for Aesthetic because they can push output too hard.

Artist convention:
- current card says artist tags should be prefixed with `@`;
- without `@`, author states effect is much weaker.

Interpretation rule:
- `@artist` is a model-trigger surface, not a rewrite of Danbooru Artist canonical identity;
- `score_7` is an Anima/Pony-derived learned Prompt convention, not Danbooru `score:` metadata;
- Base/Aesthetic/Turbo profile scope remains mandatory.

## 7. Artist / style boundary

Keep at least four concepts separate:

1. **Danbooru Artist identity** — who created a source artwork.
2. **Model artist trigger** — a token/surface learned by a checkpoint to steer style/content.
3. **Style description** — generic visual wording such as watercolor/painterly/cinematic.
4. **Style LoRA/adapter** — external learned weights with their own trigger/weight/base compatibility.

A Danbooru Artist tag does not semantically mean "apply this style". Image-generation checkpoints may nevertheless learn it as a style/content trigger. That is model behavior, not a change in Danbooru meaning.

Anima gives exact evidence of this split because the model requires an `@` artist surface although Danbooru canonical artist identity itself is not `@`-prefixed.

## 8. Prompt ordering evidence

Current exact evidence:
- NoobAI: documented caption order exists.
- Anima: documented grouping/order exists; within each section arbitrary order is allowed.
- WAI17: current card gives settings/quality/safety guidance but no comparable universal full Prompt order grammar.
- Illustrious early/base: current card gives composition guidance and quality vocabulary but no comparable universal full Prompt order grammar.

Therefore the safe project rule is:

> Prompt ordering/grouping must remain exact-model evidence. Do not invent a universal `quality -> count -> character -> ...` grammar across all models.

## 9. Negative Prompt: semantic intervention vs author recipe

Two layers must remain separate.

### Layer A — semantic principle

Negative conditioning can suppress intended concepts when overlapping target meaning. This project already treats Negative as an active semantic intervention.

### Layer B — exact-model recipe

Model authors may recommend baselines such as:
- WAI17: short quality/artifact Negative
- NoobAI: quality/date/resolution/artifact/anatomy/nonhuman exclusions
- Anima: quality/score/artifact/artist-name negatives, with Aesthetic-specific warning against score_* use
- Illustrious early/base examples: quality/comic/lowres/anatomy/artifact surfaces

These are **not interchangeable universal defaults**.

For beginner Prompt explanation, identify such tokens as `negative/model-convention` or `negative/semantic` where possible, without claiming the recipe is optimal.

## 10. Freshness recheck result — 2026-09-13

Rechecked current primary/public sources:
- WAI17 Hugging Face author card — reachable/current
- Illustrious early/base official card — reachable/current
- NoobAI XL 1.1 EPS card — reachable/current
- NoobAI XL V-Pred 1.0 card — reachable/current
- Anima author card — reachable/current
- Danbooru Help:Tags / Posts / Autotags — reachable/current
- Forge Neo public upstream `gi0baro/forge-neo` — reachable/current; describes Neo as continuation of Forge and notes most A1111 base features should still function

Forge Neo upstream current source checked:
- https://github.com/gi0baro/forge-neo

Important limitation:
- this recheck confirms public upstream/current documentation only;
- it does not pin the user's exact local Forge Neo remote/commit or installed extension versions;
- local identity HOLD remains until locally captured.

## 11. Durable conclusions ready for Claim review

Candidates for ACCEPTED project knowledge:

1. Danbooru `score:`/`rating:` metadata and model `score_*`/safety surfaces are separate layers.
2. Quality/rating/safety surfaces must be model/version scoped.
3. NoobAI and Anima have documented grouping/order; WAI17/Illustrious do not justify copying those exact orders as universal rules.
4. Danbooru Artist identity and model artist/style trigger are separate concepts.
5. Negative author recipes are exact-model guidance, not universal semantic truth.
6. Anima-Aesthetic is an explicit profile exception for quality/score handling.

No image A/B is needed to accept these narrow source/documentation facts. Image testing is needed only for claims about relative effectiveness or optimality.
