# Issue #36 exception-classifier repair contract

## Purpose
Repair the final residual English-fallback classifier after forced-JA completion.

The current residual fallback set is 1,768 rows. Audit found that many ordinary translatable tags were misclassified as `OPAQUE_SOURCE_STRING` or `PROPER_NAME_OR_QUALIFIED_LABEL`.

This phase is still UI display/search helper only. Canonical English remains authoritative for identity and Prompt generation.

## Source of truth
Start from the latest forced-JA result on `ui-ja/issue36-machine-convergence` at commit `031929c27a898ef1dbfdcb315bddaa6baecde217`.

Read Issue #36 audit checkpoint `5593398688` before implementation.

## Core rule
Do NOT treat all qualified tags or unknown single words as true English exceptions.

Reclassify every current residual fallback row using semantic intent, not syntax alone.

### Translate to Japanese when ordinary meaning is recoverable
Examples that MUST NOT remain English fallback merely because they were previously classified as opaque or qualified:
- `rectum -> 直腸`
- `rug -> ラグ` or `敷物`
- `twerking -> トゥワーク` or concise explanatory Japanese
- `february -> 2月`
- `euphemism -> 婉曲表現`
- `exorcism -> 悪魔祓い` or `除霊`
- `flatbread -> 平焼きパン`
- `floatplane -> 水上機`
- `footrest -> 足置き`
- `motorhome -> キャンピングカー`
- `monolids -> 一重まぶた`
- `sternum -> 胸骨`
- `suburb -> 郊外`
- `sunroof -> サンルーフ`
- `taskbar -> タスクバー`
- `technology -> 技術`

### Qualified labels are not automatically proper names
Parenthetical qualifiers such as `(style)`, `(object)`, `(gesture)`, `(room)`, `(animated)`, `(medium)`, `(plant)`, `(symbol)`, etc. often disambiguate ordinary concepts and SHOULD be translated when the base concept is ordinary.

Examples:
- `1980s_(style) -> 1980年代風`
- `ace_(playing_card) -> エース（トランプ）`
- `breathing_(animated) -> 呼吸アニメーション`
- `study_(room) -> 書斎`
- `stop_(gesture) -> ストップのジェスチャー`

### Keep English/original-form fallback only for true exceptions
Examples of valid residual exception classes:
- pure symbols / emoticons where Japanese adds no value,
- true character/person/artist/style names,
- franchise-specific names where transliteration/official Japanese is not available or would be less useful,
- model/product/platform identifiers such as `iphone`, `figma`, `mig-29`, `su-57`, etc.,
- genuinely opaque/malformed source strings where ordinary semantic recovery is not possible.

## Classification requirements
1. Re-evaluate ALL 1,768 residual rows.
2. Do not use underscore/parenthesis presence alone as evidence of proper-name status.
3. Do not classify an ordinary dictionary word as opaque when a clear Japanese meaning exists.
4. Prefer concise, glanceable Japanese over leaving ordinary English.
5. Adult/sexual meaning is not a reason for fallback.
6. Keep true names/identifiers intact when translation would reduce recognizability.
7. Every remaining fallback must carry one specific justified reason.

## Required outputs
- complete reclassified residual ledger,
- before/after fallback counts,
- complete merged 30,629-row translation table,
- explicit remaining exception count by reason class,
- tests covering ordinary-word recovery and qualifier handling,
- replay PASS,
- protected-boundary PASS,
- generic REVIEW/PENDING = 0,
- commit and push,
- post Issue #36 completion checkpoint.

## Success criterion
A residual fallback is acceptable only if it is a true name/identifier/symbol/opaque-source exception after semantic re-evaluation.

Do not stop merely because the previous classifier already marked a row as terminal.

## Hard boundaries
Quarantine/tests only. Do not modify production `data/**`, canonical English identity, Prompt syntax, co-occurrence data, recommendation ordering/scoring, semantic support, generation profiles/model observations, #32, #35, CURRENT_DEV_TASK, main, or Stage10 production A/B.

Production promotion remains separate and is NOT authorized by this contract.
