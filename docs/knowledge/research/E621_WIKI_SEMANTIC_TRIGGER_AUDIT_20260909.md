# e621 Wiki — Semantic / Alternate-Trigger / Nonhuman Coverage Audit

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-09

Status: `AUTHORITATIVE_SOURCE_PASS_V1`

## Purpose

NoobAI XL 1.1 / V-Pred が Danbooru だけでなく e621 データも学習しているため、e621 Wiki を DanbooruTagTool の生成知識にどう使うかを固定する。

結論:

**e621 Wiki is a high-value secondary semantic and vocabulary source for nonhuman / anatomy / fetish / relation concepts, but it is not allowed to overwrite Danbooru canonical identity.**

Use it for:
- alternate trigger / training-surface hypotheses;
- concept decomposition;
- nonhuman/anatomy vocabulary;
- relation/topology distinctions;
- NoobAI exposure reasoning.

Do not use it to silently replace a Danbooru canonical tag.

---

## 1. Site semantics and tagging philosophy

e621 has a large structured tag vocabulary and explicit alias/implication systems. Its API exposes tags, tag aliases, tag implications and wiki pages as distinct resources.

The site is strongly `Tag What You See` oriented for general/species tags.

Project implication:
- e621 wiki semantics are primarily visual-index semantics;
- its fine granularity can improve generation decomposition;
- creator lore/intention and visible anatomy may be represented in different tag categories, reinforcing the need to separate visual semantics from identity/lore.

---

## 2. Alias / implication lessons

Like Danbooru:
- Alias = alternate/preferred surface for the same indexed concept.
- Implication = a broader/always-also semantic relationship, not synonymy.

The e621 ecosystem also uses bulk update requests and forum discussion before many tag relationship changes.

Project rule:
- only active/approved alias relations are identity-equivalence evidence;
- pending/rejected forum proposals are hypothesis/history, never canonical truth;
- e621 alias may be an alternate NoobAI trigger hypothesis even when Danbooru uses a different canonical surface.

---

## 3. Why e621 matters specifically to NoobAI

NoobAI XL 1.1 author states the model was trained using full/latest Danbooru plus an `e621-2024-webp-4Mpixel` dataset with native tag captions.

Therefore e621 vocabulary is not merely external community knowledge: it is a plausible direct training-surface source for NoobAI.

But this does **not** prove:
- every current e621 tag existed before cutoff;
- every tag had sufficient frequency;
- every current wiki meaning matches 2024 training semantics;
- an e621 surface is stronger than Danbooru surface for a particular concept.

Exact trigger preference remains controlled-test territory.

---

## 4. High-value semantic areas

### Nonhuman / alternate anatomy

e621's tag groups place strong emphasis on:
- anatomy / feral anatomy;
- species and body-form distinctions;
- appendages;
- unusual genital/anatomical variants;
- transformation;
- size difference;
- nonhuman interactions.

Project use:
- identify decomposable visual primitives for Semantic/rare Special;
- detect where Danbooru-centric anatomy assumptions are incomplete;
- test NoobAI alternate surface where Danbooru trigger is rare or renamed.

### BDSM / bondage topology

Example `bound together` explicitly means two or more characters physically bound to each other, including single/multiple connection points, sometimes with devices/machines. `tied_together` is an Alias; tag implicates `bound`.

Project implication:
- restraint topology can be semantically richer than generic `bondage` or `rope` presence;
- actor-to-actor connectivity is an intrinsic predicate for such concepts.

### `chastity cage`

Aliases include surfaces such as `cock_cage` / `penis_cage`; it implicates broader `chastity_device`.

Project implication:
- e621 may preserve colloquial/legacy trigger surfaces that a NoobAI training set could have seen;
- Alias surfaces are useful alternate-trigger candidates, not new canonical meanings.

### `wartenberg wheel`

Wiki distinguishes the medical instrument from unrelated `pinwheel`, and notes BDSM use.

Project implication:
- object identity and use-context must be separated;
- ordinary-object detector success does not prove BDSM relation.

