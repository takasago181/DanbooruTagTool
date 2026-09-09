# Current Product Goal — KNOWLEDGE Rebase 2026-09-09

Owner: Issue #44 `[KNOWLEDGE][ONGOING] Persistent generation knowledge corpus for dictionary audit and Stage10`

Status: KNOWLEDGE-side purpose baseline / evidence-routing reference

This file does not change production specification. It defines the current product goal that the KNOWLEDGE corpus should optimize evidence for.

## 1. Current product objective

The current project goal is best represented as:

`short Japanese/English intent -> correct Special Core Dictionary candidate(s) -> minimum useful support / structure -> model-family-appropriate canonical-English Prompt -> fewer iterations to the intended niche image`

The product is not primarily:
- a generic Danbooru browser;
- a translation dictionary;
- a maximal-tag Prompt generator;
- a generic Stable Diffusion tuning handbook;
- an evaluator benchmark harness;
- a runtime LLM assistant.

Those can be inputs or supporting functions, but they are not the end goal.

## 2. Primary success criterion

The strongest product-level success signal is **practical reduction of manual trial-and-error while preserving semantic correctness and traceability**.

A good recommendation is not merely a plausible tag. It should help the user reach the intended visual result with fewer unnecessary iterations.

Therefore KNOWLEDGE should prioritize evidence that helps answer:
1. Did we select the right Special meaning?
2. What minimum support is actually needed for this model family?
3. Which otherwise-plausible support conflicts with the target?
4. Is failure caused by tag exposure, composition/binding, visibility, Prompt competition, model mismatch, Negative collision, or evaluator uncertainty?
5. At what point should the system stop adding tags and admit REVIEW / IMAGE_TEST_REQUIRED / assisted-control need?

## 3. Product invariants relevant to KNOWLEDGE

### 3.1 Local / runtime non-LLM

Runtime must remain local and non-LLM. ChatGPT research can improve static knowledge, dictionaries, profiles, test design and deterministic rules during development, but runtime success must not depend on ChatGPT or a local LLM.

### 3.2 Special-first

The Special Core Dictionary is the product's generation nucleus. Full Danbooru, co-occurrence, semantic/support assets, Japanese search/display and LoRA knowledge are supporting layers.

User-selected one-or-more Specials form the Core Tag Set. Support should clarify, stabilize, expose or disambiguate the Core Tag Set; it must not silently replace it.

### 3.3 Multiple Specials are first-class

The target is not limited to one easy unary tag. Knowledge must cover:
- one Special;
- multiple compatible Specials;
- multiple conflict-prone Specials;
- actor-target / body-site / ownership relations;
- rare/composite concepts;
- visibility and geometry dependencies.

### 3.4 Minimum sufficient Prompt

More tags are not automatically better.

The practical target is the **smallest traceable set that reliably expresses the intended concept for the applicable model family**.

Knowledge should therefore cover both:
- what to add;
- what to remove / not combine.

### 3.5 Model-family scope is part of every generation claim

WAI Illustrious v17, Illustrious, NoobAI EPS, NoobAI V-Pred and Anima profiles must not be flattened into one grammar.

A model-specific trigger, order, Negative, support or parameter claim remains model-scoped unless independent evidence supports broader transfer.

### 3.6 Unknown is acceptable

The product must fail closed when semantics or generation behavior cannot be justified.

`REVIEW`, `UNKNOWN`, `IMAGE_TEST_REQUIRED`, and assisted-control escalation are valid outcomes. False certainty is worse than excess review.

## 4. What KNOWLEDGE should optimize for now

Priority order:

### P0 — semantic/generation false-assumption prevention
- canonical meaning vs model trigger separation
- Alias/canonical/Semantic generation-response distinction
- actor-target / ownership / body-site binding
- rare/composite concept handling
- unusual anatomy / count-changing concept interactions
- Negative collisions
- support-class confusion: meaning vs geometry vs visibility vs resource parking
- post-processing rescue confounds

