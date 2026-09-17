# BATCH N — Scene intent / discovery / workflow synthesis

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-17

Status: `RESEARCH_SYNTHESIS_COMPLETE / NO_PRODUCT_ADOPTION / USER-WORKFLOW_VALIDATION_OPEN`

## 0. Purpose

This batch audits the current KNOWLEDGE corpus against a concrete missing question:

> When an adult user is building a consensual adult image, what semantic dimensions should be decided, in what human-facing order, and how should that differ from dictionary browse taxonomy and model-specific Prompt serialization?

This is a KNOWLEDGE organization/research task. It does **not** authorize a WPF redesign, General/Special merge, automatic Prompt rewrite, or production taxonomy mutation.

Detailed generation guidance remains limited to clearly adult consensual sexual/BDSM content and adult fantasy. Existing dictionary inventory may contain other boundary categories, but this batch does not turn those into generation recipes.

---

## 1. Audit result — what #44 already knows well

Current #44 is already strong in these areas:

- canonical / Alias / implication / model-trigger separation;
- model/version/profile scoping;
- minimum-sufficient Prompt and anti-support;
- relation/binding failures;
- body-site/count as first-class predicates;
- restraint topology;
- machine/device functional relation;
- tentacle/nonhuman source/ownership relation;
- fluid source/destination/state/quantity;
- Negative collision;
- Prompt-only vs LoRA/control/postprocess evidence separation;
- seed/evaluator/evidence discipline.

Relevant current Claim families:
- `K-GOV-*`
- `K-PROMPT-*`
- `K-SUPPORT-*`
- `K-BIND-*`
- `K-HARD-*`
- `K-NEG-*`
- `K-TOOL-*`
- `K-EVID-*`

### Main gap found

The corpus is much stronger at **diagnosing a difficult generated image** than at describing the **human scene-construction workflow before generation**.

The missing layer is not another fetish taxonomy. It is a reusable scene-planning projection over already accepted semantic predicates.

---

## 2. Five layers that must stay separate

### Layer A — canonical semantic identity

What the tag/concept actually means.

Authority:
- Danbooru Wiki + active Alias/Implication for Danbooru-origin identity;
- existing project canonical rules.

This layer answers:
- what is the concept?
- what is intrinsic to it?
- what is only related/supporting context?

### Layer B — human scene-construction order

The order in which a user can most naturally decide the intended picture.

This is a **planning workflow**, not model grammar and not canonical ontology.

### Layer C — browse/discovery entry path

How a user finds a concept they do not already know.

A user may start from:
- action;
- body site;
- position/pose;
- object/device;
- theme;
- ordinary search.

The entry point does not redefine the tag's semantic home.

### Layer D — model-specific Prompt serialization

How the selected concepts are arranged for a specific model family/profile.

This is model-scoped.

### Layer E — generation diagnosis/evaluation

How to judge whether the output actually satisfies the requested semantic predicates, and how to repair failures.

Do not collapse Layers B/C into D, and do not infer A from generation behavior in E.

---

## 3. Reusable scene semantic skeleton

For adult consensual scenes and other relation-heavy image generation, the existing hard/niche research converges on the following reusable dimensions.

### 3.1 Subjects

- subject count;
- character/person identity;
- visible distinguishing attributes when ownership matters.

### 3.2 Core action or state

What is fundamentally happening or what state is being depicted.

Examples of semantic classes:
- action/contact;
- body state;
- restraint state;
- device-mediated action;
- nonhuman-appendage relation;
- fluid/material state.

### 3.3 Relation / role / ownership

- actor;
- target/receiver;
- owner/source;
- which subject a body part/device/appendage belongs to;
- role when intrinsic.

This is separate from mere component presence.

### 3.4 Target / body site

Exact body site is a first-class predicate when intrinsic.

Body-site selection is cross-cutting: the same site may be relevant to an action, state, object, device, restraint, fluid or nonhuman relation.

