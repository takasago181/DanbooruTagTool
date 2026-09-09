# Hugging Face Model Cards / Discussions Audit — WAI, NoobAI, Anima

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-09

Status: `AUTHORITATIVE_SOURCE_PASS_V1`

## Purpose

モデル作者公式カードとHugging Face Discussionsを分離して監査し、DanbooruTagToolが model-family knowledge を誤って一般化しないためのルールを固定する。

Core rule:

**Model card / author statement > community discussion. Discussion is valuable for failure-mode discovery, not automatic FACT.**

---

## 1. WAI Illustrious v17

### Exact author facts

Source: `LyliaEngine/waiIllustriousSDXL_v170` model card.

Current durable facts:
- Steps 15–30
- CFG 5–7
- Euler a
- author discourages too many quality/aesthetic tags
- author discourages overly long Negative Prompt because it can reduce quality / blur
- v17 includes Hires guidance and attempts to improve limb/hand/foot results
- exact model/version identity must be preserved.

### Discussion availability

The HF Discussions page currently contains no substantial project-relevant community corpus comparable to Anima's.

Decision:
- do not invent WAI relation/binding conclusions from absent discussions;
- exact hard relation/body-site/topology behavior remains `IMAGE_TEST_REQUIRED`;
- use external practical sources only as lower-rank hypotheses.

---

## 2. NoobAI XL 1.1 EPS

### Exact author facts

Source: `Laxhar/noobai-XL-1.1` model card.

- trained on latest/full Danbooru plus e621 2024 dataset with native tag captions;
- recommended CFG 5–6;
- steps 25–30;
- Euler a;
- ~1MP SDXL resolutions;
- caption structure:
  `count -> character -> series -> artist -> special tags -> general tags -> other tags`;
- quality/date tags are explicitly defined;
- model is SDXL/CLIP-based, not an NL-first Qwen-style encoder.

### Important training-cutoff nuance

The v1.0 model card states Danbooru data approximately before 2024-10-23; v1.1 is fine-tuned from v1.0 and uses the latest/full dataset wording.

Decision:
- exact tag exposure date for every current Special remains unresolved;
- current alias/rename must not be assumed present during training;
- e621 alternate vocabulary is plausible but still test-required.

### Discussion availability

The public Discussions page currently exposes little/no substantive prompt-relation corpus.

Decision:
- do not fill relation/body-site/camera rules from memory/community folklore;
- `Special before General` is exact structural evidence because it is in the official card;
- actor-target binding, canonical-vs-alias response, rare trigger preference remain `TEST_REQUIRED`.

---

## 3. Anima — exact author source

Source: `circlestone-labs/Anima` model card.

### Exact author facts

- trained on Danbooru-style tags, natural-language captions, and combinations;
- tags use lowercase and spaces rather than underscores (score tags excepted);
- prefer Gelbooru version when Danbooru/Gelbooru tag surfaces differ;
- prompt weighting works but may need larger weights than typical SDXL examples;
- random tag dropout means every relevant tag need not be included;
- pure natural language should be descriptive rather than extremely short;
- mixed tag + natural language is supported in arbitrary order;
- naming a character plus basic appearance is especially important for multiple characters;
- Base / Aesthetic / Turbo prompting/inference assumptions differ.

This is stronger than general Illustrious community lore.

---

## 4. Anima Discussions — high-value practical failure modes

Discussion evidence class by default:
`PRACTICAL / COMMUNITY_ON_OFFICIAL_HOST`

### #93 — multiple characters

Users report some character pairs work with names alone, some require extra description, some remain unreliable.

Adopted lesson:
- multi-character success is combination-dependent;
- single-character activation does not prove pairwise compositional success;
- explicit identity/basic appearance is a justified intervention because the model card independently supports it.

Not adopted:
- any universal magic syntax or success rate.

### #120 — separate character attributes

User reports attribute swapping/cross-contamination between two subjects; quoted/grouped phrasing can help in simple cases but breaks again as complexity grows.

Adopted lesson:
- multi-person attribute binding is still a real failure class in Anima;
- noun/attribute presence cannot certify correct ownership.

