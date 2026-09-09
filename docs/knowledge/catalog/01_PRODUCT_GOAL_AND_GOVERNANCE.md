# 01 — Product Goal / Governance

## 現在の目的

Special-firstの核は維持されている。現在の成功条件は初期より広い。

`短い日本語/英語の意図 -> 正しいSpecial候補 -> 必要最小限のsupport/structure -> model-familyに合った英語Prompt -> 失敗原因を安全に切り分け -> 無駄な生成試行を減らす`

最終目的は「Promptを作ること」ではなく、**ユーザーが狙ったニッチな画像へ到達するまでの試行錯誤を減らすこと**。

## 固定境界

- ローカル個人利用。
- 実行時ChatGPT/ローカルLLMなし。
- Special2788がCore Tag Set。
- Danbooru全体、共起、日本語辞書、Semantic、LoRAは補助。
- Core / Auxiliary / LoRAを分離。
- productionデータの意味・identityは知識班が勝手に書き換えない。
- KNOWLEDGE:#44は evidence/reference lane。#32 verdict権限やStage10 production開始権限を持たない。
- 現在は他班との独立性を保つ。explicit handoff時のみ還元。

## 初期から変わった点

### 維持
- Special-first
- 日本語短文から英語Promptへの橋渡し
- 非LLM runtime
- local-first
- 候補集約とsupport利用

### 拡張
- model-family差を第一級に扱う
- 最小十分Promptを重視
- anti-support/競合を扱う
- failure diagnosisを製品価値に含める
- rare/hard relationを別問題として扱う
- evaluatorのcoverage/OODを考慮
- 実画像A/Bで知識を更新する前提

## 知識の状態ラベル

- `FACT_EXACT_MODEL` — exact model/version author等
- `FACT_GENERAL` — 一般機構として強い
- `CONTROLLED_PRACTICAL` — 比較条件が比較的制御された実践
- `PRACTICAL` — 実用報告
- `COMMUNITY` — failure discovery候補
- `HOLD / TEST_REQUIRED / IMAGE_TEST_REQUIRED` — 未確定
- `REJECT` — 誤り/一般化禁止/現目的に不適切

## 原本

- `docs/knowledge/CURRENT_PRODUCT_GOAL_20260909.md`
- `docs/knowledge/PRODUCT_GOAL_EVOLUTION_20260909.md`
- `docs/knowledge/KNOWLEDGE_REASSESSMENT_20260909.md`
- `docs/PRODUCT_GOAL_LOCK.md`
- `docs/project/PERMANENT_RULES.md`
- Issue #44