### 3.5 Geometry / position / topology

- pose/position;
- relative orientation;
- restraint connectivity;
- device alignment/contact geometry;
- simultaneous relation geometry.

This must stay separate from camera/viewpoint.

### 3.6 Implement / device / appendage

What performs or mediates the action:
- body part;
- object/toy;
- restraint device;
- machine/actuator;
- nonhuman appendage.

Object presence alone does not prove functional relation.

### 3.7 State / timing / count / source-destination

Use when intrinsic:
- exact count;
- simultaneous vs sequential;
- imminent/current/post-action state;
- source;
- destination;
- quantity/state of material/fluid.

### 3.8 Visibility / framing

Whether the requested semantic predicates can actually be seen and judged.

Normally this is an observability/composition support layer, not canonical meaning.

### 3.9 Appearance / clothing / exposure / expression

These refine the subjects and scene but usually should not replace the semantic nucleus.

### 3.10 Setting / background / lighting / style

Scene finishing/context layer unless the setting or style is itself the requested target.

---

## 4. Default human construction order

A useful default order, derived from the current semantic predicates rather than from one model's tokenizer/caption grammar, is:

1. **subjects / count / identities**
2. **core action or state**
3. **relation / role / ownership**
4. **target body site**
5. **position / geometry / topology**
6. **implement / device / appendage**
7. **state / timing / exact count / source-destination**
8. **visibility / camera / framing**
9. **appearance / clothing / exposure / expression**
10. **setting / lighting / style**

### Important limitation

This is a **default planning sequence**, not a mandatory wizard and not an accepted universal UX optimum.

The optimal first click depends on user intent. Someone may start from a body site, tool, position or theme. The product should not require users to restate their intention in an ontology-first order merely to browse.

---

## 5. Adaptive entry principle

A better discovery model is:

> enter from any strong intent -> preserve that selection -> surface the most informative missing dimensions next.

Examples of next-dimension priorities:

### Insertion/body-site intent

`site -> action/state -> implement -> actor/target -> count/timing -> visibility`

### BDSM/restraint intent

`theme or target restraint -> role -> device -> body site -> topology/pose -> visibility`

### Machine/device intent

`device -> target subject -> body site -> functional relation -> geometry -> count/visibility`

### Tentacle/nonhuman intent

`source/ownership -> target -> body site -> relation -> appendage role -> count/density -> visibility`

### Fluid/material intent

`material -> source -> destination -> state/timing -> quantity -> actor/target -> visibility`

These are semantic completion routes, not mandatory Prompt token order.

---

## 6. Evidence from current tag ecosystems

### Danbooru

The current Danbooru tagging checklist separates explicit content into distinct discovery concerns including:
- body parts;
- sexual actions;
- sexual positions;
- sexual themes;
- sexual objects.

This supports treating these as separate discovery dimensions rather than forcing them into one mutually exclusive genre tree.

Source:
- https://safebooru.donmai.us/wiki_pages/howto%3Atag_checklist
- checked 2026-09-17
- source role: `SEMANTIC/DISCOVERY STRUCTURE`, not Prompt grammar.

Danbooru's group index also routes sex-related discovery separately through sex acts and sexual positions.

Source:
- https://safebooru.donmai.us/wiki_pages/tag_group%3Agroups
- checked 2026-09-17

### e621

The tag-group index explicitly allows one tag to participate in multiple groups, with easy tag accessibility as the stated goal.

Source:
- https://e621.net/wiki_pages/1671
- checked 2026-09-17
- source role: secondary browse-design evidence; never Danbooru canonical authority.

This is compatible with the project rule that semantic home and cross-cutting discovery routes should not be forced into one axis.

---

## 7. Evidence from compositional-generation research

### T2I-CompBench

The benchmark separates:
- attribute binding;
- spatial relationships;
- non-spatial relationships;
- complex composition.

This reinforces the project's existing rule that component presence and relation correctness are different problems.

