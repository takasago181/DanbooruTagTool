# AGENTS.md — DanbooruTagTool Codex routing

## 1. 役割

Codexは独立班ではなくDEV（開発班）の実装担当。
仕様・現在地・Gateをチャット記憶から推測しない。

常設班はDEVとKNOWLEDGE。旧PROMPT班は廃止され、Prompt/generation-effectiveness知識はKNOWLEDGE #44へ統合された。

## 1.5. Execution architecture

Project-wide execution efficiency authority:

- `docs/project/EXECUTION_ARCHITECTURE.md`
- `docs/project/CURRENT_ROUTING.json`

New Codex session / lane selection remains a **cold start** and follows the full gate below.

Recurring same-lane automation or deterministic append-only resume may use the compact **warm resume** path defined by Issue #188 when contract/routing fingerprints match. Do not generalize warm-resume shortcuts to production promotion, protected-data mutation, cleanup, or uncertain routing.

## 2. 作業開始ゲート

新規セッション・lane選択・task branch作成前の **cold start** では必ず:

1. `git status --short --branch`
2. `git fetch origin --prune`
3. GitHub live `origin/main` のHEADを確認
4. `origin/main:docs/project/CURRENT_ROUTING.json`
5. `origin/main:docs/project/CURRENT_STATE.md`
6. routingが示す対象DEV laneのlive GitHub Issue本文と最新コメントを取得
7. `origin/main:docs/project/PERMANENT_RULES.md`
8. Issue title / state / body / latest checkpoint / completion condition / blockerを確認
9. product behavior / UX / scope判断が関係する場合は `docs/PRODUCT_GOAL_LOCK.md` と当該Issueが参照する現行仕様を読む
10. branch-local管理文書との差分はその後に確認する

同一lane・同一contractのrecurring Automation / append-only warm resumeでは、このfull gateを毎run再実行しない。Section 1.5 / `EXECUTION_ARCHITECTURE.md` のcompact warm-resume pathを使う。

現在地の優先順位:

`live main -> CURRENT_ROUTING.json -> CURRENT_STATE.md -> target live Issue -> latest checkpoint -> PERMANENT_RULES -> task branch/local worktree`

古いbranch、旧handoff、過去Stage資料で現在地を巻き戻さない。
矛盾時はfail-closedで停止する。

CURRENT_STATEが複数のactive DEV laneを示す場合、**ユーザーが依頼したlaneだけを選ぶ**。別laneを勝手に混ぜない。

### Runtime preflight override — 2026-09-20

Before local runtime/deploy/performance work, also verify:
- live main SHA;
- `docs/project/CURRENT_DEV_TASK.md`;
- current runtime root `C:\Codex\DanbooruTagTool-App`;
- `runtime-manifest.json` when inspecting a built runtime;
- real UserData location/hash before any promotion that could touch user state.

Do not assume `artifacts/current/` is the current launch target.
Do not treat local UserData as disposable publish content.

## 3. 現在の製品目的

製品目的の正本は `docs/PRODUCT_GOAL_LOCK.md`。

v1の中心は:

`理解 -> 発見 -> 選択 -> 出力`

対象ユーザーは画像生成初心者で、英語/Danbooruタグ知識が十分でなくても使えることを重視する。

v1で必須:
- 既存Promptのタグを日本語-first + canonical Englishで理解できる
- 日本語/英語/混在で検索できる
- exact/strong intentをincidental fuzzy/substring noiseより優先できる
- Special Core Dictionaryをジャンル/サブジャンルから深く発見できる
- production Japanese overlay 30,629件のGeneralタグを浅い実用ジャンルから発見できる
- Special/Generalをユーザー自身が追加・削除・並べ替えできる
- 最終Promptはcanonical Englishでコピーできる

v1でデフォルトにしない:
- automatic support insertion
- automatic minimum-sufficient Prompt construction
- automatic conflict removal / Negative生成
- automatic model-family rewrite
- Prompt文字列だけからのautomatic failure diagnosis
- model verification/status UI
- A/B experiment manager
- local generation success/failure DB
- evaluator success probability UI
- Raw Lift / recommendation-score dashboard
- full Generation Profile / knowledge dashboard
- runtime tagger stack
- full 11M-post / ~3GB statistics indexの必須化
- Forge/ComfyUI direct generation integrationの必須化

## 4. Current active DEV routing

### Live authority — 2026-09-23

Routing-sync base before the 2026-09-23 management update:

`95b53e6d114432358a2a1cea4e8554fcfae65bfd`

This is a snapshot base, **not a permanent current-main pointer**. Always fetch live `origin/main` before selecting a lane.

Current user-facing runtime remains:

