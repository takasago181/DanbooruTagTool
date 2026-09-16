# DECISIONS

重要な設計判断のみを残す。
日々の進捗・checkpointは `CURRENT_STATE.md` / 各Issueへ置く。
旧詳細はGit historyと各Issueに保存されている。

---

## D-001 常設3班 + AUDIT on-demand

Status: **SUPERSEDED BY D-016**

Historical decision: DEV / KNOWLEDGE / PROMPT + on-demand AUDIT。
2026-09-12にPROMPT班を廃止しKNOWLEDGEへ統合。現在はD-016を参照する。

---

## D-002 Codexは独立班にしない

Status: ADOPTED

CodexはDEVの実装担当。仕様決定・Gate PASSを代行しない。

---

## D-003 GitHub live authority / fail-closed

Status: ADOPTED

現在地は原則:

`live main CURRENT_STATE -> live current Issue -> latest checkpoint -> PERMANENT_RULES -> task branch/local`

で復元する。古いchat/handoff/branch-local管理文書で巻き戻さない。不一致時はfail-closed。

---

## D-004 GitHub-first proactive handoff

Status: ADOPTED

長いchatを記憶装置にしない。大区切り・大方針変更・handoff前にGitHub正本を更新し、意味のある途中成果をIssue checkpointへ残す。

---

## D-005 Shared management docsはlatest-mainへ差分統合

Status: ADOPTED

`CURRENT_STATE.md` / `PERMANENT_RULES.md` / `DECISIONS.md` 等をstaleな会話内コピーで全上書きしない。変更直前にlatest mainを取得し、競合時は停止する。

---

## D-006 Local protected dataをGitHub管理状態と分離

Status: ADOPTED

GitHubはlocal workspace全体のbackupではない。ignored runtime/source/derived/large dataを保護する。

禁止:
- `git clean -fdx`
- `git clean -fdX`
- protected ignored dataの広範囲cleanup

---

## D-007 Codex本体実装はfeature branch / GitHub review優先

Status: ADOPTED

- direct main implementation commitを避ける
- stable checkpointをcommit/push
- GitHubからreview可能ならZIP不要
- local-only/binary/push failure時のみfallback

---

## D-008 Special Core Dictionary identity / browse taxonomy — historical baseline

Status: HISTORICAL BASELINE / SUPERSEDED AS CURRENT POPULATION BY D-020

- final population 2,788
- canonical identity/freeze chain completed
- #56で2,788/2,788 Japanese-first UI browse mapping completed
- UI taxonomyはsemantic ground truthではなくbrowse index
- multi-path可
- old oversized catch-all解消済み

---

## D-009 Japanese overlay 30,629

Status: ADOPTED / COMPLETED DATA BASE

Production Japanese overlayは30,629 canonical entries。用途は日本語表示/検索補助。Japanese wordingをcanonical semantic authorityにしない。

---

## D-010 Product-fit eligibilityはsidecar

Status: ADOPTED / COMPLETED

Special product-purpose full audit 2,788/2,788:
- KEEP 1618
- KEEP_REFERENCE_ONLY 1133
- OUT_OF_SCOPE_PRODUCT 12
- REVIEW 25

Canonical rowsを書き換えずID-keyed sidecarとして実装。Issue #63は完了/merged。

---

## D-011 Beginner-first v1 product reset — 2026-09-12

Status: ADOPTED

v1目的を以下へ固定:

`理解 -> 発見 -> 選択 -> 出力`

- existing Promptを日本語-firstで理解
- Japanese/English/mixed検索
- Specialを深いジャンルから発見
- General 30,629を浅い実用ジャンルから発見
- userが明示的に選択/編集
- canonical-English Promptをcopy

自動最適Prompt生成をv1の目的にしない。

Canonical product file: `docs/PRODUCT_GOAL_LOCK.md`。
Current app/search/final acceptance owner: Issue #66。
Historical Issue #42/#34はactive Gateではない。

---

## D-012 General 30,629 practical taxonomy — separate sidecar

Status: ADOPTED / COMPLETED + INTEGRATED

Issue #64 is completed and integrated; its accepted sidecar remains the current
General taxonomy artifact.

- target = exact production Japanese-overlay 30,629 population
- canonical-tag keyed separate sidecar
- Japanese overlay自体は変更しない
- Specialより浅いPrompt用途中心分類
- full 100k+ Danbooru ontologyは作らない
- pilot -> audit -> full rollout

検索語を知らない初心者にもbrowse discoveryを提供するため。

---

## D-013 Stage10 / generation-effectiveness is not a v1 blocker

Status: **ADOPTED FOR v1 BOUNDARY / OLD STAGE10 MEANING SUPERSEDED BY D-017**

- generation-effectivenessはv1 completion blockerではない
- evaluator / Generation Profile / historical Stage10 A/B evidenceはoptional assets
- Prompt/generation knowledgeはKNOWLEDGE #44が所有
- former Issue #5はretired/closed

旧 `Stage10 = production A/B validation lane` 定義はD-017で置換。

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

既存資産は保持可だが、実装済みであることをUI採用理由にしない。

---

## D-015 Full statistics index is optional for v1

