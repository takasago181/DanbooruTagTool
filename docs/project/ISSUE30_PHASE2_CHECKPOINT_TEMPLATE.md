# Issue #30 Phase 2 Checkpoint Template

## RESULT

Status:
`PREPARED / RUNNING / FIRST_WAVE_COMPLETE / REVIEW_REQUIRED / BLOCKED / PHASE2_COMPLETE`

Completed:
- 
- 
- 

Counts:
- existing images reused:
- new images generated:
- evaluator runs:
- BLOCKED:
- review pairs:
- reviewed images:
- unresolved questions:

## EVIDENCE

Branch:
`<branch>`

Commit:
`<commit SHA>`

Relevant files:
- `<file>`
- `<file>`
- `<file>`

Local-only artifact root:
`<path or NONE>`

Execution identity:
- Forge Neo:
- checkpoint:
- checkpoint hash:
- sampler:
- scheduler:
- steps:
- CFG:
- resolution:
- Hires:
- ADetailer:
- LoRA:
- Control/regional:
- seeds:

Review display:
- selected Japanese font:
- Japanese display check:
- bilingual Prompt labels complete:

Tests / checks:
- 
- 

## DECISION

| Item | Decision | Reason |
|---|---|---|
| `<item>` | ADOPT / HOLD / REJECT / TARGETED_IMAGE_TEST_REQUIRED / DEFER | `<reason>` |

Current automation conclusion:
`<what can realistically reduce user work>`

Still HUMAN_REVIEW_ONLY:
- 
- 

## EXPERIMENT RESULTS

Use:
- `A_ONLY_PASS`
- `B_ONLY_PASS`
- `BOTH_PASS`
- `BOTH_FAIL`
- `TIE`
- `UNCLEAR`
- `BLOCKED`

| Experiment ID | Question | Seed | Result | Failure class | Needs review |
|---|---|---:|---|---|---|
| | | | | | |

For every user-facing review question, also record:
- `visible_pass_condition_ja`
- `visible_fail_condition_ja`
- `why_this_is_judgeable_from_one_still_image`

If these cannot be stated clearly, use `DEFER` instead of asking an abstract question.

## ARTIFACT / VALIDITY

Artifact failures:
- 

Experiment-validity failures:
- 

Contact-sheet validity:
- 

Artifact failure and experiment-validity failure are not evaluator semantic failures.

## LIMITATION

Known limitations:
- 
- 

Evaluator limitations:
- 

Evidence not yet sufficient for:
- 

No claim outside the tested model/profile/conditions is implied.

## USER REVIEW

If review is required:

Review asset:
`<contact sheet / file>`

Review pairs:
`<N>`

Reviewed images:
`<N>`

Exact Japanese question(s):
- `<what visible condition makes this PASS?>`

Question format:
`A / B / both / neither / tie / unclear`

Do not require the user to inspect raw evaluator logs or edit CSV manually.

## NEXT

Next allowed action:
`<one narrow next action>`

Stop condition reached:
`YES / NO`

If NO, reason additional work still has practical value:
`<reason>`

If additional generation is proposed:
- exact unresolved question:
- additional images:
- additional seeds:
- expected user-work reduction:
- why existing evidence is insufficient:

Do not automatically continue beyond this checkpoint when review or management decision is required.

## BOUNDARY CONFIRMATION

- Original 128-image pilot wholesale rerun: NO
- 2,788-image sweep: NO
- Stage10 production A/B: NO
- production `data/**` modification: NO
- #32 verdict modification: NO
- canonical modification: NO
- unnecessary extension installation: NO
- runtime LLM dependency: NO
