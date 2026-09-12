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

Stage10 learning is parallel to this route and is not a v1 Gate.

## Current Stage10 learning flow

Current authority:
- Issue #65
- `docs/stages/STAGE_10_LEARNING.md`

Primary model:
- NoobAI XL 1.1 EPS + Forge Neo

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

Stage10の実生成ループ:

```mermaid
flowchart TD
 A[日本語の意図] --> B[NoobAI中心にmodel/profile選択]
 B --> C[Prompt設計]
 C --> D[探索生成]
 D --> E[観察]
 E --> F{何が失敗?}
 F --> G[concept / presence]
 F --> H[actor-target / body-site / count / relation]
 F --> I[camera / crop / visibility]
 F --> J[Negative / weight / LoRA conflict]
 G --> K[最小の意味ある修正]
 H --> K
 I --> K
 J --> K
 K --> L{Prompt-onlyで十分?}
 L -- Yes --> M[仕上げ]
 L -- No --> N[LoRA / Hires / ADetailer / inpaint / regional / Control]
 N --> M
 M --> O[metadata/infotext保存]
 O --> P[何が効いたか説明]
```

Hard/nicheの成功判定はpresenceだけでなく、必要に応じてactor / target / ownership / body-site / relation / count / visibility / source-destination / topologyまで見る。

Animaはrelation-heavy / multi-character / tag+natural-languageの比較・fallback lane。
WAI Illustrious v17はhistorical/comparison lane。
NoobAI V-PredはEPSと別profileとして扱う。

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
Stage10で手動学習することと、v1製品へ自動化を追加することは別判断。

## KNOWLEDGE / Stage10 evidence flow

```mermaid
flowchart TD
 A[Stage10 practical case] --> B{単発case?}
 B -- Yes --> C[local lessonとして保持]
 B -- No --> D[controlled repeat / scope確認]
 D --> E{durable evidence?}
 E -- No --> C
 E -- Yes --> F[KNOWLEDGE #44 Claim/HOLD候補]
 F --> G[scope付きで整理]
 G --> H{product adoptionが必要?}
 H -- No --> I[knowledge assetとして保持]
 H -- Yes --> J[DEV/productへhandoff]
```

KNOWLEDGEは知識・検証を所有するが、production採用を独断で決めない。

## Historical architecture note

Stage0〜Stage9で作ったfull index、true AND、Candidate Aggregation、recommendation、Generation Profile、Prompt Composer、evaluator infrastructureは削除対象ではない。
旧PROMPT #5のStage10/Prompt handoff資料、旧Stage10 production A/B準備、Issue #30 evaluator/calibrationもhistorical evidence/testing assetsとして保持する。

2026-09-13以降、これらは**新Stage10のcompletion Gateではなく、教材・比較・診断道具**として扱う。

旧 `Special -> true AND -> recommendation -> Prompt -> production A/B Stage10` を現在の必須ユーザーフロー/Stage10定義として扱わない。
