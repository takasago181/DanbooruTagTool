# FLOWCHARTS.md

## Current v1 user flow

```mermaid
flowchart TD
 A[既存Promptを貼る / 空から開始] --> B[タグを日本語-first + Englishで理解]
 B --> C{欲しいタグを知っている?}
 C -- Yes --> D[日本語/英語/混在検索]
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
 B --> C[Exact canonical / exact English]
 C -->|なし| D[Exact approved Alias]
 D -->|なし| E[Japanese display/search]
 E -->|なし| F[approved Semantic/search bridge]
 F -->|なし| G[prefix / partial / fuzzy]
 C -->|hit| H[候補]
 D -->|hit| H
 E -->|hit| H
 F -->|hit| H
 G --> H
 H --> I[product-fit eligibility + relevance ordering]
 I --> J[日本語-first + canonical English表示]
```

Exact / strong Japanese intent / word-boundary intent を incidental substring/fuzzy collision より優先する。
Known regression `anal -> piano / analog...` を含む検索品質はIssue #66のacceptance scope。

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

Exact execution orderの正本は `docs/project/CURRENT_STATE.md`。
Issues #42 / #34 は retired / closed。製品scope・検索品質・最終acceptanceはIssue #66へ統合済み。

```mermaid
flowchart TD
 A[#64 General 30,629 taxonomy] --> C[#66 consumes accepted General taxonomy]
 B[#66 app/UI/search foundation] --> C
 C --> D[#66 final scope + search + integration check]
 D --> E[focused regression + real Windows UI acceptance]
 E --> F[v1 baseline]
 F --> G[Stage10 #65 resume]
```

#64と#66 foundationは並行可能。
#66は#64の分類データを先回りで発明せず、accepted sidecarを後からconsumeする。

## Current Stage10 learning flow — currently paused by priority

Current authority:
- Issue #65
- `docs/stages/STAGE_10_LEARNING.md`

Primary model:
- NoobAI XL 1.1 EPS + Forge Neo

Current user priority:
- practical v1 app baseline first
- then resume Stage10 unless explicitly changed

```mermaid
flowchart TD
 A[10.0 環境・再現性] --> B[10.1 Prompt基礎]
 B --> C[10.2 構図・カメラ・可視性]
 C --> D[10.3 hard/niche 構造分解]
 D --> E[10.4 失敗診断・controlled iteration]
 E --> F[10.5 Seed / Negative / Weight / LoRA]
 F --> G[10.6 Hires / ADetailer / img2img / inpaint]
 G --> H[10.7 Regional / Control escalation]
 H --> I[10.8 効率的な日常運用]
 I --> J[10.9 自力Capstone]
```

Stage10は製品Gateではない。

## Optional/future product subsystem flow

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

## KNOWLEDGE evidence flow

```mermaid
flowchart TD
 A[研究/Stage10 practical case] --> B{単発case?}
 B -- Yes --> C[local lesson / HOLD]
 B -- No --> D[controlled repeat / scope確認]
 D --> E{durable evidence?}
 E -- No --> C
 E -- Yes --> F[KNOWLEDGE #44 Claim/HOLD候補]
 F --> G[scope付きで整理]
 G --> H{product adoptionが必要?}
 H -- No --> I[knowledge assetとして保持]
 H -- Yes --> J[DEVへhandoff]
```

KNOWLEDGEは知識・検証を所有するが、production採用を独断で決めない。

## Historical architecture note

Stage0〜Stage9で作ったfull index、true AND、Candidate Aggregation、recommendation、Generation Profile、Prompt Composer、evaluator infrastructureは削除対象ではない。
旧PROMPT #5、旧Stage10 production A/B、Issue #30 evaluator/calibration、旧#42/#34 commentsはhistorical evidence/provenanceとして保持する。

旧 `Special -> true AND -> recommendation -> Prompt -> production A/B Stage10` を現在の必須ユーザーフローとして扱わない。