### Anal / living-insertion vocabulary

`anal vore` illustrates how e621 decomposes:
- anal body-site;
- swallowed/consumed role;
- living insertion;
- size relation;
- specific action variants.

The page explicitly notes that anal penetration may occur without `sex`.

Project implication:
- NoobAI's e621 exposure may support niche relation primitives beyond Danbooru's most common surfaces;
- body-site/action/intention remain separate.

### Pose / participant structure

`tag group:pose` explicitly organizes by participant count and separates static pose from sexual positions; examples include `doggystyle`, `from_behind_position`, `straddling`, `spitroast`, etc.

Project implication:
- exact participant count is structurally important;
- pose and sex-act relation should not be flattened into one label.

---

## 5. High-value distinction: visible semantics vs lore

e621 lore tags explicitly coexist with `Tag What You See`; e.g., gender lore does not replace visible gender tagging.

Durable project lesson:

**A dataset may encode multiple semantic layers for one character/image.**

For generation knowledge:
- visible body state;
- character/canonical identity;
- lore;
- action/relation;
- style/context

must not be assumed to collapse into one trigger.

This strengthens the existing DanbooruTagTool separation between canonical identity, UI wording, generation trigger and support.

---

## 6. e621 as alternate-trigger source

For NoobAI only, an e621-derived surface may be promoted to `ALTERNATE_TRIGGER_CANDIDATE` when:
1. exact concept is in current e621 wiki/tag system;
2. semantics are compatible with target Special;
3. surface plausibly existed by the model's training period;
4. Danbooru canonical surface is rare/renamed/Semantic/weak;
5. image A/B confirms benefit without semantic drift.

It must never automatically become:
- Danbooru canonical name;
- Japanese display meaning;
- universal model-family trigger;
- mandatory support.

---

## 7. Risk flags

### `VOCABULARY_DIVERGENCE`
Same concept has different preferred Danbooru/e621 surfaces.

### `SEMANTIC_SCOPE_DIVERGENCE`
Same English phrase is applied with different scope.

### `TRAINING_CUTOFF_DRIFT`
Current e621 tag/alias may postdate NoobAI's dataset.

### `NONHUMAN_PRIOR`
e621 surface may carry furry/feral/species context into anime-human generations.

### `LIVING_INSERTION_OR_SIZE_PRIOR`
Niche e621 relation tags may import macro/micro/nonhuman priors.

### `LORE_VISUAL_MISMATCH`
Lore tag semantics are not equivalent to visible-image semantics.

### `ALIAS_HISTORY_DRIFT`
Old alias surface may be model-useful while current canonical identity differs.

---

## 8. Audit protocol for NoobAI Special

When a target is rare/complex:
1. resolve Danbooru canonical meaning first;
2. inspect Danbooru Alias/implications;
3. inspect e621 exact/near concepts;
4. classify e621 surface as exact-semantic / broader / narrower / related;
5. estimate cutoff plausibility;
6. keep current Danbooru canonical unchanged;
7. A/B Danbooru surface vs e621 alternate on same seeds if justified;
8. score target semantics and collateral furry/nonhuman/context bleed separately.

---

## 9. Sources

Primary e621 pages consulted:
- https://e621.net/wiki_pages/e621%3Aforum
- https://e621.net/wiki_pages/1671 (`tag group:index`)
- https://e621.net/wiki_pages/11632 (`bound together`)
- https://e621.net/wiki_pages/chastity_cage
- https://e621.net/wiki_pages/anal_vore
- https://e621.net/wiki_pages/4612 (`tag group:pose`)
- https://e621.net/wiki_pages/46487 (`wartenberg wheel`)
- https://e621.net/wiki_pages/33001 (`trans (lore)`; used only for visible-vs-lore semantic-layer lesson)

API surface reference:
- https://e621.wiki/

NoobAI exact-model source:
- https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md

## Final decision

**e621 is a high-value secondary semantic + trigger-history source, especially for NoobAI and nonhuman/niche concepts. Danbooru remains canonical authority for DanbooruTagTool identities.**
