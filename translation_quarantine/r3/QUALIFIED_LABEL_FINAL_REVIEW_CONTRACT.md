# Issue #36 qualified-label final review contract

## Purpose
Perform one final bounded review of the residual English fallback set after the exception-classifier repair, focusing on `PROPER_NAME_OR_QUALIFIED_LABEL` rows that still contain a translatable ordinary concept plus a franchise / source / role / qualifier.

This remains UI display/search-helper work only. Canonical English stays authoritative for identity and Prompt generation.

## Source
Use the latest result on branch `ui-ja/issue36-machine-convergence` after commit `61ae092d31c60c544a3e61abb219515f64b1a719`.

Current residual English fallback count: **876**.
Current `PROPER_NAME_OR_QUALIFIED_LABEL` count: **731**.

## Core rule
Do not treat a row as untranslatable merely because it contains a proper-name qualifier or parentheses.

For each residual `PROPER_NAME_OR_QUALIFIED_LABEL` row, separate:
1. the ordinary/translatable concept, and
2. the proper-name / franchise / character / artist / model / source qualifier.

If the ordinary concept is meaningful on its own, translate that concept and preserve the proper-name qualifier in original or recognized form.

Examples of desired behavior:
- `human_(warcraft)` -> Japanese for `human` + `(Warcraft)`
- `hydro_symbol_(genshin_impact)` -> Japanese for `hydro symbol` + `(Genshin Impact / 原神)`
- `advanced_ship_(eve_online)` -> Japanese for `advanced ship` + `(EVE Online)`
- `ace_(playing_card)` -> `エース（トランプ）`
- `1980s_(style)` -> `1980年代風`
- `study_(room)` -> `書斎`

Do NOT translate away or distort true proper names where the proper name is the actual identity:
- character cosplay names,
- artist/style names,
- product/service names,
- franchise-specific named artifacts where translation would reduce recognition,
- military/model identifiers,
- symbols/emoticons.

## Translation strategy
For each residual row:
1. classify whether the base noun/action/concept is ordinary and translatable,
2. if yes, translate the base concept,
3. preserve qualifier identity with concise parentheses when useful,
4. prefer recognized Japanese franchise names if already present in repository assets, otherwise preserve original recognized name,
5. keep English/original fallback only when the whole identity is genuinely name/code/symbol-like or translation would be less useful.

Minor awkwardness is acceptable. Material semantic errors are not.

## Non-fallback reasons
The following alone are NOT sufficient reasons to keep English:
- parentheses,
- underscores,
- presence of a franchise qualifier,
- presence of a source label,
- compound structure,
- imperfect but understandable Japanese.

## Completion criteria
Process the entire current residual fallback set in one run, with special attention to the 731 `PROPER_NAME_OR_QUALIFIED_LABEL` rows.

Required outputs:
- source residual ledger,
- reviewed/reclassified ledger,
- final rows,
- residual fallback ledger with reason per row,
- complete 30,629-row merged table,
- before/after coverage,
- final fallback counts by reason,
- examples of translated-qualified rows and intentionally preserved true names,
- replay verification,
- protected-boundary verification,
- focused tests.

Generic REVIEW/PENDING must remain 0.

## Focused tests
At minimum prove:
- `human_(warcraft)` is no longer English fallback,
- `hydro_symbol_(genshin_impact)` is no longer English fallback,
- `advanced_ship_(eve_online)` is no longer English fallback,
- character cosplay names remain original/properly preserved,
- artist/style names remain preserved when the name itself is the identity,
- code/model identifiers and symbols remain fallback/original,
- full table has exactly 30,629 unique canonicals,
- replay PASS,
- protected boundary PASS,
- production unchanged.

## Hard boundaries
Quarantine/tests only. Do not modify production `data/**`, canonical English identity, Prompt syntax, co-occurrence data, recommendation ordering/scoring, semantic support, generation profiles/model observations, #32, #35, CURRENT_DEV_TASK, main, or Stage10 production A/B.

Production promotion remains separate and is NOT authorized by this contract.
