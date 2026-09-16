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

## 4. Current lanes

### Completed v1 foundations

- Issue #64 General 30,629 practical taxonomy is completed and integrated.
- Issue #66 beginner-first WPF app/search/UI and practical-v1 acceptance are completed.
- Issue #76 Special Browse v2 is the current Special browse authority.
- Issue #83 cleanup and Issue #109 Special production integration are completed.

Do not reopen #64 or #66, or infer an active implementation task from their
historical build specifications, without an explicit new request and a concrete
regression.

### Independent active lanes

- Issue #70 — post-v1 Character/Copyright/Artist Japanese dictionary expansion
  and i18n result ledger; reconcile from the source manifest and immutable
  accepted result files.
- Issue #65 — independent practical Stage10 learning lane.
- Issue #44 — ongoing KNOWLEDGE lane.

If no active DEV implementation issue is designated, do not restart an old
Issue #64/#66 task by inference.

### Completed architecture invariant

The current WPF product is clean C#/.NET under `src/`, has no Python/Tcl/Tk
runtime dependency, and separates rebuildable `catalog.db` from user-owned
`user.db`/`UserData`. Legacy Python/Tk paths and compatibility data remain
historical/reference assets; do not move or delete them as a routing shortcut.

Issues #34 and #42 are retired/closed historical provenance only. Do not use them as future Gates.

## 5. Stage10 relationship

Stage10 is not a v1 product Gate.
It is defined by Issue #65 / `docs/stages/STAGE_10_LEARNING.md` as a practical image-generation learning stage.
Practical v1 is complete; Stage10 is an independent active/available learning
lane and is not a v1 completion gate.

Primary learning model:
- NoobAI XL 1.1 EPS + Forge Neo

Secondary:
- Anima = relation-heavy / multi-character / tag+natural-language comparison/fallback
- WAI Illustrious v17 = historical/comparison
- NoobAI V-Pred = separate advanced profile

CodexはStage10学習を理由に、本体v1へ自動Prompt最適化・direct generation・evaluator UI等を勝手に実装しない。

## 6. Special / Generalの役割

### Special
- production is 3,059 stable identities in ID space 1..3,088, with 29 stable gaps
- niche/complex discovery surface
- current browse authority is Issue #76 Browse v2 (9 kinds / 6 body / 3 themes)
- #56 is historical/base provenance for the original 2,788 identity set
- product-fit eligibility is the #63 sidecar

### General
- production Japanese overlay 30,629 canonical entriesが対象
- 日本語表示/検索overlayとtaxonomyを混ぜない
- #64 canonical-tag keyed taxonomy sidecar is completed and integrated
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

Issue #64/#66 are completed historical authorities. Read their evidence only
when a regression or explicit maintenance request requires it; do not route new
implementation work there by inference.

Issue #70 work additionally reads `docs/issue70/TRANSLATION_AUTOMATION.md`,
`docs/issue70/AUTOMATION_LIGHTWEIGHT_PROTOCOL.md`, the source manifest, and
the live Issue #70 checkpoint. Its queue authority is source manifest + accepted
immutable results + deterministic reconciled queue state.

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
- legacy/data pathを移動・削除していないこと（必要な場合）
- portable publish / Windows validation状況（該当時）
- 未解決事項
- stop point / next Gate

詳細運用は `docs/project/PERMANENT_RULES.md` を正本とする。
