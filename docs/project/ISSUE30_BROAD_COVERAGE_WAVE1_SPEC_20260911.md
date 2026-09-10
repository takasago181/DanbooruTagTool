# Issue #30 Broad Coverage Wave 1 Spec

Date: 2026-09-11
State: AUTHORIZED_AFTER_PREFLIGHT / MACHINE_FIRST / FULL_CHATGPT_VISUAL_AUDIT / BROAD_MULTI_FAMILY / STAGE10_PRODUCTION_NOT_STARTED
Source Issue: #30
Working branch: `codex/issue30-calibration-design`

## Purpose

Use the repaired Batch 2 evaluator/provenance/routing pipeline to collect broad controlled image evidence across materially different Special semantic families, while measuring how trustworthy the machine routing actually is against an independent full visual review.

This is still Issue #30 Phase 2 calibration/refinement. It is **not** Stage10 production A/B.

## User intent lock

The user explicitly wants useful broad generation across many different Special genres/families now and will upload the generated Wave 1 review assets so ChatGPT can inspect **all generated images**, not only a machine-selected sample.

Therefore:
- this task authorizes new generation **after mandatory preflight passes**;
- Wave 1 machine routing remains active and must be recorded, but it must **not hide any valid generated image from the independent ChatGPT visual audit**;
- the previous 4-image false-safe audit is superseded as a separate blocking step; historical Batch 2 machine-handled pairs may still be used as optional anchors without regeneration;
- Wave 1 is a calibration wave for machine-vs-visual agreement, not a demonstration that human review can already be safely reduced.

## Mandatory preflight — before generating any new image

Codex must first:

1. fetch the latest live `origin/main` and merge it into `codex/issue30-calibration-design`;
2. no rebase and no force rewrite;
3. verify Batch 2 accepted evidence remains readable;
4. verify actual evaluator-success counting is artifact/result based;
5. verify per-image evaluator-reference integrity is enforced;
6. verify pair routes are calculated from actual image routes;
7. verify A/B condition comes from structured manifest, not filename guessing;
8. implement/verify audit-cache deletion containment / sentinel / ownership-manifest / fail-closed guards required by `AUDIT_ARTIFACT_CACHE_POLICY.md`;
9. run focused regression fixtures containing at least one machine-handled pair, one human-required pair, and one blocked/mismatch case;
10. if any mandatory preflight item fails: **STOP with 0 new images**.

The cache-safety implementation is prerequisite work inside this same task; it does not require a separate user-visible audit cycle before generation.

## Wave 1 size

Target:
- **16 independent experiments**
- normally **A/B × 2 predetermined fixed seeds** per experiment
- target **64 new images**

Allowed adaptive range:
- minimum 12 experiments / 48 images if strong redundancy or invalid candidates make further generation low-value;
- maximum 20 experiments / 80 images;
- no automatic extra seeds;
- no quota filling with redundant cases;
- no blind 2,788-entry sweep.

## Broad family stratification

Select real current Special entries so that Wave 1 covers materially different generation behaviors. Do not let one family dominate the batch.

Aim for roughly one to two experiments from as many of these families as practical:

1. **DIRECT_SIMPLE_UNARY** — visually explicit single-concept cases suitable for machine handling.
2. **BODY_VISIBILITY_ATTRIBUTE** — clear body/visibility/attribute changes without relation semantics.
3. **CLOTHING_EXPOSURE_STATE** — clothing/exposure state changes where the visual target is direct.
4. **POSE_COMPOSITION** — pose, orientation, framing, or composition-sensitive cases.
5. **OBJECT_TOOL_PRESENCE** — clear object/tool presence or category cases.
6. **ACTION_CONTACT** — contact/action cases where topology matters and human protection may be required.
7. **BODY_SITE_SPATIAL** — body-site or spatial-placement correctness cases.
8. **ACTOR_COUNT_ROLE** — actor/count/role assignment cases.
9. **MULTI_PERSON_BINDING** — multi-person relation/binding cases.
10. **MULTI_SPECIAL_RETENTION** — two or more requested Special concepts that must coexist without one disappearing.
11. **RESTRAINT_OR_DEVICE_STATE** — restraint/device/attachment-state cases.
12. **FLUID_OR_VISIBLE_STATE** — visually evident fluid/state-result cases.
13. **NONHUMAN_OR_UNUSUAL_FORM** — unusual/nonhuman visual-form cases where identity/category can be tested without relying on tagger semantics alone.
14. **REPRODUCTIVE_OR_BODY_STATE** — adult body-state cases where visible state can be checked.
15. **SCENE_CONTEXT_SITUATION** — context/situation/background interactions with the main Special.
16. **SINGLE_SUPPORT_TAG_EFFECT** — one support-tag addition/removal with a causally clean A/B contrast.