`C:\\Codex\\DanbooruTagTool-App`

Runtime/performance/portable hardening is already completed. **Do not route by default to Performance / Runtime Load Audit.**

Current major independent research lanes are:

- **#179** — Character/Copyright identity, Japanese display/search, ranking, and 2D-scope quality audit. Artist audit excluded.
- **#180** — Character -> single canonical HOME Copyright authority reconstruction. Research-only until separately accepted.
- **#132** — full 31,003-identity tag discoverability/classification usability audit.

When the user selects one lane, work only that lane. Never combine #179/#180/#132 branches, datasets, or semantic decisions.

### #132 execution routing

#132 is no longer at bounded-prototype / pre-handoff status.

Current execution:
- branch: `research/taxonomy-usability-audit`
- 3 normal ChatGPT Automation workers + 1 coordinator
- 300 identities per worker run **ceiling, not quota**
- compact normal preflight via `docs/issue132/parallel/WORKER_EXECUTION_CARD_V1.md`; reread full frozen docs only on drift/contradiction
- 25-row immutable checkpoints for new work
- strict per-row finalization before moving on; ambiguity/proper noun/specialist/sexual-boundary uncertainty requires `RESEARCHED`, unresolved meaning uses `SEMANTIC_UNRESOLVED`
- cumulative lane-local 100-row QA: all high-risk rows + deterministic ordinary CHECKED spot-checks
- no redundant full-25 second reread, no status write/CI wait after every checkpoint, and no anticipated-time `EXECUTION_LIMIT` self-stop
- frozen Pass-A semantic contract remains unchanged
- no production mutation / main merge from the research lane

Read `research/taxonomy-usability-audit:docs/issue132/parallel/CURRENT_AUTOMATION_OPERATION.md` for live operational cadence and `research/taxonomy-usability-audit:docs/issue132/parallel/WORKER_EXECUTION_CARD_V1.md` for the compact worker rules. These are branch-local execution authority; do not infer that a duplicate main copy exists. Old `READY FOR CODEX LUNA PASS A`, 100-row, or 200-row target wording is historical/frozen context, not current execution routing.

### Runtime baseline

- PR #131 UI refinement completed.
- PR #133 portable/runtime hardening completed.
- PR #135 performance/runtime optimization completed.
- self-contained `win-x64` runtime remains the workstation launch target.
- `runtime-manifest.json` remains runtime provenance/hash contract.
- `artifacts/current/` is fallback/reference only.
- Artist remains hidden and old unreliable Character<->Copyright relation UI remains disabled by #177.

Do not use stale #64/#66/#117/performance text as active routing merely because it remains in historical documents.

## 5. Stage10 relationship

Stage10 is not a v1 product Gate.
It is defined by Issue #65 / `docs/stages/STAGE_10_LEARNING.md` as a practical image-generation learning stage.
Current user priority pauses Stage10 until the practical v1 app baseline is complete.

Primary learning model:
- NoobAI XL 1.1 EPS + Forge Neo

Secondary:
- Anima = relation-heavy / multi-character / tag+natural-language comparison/fallback
- WAI Illustrious v17 = historical/comparison
- NoobAI V-Pred = separate advanced profile

CodexはStage10学習を理由に、本体v1へ自動Prompt最適化・direct generation・evaluator UI等を勝手に実装しない。

## 6. Special / Generalの役割

### Special
- current production Special populationは **3,059** stable identities（ID 1..3,088中29 gaps）
- current browse authorityはIssue #76のshallow kind/body/theme model
- historical 2,788 base / #56 deep taxonomyはprovenanceとして保持し、current production population/browse authorityと混同しない
- canonical identityとbrowse taxonomyは分離し、#132 researchは既存authorityを直接書き換えない

### General
- production Japanese overlay 30,629 canonical entriesが対象
- 日本語表示/検索overlayとtaxonomyを混ぜない
- #64でcanonical-tag keyedの別taxonomy sidecarを作る
- Specialより浅いPrompt用途中心の分類にする
- 全100k+ Danbooru universeへ勝手に拡張しない

## 7. protected data safety

GitHubは管理状態とcommit済みcode/docsの正本であり、local workspace全体のbackupではない。

`.gitignore`配下の例:
- `data/source/`
- `data/derived/`
- `data/runtime/`
- `data/runtime_index/`
- `data/runtime_source/`
- `data/special2788/*.csv`, `*.xlsx`
- `_handoff/`, backups, large serialized/index data

GitHubに見えないことを削除・不要と解釈しない。

絶対禁止:
- `git clean -fdx`
- `git clean -fdX`
- ignored protected dataの広範囲cleanup
- 復元可能性を確認しない上書き/削除

