# KNOWLEDGE Master Catalog

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `TOPIC_CATALOG_V3 / CLAIM_REGISTRY_LINKED`

このファイルは、知識班が蓄積した生成知識を**ジャンルから引く人間向け入口**である。

重要: **現在その知識をどう扱うかというclaim単位のcurrent verdict正本は
`docs/knowledge/current/CLAIM_REGISTRY.csv`。**
このCatalogは読みやすい説明層であり、Registryと食い違う古い表現が残った場合はRegistryを優先し、
元文書はevidence/historyとして扱う。

`research/` の原本・証拠・履歴は削除/移動せず保全する。

## 最短復元順

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 最新コメント
4. `docs/knowledge/KNOWLEDGE_HANDOFF_CURRENT_20260909.md`
5. `docs/knowledge/current/CURRENT_QUICK_REFERENCE.md`
6. `docs/knowledge/current/CLAIM_REGISTRY.csv`
7. **`docs/knowledge/KNOWLEDGE_CATALOG.md`（このファイル）**
8. 必要な `docs/knowledge/catalog/*.md`
9. HOLD確認時は `docs/knowledge/current/HOLD_CONFLICT_REGISTER.md`
10. version/freshness確認時は `docs/knowledge/current/VERSION_FRESHNESS_LEDGER.csv`
11. 根拠確認が必要な時だけ `docs/knowledge/research/*`
12. 横断確認時に `GENERATION_KNOWLEDGE_CORPUS.md` / `GENERATION_KNOWLEDGE_SOURCES.md`

current管理層の入口:
`docs/knowledge/current/README.md`

## Canonical topic catalog

| # | ジャンル | 入口 | 主な内容 |
|---|---|---|---|
| 00 | 基礎・目的・権限 | `catalog/00_FOUNDATIONS_AND_AUTHORITY.md` | 現在目的、Special-first、authority境界 |
| 01 | モデル別生成知識 | `catalog/01_MODEL_FAMILIES.md` | WAI17 / Illustrious / NoobAI / Anima |
| 02 | Prompt・Support・構成 | `catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md` | 最小十分Prompt、support、anti-support、複合構成 |
| 03 | 失敗診断・テスト・評価 | `catalog/03_FAILURE_TESTING_AND_EVALUATION.md` | binding、seed、E0-E3、WD/Kagami/CL、TIE/UNCLEAR |
| 04 | ツール・後処理・LoRA | `catalog/04_TOOLS_POSTPROCESS_AND_LORA.md` | Forge/Hires/ADetailer/img2img/Control/regional/LoRA |
| 05 | 特殊・ハード系成人生成 | `catalog/05_HARD_NICHE_ADULT_GENERATION.md` | body-site、BDSM、機械、触手、体液、rare/extreme |
| 06 | 意味・Alias・Trigger | `catalog/06_SEMANTICS_ALIAS_TRIGGER.md` | Danbooru canonical、Alias、implication、e621/Gelbooru、trigger drift |
| 07 | WAI17ローカル実証 | `catalog/07_WAI17_LOCAL_TEST_PROFILE.md` | 現在環境、固定baseline、最初のテスト順 |
| 08 | 情報源・サイト監査 | `catalog/08_SOURCE_AND_SITE_AUDITS.md` | source hierarchy、AIArtRecipe、としあきWiki、HF、Danbooru/e621 |
| 09 | HOLD・未解決 | `catalog/09_OPEN_QUESTIONS_AND_HOLD.md` | 人間向けHOLD説明。current registerへ誘導 |
| 10 | 全ファイル地図 | `catalog/10_FILE_MAP.md` | root/research/current管理ファイルの対応 |

`catalog/README.md` も同じ番号体系を使う。**別の並行ジャンル番号体系は作らない。**
`current/` はジャンル体系ではなくclaim/status/versionを管理する横断metadata層。

## 横断原則

- **model family/version/profileは主張の一部。** 別モデルへ自動一般化しない。
- **canonical意味、Alias、implication、UI日本語、model trigger、generation supportは別レイヤー。**
- **presence != relation success.**
- **minimum sufficient != shortest.**
- **supportはanti-supportになり得る。**
- **Negativeはactive semantic intervention.**
- **Hires/ADetailer/inpaint/Control/LoRA成功はbase Prompt成功と別。**
- **1 seedはcase evidence.**
- **Tagger confidenceはsemantic ground truthではない。**
- **不明はHOLDのまま残す。**

個々の原則の現在状態・scope・source class・validationは
`current/CLAIM_REGISTRY.csv` を参照する。

## 現在の最優先

当面の実画像テスト環境は **WAI Illustrious v17 + Forge Neo**。

読む順:
1. `current/CURRENT_QUICK_REFERENCE.md`
2. `current/CLAIM_REGISTRY.csv` の `K-MODEL-WAI-*`
3. `catalog/07_WAI17_LOCAL_TEST_PROFILE.md`
4. `catalog/01_MODEL_FAMILIES.md`
5. `catalog/03_FAILURE_TESTING_AND_EVALUATION.md`
6. `catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md`
7. 特殊/ハード対象なら `catalog/05_HARD_NICHE_ADULT_GENERATION.md`
8. 未確定は `current/HOLD_CONFLICT_REGISTER.md`

## 6層構造

- **handoff** = 現在地・復元順・当面優先度
- **current management** = Claim Registry / HOLD / version / legacy / quick ref。current verdict metadata
- **catalog** = 現在知識の人間向けジャンル説明
- **corpus** = 横断統合知識
- **sources** = 出典台帳
- **research** = 詳細調査・証拠・limitations・履歴

## 保全・更新ルール

新しい意味のある知識では:
1. research/source evidenceを保存または参照
2. Claim Registryの既存Claimを確認し、追加/更新
3. category説明を必要な場合だけ更新
4. 未解決ならHOLD/CONFLICT registerを更新
5. version依存ならVersion/Freshness ledgerを更新
6. 新規文書なら`catalog/10_FILE_MAP.md`へ登録
7. downstream handoffが必要な時だけ班間Issueへ返却
8. #44へcheckpoint

research原本を整理目的だけで削除しない。同じcurrent status文章を複数ファイルへコピーしない。