The exact selected Special IDs are Codex's responsibility; the user must not be asked to search the 2,788-entry dictionary manually.

### Safety/content scope for Wave 1 selection

Use clearly adult subjects only. Exclude age-ambiguous or minor-coded cases from generated evidence. Avoid selecting graphic injury/gore material merely to increase category count. This restriction does not mutate or delete the canonical dictionary; it only constrains this controlled image-generation wave.

## Experiment construction

Each experiment must answer one clear question.

Preferred A/B structure:
- A = baseline/core construction
- B = one controlled change, support, disambiguator, or alternative construction

Requirements:
- keep all non-target generation settings fixed within a pair;
- use predetermined fixed paired seeds;
- do not alter multiple unrelated factors at once;
- record exact Special IDs and support tags in machine-readable manifest;
- mark whether the experiment is expected to be machine-judgeable, human-protected, or mixed before generation.

## Generation profile

Unless a selected experiment has a documented reason to differ, use the accepted Batch 2 profile:

- Forge Neo
- WAI Illustrious v17
- Euler a
- scheduler: Automatic
- Steps: 25
- CFG: 5
- resolution: normally 1024 × 1344
- Hires fix: OFF
- ADetailer: OFF
- LoRA: OFF
- ControlNet: OFF
- regional/Forge Couple: OFF

Any exception must be experiment-specific and recorded; do not silently change the common profile.

## Mandatory machine-first order

For every valid new image:

`generate -> artifact/provenance gate -> WD14 -> Kagami-24k -> CL Tagger v2.00 -> evaluator-reference integrity -> image route -> pair route -> machine result freeze -> full ChatGPT visual-audit export`

All three evaluators run on every valid image.

Machine evaluation must affect and record the provisional route. It is not decorative telemetry. However, during Wave 1 the provisional route does **not** suppress images from the independent visual audit.

## Routing policy

### MACHINE_HANDLED_PAIR

Eligible only when both A and B images in the pair are safely handled under existing calibrated rules, with complete provenance and evaluator agreement/confidence sufficient for the experiment question.

Keep eligibility narrow and mainly direct/non-relation/simple-unary.

### HUMAN_REVIEW_REQUIRED_PAIR

Use when either side requires protected semantic judgment, including:
- relation/binding;
- exact count;
- actor/subject/object assignment;
- multi-person role assignment;
- body-site ownership/correctness;
- insertion/contact/spatial topology;
- compound/multi-Special retention;
- ambiguous identity/category;
- evaluator disagreement or low confidence.

### BLOCKED_PAIR

Use for artifact/provenance/evaluator/A-B-manifest failure that prevents a valid comparison.

Do not convert a blocked or structural case into machine-handled merely to improve a review-reduction metric.

## Wave 1 full ChatGPT visual audit — mandatory

### Core rule

**Every valid generated Wave 1 image must be represented in the ChatGPT-visible audit package.**

Do not omit an image because its pair was routed `MACHINE_HANDLED_PAIR`.

The purpose is to compare the frozen machine route/verdict against independent image-level and pair-level visual judgments across the entire Wave 1 dataset.

### Review package

After generation and machine routing, export:

1. a complete index manifest mapping every generated image to:
   - display number;
   - experiment ID;
   - semantic family;
   - image ID;
   - A/B condition;
   - seed;
   - source hash;
   - source locator;
   - provisional machine image route;
   - provisional machine pair route;
   - evaluator-result locators;
2. readable visual audit sheets covering **all valid generated images**;
3. disposable individual audit copies for all valid images in the audit cache so a specific image can be inspected at higher resolution if a sheet is ambiguous.

Preferred audit-sheet density:
- normally 4 A/B pairs = 8 images per sheet;
- fewer when fine spatial/body-site details would become hard to inspect;
- do not create one giant 48–80-image sheet that makes individual images too small.

The user may upload all sheets/images to ChatGPT. Codex must not require the user to manually classify all images; the user's role is primarily to provide the visual assets. ChatGPT performs the independent visual comparison, with user judgment reserved for genuine ambiguity or a later product decision when needed.

### Visual verdict vocabulary

Prepare the review mapping so ChatGPT results can be recorded per A/B pair using:
- `A_ONLY_PASS`
- `B_ONLY_PASS`
- `BOTH_PASS`
- `BOTH_FAIL`
- `UNCLEAR`
- `ASSET_INVALID`

The concrete Japanese question for each experiment must state what visual property/relation is being checked. Do not ask a vague question such as only “どちらが良いか”.

### Machine-vs-visual calibration metrics

