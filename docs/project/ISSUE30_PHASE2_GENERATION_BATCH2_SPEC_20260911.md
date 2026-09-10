# Issue #30 Phase 2 Generation Batch 2 Specification — 2026-09-11

## Status

**AUTHORIZED_AFTER_PREFLIGHT / MACHINE_FIRST / TARGET_4_TO_5_EXPERIMENTS / MAX_20_NEW_IMAGES / STAGE10_PRODUCTION_NOT_STARTED**

This contract follows acceptance of the Machine Triage Audit at commit `2660c3106d2252c8aa8f3006f2a1040fd95004db`.

The goal is not to make the user review another full batch. The required workflow is:

`generate -> artifact/provenance gate -> WD14/Kagami/CL -> evaluator-reference integrity -> machine triage -> only human-required pairs -> user review`

Chat history is not canonical.

## Restore order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #30 current body/comments
4. `docs/project/CURRENT_DEV_TASK.md`
5. `docs/project/ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT_20260911.md`
6. this file
7. latest `codex/issue30-calibration-design` evidence

## Accepted audit facts

Accepted audit commit:
- `2660c3106d2252c8aa8f3006f2a1040fd95004db`

Accepted findings:
- existing Generation Batch images: 12
- actual evaluator successes: 36/36
  - WD14: 12
  - Kagami-24k: 12
  - CL Tagger v2.00: 12
- raw evaluator artifact image-ID binding: PASS
- original Generation Batch report evaluator-reference mismatches: 33
- defect class: reporting/provenance reference defect; raw evaluator outputs themselves existed and were readable
- A/B marker integrity in the audited batch: PASS
- retrospective machine-first reduction: 0%
- reason: selected batch cases were relation/binding/body-site or low-confidence; this is a batch-selection failure for user-work reduction, not a user failure

The old 12 images must not be sent to the user again.

## Mandatory preflight fixes — before any new generation

Codex must fix/verify the measurement and reporting path before generating Batch 2.

### 1. Evaluator success counts

Do not report evaluator success as `image_count * 3` alone.

The Batch 2 report must count verified evaluator artifacts/results and expose:
- planned evaluator runs
- actual successful evaluator runs
- failed/missing evaluator runs
- per-evaluator success/failure counts
- evaluator-reference integrity PASS/FAIL

### 2. Per-image evaluator references

Every image record must reference evaluator artifacts derived from its own `image_id`.

Before machine triage:
- expected artifact path must match the image ID;
- artifact must exist/read successfully and not be an error object;
- mismatch => provenance failure; do not silently continue as machine-handled.

### 3. Pair-level routing metrics

The current audit helper contains measurement shortcuts that are only harmless for the all-human 0% audit and must not carry into Batch 2:
- `machine_handled_pairs` must be computed, not hard-coded;
- `human_required_pairs` must be computed from machine routes, not copied from historical human-review count.

For A/B experiments, user burden is measured primarily at **pair level**:
- `MACHINE_HANDLED_PAIR`: both A and B are safely machine-handled for that experiment question;
- `HUMAN_REVIEW_REQUIRED_PAIR`: either A or B needs human semantic judgment;
- `BLOCKED_PAIR`: artifact/provenance/evaluator failure prevents valid comparison.

If one image in a pair is human-required, keep the complete A/B pair available for human comparison.

Report both:
- image-level reduction
- pair-level reduction

### 4. Regression tests

Before generation, focused tests must include synthetic or fixture coverage where:
- at least one complete A/B pair becomes `MACHINE_HANDLED_PAIR`;
- at least one complete pair remains `HUMAN_REVIEW_REQUIRED_PAIR`;
- computed pair counts and reduction are non-zero where expected;
- evaluator-reference mismatch becomes BLOCKED/not machine-handled;
- A/B marker mismatch becomes `REVIEW_ASSET_INVALID / BLOCKED`.

If these preflight checks fail: **STOP with 0 new images**.

## Batch size

Target:
- **4–5 independent experiments**
- normally A/B × 2 predetermined fixed seeds
- normally **16–20 new images**

Hard cap:
- **20 new images**

Do not fill quota. If only four clean experiments exist, run four.

No automatic extra seeds.

## Experiment mix — mandatory

Do not repeat the previous mistake of selecting only cases that must all go to the user.

Batch 2 should contain both:

### A. Fresh machine-judgeable lane — target 1–2 experiments

Purpose:
Demonstrate the real end-to-end user-work reduction path on new images using narrow direct/simple-unary cases.

Selection requirements:
- direct / non-relation / simple-unary
- visually explicit in a still image
- evaluator vocabulary/coverage is adequate under existing calibrated logic
- no actor-role, ownership, body-site binding, exact-count, insertion/contact topology, compound-retention or multi-person assignment question
- target and contrast are causally clean
- not already known low-confidence
- do not invent a looser threshold merely to create machine-handled results

Prefer cases supported by existing Phase 1 AUTO-support/high-confidence evidence classes, while using a fresh bounded comparison where useful.

These cases may be removed from mandatory user review only when the complete A/B pair passes the narrow machine-handled rule and provenance checks.

No broad semantic AUTO promotion follows from this lane.

### B. High-value structural lane — target 2–3 experiments

Priority order:

1. **ACTOR_COUNT_DISAMBIGUATION**
   - previously deferred from the first Generation Batch;
   - A = Special + minimal baseline;
   - B = same + exactly one actor/count clarification;
   - success must be directly judgeable from one still image.

2. **MULTI_SPECIAL_RETENTION — clearer replacement case**
   - do not simply repeat `holding sex toy + vibrator`, whose object identity was ambiguous;
   - choose two visually distinguishable Specials with clear still-image success predicates;
   - B adds exactly one second Special, or reuse valid single-Special evidence and generate only the causally necessary comparison condition.

