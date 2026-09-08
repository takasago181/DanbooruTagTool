# CURRENT STATE

最終更新: 2026-09-08

## Current Stage

Stage 9 overall Gate 完了 / Stage10 準備Gate実施中 / automated E2E PASS

## Completed

- Stage9A: PASS。
- Stage9B: 実装完了 / Issue #3 independent audit PASS。
- Stage9C / Stage9D: Issue #17 DEV完了 / Issue #22 independent audit PASS。
- Stage9C/9D監査済みPR #27をcurrent mainへ統合済み。
  - audited head: `94c6789fc6f921b7362c0e890d3fee7f3db893a3`
  - merge commit: `0f17d65e1e3c737dfacd9cfee0c9d4062b683ade`
- Issue #26 protected integrity修正: audit PASS / main反映 / completed。
- Stage9 overall Gate: **PASS / completed**。
- Issue #4 `[Stage10][KNOWLEDGE] Test Prompt knowledge`: Stage10開始前外部調査完了 / Prompt班へhandoff済み。
  - knowledge handoff: `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md`
  - handoff commit: `e1f676f28fcf963b6b2e0942c2381458065a1a5e`
  - 残る不確定項目はStage10実画像A/BへHOLD移管。
- Issue #28 `[Stage10-PREP][DEV] Automated E2E functional test + machine verdict`: **PASS / completed**。
  - branch: `codex/issue28-e2e-verdict`
  - tested source: `fcf7b217d4270f43747cb7259aa80153e90ae45d`
  - evidence head: `04629908b38c29e3896eeca3c1fb64cf164c7142`
  - PR #33 merged to main
  - merge commit: `9504fd64ce6b4acc762f589a734d67eac6b79e93`
  - real Windows local protected-data environment / real Tk 8.6.15 / no mocked rendering
  - full suite 285 passed / exit 0 / machine verdict PASS
  - required real-Tk scenarios 3/3 PASS
  - E2Eでinvalid recommendation resultのstate破壊バグを発見し、検証完了前に候補状態を置換しない最小修正を実施。
  - Stage0 protected hash/size/path-set checks維持・PASS。
- Issue #6 `[Stage10][TEMP] Forge Neo comparison environment`: **PASS_WITH_NOTE / completed**。
  - Multi Prompt Slots fixed SHA: `b3f45b17e5a24a20b4fa04edac74e6a4fec23dfe`。
  - Forge Neo Infinite Image Browsing fixed SHA: `ced039479c2e1463c9bdb136d355e01b3dfc9279`。
  - fixed-seed A/B (Seed 5072) — PASS; PNG metadata / actual Prompt traceability — PASS; baseline regular-generation regression — PASS。
  - completion checkpoint: `docs/testing/ISSUE6_COMPLETION_CHECKPOINT_20260908.md`。
  - verification: `docs/testing/ISSUE6_EXTENSION_INSTALL_AND_VERIFICATION_20260908.md`。
  - audit: `docs/testing/ISSUE6_EXTENSION_AUDIT_20260908.md`、commit `472a219058771fe117b87d62c9d53d5402b8cff9`。
  - note: Multi Prompt Slots namespaced UI-state persistence and the approved Infinite Image Browsing declared `imageio-ffmpeg` missing-dependency bootstrap are retained as standard-install side effects; unrelated updates were not authorized。
- 常設班: 開発 / 監査 / 知識 / Prompt の4班。
- 別働横断班: ツール本体UIおよび翻訳改善班（Issue #34）。常設4班とは別枠で、実UIの視認性・操作性、日本語display/search品質、検索ノイズを監査・改善仕様化し、必要な実装はDEVへhandoffする。

## Active Work / Issues

- 現在activeなDEV実装Issue: **#35 `[UI][DEV] Japanese-first desktop UI pass (dictionary frozen)`**。
  - parent: #34 UI-JA cross-team。
  - branch: `ui-ja/issue35-ui-only`
  - UI/presentation-only。辞書本体の自動改善が別系統で進行中のため、このIssueでは `data/**`、Japanese overlay内容、Special2788内容、canonical/alias/semantic/generation-profile dataを変更しない。
  - Final Prompt以外のタグ/候補表示は、日本語がある場合 `日本語 / canonical`、ない場合 `日本語未登録 / canonical` とし、英語のみの無言fallbackをなくす。
  - `Prompt preview`等の開発的英語chromeを日本語優先へ統一する。
  - recommendation/search ranking semanticsとStage9 composition semanticsは変更しない。
  - 実装後はreal Windows Tk screenshot/manual inspectionを必須とし、automated E2Eだけで完了扱いにしない。
- #5 `[Stage10][PROMPT] Formal handoff pending`
  - #4 KNOWLEDGE handoff受領済み。
  - Stage10正式handoff / Specialデータ / 実験仕様 / 固定条件 / 自動化運用を整理する。
