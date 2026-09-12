# AGENTS.md — DanbooruTagTool Codex routing

## 1. 役割

Codexは独立班ではなくDEV（開発班）の実装担当。
仕様・現在地・Gateをチャット記憶から推測しない。

常設班はDEVとKNOWLEDGE。旧PROMPT班は2026-09-12に廃止され、Prompt/generation-effectiveness知識はKNOWLEDGE #44へ統合された。

## 2. 作業開始ゲート

新規セッション・再開・task branch作成前に必ず:

1. `git status --short --branch`
2. `git fetch origin --prune`
3. GitHub live `origin/main` のHEADを確認
4. `origin/main:docs/project/CURRENT_STATE.md`
5. `origin/main:docs/project/PERMANENT_RULES.md`
6. `CURRENT_STATE.md` が示すcurrent DEV Issueを `gh issue view <ISSUE> --comments` で取得
7. Issue title / state / body / latest checkpoint / completion condition / blockerを確認
8. 必要なら `docs/PRODUCT_GOAL_LOCK.md` と当該Issueが参照する現行仕様を読む
9. branch-local管理文書との差分はその後に確認する

現在地の優先順位:

`live main CURRENT_STATE -> live Issue -> latest checkpoint -> PERMANENT_RULES -> task branch/local worktree`

古いbranch、旧handoff、過去Stage資料で現在地を巻き戻さない。
矛盾時はfail-closedで停止する。

`NO_CURRENT_DEV / MANAGEMENT_HANDOFF` は正常な停止状態。open Issueを勝手にcurrent DEVへ昇格しない。

## 3. 現在の製品目的

製品目的の正本は `docs/PRODUCT_GOAL_LOCK.md`。

v1の中心は:

`理解 -> 発見 -> 選択 -> 出力`

対象ユーザーは画像生成初心者で、英語/Danbooruタグ知識が十分でなくても使えることを重視する。

v1で必須:
- 既存Promptのタグを日本語-first + canonical Englishで理解できる
- 日本語/英語の両方で検索できる
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

Stage10 / generation-effectivenessはv1の必須Gateではない。旧Issue #5はretired/closedで、将来generation-effectivenessを主張する機能を採用した時はKNOWLEDGE #44が既存claimsを確認し、必要な最小実験だけを扱う。

## 4. Special / Generalの役割

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

## 5. 現行Issueが最優先

このファイルはrouting/invariantを示すだけ。
実装scope・禁止事項・completion criteriaはlive current DEV Issue本文が正本。

current DEVが#64なら#64だけを実装し、#34/#42を先取りしない。
製品方向変更があっても、現行Issueの実装境界を勝手に拡張しない。

KNOWLEDGE #44はcurrent core DEVとは別のnon-blocking lane。Prompt/generation-effectiveness知識を所有していても、Codexがそこからproduction仕様を推測して実装しない。

## 6. protected data safety

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

## 7. branch / handoff

- 本体実装は原則latest mainからtask feature branch
- 直接mainへ未review実装をcommitしない
- stable checkpointはcommit
- push可能ならremoteへpush
- branch / commit SHA / changed files / tests / unresolvedを返す
- main mergeやGate PASSをCodexが独断で宣言しない
- GitHubからreview可能ならユーザーへZIP uploadを要求しない
- local-only/binary/push失敗時のみ `docs/CHATGPT_CODEX_HANDOFF.md` fallback

## 8. 読む仕様を必要最小限にする

常時読む:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. current DEV Issue
4. `docs/PRODUCT_GOAL_LOCK.md`
5. current Issueが指定する仕様

v1 product scope確認時:
- `docs/FEATURE_PRIORITY.md`
- `docs/FLOWCHARTS.md`
- Issue #42
- Issue #64（General taxonomy作業時）

KNOWLEDGE / generation-effectivenessを参照する必要がある時だけ:
- Issue #44
- `knowledge/generation-corpus` のcurrent/catalog/research
- historical Issue #5 はprovenance確認が必要な時だけ

以下は**該当Issueが必要とする時だけ**読む subsystem / historical architecture docs:
- `docs/CORE_TAG_SET_SCHEMA.md`
- `docs/STATISTICS_POLICY.md`
- `docs/SEMANTIC_BRIDGE_SCHEMA.md`
- `docs/AUXILIARY_TAG_ROLE_POLICY.md`
- Generation Profile / Stage8 / Stage9 / Stage10資料
- co-occurrence / full-index architecture資料

過去に実装済みだからという理由だけで、subsystemをv1 UI/runtime必須へ戻さない。

## 9. 実装原則

- canonical identityを日本語UX都合で変更しない
- 日本語は理解/検索/表示補助でありsemantic authorityではない
- Japanese + English searchを維持
- user explicit choiceを優先し、v1で隠れたautomatic insertionを作らない
- 既存機能が目的を満たすなら重複実装しない
- overengineeringしない
- runtime LLM dependencyを導入しない
- focused test + applicable regression + user-visible UI変更時の実Windows確認を行う

## 10. 報告

最低限:
- branch / commit SHA / push状況
- changed files
- 実施テストと結果
- protected/canonical dataへの影響
- 未解決事項
- stop point / next Gate

詳細運用は `docs/project/PERMANENT_RULES.md` を正本とする。
