# Batch C — Evidence Reliability / Evaluator Boundaries — 2026-09-09

Owner: Issue #44 `[KNOWLEDGE][ONGOING] Persistent generation knowledge corpus for dictionary audit and Stage10`

Status: durable KNOWLEDGE evidence / not production specification

Source registry:
`docs/knowledge/research/BATCH_C_SOURCES_20260909.md`

## Executive result

Batch C replaces a dangerous question:

`How many images are enough?`

with a more defensible one:

> **What kind of claim are we trying to make, and what paired/repeated evidence is required for that claim?**

A single generated pair can establish a reproducible example or disprove a universal claim. It cannot estimate reliability. Multiple paired seeds can show repeatability. Statistical comparison requires a predeclared sample and paired analysis. A production/general rule requires replication across representative semantic cases and the applicable model family.

The evidence hierarchy also changes evaluator usage:
- vocabulary/coverage check comes before confidence;
- unary tag presence is not relation truth;
- OOD/calibration belong to the score identity;
- human `TIE / UNCLEAR` are legitimate outcomes;
- local personal history may improve local ranking, but never canonical semantics.

---

# 1. Four evidence levels for generation claims

No fixed image count is globally valid. Use claim-dependent levels.

## E0 — CASE / DEBUG EVIDENCE

Purpose:
- verify pipeline and traceability;
- demonstrate that an effect can occur;
- produce a concrete counterexample;
- isolate one variable under one seed.

Typical evidence:
- one or a few predetermined paired seeds;
- exact same seed/metadata on A and B.

Can support:
- `this conflict occurred`;
- `this support can alter the result`;
- `this universal claim is false because a valid counterexample exists`;
- bug/root-cause debugging.

Cannot support:
- success probability;
- general support reliability;
- model incapability;
- production default threshold.

## E1 — REPEATABILITY EVIDENCE

Purpose:
- determine whether the A/B direction recurs rather than appearing only on one seed.

Required properties:
- seed list fixed before reviewing outputs;
- paired A/B on identical seeds;
- all outputs retained, including failures/ties;
- no seed cherry-picking;
- absolute success and pairwise direction both recorded.

Can support:
- `the benefit repeats in this case/model under this seed set`.

Cannot automatically support:
- other Specials;
- other model families;
- universal production rule.

## E2 — COMPARATIVE / INFERENCE EVIDENCE

Purpose:
- make a defensible claim that A and B differ under a predeclared test population.

Required properties:
- predeclared seed/case sample;
- paired analysis;
- uncertainty interval/test appropriate to outcome type;
- effect size/practical impact reported, not only p-value;
- `TIE / UNCLEAR / BLOCKED` handling defined before judging;
- evaluator capability fixed/pinned.

For binary target success:
- paired binary outcomes naturally fit a McNemar/exact-binomial view of discordant pairs.

For scalar scores:
- use paired differences/resampling rather than independent-system point estimates when the same images/cases are compared.

Can support:
- scoped comparative claims under the tested model/case distribution.

## E3 — GENERALIZATION / RULE EVIDENCE

Purpose:
- justify a reusable model-family or production-level knowledge rule.

Requires more than E2:
- multiple representative semantic cases;
- relevant rare/common/relation/multi-Special strata;
- repeated evidence across seeds;
- exact model-family/profile scope;
- evaluator limitations accounted for;
- collateral effects measured;
- failure cases preserved, not averaged away.

A rule does not become universal merely because it is statistically significant in one Special.

---

# 2. Pairing is mandatory when seed is controllable

For Prompt/support A/B, use the same seed for A and B.

Why:
- seed/noise materially affects composition;
- pairing cancels a large part of case/seed difficulty;
- Kagami's evaluator comparison likewise uses paired resampling over identical images to reduce per-image difficulty noise.

## Wrong design

A seeds: `[1,2,3,4]`
B seeds: `[5,6,7,8]`

A/B differences mix Prompt effect with seed difficulty.

## Preferred design

Seeds: `[s1,s2,s3,...]`

For every `si`:
- generate A(si)
- generate B(si)
- judge the pair under the same question.

Order presented to human reviewer should be masked/randomized when practical so the reviewer does not know which is the supposed improvement.

---

# 3. Relative improvement and absolute reliability are separate

This distinction is essential.

Suppose a seed produces:
- A = fail
- B = fail

This pair gives no directional evidence that B is better than A, but it is still a major **absolute reliability failure**.

Likewise:
- A = pass
- B = pass

The pair does not distinguish A from B, but both may be practically reliable on that seed.

Therefore every experiment should record two views.

## View 1 — absolute outcome

