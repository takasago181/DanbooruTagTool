# Issue #36 — Machine-translation convergence policy

Status: ACTIVE POLICY FOR UI-JA CONVERGENCE
Lane: UI-JA DATA / quarantine
Branch: `ui-ja/issue36-r3-bulk-canary`

## Purpose
Finish the UI-JA display/search layer without turning display wording into a permanent project blocker.

This policy changes only the approval strategy for Japanese display/search helper text. It does not change canonical English tag identity, Prompt syntax, co-occurrence data, recommendation data, semantic-support data, generation metadata, model behavior, or ranking logic.

## Product intent
For this lane, Japanese is primarily a quick human-facing aid. The target quality is:

- a user can glance at the Japanese text and understand what the English canonical tag means,
- obvious mistranslations and materially misleading wording are rejected,
- minor stylistic awkwardness is acceptable initially,
- difficult or ambiguous Danbooru-specific semantics remain subject to stricter review.

Perfect literary Japanese is not required for initial completion.

## Default route
For unresolved rows, use machine translation / deterministic dictionary composition as the default candidate-generation route.

Low-risk, transparent canonicals may be accepted with a lightweight gate when all of the following hold:

1. canonical English identity is unchanged,
2. the proposed Japanese is an obvious direct rendering of the canonical components or a common lexical equivalent,
3. the result is understandable at a glance in the UI,
4. it does not reverse, materially broaden, or materially narrow the meaning,
5. it does not add a new actor, target, relation, body site, direction, count, action/state distinction, or other semantic proposition,
6. it does not conflict with an existing known Danbooru-specific meaning,
7. the row is not in a high-risk/ambiguous class requiring strict review.

Examples of candidates that should normally qualify for the lightweight route when no contradiction exists:

- `pink_hair` -> `ピンク髪`
- `night` -> `夜`
- `sunglasses` -> `サングラス`
- `apron` -> `エプロン`
- `yellow_flower` -> `黄色い花`

## Strict-review route
Keep or escalate to strict R3-style review when any of the following applies:

- Danbooru-specific idiom or non-literal canonical
- symbols/emoticons with unclear UI wording
- actor/target/body-site/direction/count/ownership/relation ambiguity
- action vs state ambiguity
- adult/anatomy wording where a mistranslation would materially change meaning
- multiple materially different candidate translations
- explanatory prose is being proposed instead of a concise label
- known regression fixtures such as `uncensored`
- a machine translation appears to broaden/narrow or reinterpret the canonical

## Display vs search
`display_ja` and `search_ja` remain distinct.

### display_ja
Primary goal: glanceable meaning in the UI.
Minor stylistic awkwardness is acceptable if meaning is clear and not misleading.

### search_ja
Primary goal: help the user find the canonical with natural Japanese queries.
Search synonyms may be broader in surface form than display wording, but must not resolve to a different canonical meaning.

A display translation may be accepted even when extra search synonyms are not yet available. Lack of rich search synonyms must not block basic display completion.

## Completion / convergence rule
Do not require every row to satisfy the previous strict semantic-authority path before UI-JA can be considered complete.

Target convergence order:

1. auto-fill low-risk transparent rows via machine translation / deterministic composition,
2. run a lightweight audit for obvious mistranslation, contradiction, semantic inversion, material broadening/narrowing, or nonsense,
3. route only ambiguous/high-risk rows to strict review,
4. when strict review no longer produces meaningful progress, bulk-fill remaining display-only rows with clearly marked machine-translated candidates where the canonical itself remains visible and authoritative,
5. retain English canonical fallback for the genuinely unresolved tail rather than blocking completion indefinitely.

## Safety boundary
This policy must not modify or reinterpret:

- canonical English tag identity
- Prompt output syntax
- co-occurrence data or counts
- recommendation scoring/order
- semantic-support relations/classes/slots
- generation profiles/families/model observations
- #32 meaning/generation verdicts
- #35 UI code
- `CURRENT_DEV_TASK.md`
- Stage10 production A/B state

Production promotion remains a separate audited step.

## Audit priority
For the next campaign, optimize for project completion while preserving the following red lines:

- no semantic inversion
- no materially misleading label
- no canonical replacement
- no cross-lane data mutation
- no use of new candidates as semantic teachers for unrelated canonicals

Minor unnatural phrasing alone is not a blocker for the initial UI display layer if the meaning is still immediately understandable.

## Expected next execution
Run a convergence campaign over the current unresolved remainder using:

`machine candidate -> lightweight safety audit -> strict review only for flagged rows -> final fallback/freeze`

Report:
- rows auto-filled by lightweight route
- rows rejected by lightweight audit and why
- rows requiring strict review
- final English-fallback count
- obvious mistranslation count
- production_modified: NO

Stop after producing quarantine artifacts and a reviewable result. Do not promote to production or merge main.