Source:
- https://arxiv.org/abs/2307.06350

### ConceptMix

ConceptMix varies the number of requested concepts and reports marked performance degradation as compositional load increases, especially for open models.

Project consequence:
- do not treat scene construction as a flat pile of independent tags;
- preserve a semantic nucleus;
- add optional refinement/support only after core constraints are coherent.

Source:
- https://arxiv.org/abs/2408.14339

### Current 2026 compositional research

Recent iterative-refinement research continues to report difficulty with prompts containing multiple simultaneous objects, relations and attributes. This is supporting general evidence only; its VLM-in-the-loop method is not adopted as product runtime behavior.

Source:
- https://arxiv.org/abs/2601.15286
- checked 2026-09-17

---

## 8. Model Prompt order is a different layer

### NoobAI XL 1.1 EPS

Current author card documents native caption order:

`count -> character -> series -> artist -> special -> general -> other`

The model is trained with native Danbooru/e621 tags.

Source:
- https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- rechecked 2026-09-17

Consequence:
- `Special before General` is valid exact-model structural guidance;
- it does **not** mean the user's browse UI must ask for Special before every General concept.

### Anima official family

Current author card documents:

`quality/meta/year/safety -> count -> character -> series -> artist -> general`

and says:
- tags inside each section can be in arbitrary order;
- tags and natural language can be mixed;
- multiple characters benefit from naming each character and describing basic appearance.

Source:
- https://huggingface.co/circlestone-labs/Anima/blob/main/README.md
- rechecked 2026-09-17

Consequence:
- Anima and NoobAI already demonstrate that one universal model-output ordering rule is inappropriate;
- human scene-planning order should remain separate from model-specific serialization.

### Illustrious early/base

Official guidance warns against overusing multiple critical composition tags such as close-up / upside-down / cowboy shot because they can conflict.

Source:
- https://huggingface.co/OnomaAIResearch/Illustrious-xl-early-release-v0
- rechecked 2026-09-17

This strengthens the existing same-role conflict rule rather than creating a new Prompt grammar.

---

## 9. Assisted-control boundary rechecked

Current Forge Couple supports Forge Neo and Anima, but its README explicitly states that regional conditioning depends on the checkpoint already understanding the composition.

Source:
- https://github.com/Haoming02/sd-forge-couple
- rechecked 2026-09-17

Therefore:
- actor/resource region separation is a valid assisted lane;
- it must not become a substitute for semantic scene planning;
- assisted success still does not prove Prompt-only capability.

Current Forge Neo upstream remains:
- `Haoming02/sd-webui-forge-classic`, branch `neo`;
- current September feature list supports Anima 2B / 2.9B / 3.8B, Anima LLLite and Region ControlNet paths.

Source:
- https://github.com/Haoming02/sd-webui-forge-classic/tree/neo
- rechecked 2026-09-17

This does not promote community 2.9B/3.8B derivatives over the official CircleStone 2B Base/Aesthetic/Turbo project baseline.

---

## 10. Japanese practical-source recheck

The current としあきdiffusion Wiki Anima page remains useful practical evidence for:
- current Base/Aesthetic/Turbo operation;
- Danbooru-tag plus natural-language prompting;
- explicit character descriptions for multi-character scenes;
- Forge Neo operation.

Source:
- https://wikiwiki.jp/sd_toshiaki/Anima
- page last-modified 2026-07-30; rechecked 2026-09-17.

Authority remains `COMMUNITY/PRACTICAL`, below current author/runtime sources.

The general beginner Prompt page correctly emphasizes that model families differ in Prompt style. Treat it as community teaching evidence, not exact model authority.

Source:
- https://wikiwiki.jp/sd_toshiaki/%E5%88%9D%E3%82%81%E3%81%A6%E3%81%AE%E3%83%97%E3%83%AD%E3%83%B3%E3%83%97%E3%83%88
- rechecked 2026-09-17.

---

