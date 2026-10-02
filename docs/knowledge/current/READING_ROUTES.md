# KNOWLEDGE 用途別の読む順番

Owner: Issue #44 `KNOWLEDGE:#44`

最初にmainの現在状態・恒久ルール・live Issue #44を確認する。
以下はその後に読む**知識班内の短い経路**。

## 1. 画像生成の基礎

1. `IMAGE_GENERATION_FOUNDATIONS_JA.md`
2. `CURRENT_QUICK_REFERENCE.md`
3. 必要なら `CLAIM_REGISTRY.csv`
4. 根拠が必要な時だけ BATCH_AZ / BA / BB / BC のfull filename

## 2. NoobAI / Animaの実践

1. `PRACTICAL_GENERATION_NOOB_ANIMA.md`
2. `VERSION_FRESHNESS_LEDGER.csv`
3. `CLAIM_REGISTRY.csv`
4. 未解決なら `HOLD_CONFLICT_REGISTER.md`
5. 詳細根拠が必要な時だけ関連research

## 3. 成人向け生成の失敗診断

1. `ADULT_IMAGE_GENERATION_DECISION_TREE.md`
2. モデル差が必要なら `PRACTICAL_GENERATION_NOOB_ANIMA.md`
3. `CLAIM_REGISTRY.csv`
4. `HOLD_CONFLICT_REGISTER.md`
5. 詳細根拠はBATCH_AW等

## 4. 成人向け生成を学ぶ

1. `IMAGE_GENERATION_FOUNDATIONS_JA.md`
2. `PRACTICAL_GENERATION_NOOB_ANIMA.md`
3. `ADULT_IMAGE_GENERATION_TEACHING_CURRICULUM.md`
4. `ADULT_IMAGE_GENERATION_DECISION_TREE.md`
5. 必要な時だけ `LOCAL_ADULT_WORKFLOW_PLAYBOOK_20261002.md`

## 5. 先生役として回答する

1. `ADULT_IMAGE_GENERATION_TEACHER_REFERENCE.md`
2. 相談内容に応じた専門正本
3. `CLAIM_REGISTRY.csv`
4. HOLDなら断定せず `HOLD_CONFLICT_REGISTER.md`

## 6. Animaだけ詳しく見る

1. `PRACTICAL_GENERATION_NOOB_ANIMA.md`
2. `CLAIM_REGISTRY.csv` の `K-MODEL-ANIMA-*`
3. `VERSION_FRESHNESS_LEDGER.csv`
4. `../catalog/01_MODEL_FAMILIES.md`
5. 必要なfocused research

タグのみ vs 短い自然文併用など、HOLD中の項目は勝敗を固定しない。

## 7. NoobAIだけ詳しく見る

1. `PRACTICAL_GENERATION_NOOB_ANIMA.md`
2. `CLAIM_REGISTRY.csv` の `K-MODEL-NOOB-*`
3. `VERSION_FRESHNESS_LEDGER.csv`
4. `../catalog/01_MODEL_FAMILIES.md`
5. `HOLD_CONFLICT_REGISTER.md`

EPSとV-Predを混ぜない。

## 8. WAI17を見る

1. `CLAIM_REGISTRY.csv` のWAI scope
2. `../catalog/07_WAI17_LOCAL_TEST_PROFILE.md`
3. `VERSION_FRESHNESS_LEDGER.csv`
4. 必要なら旧ローカル研究

WAI17は現在、比較・履歴レーン。

## 9. タグの意味・canonical・Alias

1. `CLAIM_REGISTRY.csv` の `K-SEM-*`
2. `../catalog/06_SEMANTICS_ALIAS_TRIGGER.md`
3. Danbooru/e621 semantic research
4. freshnessが必要ならVersion Ledger

「意味が正しい」と「モデルがその文字列へ反応する」は別。

## 10. Prompt / supportの効果

1. `CLAIM_REGISTRY.csv` の `K-PROMPT-* / K-SUPPORT-*`
2. `../catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md`
3. `HOLD_CONFLICT_REGISTER.md`
4. 必要ならminimum-sufficient Prompt research

## 11. 特殊・ハード・relation-heavy

### sceneをどう構造化するか
1. `../catalog/05_HARD_NICHE_ADULT_GENERATION.md`
2. `../research/BATCH_N_SCENE_INTENT_DISCOVERY_WORKFLOW_20260917.md`
3. `CLAIM_REGISTRY.csv`

### 生成失敗をどう直すか
1. `ADULT_IMAGE_GENERATION_DECISION_TREE.md`
2. `LOCAL_ADULT_WORKFLOW_PLAYBOOK_20261002.md`
3. model-specific guide
4. HOLD / Registry

planningとgeneration diagnosisを混ぜない。

## 12. LoRA / Control / Reference

1. `../catalog/04_TOOLS_POSTPROCESS_AND_LORA.md`
2. `LOCAL_ADULT_WORKFLOW_PLAYBOOK_20261002.md`
3. `CLAIM_REGISTRY.csv` のLoRA/Control関連
4. model-specific guide
5. focused research

## 13. evaluator / tagger

1. `CLAIM_REGISTRY.csv` の `K-EVAL-*`
2. `../catalog/03_FAILURE_TESTING_AND_EVALUATION.md`
3. `VERSION_FRESHNESS_LEDGER.csv`
4. `HOLD_CONFLICT_REGISTER.md`
5. 必要ならevaluator research

tagger confidenceをsemantic truthにしない。

## 14. 新しい外部サイト・情報源を監査

1. `KNOWLEDGE_GOVERNANCE.md`
2. `../catalog/08_SOURCE_AND_SITE_AUDITS.md`
3. `../GENERATION_KNOWLEDGE_SOURCES.md`
4. 既存Source ID確認
5. Claimを作る前に `CLAIM_REGISTRY.csv` を確認

Source IDは必ず一意。

## 15. 新しいモデルを追加

1. `KNOWLEDGE_GOVERNANCE.md`
2. `VERSION_FRESHNESS_LEDGER.csv`
3. `../catalog/01_MODEL_FAMILIES.md`
4. `CLAIM_REGISTRY.csv`
5. `HOLD_CONFLICT_REGISTER.md`

最初から全モデル共通へ一般化しない。

## 16. 古い説がまだ有効か確認

1. `LEGACY_MAP.md`
2. `CLAIM_REGISTRY.csv`
3. `LABEL_MIGRATION_MAP.md`
4. 現在のtopic正本
5. 根拠が必要ならhistorical/research

古い文章よりRegistryが優先。

## 17. DEV / product / AUDITへ正式回答

1. 問いを「意味 / モデル / Prompt / binding / runtime / evaluator」に分類
2. 該当Claimを抽出
3. STATUS / SCOPE / VALIDATION_STATE確認
4. HOLD確認
5. version依存ならFreshness確認
6. 必要な根拠だけ読む

正式判定では `Claim ID + STATUS + SCOPE + VALIDATION_STATE + evidence` を返す。

## 履歴資料の扱い

2026-09の固定日付handoff・旧audit・旧backlogは現役導線に使わない。
必要な場合は `LEGACY_MAP.md` から履歴として参照する。
