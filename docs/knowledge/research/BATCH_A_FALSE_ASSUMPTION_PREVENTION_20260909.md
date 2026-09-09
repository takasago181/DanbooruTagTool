# Batch A — False-Assumption Prevention — 2026-09-09

Owner: Issue #44 `[KNOWLEDGE][ONGOING] Persistent generation knowledge corpus for dictionary audit and Stage10`

Purpose baseline:
- `docs/knowledge/CURRENT_PRODUCT_GOAL_20260909.md`
- `docs/knowledge/KNOWLEDGE_REASSESSMENT_20260909.md`
- `docs/knowledge/PRODUCT_GOAL_EVOLUTION_20260909.md`

Source registry:
- `docs/knowledge/research/BATCH_A_SOURCES_20260909.md`

Status: durable KNOWLEDGE evidence / not production specification

## Executive result

Batch A strengthens a central rule for the current product:

> **When a generated target is missing or wrong, do not jump from “image failed” to “the Special/tag is wrong or unknown.” First distinguish semantic selection, trigger/exposure, composition/binding, visibility/geometry, Prompt competition, Negative suppression, LoRA/personalization interference, seed sensitivity, assisted-control confounds, and evaluator blindness.**

The strongest new evidence is not a new magic Prompt. It is a more reliable **failure-diagnosis tree** and clearer limits on what static generation metadata may safely claim.

High-confidence findings:
1. multi-concept composition has genuine concept-competition/mode-collision failure modes;
2. relation binding is distinct from unary concept recognition;
3. initial random seed materially changes compositional reliability;
4. Negative Prompt can delete a positively requested concept through latent cancellation;
5. canonical identity and learned model trigger can diverge after tag rename/version drift;
6. multiple LoRAs/personalized concepts can interfere, leak or carry unwanted context priors;
7. regional prompting can reduce actor mixing but introduces its own partition/count/coherence constraints;
8. one generated image is useful for a causal pair/counterexample but is insufficient for a reliability-rate claim.

---

# 1. Multi-concept failure: concept competition before “unknown tag”

## Evidence

ICLR 2026 CO3 describes multi-concept prompts where one requested concept becomes missing, faint or collides with another. The paper frames this as drift toward mixed modes that over-emphasize a strongly learned single concept. It also reports that some multi-concept guidance weight regimes can amplify imbalance rather than fix it.

ConceptMix independently shows compositional performance declining as more requested visual concepts are added, especially in open models.

## KNOWLEDGE verdict

**FACT_GENERAL / KEEP_CORE**

For a composite Prompt, missing concept B does not establish:
- B is unknown to the model;
- B's canonical identity is wrong;
- B needs a broad parent injected;
- B should be replaced by an alias;
- B needs more weight.

## Required diagnostic sequence

When feasible, use:

1. `A_ONLY`
2. `B_ONLY`
3. `AB_MINIMAL`
4. `AB + minimum visibility/frame`
5. `AB + targeted geometry/relation support`
6. `AB + actor/resource separation`
7. only then test weighting, decomposition, alternate trigger, regional control, etc.

### Interpretation

- A fail alone -> possible A exposure/trigger/semantic problem.
- B fail alone -> possible B exposure/trigger/semantic problem.
- A pass + B pass + AB fail -> **composition/competition/binding is the default hypothesis**, not tag ignorance.
- AB improves after visibility support -> likely observability/geometry problem, not intrinsic meaning deficiency.
- AB improves only under regional control -> Prompt-only ceiling/actor separation problem is plausible.

## Anti-rule

**REJECT:** `If AB fails, add more support tags until it works.`

More concepts/instructions increase compositional load and can worsen competition.

---

# 2. Relation correctness is a separate target from concept presence

## Evidence

EMNLP 2025 R-Bind explicitly distinguishes:
- entity-attribute binding;
- entity-relation-entity binding.

This matters because an image can contain all requested entities yet still attach attributes or relations to the wrong entity.

## KNOWLEDGE verdict

**FACT_GENERAL / KEEP_CORE**

For DanbooruTagTool, relation-oriented Specials must not be evaluated only as a bag of present tags/objects.

Examples of separate questions:
- Are both actors present?
- Is the intended target body site present/visible?
- Is actor A acting on actor B rather than themselves?
- Is the body-site assignment correct?
- Is left/right or ownership correct?
- Is the relation itself visually established?

## Audit consequence

A generation profile that asserts `ActorRequirement`, `BodypartRequirement`, `SpatialAssignment`, or relation support should be treated as structurally higher risk than a unary object/attribute statement.

Static semantic evidence may establish that the relation is intrinsic to the canonical meaning. It does **not** establish that a model reliably renders the relation.

