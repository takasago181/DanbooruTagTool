# Issue #30 Phase 2 Wave 2 Execution Specification — 2026-09-10

## Status

AUTHORIZED_AFTER_PREREQUISITES / MAX_12_NEW_IMAGES / STAGE10_PRODUCTION_NOT_STARTED

This specification continues Issue #30 Phase 2 after Wave 1 human review. It does not replace the project-wide rules in `CURRENT_STATE.md`, `PERMANENT_RULES.md`, or the Phase 2 base execution specification.

## Restore order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #30 current body
4. `docs/project/CURRENT_DEV_TASK.md`
5. `docs/project/ISSUE30_PHASE2_EXECUTION_SPEC_20260910.md`
6. this file
7. Wave 1 evidence at branch `codex/issue30-calibration-design`, commit `233a2a25b58de388cdf4ccff1183fca0a3260472`

Chat history is not canonical.

## Wave 1 accepted evidence

Wave 1 is accepted for Phase 2 evidence use.

Human review summary:
- P2-001 `vibrator in anus`: both seeds `BOTH_FAIL`; device/body-site binding was not realized correctly.
- P2-002 `holding sex toy`: one `A_ONLY_PASS`, one `BOTH_PASS` with contrast contamination.
- P2-003 `breast expansion`: both seeds `BOTH_PASS`; adding the same target to Negative Prompt did not produce a consistent suppressive effect in the tested pair.

Consequences:
- relation/binding/body-site semantics remain `HUMAN_REVIEW_ONLY`.
- artifact-quality gate, bounded manifest-driven generation, evaluator triage, and numbered human review remain adopted.
- no structural AUTO promotion is authorized.

## Prerequisites before any Wave 2 generation

1. Fetch latest `origin/main`.
2. Merge latest `origin/main` into `codex/issue30-calibration-design`.
   - Do not rebase/force-rewrite preserved Issue #30 history.
   - Resolve conflicts conservatively.
   - Preserve Phase 1 and Wave 1 evidence.
3. Complete the bilingual review-display implementation.
   - User-facing review assets must show the actual executed Positive and Negative Prompt tags/tokens as `English (日本語)`.
   - Do not show only `canonical_ja`.
   - English remains the executed/canonical payload; Japanese is display-only.
4. Japanese rendering validity:
   - prefer Meiryo (`meiryo.ttc`)
   - then Yu Gothic (`YuGothM.ttc` or another installed Yu Gothic face)
   - then MS Gothic (`msgothic.ttc`)
   - a font fallback that renders Japanese as tofu/squares is invalid.
5. Regenerate the Wave 1 contact sheet without regenerating images.
6. Perform a local display sanity check and record:
   - selected font
   - Japanese label sample checked
   - display result PASS/FAIL
7. Correct report semantics so `6 review pairs = 12 reviewed images` is explicit. Do not use one ambiguous count field for both concepts.
8. Re-run Phase 2 focused tests, syntax checks, and dry-run after the merge and review-display changes.
9. Preserve `data/**`, #32 verdicts, canonical data, local-only images, and unrelated untracked user files.

If any prerequisite fails, stop before new generation.

## Wave 2 objective

Use Wave 1 plus existing Phase 1 structural coverage to test the next highest-value unresolved generation questions with the smallest useful new image set.

Priority order:

1. `EXACT_COUNT_RETENTION`
   - Test whether a count-specific Special/Prompt preserves the required exact count versus a controlled broader/less-specific condition.
   - Select a real current Special ID from canonical project data.

2. `CANONICAL_VS_ALIAS_OR_ALTERNATE_TRIGGER`
   - Compare canonical English with a legitimate known Alias/alternate surface under identical settings.
   - Preserve dictionary identity separately from generation trigger behavior.

3. `MULTI_SPECIAL_RETENTION`
   - Test whether two individually supported Specials remain jointly realized in an AB-minimal prompt.
   - Reuse compatible existing A_ONLY/B_ONLY evidence when valid.
   - If compatible single-Special evidence cannot be reused without weakening causal interpretation, defer this question rather than exceeding the Wave 2 image cap.

If existing evidence already answers a priority question well enough, skip it. Do not fill an arbitrary quota.

## Image bound and adaptive rule

- Maximum `12` new images for Wave 2.
- Start with `2` predetermined fixed seeds per comparison.
- No automatic seed expansion.
- Mixed/unclear results stop for DEV/ChatGPT review before adding seeds.
- One experiment = one primary question.
- Keep all settings fixed except the intended A/B variable.

For multi-Special experiments, compatible existing single-Special evidence should be reused first. If a clean design would require more than 12 new images in total, defer multi-Special instead of increasing the cap.

## Default generation lane

