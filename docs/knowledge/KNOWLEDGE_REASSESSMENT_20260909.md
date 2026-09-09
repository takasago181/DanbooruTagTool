# Knowledge Reassessment — 2026-09-09

Owner: Issue #44

Baseline: `docs/knowledge/CURRENT_PRODUCT_GOAL_20260909.md`

Status: initial corpus re-audit before new research

This document classifies the existing KNOWLEDGE corpus against the current product goal. It does not delete historical evidence. A lower priority does not mean the knowledge is false; it means it should not dominate research or audit decisions for the current product.

## Decision labels

- `KEEP_CORE` — directly supports the current product goal and should remain central.
- `MODEL_ONLY` — valuable but must stay limited to the exact family/version/profile.
- `DOWNGRADE` — still useful, but secondary relative to current practical success/failure goals.
- `TEST_REQUIRED` — plausible/important but not safe as a static rule; controlled image evidence needed.
- `OBSOLETE_AS_GOAL` — historical framing is no longer the current target, even if individual facts remain useful.
- `REJECT` — unsafe generalization or incorrect product assumption.
- `MISSING` — knowledge needed by the current goal but not yet strong enough in the corpus.

---

## 1. KEEP_CORE

### 1.1 Model-family separation

**Decision: KEEP_CORE**

Why:
The current product must reduce trial-and-error, and cross-family copy/paste rules can actively increase it. Exact family/profile remains part of claim identity.

Keep central:
- WAI v17 != generic Illustrious
- NoobAI EPS != V-Pred
- Anima Base != Aesthetic != Turbo
- model-specific trigger/order/Negative/settings remain scoped

### 1.2 Canonical identity vs model trigger

**Decision: KEEP_CORE**

Why:
The product needs a stable semantic dictionary while still exploiting model-specific learned spellings. Confusing these would corrupt dictionary meaning or hide why generation differs.

### 1.3 Support taxonomy

**Decision: KEEP_CORE, EXPAND NEEDED**

Current useful separation:
- Meaning
- Geometry/Kinematic
- Visibility
- Resource parking/disambiguation
- Aesthetic
- Redundant decoration

Gap:
The corpus still needs stronger evidence for conflict classification and pruning: support can be semantically compatible yet generation-harmful under a particular family or composition.

### 1.4 Single-vs-composite failure diagnosis

**Decision: KEEP_CORE**

A_ONLY / B_ONLY before AB remains fundamental. Missing B in an AB Prompt cannot prove B is unknown.

### 1.5 Prompt/concept density

**Decision: KEEP_CORE**

The important variable is not raw text length but number of competing concepts, relations, actor bindings, geometry and support blocks.

### 1.6 Negative semantic interference

**Decision: KEEP_CORE + TEST_REQUIRED for exact family effects**

General risk is central; exact unusual-anatomy/count-changing interactions remain image-test dependent.

### 1.7 Hires / img2img / ADetailer / ControlNet / regional-control confounds

**Decision: KEEP_CORE**

The product must know whether a Prompt succeeded or a later intervention repaired it. This is essential for honest Stage10 interpretation and failure diagnosis.

### 1.8 Evaluator/tagger limitations

**Decision: KEEP_CORE**

Automatic evaluation must not convert vocabulary gaps or relational blindness into false generation failure.

---

## 2. MODEL_ONLY

### 2.1 WAI v17 exact quality prefix / settings / Hires advice

**Decision: MODEL_ONLY**

Useful as exact baseline evidence. Do not let WAI author examples become universal product defaults.

### 2.2 NoobAI EPS native caption order

**Decision: MODEL_ONLY, HIGH VALUE**

Special-before-General is strong evidence for NoobAI EPS. It should not silently define WAI/Anima order.

### 2.3 NoobAI V-Pred inference regime

**Decision: MODEL_ONLY, HIGH VALUE**

CFG/Steps/sampler differences are essential when interpreting V-Pred evidence, but are not generic NoobAI knowledge.

### 2.4 Anima tag formatting/profile behavior

**Decision: MODEL_ONLY, HIGH VALUE**

Spaces vs underscores, Gelbooru preference, artist `@`, profile quality behavior and tag/NL mixture are directly useful only under Anima scope.

---

## 3. DOWNGRADE

### 3.1 Generic sampler tuning

**Decision: DOWNGRADE**

Why:
The current product is not a sampler optimization tool. Sampler/CFG/Steps matter as experiment identity and exact-model validity, but research time should prioritize semantic success, binding, conflicts and minimum sufficient support.

Promote back to P0/P1 only when a specific sampler/CFG choice demonstrably changes Special reliability.

