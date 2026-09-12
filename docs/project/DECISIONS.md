# DECISIONS

重要な設計判断のみを残す。
日々の進捗・checkpointは `CURRENT_STATE.md` / 各Issueへ置く。
旧詳細はGit historyと各Issueに保存されている。

---

## D-001 常設3班 + AUDIT on-demand

Status: **SUPERSEDED BY D-016**

Historical decision:
- DEV
- KNOWLEDGE
- PROMPT

AUDITは常設班ではなく、必要な品質Gateごとに起動する独立監査ロール。
Codexは班ではなくDEVの実装担当。
TEMPは期間限定。

2026-09-12にPROMPT班を廃止し、KNOWLEDGEへ統合したため現在の体制はD-016を参照する。

---

## D-002 Codexは独立班にしない

Status: ADOPTED

CodexはDEVの実装担当。
仕様決定・Gate PASSを代行しない。

---

## D-003 GitHub live authority / fail-closed

Status: ADOPTED

現在地は:

`live main CURRENT_STATE -> live current Issue -> latest checkpoint -> PERMANENT_RULES -> task branch/local`

で復元する。
古いchat/handoff/branch-local管理文書で巻き戻さない。
不一致時はfail-closed。

---

## D-004 GitHub-first proactive handoff

Status: ADOPTED

長いchatを記憶装置にしない。
大区切り・大方針変更・handoff前にGitHub正本を更新する。
意味のある途中成果はIssue checkpointへ残す。

---

## D-005 Shared management docsはlatest-mainへ差分統合

Status: ADOPTED

`CURRENT_STATE.md` / `PERMANENT_RULES.md` / `DECISIONS.md` 等をstaleな会話内コピーで全上書きしない。
変更直前にlatest mainを取得し、競合時は停止する。

---

## D-006 Local protected dataをGitHub管理状態と分離

Status: ADOPTED

GitHubはlocal workspace全体のbackupではない。
ignored runtime/source/derived/large dataを保護する。

禁止:
- `git clean -fdx`
- `git clean -fdX`
- protected ignored dataの広範囲cleanup

---

## D-007 Codex本体実装はfeature branch / GitHub review優先

Status: ADOPTED

- direct main implementation commitをしない
- stable checkpointをcommit/push
- GitHubからreview可能ならZIP不要
- local-only/binary/push failure時のみfallback

---

## D-008 Special Core Dictionary identity / browse taxonomy

Status: ADOPTED / COMPLETED

- final population: 2,788
- canonical identity/freeze chain completed
- #56で2,788/2,788 Japanese-first UI browse mapping completed
- UI taxonomyはsemantic ground truthではなくbrowse index
- multi-path可
- old oversized catch-allは解消済み

---

## D-009 Japanese overlay 30,629

Status: ADOPTED / COMPLETED DATA BASE

production Japanese overlayは30,629 canonical entries。
用途は日本語表示/検索補助。
Japanese wordingをcanonical semantic authorityにしない。

---

## D-010 Product-fit eligibilityはsidecar

Status: ADOPTED

Special product-purpose full audit 2,788/2,788:
- KEEP 1618
- KEEP_REFERENCE_ONLY 1133
- OUT_OF_SCOPE_PRODUCT 12
- REVIEW 25

canonical rowsを書き換えずID-keyed sidecarとして実装する。
Current implementation owner: Issue #63 until accepted/merged.

---

## D-011 Beginner-first v1 product reset — 2026-09-12

Status: ADOPTED

製品の原点を再確認し、v1目的を以下へ固定した。

`理解 -> 発見 -> 選択 -> 出力`

対象問題:
- 画像生成初心者
- 英語/Danbooruタグ知識が弱い
- 既存Promptの意味が分かりにくい
- ニッチタグは名前自体を知らず検索できない

v1では:
- existing Promptを日本語-firstで理解
- Japanese/English検索
- Specialを深いジャンルから発見
- General 30,629を浅い実用ジャンルから発見
- userが明示的に選択
- canonical-English Promptをcopy

する。

自動最適Prompt生成をv1の目的にしない。

Canonical product file: `docs/PRODUCT_GOAL_LOCK.md`。
Scope Gate: Issue #42。

---

## D-012 General 30,629 practical taxonomy — separate sidecar

Status: ADOPTED / RESERVED IMPLEMENTATION

Issue #64。

- target = exact production Japanese-overlay 30,629 population
- canonical-tag keyed separate sidecar
- Japanese overlay自体は変更しない
- Specialより浅いPrompt用途中心分類
- full 100k+ Danbooru ontologyは作らない
- pilot -> audit -> full rollout

理由:
検索語を知らない初心者にはsearchだけでは発見できないため。

---

## D-013 Stage10 / generation-effectiveness is not a v1 blocker

Status: **ADOPTED FOR v1 BOUNDARY / OLD STAGE10 MEANING SUPERSEDED BY D-017**

The v1 boundary remains valid:
- generation-effectiveness is not a v1 completion blocker
- evaluator / Generation Profile / historical Stage10 A/B evidence remain optional assets for the product
- Prompt/generation knowledge remains owned by **KNOWLEDGE #44**
- former Issue #5 remains retired/closed and historical only