Model reliability claim -> `IMAGE_TEST_REQUIRED` unless exact controlled evidence exists.

---

# 3. Actor-target and local-attribute binding: exact-family evidence is asymmetric

## Anima official contract

The Anima model card says that for multiple characters, naming a character and describing basic appearance is especially important; listing names alone can confuse the model. This is exact author guidance.

## Anima practical evidence

Official-hosted discussions and Japanese practical tests show recurring patterns:
- some character pairs work while other pairs fail despite both individuals working alone;
- descriptive character-scoped text can rescue some pairings;
- local attributes/ornaments are more prone to crossing actors than strong global identity attributes;
- strong franchise/concept tokens can bleed into the other actor;
- lowering a strong token can reduce bleed but also reduce identity fidelity;
- 3–4 actors with independent location/outfit/object assignments can exceed practical Prompt-only capacity;
- regional prompting is suggested for severe cases.

## KNOWLEDGE verdict

### `character-scoped short natural-language descriptions can help Anima multi-character separation`

**PRACTICAL / MODEL_ONLY / ADOPT_AS_TEST_CANDIDATE**

Not universal FACT.

### `more description always fixes binding`

**REJECT**

Evidence includes cases where more local detail worsens or does not resolve mixing.

### `3+ actors are impossible in Anima`

**REJECT**

Some multi-character combinations work; difficulty depends on pairing, exposure, relation load and prompt structure.

### `3+ actors with many independent attributes are safe Prompt-only`

**REJECT as default assumption**

Treat as HIGH difficulty / likely assisted-control candidate.

## Cross-family caution

Anima's language encoder/training differs materially from WAI/NoobAI. Do not transfer its NL grouping recipe to Illustrious-derived models as a universal grammar.

---

# 4. Support can become anti-support

The current corpus already separated support into Meaning / Geometry / Visibility / Resource Parking / Aesthetic / Redundant Decoration. Batch A adds an important second axis:

> **Semantically compatible support can still be generation-harmful because it competes with composition, actor binding, count, framing or model-specific learned priors.**

## Supported anti-support classes

### 4.1 Competing composition/frame instructions

Existing Illustrious author guidance warns against overusing critical composition tags. Practical evidence shows full-body/close-up/cowboy-shot style combinations can compete and crop needed regions.

**Class:** `FRAME_CONFLICT`

### 4.2 Over-segmentation / prompt fragmentation

WAI v17 + Forge Couple practical evidence warns that splitting one actor's hair/eyes/clothes across too many disconnected prompt pieces can weaken actor coherence.

**Class:** `PARTITION_OVERFRAGMENTATION`

### 4.3 Global count vs regional count conflict

Regional workflows can have a global `2girls`-type count concept bleed into per-region actor blocks; per-region count/solo and global count weighting may require adjustment.

**Class:** `COUNT_SCOPE_CONFLICT`

### 4.4 Strong concept/franchise bleed

Anima practical evidence shows a strong franchise/concept token can spread its features across another character. Lowering its weight may reduce bleed while degrading identity.

**Class:** `STRONG_TRIGGER_BLEED`

### 4.5 Negative-positive semantic collision

A Negative that overlaps the intended concept can directly suppress it.

**Class:** `NEGATIVE_TARGET_COLLISION`

### 4.6 LoRA/context prior conflict

Personalized tokens/LoRAs can carry unwanted pose/background/context priors and multiple LoRAs can interfere.

**Class:** `PERSONALIZATION_CONTEXT_CONFLICT`

## New schema recommendation for future knowledge representation

Without changing production schema now, future KNOWLEDGE should distinguish:
- `support_semantic_compatibility`
- `support_generation_effect`

A tag can be:
- semantically compatible + beneficial;
- semantically compatible + neutral/redundant;
- semantically compatible + harmful under specific family/context;
- semantically incompatible;
- unknown/unvalidated.

This distinction is central to minimum-sufficient Prompt work.

---

# 5. Rare/canonical/Alias trigger drift: identity and activation are separate axes

## Exact Anima evidence

The author model card explicitly says:

- when Danbooru and Gelbooru tag names differ, prefer the Gelbooru version.

Official-hosted user evidence shows cases where an older/Gelbooru spelling activates an artist concept while the current Danbooru spelling produces little/no response.

## KNOWLEDGE verdict

**FACT_EXACT_MODEL:** Anima has an author-documented Gelbooru-preference rule for differing tags.

**PRACTICAL:** specific renamed artists respond to an old/alternate spelling in reported tests.

## Product consequence

