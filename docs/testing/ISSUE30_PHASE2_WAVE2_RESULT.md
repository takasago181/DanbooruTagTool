# Issue #30 Phase 2 second-wave result — 2026-09-10

Status: `SECOND_WAVE_COMPLETE_REVIEW_REQUIRED`

The bounded second wave completed with 8 new images and 24 evaluator runs. Machine screening is triage only; no structural success is inferred before human review.

## Counts

- Images generated: **8**
- Evaluator-complete images: **8**
- Artifact gate: **8 PASS / 0 BLOCKED**
- Human review: **4 pairs / 8 images**
- Machine-selected review queue: **5** images
- Experiment validity: **pending human review; failures recorded 0**

## Experiments

| ID | Special | Question | Images | Artifact | Screening classes | Review |
|---|---|---|---:|---|---|---:|
| `P2-004` | `double dildo` | Does the count-/shape-specific tag preserve the intended exact object distinction versus a broader tag? | 4 | PASS=4 | LOW_CONFIDENCE=4 | 4 |
| `P2-005` | `anal / anal penetration` | Does the legitimate alias trigger the same visible target as the canonical English surface under identical settings? | 4 | PASS=4 | RELATION_OR_BINDING=4, COMPONENT_ONLY=4, LOW_CONFIDENCE=3 | 1 |

## Generation identity

- Checkpoint: `waiIllustriousSDXL_v170.safetensors`
- Checkpoint hash: `f116b0c78ff441467b0cdc8f1936e1ed18ea31e9997c7b132b1b8db533f0bd04`
- Forge: `neo-2.29`
- Sampler/schedule: `Euler a` / `Automatic`
- Steps / CFG: `25` / `5.0`
- Resolution: `1024×1344`
- Hires / ADetailer / LoRA / Control / regional / Couple: OFF

## User review

Review asset: `C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\issue30_phase2_wave2_20260910\review_queue\phase2_wave2_ab_contact_sheet.png`

Japanese font: `C:\Windows\Fonts\meiryo.ttc`; display check: **PASS**.

Review all 8 numbered A/B images (4 pairs) in the contact sheet. For each question, compare the same seed's A and B condition and answer `A / B / both / neither / tie / unclear`. Do not inspect raw evaluator logs.

## Decision and limitation

All declared questions remain `HOLD_HUMAN_REVIEW_REQUIRED` until human review. Evaluator output is assistive only; exact count, alias-trigger equivalence, and relation/binding semantics are not auto-promoted. No additional seeds or experiments are authorized before review.

Local-only artifact root: `C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\issue30_phase2_wave2_20260910`
