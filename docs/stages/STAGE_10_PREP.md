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
- Stage9B完了だけでStage10へ進まない。承認済み `docs/stage9/STAGE9_PROMPT_COMPOSER_SPEC_v1.md` ではStage9C / Stage9DまでがStage9に含まれる。

## Stage9 → Stage10 Gate

Stage9仕様は次を定義する。

- Stage9A: Pure Composer core — PASS済み
- Stage9B: Candidate lanes and runtime integration — 実装完了、Issue #3監査PASS
- Stage9C: Local UI integration — Issue #17差し戻し修正、DEV実確認待ち
- Stage9D: Stage10 experiment hooks — Issue #17差し戻し修正、DEV実確認待ち

Stage9C / 9Dの現行DEVはIssue #17。common / rare候補管理とSection 10の可逆ノブを修正対象とする。
DEVがremote branch / commit / tests / implementation reportを実確認し、#17へ完了証跡を記録するまでは未完了扱いとし、#22へhandoffしない。
その後、独立AUDIT Issue #22がPASSした時だけStage9全体Gateを完了扱いにする。Stage10は未開始。

比較条件の境界は `ComposerVariant` と `Stage9ComposerSession.comparison_snapshot()`。
Special位置、明示的なbroad support 0/1/2、role別追加セット、model-family指定のweight表記、
独立LoRA入力と明示入力IDによる縮約、frontend/runtime metadataを切り替え、元variantへ復元できる。
比較結果の保存・採点・winner選定やmodel grammarの確定は行わない。

もしDEVがStage9C/9Dの一部を不要・延期と判断する場合、暗黙に省略せず、根拠付きDecisionとStage9仕様の正式改訂を行い、`CURRENT_STATE.md` とこの文書も同じ管理作業内で更新する。その変更自体も#22監査対象に含める。

## Stage10開始前チェック

- [x] Stage9B完了（Issue #2）
- [x] Stage9B監査PASS（Issue #3）
- [ ] Stage9Cを処理（Issue #17）
- [ ] Stage9Dを処理（Issue #17）
- [ ] Stage9C/9D完了監査PASS（Issue #22）
- [ ] Stage9全体Gate完了
- [ ] Stage10正式handoff
- [ ] Forge Neo比較環境導入・動作確認（Issue #6）
- [ ] Multi Prompt Slots等の比較手段確認
- [ ] テストPrompt班へ正式Specialデータ提供（Issue #5）
- [ ] A/Bの固定条件定義
- [ ] metadata保存方法定義
- [ ] model familyごとのPrompt grammar差を保持し、未検証共通化をしていない
- [ ] 実際に使ったPromptを各画像/結果へ追跡できる

このchecklistを満たす前にStage10本番画像A/Bを正式開始しない。
