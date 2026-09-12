# ARCHITECTURE_POLICY.md

## Current v1 architecture priority

v1 core path:

`Prompt understanding -> bilingual search / browse discovery -> manual selection -> canonical-English copy`

このcore pathはfull statistics index、Stage10/evaluator、Generation Profile、runtime LLMが無くても起動・利用できること。

## Keep layers separate

少なくとも次を混ぜない:

1. canonical English identity
2. Alias / semantic relation
3. Japanese display/search overlay
4. Special UI browse taxonomy
5. General 30,629 UI browse taxonomy
6. optional statistics/co-occurrence data
7. optional generation/model evidence

Japanese UXやbrowse taxonomyの都合でcanonical identityを書き換えない。

## Existing subsystem boundaries

既存実装の境界は再利用してよい:

- DataSource
- TagSearchEngine
- CooccurrenceEngine
- Translation / SpecialDictionary
- PromptFormatter

ただしCooccurrenceEngine等が存在することはv1 runtime dependencyを意味しない。
新しい抽象化を追加して境界を増やす前に、current Issueの実際のgapを確認する。

## General taxonomy sidecar

Issue #64の30,629件taxonomyは:

- canonical tag keyed
- read-only sidecar
- Japanese overlayから分離
- shallow practical classification
- runtime LLMなし

とする。

## External / Existing Tool First

新機能・補助ツール・自動化を追加する前に、既存資産で目的を満たせないか確認する。

優先順:
1. 既に導入済み・利用中の機能/拡張
2. 対象アプリの標準機能
3. 対象環境に対応した既存拡張
4. ローカルで利用できる既存CLI / API / OSSライブラリ
5. 残るgapだけ最小限の自作コード

既存資産で十分な機能を重複実装しない。
自作の方がきれいという理由だけで置き換えない。

## 禁止する過剰設計

- PluginManager
- Event Bus
- Service Locator
- generic DB abstraction
- multiple GUI backend abstraction
- generic API connector framework
- cloud sync
- ranking plugin system
- incremental update framework
- v1に不要なgeneration orchestration framework

## Runtime / package

- Windows desktop first
- runtime local/non-LLM
- Forge等と同時常駐して邪魔にならないこと
- optional full index不在でもv1 core pathは動くこと
- 巨大JSON全展開を通常runtime形式にしない
- default distributionを不必要にmulti-GB化しない

将来standalone/Forge/ComfyUI/CLIへ再利用できる設計は許容するが、v1のためにfront-end/plugin frameworkを作らない。
