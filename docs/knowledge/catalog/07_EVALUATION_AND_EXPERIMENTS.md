# 07 — Evaluation / Experiments

## 証拠強度 E0–E3

### E0 — CASE / DEBUG
1枚/少数。現象確認・反例・バグ切り分け。

### E1 — REPEATABILITY
事前固定paired seedを複数。方向の再現性を見る。

### E2 — COMPARATIVE / INFERENCE
sample事前固定 + paired解析 + 不確実性 + practical effect。

### E3 — GENERALIZATION / RULE
複数Special・複数semantic class・必要なら複数model scopeまで跨いで再利用ルール候補。

## paired A/B

同じseedを使うだけで十分ではない。

保存する outcome:
- `A_ONLY_PASS`
- `B_ONLY_PASS`
- `BOTH_PASS`
- `BOTH_FAIL`
- `TIE`
- `UNCLEAR`
- `BLOCKED`

relative improvementとabsolute reliabilityは別に報告。

## Human judgement

二択を強制しない。

- TIE = 同程度
- UNCLEAR = 判定不能/証拠不足
- BOTH_FAIL = 両方目的未達
- BLOCKED = evaluator/visibility/technical issue

## Tagger/evaluatorの原則

machine verdict前に:
1. targetがvocabularyにあるか
2. semantic classが評価器向きか
3. exact version/threshold/calibrationが分かるか
4. OOD riskが高くないか
5. human contradictionがないか

## WD EVA02 v3

- common/unary baseline向き
- <600-image tagsがfilterされているためrare Specialで構造的blind spotあり
- target未出力 != image failure

## Kagami-24k

- wide vocabularyの有力候補
- WDより広いcoverageの実証あり
- rare tail reliabilityは別問題

## CL Tagger v2

- wide vocabulary
- per-tag calibration / thresholds
- OOD reference
- global fixed threshold設計を疑う強い根拠

## relation-heavy class

Tagger単独で判定しにくい:
- actor-target
- body-site
- restraint topology
- machine functional relation
- appendage ownership
- source-destination

この層はdecomposed signals / specialized evaluator / human REVIEWへroute。

## full 2788 evaluator comparison

WD / Kagami / CLの全Special2788 coverage比較は、dictionary finalization後に実施予定。

比較軸:
- Core / Extended / Alias / Semantic
- Alias raw vs canonical target
- post_count/rarity band
- vocabulary coverage
- confidence/calibration
- OOD
- human label disagreement

## 原本

- `research/BATCH_C_EVIDENCE_RELIABILITY_20260909.md`
- `research/BATCH_C_SOURCES_20260909.md`
- `GENERATION_KNOWLEDGE_INDEX.md`
- Issue #37 / #30 historical checkpoints