### P1 — minimum-sufficient support and conflict knowledge
- support additions that measurably improve success
- support that is redundant
- support that is model-specific harmful or ineffective
- conflicting frame / pose / relation / count instructions
- prompt/concept density
- broad + specific combinations
- exact model-family order / trigger / weighting behavior where evidence exists

### P2 — failure diagnosis and recovery
- tag unknown vs composition failure
- relation/binding failure vs wrong canonical
- visibility/crop failure vs concept absence
- Prompt competition vs insufficient support
- model-family mismatch
- LoRA interaction
- post-processing/control rescue
- evaluator uncertainty

### P3 — evaluation design
- how many seeds/images are needed before a generation claim is credible
- pairwise A/B design
- human-vs-machine evidence boundaries
- evaluator vocabulary/semantic coverage
- deterministic metadata needed to interpret results

### P4 — lower-priority tuning detail
- fine sampler differences when they do not materially affect target semantics
- aesthetic/style polish unrelated to target recognition
- general-purpose quality tricks without demonstrated effect on Special success

These remain useful but should not displace the higher-priority evidence above.

## 5. Knowledge outputs the product needs

KNOWLEDGE should aim to produce reusable evidence for:

1. **Generation profile**
   - model-family scope
   - tag/trigger form
   - support candidates
   - known conflicts
   - known HOLD areas

2. **Failure diagnosis**
   - likely failure class
   - evidence needed to distinguish alternatives
   - safe next experiment

3. **Prompt pruning**
   - redundant/overlapping support
   - conflict-prone support
   - minimum-sufficient candidate set

4. **Stage10 test design**
   - representative cases
   - one-question A/B comparisons
   - model-family-specific conditions
   - required metadata

5. **Audit evidence**
   - what may be statically accepted
   - what must remain HOLD/REVIEW
   - what requires controlled images

## 6. Explicit non-goals for the KNOWLEDGE lane

- deciding Japanese display wording
- redefining canonical identity from Japanese or model response
- changing #32 or another lane's verdicts
- selecting production implementation architecture
- introducing runtime LLM dependence
- maximizing automatic coverage at the cost of false approval
- making every model behave through one universal Prompt template
- turning community practice into global production truth

## 7. Current research philosophy

Research should be gap-driven, not curiosity-driven.

Order:
1. current product goal;
2. current corpus claim inventory;
3. KEEP / MODEL_ONLY / DOWNGRADE / TEST_REQUIRED / OBSOLETE / MISSING reassessment;
4. identify high-value gaps;
5. research those gaps with multilingual evidence;
6. store source scope and limitations;
7. convert durable conclusions into audit/test guidance without silently promoting them into production rules.

## 8. Source-of-purpose anchors

Current purpose is consistent with:
- `docs/project/CURRENT_STATE.md`: current persistent KNOWLEDGE lane and Stage10-prep position;
- `docs/project/PERMANENT_RULES.md`: local/non-LLM boundaries, four-team authority, user-effort reduction, evidence/handoff discipline;
- `docs/ARCHITECTURE_POLICY.md`: external/existing-tool first, local/runtime constraints, avoid over-engineering;
- Issue #42 reserved product-purpose formulation: `short Japanese intent -> correct Special2788 candidate(s) -> useful support tags / structure -> practical local non-LLM Prompt -> fewer iterations to the intended niche image`;
- Issue #44: persistent evidence corpus for dictionary audit, Stage10, failure diagnosis, and future product-purpose review.

## 9. KNOWLEDGE independence during this rebase

For the current rebase/research pass, KNOWLEDGE remains independent from other active teams:
- no requests for their judgement;
- no borrowing their in-progress verdict as evidence authority;
- no cross-write into their Issues/workspaces;
- no return handoff until explicitly requested later.

Stable project-wide decisions and completed/historical evidence may be read as context, but the KNOWLEDGE reassessment and research conclusions are generated independently.