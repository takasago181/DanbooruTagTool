# KNOWLEDGE Catalog ディレクトリ

Owner: Issue #44 `KNOWLEDGE:#44`

このディレクトリは、知識を**topic別に読むための説明層**。

現在判定の正本:
`../current/CLAIM_REGISTRY.csv`

current管理入口:
`../current/README.md`

topic全体地図:
`../KNOWLEDGE_CATALOG.md`

research原本は `../research/` に保全する。
CatalogはClaimを読みやすく説明するが、RegistryのSTATUS/SCOPEを上書きしない。

## topic番号

0. `00_FOUNDATIONS_AND_AUTHORITY.md` — 基礎・目的・権限
1. `01_MODEL_FAMILIES.md` — モデル別
2. `02_PROMPT_SUPPORT_AND_COMPOSITION.md` — Prompt・support・構成
3. `03_FAILURE_TESTING_AND_EVALUATION.md` — 失敗診断・評価
4. `04_TOOLS_POSTPROCESS_AND_LORA.md` — ツール・後処理・LoRA
5. `05_HARD_NICHE_ADULT_GENERATION.md` — 特殊・ハード系成人生成
6. `06_SEMANTICS_ALIAS_TRIGGER.md` — 意味・Alias・trigger
7. `07_WAI17_LOCAL_TEST_PROFILE.md` — WAI17履歴/比較
8. `08_SOURCE_AND_SITE_AUDITS.md` — 情報源監査
9. `09_OPEN_QUESTIONS_AND_HOLD.md` — HOLD説明
10. `10_FILE_MAP.md` — 全ファイル地図

この番号体系を正本とし、並行する別taxonomyを作らない。
`current/` はtopic体系ではなく、Claim/status/versionを横断管理する層。

## 2つの知識用途

### v1支援
- canonical意味
- 日本語理解
- 検索・発見
- 出典追跡

### 実践・高度生成
- Prompt構成
- モデル差
- failure diagnosis
- LoRA / Control
- evaluator
- controlled generation evidence

別チームには分けない。

## 復元順

1. main `CURRENT_STATE`
2. main `PERMANENT_RULES`
3. live Issue #44
4. main `PRODUCT_GOAL_LOCK`
5. `../current/README.md`
6. `../current/CURRENT_QUICK_REFERENCE.md`
7. `../current/CLAIM_REGISTRY.csv`
8. 必要なtopic
9. HOLD / freshness
10. 必要な時だけresearch

固定日付handoffはhistorical。

## 不変条件

混ぜない:
- canonical意味
- Alias
- implication
- 関連・共起
- UI日本語
- model trigger
- generation support
- Prompt-only能力
- LoRA/Control/Edit後の能力
- evaluator判定
- product採用

不明はHOLDのまま残す。

## 更新

`research/source -> Claim確認 -> Registry -> 必要なtopicだけ更新 -> HOLD/freshness -> 必要なら狭い検証 -> #44 checkpoint`

同じ結論を複数topic/currentへコピーしない。
