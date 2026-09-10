# Issue #30 Broad Coverage Automation Direction — 2026-09-11

Status: **RESERVED NEXT / DESIGN DIRECTION ONLY / NOT YET AUTHORIZED FOR GENERATION**

This records the user's next-direction request after Generation Batch 2: increase real-image testing substantially, cover varied Special Core Dictionary semantic families, and automate as much of generation/evaluation/routing/audit as safely possible.

This file does **not** start Stage10 production A/B and does not authorize a new large batch yet. Activation requires DEV review of Batch 2, latest-main synchronization, and an explicit current task contract update in Issue #30 + `CURRENT_DEV_TASK.md`.

## Final product objective

The goal is **not** to maximize generated image count.

The goal is to raise DanbooruTagTool's practical completion quality by repeatedly answering, with real-image evidence:

- which Special Core Dictionary families work reliably as-is;
- which require support/clarification tags;
- which fail by seed/model/context;
- which evaluator classes can safely reduce human work;
- which structural classes must remain human-protected;
- which failure clusters should feed product improvements before Stage10 production A/B.

Target end-state:

`Japanese intent -> Special/Core + support selection -> model-aware prompt construction -> high probability of intended visual result`

with the tool automatically handling as much search, selection, generation test, evaluator triage, provenance, and review routing as practical, while the user reviews only genuinely ambiguous/high-value residuals.

## Why broader coverage is valuable

Generation Batch 2 demonstrates the machine-first path, but four experiments are too narrow to estimate behavior across the Special Core Dictionary. Product completeness improves more from **stratified semantic coverage + measured failure modes** than from simply generating many random cases.

The next lane should therefore test multiple semantic strata and accumulate evidence over repeatable waves.

## Proposed semantic strata

Use current canonical Special IDs and existing knowledge/evidence to sample across materially different behavior classes, including:

1. direct / simple-unary visually explicit tags
2. object/attribute visibility and identity support
3. actor/count disambiguation
4. relation / subject-object binding
5. body-site / contact ownership
6. spatial/contact/topology-sensitive cases
7. multi-Special retention / compound coexistence
8. single-support-tag effect
9. evaluator-disagreement / low-confidence / ambiguous identity cases
10. rare / long-tail Special families with weak evaluator coverage
11. temporal/state-change concepts only when a still-image predicate is actually valid; otherwise keep them out of image A/B and record them as non-image-testable

Do not sample uniformly from 2,788 entries merely to increase volume. Avoid repeating already answered cases unless replication is needed to measure seed/model sensitivity.

## Proposed wave size

Initial broad-coverage wave target:

- **12–20 independent experiments**
- normally A/B × 2 predetermined fixed seeds
- approximately **48–80 new images per wave**
- no automatic extra seeds merely to chase a desired result

Later wave size may increase only after automation, provenance, visual-audit transfer, and false-safe checks are proven reliable. Prefer several measured waves over one uncontrolled image dump.

## Automated pipeline

Target flow:

`select stratified cases -> freeze manifest -> generate -> artifact/provenance gate -> WD14/Kagami/CL -> evaluator-reference integrity -> machine image route -> pair route -> independent visual audit sample -> human-required remainder only -> aggregate coverage metrics -> choose next wave adaptively`

The user should not manually search the Special Core Dictionary or review every generated image.

## Audit image transport — adopted direction

Google Drive is **not** used.

Audit-image organization uses a separate private disposable cache repository conceptually named:

`DanbooruTagTool-AuditCache`

It is not canonical. It contains only current disposable audit copies/contact sheets and ownership metadata. Original generated images remain protected locally; accepted textual evidence remains in the main `DanbooruTagTool` repository.

Because direct private binary rendering through the current ChatGPT GitHub connector is not assumed, the guaranteed review handoff is one current contact sheet/audit sheet attached to ChatGPT per wave. That sheet contains all human-required pairs plus a sampled subset of machine-handled pairs. If direct private binary retrieval is later proven, it may replace this one-sheet manual handoff.

All cleanup follows `docs/project/AUDIT_ARTIFACT_CACHE_POLICY.md`. Cleanup must fail closed and may never cross into the main repository, protected data, source images, accepted evidence, or model directories.

## Machine vs human boundary

Machine-handled eligibility stays narrow and must be evidence-backed:

- direct / non-relation / simple-unary
- complete provenance
- all required evaluator artifacts valid
- calibrated agreement/confidence satisfied
- no structural ambiguity

Human-protected by default:

- relation/binding
- actor/subject/object assignment
- exact-count semantics
- multi-person assignment
- body-site ownership/correctness
- insertion/contact/spatial topology
- compound/multi-Special retention
- ambiguous identity/category
- evaluator disagreement/low confidence

Large volume must not be used to silently broaden semantic AUTO authority.

## Independent visual audit of machine-handled results

Every large wave must include a **risk/coverage sample of machine-handled pairs** for independent visual false-safe checking.

Initial rule:

- sample at least **10% of machine-handled pairs**, with a floor of **2 pairs** when two or more exist;
- stratify the sample across distinct semantic families and confidence bands when possible;
- always include suspicious/borderline cases even if that exceeds the percentage;
- if an audited machine-handled pair is false-safe, stop automatic expansion for that affected rule/class and route the class back to human review until recalibrated.

The audit images follow `docs/project/AUDIT_ARTIFACT_CACHE_POLICY.md`: disposable private copies, current-only retention, strict deletion containment, no public Git-history image accumulation.

## Metrics per wave

Record at minimum:

- experiments/images/pairs by semantic stratum
- actual evaluator success/failure counts
- evaluator coverage and disagreement by stratum
- artifact/provenance failures
- machine-handled / human-required / blocked counts at image and pair level
- image-level and pair-level user-review reduction
- visual-audit sample size
- false-safe findings from machine-handled audit sample
- A/B outcomes and seed sensitivity
- support-token benefit/no-benefit/reversal where applicable
- repeated failure clusters and candidate product improvements

Do not claim general reliability from aggregate counts alone; preserve per-stratum behavior.

## Adaptive expansion

After each wave:

- expand strata where results are stable and machine/human routing is behaving correctly;
- spend more samples on high-variance, seed-sensitive, disagreement-heavy, or product-important strata;
- stop low-value repetitions and already-saturated cases;
- use findings to drive #42/product-purpose improvement rather than treating image count itself as success.

No fixed production threshold should be invented merely to automate more aggressively. Fail closed where evidence is weak.

## Preconditions before activation

1. Batch 2 DEV review completed.
2. Issue #30 branch merged/synchronized with latest live `main`; stale `origin/main` is not accepted.
3. Batch 2 machine-handled pairs receive independent visual audit or an explicit DEV rationale for why they are sufficient without it.
4. Disposable audit-image path and one-sheet ChatGPT handoff are available.
5. Audit-cache deletion guards from `AUDIT_ARTIFACT_CACHE_POLICY.md` are implemented/tested before any automated cleanup.
6. Current Issue #30 body and `CURRENT_DEV_TASK.md` are updated together to authorize the new broad-coverage lane.

## Hard boundaries

- no Stage10 production A/B from this direction document
- no production `data/**` mutation
- no #32 canonical/verdict mutation
- no 2,788-image blind sweep
- no runtime LLM dependency
- no public-repository accumulation of generated audit images
- no unsafe broad filesystem cleanup
- no automatic semantic promotion of structural classes

This direction exists to improve final product quality while reducing repeated user review work through measured automation, not to maximize raw generation volume.
