# KNOWLEDGE Master Catalog

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `GENRE_CATALOG_V1`

このファイルは、知識班が蓄積した生成知識を**ジャンルから引けるようにする最上位入口**である。

既存の research ファイルは削除・移動しない。原本・証拠・履歴として保全し、本Catalog層が「現在の整理済み結論」を案内する。

## 最短復元順

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 最新コメント
4. `docs/knowledge/KNOWLEDGE_HANDOFF_CURRENT_20260909.md`
5. **このファイル**
6. 必要な `docs/knowledge/catalog/*.md`
7. 詳細が必要な時だけ `docs/knowledge/research/*`
8. `GENERATION_KNOWLEDGE_CORPUS.md` / `GENERATION_KNOWLEDGE_SOURCES.md`

## ジャンル一覧

| # | ジャンル | 入口 | 主な内容 |
|---|---|---|---|
| 01 | 目的・権限・方針 | `catalog/01_PRODUCT_GOAL_AND_GOVERNANCE.md` | 現在目的、Special-first、非LLM、知識班の権限 |
| 02 | モデル別生成知識 | `catalog/02_MODEL_FAMILIES.md` | WAI17 / Illustrious / NoobAI / Anima |
| 03 | Prompt・Support設計 | `catalog/03_PROMPT_AND_SUPPORT_DESIGN.md` | 最小十分Prompt、support role、anti-support、Negative |
| 04 | 失敗診断・複合構成 | `catalog/04_FAILURE_DIAGNOSIS_AND_COMPOSITION.md` | binding、count、visibility、multi-Special、原因切り分け |
| 05 | 特殊・ハード系成人生成 | `catalog/05_HARD_NICHE_ADULT_GENERATION.md` | 挿入、BDSM、機械、触手、体液、rare/extreme |
| 06 | 意味・Alias・Trigger | `catalog/06_SEMANTICS_ALIAS_TRIGGER.md` | Danbooru canonical、Alias、implication、e621/Gelbooru、trigger drift |
| 07 | 評価器・実験設計 | `catalog/07_EVALUATION_AND_EXPERIMENTS.md` | WD/Kagami/CL、paired seed、E0-E3、TIE/UNCLEAR |
| 08 | ツール・後処理・制御 | `catalog/08_TOOLS_POSTPROCESS_AND_CONTROLS.md` | Forge Neo、Hires、ADetailer、LoRA、ControlNet、regional |
| 09 | 情報源・サイト監査 | `catalog/09_SOURCE_AUTHORITY_AND_SITE_AUDITS.md` | 情報源権限、AIArtRecipe、としあきWiki、HF Discussions |
| 10 | HOLD・未解決・次研究 | `catalog/10_HOLD_AND_NEXT_RESEARCH.md` | 現時点で断定禁止の項目、WAI17優先テスト |

## 横断原則

- **モデルfamily/version/profileは主張の一部。** 別モデルへ自動一般化しない。
- **canonical意味、Alias、UI日本語、model trigger、generation supportは別レイヤー。**
- **存在とrelation成功は別。** object/tagが見えてもactor-target/body-site/topologyが違えば失敗。
- **minimum sufficient = 最短ではない。** 意味核を守り、冗長・競合だけ削る。
- **Negativeは意味に作用する。** 特殊解剖・count変更と衝突し得る。
- **Hires/ADetailer/inpaint/Control/LoRAの成功はbase Prompt成功と分ける。**
- **1 seedはケース証拠。** 信頼性や一般則には複数の事前固定paired seedが必要。
- **Tagger confidenceはsemantic ground truthではない。** 語彙・semantic class・較正・OODを先に確認。
- **不明はHOLD/TEST_REQUIREDのまま残す。** 空白を経験則で埋めない。

## 現在の最優先

当面の実画像テスト環境は **WAI Illustrious v17 + Forge Neo**。

まず読む:
- `catalog/02_MODEL_FAMILIES.md`
- `research/WAI17_LOCAL_ENV_TEST_BASELINE_20260909.md`
- `catalog/07_EVALUATION_AND_EXPERIMENTS.md`
- 対象が特殊/ハードなら `catalog/05_HARD_NICHE_ADULT_GENERATION.md`

## 保全方針

このCatalogは整理層であり、research原本を置き換えない。

- research = 調査過程・出典・詳細 evidence
- catalog = 現在採用している整理済み知識
- corpus = 横断的な長期知識本体
- handoff = チャット移行時の現在地

同じ内容が重複する場合、**最新Catalogの整理を入口にし、根拠確認時に原本へ降りる**。