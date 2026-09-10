# Issue #30 Phase 2 structural coverage — 2026-09-10

This report reuses the frozen Phase 1 pilot. It does not reinterpret the Phase 1 verdicts or promote any production AUTO rule.

## Reused evidence

- Run: `issue30-pilot-20260910`
- Existing images: **128**
- Evaluator records: **384**
- Complete three-evaluator images: **128**
- Human review records reused: **19**
- Artifact gate PASS / BLOCKED: **127 / 1**
- Experiment-validity failures recorded by human review: **1**

## Capability coverage

| Class | Cases | Images | Human-reviewed | Evaluator complete | High-confidence | Disagreement | Artifact BLOCKED | Additional value |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `BODY_SITE_STATE` | 3 | 12 | 1 | 12 | 0 | 5 | 0 | TARGETED |
| `COMPOSITE_HARD` | 4 | 16 | 1 | 16 | 0 | 0 | 0 | TARGETED |
| `MULTI_OBJECT_OR_COUNT` | 3 | 12 | 1 | 12 | 0 | 4 | 0 | NARROW_ONLY |
| `RESTRAINT_TOPOLOGY` | 1 | 4 | 1 | 4 | 0 | 2 | 0 | TARGETED |
| `SIMPLE_RELATION` | 13 | 52 | 4 | 52 | 0 | 16 | 0 | TARGETED |
| `UNARY_OBJECT_OR_STATE` | 8 | 32 | 11 | 32 | 1 | 11 | 1 | NARROW_ONLY |

## Evidence boundaries

- The 19 human records answer only whether the target concept was visible; unasked relation, ownership, count, spatial, compound, and Stage10-preference dimensions remain unlabelled.
- Evaluator disagreement and component-only observations remain triage signals. They do not authorize structural Special success.
- Artifact failures are reported as `BLOCKED` before semantic evaluation. A failed target/contrast realization is reported separately as experiment-validity failure.
- Existing evidence supports only narrow targeted questions; broad AUTO calibration is not justified.

## Recommended first-wave questions

See `ISSUE30_PHASE2_TEST_DESIGN.md` and `ISSUE30_PHASE2_TEST_MANIFEST.csv`. The selected wave is capped at 12 images: three questions, A/B paired conditions, two predetermined seeds per condition.

## Local-only source

`C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Models\Issue30Evaluators\issue30_pilot_20260910`
