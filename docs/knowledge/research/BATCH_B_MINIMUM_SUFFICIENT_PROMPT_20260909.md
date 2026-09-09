# Batch B — Minimum-Sufficient Prompt / Pruning — 2026-09-09

Owner: Issue #44 `[KNOWLEDGE][ONGOING] Persistent generation knowledge corpus for dictionary audit and Stage10`

Status: durable KNOWLEDGE evidence / not production specification

Source registry:
`docs/knowledge/research/BATCH_B_SOURCES_20260909.md`

## Executive result

The current product should not optimize for the shortest Prompt or the largest plausible support set.

The useful target is:

> **A minimum-sufficient Prompt is the smallest traceable semantic/support set for which removing another non-intrinsic element causes a repeatable meaningful loss of target success, visibility/binding correctness, or unacceptable collateral errors under the applicable model-family test conditions.**

This is an empirical concept, not a fixed tag-count threshold.

Batch B strengthens five rules:

1. **Do not prune intrinsic meaning.** Special identity, intrinsic actor/target/body-site/count/relation modifiers and required model-facing trigger syntax belong to the semantic nucleus.
2. **Prune functional redundancy and conflicts, not characters/tokens blindly.** More complex prompts create token/concept competition, but structure can improve binding.
3. **Same-role support should usually be replaced/tested rather than stacked by default.** Exact Illustrious evidence specifically warns about conflicting critical composition tags.
4. **Model-family prompting conventions survive pruning.** Anima can benefit from adequate structured description and does not reward an indiscriminate shortest-prompt strategy; WAI directly warns about excess quality/Negative content.
5. **Support necessity should be tested by paired ablation across predetermined seeds.** One good/bad seed can show a case, not a general necessity/redundancy rule.

---

# 1. Minimum sufficient is not shortest

## Evidence logic

Primary compositional research shows both sides of the problem:
- increasing semantic complexity increases competition among requested concepts/tokens;
- preserving linguistic/syntactic structure can improve attribute/relation binding.

Therefore two simplistic rules are both wrong:

**REJECT:** `longer is always worse`

**REJECT:** `more descriptive/support tags are always better`

## Product definition

A Prompt can be longer than another and still be more efficient if its extra words encode necessary actor/target/relation structure.

A Prompt can be shorter and worse if pruning deletes:
- which actor owns an attribute;
- the target body site;
- a count modifier;
- an intrinsic spatial/relation condition;
- a model-required trigger surface;
- the only visibility/geometry cue that makes the target observable.

The optimization target is **information utility per added concept**, not raw length.

---

# 2. Protect the semantic nucleus before pruning

Before any pruning experiment, freeze a `SEMANTIC_NUCLEUS` for the case.

This nucleus should contain only meaning-bearing content that cannot be removed without changing what the user asked for.

Potential nucleus fields:
- selected Special canonical identity / exact model trigger form when separately justified;
- multiple selected Specials;
- intrinsic count/cardinality;
- intrinsic actor/ownership distinction;
- intrinsic target/body-site;
- intrinsic action/state/relation;
- required direction/orientation only when part of canonical meaning rather than merely helpful composition;
- required object/implement when intrinsic;
- character identity if the test requires a fixed character;
- exact model-family syntax needed to express the above.

## Important distinction

A tag may be useful to generate or observe the concept without being part of its semantic nucleus.

Examples:
- `full body` may expose a body site but usually is not intrinsic Special meaning;
- `from side` may make a relation visible but is often a viewpoint support;
- a broad parent may reinforce a specific concept but is not automatically part of the specific identity;
- quality/aesthetic tags are not Special meaning.

Pruning should not rewrite the nucleus to make generation easier. If the model only succeeds after changing the requested meaning, that is not success.

---

# 3. Two-axis support model

Batch A added the need to separate semantic compatibility from generation effect. Batch B formalizes it.

For each support candidate, track conceptually:

## Axis A — semantic relation
- `INTRINSIC`
- `COMPATIBLE_SUPPORT`
- `OPTIONAL_VARIATION`
- `UNRELATED`
- `CONFLICTING_MEANING`

## Axis B — empirical generation effect under a model/case
- `BENEFICIAL`
- `NEUTRAL_OR_REDUNDANT`
- `HARMFUL`
- `MIXED_SEED_SENSITIVE`
- `UNTESTED`

This prevents a major error:

`semantically compatible` **does not imply** `should be included`.

A support may be perfectly compatible yet:
- compete for framing;
- duplicate another concept;
- add count ambiguity;
- bind to the wrong actor;
- increase text-encoder/chunk complexity;
- trigger a strong learned prior;
- be unnecessary for the selected model.

