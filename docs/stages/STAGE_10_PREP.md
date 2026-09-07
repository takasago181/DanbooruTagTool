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
- Stage9B: Candidate lanes and runtime integration — 現行作業
- Stage9C: Local UI integration — 未開始
- Stage9D: Stage10 experiment hooks — 未開始

Stage9は9A〜9DのGateが処理されて初めて完了とする。
Stage9C / 9Dは将来DEV Issue #17で処理する。

もしDEVがStage9C/9Dの一部を不要・延期と判断する場合、暗黙に省略せず、根拠付きDecisionとStage9仕様の正式改訂を行い、`CURRENT_STATE.md` とこの文書も同じ管理作業内で更新する。

## Stage10開始前チェック

- [ ] Stage9B完了（Issue #2）
- [ ] Stage9B監査PASS（Issue #3）
- [ ] Stage9Cを処理（Issue #17）
- [ ] Stage9Dを処理（Issue #17）
- [ ] Stage9全体の完了Gateを確認、またはStage9仕様の正式改訂を完了
- [ ] Stage10正式handoff
- [ ] Forge Neo比較環境導入・動作確認（Issue #6）
- [ ] Multi Prompt Slots等の比較手段確認
- [ ] テストPrompt班へ正式Specialデータ提供（Issue #5）
- [ ] A/Bの固定条件定義
- [ ] metadata保存方法定義
- [ ] model familyごとのPrompt grammar差を保持し、未検証共通化をしていない
- [ ] 実際に使ったPromptを各画像/結果へ追跡できる

このchecklistを満たす前にStage10本番画像A/Bを正式開始しない。