Status: ADOPTED

Stage5 full index / true AND / Candidate Aggregation / reliability rankingは既存資産として保持するが、通常の

`understand -> discover -> choose -> copy`

にfull 11M-post / ~3GB indexを必須化しない。

---

## D-016 PROMPT班廃止 / KNOWLEDGEへ統合 — 2026-09-12

Status: ADOPTED

常設体制:
- DEV
- KNOWLEDGE

AUDITはon-demand、TEMPは期間限定、CodexはDEV実装担当。
旧PROMPT班のPrompt/generation-effectiveness責務はKNOWLEDGE #44へ統合。
KNOWLEDGEはproduction/spec authorityを持たず、runtime/UI採用判断はDEV/product routingが行う。

---

## D-017 Stage10を実践画像生成学習ステージへ再定義 — 2026-09-13

Status: ADOPTED

Stage10をSpecial Core Dictionaryの広範囲production A/B検証から、ユーザー自身の**実践画像生成学習**へ変更。

Canonical:
- `docs/stages/STAGE_10_LEARNING.md`
- Issue #65

Primary:
- NoobAI XL 1.1 EPS + Forge Neo

Secondary:
- Anima = relation-heavy / multi-character fallback/comparison
- WAI Illustrious v17 = historical/comparison
- NoobAI V-Pred = separate advanced profile

Curriculumは10.0–10.9。Old A/B/evaluator assetsは教材・controlled comparison・provenanceとして保持する。
Stage10はv1 blockerではなく、practical-v1 completion待ちではないIssue #65の
独立learning laneである。

---

## D-018 Clean WPF rewrite — 2026-09-13

Status: **ADOPTED / PORTABLE SUBDECISION SUPERSEDED BY D-019**

Issue #66は既存Python/Tk UIを継ぎ足すのではなく、同一repository内にC#/.NET/WPFアプリを新設する。

原則:
- `src/` treeにclean implementation
- WPF runtimeからPython/Tcl/Tkを必須呼出ししない
- accepted data / identity / taxonomy / search rules / regression evidenceを再利用
- existing `data/` とlegacy Python pathsをactive migration中に大規模移動しない
- `catalog.db` = rebuildable/read-mostly catalog knowledge
- `user.db` / `UserData` = user-specific state
- normal startupでtaxonomy/audit/source rebuildを走らせない

Phase B baselineはmainへmerge済み。

2026-09-13時点の「self-contained portable folderを標準配布形式/acceptance要件にする」部分はD-019で置換する。

Canonical architecture file:
- `docs/product/V1_WPF_ARCHITECTURE_BASELINE.md`

---

## D-019 Portableをpractical v1 Gateから外す — 2026-09-14

Status: ADOPTED

DanbooruTagToolは現状ユーザー個人のlocal Windows利用が主目的であり、portable/別PC配布検証をpractical v1完成条件にしない。

Keep:
- clean WPF architecture
- Python/Tcl/Tk runtime非依存
- catalog/user-data分離
- relative/local path設計
- 既に動くself-contained publish能力は削除不要

practical v1では必須にしない:
- every-iteration self-contained publish
- portable folderをstandard user formatにすること
- second-PC folder-copy validation
- .NET-runtime-absent PC validation
- UserDataの別PC移行acceptance

Portable/self-contained distributionはoptional/post-v1。必要になった場合のみ再度扱う。

Development artifactsもversioned folderを毎回増殖させず、固定disposable pathを使う。Routine UI workではbuild/test/actual Windows launchを優先し、publishは明示要求時のみ。

---

## D-020 Special production 3,059 stable subset after #109 — 2026-09-16

Status: ADOPTED / CURRENT PRODUCTION AUTHORITY

- 2,788 is the historical base provenance set.
- Issue #96 expanded the historical line to 2,983; Issue #107 expanded it to 3,088.
- Issue #109 removed 29 user-approved rows.
- Current production Special is 3,059 rows in stable ID space 1..3,088.
- The 29 IDs remain gaps; IDs are not compacted or renumbered.
- Current browse authority is Issue #76 v2: 9 kinds / 6 body facets / 3 themes.
- Legacy `special2788` filenames and paths remain compatibility/provenance names.

---

## D-021 Issue #70 result-ledger and reconciled queue authority — 2026-09-16

Status: ADOPTED / CURRENT ACTIVE LANE

Issue #70 progress is derived from the source chunk manifest and validated
immutable result CSVs, including legacy result lanes and queue results. The
deterministic `queue_manager.py reconcile` command verifies identity/order,
duplicates, result SHA, and accepted/review counts, then rebuilds completed
queue records while preserving pending/valid claims. `queue_state.json` is the
reconciled operational view, not a standalone authority. UserData, General,
Special, and accepted result CSV contents are outside this lane.

---

## Historical note

旧Stage0–9実装判断、旧Stage10 A/B準備、evaluator校正、Prompt Composer研究等の詳細はGit historyと対応Issue/Stage文書に保持する。
Historical decisionは現在の `PRODUCT_GOAL_LOCK.md` / `CURRENT_STATE.md` / #66 / D-017 / D-018 / D-019 より優先しない。
