# KNOWLEDGE Master Catalog

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `TOPIC_CATALOG_V4 / CLAIM_REGISTRY_LINKED / PROMPT_MERGED`

このファイルは、知識班が蓄積した知識を**ジャンルから引く人間向け入口**である。

重要: **現在その知識をどう扱うかというclaim単位のcurrent verdict正本は `docs/knowledge/current/CLAIM_REGISTRY.csv`。**
このCatalogは読みやすい説明層であり、Registryと食い違う古い表現が残った場合はRegistryを優先し、元文書はevidence/historyとして扱う。

さらに製品目的そのものはmainの `docs/PRODUCT_GOAL_LOCK.md` が正本であり、branch-localな古いSpecial-first表現はcurrent product goalを上書きしない。

`research/` の原本・証拠・履歴は削除/移動せず保全する。

## 2026-09-12 ownership update

独立PROMPT班は廃止され、Prompt/generation-effectiveness知識はKNOWLEDGE #44へ統合された。

KNOWLEDGEは以下を一体で保持する:
- v1を支える意味・検索・発見・authority知識
- 将来/高度向けのPrompt composition / support / model behavior / failure diagnosis / evaluator / image-dependent evidence

ただし知識の存在はproduct/runtime採用を自動決定しない。

## 最短復元順

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 最新body/comments
4. `docs/PRODUCT_GOAL_LOCK.md`
5. `docs/knowledge/KNOWLEDGE_HANDOFF_CURRENT_20260909.md`
6. `docs/knowledge/current/CURRENT_QUICK_REFERENCE.md`
7. `docs/knowledge/current/CLAIM_REGISTRY.csv`
8. **`docs/knowledge/KNOWLEDGE_CATALOG.md`（このファイル）**
9. 必要な `docs/knowledge/catalog/*.md`
10. HOLD確認時は `docs/knowledge/current/HOLD_CONFLICT_REGISTER.md`
11. version/freshness確認時は `docs/knowledge/current/VERSION_FRESHNESS_LEDGER.csv`
12. 根拠確認が必要な時だけ `docs/knowledge/research/*`
13. 横断確認時に `GENERATION_KNOWLEDGE_CORPUS.md` / `GENERATION_KNOWLEDGE_SOURCES.md`

current管理層の入口:
`docs/knowledge/current/README.md`

## Current product relationship

v1 core:

`理解 -> 発見 -> 選択 -> 出力`

知識のうち、semantic authority / 日本語理解検索 / browse discovery / provenance はv1-supporting。
モデル生成挙動 / support / Prompt最適化 / failure diagnosis / A/Bはfuture/advanced knowledgeであり、具体的採用featureが要求しない限りv1 blockerではない。

## Canonical topic catalog

| # | ジャンル | 入口 | 主な内容 |
|---|---|---|---|
| 00 | 基礎・目的・権限 | `catalog/00_FOUNDATIONS_AND_AUTHORITY.md` | current product goal、2 knowledge horizons、authority境界 |
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
旧PROMPT資料を別taxonomy/storeとして再構築しない。

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
- **knowledge verdictとproduct adoptionは別。**

個々の原則の現在状態・scope・source class・validationは `current/CLAIM_REGISTRY.csv` を参照する。

## 現在の実証優先

画像依存の検証が本当に必要な場合の第一候補は **WAI Illustrious v17 + Forge Neo**。
これはv1 completion requirementではない。

読む順:
1. `current/CURRENT_QUICK_REFERENCE.md`
2. `current/CLAIM_REGISTRY.csv` の該当Claim
3. 関連 `catalog/*.md`
4. 未確定は `current/HOLD_CONFLICT_REGISTER.md`
5. 根拠が必要な時だけ `research/*`

## 6層構造

- **handoff** = 現在地・復元順・当面優先度
- **current management** = Claim Registry / HOLD / version / legacy / quick ref。current verdict metadata
- **catalog** = 現在知識の人間向けジャンル説明
- **corpus** = 横断統合知識
- **sources** = 出典台帳
- **research** = 詳細調査・証拠・limitations・履歴

旧PROMPT laneはこの6層とは別の7層目を作らず、必要な情報をこの構造へ吸収する。

## 保全・更新ルール

新しい意味のある知識では:
1. research/source evidenceを保存または参照
2. Claim Registryの既存Claimを確認し、追加/更新
3. category説明を必要な場合だけ更新
4. 未解決ならHOLD/CONFLICT registerを更新
5. version依存ならVersion/Freshness ledgerを更新
6. 新規文書なら`catalog/10_FILE_MAP.md`へ登録
7. image-dependentなら必要性を確認し、広いStage10 sweepではなく狭いcontrolled validationを優先
8. downstream handoffが必要な時だけDEV/productへ返却
9. #44へcheckpoint

research原本を整理目的だけで削除しない。同じcurrent status文章を複数ファイルへコピーしない。