### #99 — directional prompts

Reported failures include:
- left/right frame vs character-side ambiguity;
- left/right limb action inconsistent across seeds;
- `looking back` prior overriding a more complex spatial relation.

Adopted lesson:
- directional/spatial relation is seed-sensitive and training-prior-sensitive;
- left/right should not be treated as high-reliability semantic control without assisted/controlled tests.

### #140 — tags vs natural language

A user reports tags-only often gives cleaner/sharper structure while long natural language can increase detail but also anatomy issues. Community response suggests keeping NL compact and using tags as structural base.

Decision:
- `PRACTICAL`, not exact author FACT;
- reinforces project `tag anchor + concise factual relation clause` test design;
- rejects the idea that more descriptive prose is always better.

### #154 — Danbooru vs Gelbooru surface

Community example reports a character surface working under Gelbooru naming while Danbooru naming did not.

Decision:
- strengthens the official model-card rule that Gelbooru surface may matter;
- still only a case example, not proof for all tags.

### #96 / #105 / #205 — captioning / LoRA training

Community reports generally favor retaining model-native order and using a mixture of tags/NL for training when applicable.

Decision:
- use as LoRA/caption hypothesis only;
- exact training recipe authority remains model author documentation / controlled local results.

### #202 — multi-character LoRA interference

User reports identity bleed / feature blending / one LoRA overpowering another in multi-LoRA scenes despite structured prompts.

Decision:
- consistent with general personalization interference research;
- strengthens `LoRA state is part of evidence identity`;
- no exact threshold/weight rule is adopted.

### #141 — structured adult relation captions

Community shares explicit structured actor IDs / relation description workflows.

Project use:
- hypothesis for relation decomposition and stable actor IDs;
- **external runtime LLM generation is not adopted** because DanbooruTagTool runtime is non-LLM;
- useful knowledge is the decomposition structure only.

---

## 5. Cross-family conclusions

### Safe to transfer across models

- model/version is part of every claim;
- unary presence != correct relation/binding;
- multi-character complexity can create cross-contamination;
- seed is part of evidence identity;
- LoRA/control/postprocessing must be separated from base Prompt ability;
- historical/current tag surface may differ.

### Not safe to transfer

- WAI Negative to NoobAI/Anima;
- NoobAI caption order to Anima;
- Anima natural-language advantage to WAI/NoobAI;
- Gelbooru-preference rule to every model;
- prompt weighting values;
- exact camera/framing syntax;
- model-specific alternate triggers.

---

## 6. New audit rule: `AUTHOR / HOST / USER` separation

When reading Hugging Face:

### `AUTHOR_CARD`
Official model card / author edit.
Highest model-specific authority.

### `AUTHOR_DISCUSSION_REPLY`
Author/team response in Discussion.
High authority but scope to exact question/version.

### `COMMUNITY_DISCUSSION`
Useful failure-mode/practical evidence.
Requires controlled test or independent support before promotion.

### `MODEL_HOST_ONLY`
The fact that a claim appears on Hugging Face does not make it author-endorsed.

This distinction is mandatory in the knowledge corpus.

---

## 7. Sources

Exact models:
- https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170
- https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- https://huggingface.co/circlestone-labs/Anima

Anima discussions reviewed:
- https://huggingface.co/circlestone-labs/Anima/discussions/93
- https://huggingface.co/circlestone-labs/Anima/discussions/99
- https://huggingface.co/circlestone-labs/Anima/discussions/120
- https://huggingface.co/circlestone-labs/Anima/discussions/140
- https://huggingface.co/circlestone-labs/Anima/discussions/141
- https://huggingface.co/circlestone-labs/Anima/discussions/154
- https://huggingface.co/circlestone-labs/Anima/discussions/96
- https://huggingface.co/circlestone-labs/Anima/discussions/105
- https://huggingface.co/circlestone-labs/Anima/discussions/202
- https://huggingface.co/circlestone-labs/Anima/discussions/205

## Final decision

**Use model cards aggressively as exact-family facts. Use Discussions aggressively for failure-mode discovery, but never collapse community posts into author FACT.**
