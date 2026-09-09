# Stage10 PROMPT official model source matrix

最終更新: 2026-09-09  
Owner: PROMPT / Issue #5  
Status: official-source ledger. **Not production specification.**

## 1. Anima

Source: https://huggingface.co/circlestone-labs/Anima
Evidence: `OFFICIAL_FACT`

Confirmed:
- trained on Danbooru-style tags, natural-language captions, and combinations of both
- use lowercase tags and spaces instead of underscores, except score tags
- recommended positive/negative examples are provided
- tag order: `[quality/meta/year/safety] [count] [character] [series] [artist] [general tags]`
- tag order inside each section can be arbitrary
- prompt weighting works; official example uses stronger weight than typical SDXL
- Aesthetic version can omit positive quality tags; score_* overuse can push output in an undesirable/slop direction
- natural-language prompting: descriptive is better; pure NL should be more than a tiny phrase
- tags and natural language may be mixed
- multiple characters: character name plus basic appearance is especially important
- short/under-detailed prompts can produce undesired content

PROMPT implications:
- use `HYBRID_RELATION_AWARE` as a Stage10 hypothesis, not a production fact
- test tag-only vs tag + short relation sentence
- test appearance anchors for multiple actors
- Base/Aesthetic/Turbo/derivatives must not be collapsed

## 2. NoobAI XL 1.1

Source: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
Evidence: `OFFICIAL_FACT`

Confirmed:
- based on Illustrious-xl
- trained with latest full Danbooru and e621 datasets at the stated training period
- native tags caption
- CFG 5–6 / Steps 25–30 / Euler a / ~1024² area recommendations
- caption order: `<count>, <character>, <series>, <artists>, <special tags>, <general tags>, <other tags>`
- quality and date tags are explicitly defined
- official prompt prefix and negative examples exist

PROMPT implications:
- preserve `SPECIAL_BEFORE_GENERAL` as a strong caption-structure baseline
- do not mechanically inherit the official `safe` positive or `nsfw` negative into adult hard-target tests; treat safety tags as experiment context
- e621 presence supports investigation of non-human taxonomy, but does not prove superior hard-target generation
- canonical vs alias/model-trigger response remains Stage10 evidence question

## 3. Illustrious XL

Sources:
- https://huggingface.co/OnomaAIResearch/Illustrious-XL-v1.1
- https://www.illustrious-xl.ai/
Evidence: `OFFICIAL_FACT`

Confirmed:
- v1.1 is explicitly described as more natural-language focused than v1.0
- official platform emphasizes natural-language prompting, high-resolution generation, custom presets and prompt enhancers
- official platform now exposes multiple model generations/tiers, including later v2/v3 series

PROMPT implications:
- `Illustrious = booru-only` is obsolete as a universal statement
- version must be retained in every prompt claim
- Illustrious base behavior must not be collapsed with WAI-derived checkpoints
- current DanbooruTagTool Stage10 scope should test the exact target checkpoint rather than extrapolate from the latest official web platform

## 4. WAI Illustrious v17

Source lane:
- author-linked Civitai page when accessible
- trusted Hugging Face mirrors carrying WAI0731 instructions
Evidence: `AUTHOR_GUIDE / PRIMARY_RECHECK_DESIRED`

Known author guidance preserved in existing PROMPT corpus:
- Steps 15–30
- CFG 5–7
- Euler a
- original size around/above 1024² family
- positive quality example: `masterpiece, best quality, amazing quality`
- negative example includes quality/censor terms
- warning against excessive quality/aesthetic tags
- warning that overly long negative can reduce quality / increase blur

PROMPT implications:
- WAI v17 initial hypothesis: `LEAN_TAG_FIRST`
- generic long-negative templates are not safe defaults
- quality tag count must not be used as a proxy for image quality
- exact author primary source should be rechecked before final production promotion

## 5. Cross-family do-not-merge list

Do not merge into one universal grammar:
- caption order
- natural-language reliance
- count syntax
- artist tag syntax
- score/quality/meta behavior
- negative length/profile
- recommended weighting
- model-specific safety tags

## 6. Stage10 test priorities derived from official sources

1. family-specific baseline vs generic shared baseline
2. tag-only vs hybrid relation support
3. special placement/order where family evidence exists
4. minimum vs expanded quality/meta
5. minimum vs long negative
6. appearance anchor for multi-actor
7. canonical vs alias/alternate trigger
8. Base/Aesthetic/Turbo/derivative separation for Anima

## Boundary

Official recommendations are strongest baselines, not proof of globally optimal prompts. All hard-target production rules still require Stage10 evidence.