---

# 4. Pruning order v1

This is a safe **research order**, not a production auto-delete rule.

The semantic nucleus is protected throughout.

## P1 — Remove pure decoration not under test

First candidates:
- ornamental aesthetic adjectives;
- extra lighting/background/style detail unrelated to target judgement;
- generic “quality magic” beyond the exact family baseline;
- social/media artifact terms in positive Prompt when not needed.

Why first:
They increase concept load without helping target semantics.

Exact WAI v17 evidence also warns that excessive quality/aesthetic additions can degrade output.

## P2 — Remove duplicate/synonymous representations

Examples:
- exact duplicate tags;
- repeated same concept across structured fields;
- multiple weak synonyms whose only purpose is to restate one concept.

Caution:
Do not treat canonical + model-specific trigger as a duplicate unless their generation use has been explicitly designed; they are different identity layers.

## P3 — Resolve same-role composition conflicts by replacement

Examples:
- `close-up + cowboy shot + full body`;
- multiple incompatible viewpoints;
- mutually inconsistent orientation cues.

Prefer one deliberately selected frame/viewpoint baseline rather than stacking all plausible options.

This is directly supported by Illustrious author guidance and a Japanese fixed-seed counterexample.

## P4 — Ablate unproven broad parents / constituent supports

Test:
`SPECIFIC_ONLY` vs `SPECIFIC + BROAD_PARENT`

Do not assume broad parent always reinforces the specific concept.

Possible outcomes:
- benefit;
- no measurable change;
- dilution/competition;
- model/seed-specific mixed effect.

Broad + specific remains `TEST_REQUIRED` globally.

## P5 — Prune optional contextual natural language

For hybrid-capable families, remove context clauses that do not carry:
- actor identity;
- relation;
- spatial assignment;
- needed scene geometry.

Do not strip a useful structured relation sentence merely because prose is longer than tags.

Anima exact/practical evidence especially requires this distinction.

## P6 — Ablate visibility / geometry supports one by one

Examples:
- frame;
- viewpoint;
- orientation;
- body-site visibility;
- resource parking.

Only after semantic/decorative conflicts are cleaned.

If removing a support repeatedly causes the target to disappear/off-frame/bind incorrectly, it is empirically useful for that case/family even if not intrinsic meaning.

## P7 — Re-test weights only after structural pruning

Do not use weighting to rescue a fundamentally conflicting Prompt before removing redundancy/conflicts.

Weighting can create trade-offs: stronger concept A can suppress/bleed into B or alter identity.

Exact optimal weights remain model/case-specific.

---

# 5. Leave-one-out support ablation protocol

The strongest practical method for identifying minimum sufficient support is paired support ablation.

Suppose a working Prompt has semantic nucleus `N` and support set `{s1, s2, s3}`.

Test:
- `N + s1 + s2 + s3`
- `N + s2 + s3`  (`-s1`)
- `N + s1 + s3`  (`-s2`)
- `N + s1 + s2`  (`-s3`)

Use the **same predetermined seed set** for each pair and preserve exact generation metadata.

## Evaluate more than target presence

For each ablation, record:
- Special target success;
- actor-target/body-site correctness;
- visibility/crop;
- unintended leakage/fusion;
- anatomy/structural collateral errors relevant to the experiment;
- evaluator uncertainty;
- any effect on other simultaneous Specials.

## Support disposition

A support is a strong `KEEP` candidate when:
- removing it causes a repeatable meaningful degradation in the intended target or required observability;
- the effect is not merely an artifact of one cherry-picked seed;
- a simpler lower-conflict support does not provide the same benefit.

A support is a strong `PRUNE` candidate when:
- removal does not meaningfully reduce target success over the tested seeds/cases; or
- removal improves success/reduces collateral errors; and
- it is not part of the semantic nucleus.

A support remains `MIXED/REVIEW` when:
- effects change direction across seeds;
- the evaluator cannot judge reliably;
- it helps one Special while harming another and the product trade-off is unresolved.

## Numeric threshold

No exact required number of seeds or effect-size threshold is promoted in Batch B. This remains a Batch C / Stage10 test-design question.

---

# 6. Why broad + specific remains HOLD

The research did not recover sufficiently strong exact-family evidence for a universal policy such as:
- always add the broad parent;
- never add the broad parent;
- always decompose rare/composite Specials into constituents.

This is important because `broad + specific` can serve different roles:
- exposure reinforcement;
- semantic clarification;
- redundant restatement;
- competition/dilution;
- model-specific trigger bridge.