Per condition:
- pass count/rate;
- fail count/rate;
- unclear/blocked count;
- confidence interval when making reliability claims.

## View 2 — paired directional outcome

Per seed/case:
- `A_ONLY_PASS`
- `B_ONLY_PASS`
- `BOTH_PASS`
- `BOTH_FAIL`
- `TIE_VISUAL`
- `UNCLEAR`
- `BLOCKED`

For paired binary success comparison, McNemar focuses on the two discordant cells (`A_ONLY_PASS` vs `B_ONLY_PASS`).

Do not discard `BOTH_FAIL` from the product report merely because it does not affect the paired difference test.

---

# 4. Small-sample exact paired inference

When target success is truly binary and pairs are independent across chosen seeds/cases, exact McNemar uses the binomial distribution over discordant pairs.

This creates an important practical lesson:

> **The informative sample size for directional binary difference is the number of discordant pairs, not merely the total number of seeds.**

Illustration under a two-sided exact binomial null of equal discordant directions:
- 5 discordant pairs all favor B -> p = 0.0625;
- 6 discordant pairs all favor B -> p = 0.03125.

This is an illustration, **not a rule that six seeds are enough**. If most seeds are both-pass/both-fail, total seeds can be much larger while directional evidence remains weak.

## Practical consequence

Do not predefine evidence as:
`8 seeds = proven`.

Instead predefine:
- target outcome definition;
- total planned seeds/cases;
- paired analysis;
- acceptable uncertainty/practical effect;
- handling if discordant information is too sparse.

---

# 5. Statistical significance is not product usefulness

A support can have a statistically consistent effect that is too small to reduce user trial-and-error meaningfully.

Conversely, a large practical improvement may initially have wide uncertainty because rare/composite generation is expensive and variable.

Therefore every KEEP/PRUNE conclusion should distinguish:

## `DIRECTION`
Does removal/addition tend to help or hurt?

## `MAGNITUDE`
How much absolute success/quality/binding changes?

## `COLLATERAL`
Does it introduce another error?

## `UNCERTAINTY`
How wide/unstable is the estimate?

## `USER_VALUE`
Is the effect likely to reduce iterations or prevent a serious false result?

Never promote based on p-value alone.

---

# 6. Support-ablation evidence states

Batch B introduced leave-one-out support ablation. Batch C gives it evidence states.

For support `s` under a pinned model/case:

## `KEEP_CASE_EVIDENCE`
One/few pairs show a concrete useful effect, but reliability unknown.

## `KEEP_REPEATABLE`
Predetermined paired seeds show the benefit repeatedly with no major unresolved collateral problem.

## `KEEP_COMPARATIVE`
Predeclared paired analysis supports a meaningful benefit under the tested distribution.

## `PRUNE_REPEATABLE`
Removing `s` repeatedly does not reduce target success or improves collateral behavior under the scoped test.

## `MIXED_SEED_SENSITIVE`
Effect direction changes materially across seeds.

## `TRADEOFF`
Helps one required dimension while harming another.

## `NO_INFORMATION`
Too few discordant/informative outcomes; both conditions behave similarly or evaluator cannot distinguish.

## `BLOCKED_EVALUATOR`
Target cannot be validly judged by the current evaluator.

No exact automatic threshold between these states is fixed in KNOWLEDGE yet.

---

# 7. Human pairwise judgement should allow uncertainty

Pick-a-Pic explicitly supports ties, and its authors report that two-image comparison with ties performed best among their tested annotation interfaces for engagement/agreement.

For DanbooruTagTool, forcing a reviewer to choose A or B when neither is meaningfully better would manufacture evidence.

## Recommended judgement vocabulary

- `A_WIN`
- `B_WIN`
- `TIE`
- `UNCLEAR`
- `BOTH_FAIL`
- `BLOCKED`

These are not interchangeable.

### `TIE`
Both are judgeable and no meaningful preference/difference exists for the stated question.

### `UNCLEAR`
The intended concept/relation cannot be judged confidently from the images.

### `BOTH_FAIL`
Both are judgeable and both fail the required target.

### `BLOCKED`
Traceability/evaluator/input is invalid or missing.

This separation prevents ambiguous images from becoming fake ties or fake wins.

---

# 8. Human judgement itself is noisy

Studies of image/anatomy evaluation show annotator-style differences and non-perfect inter-rater agreement.

Therefore high-risk judgement should define what the reviewer is judging before showing the pair.

For example, instead of:
`Which image is better?`

Ask:
- Is the requested Special relation present?
- Is actor A acting on actor B?
- Is the required body site correct and visible?
- Is either image unjudgeable due crop/occlusion?
- Did the support create an unwanted competing error?

A global aesthetic preference can disagree with semantic success and should be a separate question.