Keep four concepts separate:
1. canonical semantic identity;
2. alias/historical identity relation;
3. user search/display surface;
4. model-family trigger surface.

Never rewrite canonical identity because a model responds better to an older form.

## Diagnostic implication

When a canonical tag appears semantically correct but fails generation:

1. confirm canonical meaning;
2. check exact model training cutoff/source conventions if known;
3. inspect known historical/alternate spellings;
4. test canonical vs justified alternate trigger under fixed conditions;
5. store result as model-specific trigger evidence.

## Anti-rule

**REJECT:** `Alias identity guarantees equal generation response.`

Dictionary equivalence and text-encoder/training exposure are different questions.

---

# 6. Current post count is weak evidence for model knowledge

A modern Danbooru post count may be useful for rarity context, but model knowledge depends on:
- training snapshot date;
- source sites/datasets;
- filtering;
- tag rename state at training time;
- caption normalization;
- tag dropout;
- weighting/repetition;
- model finetune/merge history.

Anima has a September 2025 knowledge cutoff and an explicit Gelbooru preference. NoobAI uses its own documented data/caption process. Therefore current 2026 Danbooru count cannot be treated as a direct model-exposure probability.

## KNOWLEDGE verdict

**REJECT:** `current post_count -> model knows/doesn't know tag`

Use post_count only as one contextual rarity signal.

---

# 7. Negative Prompt: a direct failure cause, not neutral cleanup

## Evidence

The negative-prompt mechanism paper reports:
- delayed effect;
- deletion through neutralization/cancellation against positive concepts in latent space.

## KNOWLEDGE verdict

**FACT_GENERAL / KEEP_CORE**

Negative Prompt is an active semantic intervention.

## Diagnostic rule

If the intended Special is missing and the Negative contains a concept overlapping its visible anatomy/count/relation:

1. do not conclude the Special is weak;
2. classify `NEGATIVE_TARGET_COLLISION_POSSIBLE`;
3. test an N0 baseline without the overlapping broad Negative;
4. add negatives one class at a time.

Recommended diagnostic classes:
- `QUALITY_ARTIFACT_NEGATIVE`
- `TEXT_WATERMARK_NEGATIVE`
- `HAND_INTEGRITY_NEGATIVE`
- `BODY_INTEGRITY_NEGATIVE`
- `COUNT_LIMB_NEGATIVE`
- `TARGET_CONCEPT_NEGATIVE`

## Exact-family caution

The mechanism is general. The exact effect of `bad anatomy`, `extra limbs`, `extra arms`, `malformed anatomy` on each project model/Special remains **TEST_REQUIRED**.

NoobAI EPS's author model card includes `bad hands` / `mutated hands` in its example negative, but this does not justify making broader anatomy/count negatives universal defaults.

---

# 8. Seed is part of composition evidence identity

## Evidence

ICLR 2025 Reliable Random Seeds finds that initial noise patterns affect compositional reliability and object placement.

WACV 2025 Good Seed Makes a Good Crop reports seed-dependent effects on object location, size, depth and other visual dimensions.

Anima's own comparison workflow places models in columns and different seeds in rows.

GenEval generates four images per prompt. T2I-CompBench generates ten images per prompt for its metrics. These benchmarks differ in design, so neither number should be copied blindly as a project threshold.

## KNOWLEDGE verdict

**FACT_GENERAL / KEEP_CORE**

### One seed is enough for:
- paired visual debugging;
- checking that a deterministic A/B pipeline changes only the intended variable;
- demonstrating a specific counterexample;
- rejecting a universal claim when one valid counterexample logically disproves it.

### One seed is NOT enough for:
- estimating success probability;
- declaring a support generally reliable;
- declaring a model generally incapable;
- selecting a production threshold based on frequency.

## Proposed Stage10 evidence levels

Not a production rule yet; use as a research framing:

### `CASE_EVIDENCE`
One or few fixed paired seeds. Shows a mechanism/example.

### `REPEATABILITY_EVIDENCE`
Multiple predetermined seeds. Shows whether the A/B direction repeats.

### `RELIABILITY_EVIDENCE`
Enough predetermined seeds/cases to estimate a success-rate difference with uncertainty.

The exact seed count should depend on effect size, variance, experiment cost and risk. It remains `TEST_REQUIRED` rather than copying 4 or 10 from generic benchmarks.

## Anti-cherry-pick rule

Seeds used to claim improvement should be predetermined or selected by a reproducible rule. A seed discovered because it shows the desired result cannot alone support a reliability claim.

---

# 9. LoRA is an intervention even without an obvious trigger effect

## Evidence

