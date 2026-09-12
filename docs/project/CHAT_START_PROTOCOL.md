# CHAT START PROTOCOL

目的: 新しいChatGPT/Codexチャットが、古いhandoffや旧Stage方針に引っ張られず、GitHub正本から同じ現在地・製品目的・担当境界を復元する。

## 1. 読取順

### DEV / KNOWLEDGE / PROMPT / TEMP / AUDIT / GitHub管理

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. `CURRENT_STATE.md` が示す自班/担当/監査対象のlive Issue
4. `docs/PRODUCT_GOAL_LOCK.md`
5. 必要な `docs/project/DECISIONS.md` / current Issue-specific spec / main実装状態
6. 必要なlatest checkpoint / result comment

### Codex DEV

`AGENTS.md` のstartup gateを優先し、live current DEV Issueを直接取得する。

Issue番号・branch・Stageは過去chatや記憶から推測しない。
矛盾・取得失敗時はfail-closed。

## 2. 現在の製品方向

v1 product core:

`理解 -> 発見 -> 選択 -> 出力`

- existing Promptを日本語-firstで理解
- Japanese / English検索
- Specialを深いgenre/subgenreから発見
- General 30,629を浅い実用genreから発見
- userが手動選択
- canonical-English Promptをcopy

Issue #5 / Stage10 / generation-effectivenessはv1の必須laneではない。
PROMPT班は、将来採用featureが画像依存のgeneration evidenceを必要とする時にcontrolled Prompt/A-B設計を担当する。

## 3. チャット移行を提案する条件

- 会話長大化で現在地混同リスクが高い
- 過去メッセージ再探索/訂正が増えた
- Stage/Pilot/Audit等の大区切り
- 大方針/担当/正式contract変更
- ユーザーが移行を希望

移行前にGitHub正本を更新する。
長大なmanual handoffをユーザーへ作らせることを標準にしない。

## 4. 途中checkpoint

次の場合は担当Issueへ短いcheckpointを残す:
- 意味のある実装/調査/監査/環境確認が成功
- 後続前提になる事実が確定
- 長時間中断/話題切替/handoff
- 失うと再開コストが高い状態

最低限:
1. 最後に成功したこと / 結果
2. 未完了 / blocker
3. 次作業
4. branch / commit / file / evidence

checkpointはtask contractを黙って変更しない。
scope/禁止/完了条件を変える場合はlive Issue本文と必要なmanagement docsを更新する。

## 5. チャット移行前

- current Issueへ必要checkpointを反映
- global stateが変わった場合のみ `CURRENT_STATE.md` 更新
- product direction変更なら `PRODUCT_GOAL_LOCK.md` / #42等product-scope Issue / `DECISIONS.md` / `AGENTS.md` / `FEATURE_PRIORITY.md` / `FLOWCHARTS.md` / 影響lane Issueを照合
- shared docs更新直前にlatest mainを再取得
- GitHub更新後に新chatへ移行

## 6. 新チャット認識確認

必要な担当では次をlive確認して表示する:

```text
TEAM_ID: <stable workstream id>
TEAM: <team/role>
ROLE: <current role>
ISSUE: <#number / N/A>
BRANCH: <verified branch / main / N/A>
HEAD: <verified commit SHA>
CHECKPOINT: <latest relevant checkpoint / N/A>
CONTRACT: <live Issue / contract file>
PHASE: <current phase/gate>
SOURCE_OF_TRUTH: CURRENT_STATE -> live Issue -> PERMANENT_RULES -> PRODUCT_GOAL_LOCK -> relevant specs
```

矛盾があれば `IDENTITY_CONFLICT` として作業を止める。

## 7. 役割境界

### DEV
- 唯一の仕様/routing司令塔
- Codexへ実装指示
- 成果回収/受入れ
- AUDIT PASSを代行しない

### KNOWLEDGE
- 外部知識・generation knowledge corpus
- production仕様を勝手に変更しない
- v1へadvanced機能を強制しない

### PROMPT
- future generation-effectiveness / controlled experiments when explicitly activated
- v1 completion blockerではない
- model/image依存claimが必要な時だけ動く

### AUDIT
- on-demand independent Gate role
- target/deltaをGitHubから復元してPASS/HOLD/FAIL
- 完了後は常設しない

### TEMP
- `CURRENT_STATE.md` に明示された期間限定scopeのみ

### Codex
- DEVの実装担当
- current Issue scopeのみ
- self-merge / self-PASSしない

### GitHub管理・調整
- 班ではない
- Issue/management docs/routingの整合のみ

## 8. protected / stale safety

- chat historyは正本ではない
- stale branch-local management docsで現在地を決めない
- GitHubに見えないignored runtime/source dataを削除扱いしない
- `git clean -fdx` / `git clean -fdX` 禁止
- completed/superseded workをold handoffから再開しない

最後に必要なら:

`GitHub正本運用：認識済み`

を明示する。