---

# 9. Preference reward models are not Special truth

HPS/ImageReward/PickScore-style systems learn broad human preferences and can be useful for:
- aesthetics;
- general prompt alignment;
- broad pairwise ranking.

They are **not** automatically valid for:
- rare Special canonical semantics;
- actor-target reversal;
- body-site correctness;
- unusual anatomy intended by the prompt;
- niche relation fidelity.

Use as optional auxiliary signal only after validating relevance to the exact question.

---

# 10. Evaluator capability gate v1

Before using any automatic evaluator score, check in this order.

## Gate 1 — vocabulary / target representability

Question:
`Can this evaluator output or meaningfully score the target?`

If no:
`UNSUPPORTED_EVALUATOR`, not generation fail.

WD v3 structurally filtered tags below 600 training images, so many rare targets can never be direct WD labels.

## Gate 2 — semantic class

Classify target:
- unary presence;
- count;
- simple attribute;
- framing/pose;
- body site;
- relation;
- actor-target/ownership;
- composite/multi-Special;
- semantic/decomposed concept.

A unary multi-label tagger is strongest in the first classes and cannot be presumed to solve relation/ownership merely because component tags score highly.

## Gate 3 — calibration / threshold identity

Record:
- evaluator version;
- target tag;
- raw score;
- threshold source;
- per-tag calibration if available;
- whether a global threshold is being used.

CL Tagger v2 explicitly provides per-tag metrics/calibration and warns that F1-optimal tag thresholds tend to over-tag in practical use. This is direct evidence against treating a single number as universal truth.

## Gate 4 — OOD / input-distribution risk

If evaluator exposes OOD statistics, use/report them where relevant.

OOD or unusual anatomy/style/crop should lower confidence in automatic verdict, not silently keep the same threshold.

## Gate 5 — human contradiction

If machine and informed human judgement disagree on a high-risk target:
- preserve both;
- route to REVIEW;
- do not auto-train the human or machine to be “wrong” from one case.

---

# 11. Evaluator roles for current candidates

This is knowledge classification, not final tool allocation.

## WD EVA02 v3

Strength:
- cheap/common booru-style presence signal;
- existing integration.

Hard limitation:
- tags below 600 training images were filtered;
- vocabulary narrow relative to current Special ambitions.

Use:
`BASELINE / COMMON_UNARY_SIGNAL`

Never:
`GLOBAL_SPECIAL_GROUND_TRUTH`

## Kagami-24k

Strength:
- 24k general vocabulary;
- strong common-intersection AP results vs WD;
- paired-bootstrap uncertainty reported;
- open Apache-2.0.

Limit:
- larger vocabulary does not prove equal rare-tail reliability;
- still a Danbooru multi-label tagger, not a relation reasoner.

Use:
`WIDE_VOCAB_UNARY_CANDIDATE`

## CL Tagger v2

Strength:
- very wide vocabulary;
- per-tag metrics/thresholds/calibration;
- OOD reference statistics.

Limits:
- false positive/negative inherent;
- ambiguous General/Meta lower-confidence classes;
- gated/custom license;
- stable/provisional versions differ.

Use:
`WIDE_VOCAB_CALIBRATED_CANDIDATE`

Do not finalize adoption/coverage until the final dictionary is frozen and exact license/integration decision is made.

---

# 12. Capability-routed evaluator principle

No one evaluator/threshold should answer every question.

Conceptual routes:

### `DIRECT_UNARY`
Direct tag in validated vocabulary.

### `COUNT_ATTRIBUTE`
Direct count/simple attribute with evaluator known to perform that class.

### `DECOMPOSED`
Semantic target broken into machine-checkable predicates; overall success still conservative.

### `RELATION_HUMAN_OR_SPECIALIZED`
Actor-target/body-site/relation requires human or separately validated relation evaluator.

### `GEOMETRY_VISIBILITY`
Pose/keypoint/framing signal can assist but cannot certify niche semantic relation.

### `UNSUPPORTED_OR_OOD`
REVIEW rather than FAIL.

This is the evaluator counterpart of the Prompt support taxonomy.

---

# 13. Deterministic local history without semantic contamination

The current product may benefit from remembering which supports worked for the user locally. This is compatible with runtime non-LLM if handled as statistics, not semantic truth.

## What local history MAY learn

Under matching context:
- support `s` tends to improve this Special/model combination;
- alternate trigger form works better for this exact model version;
- a support is frequently redundant locally;
- a certain Prompt-only relation is highly seed-sensitive;
- assisted control is often required.

It may influence:
- local ranking;
- warning badges;
- default experiment suggestion;
- `previously worked for this model/context` hints.

