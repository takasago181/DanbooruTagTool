# DanbooruTagTool Control Board Migration Design

Status: **PROPOSAL ONLY / NOT YET ADOPTED**  
Created: 2026-09-09

この文書は、現在のGitHub-first運用を壊さずに、Issue番号中心の管理から **GitHub Projects + Issue hierarchy/dependencies + 薄いCURRENT_STATE** へ段階移行するための設計案。

この文書を追加しただけでは、既存の正本・班構成・Issue契約・CURRENT_DEV_TASK運用は変更しない。

---

## 1. 目的

現在の管理は安全性は高いが、以下の負担が増えている。

- Issue番号が「住所」と「人間向けの名前」を兼ねており、#1がPR、#2がIssueのようなGitHub共通番号列が直感的でない。
- `CURRENT_STATE.md` が routing / active state / completed history / gates / next actions / blockers を抱え、更新量が増えている。
- 親子関係や依存関係がIssue本文に自然言語で書かれており、一覧で追いにくい。
- 完了Issueが増えるほど「今見るべきもの」と「履歴」が混ざりやすい。

目標は、GitHub-first思想を維持したまま、

1. 人間は一画面で現在地を確認できる
2. ChatGPT/Codexは短い正本から安全に復元できる
3. Issueはtask contractと証跡に集中する
4. 依存関係を文章だけでなく構造で表現する
5. 完了履歴を毎回読まなくてよい

状態にすること。

---

## 2. 正本の役割分担

### 2.1 GitHub Issue

**task contract / result history の正本。**

保持するもの:
- purpose
- scope
- forbidden
- acceptance/completion criteria
- checkpoint comments
- result/evidence

保持しないもの:
- プロジェクト全体の現在地一覧
- 他Issueの詳細履歴の複製

### 2.2 `CURRENT_STATE.md`

**ChatGPT/Codex復元用の最小global routing正本。**

将来的には以下だけを保持する。

- Current Stage
- Active Team Registry
- Global Gates
- Latest Global Transition
- Immediate Next Actions
- Blocking / Unknown

過去完了Issueの長大な履歴は原則置かず、Issue / Project / DECISIONSへ委譲する。

### 2.3 `CURRENT_DEV_TASK.md`

**Codexが現行DEV Issueを読むための同期ミラー。**

現行ルールを変更しない。
Projectを導入しても、Codex task contractの正本にはしない。

### 2.4 `PERMANENT_RULES.md`

**変わりにくい運用ルールの正本。**

4班制、authority、GitHub-first、protected data、handoff、stale overwrite防止等を維持。

### 2.5 GitHub Project

**人間向けControl Board / operational index。**

重要:
- Projectはtask contractの正本にしない。
- Project fieldとIssue本文が矛盾した場合、Issue + CURRENT_STATE + PERMANENT_RULESを優先する。
- ChatGPT connectorからGitHub Projectsを直接操作・取得できない環境でも復元可能な設計を維持する。

---

## 3. Project名称

推奨:

**DanbooruTagTool Control Board**

Issue番号ではなく、タイトル + Workstream + Statusで現在地を見る。

---

## 4. Project Fields

現行 `WORKFLOW.md` の推奨Fieldsを、現在の実運用に合わせて整理する。

### 4.1 Status

単一選択:

- `ACTIVE`
- `WAITING`
- `GATED`
- `RESERVED`
- `BACKLOG`
- `COMPLETED`

`Working / Audit / Hold / Done` のように工程と状態を混ぜず、まず lifecycle を表す。

### 4.2 Workstream

単一選択:

- `DEV`
- `AUDIT`
- `KNOWLEDGE`
- `PROMPT`
- `DICT`
- `UI-JA`
- `TEMP`
- `MAINTENANCE`
- `MANAGEMENT`

注:
- 常設班は今までどおり DEV / AUDIT / KNOWLEDGE / PROMPT の4班だけ。
- DICT / UI-JA / TEMPは作業lane分類であり、常設班追加を意味しない。

### 4.3 Stage

単一選択:

- `CONTINUOUS`
- `STAGE9-HISTORY`
- `STAGE10-PREP`
- `STAGE10`
- `MAINTENANCE`

