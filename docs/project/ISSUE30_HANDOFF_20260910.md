# Issue #30 Completion Handoff — 2026-09-10

## 0. Purpose

この文書は Issue #30 の完了状態を、次チャット / 次DEV / #42 / #5 / Stage10準備へ引き継ぐための分解済みhandoffである。

チャット履歴ではなく、GitHub上のIssue・commit・成果物を正本として扱う。

## 1. Final status

**Issue #30: COMPLETED / CALIBRATION PILOT COMPLETE / TAGGER-ASSISTED ROUTING ONLY**

Stage10 production A/Bは未開始。
2,788件sweepは実施していない。
production `data/**`、#32 verdict、canonicalは変更していない。

## 2. Core evidence anchors

- evaluator desk coverage source: Issue #44 correction checkpoint `5614819866`
- #44 machine coverage commit: `557aa4c`
- #30 handoff sync from #44: `dba23df`
- calibration design branch: `codex/issue30-calibration-design`
- screening-first design commit: `87585424e8b5dfae19b6522e60306115641526ac`
- pilot/cache safety commit: `8ff9ef142e6b7c25ae601589a82c136d96748991`
- minimal human review result commit: `5ea66ec69a7b9aeefde359997428ca5e243daf4b`

Important Issue #30 checkpoints include:
- screening-first design checkpoint: `5615347707`
- pilot completion checkpoint: latest #30 pilot completion comment
- minimal-review result checkpoint: latest #30 result comment

## 3. What was actually tested

32 representative Special cases × 4 images = 128 unique images.

Each case used:
- target-present seed A
- target-present seed B
- contrast/control seed A
- contrast/control seed B

The set intentionally included:
- simple unary
- rare/tail
- relation/binding
- actor/subject/object
- body-part/site binding
- quantity
- spatial
- insertion/contact/restraint
- compound
- component-only
- evaluator disagreement
- AUTO/REVIEW/BLOCKED controls

This was a Special Core Dictionary evaluator-calibration test, not a general healthy-image tagger benchmark.

## 4. Evaluators

All 128 images were processed by all three evaluators:

- WD14 / `wd-eva02-large-tagger-v3`: 128/128
- Kagami-24k: 128/128
- CL Tagger v2.00: 128/128

All raw outputs were preserved.

## 5. Pilot screening result

Screening classes are overlapping counts:

- LOW_CONFIDENCE: 93
- RELATION_OR_BINDING: 92
- COMPONENT_ONLY: 84
- DISAGREEMENT: 38
- BLOCKED: 20
- HIGH_CONFIDENCE_AUTO_LIKELY: 1

Final screen-only routing snapshot:

- SCREENED_AUTO_LIKELY: 1
- NOT_REVIEWED: 66
- BLOCKED: 3

Screen-only planned human-review reduction: 54.69%.

Interpretation:
- Three taggers can execute reliably as infrastructure.
- They do not provide broad semantic proof for Special Core Dictionary entries.
- Structural/relation-heavy Specials dominate the cases that cannot safely be auto-resolved.

## 6. Minimal human review result

19 high-information images were reviewed rather than the full review queue.

Result:
- target present: 16
- target absent: 1
- unclear: 2
- provisional AUTO-support candidates: 8
- HUMAN_REVIEW_ONLY: 9
- BLOCKED: 2
- UNRESOLVED: 1

The human review scope was target-concept presence and explicitly asked structural dimensions only; unasked dimensions were not inferred.

## 7. Important concrete failure examples

### 7.1 Contrast validity failure

`exposed genitals` contrast case:
- contrast image did not realize the intended experimental contrast.
- This is **generation / experiment validity failure**, not Tagger false positive.

Rule:
- invalid contrast must not be used for threshold fitting or evaluator blame.

### 7.2 Artifact quality failure

One `anus` image was gray/unobservable.

Rule:
- gray/unreadable/corrupt/metadata-missing artifacts should be rejected by an artifact-quality gate before semantic evaluator scoring.

