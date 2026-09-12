# DanbooruTagTool 管理骨格

目的は、班を増やさず、正本・現在地・Issue・Codex作業境界を固定し、ユーザーの手作業を減らすこと。

## 最初に見るもの

作業チャットは古いhandoffや記憶ではなくlive GitHubから確認する。

1. `docs/project/CURRENT_STATE.md` — 現在地/routing
2. `docs/project/PERMANENT_RULES.md` — 恒久運用ルール
3. `CURRENT_STATE.md` が示す自班/担当Issue
4. `docs/PRODUCT_GOAL_LOCK.md` — 現在の製品目的
5. 必要な `DECISIONS.md` / current Issue-specific spec / main実装状態

Codexはさらにrepo root `AGENTS.md` に従う。

## 現在の製品方向

v1の中心:

`理解 -> 発見 -> 選択 -> 出力`

- Promptを日本語で理解
- Japanese/English検索
- Specialを深いジャンルから発見
- General 30,629を浅い実用ジャンルから発見
- ユーザーが手動で選択
- canonical-English Promptをcopy

Issue #5 / Stage10 / generation-effectivenessは将来laneであり、v1 blockerではない。

## 役割

- **DEV**: 唯一の司令塔。仕様決定、routing、Codex実装指示、成果確認。
- **KNOWLEDGE**: generation knowledge corpusの維持。v1へ機能を強制しない。
- **PROMPT**: 将来のgeneration-effectiveness / controlled Prompt実験が必要な時の担当。v1の必須laneではない。
- **AUDIT**: 常設ではなく、必要な品質Gateごとに起動する独立監査ロール。
- **TEMP**: 期間限定担当。
- **Codex**: DEVの実装担当。独立した仕様決定権は持たない。
- **GitHub管理・調整チャット**: 班ではない。Issue/管理文書/routing整合を担当。

常設は **DEV / KNOWLEDGE / PROMPT** の3班。

## 正本

- `docs/project/CURRENT_STATE.md`
  - 今どこにいるか / current DEV routing
- live GitHub Issue
  - task contract / scope / completion / checkpoint / evidence
- `docs/project/PERMANENT_RULES.md`
  - Stageをまたぐ固定運用
- `docs/PRODUCT_GOAL_LOCK.md`
  - 現在の製品目的
- `docs/project/DECISIONS.md`
  - 重要な設計判断
- branch / commit / PR
  - 実際の変更

チャット履歴は正本ではない。

## Current DEV

- Issue本文が実装task contract
- `CURRENT_STATE.md` はIssue番号/routing
- Issueコメントはcheckpoint/evidence
- Codexは毎回live Issueを取得
- mismatch時はfail-closed

`CURRENT_DEV_TASK.md` が存在してもlive Issueを置き換えない。

## checkpoint

意味のある成果をチャットだけに保持しない。

Issue checkpointへ最低限:
- 最後に成功したこと/結果
- 未完了/blocker
- 次作業
- branch/commit/file/evidence

Global routingが変わらない通常checkpointだけで `CURRENT_STATE.md` を肥大化させない。

## 班間handoff

DEV / KNOWLEDGE / PROMPT / 必要時AUDIT / TEMPは原則GitHub Issue経由。

- REQUEST / WHY / EXPECTED OUTPUT / RELATED ISSUE・FILE
- RESULT / EVIDENCE / VERDICT / LIMITATION / NEXT

ユーザーをコピペ中継役にしない。

## Codex / review

- latest mainからtask feature branch
- direct main implementation commitをしない
- stable checkpointをcommit/push
- GitHub branch/commit/PRからreviewできるならZIP不要
- local-only/binary/push failure時だけfallback
- Codex自己申告だけでGateを越えない

## protected data

GitHubはlocal workspace全体のbackupではない。
`.gitignore` のruntime/source/derived/large Special data等を保護する。

禁止:
- `git clean -fdx`
- `git clean -fdX`
- ignored protected dataの広範囲cleanup

## 大方針変更

大方針が変わった場合は、最低限:

1. `PRODUCT_GOAL_LOCK.md`
2. product-scope Issue（現在は#42）
3. `FEATURE_PRIORITY.md`
4. `FLOWCHARTS.md`
5. `AGENTS.md`
6. `DECISIONS.md`
7. 必要なら `CURRENT_STATE.md`
8. 影響を受けるlane Issue（例: #5 / #44 / #64）

を照合する。

旧Stage資料や旧実装仕様を「昔そうだった」だけで現行製品目的より優先しない。

## 最小運用

1. current stateを読む
2. current Issueを読む
3. product goalを確認
4. Issue scopeだけ作業
5. checkpointをGitHubへ残す
6. Gateを越える時だけrouting更新
7. protected dataを壊さない
8. ユーザーの操作量と管理コストを増やさない

詳細は `PERMANENT_RULES.md` / `AGENTS.md` / `CHAT_START_PROTOCOL.md` を参照。