## Safe rule

Treat a broad parent/constituent as **empirical generation support**, not automatically intrinsic meaning.

Pairwise test:
1. specific alone;
2. specific + one broad parent/constituent;
3. optionally alternate justified trigger if the hypothesis is training exposure rather than semantic support.

Do not stack several parents/constituents at once for the first test because attribution becomes impossible.

---

# 7. Concept density beats raw token count

Batch B reinforces that prompt density should record **semantic workload**, not merely tokenizer length.

Recommended experimental descriptors:
- Special count;
- actor count;
- relation count;
- attribute-binding count;
- target body-site count;
- object/implement count;
- frame/viewpoint/orientation instruction count;
- support block count;
- natural-language relation/context clause count;
- Negative concept overlap count;
- LoRA count;
- raw token count as an additional descriptive metric.

## Why

Two prompts with 100 tokens can have very different difficulty:
- one may contain harmless style adjectives;
- another may require three actors, four attribute bindings and two spatial relations.

Primary composition research supports concept/binding complexity as the meaningful difficulty driver.

---

# 8. A1111 / Forge chunking means token count is also a tool confound

A1111 documents prompts longer than its standard 75 tokens as multiple independently encoded 75-token chunks concatenated before the UNet.

Forge retains prompt word-wrap/chunk controls around the same boundary.

NoobAI's underlying CLIP configs expose 77 positional embeddings, but this does **not** mean a Forge prompt beyond 77 tokens is simply truncated.

## KNOWLEDGE consequence

**REJECT:** `75/77 tokens is a universal hard maximum for this project.`

Instead:
- record actual WebUI/runtime;
- record tokenizer/token count where possible;
- treat chunk-boundary changes as a confound if an A/B edit moves content across chunks;
- use explicit `BREAK` only as a separately tested formatting intervention, not a free optimization.

Exact Forge Neo local behavior must remain tied to the validated local build rather than generic A1111 assumptions.

---

# 9. Model-family pruning profiles

## 9.1 WAI Illustrious v17

### Strong evidence
- excessive quality/aesthetic tags: prune candidate;
- overly long Negative: prune candidate;
- exact small author baselines exist.

### Keep separate
- target/general tag density is not covered by the author's warning in the same exact way;
- do not turn the warning into a global maximum positive-tag count.

### Recommended research baseline
Start from:
- semantic nucleus;
- minimal exact-family quality baseline;
- one required frame/viewpoint support at a time;
- small Negative baseline with target-overlap negatives excluded when testing target retention.

Then add support by one functional role.

## 9.2 Illustrious XL early

### Strong evidence
- overusing critical composition tags can conflict/confuse;
- choose a suitable composition tag for the use case.

### Recommended pruning priority
- same-role composition conflict is high priority;
- frame/visible-detail consistency matters: off-frame detail tags are legitimate pruning candidates in practical workflows.

## 9.3 NoobAI XL 1.1 EPS

### Strong evidence
- native caption order separates Special from General;
- exact family baseline settings/prefix exist.

### Missing evidence
- exact minimum sufficient General/support set;
- broad+specific behavior;
- relation sentence utility;
- exact camera support.

### Rule
Preserve Special-before-General as a family baseline when testing pruning, but do not infer that all General tags should be retained or deleted.

## 9.4 Anima

### Strong exact evidence
- random tag dropout -> every relevant tag need not be supplied;
- pure natural language should not be extremely short; adequate description matters;
- multiple characters benefit from identity + basic appearance descriptions;
- tags and natural language can be mixed.

### Practical evidence
- targeted relation/action sentence can improve behavior in some fixed-seed tests;
- excessive/unstructured environment prose can overpower framing in reports;
- hybrid prompts often trade richer relation/context for higher concept load.

### Rule
For Anima, **minimum sufficient is explicitly not “fewest words.”**

Prefer:
- high-information identity/count tags;
- only needed appearance tags;
- direct action/relation tags;
- one concise structured relation/layout sentence when the relation cannot be expressed robustly as tags;
- remove redundant synonyms and irrelevant prose.

Exact hybrid recipe remains profile/case-specific.

---

# 10. Pruning cannot delete hidden observability requirements

A support can appear redundant when the evaluator does not notice what it protects.

Example failure:
- remove `from side`;
- target still exists semantically;
- body-site relation becomes visually ambiguous;
- unary tagger still reports component tags;
- system incorrectly marks support redundant.

Therefore pruning evaluation must test the **question the support was intended to solve**, not only final target tag confidence.