## What local history MUST NOT learn automatically

- canonical meaning;
- Alias equivalence;
- semantic-support intrinsic relationship;
- model-independent production rule;
- global negative/positive rule from one person's results.

## Minimum context identity for a history observation

Persist enough to avoid pooling incompatible experiments:
- exact checkpoint/model hash/version;
- model family/profile;
- Special canonical/ID(s);
- actual model trigger surface;
- support set and support roles;
- positive Prompt hash/text reference;
- Negative Prompt hash/text reference;
- seed;
- sampler/scheduler/steps/CFG/resolution;
- LoRA names/versions/weights;
- Hires/img2img/ADetailer state;
- regional/ControlNet state;
- evaluator version;
- human/machine outcome and uncertainty.

## Scope rule

A model update creates a new empirical scope by default. Old history remains evidence, but should not silently pool into the new version.

## Statistical rule

Store counts/outcomes and uncertainty, not a single hard learned “truth” bit.

For binary local success, an exact/Wilson interval can communicate how uncertain a small count is. For paired support comparisons, retain the paired table rather than flattening to independent win counts.

No heavy ML platform is required.

---

# 14. Assisted-control evidence identity

A Prompt-only test and a regional/ControlNet/ADetailer-assisted test are different interventions.

Record the lane explicitly:
- `PROMPT_ONLY`
- `REGIONAL_ASSISTED`
- `CONTROLNET_ASSISTED`
- `POSTPROCESS_REPAIR`

If Prompt-only fails and assisted control succeeds:
- record `PROMPT_ONLY_CEILING` or similar scoped finding;
- do not rewrite the Prompt-only condition as success.

This keeps failure diagnosis honest and tells the future product when adding more tags is the wrong recovery path.

---

# 15. Seed/sample protocol v1 — knowledge recommendation

No global fixed seed count is promoted. Instead use the lowest evidence level sufficient for the decision.

## For debugging / pipeline verification
E0 is enough.

## For deciding whether a support deserves further consideration
Use E1 predetermined paired replication.

## For KEEP/PRUNE claims that may influence persistent model-family guidance
Use E2 predeclared paired analysis plus absolute reliability and collateral metrics.

## For reusable defaults across a semantic class
Require E3 across representative cases, not merely more seeds on one case.

### Escalate sample size when
- outcome direction is mixed;
- discordant pairs are too few;
- confidence interval is too wide for the practical decision;
- high-risk false certainty would be costly;
- effect is small but proposed as a default.

### Do not spend more images merely to force significance when
- both conditions are clearly inadequate and need a different intervention;
- evaluator cannot judge the target;
- experiment question is malformed;
- semantic identity is unresolved.

Fix the experiment first.

---

# 16. New REJECT rules

- `N total seeds alone determines evidence strength.`
- `8 seeds = proven` or any other context-free fixed count.
- `Same-seed A/B means one seed is enough for reliability.`
- `Statistical significance = user-useful improvement.`
- `Both-fail pairs can be ignored because they do not affect McNemar direction.`
- `Human reviewer must choose A or B.`
- `TIE and UNCLEAR are the same.`
- `Preference reward = semantic correctness.`
- `If target tag is absent from evaluator vocabulary, image failed.`
- `One global confidence threshold is valid across all Special classes.`
- `High calibrated unary confidence proves relation/ownership correctness.`
- `Personal local success can rewrite canonical/semantic truth.`
- `Assisted-control success can be pooled into Prompt-only success rate.`

---

# 17. What Batch C resolves

### M7 Seed/sample evaluation reliability
Status: **STRONG FRAMEWORK / exact Stage10 counts intentionally not fixed**

### evaluator uncertainty
Status: **STRONG PRINCIPLE / final final-dictionary coverage still pending**

### local history interpretation
Status: **STRONG SAFETY/DATA-SCOPE RULES / implementation later if desired**

### LoRA confounding
Status: **STRONG evidence-identity rule / exact project interaction remains TEST_REQUIRED**

### assisted-control boundary
Status: **STRONG evidence separation / exact escalation threshold remains HOLD**

---

# 18. Remaining high-value research after Batch C

The most important unresolved knowledge is now more exact-family-specific than conceptual:

1. WAI v17 actual actor-target/body-site relation ceiling;
2. NoobAI EPS relation/framing/support behavior;
3. cross-family canonical/Alias/alternate-trigger generation response;
4. unusual anatomy/count-changing Negative interaction magnitude;
5. broad+specific support behavior;
6. LoRA x Special/support interaction under actual project families;
7. representative evaluator coverage after final Special Core Dictionary freeze.

Generic image-generation advice is now lower-value than controlled evidence on these gaps.