### 7.3 Body-site / binding failure

`anal object insertion`:
- target concept existed, but another body-site interpretation also appeared.
- Therefore direct concept detection is insufficient to prove correct Special semantics.

Rule:
- body-site ownership / binding / insertion topology remains HUMAN_REVIEW_ONLY unless a future dedicated method proves otherwise.

### 7.4 Restraint-state ambiguity

`bound penis`:
- restraint state remained unclear.

Rule:
- restraint/state semantics remain HUMAN_REVIEW_ONLY / UNRESOLVED when image evidence is ambiguous.

## 8. Final evaluator policy from #30

### Keep as candidate Tagger-assisted automation

Only narrow classes such as:
- direct
- non-relation
- simple unary
- visually explicit
- complete provenance
- strong evaluator agreement

These are **AUTO-support candidates**, not production AUTO authorization.

### HUMAN_REVIEW_ONLY by default

- relation / binding
- actor/subject/object assignment
- body-part ownership / site
- quantity / multi-person assignment
- spatial direction/topology
- insertion / contact / restraint
- compound Special retention
- component-only evidence
- evaluator disagreement
- weak/low-confidence cases

### BLOCKED / EXCLUDE conditions

- evaluator execution failure
- missing required image/hash/metadata/provenance
- gray/unobservable/corrupt artifact
- no useful verified observation
- experiment contrast not valid for the intended question

## 9. What Taggers are for after #30

Adopt them as **assistive triage**, not semantic authority.

Useful roles:
- automatic pre-screening
- obvious simple-unary support
- disagreement detection
- low-confidence detection
- review prioritization
- safe abstention / routing to HUMAN REVIEW

Do not use them as:
- complete Special Core Dictionary truth
- proof of who did what to whom
- proof of correct body-site ownership
- proof of correct count/spatial topology
- proof that a compound or restraint relation is semantically correct

## 10. Optional future validation

Simple unary may receive targeted additional validation only if later product design shows meaningful manual-work savings.

Do not automatically generate more images.
Do not require every class to reach a fixed sample count.
Only validate an evidence-backed candidate class with a clear expected benefit.

## 11. Handoff to Issue #42

Issue #42 should consume these conclusions:

1. Do not design Stage10 around full Tagger automation.
2. Treat evaluator output as triage/support metadata.
3. Preserve HUMAN REVIEW for structural Special semantics.
4. Add/retain artifact-quality checks before semantic evaluation where practical.
5. Separate experiment validity failures from evaluator failures.
6. Reduce user work by prioritizing/abstaining rather than forcing binary machine verdicts.
7. Integrate this with #42 targets:
   - Japanese intent variation / search robustness
   - Special/support conflicts
   - model-family ineffective/harmful guidance
   - failure diagnosis
   - Prompt bloat/pruning
   - minimum sufficient Prompt
   - optional deterministic local history
8. Do not resurrect full automatic evaluator scoring merely because simple unary showed a few positive examples.

## 12. Handoff to Issue #5 / Stage10

#5 and final Stage10 test design should preserve:
- one experiment = one question
- fixed model/seed/settings and actual Prompt traceability
- model-family differences
- Tagger-assisted triage only
- human-review boundary for structural Specials
- artifact-quality / experiment-validity separation
- no silent conversion of REVIEW/BLOCKED into FAIL

## 13. Do not restart

Do not restart:
- Issue #44 full 2,788 evaluator coverage
- Issue #30 128-image pilot
- generic golden-set evaluation as production authority
- #32 completed dictionary validation
- 2,788-image generation sweep

Only reopen #30 if a specific future regression or evaluator-method change requires a narrowly scoped revalidation.

## 14. Next routing

Issue #30 can be closed as completed.

After closing #30, current core DEV should return to `NONE / MANAGEMENT_HANDOFF` until management explicitly activates the next DEV.

Issue #42 remains the intended next product-purpose pass, but its existing #36/#34 material UI-JA/search Gate must still be completed or explicitly separated before activation.
