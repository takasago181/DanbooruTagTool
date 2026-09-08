# Issue #36 — Final UI-JA completion contract

Status: ACTIVE FINALIZATION CONTRACT
Lane: UI-JA DATA / quarantine
Branch: `ui-ja/issue36-machine-convergence`

## User decision
The user approved the current practical-quality direction for the UI Japanese layer.

For this finalization pass:

- accept the current 26 strict-review Japanese candidates unless a concrete mistranslation/semantic inversion is found,
- translate the 137 English-fallback rows using machine translation and/or deterministic lexical composition,
- prioritize glanceable Japanese over literary perfection,
- retain English canonical as authoritative identity,
- only keep English fallback where a Japanese rendering would be materially misleading or genuinely unintelligible.

## Product intent
This Japanese text is UI display/search assistance only.
It does not control canonical identity, Prompt output, co-occurrence, recommendation behavior, semantic-support behavior, generation metadata, model behavior, or ranking.

## Required final states
Every row in the 556-row table must end in one of:

- `JA_ACCEPT`
- `ENGLISH_FALLBACK_EXCEPTION`

No unresolved `REVIEW` state should remain.

## Finalization policy
1. Carry forward the existing 393 accepted Japanese rows.
2. Revisit the 26 strict-review rows and accept the existing candidate unless there is a specific concrete defect.
3. For the 137 fallback rows, generate a concise Japanese display label and a minimal Japanese search term.
4. Allow machine translation and deterministic composition.
5. Minor awkwardness is acceptable if meaning is obvious at a glance.
6. Reject only concrete defects such as semantic inversion, material broadening/narrowing, added actor/target/relation/body site/count/direction, or nonsense.
7. Symbols/emoticons may remain canonical if there is no useful Japanese label; this is not a blocker.
8. Preserve canonical English in all records.

## Required artifacts
Produce a final quarantine run directory containing:

- final 556-row table CSV and Markdown,
- accepted Japanese count,
- English fallback exception count,
- list of any fallback exceptions with exact reason,
- before/after protected boundary evidence,
- replay/reproducibility evidence,
- focused tests,
- final report.

The final user-facing table must contain:

- canonical
- display_ja
- search_ja
- final_state
- route
- reason
- risk_class

## Safety boundaries
Do not modify:

- production `data/**`
- canonical English identity
- Prompt syntax
- co-occurrence data/counts
- recommendation scoring/order
- semantic-support relations/classes/slots
- generation profiles/families/model observations
- #32 meaning/generation verdicts
- #35 UI code/tests
- `CURRENT_DEV_TASK.md`
- main branch
- Stage10 production A/B state

Quarantine only. No production promotion or main merge.

## Completion
Stop only when:

- all 556 rows are terminal,
- no generic `REVIEW` remains,
- focused tests pass,
- protected boundary is unchanged,
- final artifacts are committed and pushed,
- the final report contains exact counts and the full user-facing table path.
