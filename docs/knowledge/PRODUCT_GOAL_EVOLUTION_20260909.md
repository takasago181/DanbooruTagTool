# Product Goal Evolution — 2026-09-09

Owner: Issue #44 `[KNOWLEDGE][ONGOING] Persistent generation knowledge corpus for dictionary audit and Stage10`

Status: KNOWLEDGE interpretation of stable project-purpose evolution

This document compares the early/frozen product goal with the current product-success criterion. It does not rewrite `docs/PRODUCT_GOAL_LOCK.md` or production specification.

## Conclusion

**The foundational goal has not reversed. It has expanded.**

The durable invariant from the early design remains:

`Special-first -> Core Tag Set -> auxiliary/support only where needed -> canonical English Prompt`

What has changed is the definition of *success*.

Early success was largely:

`find/select the intended Special(s) -> supplement with co-occurrence/general tags -> build/copy a useful Prompt`

Current success is stronger:

`short Japanese/English intent -> correct Special candidate(s) -> minimum sufficient model-family-appropriate support -> canonical English Prompt -> diagnose misses safely -> reduce unnecessary generation iterations`

The project has therefore moved from **Prompt construction** toward **reliable intent-to-generation assistance** without changing the Special-first authority model.

---

## 1. Early locked purpose that remains valid

### `docs/PRODUCT_GOAL_LOCK.md`

The locked purpose states that the project is not primarily search, analysis, or dictionary editing. Its first purpose is to select Special dictionary words/combinations as the generation nucleus, then use full Danbooru and real co-occurrence to find auxiliary tags for elements that are difficult to stabilize with the nucleus alone.

It defines the primary/auxiliary hierarchy:

Primary:
- Special words
- Special combinations
- Core Tag Set

Auxiliary:
- full Danbooru canonical
- true multi-tag AND
- Candidate Aggregation
- Alias
- Japanese search
- Semantic Bridge
- Recommendation
- Prompt Builder
- LoRA

It also defines the user flow:

`find Special -> add to core -> inspect real-co-occurrence auxiliaries -> add only needed auxiliaries -> Prompt Copy`

**Current verdict: KEEP_CORE.**

None of the current product-purpose improvements justify reversing this hierarchy.

### `docs/CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md`

The v1.3 FINAL goal likewise says the tool is not a universal Danbooru search tool. One or multiple Specials form the Core Tag Set; true multi-tag AND and Candidate Aggregation support that nucleus; full Danbooru is widened to only when needed; the output is an English image-generation Prompt.

**Current verdict: KEEP_CORE.**

The implementation baseline still matches the current user goal structurally.

---

## 2. What has expanded since the early goal

The following were not the dominant success criteria in the early lock, but have become central through later Stage8/9/10-prep experience and the current product-purpose reservation.

### 2.1 Fewer iterations is now a product-level objective

The tool should not merely return plausible tags. It should reduce the number of manual trial-and-error cycles needed to reach the intended niche image.

Knowledge implication:
- prioritize reliability, conflict and failure-cause evidence over generic Prompt folklore;
- prefer evidence that changes what the user does next.

### 2.2 Minimum sufficient Prompt is now preferred over maximal plausible support

Early architecture correctly provided auxiliary candidates, but later design now asks a second question:

`which plausible tags should NOT be added?`

Current success requires:
- required/core support;
- useful support;
- optional variation;
- redundant support;
- conflict-prone / harmful support;
- evidence for pruning.

### 2.3 Multiple-Special composition is now an explicit quality target

The early goal already supported multiple Specials, but later knowledge work shows that this is not simply a set-union problem.

The current product must treat as first-class:
- A works, B works, AB fails;
- actor-target reversal;
- body-site binding;
- concept bleeding;
- count/resource conflicts;
- visibility/geometry dependency;
- regional-control ceiling.

### 2.4 Model-family-specific ineffective/harmful guidance matters

The original implementation goal did not need to encode a complete model-family Prompt science.

