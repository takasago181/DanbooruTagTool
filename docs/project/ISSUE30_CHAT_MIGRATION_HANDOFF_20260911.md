# Issue #30 Chat Migration Handoff — 2026-09-11

## Purpose

この文書は DanbooruTagTool / Issue #30 の担当チャット移行用checkpointである。

チャット履歴を正本にしない。新しいチャットは、まずGitHub正本から現在地を復元すること。

このhandoffは task contract を新しく作るものではない。現行task contractは Issue #30 本文、`docs/project/CURRENT_DEV_TASK.md`、`docs/project/ISSUE30_PHASE2_GENERATION_BATCH2_SPEC_20260911.md` を優先する。

---

## Restore Order — new chat must read in this order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #30 current body + latest checkpoints
4. `docs/project/CURRENT_DEV_TASK.md`
5. `docs/project/ISSUE30_PHASE2_GENERATION_BATCH2_SPEC_20260911.md`
6. Machine Triage Audit commit `2660c3106d2252c8aa8f3006f2a1040fd95004db`
7. `docs/testing/ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT.md`
8. `docs/testing/ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT.json`
9. 必要な場合だけ過去Phase 2 evidenceを参照する

Migration時点のmain確認SHA:
- `10f91e0491c3a0c98d0f240f0c9e209327e97e6e`

Migration時点のCodex branch:
- `codex/issue30-calibration-design`
- HEAD `2660c3106d2252c8aa8f3006f2a1040fd95004db`

新チャット開始時には、上記SHAを最新値と決め打ちせず、必ずlive main / Issue / branchを再取得する。

---

## Current State

Current Core DEV:
- Issue #30
- `PHASE2_TARGETED_REFINEMENT`
- `GENERATION_BATCH2_MACHINE_FIRST`
- Stage10 production A/B: **NOT STARTED**

Current continuation contract:
- `docs/project/ISSUE30_PHASE2_GENERATION_BATCH2_SPEC_20260911.md`

State:
- **Generation Batch 2 authorized only after preflight passes**
- Codex has not yet executed Batch 2 at migration time

Issue #42 remains downstream and is still gated by material #36 V5 / #34 work completion or explicit separation. #30 does not bypass that Gate.

---

## Completed Evidence — do not repeat

### Phase 1

Frozen representative calibration:
- 32 Special cases
- 128 generated images
- WD14 / Kagami-24k / CL Tagger v2.00 each 128/128
- machine taggers are assistive triage, not Special semantic ground truth
- structural relation/binding/count/body-site etc. remain human-protected

Do not rerun the original 128-image pilot wholesale.

### Phase 2 Wave 1

Human-reviewed evidence preserved.
Key conclusions include:
- relation/binding examples showed machine component detection is insufficient for semantic truth
- no broad structural AUTO promotion

### Phase 2 Wave 2

Human-reviewed.
Important carry-forward:
- `double dildo` was not a clean exact-count test; preserve as shape/lexical-collapse evidence only
- `anal` vs `anal penetration` was seed-sensitive; no stable equivalence conclusion

### Reuse-only review

Commit:
- `44c3874ea6083590db256f819d5445501c49ff60`

Result:
- `CAL-023 double handjob`
- 2 pairs / 4 existing images
- both `A_ONLY_PASS`
- new generation 0
- evaluator rerun 0

Use only as a narrow positive count/action anchor. Do not generalize count semantics to AUTO.

### First Generation Batch

Execution:
- `6e19da24a9718691b3c2e726bbe256fcb69f4a68`

Human review:
- `4a3e6ef5d19b33b5482bcfc86cc362ad6cbad9f3`

Result:
- 3 experiments
- 12 new images
- 6 A/B pairs
- GB-001: 2 × `UNCLEAR`
- GB-002: 2 × `BOTH_PASS`
- GB-003: 2 × `BOTH_PASS`

Problem discovered afterward:
- all 12 images had been routed to human review from the beginning
- therefore machine evaluation did not reduce user workload
- this violated the intended workflow even though evaluators had run

Do not ask the user to review these 12 images again.

### Machine Triage Audit

Commit:
- `2660c3106d2252c8aa8f3006f2a1040fd95004db`

Accepted by DEV.

Verified facts:
- existing batch images: 12
- actual successful evaluator results: **36/36**
  - WD14: 12
  - Kagami-24k: 12
  - CL Tagger v2.00: 12
- raw evaluator image-ID binding: **PASS**
- old report evaluator reference mismatches: **33**
- defect was reporting/provenance reference mapping, not missing evaluator execution
- A/B marker integrity: **PASS**
- retrospective machine-first human-review reduction: **0%**

0% reason:
- previous batch contained only `RELATION_OR_BINDING` or `LOW_CONFIDENCE` cases
- it was a test-selection/user-work-reduction design failure, not a failure by the user

Important audit-code observation found during DEV review:
- `machine_handled_pairs` had been hard-coded to 0
- `human_required_pairs` reused historical human-review count rather than actual pair routes
- these do not alter the old batch's 0% result because all 12 truly remained human-required, but they must be fixed before Batch 2 so future reduction metrics are real

---

## User Intent — preserve exactly

The user does **not** want every generated image manually judged.

Intended workflow:

`generate -> artifact/provenance gate -> WD14/Kagami/CL -> evaluator-reference integrity -> machine triage -> remove safe machine-handled pairs -> user reviews only unresolved/structural remainder`

Machine evaluation must change routing. It is not decorative.

If 20 images are generated and safe machine triage can remove 8 images / corresponding complete pairs, the user should receive only the remaining human-required review items.

Do not send machine-handled items to the user merely because they were generated.

