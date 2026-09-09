# PROMPT Knowledge Index

最終更新: 2026-09-09
Owner: PROMPT / Issue #5
Status: PROMPT班の知識ナビゲーション正本。**本体production仕様ではない。**

## 目的

このディレクトリは、PROMPT班が蓄積した知識を「調査した順」ではなく「何を知りたいか」で読めるように整理した入口。

DanbooruTagToolのPROMPT側の現在目的は、単なるタグ整形ではなく、**日本語の制作意図からSpecialを核に必要な構造・supportを選び、対象model familyで高品質かつ難度の高いニッチ/複合画像を少ない手直しで成立させやすいPromptへ変換すること**。

ここにある文書はPROMPT側の知識・監査・Stage10候補を整理するものであり、production `data/**`、Stage9 Composer仕様、#32 dictionary verdict、DEV仕様を勝手に変更しない。

## 最初に読む順

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #5 最新checkpoint
4. この `README.md`
5. 当面WAI17で試験する場合は `10_WAI17_LOCAL_FIRST_PROFILE.md`
6. 必要なジャンルだけ以下を読む

## ジャンル

| No. | ファイル | 何が分かるか |
|---|---|---|
| 01 | `01_PRODUCT_PURPOSE_AND_GUARDRAILS.md` | 製品目的、PROMPT班の役割、実験/実戦モード、ユーザー負担、禁止事項 |
| 02 | `02_MODEL_FAMILY_PROFILES.md` | WAI17 / Illustrious / NoobAI / Anima のfamily差 |
| 03 | `03_PROMPT_CONSTRUCTION_AND_SUPPORT.md` | Prompt内部構造、support分類、minimum sufficient、replacement slot |
| 04 | `04_HARD_TARGET_GENRES.md` | body-site、拘束、機械、非人間付属肢、multiple-Special、多人数等の難所分類 |
| 05 | `05_FAILURE_DIAGNOSIS_AND_ASSISTED_CONTROL.md` | 失敗原因の切り分け、Prompt-only ceiling、Forge Couple/ControlNet等への昇格 |
| 06 | `06_QUALITY_CAMERA_NEGATIVE_DENSITY.md` | quality/meta、camera、visibility、Negative、weighting、Prompt density |
| 07 | `07_EVALUATION_AND_STAGE10_TESTING.md` | A/B方法、scorecard、WD14境界、Stage10優先テスト |
| 08 | `08_SOURCES_EVIDENCE_AND_CORRECTIONS.md` | 出典階層、AIArtRecipe/としあきWiki、公式、Danbooru/e621、論文、訂正 |
| 09 | `09_HOLD_CONFLICT_AND_REVALIDATION.md` | 未確定事項、古い仮定、矛盾、Stage10/future #42で再検証するもの |
| 10 | `10_WAI17_LOCAL_FIRST_PROFILE.md` | 現在の実機WAI17 + Forge Neoに絞った当面のテスト基準 |
| Map | `LEGACY_SOURCE_MAP.md` | 既存Stage10 PROMPT文書を上のジャンルへ全件割り当てる索引 |

## 情報の強さ

PROMPT班では最低限次を区別する。

- `OFFICIAL_FACT`: exact model/extension作者の公式情報
- `AUTHOR_GUIDE`: 作者/配布者の運用説明
- `SEMANTIC_AUTHORITY`: Danbooru canonical/alias/implication等
- `RESEARCH_BACKGROUND`: 論文が示す一般的 failure mechanism
- `CONTROLLED_PRACTICAL`: 条件をある程度固定した実験
- `COMMUNITY_CANDIDATE`: 日本語Wiki/ブログ/Reddit等の実践知
- `PROJECT_HYPOTHESIS`: 上記から導いたStage10候補
- `HOLD / CONFLICT`: 根拠不足・版差・矛盾・実画像待ち

## Source precedence

単純な一列順位ではなく、主張の種類ごとに正本を分ける。

- タグの意味: Danbooru semantic authority
- model grammar/settings: exact model/version official
- parser/extension挙動: exact extension/runtime official
- failure mechanism: research + controlled evidence
- 実用上のコツ/失敗例: community evidenceを候補として保持し、上位情報と照合

共通原則:

- `tag exists` != `model recognizes tag`
- `model recognizes tag` != `correct binding`
- `Prompt contains token` != `image realizes intent`
- `community success` != `production rule`
- `caption order` != `universally optimal inference order`
- `assisted-control success` != `PROMPT_ONLY success`

## 旧資料の扱い

`docs/stages/STAGE_10_PROMPT_*.md` は削除・移動しない。

- 新ディレクトリ = 日常的に読む整理済み知識
- 旧Stage10文書 = 詳細証拠、監査履歴、個別site coverage、実験backlog

どの旧資料がどこへ属するかは `LEGACY_SOURCE_MAP.md` を正本とする。

## 更新規則

新しい知識が入ったら、まず該当ジャンルへ以下を追記する。

1. 何を改善する知識か
2. family/version scope
3. evidence class
4. ADOPT / HOLD / CONFLICT
5. Stage10で確認が必要か
6. 詳細出典/元文書

旧資料だけ増やしてIndexを更新しない状態を作らない。