WPF migrationを理由にexisting `data/` を先に移動・整理しない。

## 8. branch / handoff

- 本体実装は原則latest mainからtask feature branch
- #64 rollout branchと#66 app branchを混ぜない
- 直接mainへ未review実装をcommitしない
- stable checkpointはcommit
- push可能ならremoteへpush
- branch / commit SHA / changed files / tests / unresolvedを返す
- main mergeやGate PASSをCodexが独断で宣言しない
- GitHubからreview可能ならユーザーへZIP uploadを要求しない
- local-only/binary/push失敗時のみ `docs/CHATGPT_CODEX_HANDOFF.md` fallback

## 9. 読む仕様を必要最小限にする

### cold startで読む
1. `docs/project/CURRENT_ROUTING.json`
2. `docs/project/CURRENT_STATE.md`
3. target live DEV Issue
4. `docs/project/PERMANENT_RULES.md`
5. product behavior / UX / scope判断が関係する場合だけ `docs/PRODUCT_GOAL_LOCK.md`
6. target Issueが指定する仕様

### warm resumeで読む
1. compact routing / contract fingerprint
2. task-local immutable progress listing
3. next bounded input
4. changed evidenceだけ

`CURRENT_STATE_HISTORY.md` や変更されていない大型spec群を通常のwarm resume read setへ入れない。

Issue #64作業時:
- `docs/project/CURRENT_DEV_TASK.md`
- live Issue #64 latest checkpoint
- `docs/issue64/full_rollout/PROGRESS.md`
- 必要なrollout files

Issue #66作業時:
1. live Issue #66
2. `docs/product/V1_UI_FIRST_IMPLEMENTATION_BASELINE.md`
3. `docs/product/V1_WPF_ARCHITECTURE_BASELINE.md`
4. `docs/FEATURE_PRIORITY.md`
5. `docs/FLOWCHARTS.md`
6. Issue #64はdependency/boundary確認に必要な範囲だけ
7. existing `tools/legacy/python/danbooru_tag_tool/` / Python tests は **legacy/reference・behavior/regression evidenceとして必要な箇所だけ**読む

Issue #66では旧Python `ui.py` をnew UI implementation baseと解釈しない。

Stage10 learningを扱う時:
1. Issue #65
2. `docs/stages/STAGE_10_LEARNING.md`
3. Issue #44 / `knowledge/generation-corpus` のcurrent knowledge
4. 必要なexact model/tool source
5. old Stage10 docs only as historical/testing reference

KNOWLEDGE / generation-effectivenessを参照する必要がある時:
- Issue #44
- `knowledge/generation-corpus` のcurrent/catalog/research
- historical Issue #5 はprovenance確認が必要な時だけ

以下は該当Issueが必要とする時だけ読む:
- `docs/CORE_TAG_SET_SCHEMA.md`
- `docs/STATISTICS_POLICY.md`
- `docs/SEMANTIC_BRIDGE_SCHEMA.md`
- `docs/AUXILIARY_TAG_ROLE_POLICY.md`
- Generation Profile / Stage8 / Stage9 / legacy Stage10 A/B資料
- co-occurrence / full-index architecture資料

## 10. 実装原則

- canonical identityを日本語UX都合で変更しない
- 日本語は理解/検索/表示補助でありsemantic authorityではない
- Japanese + English + mixed searchを維持
- exact/strong intentをincidental fuzzy/substringより優先
- user explicit choiceを優先し、v1で隠れたautomatic insertionを作らない
- existing Promptの順序・raw surfaceを明示編集なしに壊さない
- dictionary追加はaccepted UI baselineどおりPrompt末尾 + canonical English
- 日本語表示を意味が欠けるellipsisで省略しない
- 既存機能/データが目的を満たすならbehavior/dataは再利用するが、Python runtime dependencyは移植しない
- overengineeringしない
- runtime LLM dependencyを導入しない
- normal startupでtaxonomy/audit/catalog source rebuildを走らせない
- WPF standard distributionはself-contained portable win-x64を目標にする
- machine-specific absolute path / registry必須設計を避ける
- focused test + applicable regression + user-visible UI変更時の実Windows確認を行う
- portable acceptanceでは別location/PCへのfolder copy起動を確認する

## 11. 報告

最低限:
- branch / commit SHA / push状況
- changed files
- 実施テストと結果
- protected/canonical dataへの影響
- legacy/data pathを移動・削除していないこと（#66 first WPF build中）
- portable publish / Windows validation状況（該当時）
- 未解決事項
- stop point / next Gate

詳細運用は `docs/project/PERMANENT_RULES.md` を正本とする。