LoRACLR, ConceptSplit and TARA all motivate their methods with multi-concept interference/entanglement problems. TARA specifically identifies identity missing, feature leakage, token-wise interference and spatial misalignment when combining multiple LoRA modules.

WACV personalization work shows subject tokens can bind subject-irrelevant background/pose elements, producing context conflicts.

## KNOWLEDGE verdict

**FACT_GENERAL:** multi-personalization interference is a real mechanism class.

**TEST_REQUIRED:** exact project LoRA x Special behavior.

## Audit/experiment consequence

Every generation claim using LoRA should preserve at least:
- LoRA name/version/hash when available;
- weight;
- trigger text used/not used;
- number of loaded LoRAs;
- whether style/character/pose/concept LoRA;
- base checkpoint.

If target behavior changes only with LoRA loaded, do not attribute the effect solely to the Special/support Prompt.

## Practical hypothesis worth testing

A LoRA can alter base behavior even without an explicit trigger because adapter weights modify the model path when loaded. This is widely plausible and supported by training/practical evidence, but exact impact varies; keep as model/LoRA-specific evidence rather than universal magnitude claim.

---

# 10. Assisted control: useful, but do not let it erase Prompt-only diagnosis

## Forge Couple / regional prompting evidence

Practical WAI v17 evidence and official Forge Couple behavior support using spatial regions to reduce actor/color mixing. However:
- outcome still depends on checkpoint ability;
- global vs per-region counts can conflict;
- excessive prompt partitioning can reduce coherence;
- region weights can cause leakage;
- boundary-heavy scenes remain difficult.

Anima community/practical evidence similarly points toward regional prompting when multi-actor binding becomes too complex for ordinary prompting.

## KNOWLEDGE verdict

**ADOPT as separate assisted-control lane.**

Do not call it automatic evidence that the base Prompt grammar was sufficient.

## Proposed escalation logic for research

1. minimal Prompt-only baseline;
2. minimal semantic support;
3. visibility/geometry support;
4. character/relation-scoped phrasing if family supports it;
5. Prompt-only ceiling documented;
6. regional/ControlNet assisted lane;
7. post-generation inpaint/ADetailer repair lane.

This prevents endless Prompt bloat.

Exact escalation thresholds remain `MISSING / TEST_REQUIRED`.

---

# 11. Evaluator decomposition should mirror failure classes

Batch A reinforces that a single tagger score cannot answer all Stage10 questions.

For a relation/composite target, machine/human evaluation should distinguish:
- entity presence;
- count;
- target body-site visibility;
- attribute ownership;
- relation correctness;
- spatial assignment;
- forbidden leakage/fusion;
- overall prompt-level success.

This resembles atom-based composition evaluation used in modern T2I benchmarks.

## KNOWLEDGE verdict

**KEEP_CORE**

A unary image tagger can be useful for presence, but relation/body-site/ownership failures must not be silently collapsed into the same confidence threshold.

---

# 12. Failure-diagnosis tree v1

This is the primary practical output of Batch A.

When a target image misses the intended Special or combination:

## Step 0 — Traceability gate

Check:
- exact checkpoint/profile;
- actual positive Prompt;
- actual Negative;
- seed;
- sampler/steps/CFG/resolution;
- LoRA/adapters;
- Hires/img2img/ADetailer;
- regional/ControlNet;
- actual model trigger spelling.

If missing -> evidence may be `BLOCKED` rather than generation failure.

## Step 1 — Semantic identity

Question:
`Is the selected canonical/Special actually the intended meaning?`

If no -> `WRONG_SELECTION / SEMANTIC_MISMATCH`.

If uncertain -> `REVIEW`.

## Step 2 — Single-concept activation

Generate/test target alone with minimum model-family baseline.

If it fails alone:
- investigate trigger spelling/history;
- training cutoff/exposure;
- canonical vs justified alternate trigger;
- target visibility;
- conflicting Negative.

Possible class:
`EXPOSURE_OR_TRIGGER_FAILURE`.

## Step 3 — Composition comparison

If A and B pass separately but AB fails:

Default class:
`COMPOSITION_OR_BINDING_FAILURE`.

Do not label B unknown.

## Step 4 — Visibility / geometry

If target might be cropped/occluded/impossible to observe:
- add only minimum frame/visibility support;
- then minimum geometry support.

If target appears -> `VISIBILITY_GEOMETRY_FAILURE`.

## Step 5 — Negative collision

Remove semantically overlapping body/count/concept negatives in controlled A/B.

If target returns -> `NEGATIVE_TARGET_COLLISION`.

## Step 6 — Prompt competition / anti-support

Prune:
- competing frame tags;
- redundant parents;
- excessive detail;
- strong unrelated concept triggers;
- duplicated count cues;
- conflicting relation/pose support.

