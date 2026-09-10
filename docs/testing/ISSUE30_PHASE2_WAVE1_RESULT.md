# Issue #30 Phase 2 first-wave result — 2026-09-10

Status: `FIRST_WAVE_COMPLETE_REVIEW_REQUIRED`

The bounded first wave completed with 12 new images and 36 evaluator runs. Machine screening is triage only; no structural success is inferred before human review.

## Counts

- Images generated: **12**
- Evaluator-complete images: **12**
- Artifact gate: **12 PASS / 0 BLOCKED**
- Human review queue: **6** protected/low-confidence images
- Experiment validity: **pending human review; failures recorded 0**

## Experiments

| ID | Special | Question | Images | Artifact | Screening classes | Review |
|---|---|---|---:|---|---|---:|
| `P2-001` | `vibrator in anus` | Does the prompt preserve the functional device-to-body-site relation? | 4 | PASS=4 | RELATION_OR_BINDING=4, COMPONENT_ONLY=4, LOW_CONFIDENCE=4 | 1 |
| `P2-002` | `holding sex toy` | Does the prompt preserve the subject-to-object holding relation? | 4 | PASS=4 | RELATION_OR_BINDING=4, LOW_CONFIDENCE=1 | 1 |
| `P2-003` | `breast expansion` | Does adding the target to Negative Prompt suppress or destabilize the anatomy-changing target? | 4 | PASS=4 | LOW_CONFIDENCE=4 | 4 |

## Generation identity

- Checkpoint: `waiIllustriousSDXL_v170.safetensors`
- Checkpoint hash: `f116b0c78ff441467b0cdc8f1936e1ed18ea31e9997c7b132b1b8db533f0bd04`
- Forge: `neo-2.29`
- Sampler/schedule: `Euler a` / `Automatic`
- Steps / CFG: `25` / `5.0`
- Resolution: `1024×1344`
- Hires / ADetailer / LoRA / Control / regional / Couple: OFF

## User review

Review asset: `C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\issue30_phase2_wave1_profile_20260910\review_queue\phase2_wave1_ab_contact_sheet.png`

Review all 12 numbered A/B images in the contact sheet. For each question, compare the same seed's A and B condition and answer `A / B / both / neither / tie / unclear`. Do not inspect raw evaluator logs.

## Decision and limitation

All three questions remain `HOLD_HUMAN_REVIEW_REQUIRED`. P2-001 and P2-002 are relation-sensitive; evaluator agreement cannot prove device/site or ownership binding. P2-003 has not yet been judged for target realization or Negative collision. No additional seeds or experiments are authorized before review.

Local-only artifact root: `C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\issue30_phase2_wave1_profile_20260910`
