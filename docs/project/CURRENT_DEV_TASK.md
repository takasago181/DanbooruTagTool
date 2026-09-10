# CURRENT DEV TASK

最終同期: 2026-09-10

## Mirror Metadata

- Source Issue: **#30** `[Stage10-PREP][PHASE2_ACTIVE] Targeted evaluator refinement before #42`
- State: **ACTIVE / PHASE2_TARGETED_REFINEMENT**
- Branch: `codex/issue30-calibration-design`
- Previous completed phase: #30 Phase 1 representative evaluator calibration
- Current Stage: Stage10準備Gate実施中

## Purpose

Issue #30 Phase 1は完了・凍結済み。#36/#34が#42 activationを待たせている間に、Stage10でユーザー目視負担をさらに減らせるかを、既存evaluator成果を中心に狭く検証する。

Primary restore anchors:
- `docs/project/ISSUE30_HANDOFF_20260910.md` — Phase 1
- `docs/project/ISSUE30_PHASE2_HANDOFF_20260910.md` — Phase 2

Phase 1 evidence:
- screening-first design commit `87585424e8b5dfae19b6522e60306115641526ac`
- pilot/cache commit `8ff9ef142e6b7c25ae601589a82c136d96748991`
- minimal review result commit `5ea66ec69a7b9aeefde359997428ca5e243daf4b`
- 128 unique images / WD14-Kagami-CL each 128/128
- minimal review 19

## Frozen Phase 1 policy

- Taggers are assistive triage, not Special semantic authority.
- direct / non-relation / simple unaryのみ補助AUTO候補。
- relation/binding / actor-object / body-site / quantity / spatial / insertion/contact/restraint / compound / component-only / disagreement / low-confidenceは原則HUMAN REVIEW。
- gray/unreadable/corrupt/hash/metadata/provenance欠損はsemantic評価前にBLOCKED。
- invalid target/contrastはexperiment-validity failureとしてevaluator failureから分離。

## Phase 2 work

優先順:
1. 既存128-image raw outputs / metadataを再利用してthreshold/agreementを再分析する。
2. direct / non-relation / simple-unaryで実用的な補助AUTO余地が残るかを絞る。
3. review queue / prioritization / abstentionでユーザー確認数をさらに減らせるか測る。
4. gray/unreadable/corrupt/metadata failureのartifact-quality gateを改善する。
5. target/contrast不成立をexperiment-validityとして検出する方法を検討する。
6. 追加evaluator / deterministic non-LLM signalは、unique coverageまたは誤判定抑制に実益がある場合だけ調査・採用する。
7. 新規画像が必要なら一つの未解決疑問に対する最小targeted testだけ許可する。

## Decision labels

- ADOPT
- HOLD
- REJECT
- TARGETED_IMAGE_TEST_REQUIRED

## Hard prohibitions

- original 128-image pilotの全再実行禁止
- 2,788-image sweep禁止
- Stage10 production A/B禁止
- production `data/**`変更禁止
- #32 verdict / canonical変更禁止
- Tagger direct-matchをstructural Special truthへ昇格禁止
- relation/binding全面AUTO化を狙わない
- model-family flattening禁止
- 大型独自automation platform禁止

## Completion criteria

Phase 2完了時に、少なくとも以下をreviewable evidenceとして返す:
- 改善したautomation品質があるか
- realisticなuser-review削減量
- simple-unary/directのpromising/reject分類
- artifact/experiment validity gateの採否
- 追加evaluator/toolのADOPT/HOLD/REJECT
- HUMAN_REVIEW_ONLYとして残す範囲
- diminishing returnsに達したか

## Downstream

#42は依然として #36 V5 / #34 material UI/search workの完了または明示分離待ち。Phase 2はそのGateを迂回しない。

Phase 2終了後はIssue #30 checkpointとhandoffを更新し、次DEVが未選択ならCURRENT_STATE/CURRENT_DEV_TASKを再びmanagement handoffへ戻す。

## Start / continuation Gate

Codexは作業開始前に必ず:
1. latest `main` を取得
2. Issue #30がPHASE2_ACTIVEであることを確認
3. `CURRENT_STATE.md` current core DEV = #30 Phase 2 を確認
4. 本ファイル Source Issue = #30 を確認
5. scope不一致ならSTOP

Current routing authority: `docs/project/CURRENT_STATE.md`.