## 11. What should be consolidated into current KNOWLEDGE

This batch does **not** require new model-effectiveness verdicts. It mainly organizes existing accepted Claims into one missing workflow view.

### Durable synthesis

1. Human scene-construction order, browse/discovery path, canonical semantic role, and model-specific Prompt serialization are separate layers.
2. A reusable scene semantic skeleton can be formed from already accepted #44 predicates: subject/count, action/state, relation/ownership, body-site, geometry/topology, implement/device, count/timing/source-destination, and visibility.
3. Appearance/clothing/expression and setting/style normally refine the semantic nucleus rather than replacing it.
4. Adult discovery is naturally multi-axis: action, position/geometry, body site, object/device and theme can cross-cut one another.
5. Start-from-any-intent + next-missing-dimension is a better research hypothesis for discovery than ontology-first navigation.
6. None of the above establishes a universal optimal WPF click order without practical UI validation.

### Existing Claims carrying this synthesis

Primary:
- `K-GOV-001`, `K-GOV-002`
- `K-PROMPT-001`, `K-PROMPT-002`, `K-PROMPT-003`
- `K-SUPPORT-001`, `K-SUPPORT-002`
- `K-BIND-001`
- `K-HARD-001` through `K-HARD-006`
- `K-TOOL-001`, `K-TOOL-004`
- `K-MODEL-NOOB-001`
- `K-MODEL-ANIMA-002`, `K-MODEL-ANIMA-004`, `K-MODEL-ANIMA-005`

No current HOLD was closed by source browsing alone.

---

## 12. New open questions created by this audit

These are product/usability research questions, not current generation-effectiveness Claims.

### SW-01 — default human selection order

Is the proposed default:

`subjects -> action -> relation -> body-site -> geometry -> implement -> state/count -> visibility -> appearance -> setting/style`

actually faster/easier in the current WPF than the existing taxonomy-first route?

Required evidence:
- bounded hands-on tasks;
- click path / backtracking / search fallback observations;
- no need for a large user study before a prototype decision, but do not call the order universally optimal.

### SW-02 — adaptive next-facet ranking

After an entry point such as body-site/device/theme is selected, which missing dimension should be shown next for the least backtracking?

Required evidence:
- representative adult consensual tasks across insertion, restraint, device, nonhuman and fluid scenes;
- compare fixed order vs context-sensitive next axes.

### SW-03 — ordinary adult-scene coverage

#44 has deep hard/niche coverage but less explicit organization of ordinary adult scenes that do not stress rare topology/count/device relations.

Required next research only if useful:
- bounded representative ordinary scenes;
- identify whether the same skeleton is sufficient without adding more taxonomy.

### SW-04 — General/Special unified discovery consequences

If product UI later unifies General/Special browsing, determine whether current #64 + #76 metadata is sufficient to support the scene-planning projection without reclassifying production identity.

This is a DEV/product design question. KNOWLEDGE provides predicates/evidence only.

---

## 13. Verdict

`SCENE_WORKFLOW_KNOWLEDGE_GAP_FILLED_AT_SYNTHESIS_LEVEL`

The corpus does **not** need another adult fetish genre ontology.

The useful missing abstraction is:

`intent entry -> semantic scene skeleton -> optional refinements -> model-specific serialization -> generation/evaluation`

The current hard/niche corpus already supplies most semantic predicates required for that abstraction.

### Limitations

- no claim that one human click order is universally optimal;
- no claim that changing UI order improves generation quality by itself;
- no new exact-model hard-relation success rates;
- no product/WPF adoption authorization;
- no broad Stage10 sweep authorized.

### Next

1. expose this synthesis from the #44 adult-generation catalog/file map;
2. keep current Claims/HOLDs unchanged unless a genuinely new verdict is later required;
3. use SW-01/SW-02 only if DEV/product wants a unified scene-oriented browse prototype;
4. continue controlled image tests only for existing exact-model HOLDs when explicitly useful.
