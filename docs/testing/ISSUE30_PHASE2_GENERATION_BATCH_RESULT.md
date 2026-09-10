# Issue #30 Phase 2 Generation Batch Wave result — 2026-09-11

## RESULT

Status: `BATCH_COMPLETE_REVIEW_REQUIRED`

3 experiments completed in one bounded batch: 12 new images and 36 evaluator runs. No automatic promotion is inferred before human review.

## EVIDENCE

- New images: **12** / reused images: **0** / blocked: **0**
- Review: **6 pairs / 12 images**
- Artifact gate: `{'PASS': 12}`
- Contact sheet: `C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\issue30_phase2_generation_batch_20260911\review_queue\generation_batch_large_question_contact_sheet.png`
- Japanese font: `C:\Windows\Fonts\meiryo.ttc`; display check: **PASS**; question font: **30 px**

| ID | Family | Special IDs | Question | Images |
|---|---|---|---|---:|
| `GB-001` | `MULTI_SPECIAL_RETENTION` | `750, 263` | Bでは、手に持った性具がバイブレーターとして見え、手で持つ状態も同時に成立しているか？ | 4 |
| `GB-002` | `SINGLE_SUPPORT_TAG_EFFECT` | `264, 147` | Bでは、バイブレーターが肛門内に見えているか？ | 4 |
| `GB-003` | `SPECIFIC_ONLY_VS_BROAD_PLUS_SPECIFIC` | `2024, 2170` | Bでは、乳房が誇張して大きくなる状態が成立しているか？ | 4 |

## Traceability

The JSON result and manifest retain exact executed Positive/Negative prompts, English canonical tokens, Japanese display labels, seeds, settings, image hashes/paths, and evaluator references. The user-facing sheet intentionally contains only the large number, A/B marker, and concrete Japanese question.

## DECISION / LIMITATION / NEXT

All three families remain `HOLD_FOR_HUMAN_REVIEW`: multi-Special retention, one support tag effect, and broad-plus-specific interaction. Relation, body-site, count, and role semantics remain human-review protected. After the 6-pair review, DEV/ChatGPT decides Phase 2 close or a separately justified final experiment. Do not add seeds or start Stage10 automatically.

Local-only artifact root: `C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\issue30_phase2_generation_batch_20260911`