- #30 `[Stage10-PREP][TEMP] Forge Neo A/B automation & external-tool integration`
  - Stage10本番A/Bの手作業を可能な限り減らす臨時担当。
  - 既存導入済み拡張 → Forge Neo標準機能 → Forge Neo対応拡張 → 外部CLI/API/OSS → 不足分だけ薄いglue scriptの順で検討する。
  - A/B Prompt差し替え、固定/複数seed生成、metadata/実Prompt追跡、WD14等による一次判定、`A_WIN / B_WIN / REVIEW / BLOCKED` 振り分け、結果レポートまでを対象とする。
  - **Infrastructure pipeline: PASS_PIPELINE**。remote evidence branch `codex/issue30-automation-dry-run-20260908` / commit `f2fc7acb15f996630c9f008284d80cf3261fb32f`。
  - Forge Neo API → fixed-seed A/B 2枚生成 → `/sdapi/v1/png-info` 実metadata追跡 → WD14 `wd14-eva02.v3.large` raw confidence取得まで、user manual operations 0で通過。
  - Seed 5072 / Steps 24 / CFG 4.5 / Euler a / Automatic / 1024x1024 / `waiIllustriousSDXL_v170` を固定し、`standing` A=0.80345 / B=0.00976、`sitting` A=0.00100 / B=0.93025 を取得。これは配管診断でありwinner規則ではない。
  - Agent SchedulerはHOLD、`/sdapi/v1/options` POST・model switch・production scoringは未実施。
  - 残作業はcoverage-awareな `A_WIN / B_WIN / REVIEW / BLOCKED` routingとgolden-set検証。Issue #30自体は未完了。
- #34 `[UI-JA][CROSS] Tool UI / Japanese translation quality improvement`
  - 常設4班とは別の横断改善班。
  - 現在は辞書内容改善を凍結し、#35でUI-first改善を先行する。
  - real desktop screenshotを基準にvisual/manual UI監査、日本語表示の使い方、操作導線を改善する。
  - 検索ノイズや翻訳内容そのものの改善は辞書自動改善完了後または別Issueで扱う。

## Not Started / Do Not Start Yet

- Stage10本番画像A/B試験
- Stage10 winner/scoring logicのproduction固定
- model family別Prompt grammarの未検証共通化

## Current Gates

Stage10本番開始前に最低限必要:

1. Stage9 overall Gate — **SATISFIED**
2. #28 automated E2E functional test — **SATISFIED**
3. #4 KNOWLEDGEのStage10知識整理を正式handoffへ反映 — **SATISFIED**
4. #6 Forge Neo比較環境の導入・動作確認 — **SATISFIED / PASS_WITH_NOTE**
5. #30 Forge Neo A/B automationのexternal-tool-first構成確認 + dry run
   - infrastructure plumbing (`Forge API -> A/B -> metadata -> WD14 raw`) — **SATISFIED / PASS_PIPELINE**
   - verdict routing / REVIEW fallback / golden-set validation — **REMAINS**
6. #5 Prompt班へ正式Specialデータ・実験仕様・自動化運用をhandoff
7. Multi Prompt Slots等の比較手段確認 — **SATISFIED**
8. A/B固定条件定義
9. metadata保存方法定義 — **SATISFIED for Issue #6 baseline / handoff**
10. model family差を保持し未検証共通化していないこと
11. 実際に使ったPromptを各画像/結果へ追跡できること — **SATISFIED for Issue #6 baseline / handoff**
12. `docs/stages/STAGE_10_PREP.md` の残チェックを満たすこと

## Next Actions

1. #35を実装し、日本語-first表示・UI chrome・状態判別・関連候補可読性・resizeをUI-onlyで改善する。`data/**`は変更しない。
2. #35完了後、real Windows Tk screenshot/manual inspection + focused/regression/full suite可能範囲を確認し、#34へ結果を戻す。
3. #30はPASS_PIPELINEを土台に、WD14語彙coverageとconfidenceを使った保守的routingをgolden setで検証し、低信頼・未対応を必ずREVIEWへ逃がす。
4. #5は `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md` と #30の最終結果を正式handoffへ反映する。
5. A/B固定条件、metadata保存、実Prompt traceability、model-family差保持を最終確認する。
6. 全Gateが満たされた後にのみStage10本番A/Bへ移行する。

## Blocking / Unknown

- Stage9 blockerはなし。
- Issue #28 blockerは解消済み。functional E2EはPASS。
- E2Eはvisual-layout/manual desktop inspection、全2,788 Special総当たり、Forge同時稼働性能、画像品質を検証するものではない。
- GitHub Actions CIは未導入。#28 PASSはlocal protected-data environmentの実Tk証跡であり、CI PASSとは表現しない。
- #30のForge API / A/B生成 / metadata / WD14配管blockerは解消済み。残る#30 blockerは自動routingの妥当性・REVIEW fallback・golden-set validation。
- Stage10はまだ未開始。#30 / #5 と `STAGE_10_PREP.md` の残Gateがblocker。#6は完了済み。
- #30の自動評価は完全自動判定を前提にせず、認識困難・信頼度不足をREVIEWへ逃がす。
- #34 / #35はStage10開始Gateそのものではないが、現行UIを完成UIとして扱わない。#35では辞書内容を触らずUI-first改善を実施する。

## Source-of-Truth Rule

- このファイルは現在地の正本。
- 実作業の管理記録・完了条件・結果は対応Issueに残す。
- active DEV Issueが存在する場合のみ `docs/project/CURRENT_DEV_TASK.md` をそのIssue本文の同期ミラーとして使う。
- 現在activeなDEV Issueは **#35**。Codexは #35 と同期済み `CURRENT_DEV_TASK.md` のみを現行DEV実装として扱う。
- 新しいDEV Issueを開始する時はIssue本文 / CURRENT_STATE / CURRENT_DEV_TASKを同じ管理作業内で同期し、live照合後にCodexへhandoffする。
- Codexはprivate Issueへ直接書き込む前提ではない。repository成果を残し、DEVが確認してIssueへ証跡化する。
- Codexの完了報告だけで次Gateへ進まない。
- 仕様変更は `DECISIONS.md` またはStage仕様へ反映する。
- 共有管理ファイルは最新mainを取得してから更新し、stale copyで上書きしない。