細かい9B/9C/9Dは完了履歴側に残し、現行運用で不要な粒度をBoardへ持ち込まない。

### 4.4 Type

単一選択:

- `PARENT`
- `IMPLEMENTATION`
- `DATA`
- `AUDIT`
- `RESEARCH`
- `EXPERIMENT`
- `MAINTENANCE`
- `NAMING`
- `MANAGEMENT`

### 4.5 Gate

単一選択:

- `N/A`
- `OPEN`
- `HOLD`
- `BLOCKED`
- `EXECUTION_AUTHORIZED`
- `PROMOTION_PENDING`
- `PASS`

StatusとGateを分ける。

例:
- #36 = Status `ACTIVE`, Gate `EXECUTION_AUTHORIZED`
- #30 = Status `GATED`, Gate `HOLD`
- #45 = Status `COMPLETED`, Gate `PASS`

### 4.6 Priority

単一選択:

- `P0`
- `P1`
- `P2`
- `NONE`

### 4.7 Short Name

Text field。

Issue番号を人間向け識別名にしないための短縮名。

例:
- #32 → `Dictionary Validation`
- #36 → `UI-JA Final Convergence`
- #44 → `Knowledge Corpus`
- #30 → `Stage10 A/B Automation`

番号はあくまでGitHub上のlocatorとして残す。

---

## 5. 推奨Views

### View 1 — `NOW`

目的: **普段はこれだけ見ればよい。**

Filter:
- Status != COMPLETED
- Status != RESERVED
- Status != BACKLOG

Group:
- Workstream

表示Fields:
- Title
- Short Name
- Status
- Gate
- Stage
- Priority

現在想定:
- #35
- #32
- #44
- #36
- #30
- #5
- #34 parent

### View 2 — `BLOCKED & GATED`

Filter:
- Status = GATED OR WAITING
- Gate = HOLD OR BLOCKED OR PROMOTION_PENDING

目的:
「何待ちなのか」をすぐ確認する。

### View 3 — `ROAD TO STAGE10`

Filter:
- Stage = STAGE10-PREP OR STAGE10
- Status != COMPLETED

依存関係を表示し、Stage10までの流れを見る。

### View 4 — `UI-JA TREE`

Root:
- #34

表示:
- #35
- #36
- #38
- #39
- #41
- #45

目的:
翻訳/UI系の履歴と現在地を1本の木として見る。

### View 5 — `DICTIONARY FREEZE`

対象:
- #32
- #43
- #42
- #5
- #30

目的:
辞書freezeからStage10へ進む依存だけを見る。

### View 6 — `HISTORY`

Filter:
- Status = COMPLETED

Group:
- Stage または Workstream

完了IssueをNOWから完全に退避する。

### View 7 — `MAINTENANCE`

対象:
- #24
- 将来の非blocking保守

---

## 6. Issue hierarchy 設計

新しいIssueを増やさず、既存Issueの構造を明示する。

### 6.1 UI-JA

```text
#34 UI-JA parent
├─ #35 Japanese-first desktop UI
└─ #36 Japanese overlay / Final Convergence
   ├─ #38 R3 spec + review          [completed]
   ├─ #39 R3 test engine            [completed]
   ├─ #41 fresh100 / blind30 pilot  [completed]
   └─ #45 V3.1 spec audit           [completed]
```

#38/#39/#41/#45は履歴として残すが、NOWには出さない。

### 6.2 Stage9 history

Stage9完了系列は無理に新parentを作らない。
Project `HISTORY` viewでまとめる。

主要line:

```text
#2 Stage9B DEV
→ #3 Stage9B AUDIT
→ #17 Stage9C/9D DEV
→ #22 Stage9C/9D AUDIT
→ #28 E2E Gate
```

### 6.3 Dictionary / Stage10

#32を辞書freeze系列の主anchorとして扱う。

```text
#32 Dictionary Validation
   ↓
#43 Naming Gate
   ↓
#42 Product-purpose Improvement
   ↓
#5 Formal Prompt Handoff
   ↓
Stage10 production A/B
```

#30はStage10 A/B automation laneとして並行し、final calibrationはdictionary freeze後に合流する。

