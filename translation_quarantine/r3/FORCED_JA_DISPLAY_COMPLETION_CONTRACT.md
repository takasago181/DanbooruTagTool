# Issue #36 forced Japanese display completion contract

## Purpose
Close the remaining UI-JA display gaps without repeatedly parking ordinary translatable tags in English fallback.

This phase is for UI display/search helper labels only. Canonical English remains authoritative for identity and Prompt generation.

## Source
Use the latest fallback-closure result on `ui-ja/issue36-machine-convergence` as input. The current residual English fallback set is the only target set.

## Core rule
For every residual fallback row, produce a Japanese display label by default.

Do NOT keep English fallback merely because:
- the tag is adult/sexual,
- the tag is a compound tag,
- the wording is slightly awkward,
- a perfect Danbooru-specific Japanese term is unavailable,
- deterministic token composition is incomplete,
- strict semantic certainty is unavailable.

The objective is glanceable Japanese UI wording, not publication-grade terminology.

## Allowed translation routes
Use, in order as useful:
1. existing Japanese assets / aliases / prior accepted wording,
2. exact deterministic mappings,
3. direct Japanese translation of the canonical meaning,
4. transparent lexical composition,
5. concise explanatory Japanese when no compact conventional term exists.

Adult tags are not a reason to refuse translation. If the canonical meaning is clear, translate it directly.

## English fallback is exceptional
Residual English fallback is allowed only when a Japanese label would be genuinely less useful than the original canonical, for example:
- pure symbols/emoticons where no useful Japanese display exists,
- proper names / product names / franchise-like labels that should remain unchanged,
- acronym/code-like tokens whose English form is the actual user-recognized label,
- genuinely untranslatable malformed/opaque source strings.

Every fallback exception must have a specific reason. Generic reasons such as `STRICT_UNRESOLVED`, `INSUFFICIENT_EVIDENCE`, `NO_SAFE_TRANSLATION`, `ADULT_TERM`, or `COMPOUND_TAG` are NOT sufficient by themselves.

## Completion criteria
- process the entire residual fallback set in one Codex run,
- generic REVIEW/PENDING = 0,
- produce Japanese for all ordinary translatable rows,
- keep only narrowly justified English fallback exceptions,
- regenerate the complete 30,629-row final table,
- emit an explicit residual fallback ledger with count and reason per row,
- report before/after Japanese coverage,
- preserve replay/protected-boundary checks,
- add focused tests proving the fallback exception policy,
- commit, push, and post an Issue #36 completion checkpoint.

## Quality bar
Reject or correct only material meaning errors: reversal, wrong object/body part/actor/target/count/direction/action-state, materially broader/narrower meaning, or a different canonical concept.

Minor awkwardness is acceptable for display-only Japanese if the meaning is quickly understandable.

## Hard boundaries
Quarantine/tests only. Do not modify production `data/**`, canonical English identity, Prompt syntax, co-occurrence data, recommendation ordering/scoring, semantic support, generation profiles/model observations, #32, #35, CURRENT_DEV_TASK, main, or Stage10 production A/B.

Production promotion remains separate and is NOT authorized by this contract.
