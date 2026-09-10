# CURRENT DEV TASK

最終同期: 2026-09-10

## Mirror Metadata

- Source Issue: **NONE**
- State: **NO_CURRENT_DEV / MANAGEMENT_HANDOFF**
- Previous DEV: **#30** `[Stage10-PREP][COMPLETED] Forge Neo evaluator calibration & A/B automation`
- Current Stage: Stage10準備Gate実施中

## Current status

Issue #30はauthorized controlled calibrationを完了し、結果をhandoff化した。

Completion anchors:
- `docs/project/ISSUE30_HANDOFF_20260910.md`
- branch `codex/issue30-calibration-design`
- screening-first design commit `87585424e8b5dfae19b6522e60306115641526ac`
- pilot/cache commit `8ff9ef142e6b7c25ae601589a82c136d96748991`
- minimal review result commit `5ea66ec69a7b9aeefde359997428ca5e243daf4b`

#30 final policy:
- WD14 / Kagami / CLはSpecial全体のsemantic authorityにはしない
- direct / non-relation / simple unaryのみ将来の補助AUTO候補
- relation/binding / actor-object / body-site / quantity / spatial / insertion/contact/restraint / compound / component-only / disagreement / low-confidenceは原則HUMAN REVIEW
- gray/unreadable/hash/metadata/provenance欠損はsemantic評価前にBLOCKED
- invalid target/contrastはexperiment validity failureとしてevaluator failureから分離

## Next DEV selection

Issue #42は次のproduct-purpose improvement候補だが、現時点では未activate。

#42 activation前に:
1. Issue #36 V5 material UI-JA/data homeworkを完了する、またはStage10 Gateから明示分離する
2. Issue #34 material bilingual-search/search-noise concernを完了する、または明示分離する
3. managementがIssue #42本文・CURRENT_STATE・CURRENT_DEV_TASKを同一管理操作で同期する

## Codex rule

Current Core DEV = NONE の間、Codexは新しいDEV Issueを推測して開始しない。

次のcore DEV開始前に必ず:
1. latest `main` を取得
2. live Issueを確認
3. `docs/project/CURRENT_STATE.md` のcurrent core DEVを確認
4. `docs/project/CURRENT_DEV_TASK.md` Source Issueを同期
5. Issue / CURRENT_STATE / CURRENT_DEV_TASKのscope一致を確認

不一致ならSTOPして管理へ返す。

## Parallel lanes

- #36 V5 ChatGPT-led UI-JA repair/audit: independent active lane
- #34 bilingual search relevance: cross-cutting remaining concern
- #24 protected-data maintenance: parallel safety debt
- #44 KNOWLEDGE: evaluator coverage completed; scoped follow-up only

## Hard prohibitions

- Stage10 production A/Bを開始しない
- #30 128-image pilotを再実行しない
- 2,788-image sweepをしない
- production `data/**`を変更しない
- #32 verdict / canonicalを書き換えない
- TaggerをSpecial Core Dictionaryの完全なground truthへ昇格しない

Current routing authority: `docs/project/CURRENT_STATE.md`.
