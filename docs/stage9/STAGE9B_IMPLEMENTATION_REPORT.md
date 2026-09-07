# Stage9B Runtime Composer Implementation Report

Date: 2026-09-08 JST
Current DEV Issue: #2 `[Stage9B][DEV] Runtime Composer Stage9B`
Status: IMPLEMENTATION AND TESTS COMPLETE — awaiting independent audit #3

## 1. Changed items

- Added `danbooru_tag_tool/stage9b_runtime.py`.
  - Adapts existing Stage8A classified semantic/search auxiliary candidates into the separate `SEMANTIC_AUX` Composer lane.
  - Adapts existing Stage6 true-AND recommendation candidates into the separate default-off `COOCCURRENCE` lane.
  - Copies raw statistical facts and optional snapshot identity without calculating a combined semantic/statistical score.
  - Adds stable candidate IDs, a rank-independent `Stage9BSelectionState`, and explicit INCLUDE/EXCLUDE decisions that callers retain across recompose calls.
  - Maps only approved Stage8A semantic-role metadata to Composer blocks; it never infers a role from tag text.
- Extended `ComposerInput` with a supplied reason and strengthened canonical render dedupe in `prompt_composer.py`.
  - A selected same-canonical atom merges all lanes, provenance, and evidence into the one rendered atom.
  - A suppressed same-canonical atom remains in the plan and records its merge reason.
- Added `tests/test_stage9b_runtime.py` with focused Stage9B coverage.

## 2. Explicitly unchanged protected surfaces

- `data/source/` and `data/special2788/`
- Stage0-8B source identity/data authority
- Ruleset2 authority
- Stage8C semantic support rows, family rules, and review decisions
- Stage6 statistics formulas, ranking, runtime index, and raw recommendation values
- Stage7/8 UI and local application flow
- Prompt block ordering/profile grammar, automatic weighting, LoRA contraction, and Stage10 logic

## 3. Runtime behavior

- `SEMANTIC_AUX` and `COOCCURRENCE` stay separate lanes. No combined score exists.
- Both Stage9B lanes are default-off suggestions. A co-occurrence ranking never auto-selects a tag.
- User decisions are keyed by stable candidate ID, never by current rank/index.
- Same-canonical candidates render once when selected while retaining every lane's evidence/provenance in the output atom.
- Special IDs remain independently selected first-class identities and are never replaced by a lane candidate.
- The adapter is pure local code: no UI, network, LLM, Stage10 experiment runner, or model-family grammar unification was added.

## 4. Tests executed

- Stage9A regression + Stage9B focused:
  - `python -m pytest -q tests/test_stage9a_prompt_composer.py tests/test_stage9b_runtime.py`
  - **36 passed**
- Stage8C / Ruleset2 regression:
  - `python -m pytest -q --basetemp .pytest-stage9b-ruleset2 tests/test_ruleset2_integration.py tests/test_stage8c_phase0.py tests/test_stage8c_pilot001.py`
  - **34 passed**
- Full suite, verified as an exhaustive partition because the default Windows temp directory is inaccessible:
  - existing Stage0-8C: **208 passed**
  - Stage9A/9B/static data: **40 passed**
  - total: **248 passed**
- Protected hash / identity regression:
  - `python -m pytest -q --basetemp .pytest-stage9b-protected tests/test_stage0_integrity.py tests/test_stage3_knowledge.py tests/test_generation_profile.py tests/test_stage8c_phase0.py tests/test_stage8c_pilot001.py tests/test_ruleset2_integration.py`
  - **108 passed**
- `git diff --check`: PASS.

## 5. Test coverage added for Stage9B

- semantic lane delivery, reason, and evidence
- true-AND co-occurrence default-off behavior and explicit INCLUDE rendering
- INCLUDE/EXCLUDE persistence across recompose and candidate ordering changes
- same-canonical multi-lane render dedupe with complete provenance/evidence retention
- Special identity survival under lane exclusions
- approved-role mapping without tag-text role guessing
- deterministic output and absence of score mixing
- Stage9A negative-conflict and model-profile scope regression
- no network/LLM dependency

## 6. Unresolved items / intentional boundary

- The selection state is a pure persistable value object. Storage and UI controls belong to Stage9C, not Stage9B.
- This adapter consumes existing Stage6/Stage8 candidate objects. Candidate discovery/ranking and UI delivery are not reimplemented.
- The GitHub Issue #2 checkpoint comment was not written: `gh` is not installed and the current mirror policy explicitly avoids requiring private Issue authentication. No Issue content or mirror was guessed or modified.

## 7. Audit #3 checklist

- Verify that both runtime lanes remain distinct and that no combined score is introduced.
- Verify raw co-occurrence evidence is copied unchanged, including snapshot identity when supplied.
- Verify rank-independent INCLUDE/EXCLUDE decisions and same-canonical provenance/evidence merging.
- Verify Special identities, negative conflicts, profile scope, and deterministic rendering remain intact.
- Verify no UI, Stage10 knowledge/experiments, model-family grammar rule, or protected authority change was introduced.

## 8. Exact stopping point

Stage9B implementation and regression testing are complete. Stop here and hand the feature branch to Issue #3 for independent Stage9B audit. Do not begin Stage9C, Stage9D, Stage10, image A/B testing, Prompt grammar decisions, or UI integration unless #3 passes and a later DEV gate promotes the work.
