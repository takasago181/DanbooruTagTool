# Issue #30 Phase 2 Generation Batch Wave design — 2026-09-11

## RESULT

3 independent experiments, 12 new images total (A/B × 2 fixed seeds), will run as one bounded batch. No automatic seed expansion is permitted.

## EVIDENCE / SELECTION

| ID | Family | Current Specials | A/B change | Concrete PASS question | Images |
|---|---|---|---|---|---:|
| GB-001 | MULTI_SPECIAL_RETENTION | 750 `holding sex toy`, 263 `vibrator` | B adds exactly `vibrator` to A | `Bでは、手に持った性具がバイブレーターとして見え、手で持つ状態も同時に成立しているか？` | 4 |
| GB-002 | SINGLE_SUPPORT_TAG_EFFECT | 264 `vibrator in anus`, 147 `anal` | B adds exactly `anal` as body-site support | `Bでは、バイブレーターが肛門内に見えているか？` | 4 |
| GB-003 | SPECIFIC_ONLY_VS_BROAD_PLUS_SPECIFIC | 2024 `breast expansion`, 2170 `breasts` | B adds exactly broad `breasts` to specific target | `Bでは、乳房が誇張して大きくなる状態が成立しているか？` | 4 |

All IDs and Japanese meanings are confirmed in current protected project data. A/B settings are identical: Forge Neo, WAI Illustrious v17, Euler a, Automatic, 25 steps, CFG 5, 1024×1344, Hires/ADetailer/LoRA/ControlNet/regional/Couple OFF. Only the declared Positive token changes; baseline Negative is fixed.

## DEFERRED

- Exact-count: no new generic exact-count slot; `CAL-023` reuse review provides a narrow positive anchor and `P2-004` is lexical-collapse evidence.
- `ACTOR_COUNT_DISAMBIGUATION`: `CAL-023` already supplies the most concrete existing count/action anchor; broader actor-role truth remains human-review protected.
- `CAL-024 teamwork (sexual)` and `CAL-032 anus + after footjob`: still-image role/temporal interpretation is not clean enough for this batch.

## REVIEW

The user-facing contact sheet will show only a large image number, A/B marker, and one concrete Japanese question per cell. Detailed prompts, negatives, seeds, hashes, evaluator references, and Japanese token labels remain in the repository traceability report.

Expected review: 6 pairs / 12 images. Machine evaluators remain assistive triage only.

## STOP

After this batch, stop for user/DEV review. Do not add seeds, start another batch, or start Stage10 production A/B.