### 3.2 Generic aesthetic/quality tricks

**Decision: DOWNGRADE**

Aesthetic quality matters to practical output, but is secondary to correct Special selection and relation/composition success.

Quality/meta remains relevant mainly when:
- it changes framing/composition;
- it suppresses/changes Special recognition;
- it materially changes Prompt competition.

### 3.3 Broad generic Stable Diffusion advice

**Decision: DOWNGRADE / REJECT WHEN UNIVERSALIZED**

Advice detached from exact family/version should be used only as hypothesis generation unless mechanism-level primary evidence applies.

---

## 4. TEST_REQUIRED

### 4.1 Anatomy-sensitive Negative

- `bad anatomy`
- `extra limbs`
- `extra arms`
- `malformed anatomy`

**Decision: TEST_REQUIRED / high priority**

Need exact-family controlled ON/OFF evidence for unusual anatomy, multi-limb, count-changing and body-site-sensitive Specials.

### 4.2 NoobAI EPS exact frame/viewpoint placement

**Decision: TEST_REQUIRED**

Native caption order is known; exact camera/support placement and benefit are not.

### 4.3 Canonical vs Alias vs Semantic generation response

**Decision: TEST_REQUIRED / high priority**

Dictionary relationship does not prove equal model activation. This matters directly to Special selection and generation profile correctness.

### 4.4 Broad + specific support

**Decision: TEST_REQUIRED**

A broad parent may reinforce, compete with or dilute a specific Special depending on model/context.

### 4.5 Exact family-specific prompt-density breakpoint

**Decision: TEST_REQUIRED**

No global threshold should be created from generic concept-count research.

### 4.6 Simultaneous Special-count breakpoint

**Decision: TEST_REQUIRED**

Need representative single/dual/triple+ Special tests by semantic complexity, not just count.

### 4.7 LoRA interaction rules

**Decision: TEST_REQUIRED**

Current evidence is enough to treat LoRA as a confounder, not enough for universal corrective rules.

### 4.8 Tag-only vs short relation sentence

**Decision: TEST_REQUIRED / family-specific**

Especially relevant to Anima and complex relation gaps; do not globalize.

---

## 5. OBSOLETE_AS_GOAL

### 5.1 `Issue #4 research is complete, therefore knowledge is no longer a blocker`

**Decision: OBSOLETE_AS_GOAL**

Historical truth:
#4 completed its pre-Stage10 assignment.

Current interpretation:
The project goal has expanded toward minimum-sufficient Prompt, failure recovery, conflict detection, evaluator routing and practical iteration reduction. Persistent KNOWLEDGE therefore remains active even though #4 itself was correctly completed.

### 5.2 Generic Stage10 fixture success as representative product validation

**Decision: OBSOLETE_AS_GOAL / REJECT as representative evidence**

Simple `standing / sitting / long_hair / smile`-style success remains useful plumbing evidence only. It cannot establish product performance on rare, relational, body-site-binding or multi-Special goals.

### 5.3 `Good Prompt knowledge` as the end product

**Decision: OBSOLETE_AS_GOAL**

The current goal is an effective local deterministic workflow with fewer iterations. Prompt knowledge is one means, not the end.

---

## 6. REJECT

### 6.1 One universal Prompt grammar

**Decision: REJECT**

### 6.2 `More support tags monotonically improve generation`

**Decision: REJECT**

### 6.3 `Current Danbooru post_count directly predicts model knowledge`

**Decision: REJECT**

### 6.4 `Alias identity guarantees equal generation response`

**Decision: REJECT**

### 6.5 `Negative Prompt is neutral cleanup`

**Decision: REJECT**

### 6.6 `Final post-processed image proves base Prompt success`

**Decision: REJECT**

### 6.7 `Low tagger confidence means generation failure`

**Decision: REJECT**

### 6.8 `Long Prompt is bad because it is long`

**Decision: REJECT**

Concept/relationship competition is the meaningful variable; token count alone is insufficient.

---

## 7. MISSING — highest-value gaps

### M1. Support conflict / anti-support knowledge

Current corpus is stronger at `what may help` than `what should not be combined`.

Need evidence for:
- mutually competing frame tags;
- pose vs relation conflicts;
- count/body-structure conflict;
- parent+broad tag dilution;
- visibility support that unintentionally changes pose;
- model-specific redundant or adverse supports;
- interaction with quality/meta blocks.

Priority: **P0/P1**

### M2. Minimum sufficient Prompt / pruning

Need a stronger evidence framework for deciding when support can be removed without reducing target reliability.