However, the old definition of `Stage10 = future production A/B validation lane` is superseded by D-017.
Old A/B/evaluator infrastructure remains preserved as evidence/testing tooling and can be used inside the new learning Stage10 when useful.

---

## D-014 Default v1 automatic assistanceを抑制

Status: ADOPTED

Default v1では以下を採用しない:
- automatic support insertion
- automatic minimum-sufficient Prompt construction
- automatic conflict removal / Negative generation
- automatic model-family rewrite
- Prompt-only automatic failure diagnosis
- user-facing evaluator success probability
- model verification-status UI
- A/B manager / local result DB

既存コード/データは必要なら保持するが、実装済みであることをUI採用理由にしない。

---

## D-015 Full statistics index is optional for v1

Status: ADOPTED

Stage5 full index / true AND / Candidate Aggregation / reliability rankingは既存資産として保持する。

ただしcore v1:

`understand -> discover -> choose -> copy`

の通常利用にfull 11M-post / ~3GB statistics indexを必須化しない。
将来の関連候補/統計機能で必要ならoptional subsystemとして使う。

---

## D-016 PROMPT班廃止 / KNOWLEDGEへ統合 — 2026-09-12

Status: ADOPTED

常設体制を以下へ変更する。

- DEV
- KNOWLEDGE

AUDITはon-demand独立監査ロール、TEMPは期間限定担当、CodexはDEV実装担当のまま。

旧PROMPT班は廃止し、その責務を `KNOWLEDGE:#44` へ統合する。

KNOWLEDGE #44が所有する範囲:
- generation knowledge corpus
- Prompt composition knowledge
- minimum-sufficient Prompt / support / anti-support research
- model-family-specific Prompt guidance
- generation-effectiveness research
- relation/binding/count/topology failure knowledge
- evaluator/tool/LoRA/control knowledge
- concrete adopted featureが必要とする場合のnarrow controlled validation / Stage10-style evidence handoff

ただしKNOWLEDGEはproduction/spec authorityを持たない。
知識・実証結果をruntime/UIへ採用する判断はDEV/product routingが行う。

Issue #5はretired/closedとし、comments/docs/resultsはhistorical evidenceとして保持する。
旧文書の`PROMPT:#5`参照は新しい独立班を意味せず、必要に応じて#44から参照する。

v1 knowledgeとfuture/advanced generation knowledgeは別チームに分けず、同じKNOWLEDGE内でproduct relevance / scope / validation stateを明示して管理する。

---

## D-017 Stage10を実践画像生成学習ステージへ再定義 — 2026-09-13

Status: **ADOPTED**

Stage10の目的を、Special Core Dictionaryの広範囲production A/B検証から、**ユーザー自身が画像生成を実践的に習得するための学習ステージ**へ変更する。

Canonical Stage10 definition:
- `docs/stages/STAGE_10_LEARNING.md`
- Issue #65 `[STAGE10][LEARNING][ACTIVE] Practical image-generation mastery with NoobAI`

目標:

`日本語の意図 -> Prompt設計 -> 生成 -> 観察 -> 原因分解 -> 修正 -> 必要ならLoRA/修復/領域制御 -> 仕上げ -> 再現可能な保存`

を初心者が自力で回せるようにする。

最終的には、成人の架空/二次元を前提としたハード・ニッチな表現を含む難しい生成でも、単なるレシピコピーではなく、
- model/profile選択
- Prompt構成
- camera/visibility
- actor-target/body-site/count/relation
- Negative/Seed/weight
- LoRA
- Hires/ADetailer/img2img/inpaint
- regional/control
- failure diagnosis

を使い分け、狙った絵へ修正しながら完成させられる状態をStage10 completionとする。

Primary learning lane:
- **NoobAI XL 1.1 EPS + Forge Neo**

Secondary lanes:
- Anima = relation-heavy / multi-character / tag+NL comparison/fallback
- WAI Illustrious v17 = historical/comparison
- NoobAI V-Pred = separate advanced profile

Curriculum:
- 10.0 environment/reproducibility
- 10.1 Prompt fundamentals
- 10.2 composition/camera/visibility
- 10.3 hard/niche structural generation
- 10.4 failure diagnosis/controlled iteration
- 10.5 seed/Negative/weights/LoRA
- 10.6 finishing/local repair
- 10.7 regional/control escalation
- 10.8 efficient daily workflow
- 10.9 independent capstone

Old Stage10 production A/B assets are **not deleted**. They become:
- teaching material
- controlled-comparison tooling
- provenance/evidence
- failure-diagnosis aids

Stage10 is parallel to the v1 product route and remains **not a v1 completion blocker**.
Likewise, v1 completion does not imply Stage10 learning completion.

KNOWLEDGE #44 supplies the research/claims; Stage10 may feed repeated practical observations back to #44. One successful image must not be promoted to universal model truth.

---

## Historical note

旧Stage0–9実装判断、旧Stage10 A/B準備、evaluator校正、Prompt Composer研究等の詳細はGit historyと対応Issue/Stage文書に保持する。
Historical decisionは現在の `PRODUCT_GOAL_LOCK.md` / #42 scope / D-017 Stage10 definitionより優先しない。