Each support candidate should have an intended role/question:
- `FRAME`: is the target in frame?
- `VIEWPOINT`: is the relation/body site judgeable?
- `GEOMETRY`: is the requested pose physically expressible?
- `RESOURCE`: are hands/actors assigned without leakage?
- `MEANING`: is an intrinsic semantic component missing?
- `AESTHETIC`: does it improve a separately stated aesthetic objective?

If no question can be stated for a support, it is a strong redundancy candidate.

---

# 11. Stop rule: bounded escalation, not endless Prompt growth

Batch B cannot justify a universal numeric tag limit, but it supports a **role-bounded escalation policy** for experiments.

## Prompt-only escalation order

1. semantic nucleus only;
2. one minimal visibility/frame intervention if target cannot be judged;
3. one viewpoint/orientation intervention if geometry/relation requires it;
4. one targeted relation/geometry support;
5. one resource/actor-disambiguation support where needed;
6. family-specific concise structural natural language only where supported;
7. explicit trigger/weight experiment only for a named hypothesis.

At each step, compare against the previous step across the same seeds.

## Stop Prompt escalation when

- all relevant functional roles have been tested and none gives repeatable benefit;
- additions create new conflicts/leakage faster than they improve target success;
- A/B single concepts work but the composition repeatedly fails despite minimal structural support;
- the remaining failure is clearly spatial/actor assignment that an assisted-control lane is designed to solve;
- evidence becomes too seed-sensitive to claim a stable support rule.

Then classify:
- `PROMPT_ONLY_CEILING`;
- `ASSISTED_CONTROL_TEST_REQUIRED`;
- or `REVIEW`.

Do not continue adding unrelated synonyms/aesthetic detail merely to avoid a HOLD outcome.

Exact count of failed escalation steps is not fixed as a production threshold.

---

# 12. Minimum-sufficient Prompt acceptance concept

A case-level Prompt set can be called a **minimum-sufficient candidate** only when:

1. semantic nucleus is intact;
2. no known same-role conflict remains;
3. each remaining non-intrinsic support has a stated functional purpose;
4. leave-one-out removal of each remaining support has been tested at the required evidence level;
5. no removed support produces a repeatable material benefit that is lost;
6. no simpler alternative support gives equivalent/better target reliability with fewer collateral effects;
7. the conclusion is scoped to model/checkpoint/profile and test conditions;
8. seed/evaluator uncertainty is reported.

The exact statistical evidence requirement is intentionally deferred.

---

# 13. New anti-patterns / REJECT

- `Shortest Prompt = best Prompt.`
- `Every relevant tag from the reference image should be included.`
- `If a support is semantically compatible, keep it.`
- `If a model sometimes ignores a Special, add all broad parents/constituents.`
- `Stack several camera/frame tags so at least one works.`
- `Use weighting before resolving structural conflicts.`
- `75/77 tokens is a hard WebUI Prompt limit.`
- `Remove relation prose first because prose is longer than tags.`
- `A support is redundant if a unary tagger score stays the same.`
- `Once the Prompt works on one seed, all retained support is necessary.`
- `Keep adding support until the model eventually produces one success.`

---

# 14. What Batch B resolves

### M1 Support conflict / anti-support
Status: **STRONG GENERAL / MEDIUM EXACT-FAMILY**

We now have a practical conflict-pruning model and exact WAI/Illustrious examples.

### M2 Minimum sufficient Prompt / pruning
Status: **STRONG GENERAL / MEDIUM EXACT-FAMILY**

Definition, protected nucleus, pruning order, leave-one-out protocol and stop rule are durable.

### M5 Broad + specific
Status: **STILL TEST_REQUIRED**

Research did not justify a global rule.

### M8 Weight/order
Status: **PARTIAL**

Exact family order evidence exists (NoobAI/Anima), but weighting as a repair remains model/case-specific and should follow structural pruning.

### M10 Assisted-control escalation boundary
Status: **IMPROVED / THRESHOLD HOLD**

A role-bounded stopping principle exists. Numeric threshold remains unvalidated.

---

# 15. Next research — Batch C

Batch C should focus on **evidence reliability and remaining confounds**:

1. project-appropriate predetermined seed/sample protocol;
2. when a support benefit is strong enough to KEEP vs MIXED;
3. pairwise/human judgement uncertainty;
4. evaluator false-positive/false-negative implications for pruning;
5. LoRA x Special/support practical interactions;
6. how to use local personal success/failure history without converting it to universal semantic truth;
7. assisted-control evidence identity and stopping decision refinement.

Batch C should convert the current qualitative ablation protocol into a statistically/evidentially defensible test hierarchy without overbuilding a research platform.
