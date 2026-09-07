# CHAT START PROTOCOL

目的: 常設4班（DEV / AUDIT / KNOWLEDGE / PROMPT）が新しいChatGPTチャットへ移動した際、古いhandoffや旧チャットに引っ張られず、GitHub正本から同じ現在地を再構成する。

## 1. 旧チャット側で移動前に行うこと

- `docs/project/CURRENT_STATE.md` を最新化する。
- 自班の現行Issueへ、未完了・完了・待機条件・重要な禁止事項を反映する。
- Stage完了や仕様変更がある場合は、必要に応じて `DECISIONS.md` または現行Stage仕様へ反映する。
- チャット本文だけに新しい決定を残したまま移動しない。

## 2. 新チャット開始時の確認順

実作業を始める前に、必ず次の順で確認する。

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. `CURRENT_STATE.md` に記載された自班の現行GitHub Issue
4. 必要な `DECISIONS.md` / 現行Stage仕様 / mainの実装状態

Issue番号は固定しない。Stageや担当変更で番号が変わるため、過去チャットや記憶から推測せず、毎回 `CURRENT_STATE.md` から特定する。

## 3. 新チャットの認識確認

確認後、作業開始前に次を自分の言葉で回答する。

1. 自分の班と役割
2. 現在のStage
3. 現在の担当Issue番号と内容
4. 現在地の正本として最初に見るファイル
5. 今の次作業
6. 今やってはいけないこと
7. Codexとの役割分担
8. 古いhandoff・旧チャット・過去Stage資料とGitHub現行状態が衝突した場合の扱い

最後に必ず以下を明記する。

`GitHub正本運用：認識済み / 未認識`

認識済みと判断できるまでは実作業を開始しない。

## 4. 班ごとの固定境界

### DEV

- 唯一の司令塔。
- 仕様整理・Stage管理・Codex指示・成果確認を担当する。
- CodexはDEVの実装担当であり独立班ではない。
- AUDITの正式PASSを代行しない。

### AUDIT

- DEV/Codexから独立した品質ゲート。
- 実装差分・テスト・証拠を確認して PASS / CONDITIONAL PASS / FAIL を判定する。
- 開発班やCodexの自己申告だけでPASSしない。
- 監査対象が完成する前にPASSしない。

### KNOWLEDGE

- 外部知識の調査・根拠整理を担当する。
- 仕様決定権・本体実装権は持たない。
- 調査結果を勝手にproduction規則へ昇格しない。

### PROMPT

- Stage10実験用Promptの設計・作成を担当する。
- 本体仕様の決定権は持たない。
- 正式handoff前に本番Promptを固定しない。

## 5. 衝突時の扱い

- 古いhandoff・旧チャット・過去Stage資料を、現行 `CURRENT_STATE.md` / 現行Issue / mainの状態より優先して現在地を巻き戻さない。
- ただしGitHub側に明確な矛盾がある場合も、勝手に一方を採用・補完しない。
- `衝突あり` として明示し、確認後にGitHub正本を修正する。

## 6. Stage境界

- `CURRENT_STATE.md` の現在Stageを越えて勝手に進まない。
- 後続Stage用の実験知識・仮説を、前Stageのproduction規則へ先行固定しない。
- model family固有のPrompt grammarを、検証なしに全モデル共通ルールへしない。

## 7. 完了条件

新チャットが以下を満たした時点で移行完了とする。

- 現在Stageを正しく認識
- 現行Issueを正しく特定
- 自班の権限境界を正しく認識
- 次作業と禁止事項を正しく認識
- GitHubと古い資料の衝突処理を理解
- `GitHub正本運用：認識済み` を明記
