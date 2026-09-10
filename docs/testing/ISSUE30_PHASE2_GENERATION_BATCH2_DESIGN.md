# Issue #30 Phase 2 Generation Batch 2 design — 2026-09-11

## RESULT

4 independent experiments, 16 new images total (A/B × 2 fixed seeds), will run as one bounded machine-first batch. The batch mixes one fresh direct/simple-unary lane with three structural cases. No automatic seed expansion is allowed.

## EVIDENCE / SELECTION

| ID | Family | Current Specials | A/B change | Concrete PASS question | Expected route |
|---|---|---|---|---|---|
| B2-001 | SINGLE_SUPPORT_TAG_EFFECT / direct | 263 `vibrator`, 574 `vibrator cord` | B adds one visibility/geometry support token | `AとBの両方で、バイブレーターが画像内にはっきり見えているか？` | machine-judgeable candidate |
| B2-002 | ACTOR_COUNT_DISAMBIGUATION | 20 `double footjob` | B adds one explicit actor/count clarification `2people` | `Bでは、2人または両足による足での性器刺激が成立しているか？` | human-required |
| B2-003 | MULTI_SPECIAL_RETENTION | 669 `breasts out`, 2024 `breast expansion` | B adds exactly `breast expansion` | `Bでは、露出した乳房が誇張して大きくなる状態も同時に成立しているか？` | human-required |
| B2-004 | SINGLE_SUPPORT_TAG_EFFECT / structural | 265 `vibrator on nipple`, 263 `vibrator` | B adds exactly object-identity support `vibrator` | `Bでは、乳首にバイブレーターが当たっている状態が成立しているか？` | human-required |

All IDs and Japanese meanings are confirmed in current protected project data. A/B settings are identical: Forge Neo, WAI Illustrious v17, Euler a, Automatic, 25 steps, CFG 5, 1024×1344, Hires/ADetailer/LoRA/ControlNet/regional/Couple OFF. Only the declared Positive token changes; baseline Negative is fixed.

## ROUTING / REVIEW

The runner writes image-specific evaluator references. The post-run audit verifies each raw artifact before routing. A pair is `MACHINE_HANDLED_PAIR` only when both images pass the narrow direct/non-relation/simple-unary gates; otherwise the complete pair remains `HUMAN_REVIEW_REQUIRED_PAIR`. Any provenance/evaluator failure is `BLOCKED_PAIR`.

Expected upper bound: 16 new images, 48 planned evaluator runs. Actual success counts come from verified artifacts, not arithmetic alone. The user-facing sheet is built after routing and contains only human-required pairs with large numbers, A/B markers, and concrete Japanese questions.

## DEFERRED / NOT REPEATED

- `double dildo` exact-count: retained only as lexical-collapse evidence.
- `anal` vs `anal penetration`: already seed-sensitive.
- `holding sex toy + vibrator`, `vibrator in anus + anal`, and `breast expansion + breasts`: already reviewed in Batch 1 and are not repeated.
- `teamwork (sexual)` and `anus + after footjob`: role/temporal still-image predicates remain unclear.

## STOP

After Batch 2 and the reduced human review, stop for DEV/ChatGPT. Do not add seeds, start another batch, or start Stage10 production A/B automatically.
