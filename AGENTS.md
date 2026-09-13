# AGENTS.md — DanbooruTagTool Codex routing

## 1. 役割

Codexは独立班ではなくDEV（開発班）の実装担当。
仕様・現在地・Gateをチャット記憶から推測しない。

常設班はDEVとKNOWLEDGE。旧PROMPT班は廃止され、Prompt/generation-effectiveness知識はKNOWLEDGE #44へ統合された。

## 2. 作業開始ゲート

新規セッション・再開・task branch作成前に必ず:

1. `git status --short --branch`
2. `git fetch origin --prune`
3. GitHub live `origin/main` のHEADを確認
4. `origin/main:docs/project/CURRENT_STATE.md`
5. `origin/main:docs/project/PERMANENT_RULES.md`
6. `CURRENT_STATE.md` が示す対象DEV laneのlive GitHub Issue本文と最新コメントを取得
7. Issue title / state / body / latest checkpoint / completion condition / blockerを確認
8. 必要なら `docs/PRODUCT_GOAL_LOCK.md` と当該Issueが参照する現行仕様を読む
9. branch-local管理文書との差分はその後に確認する

現在地の優先順位:

`live main CURRENT_STATE -> target live Issue -> latest checkpoint -> PERMANENT_RULES -> task branch/local worktree`

古いbranch、旧handoff、過去Stage資料で現在地を巻き戻さない。
矛盾時はfail-closedで停止する。

CURRENT_STATEが複数のactive DEV laneを示す場合、**ユーザーが依頼したlaneだけを選ぶ**。別laneを勝手に混ぜない。

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

## 4. Current active DEV lanes

### Issue #64 — General taxonomy

Owns only:
- exact General 30,629 target population
- shallow practical taxonomy classification
- sidecar data/audit
- unresolved accounting

Do not implement UI/search behavior inside #64。
`docs/project/CURRENT_DEV_TASK.md` is an Issue #64 mirror only.

### Issue #66 — app/search/UI completion

Owns:
- beginner-first desktop UI
- **clean C#/.NET/WPF v1 implementation under a new `src/` tree**
- existing-Prompt understanding/workspace
- bilingual/mixed search quality and ranking/noise fixes
- Special browse integration
- General browse provider/UI that later consumes accepted #64 output
- explicit add/remove/reorder
- canonical-English preview/copy
- hidden automatic insertion cleanup
- self-contained portable Windows x64 packaging
- final ADOPT/HOLD/REJECT reconciliation against `PRODUCT_GOAL_LOCK.md`
- focused regression and real Windows acceptance

Issue #66 first implementation authorities:
- `docs/product/V1_UI_FIRST_IMPLEMENTATION_BASELINE.md`
- `docs/product/V1_WPF_ARCHITECTURE_BASELINE.md`

Known search regression such as `anal -> piano / analog...` is part of #66 acceptance.

### #66 architecture invariant

Current `danbooru_tag_tool/` Python/Tk code is **legacy/reference during the first WPF build**。

Do:
- create new WPF projects under `src/`
- reuse accepted data / identity / taxonomy / search rules / regression evidence / behavior
- keep current Python/data paths intact during first build
- keep #64 data ownership untouched
- target `catalog.db` + `user.db/UserData` separation
- target `win-x64` self-contained portable folder

Do not:
- make WPF depend on Python/Tcl/Tk at runtime
- refactor the old Tk UI into the new product shell
- move/delete legacy Python or broad `data/` trees before WPF baseline acceptance
- port old recommendation/automatic-support/Stage-oriented UI merely because it exists
- require a separate .NET Desktop Runtime installation for the standard portable build

Single-file EXE is not required. One copyable portable folder is preferred.

Issues #34 and #42 are retired/closed historical provenance only. Do not use them as future Gates.

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
- 2,788 identityはfreeze済み
- ニッチ/複雑概念の深い発見面
- #56のUI browse taxonomyを使う
- product-fit eligibilityは#63のsidecarを使う

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

常時読む:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. target live DEV Issue
4. `docs/PRODUCT_GOAL_LOCK.md`
5. target Issueが指定する仕様

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
7. existing `danbooru_tag_tool/` / Python tests は **legacy/reference・behavior/regression evidenceとして必要な箇所だけ**読む

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