3. **SINGLE_SUPPORT_TAG_EFFECT — new support role/case**
   - do not repeat GB-002 `vibrator in anus + anal`, which produced BOTH_PASS and showed no tested benefit;
   - choose a known/credible failure mode where exactly one support role has a clear reason to help (visibility, geometry, actor, count, body-site clarification);
   - one support role only.

Lower priority / normally skip:
- another generic exact-count test: existing `CAL-023 double handjob` is already a narrow positive anchor;
- another `double dildo` exact-count attempt: prohibited as exact-count evidence;
- immediate repeat of broad+specific `breast expansion + breasts`: prior Batch produced BOTH_PASS with no demonstrated benefit;
- immediate repeat of `anal` vs `anal penetration`: prior Wave 2 was seed-sensitive;
- extra seeds solely to resolve GB-001 object identity: do not chase diminishing returns.

## Exact case selection

Codex may select real current Special IDs without another user approval round-trip if all conditions hold:
- current canonical ID/tag exists;
- user is not asked to manually search the dictionary;
- success question is one short concrete Japanese visual question;
- exactly one meaningful A/B variable changes;
- current evidence does not already answer the question sufficiently;
- experiment belongs to the authorized lanes above;
- total new images <=20;
- production/canonical/#32 are untouched.

Record selected IDs, rationale, expected machine/human route, and exact A/B design before generation.

## Default generation profile

Unless a separately documented experiment requires otherwise:
- Forge Neo
- WAI Illustrious v17
- Euler a
- Automatic scheduler
- Steps 25
- CFG 5
- 1024×1344 when appropriate
- predetermined fixed paired seeds
- Hires OFF
- ADetailer OFF
- LoRA OFF
- ControlNet OFF
- regional prompting OFF
- Forge Couple OFF

## Machine evaluator policy

Run on every new image unless artifact/provenance failure blocks evaluation:
- WD14
- Kagami-24k
- CL Tagger v2.00

Machine evaluation is not decorative. It must feed routing.

Allowed machine-handled lane remains narrow:
- direct / non-relation / simple-unary
- provenance complete
- required evaluator outputs valid
- existing calibrated confidence/agreement criteria satisfied
- no structural ambiguity

Always human-protected unless a separately accepted future evidence change says otherwise:
- relation / binding
- body-site ownership/correctness
- insertion/contact topology
- exact count semantics
- actor/subject/object assignment
- multi-person role assignment
- compound/multi-Special retention
- ambiguous identity/category
- evaluator disagreement / low confidence

## Contact sheet rule

Build the user-facing contact sheet **after machine triage**, not before.

Only `HUMAN_REVIEW_REQUIRED_PAIR` items appear by default.

For each human-required pair show only:
- image(s)
- large image number
- correct A/B marker
- one large concrete Japanese question

Do not show by default:
- full Prompt/Negative
- seed
- case ID
- evaluator scores/logs
- model/settings
- token glossary

Question font:
- >=24 px
- preferably 28–32 px
- Meiryo -> Yu Gothic -> MS Gothic
- tofu/square => invalid

A/B integrity:
- derive condition from structured manifest/record, not filename order or prefix guessing;
- exactly one A + one B per `(experiment, seed)` pair;
- displayed marker must match executed Prompt condition;
- all-A/all-B/duplicate/mismatch => `REVIEW_ASSET_INVALID / BLOCKED`;
- record `ab_marker_integrity_check`.

If machine triage handles every pair, no contact sheet is required.

## Required outputs

Repository evidence must include:
- Batch 2 design
- manifest
- selected experiment families + exact Special IDs
- expected machine/human route rationale
- exact Prompt/Negative/seed/settings records
- generation/artifact records
- verified per-image evaluator references
- actual evaluator success/failure counts
- machine route per image
- machine route per A/B pair
- machine-handled image/pair counts
- human-required image/pair counts
- blocked image/pair counts
- image-level and pair-level human-review reduction percentages
- false-safe/unsafe concerns if observed
- simplified contact-sheet locator for human-required subset only
- detailed traceability report
- focused test result

Suggested files:
- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH2_DESIGN.md`
- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH2_MANIFEST.csv`
- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH2_RESULT.md`
- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH2_RESULT.json`

## Execution order

1. fetch latest `origin/main`
2. merge latest main into `codex/issue30-calibration-design`; no rebase/force rewrite
3. confirm Issue #30 + CURRENT_STATE + CURRENT_DEV_TASK point to this Batch 2 contract
4. preserve audit commit `2660c3106d2252c8aa8f3006f2a1040fd95004db`
5. implement/fix evaluator-count, evaluator-reference and pair-routing metrics
6. run focused regression/preflight tests
7. if preflight PASS, choose 4–5 clean experiments under the mix rules
8. prepare manifest/questions/route expectations
9. generate the whole bounded batch without intermediate approval stops
10. artifact/provenance gate
11. run WD14/Kagami/CL
12. verify evaluator references and actual successes
13. machine triage image + pair level
14. construct contact sheet from human-required pairs only
15. run Japanese display + A/B marker checks
16. commit/push branch
17. STOP for DEV/ChatGPT; user only reviews the remaining human-required subset

## Hard boundaries

- maximum new images: 20
- no automatic seed expansion
- no 2,788-image sweep
- no original 128-image wholesale rerun
- no Stage10 production A/B
- no production `data/**` mutation
- no #32 verdict/canonical mutation
- no runtime LLM dependency
- no unnecessary extension/tool
- no machine promotion to structural semantic truth
- do not hand the user machine-handled pairs merely because they were generated
- do not claim user-work reduction from arithmetic; measure the actual routed subset

After Batch 2, STOP. DEV/ChatGPT will decide whether Issue #30 has reached diminishing returns.