Unless the specific experiment requires otherwise:
- Forge Neo
- WAI Illustrious v17
- Euler a
- Steps 25
- CFG 5
- 1024×1344 when appropriate
- fixed paired seeds
- Hires OFF
- ADetailer OFF
- LoRA OFF
- ControlNet OFF
- regional prompting OFF
- Forge Couple OFF

Prompt-only and assisted evidence must remain separate.

## Evaluator and review policy

WD14 / Kagami-24k / CL Tagger v2.00 remain assistive triage only.

They may support:
- artifact/evaluator pre-screening
- direct/simple-unary evidence
- disagreement/low-confidence detection
- review prioritization

They must not independently authorize relation/binding/count/multi-actor semantic truth.

Human review output should remain answerable as:
- A
- B
- both
- neither
- tie
- unclear

A short observation may be requested only when needed to classify failure or experiment validity.

## Review asset requirements

The numbered contact sheet or adjacent review table must show:
- experiment ID
- A/B condition
- fixed seed
- primary question in Japanese
- relevant executed Positive Prompt tags/tokens as `English (日本語)`
- relevant executed Negative Prompt tags/tokens as `English (日本語)`
- enough information to judge the one declared question without opening raw evaluator logs

Record the selected Japanese font and display-check result in the repository result artifact when practical.

### Japanese review-question wording rule

User-facing Japanese questions must name the concrete visual predicate to judge. Avoid abstract wording such as 「同じ視覚的な対象を誘発するか」「差を保持するか」without saying what the target appearance/relation actually is.

Preferred form:
- 「AとBのどちらで、○○が成立しているか？」
- 「Aの具体タグで、Bにはない○○の形状・個数・関係が出ているか？」

For current Wave 2:
- P2-004 should be explained as: 「A=`double dildo` と B=`dildo` を比べ、Aで『2本の別々のディルド』ではなく『1本の両端型ディルド』が出ているか？」
- P2-005 should be explained as: 「A=`anal` と B=`anal penetration` を比べ、どちらで『肛門への挿入』が成立しているか？ ただ肛門が見える・広がるだけなら不成立。」

When another visible element violates the fixed prompt (for example `solo`なのに別人物が出る、target以外の追加挿入が出る), record it separately as a confound / prompt-adherence failure instead of silently treating it as equivalent target success.

P2-004 caveat: `double dildo` is a double-ended-object concept, not an exact "two separate dildos" count tag. Therefore P2-004 may provide evidence about shape-specific retention or lexical `double` misinterpretation, but it must not by itself close the general `EXACT_COUNT_RETENTION` question. If the target image shows two separate dildos rather than one double-ended dildo, record target realization as failed even though a numeric difference appeared.

P2-005 caveat: `anal` vs `anal penetration` can only support alias/alternate-trigger equivalence if the same concrete predicate is judged. Presence of an anus alone is insufficient; visible anal penetration is the primary predicate for this comparison. Fixed-prompt violations such as a male appearing despite `1girl, solo` weaken experiment validity and must be recorded.

## Required Wave 2 repository artifacts

Before generation:
- Wave 2 candidate rationale
- selected real Special IDs
- exact A/B design
- expected new-image count
- reused evidence list
- expected human-review count

After generation:
- manifest
- exact Positive/Negative Prompts
- seeds/settings/model/hash/provenance
- artifact gate
- evaluator outputs where applicable
- experiment-validity state
- bilingual contact sheet locator
- selected Japanese font + display-check result
- concise result summary
- machine-readable result record

Suggested names:
- `docs/testing/ISSUE30_PHASE2_WAVE2_TEST_DESIGN.md`
- `docs/testing/ISSUE30_PHASE2_WAVE2_TEST_MANIFEST.csv`
- `docs/testing/ISSUE30_PHASE2_WAVE2_RESULT.md`
- `docs/testing/ISSUE30_PHASE2_WAVE2_RESULT.json`

## Stop boundary

After the bounded Wave 2 is complete:
- do not add seeds automatically
- do not start another wave automatically
- do not start Stage10 production A/B
- do not modify production `data/**`
- do not modify #32 verdicts or canonical values
- do not add an evaluator/extension unless a concrete remaining gap demonstrates material user-work reduction

Commit/push the branch and stop for DEV/ChatGPT review.

## GitHub handoff

Repository report should include:
- RESULT
- EVIDENCE
- DECISION
- LIMITATION
- NEXT

Include:
- branch
- commit SHA
- changed files
- tests
- merged main SHA
- generated image count
- reused evidence/image count
- blocked count
- review-required pair/image counts separately
- local-only artifact root
- contact sheet locator
- selected Japanese font
- Japanese display-check result
- remaining uncertainty
