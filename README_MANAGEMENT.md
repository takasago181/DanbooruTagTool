# DanbooruTagTool 管理骨格

目的は「班を増やさず、正本・進捗・引継ぎの所在を固定する」ことです。

## 役割分担

- 本体開発班: 唯一の司令塔。仕様決定、Stage管理、Codex実装指示。
- 監査班: 第三者監査。PASS / CONDITIONAL PASS / FAIL を返す。
- 知識班: 外部調査。仕様決定権は持たない。
- テストPrompt班: Stage10のA/B実験用Prompt作成。仕様決定権は持たない。
- Forge Neo環境準備: 臨時担当。Stage10比較環境の導入・動作確認後に終了。
- Codex: 班ではなく、本体開発班の実装担当。

## 正本の置き場所

- `docs/project/CURRENT_STATE.md`
  - 「今どこにいるか」の唯一の状態表。
- `docs/project/PERMANENT_RULES.md`
  - Stageをまたいで有効な固定ルール。
- `docs/project/DECISIONS.md`
  - 重要な設計判断と理由。
- `docs/stages/`
  - Stage単位の仕様・完了条件。
- GitHub Issues
  - 「これからやる仕事」。
- Pull Request
  - 「実際に変更されたコード」。

チャット履歴は正本ではありません。

## 最小運用

1. 作業を始める前に `CURRENT_STATE.md` を見る。
2. 新しい仕事はIssue化する。
3. 作業結果は該当Issueに残す。
4. 仕様が変わったら `DECISIONS.md` または Stage仕様を更新する。
5. Stage完了・方針変更・チャット移行前だけ `CURRENT_STATE.md` を更新する。
6. 監査PASS前に次Stageを正式開始しない。
7. チャット間のコピペhandoffを減らし、各チャットにはIssue番号と正本ファイルだけ渡す。

## 推奨Issue名

`[Stage9B][DEV] Runtime Composer ...`
`[Stage9B][AUDIT] Stage9B 完了監査`
`[Stage10][KNOWLEDGE] NoobAI Prompt grammar ...`
`[Stage10][PROMPT] Special単独成立 A/B Prompt`

班名をIssueタイトルにも残すことで、Projectを使わなくても検索できます。
