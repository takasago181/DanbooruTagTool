# STAGE 10 PREP

## 目的

Special2788の機能を実画像A/B比較で検証する。

## 現時点の重要原則

- 普段の「良い画像を作るPrompt」とテストPromptを分ける。
- 1実験につき原則1疑問。
- 比較対象以外の条件を固定する。
- Special成立の有無を画像から判定しやすくする。
- model family差を保持する。
- Promptの実出力を追跡可能にする。
- Stage10専用の採点・実験管理機能を現時点で本体へ追加しない。
- Stage9 overall Gateは完了済みだが、それだけでStage10本番A/B開始とはしない。
- unit/regression test PASSだけで実アプリ動作PASSとは扱わない。Stage10前にIssue #28 automated E2E functional testのPASSが必要。

## Stage9 → Stage10 Gate

Stage9は完了済み。

- Stage9A: Pure Composer core — PASS
- Stage9B: Candidate lanes and runtime integration — PASS / Issue #3 PASS
- Stage9C: Local UI integration — PASS
- Stage9D: Stage10 experiment hooks — PASS
- Issue #17 DEV Gate — completed
- Issue #22 independent audit — PASS / completed
- PR #27 — merged to main
- merge commit — `0f17d65e1e3c737dfacd9cfee0c9d4062b683ade`
- Issue #26 protected integrity — completed

比較条件の境界は `ComposerVariant` と `Stage9ComposerSession.comparison_snapshot()`。
Special位置、明示的なbroad support 0/1/2、role別追加セット、model-family指定のweight表記、独立LoRA入力と明示入力IDによる縮約、frontend/runtime metadataを切り替え、元variantへ復元できる。
比較結果の保存・採点・winner選定やmodel grammarの確定は行わない。

## Automated E2E Gate

Issue #28で、実アプリ主要経路を自動実行し `PASS / FAIL / BLOCKED` を機械判定する。

必須観点:
- app/session初期化
- search → Special選択 → Core反映
- semantic / co-occurrence候補登録
- common / rareそれぞれから選択
- INCLUDE / EXCLUDE / DEFAULT persistence
- manual auxiliary追加/削除
- Prompt preview / copy相当出力
- provenance / evidence
- Stage9D reversible variant → baseline復元
- stale / invalid resultからcurrent stateを保護
- GUI実行可能環境ではTk headless automation

mockだけのテストをE2E PASSとは呼ばない。local-only protected dataやGUI環境不足で必須経路を実行不能ならBLOCKEDであり、Stage10本番へ進まない。

## Stage10開始前チェック

- [x] Stage9B完了（Issue #2）
- [x] Stage9B監査PASS（Issue #3）
- [x] Stage9Cを処理（Issue #17）
- [x] Stage9Dを処理（Issue #17）
- [x] Stage9C/9D完了監査PASS（Issue #22）
- [x] Stage9全体Gate完了
- [ ] Automated E2E functional test PASS（Issue #28）
- [ ] Stage10正式handoff
- [ ] Forge Neo比較環境導入・動作確認（Issue #6）
- [ ] Multi Prompt Slots等の比較手段確認
- [ ] テストPrompt班へ正式Specialデータ提供（Issue #5）
- [ ] A/Bの固定条件定義
- [ ] metadata保存方法定義
- [x] #4 KNOWLEDGEのStage10知識整理結果を正式handoffへ反映
- [ ] model familyごとのPrompt grammar差を保持し、未検証共通化していない
- [ ] 実際に使ったPromptを各画像/結果へ追跡できる

Knowledge handoff正本: `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md`

## 現在地

Stage10本番A/Bは**未開始**。
現在はIssue #28 automated E2E動作確認を現行DEV Gateとして実施しつつ、#5 PROMPT / #6 Forge Neo TEMPの残項目を準備する段階。Issue #4 KNOWLEDGEはStage10開始前調査を完了しhandoff済み。

このchecklistを満たす前にStage10本番画像A/Bを正式開始しない。