Wave 1 must report, after ChatGPT visual results are returned:
- total visually audited images / generated valid images;
- total visually audited pairs / generated valid pairs;
- machine route vs visual-review agreement by pair;
- **false-safe count/rate**: machine-handled pair for which visual audit finds the required semantics failed, ambiguous, invalid, or should not have been safely hidden;
- **false-human/over-routing count/rate**: pair sent to human route where visual evidence indicates the case was direct/clear enough to be a future auto candidate; this is only a calibration signal, not automatic promotion;
- disagreement counts by semantic family;
- machine-handled false-safe rate by semantic family;
- evaluator disagreement/low-confidence relation to visual failures;
- any recurrent failure mode that should change future routing or Prompt/support construction.

Do not claim a machine-routing class is trusted merely because it had a high aggregate agreement rate; structural protected categories remain protected unless separately justified.

## Review-reduction metric interpretation

Continue calculating the **provisional** image-level and pair-level review-reduction metrics from machine routes so they remain comparable with Batch 2.

But for Wave 1:
- these are diagnostic “what the machine would have hidden” metrics;
- actual independent visual-audit coverage is **100% of valid generated images/pairs**;
- do not report provisional review reduction as actual achieved visual-review reduction for this wave.

Later waves may return to sampled auditing only after DEV/ChatGPT explicitly accepts evidence that the relevant machine-handled families have an adequately low false-safe rate.

## Visual audit UX

All audit sheets are created only after machine triage has been frozen.

Show by default:
- image(s);
- large display number;
- correct A/B marker;
- semantic-family/experiment grouping only when needed for navigation;
- one large concrete Japanese question per A/B pair.

Do not show by default:
- full Prompt/Negative;
- raw evaluator logs/scores;
- model/settings wall of text;
- unnecessary internal identifiers.

Question font >=24 px, preferably 28–32 px.
Font priority: Meiryo -> Yu Gothic -> MS Gothic.
Tofu/square => review asset invalid.

A/B marker must be derived from structured manifest/condition. Exactly one A and one B per `(experiment, seed)` pair. Duplicate/all-A/all-B/mismatch => BLOCKED.

## Audit-cache rules

Generated review copies/contact sheets are disposable audit artifacts. Original source images and raw evaluator artifacts remain protected evidence.

Cleanup must follow `AUDIT_ARTIFACT_CACHE_POLICY.md`:
- configured audit root only;
- sentinel ownership marker;
- canonical absolute paths;
- strict descendant checks;
- per-batch ownership manifest;
- traversal/symlink/junction/reparse escape rejection;
- unknown/unowned target => 0 deletions / STOP;
- no broad wildcard recursive cleanup;
- no `git clean -fdx` / `git clean -fdX`.

Do not commit generated contact-sheet images or bulk generated audit images into normal public Git history.

## Required outputs before visual review

Create/update machine-readable and human-readable artifacts for Wave 1, including at minimum:

- `docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_DESIGN.md`
- `docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_MANIFEST.csv`
- `docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_RESULT.md`
- `docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_RESULT.json`
- complete visual-audit index manifest for all valid images;
- all-image audit sheet set and local paths;
- individual disposable audit-image directory locator.

Before ChatGPT visual review, report:
- selected semantic-family distribution;
- experiment count;
- generated image count;
- actual WD14/Kagami/CL success/failure counts;
- per-image evaluator-reference integrity;
- provisional machine/human/blocked image counts;
- provisional machine/human/blocked pair counts;
- provisional image/pair review-reduction percentages;
- number of valid images included in visual-audit package, which must equal the valid generated-image count;
- number of valid pairs included in visual-audit package, which must equal the valid generated-pair count;
- contact-sheet local path(s);
- protected-source integrity;
- focused test/preflight result.

## Stop condition

After Wave 1 generation, evaluator routing, reports, and **full all-image visual-audit package** are complete:

**STOP and return the audit package paths. Do not start Wave 2.**

The user uploads the Wave 1 visual assets to ChatGPT. ChatGPT then performs full independent visual review and the resulting verdicts/metrics are recorded before DEV decides the next step.

DEV will use Wave 1 evidence to decide whether the next step is:
- broaden to Wave 2;
- deepen weak/high-value families;
- recalibrate machine routing;
- begin sampled auditing only for sufficiently validated machine-safe families;
- or close Issue #30 Phase 2 for diminishing returns.

## Hard prohibitions

- >80 new images in Wave 1;
- blind 2,788-entry image sweep;
- automatic seed expansion;
- Stage10 production A/B;
- production/protected `data/**` mutation;
- #32 verdict/canonical mutation;
- runtime LLM dependency;
- structural semantic AUTO truth from taggers;
- unsafe broad filesystem cleanup;
- public Git accumulation of bulk generated images;
- omitting machine-handled valid Wave 1 images from the ChatGPT visual-audit package;
- changing the frozen machine route after looking at ChatGPT visual results to make agreement appear better.

#42 remains downstream and this Wave 1 does not bypass its existing #36/#34 activation gates.
