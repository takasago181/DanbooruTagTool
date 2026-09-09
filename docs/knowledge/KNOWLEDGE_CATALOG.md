# KNOWLEDGE Master Catalog

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `TOPIC_CATALOG_V2 / CONSOLIDATED`

このファイルは、知識班が蓄積した生成知識を**ジャンルから引ける最上位入口**である。

`research/` の原本・証拠・履歴は削除/移動せず保全する。`catalog/` はその上に置く現在知識の整理層。

## 最短復元順

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 最新コメント
4. `docs/knowledge/KNOWLEDGE_HANDOFF_CURRENT_20260909.md`
5. **`docs/knowledge/KNOWLEDGE_CATALOG.md`（このファイル）**
6. 必要な `docs/knowledge/catalog/*.md`
7. 根拠確認が必要な時だけ `docs/knowledge/research/*`
8. 横断確認時に `GENERATION_KNOWLEDGE_CORPUS.md` / `GENERATION_KNOWLEDGE_SOURCES.md`

## Canonical topic catalog

| # | ジャンル | 入口 | 主な内容 |
|---|---|---|---|
| 00 | 基礎・目的・権限 | `catalog/00_FOUNDATIONS_AND_AUTHORITY.md` | 現在目的、Special-first、evidence class、権限境界 |
| 01 | モデル別生成知識 | `catalog/01_MODEL_FAMILIES.md` | WAI17 / Illustrious / NoobAI / Anima |
| 02 | Prompt・Support・構成 | `catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md` | 最小十分Prompt、support、anti-support、複合構成 |
| 03 | 失敗診断・テスト・評価 | `catalog/03_FAILURE_TESTING_AND_EVALUATION.md` | binding、seed、E0-E3、WD/Kagami/CL、TIE/UNCLEAR |
| 04 | ツール・後処理・LoRA | `catalog/04_TOOLS_POSTPROCESS_AND_LORA.md` | Forge/Hires/ADetailer/img2img/Control/regional/LoRA |
| 05 | 特殊・ハード系成人生成 | `catalog/05_HARD_NICHE_ADULT_GENERATION.md` | body-site、BDSM、機械、触手、体液、rare/extreme |
| 06 | 意味・Alias・Trigger | `catalog/06_SEMANTICS_ALIAS_TRIGGER.md` | Danbooru canonical、Alias、implication、e621/Gelbooru、trigger drift |
| 07 | WAI17ローカル実証 | `catalog/07_WAI17_LOCAL_TEST_PROFILE.md` | 現在環境、固定baseline、最初のテスト順 |
| 08 | 情報源・サイト監査 | `catalog/08_SOURCE_AND_SITE_AUDITS.md` | source hierarchy、AIArtRecipe、としあきWiki、HF、Danbooru/e621 |
| 09 | HOLD・未解決 | `catalog/09_OPEN_QUESTIONS_AND_HOLD.md` | 断定禁止項目、WAI17優先テスト、将来evaluator比較 |
| 10 | 全ファイル地図 | `catalog/10_FILE_MAP.md` | root/research全current fileのジャンル対応 |

`catalog/README.md` も同じ番号体系を使う。**別の並行番号体系は作らない。**

## 横断原則

- **model family/version/profileは主張の一部。** 別モデルへ自動一般化しない。
- **canonical意味、Alias、implication、UI日本語、model trigger、generation supportは別レイヤー。**
- **presence != relation success.** object/tagが見えてもactor-target/body-site/topology/source-destinationが違えば失敗。
- **minimum sufficient != shortest.** 意味核を守り、冗長・競合だけ削る。
- **supportはanti-supportになり得る。** 意味的整合だけで自動追加しない。
- **Negativeはactive semantic intervention.** unusual anatomy/countと衝突し得る。
- **Hires/ADetailer/inpaint/Control/LoRA成功はbase Prompt成功と別。**
- **1 seedはcase evidence.** repeatability/generalizationには事前固定paired seedと適切なevidence levelが必要。
- **Tagger confidenceはsemantic ground truthではない。** vocabulary / semantic class / calibration / OODを先に確認。
- **不明はHOLD/TEST_REQUIREDのまま残す。** 別モデル・旧常識・体感で穴埋めしない。

## 現在の最優先

当面の実画像テスト環境は **WAI Illustrious v17 + Forge Neo**。

読む順:
1. `catalog/07_WAI17_LOCAL_TEST_PROFILE.md`
2. `catalog/01_MODEL_FAMILIES.md`
3. `catalog/03_FAILURE_TESTING_AND_EVALUATION.md`
4. `catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md`
5. 特殊/ハード対象なら `catalog/05_HARD_NICHE_ADULT_GENERATION.md`
6. 未確定確認は `catalog/09_OPEN_QUESTIONS_AND_HOLD.md`

## 5層構造

- **handoff** = 現在地・復元順・当面優先度
- **catalog** = 現在採用している知識をジャンル別に整理
- **corpus** = 横断統合知識
- **sources** = 出典台帳
- **research** = 詳細調査・証拠・limitations・履歴

通常はCatalogから入り、監査・根拠確認時だけresearchまで降りる。

## 保全・更新ルール

新しい大きな調査では:
1. research原本を保存
2. 対応するcanonical Catalogを更新
3. `catalog/10_FILE_MAP.md`へ登録
4. 優先度/現在地が変わる時だけhandoff更新
5. Issue #44へcheckpoint

research原本を整理目的だけで削除しない。Catalog内で重複taxonomyを作らない。