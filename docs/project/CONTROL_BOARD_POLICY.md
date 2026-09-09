# DanbooruTagTool 管理ボード運用方針

Status: **ADOPTED / PARALLEL MIGRATION**

採用日: 2026-09-09

## 1. 目的

Issue番号中心で現在地を追う負担を減らし、GitHub-firstの正本運用を維持したまま、GitHub Projectsを人間向けの管理画面として導入する。

この移行は既存作業を停止・再編成・振り直ししない。既存Issue、branch、checkpoint、task contract、production gateはそのまま維持する。

## 2. 役割分担

### GitHub Issue

実作業の目的・scope・禁止事項・完了条件・checkpoint・結果・証跡の正本。

### `docs/project/CURRENT_STATE.md`

全体現在地・active identity・global gate・直近遷移の正本。

移行期間中は現行形式を維持する。GitHub Projectが安定運用された後、履歴重複を減らして薄くする。

### `docs/project/CURRENT_DEV_TASK.md`

Codex用の現行DEV Issue同期ミラー。既存ルールを変更しない。

### GitHub Project「DanbooruTagTool 管理ボード」

人間向けの一覧・可視化・並び替え・依存関係確認用。

**Project単独ではtask contract、Gate承認、production変更権限を持たない。**

Issue / CURRENT_STATE / CURRENT_DEV_TASK / PERMANENT_RULESと矛盾した場合は、Project表示を正として勝手に進めず、正本側を確認する。

## 3. 日本語-first

人間が見るProject項目・View名・状態名は日本語を基本とする。

推奨項目:

- 状態: 作業中 / 待機 / 監査中 / 保留 / 完了
- 担当: 開発 / 監査 / 知識 / Prompt / 辞書 / UI・日本語 / 臨時
- 段階: 常時 / Stage10準備 / Stage10 / 保守
- 種類: 実装 / 辞書 / 監査 / 調査 / テスト / 管理
- ゲート: 未判定 / 保留 / 実行許可 / PASS / FAIL
- 優先度: 最優先 / 高 / 通常 / 低
- 短い名前: 人間向けの日本語名

推奨View:

- 今やること
- 待機中
- 監査待ち
- Stage10まで
- 担当別
- 完了履歴

## 4. Issue番号の扱い

Issue番号は「住所」として扱う。

人間向けには `生成辞書検証 (#32)`、`UI・日本語 最終収束 (#36)` のように短い日本語名を優先する。

GitHubのIssue/PR共通番号列による欠番を、作業消失や管理欠損と解釈しない。

## 5. 親子・依存関係

可能な範囲でGitHub Projects / Issue機能上の親子・依存関係を使い、本文だけに依存順序を埋め込まない。

ただし構造化作業は管理表現の改善であり、既存Issueのscope・authority・completion gateを変更しない。

## 6. 移行期間の安全ルール

1. 既存Issue本文を管理移行だけの理由で大量書換えしない。
2. 既存Issue番号を振り直さない。
3. 既存branch名を変更しない。
4. `CURRENT_DEV_TASK.md` の現行DEV #35を管理移行タスクで置換しない。
5. Projectの状態変更だけを根拠にStage/Gateを進めない。
6. production promotionは従来どおり独立Gateと監査を通す。
7. 各現行班は既存作業を止めず、そのIssueの最新contract/checkpointに従う。
8. Project作成・初期登録が未完了でも、既存GitHub-first運用は継続できる。

## 7. 全班共通通知

2026-09-09以降、現行班・関連レーンは本方針を共通管理ルールとして認識する。

- DEV
- AUDIT
- KNOWLEDGE
- PROMPT
- DICT
- UI-JA
- 現行TEMP

現在activeなIssueには導入通知checkpointを残す。
AUDITにactive Issueがない期間は、本方針と次回AUDIT Issueのtask contractから復元する。

## 8. 導入完了条件

移行完了は以下が揃った時点とする。

1. GitHub Project「DanbooruTagTool 管理ボード」作成
2. 現行Open Issue登録
3. 日本語項目・View作成
4. active / gated / reserved / completedの初期状態反映
5. 主要な親子・依存関係の登録
6. 各現行班への通知完了
7. CURRENT_STATEとの矛盾がないことを確認

完了後、別管理変更としてCURRENT_STATE / WORKSTREAMSの重複情報削減を検討する。

## 9. 設計参照

詳細設計:

`docs/project/CONTROL_BOARD_MIGRATION_DESIGN.md`
