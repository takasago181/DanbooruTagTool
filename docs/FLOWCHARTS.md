# FLOWCHARTS.md

## Current v1 user flow

```mermaid
flowchart TD
 A[既存Promptを貼る / 空から開始] --> B[タグを日本語-first + Englishで理解]
 B --> C{欲しいタグを知っている?}
 C -- Yes --> D[日本語/英語検索]
 C -- No --> E[ジャンルから発見]
 E --> F{Special or General}
 F -- Special --> G[Special Core Dictionary 深いbrowse]
 F -- General --> H[General 30,629 浅い実用browse]
 D --> I[候補を見る]
 G --> I
 H --> I
 I --> J[ユーザーが手動で追加/削除/並べ替え]
 J --> K[canonical-English Prompt preview]
 K --> L[Copy]
```

## Search flow

```mermaid
flowchart TD
 A[日本語 / English / mixed input] --> B[normalize lookup]
 B --> C[Exact canonical]
 C -->|なし| D[Exact Alias]
 D -->|なし| E[Japanese display/search]
 E -->|なし| F[approved Semantic/search bridge]
 F -->|なし| G[prefix / partial / fuzzy]
 C -->|hit| H[候補]
 D -->|unique| H
 E -->|hit| H
 F -->|hit| H
 G --> H
 H --> I[product-fit eligibility + relevance ordering]
 I --> J[日本語-first + canonical English表示]
```

Exact/word-boundary intentを incidental substring/fuzzy collision より優先する。
Known defect `anal -> piano / analog...` はIssue #34のscope。

## Special discovery

```mermaid
flowchart TD
 A[Special] --> B[日本語ジャンル]
 B --> C[必要ならサブジャンル]
 C --> D[2,788 browse mapping]
 D --> E[日本語 + English identity]
 E --> F[Promptへ手動追加]
```

Special taxonomyは#56で完成済み。
UI browse indexでありcanonical semantic authorityではない。

## General discovery

```mermaid
flowchart TD
 A[General] --> B[実用ジャンル]
 B --> C[必要な範囲だけ浅いサブジャンル]
 C --> D[production Japanese overlay 30,629 entries]
 D --> E[日本語 + canonical English]
 E --> F[Promptへ手動追加]
```

General taxonomyはIssue #64。
`japanese_overlay.json` へtaxonomyを埋め込まずcanonical-tag keyed sidecarで分離する。
全100k+ Danbooru universeの完全分類はv1 scope外。

## Current development route

Exact execution orderの正本は `docs/project/CURRENT_STATE.md`。この図はその可視化であり、食い違う場合は `CURRENT_STATE.md` を優先する。

```mermaid
flowchart TD
 A[#63 product-fit sidecar acceptance] --> B[#64 General 30,629 practical taxonomy]
 B --> C[#34 bilingual search relevance]
 C --> D[#42 v1 scope lock / current code delta]
 D --> E[v1 UI integration]
 E --> F[focused regression + real Windows UI acceptance]
 F --> G[v1 baseline]
```

Issue #5 / Stage10はこの必須経路の外。
将来、model-specific effectivenessやevidence-backed automatic assistanceを採用した時だけ、必要な狭い実験へ再利用する。

## Optional/future subsystem flow

```mermaid
flowchart TD
 A[ユーザーが選んだtag/Special] --> B{追加支援が本当に必要?}
 B -- No --> C[そのままPrompt]
 B -- Yes --> D[co-occurrence / Semantic / generation knowledge]
 D --> E[明示候補として提示]
 E --> F[ユーザーが選択]
 F --> C
```

v1では候補を勝手にPromptへ自動挿入しない。

## Historical architecture note

Stage0〜Stage9で作ったfull index、true AND、Candidate Aggregation、recommendation、Generation Profile、Prompt Composer、evaluator infrastructureは削除対象ではない。
ただし「既に作った」ことはv1 user-facing requirementの根拠にならない。

旧 `Special -> true AND -> recommendation -> Prompt -> Stage10` を現在の必須ユーザーフローとして扱わない。