Questions:
- Which constituent tags are actually necessary?
- When does redundancy increase competition?
- How should minimum sufficient set be measured across seeds?
- Should `required` mean semantic requirement, empirical generation requirement, or both?

Priority: **P0/P1**

### M3. Failure-diagnosis discriminators

The corpus lists failure classes but lacks enough operational discriminators.

Need evidence for how to distinguish:
- wrong Special meaning;
- model does not know trigger;
- model knows A/B separately but cannot bind them;
- target is present but off-frame/occluded;
- target is suppressed by Negative;
- target is lost due Prompt competition;
- LoRA changes target behavior;
- evaluator cannot observe target.

Priority: **P0**

### M4. Actor-target / body-site relation evidence by target family

General binding literature is strong, but exact project-family evidence is thin.

Need more controlled/practical evidence for:
- two actors;
- left/right ownership;
- hand-to-target assignment;
- body-site-specific relations;
- actor reversal;
- multiple simultaneous relations;
- when regional control becomes necessary.

Priority: **P0**

### M5. Rare/composite Special exposure and model-trigger drift

Need stronger ways to reason about:
- old vs new tag names;
- renamed/aliased concepts after model training;
- rare training exposure;
- direct tag vs decomposed constituents;
- when a model-facing trigger variant is justified.

Priority: **P0/P1**

### M6. Exact-family unusual anatomy / count-changing behavior

Need stronger exact-family evidence beyond generic Negative mechanism.

Priority: **P0**

### M7. Evaluation reliability / seed/sample design

Current corpus says fixed-seed A/B, but lacks a strong rule for when one seed is insufficient and how many seeds are needed for a durable conclusion.

Need evidence for:
- seed sensitivity;
- paired comparisons;
- minimum repeat counts by effect size/variance;
- avoiding cherry-picked seeds;
- human judgement uncertainty;
- when one dramatic counterexample is enough to reject a universal rule but not enough to establish a success rate.

Priority: **P1**

### M8. Prompt weighting and order beyond author defaults

Need controlled evidence for when weighting/order materially helps relation or rare-Special reliability rather than just changing style.

Priority: **P1/P2**

### M9. LoRA x Special / LoRA x support interactions

Need project-relevant evidence on:
- concept leakage;
- trigger/no-trigger influence;
- multiple LoRA conflict;
- style LoRA vs structural Special reliability;
- LoRA weight as experiment identity.

Priority: **P1**

### M10. Assisted-control escalation boundary

Need practical criteria for when to stop Prompt escalation and move to:
- Forge Couple / regional prompting;
- OpenPose / ControlNet;
- targeted inpaint.

The product should not endlessly add tags when Prompt-only is the wrong tool.

Priority: **P1**

### M11. Multilingual evidence depth

The source registry is multilingual, but depth is uneven.

Need more high-quality Japanese/Chinese/Korean exact-model or controlled-practical sources, especially for:
- rare/composite tags;
- actor binding;
- negative interactions;
- multi-Special behavior;
- WAI/NoobAI/Anima exact usage.

Priority: **P1**

### M12. Local success/failure history interpretation

The current product direction may benefit from deterministic local history, but KNOWLEDGE needs rules that prevent personal outcomes from becoming unreviewed universal semantic truth.

Need evidence/design principles for:
- per-model empirical preference;
- sample-size/confidence boundaries;
- separating user-local adaptation from global dictionary meaning.

Priority: **P2**

---

## 8. New research order

The next independent KNOWLEDGE research should run in this order:

### Batch A — false-assumption prevention
1. support conflict / anti-support
2. actor-target/body-site binding
3. rare/composite exposure and trigger drift
4. unusual anatomy / Negative collision
5. failure-diagnosis discriminators

### Batch B — minimum sufficient Prompt
6. pruning/redundancy
7. prompt density / concept competition
8. broad+specific
9. exact-family support ordering/weighting where meaningful

### Batch C — evidence reliability
10. seed sensitivity / multi-seed evaluation
11. human/machine evaluator limits
12. LoRA confounding and interaction
13. assisted-control escalation boundary

### Batch D — lower priority
14. aesthetic/quality refinements
15. generic sampler micro-optimization

---

## 9. Independence rule for this pass

The reassessment was produced by the KNOWLEDGE lane from project-wide stable purpose/rules and its own corpus.

During the next research batches:
- do not ask another active team to validate the conclusions;
- do not consume an in-progress team verdict as proof;
- do not write into another team Issue/workspace;
- store all research in #44 / `knowledge/generation-corpus` only;
- later cross-team handoff occurs only when explicitly requested.