At the same time, do not over-promote machine judgment. Structural semantics remain human-protected.

---

## Batch 2 — current authorized plan

Target:
- **4–5 independent experiments**
- normally **16–20 new images**
- hard cap **20 new images**
- normally A/B × 2 predetermined fixed seeds
- no automatic seed expansion
- quota filling prohibited

Mandatory mix:
- **1–2 fresh direct/simple-unary machine-judgeable experiments**
- **2–3 high-value structural experiments**

Purpose of direct/simple-unary cases:
- demonstrate that machine-first routing can actually remove some user work when appropriate

Structural priority:
1. `ACTOR_COUNT_DISAMBIGUATION`
2. clearer replacement `MULTI_SPECIAL_RETENTION`
3. new `SINGLE_SUPPORT_TAG_EFFECT`

Do not repeat merely for volume:
- generic exact-count repeat
- `double dildo` as exact-count test
- `breast expansion + breasts`
- `anal` vs `anal penetration`
- ambiguous `holding sex toy + vibrator`
- extra seeds just to chase GB-001 identity ambiguity

Codex may select exact real current Special IDs from canonical data. Do not make the user search 2,788 entries.

---

## Batch 2 mandatory preflight — no generation before PASS

Before generating any new image, Codex must fix/verify:

1. Fetch latest `origin/main` and merge into `codex/issue30-calibration-design`.
   - no rebase/force rewrite
2. evaluator success/failure counts must come from verified real artifacts/results, not `images * 3` arithmetic alone
3. per-image evaluator references must map to the correct image ID
4. any provenance reference mismatch must BLOCK handoff
5. `machine_handled_pairs` must be computed from actual pair routes
6. `human_required_pairs` must be computed from actual pair routes, not copied from historical review counts
7. calculate both image-level and pair-level human-review reduction
8. regression/fixture must include at least:
   - one machine-handled A/B pair
   - one human-required A/B pair
9. A/B marker integrity must come from structured manifest/condition
10. all-A / all-B / duplicate / mismatched A/B -> BLOCKED

If any preflight requirement fails:
- STOP
- new images = 0

---

## Machine routing policy

Machine-handled candidate is narrow:
- direct
- non-relation
- simple-unary
- complete provenance
- valid evaluator outputs
- sufficient existing calibrated agreement/confidence
- no structural ambiguity

Human review remains required for:
- relation / binding
- body-site correctness / ownership
- insertion / contact topology
- exact-count semantics
- actor / subject / object assignment
- multi-person role assignment
- compound / multi-Special retention
- ambiguous identity/category
- evaluator disagreement
- low confidence

Component presence is not proof of relation/binding truth.

---

## User-facing Review UX — important corrections

The user complained that review questions were too small and the sheet contained unnecessary detail.

Current rule:
- contact sheet is built **after machine triage**
- only human-required pairs appear by default

Show only:
- image(s)
- large image number
- correct A/B marker when needed
- one large, concrete Japanese question

Do not clutter with:
- full Positive Prompt
- full Negative Prompt
- seed
- case ID
- evaluator scores/logs
- model/settings
- bilingual token glossary

Question font:
- >=24 px
- preferably 28–32 px

Japanese font priority:
1. Meiryo
2. Yu Gothic
3. MS Gothic

Tofu/square glyph fallback -> invalid review asset.

A/B correction:
- a previous sheet displayed every sample as `B`
- next sheets must derive A/B from structured manifest/condition, not filename sort/order
- each `(experiment, seed)` pair must contain exactly one A + one B
- all-A / all-B / mismatch -> `REVIEW_ASSET_INVALID / BLOCKED`
- user is not responsible for checking metadata correctness manually

Prompt/provenance detail remains fully recorded in repository Markdown/JSON/manifest, just not shown on the quick review sheet.

---

## Next Action at Migration Point

No additional design discussion is required before Codex unless live GitHub state changed.

The next operational step is:

**Codex executes Issue #30 Generation Batch 2 from the latest `CURRENT_DEV_TASK.md`, beginning with mandatory preflight fixes.**

User can instruct Codex with:

`最新mainを取得して、CURRENT_DEV_TASK.mdからIssue #30を継続して。`

When Codex returns:

1. do not trust the completion report alone
2. fetch live main / Issue #30 / CURRENT_STATE / CURRENT_DEV_TASK / Batch2 spec
3. inspect branch HEAD and commits
4. verify preflight fixes actually exist
5. verify new images <=20
6. verify 4–5 experiments unless valid skip reasons reduce it; no quota filling
7. verify mandatory mix includes machine-judgeable + structural
8. verify real evaluator success and per-image provenance
9. verify image-level + pair-level routing metrics
10. verify only HUMAN_REVIEW_REQUIRED_PAIR items are on contact sheet
11. verify A/B markers and large Japanese questions
12. if user review is needed, ask only about the reduced remainder
13. after user review, record results to GitHub
14. then decide Issue #30 Phase 2 close vs one final justified action; do not automatically start another wave

---

## Stop / Safety Boundaries

Do not:
- rerun the 128-image Phase1 wholesale
- sweep 2,788 images
- exceed 20 new images in Batch 2
- add seeds automatically
- start Stage10 production A/B
- mutate production `data/**`
- change #32 verdicts/canonical values
- add runtime LLM dependency
- install unnecessary extensions
- promote structural semantic truth from tagger component detection
- make the user manually search Special2788
- make the user re-review already completed images

---

## Chat Migration Rule

This file exists only to prevent context loss during chat migration.

New chat must reconstruct from live GitHub and continue from the current Issue #30 contract. If live GitHub differs from this handoff, live GitHub wins.
