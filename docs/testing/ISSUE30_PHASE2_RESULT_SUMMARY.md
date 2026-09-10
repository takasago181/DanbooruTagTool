# Issue #30 Phase 2 pre-generation checkpoint — 2026-09-10

## RESULT

Status: `FIRST_WAVE_COMPLETE_REVIEW_REQUIRED`

The frozen Phase 1 artifacts were structurally analyzed and the bounded first
wave completed under the validated WAI17 profile. No Stage10 production A/B was
started. The pre-generation gate is preserved below as the preparation record;
the first-wave result is now the active checkpoint.

Counts:

- existing images reused: 128
- new images generated: 12
- evaluator runs: 36 (all 12 images complete across 3 evaluators)
- artifact gate: 12 PASS / 0 BLOCKED
- Phase 1 human review records reused: 19
- Phase 1 experiment-validity failures recorded: 1
- first-wave user review asset: 12 images, grouped into 6 A/B seed pairs
- runner protected queue: 6 anchor/low-confidence images

## EVIDENCE

Branch: `codex/issue30-calibration-design`

Relevant files:

- `docs/testing/ISSUE30_PHASE2_STRUCTURAL_COVERAGE.md`
- `docs/testing/ISSUE30_PHASE2_STRUCTURAL_COVERAGE.json`
- `docs/testing/ISSUE30_PHASE2_TEST_DESIGN.md`
- `docs/testing/ISSUE30_PHASE2_TEST_MANIFEST.csv`
- `tools/issue30_phase2_analysis.py`
- `tools/issue30_calibration_pilot.py`
- `tools/issue30_phase2_wave_report.py`
- `tests/test_issue30_phase2.py`

Local-only artifact root:

`C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\issue30_pilot_20260910`

Checks completed:

- Python syntax compilation passed.
- External-manifest dry-run passed: 3 cases / 12 planned images.
- Current profile Special ID validation passed for 264, 750, and 2024.
- Structural coverage analysis passed against the 128-image local run.
- First-wave generation completed with Forge API checkpoint/hash preflight passed.
- First-wave result report and numbered A/B contact sheet completed.
- Initial generation was 12 new images; a later screen-only provenance recheck reused all 12 without regeneration.

## DECISION

| Item | Decision | Reason |
|---|---|---|
| Frozen Phase 1 evidence reuse | ADOPT | 128 images and 384 raw evaluator records are available locally |
| Artifact-quality gate | ADOPT | objective image/hash/metadata/provenance checks separate one near-uniform artifact as BLOCKED |
| Experiment-validity gate | ADOPT | the known unrealized contrast is not counted as evaluator semantic evidence |
| Direct/simple-unary production AUTO | HOLD | only narrow target-presence evidence exists; Phase 1 remains provisional |
| Device/contact relation | HOLD | 4 images screened; structural success remains human-reviewed |
| Source/ownership relation | HOLD | 4 images screened; tagger agreement cannot prove ownership |
| Anatomy-changing Negative collision | HOLD | 4 images screened; target realization and Negative effect await review |
| Additional evaluator/tool installation | HOLD | existing evaluators already provide triage; unique coverage has not been demonstrated |

Still `HUMAN_REVIEW_ONLY`: relation/binding, actor/subject/object, body-site
ownership, quantity, spatial topology, insertion/contact/restraint, compound,
component-only, disagreement, and low-confidence cases.

## LIMITATION

- The coverage report does not turn the 19 target-presence observations into full semantic ground truth.
- The first wave completed, but human semantic/paired preference review is still pending; no claim is made about outcomes.
- The local raw images/evaluator outputs are not committed and remain outside GitHub.
- No result generalizes beyond the WAI Illustrious v17 / Forge Neo profile and exact prompts/settings in the manifest.

## NEXT

Next allowed action: human-review the numbered A/B contact sheet, then stop for
DEV/ChatGPT review. Do not add seeds or experiments automatically.

## BOUNDARY CONFIRMATION

- Original 128-image pilot wholesale rerun: NO
- 2,788-image sweep: NO
- Stage10 production A/B: NO
- production `data/**` modification: NO
- #32 verdict modification: NO
- canonical modification: NO
- unnecessary extension installation: NO
- runtime LLM dependency: NO
