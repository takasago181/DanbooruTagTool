# Issue #30 Phase 2 Generation Batch 2 result — 2026-09-11

## RESULT

Status: `BATCH2_COMPLETE_MACHINE_FIRST_REVIEW_REQUIRED`

Batch 2 completed with 16 new images. Evaluator provenance and routing were verified after generation; only human-required pairs are placed on the contact sheet.

## COUNTS

- Planned evaluator runs: **48**
- Actual successful evaluator runs: **48**
- Failed/missing evaluator runs: **0**
- Per evaluator: WD14 **16**, Kagami **16**, CL **16**
- Evaluator reference integrity: **PASS**
- Original aggregate-reference check: **FAIL** (45 mismatches; report-only repair applied: **True**)
- A/B marker integrity: **PASS**
- Machine-handled: **4 images / 2 pairs**
- Human-required: **12 images / 6 pairs**
- Blocked: **0 images / 0 pairs**
- Image-level review reduction: **25.0%**
- Pair-level review reduction: **25.0%**

## ROUTING

Pair routing is computed from the two image routes. A pair stays complete for human comparison when either A or B is human-required.

| Pair | Route | Image routes | Reasons |
|---|---|---|---|
| `B2-001:44001` | `MACHINE_HANDLED_PAIR` | `MACHINE_HANDLED_CANDIDATE, MACHINE_HANDLED_CANDIDATE` | both A and B passed narrow machine route |
| `B2-001:44002` | `MACHINE_HANDLED_PAIR` | `MACHINE_HANDLED_CANDIDATE, MACHINE_HANDLED_CANDIDATE` | both A and B passed narrow machine route |
| `B2-002:44011` | `HUMAN_REVIEW_REQUIRED_PAIR` | `HUMAN_REVIEW_REQUIRED, HUMAN_REVIEW_REQUIRED` | at least one image requires human semantic judgment |
| `B2-002:44012` | `HUMAN_REVIEW_REQUIRED_PAIR` | `HUMAN_REVIEW_REQUIRED, HUMAN_REVIEW_REQUIRED` | at least one image requires human semantic judgment |
| `B2-003:44021` | `HUMAN_REVIEW_REQUIRED_PAIR` | `HUMAN_REVIEW_REQUIRED, HUMAN_REVIEW_REQUIRED` | at least one image requires human semantic judgment |
| `B2-003:44022` | `HUMAN_REVIEW_REQUIRED_PAIR` | `HUMAN_REVIEW_REQUIRED, HUMAN_REVIEW_REQUIRED` | at least one image requires human semantic judgment |
| `B2-004:44031` | `HUMAN_REVIEW_REQUIRED_PAIR` | `HUMAN_REVIEW_REQUIRED, HUMAN_REVIEW_REQUIRED` | at least one image requires human semantic judgment |
| `B2-004:44032` | `HUMAN_REVIEW_REQUIRED_PAIR` | `HUMAN_REVIEW_REQUIRED, HUMAN_REVIEW_REQUIRED` | at least one image requires human semantic judgment |

## REVIEW

Human-required contact sheet: `C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\issue30_phase2_generation_batch2_20260911\human_required_contact_sheet.png`
Japanese font: `C:\Windows\Fonts\meiryo.ttc`; display check: **PASS**.

Machine-handled pairs are intentionally excluded from the mandatory user sheet. Detailed prompts, negatives, seeds, evaluator references, hashes, and per-image routing remain in the JSON result.

## DECISION / LIMITATION / NEXT

Machine triage remains narrow support only; it does not authorize relation, binding, body-site, count, actor-role, or compound semantic truth. Review the human-required pairs, then stop for DEV/ChatGPT Phase 2 close judgment. Do not add seeds or start Stage10 automatically.

Local-only artifact root: `C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\issue30_phase2_generation_batch2_20260911`