The current goal does need enough family-scoped knowledge to avoid:
- giving WAI advice to Anima;
- copying NoobAI EPS settings to V-Pred;
- assuming a generic Negative is harmless;
- assuming a tag spelling that is canonical is also the strongest model trigger.

### 2.5 Failure diagnosis is now part of usefulness

A failed image should not automatically cause more tags to be added.

The current system should eventually distinguish, when evidence permits:
- wrong Special selection;
- model trigger/exposure weakness;
- composition/binding failure;
- crop/visibility failure;
- Prompt competition;
- Negative collision;
- LoRA contamination;
- evaluator blindness;
- assisted-control need.

### 2.6 Evaluation uncertainty is now explicit

The current product does not need fake 100% automation.

Safe outcomes include:
- REVIEW
- UNKNOWN
- IMAGE_TEST_REQUIRED
- assisted-control escalation

The system should automate obvious/measurable cases and avoid turning weak evidence into false certainty.

### 2.7 Post-processing and control interventions must be separated from Prompt-only evidence

Hires, img2img, ADetailer, ControlNet, regional prompting and Forge Couple can repair or reshape results.

Current interpretation therefore requires:
- Prompt-only success lane;
- assisted-control lane;
- post-processing lane;
- no claim that a repaired final image proves the base Prompt succeeded unaided.

### 2.8 Local empirical learning became a candidate direction

A future deterministic local history may record per-model success/failure without runtime LLM use.

This is an extension of the original goal, not a semantic-authority replacement. Personal empirical history must never rewrite canonical meaning automatically.

---

## 3. What did NOT change

The following remain stable and should not be reopened merely because the success criterion expanded:

- Special-first product hierarchy.
- One or multiple Specials form the Core Tag Set.
- Full Danbooru/co-occurrence/Semantic/LoRA are supporting resources.
- Final Prompt identity is canonical/model-facing English rather than Japanese display text.
- Runtime is local and non-LLM.
- Japanese is an input/search/display bridge, not semantic authority.
- Unknown/ambiguous mappings must not be silently guessed.
- Model-family observations must not become universal rules without evidence.
- General distribution/product complexity is not a priority for this local personal tool.

---

## 4. Knowledge-priority change

### Earlier emphasis
- tag discovery
- co-occurrence usefulness
- semantic support candidates
- Prompt structure
- model baseline settings
- camera/visibility candidates

These remain useful.

### Current higher emphasis
1. semantic false-assumption prevention
2. support conflict / anti-support
3. minimum sufficient Prompt and pruning
4. actor-target/body-site/multi-Special binding
5. rare/composite trigger/exposure uncertainty
6. Negative semantic collision
7. failure-cause discrimination
8. model-family-specific adverse/ineffective guidance
9. multi-seed reliability/evaluation design
10. assisted-control escalation boundary

Generic sampler/aesthetic micro-optimization is now lower priority unless it materially changes Special success.

---

## 5. Knowledge-team operating consequence

The persistent KNOWLEDGE corpus should not become an encyclopedia of image-generation tips.

Each substantial research item should be judged by whether it helps one of these questions:

- Does this help select the right Special?
- Does this help establish the intended Special reliably?
- Does this reveal a support tag that should be added or removed?
- Does this prevent a model-family mistake?
- Does this distinguish one failure cause from another?
- Does this show when Prompt-only should stop and another control lane should begin?
- Does this improve the reliability of Stage10 evidence?
- Does this reduce manual trial-and-error without weakening semantic traceability?

If not, it is lower priority even if technically interesting.

---

## 6. Final KNOWLEDGE purpose baseline

For future research and audit-facing interpretation, use:

> **Special-first, local, non-LLM intent-to-generation assistance whose success is measured by semantic correctness, model-family-appropriate minimum sufficient Prompt construction, safe failure diagnosis, and reduction of unnecessary generation iterations.**

This is an expansion of the original product goal, not a replacement of it.
