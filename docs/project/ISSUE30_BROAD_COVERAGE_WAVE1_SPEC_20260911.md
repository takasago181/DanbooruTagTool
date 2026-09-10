# Issue #30 Broad Coverage Wave 1 Spec

Date: 2026-09-11
State: AUTHORIZED_AFTER_PREFLIGHT / MACHINE_FIRST / BROAD_MULTI_FAMILY / STAGE10_PRODUCTION_NOT_STARTED
Source Issue: #30
Working branch: `codex/issue30-calibration-design`

## Purpose

Use the already repaired Batch 2 evaluator/provenance/routing pipeline to collect broad controlled image evidence across materially different Special semantic families, while minimizing user review burden.

This is still Issue #30 Phase 2 calibration/refinement. It is **not** Stage10 production A/B.

## User intent lock

The user explicitly prefers doing useful broad generation now rather than spending a separate cycle only on the previously planned 4-image false-safe audit.

Therefore this task authorizes new generation **after mandatory preflight passes**. The previous 4-image audit is folded into Wave 1 machine-handled sampling rather than used as a blocking wait state.

## Mandatory preflight — before generating any new image

Codex must first:

1. fetch the latest live `origin/main` and merge it into `codex/issue30-calibration-design`;
2. no rebase and no force rewrite;
3. verify Batch 2 accepted evidence remains readable;
4. verify actual evaluator-success counting is artifact/result based;
5. verify per-image evaluator-reference integrity is enforced;
6. verify pair routes are calculated from actual image routes;
7. verify A/B condition comes from structured manifest, not filename guessing;
8. verify audit-cache deletion containment / sentinel / ownership-manifest / fail-closed guards required by `AUDIT_ARTIFACT_CACHE_POLICY.md`;
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

`generate -> artifact/provenance gate -> WD14 -> Kagami-24k -> CL Tagger v2.00 -> evaluator-reference integrity -> image route -> pair route -> review reduction accounting`

All three evaluators run on every valid image.

Machine evaluation must affect routing. It is not decorative telemetry.

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

Do not convert a blocked or structural case into machine-handled merely to improve the review-reduction metric.

## User-review reduction and machine false-safe audit

Do not show every generated image to the user.

After routing:

1. remove normal machine-handled pairs from the mandatory human-review contact sheet;
2. include every `HUMAN_REVIEW_REQUIRED_PAIR` that still needs semantic judgment;
3. keep `BLOCKED_PAIR` out of semantic review and report the blocker;
4. separately sample machine-handled pairs for independent false-safe visual audit:
   - at least **10% of machine-handled pairs**;
   - floor **2 pairs** when at least two machine-handled pairs exist;
   - include any suspicious/borderline machine-handled case even if this exceeds 10%;
5. the previous Batch 2 machine-handled B2-001 seed `44001` / `44002` pairs may be included in the audit sample as historical anchors without regeneration.

Machine-audit sample and human-required review may be combined into one compact user-facing contact sheet if labels/questions remain clear.

## Contact sheet UX

Only after machine triage.

Show by default:
- image(s);
- large display number;
- correct A/B marker;
- one large concrete Japanese question.

Do not show by default:
- full Prompt/Negative;
- seed;
- raw evaluator logs/scores;
- model/settings wall of text;
- internal case identifiers unless needed to resolve ambiguity.

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

## Required outputs

Create/update machine-readable and human-readable artifacts for Wave 1, including at minimum:

- `docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_DESIGN.md`
- `docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_MANIFEST.csv`
- `docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_RESULT.md`
- `docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_RESULT.json`

Report:
- selected semantic-family distribution;
- experiment count;
- generated image count;
- actual WD14/Kagami/CL success/failure counts;
- per-image evaluator-reference integrity;
- machine/human/blocked image counts;
- machine/human/blocked pair counts;
- image-level review reduction;
- pair-level review reduction;
- machine-handled audit-sample size and rationale;
- contact-sheet local path(s);
- protected-source integrity;
- focused test/preflight result.

## Stop condition

After Wave 1 generation, evaluator routing, artifact export, and report creation:

**STOP for DEV/ChatGPT review and user review of only the routed remainder/audit sample.**

Do not automatically start Wave 2.

DEV will use Wave 1 evidence to decide whether the next step is:
- broaden to Wave 2;
- deepen weak/high-value families;
- recalibrate machine routing;
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
- forcing the user to review every generated image.

#42 remains downstream and this Wave 1 does not bypass its existing #36/#34 activation gates.