If minimal version improves -> `PROMPT_COMPETITION / ANTI_SUPPORT`.

## Step 7 — LoRA/personalization

Re-run without nonessential LoRA/adapters where valid.

If target improves -> `LORA_OR_PERSONALIZATION_INTERFERENCE`.

## Step 8 — Seed sensitivity

Test predetermined multiple seeds.

If behavior changes widely -> `HIGH_SEED_SENSITIVITY`, not stable PASS/FAIL.

## Step 9 — Assisted control

If Prompt-only repeatedly fails while unary concepts are known:
- regional prompting / Forge Couple;
- ControlNet/OpenPose where geometry is the issue;
- targeted inpaint/ADetailer only as repair.

If assisted succeeds -> `PROMPT_ONLY_CEILING`, not evidence that the base Prompt was sufficient.

## Step 10 — Evaluator blindness

If human sees target but tagger/evaluator does not:
`EVALUATOR_COVERAGE_FAILURE`.

If neither can reliably judge:
`REVIEW / HUMAN_ONLY / IMAGE_TEST_REQUIRED`.

---

# 13. What Batch A changes in the research priority map

## M3 Failure-diagnosis discriminators

Status moves from `MISSING` to **PARTIALLY COVERED**.

We now have a defensible first diagnostic tree, but exact project-family thresholds remain missing.

## M4 Actor-target/body-site exact-family evidence

Status: **PARTIALLY COVERED**.

Anima has useful official/practical evidence. WAI/NoobAI exact-family relation evidence remains thinner.

## M5 Rare/composite trigger drift

Status: **PARTIALLY COVERED**.

Anima has exact author Gelbooru preference + concrete rename examples. Other target families still need deeper historical-trigger evidence.

## M6 Unusual anatomy/count-changing

Status: **PARTIALLY COVERED mechanism / still TEST_REQUIRED exact family**.

Negative suppression mechanism is strong; exact Special/model behavior remains unresolved.

## M7 Seed/sample reliability

Status: **STRONGLY IMPROVED, exact project sampling rule still TEST_REQUIRED**.

## M9 LoRA x Special/support

Status: **MECHANISM COVERED / project behavior TEST_REQUIRED**.

## M10 Assisted-control boundary

Status: **PARTIALLY COVERED**.

We have a proposed escalation sequence, not a validated threshold.

---

# 14. New HOLD / test candidates created by Batch A

### H-A01 — WAI v17 relation/binding Prompt-only ceiling
Need controlled multiple-seed tests on actual representative Special relations.

### H-A02 — NoobAI EPS actor/body-site binding
Official caption order exists, but exact relation-support grammar remains insufficiently supported.

### H-A03 — canonical vs alternate trigger cross-family behavior
Anima evidence is strong; WAI/NoobAI need separate tests before generalization.

### H-A04 — Negative anatomy/count collision magnitude
Mechanism known, effect magnitude/family scope unknown.

### H-A05 — Prompt pruning benefit
Batch A shows why over-support can hurt, but does not yet establish minimum-sufficient selection rules. This is Batch B.

### H-A06 — regional-control escalation threshold
Need practical rule based on repeated Prompt-only failure, actor/relation count and user cost.

### H-A07 — Stage10 seed count
Need a cost-aware project-specific protocol rather than copying 4/10 from benchmarks.

---

# 15. REJECT list strengthened by Batch A

- `A and B work separately, so AB should work.`
- `AB failure means one tag is unknown.`
- `More weight fixes a weak concept without trade-off.`
- `More description always improves actor binding.`
- `More support tags monotonically improve success.`
- `Alias/canonical equivalence means equal model activation.`
- `Current post count proves training exposure.`
- `Negative is neutral cleanup.`
- `One successful seed proves reliability.`
- `One failed seed proves incapability.`
- `Regional prompting success proves Prompt-only success.`
- `ADetailer/Hires rescue proves base anatomy/composition was correct.`
- `LoRA is irrelevant when its trigger is omitted.`
- `Tagger confidence alone validates relational composition.`

---

# 16. Next independent KNOWLEDGE research

Batch B should focus on **minimum sufficient Prompt / pruning**, using Batch A's anti-support categories as the starting point:

1. how to distinguish required vs redundant support empirically;
2. broad parent + specific Special interaction;
3. conflict-aware removal order;
4. concept-density measurement more useful than raw token count;
5. family-specific support ordering/weighting only where evidence supports it;
6. what success repetition is sufficient to remove a support candidate;
7. practical stopping rule: when to stop Prompt additions and escalate to assisted control.

No other active team input is required for Batch B research.
