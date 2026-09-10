# CURRENT DEV TASK

最終同期: 2026-09-11

## Mirror Metadata

- Source Issue: **#30** `[Stage10-PREP][PHASE2_ACTIVE] Targeted evaluator refinement before #42`
- State: **ACTIVE / PHASE2_GENERATION_BATCH2_AUTHORIZED_AFTER_PREFLIGHT / MACHINE_FIRST**
- Branch: `codex/issue30-calibration-design`
- Current Stage: Stage10準備Gate実施中

## Current continuation contract

**`docs/project/ISSUE30_PHASE2_GENERATION_BATCH2_SPEC_20260911.md`**

Machine Triage Audit is accepted evidence. Do not repeat it or re-review its 12 images.

## Accepted Phase 2 checkpoints

- Wave 1 + human review: `233a2a25b58de388cdf4ccff1183fca0a3260472`
- Wave 2 execution/human review: preserved
- Reuse-only human review: `44c3874ea6083590db256f819d5445501c49ff60`
- Generation Batch execution: `6e19da24a9718691b3c2e726bbe256fcb69f4a68`
- Generation Batch human review: `4a3e6ef5d19b33b5482bcfc86cc362ad6cbad9f3`
- Machine Triage Audit: **`2660c3106d2252c8aa8f3006f2a1040fd95004db`**

Accepted audit facts:
- 12 existing images
- actual evaluator success 36/36 = WD14 12 / Kagami 12 / CL 12
- raw evaluator image-ID binding PASS
- old report evaluator-reference mismatches 33
- A/B marker PASS
- retrospective human-review reduction 0%
- 0% reason = previous batch chose structural/relation-sensitive or low-confidence cases; not a user-review failure

## Immediate preflight — must pass before new generation

1. fetch latest `origin/main` and merge into `codex/issue30-calibration-design`; no rebase/force rewrite.
2. read `ISSUE30_PHASE2_GENERATION_BATCH2_SPEC_20260911.md`.
3. fix evaluator success reporting so success is counted from verified artifacts/results, not `images * 3` arithmetic alone.
4. keep per-image evaluator references bound to each image ID and block provenance mismatch.
5. fix pair-level routing metrics:
   - compute `machine_handled_pairs`; do not hard-code 0.
   - compute `human_required_pairs` from actual routes; do not copy historical review count.
   - compute image-level and pair-level reduction.
6. add regression/fixture coverage with at least one machine-handled A/B pair and one human-required pair.
7. A/B mismatch/all-A/all-B must block review handoff.
8. if any preflight fails: STOP with **0 new images**.

## Batch 2 purpose

Execute several useful tests in one pass while actually reducing user review through machine-first routing.

Target:
- **4–5 experiments**
- normally **16–20 new images**
- hard cap **20 new images**
- normally A/B × 2 predetermined fixed seeds
- no automatic extra seeds
- do not fill quota

Mandatory mix:
- **1–2 fresh direct/simple-unary machine-judgeable experiments** for real machine-first routing validation
- **2–3 high-value structural experiments** that genuinely require human semantic judgment

Do not select only structural cases and then send the full batch to the user.

## Structural priority

1. `ACTOR_COUNT_DISAMBIGUATION`
2. clearer `MULTI_SPECIAL_RETENTION` replacement; do not repeat ambiguous `holding sex toy + vibrator`
3. new `SINGLE_SUPPORT_TAG_EFFECT`; do not repeat GB-002 `vibrator in anus + anal`

Normally skip:
- generic exact-count repeat; `CAL-023 double handjob` is already the narrow anchor
- `double dildo` as exact-count evidence
- immediate repeat of `breast expansion + breasts`
- immediate repeat of `anal` vs `anal penetration`
- extra seeds just to chase GB-001 ambiguity

Codex may select exact real current Special IDs without asking the user to search the dictionary, provided each case meets the current spec and <=20 new images.

## Machine-first execution order

`generate -> artifact/provenance gate -> WD14/Kagami/CL -> evaluator-reference integrity -> machine triage image+pair -> human-required pairs only -> contact sheet -> user review`

Machine evaluation must affect routing; it is not decorative.

Machine-handled eligibility remains narrow:
- direct / non-relation / simple-unary
- complete provenance
- valid evaluator outputs
- existing calibrated confidence/agreement criteria satisfied
- no structural ambiguity

Human-protected:
- relation/binding
- body-site ownership/correctness
- insertion/contact topology
- exact-count semantics
- actor/subject/object assignment
- multi-person role assignment
- compound/multi-Special retention
- ambiguous identity
- disagreement/low confidence

## User review UX

Build the contact sheet **after machine triage**.

Only `HUMAN_REVIEW_REQUIRED_PAIR` items appear by default.

Show only:
- image(s)
- large number
- correct A/B marker
- one large concrete Japanese question

Do not clutter with Prompt/Negative/seed/case ID/evaluator/model/settings/token glossary.

Question font >=24 px, preferably 28–32 px. Font priority Meiryo -> Yu Gothic -> MS Gothic. Tofu/square => invalid.

A/B marker must derive from structured manifest/condition. Exactly one A + one B per pair. Mismatch/all-A/all-B => `REVIEW_ASSET_INVALID / BLOCKED`.

## Required outputs

- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH2_DESIGN.md`
- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH2_MANIFEST.csv`
- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH2_RESULT.md`
- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH2_RESULT.json`
- actual evaluator success/failure counts
- per-image evaluator-reference integrity
- image-level and pair-level machine routes
- machine-handled/human-required/blocked image + pair counts
- image-level + pair-level human-review reduction
- simplified contact sheet for human-required pairs only
- focused tests/preflight result

## Hard prohibitions

- >20 new images
- automatic seed expansion
- original 128-image wholesale rerun
- 2,788-image sweep
- Stage10 production A/B
- production `data/**` mutation
- #32 verdict/canonical mutation
- runtime LLM dependency
- unnecessary extension/tool
- machine promotion to structural semantic truth
- showing machine-handled pairs to the user merely because they were generated

After Batch 2, STOP for DEV/ChatGPT. The user reviews only the actual human-required remainder.

Current routing authority: `docs/project/CURRENT_STATE.md`.