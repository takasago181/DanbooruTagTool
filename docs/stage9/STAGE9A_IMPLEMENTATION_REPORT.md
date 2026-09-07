# Stage9A Prompt Composer Implementation Report

Date: 2026-09-07 JST

## 1. Changed items

- Added `danbooru_tag_tool/prompt_composer.py`, a pure local Composer core.
- Added `tests/test_stage9a_prompt_composer.py` with 27 focused tests.
- Copied the approved Stage9A request and specification into `docs/stage9/`.

The Composer provides `ComposerProfile`, `ComposerInput`, `SupportOverride`,
`ComposerAtom`, `ComposerPlan`, `ComposeResult`, and non-destructive warnings.
Special IDs remain the primary selection identity. Support candidates are resolved
through the existing `SupportKnowledgeStore`; canonical dedupe retains every
`SemanticSupportRelation` and provenance entry.

CORE_SUPPORT + ADDITIVE is selected by default. OPTIONAL_VARIATION,
ALTERNATIVE, and CONTEXTUAL remain suggestions unless explicitly selected or
required by an explicit profile context. User include/exclude decisions are
retained and conflicting includes generate warnings.

The baseline profile orders `RELATION` immediately after `COUNT` and `SPECIAL`
after `IDENTITY`. Both block order and Special position are profile data. The
Composer preserves Negative Prompt text, emits exact/profile-aware warnings, and
does not infer tags from text, network data, or an LLM.

## 2. Unchanged items

- Stage0 through Stage8C production behavior and accepted state
- `data/source/` and `data/special2788/`
- Ruleset2 authority and semantic routing
- Stage8C semantic CSVs and Family rules
- Stage6 statistics, ranking, and runtime index behavior
- UI integration, image generation, Stage9B/9C/9D, and Stage10
- automatic weighting, same-role thresholds, LoRA contraction, and prompt rewriting

No existing production file was modified.

## 3. New files

- `danbooru_tag_tool/prompt_composer.py`
- `tests/test_stage9a_prompt_composer.py`
- `docs/stage9/FIRST_CODEX_REQUEST_STAGE9A.txt`
- `docs/stage9/STAGE9_PROMPT_COMPOSER_SPEC_v1.md`
- this report

## 4. Backup / preservation

Existing production files were not overwritten. Stage8C protected hashes were
rechecked after implementation; all nine directly checked source/runtime/semantic
authorities matched. The approved Stage9A ZIP is preserved under
`_handoff/STAGE9A_SPEC_INCOMING_TMP/` as a read-only staging copy.

## 5. Tests executed

- Stage9A focused tests: `27 passed`
- Stage8C / Ruleset2 / source protected regression: `38 passed`
- Full existing suite: `239 passed`
- Direct protected hash checks: source, Special2788, Stage8B runtime, semantic
  support, Family support, and Ruleset2 authorities: `9 checked, 0 mismatches`

Runtime network and LLM calls are not used by the Composer.

## 6. Results

Stage9A gate: **PASS**.

The implementation remains a pure Composer core with no UI dependency. Special
identity, support provenance, deterministic block ordering, profile scope, and
non-destructive warnings are covered by tests.

## 7. Unresolved items

- The Composer is not connected to the UI or live candidate lanes.
- Co-occurrence evidence objects are accepted as explicit inputs but are not
  discovered or ranked by Stage9A.
- `ComposerProfile` values are design candidates and not image-validated.

These are intentional Stage9B/9C/9D or Stage10 boundaries.

## 8. Exact Stage9B restart point

Start Stage9B at the pure `PromptComposer.compose()` result boundary. Connect
existing semantic/search auxiliary candidates and true-AND co-occurrence
suggestions as separate `ComposerInput` lanes, preserving their evidence and
selection state. Then add persistence for user include/exclude choices and a
minimal reason display. Do not merge source lanes into one score, add UI work to
Stage9A retroactively, or begin Stage10 image A/B validation.