---

## 7. Dependency 設計

親子関係とdependencyを混同しない。

推奨:

- #43 `blocked by` #32
- #42 `blocked by` #32
- #42 `blocked by` #36  
  （UI-JAがStage10評価を無効化する未解決data変更を残さないこと）
- #5 `blocked by` #42
- #5 `blocked by` #30
- #5 `blocked by` #32

注意:
- dependencyは実際のGate条件を過度に単純化しない。
- 「#32 close = 即#43開始」と完全一致しない場合、Issue本文のGateを正本とする。

---

## 8. 現在のIssue初期マッピング

| Issue | Short Name | Status | Workstream | Stage | Type | Gate |
|---|---|---|---|---|---|---|
| #35 | Desktop UI | ACTIVE | DEV | STAGE10-PREP | IMPLEMENTATION | OPEN |
| #32 | Dictionary Validation | ACTIVE | DICT | STAGE10-PREP | DATA | OPEN |
| #44 | Knowledge Corpus | ACTIVE | KNOWLEDGE | CONTINUOUS | RESEARCH | OPEN |
| #36 | UI-JA Final Convergence | ACTIVE | UI-JA | STAGE10-PREP | DATA | EXECUTION_AUTHORIZED |
| #30 | Stage10 A/B Automation | GATED | TEMP | STAGE10-PREP | EXPERIMENT | HOLD |
| #5 | Formal Prompt Handoff | GATED | PROMPT | STAGE10-PREP | EXPERIMENT | HOLD |
| #34 | UI-JA Parent | ACTIVE | UI-JA | STAGE10-PREP | PARENT | OPEN |
| #42 | Product-purpose Pass | RESERVED | DEV | STAGE10-PREP | IMPLEMENTATION | HOLD |
| #43 | Naming Gate | RESERVED | DEV | STAGE10-PREP | NAMING | HOLD |
| #24 | Protected Data Backup | BACKLOG | MAINTENANCE | MAINTENANCE | MAINTENANCE | N/A |
| #45 | V3.1 Spec Audit | COMPLETED | AUDIT | STAGE10-PREP | AUDIT | PASS |
| #41 | R3 Pilot | COMPLETED | UI-JA | STAGE10-PREP | EXPERIMENT | PASS |
| #39 | R3 Engine | COMPLETED | DEV | STAGE10-PREP | IMPLEMENTATION | PASS |
| #38 | R3 Spec | COMPLETED | UI-JA | STAGE10-PREP | RESEARCH | PASS |
| #28 | E2E Gate | COMPLETED | DEV | STAGE10-PREP | IMPLEMENTATION | PASS |
| #22 | Stage9 Final Audit | COMPLETED | AUDIT | STAGE9-HISTORY | AUDIT | PASS |
| #17 | Stage9C/9D DEV | COMPLETED | DEV | STAGE9-HISTORY | IMPLEMENTATION | PASS |
| #3 | Stage9B Audit | COMPLETED | AUDIT | STAGE9-HISTORY | AUDIT | PASS |
| #2 | Stage9B DEV | COMPLETED | DEV | STAGE9-HISTORY | IMPLEMENTATION | PASS |

重複・事故管理Issue (#11/#12/#13/#19/#20/#25) はProjectへ通常登録しない。必要ならHISTORY/ARCHIVE専用扱いにする。

---

## 9. CURRENT_STATE縮小案

Project移行が安定した後のみ実施する。

目標形:

```markdown
# CURRENT STATE

## Current Stage
Stage10-PREP

## Active Team Registry
- DEV: #35
- DICT: #32
- KNOWLEDGE: #44
- UI-JA: #36 V3.1 EXECUTION_AUTHORIZED
- TEMP: #30 GATED
- PROMPT: #5 GATED

## Reserved
- #42
- #43

## Global Gates
- Stage9: PASS
- E2E: PASS
- Forge comparison: PASS
- #36 V3.1 spec audit: PASS / execution authorized
- Stage10 production A/B: NOT STARTED

## Latest Global Transition
#45 PASS -> #36 V3.1 execution authorized

## Immediate Next Actions
1. #35 finish manual UI gate
2. #32 continue validation
3. #36 execute frozen V3.1 contract
4. #44 maintain knowledge corpus
5. #30/#5 wait for final freeze inputs

## Blocking / Unknown
- final Special dictionary count not frozen
- production Japanese overlay not promoted
- final evaluator routing not calibrated
```

完了Issueの詳細は各Issue/HISTORY viewへ移す。

---

## 10. `WORKSTREAMS.md` の扱い

現在の `WORKSTREAMS.md` は人間向けダッシュボードとして有用だが、更新が止まると急速に古くなる。

移行後の推奨:

- GitHub Projectが人間向けダッシュボードを担当。
- `WORKSTREAMS.md` は次のどちらかにする。
  1. Projectへの案内 + 作業構造の説明だけに縮小
  2. 廃止せず historical snapshot と明記し、更新対象から外す

Project安定前に削除しない。

---

## 11. Migration phases

### Phase 0 — Design only

現在。

- この提案書を追加
- 正本変更なし
- Issue変更なし
- Project変更なし

### Phase 1 — Boardを作る

手作業は最初の一度だけに限定する。

1. GitHub Project `DanbooruTagTool Control Board` を作成
2. Fieldsを作成
3. NOW / BLOCKED & GATED / ROAD TO STAGE10 / UI-JA TREE / HISTORY Viewsを作成
4. まず現在重要な10件程度のみ登録

この時点ではCURRENT_STATEを縮小しない。

### Phase 2 — Current issuesを構造化

- #34/#36配下のcompleted chainをsub-issue化
- #32/#43/#42/#5/#30のdependenciesを設定
- Project fieldsを初期マッピング表どおり入力

既存Issue本文は原則変更しない。

### Phase 3 — 1回の並行運用

短期間、

- CURRENT_STATE
- Project

を並行利用し、driftや見落としがないか確認する。

Projectを先に正本へ昇格させない。

### Phase 4 — CURRENT_STATE slim化

並行運用で問題がなければ、CURRENT_STATEからcompleted history等を削り、routing/global gates中心へ縮小。

同時に:
- PERMANENT_RULES
- WORKFLOW
- CHAT_START_PROTOCOL

へProjectの位置づけを最小限追記する。

### Phase 5 — WORKSTREAMS整理

最後に人間向け重複ダッシュボードを整理する。

---

## 12. Project導入後の運用ルール

### Issueを新規作成する条件

既存CURRENT_STATE Issue Hygieneを維持する。

新規Issueは以下のどれかが独立する場合のみ:
- owner
- scope
- lifecycle
- gate

単なる再監査・checkpoint・結果返却で番号を増やさない。

### Project field更新タイミング

Project fieldは以下のglobal transition時に更新:
- ACTIVE開始/終了
- GATED/HOLD/BLOCKED化
- Gate PASS
- RESERVED activation
- COMPLETED

通常の途中checkpointごとには更新しなくてよい。

### Issue番号の扱い

番号はlocator。
人間向け会話では:

`Dictionary Validation (#32)`

のように **Short Nameを先、Issue番号を後** にする。

---

## 13. 採用判断

この設計を正式採用する前に確認すること:

1. GitHub Projectをユーザーが実際に見やすいと感じるか
2. Sub-issues / dependenciesが現在のIssue構造に無理なく適用できるか
3. ChatGPT/CodexがProject APIへ依存せず復元可能か
4. CURRENT_STATEを縮めても安全性が下がらないか
5. Project field更新が新たな手作業負担になりすぎないか

どれかが悪化するなら、Projectは単なる補助viewに留め、CURRENT_STATE中心運用を維持する。

---

## 14. 推奨結論

**採用候補: GitHub ProjectをControl Boardとして追加し、Issue/CURRENT_STATE/PERMANENT_RULESのauthorityは維持する。**

いきなり正本をProjectsへ移さない。

最も安全な順序は:

`Projectを補助viewとして導入 -> 現行Issueだけ登録 -> hierarchy/dependencyを可視化 -> 並行運用 -> CURRENT_STATEを縮小`

これにより、既存のGitHub-first安全性を保ちながら、Issue番号・完了履歴・長大CURRENT_STATEによる認知負荷を減らせる。
