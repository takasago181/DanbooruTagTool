# PROMPT Knowledge Index

最終更新: 2026-09-09
Owner: PROMPT / Issue #5
Status: PROMPT班の知識ナビゲーション正本。**本体production仕様ではない。**

## 目的

このディレクトリは、PROMPT班が蓄積した知識を「調査した順」ではなく「何を知りたいか」で読めるように整理した入口。

DanbooruTagToolのPROMPT側の現在目的は、単なるタグ整形ではなく、**日本語の制作意図からSpecialを核に必要な構造・supportを選び、対象model familyで高品質かつ難度の高いニッチ/複合画像を少ない手直しで成立させやすいPromptへ変換すること**。

ここにある文書はPROMPT側の知識・監査・Stage10候補を整理するものであり、production `data/**`、Stage9 Composer仕様、#32 dictionary verdict、DEV仕様を勝手に変更しない。

---

## 最初に読む順

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #5 最新checkpoint
4. この `README.md`
5. `CURRENT_QUICK_REFERENCE.md` — **30秒で現在地を掴む**
6. `00_KNOWLEDGE_GOVERNANCE.md` — 知識の読み方/label規格
7. `CLAIM_REGISTRY.md` — **現在どのclaimを採用/HOLD/REJECTしているかの正本**
8. 当面WAI17で試験する場合は `10_WAI17_LOCAL_FIRST_PROFILE.md`
9. `USE_CASE_ROUTES.md` から今の作業に必要なジャンルだけ読む

通常復元でlegacy Stage10資料を全読しない。

---

## Current authority model

### 30秒要約
`CURRENT_QUICK_REFERENCE.md`

### Current verdict / adoption state
`CLAIM_REGISTRY.md`

### Human-readable explanation
`01`–`10` のカテゴリ文書

### Version / freshness
`VERSION_AND_FRESHNESS.md`

### Detailed evidence / provenance
`docs/stages/STAGE_10_PROMPT_*.md` と旧branch資料

### Legacy label translation
`LABEL_MIGRATION_MAP.md`

旧資料とClaim Registryが食い違う場合:
- **current verdict = Claim Registry**
- old doc = evidence/history

---

## ジャンル

| No. | ファイル | 何が分かるか |
|---|---|---|
| 00 | `00_KNOWLEDGE_GOVERNANCE.md` | SOURCE/STATUS/SCOPE/VALIDATION、Claim ID、更新規格 |
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

### 管理・検索

| ファイル | 役割 |
|---|---|
| `CURRENT_QUICK_REFERENCE.md` | 人間/ChatGPT向け30秒current snapshot |
| `CLAIM_REGISTRY.md` | 重要知識を1件1IDで管理するcurrent verdict正本 |
| `VERSION_AND_FRESHNESS.md` | exact version / source確認日 / local applicability |
| `USE_CASE_ROUTES.md` | WAI17、failure診断、Stage10、source監査等の用途別最短読取ルート |
| `LABEL_MIGRATION_MAP.md` | 旧labelを新SOURCE_CLASS + STATUSへ読み替える |
| `LEGACY_SOURCE_MAP.md` | 既存Stage10 PROMPT文書をジャンルへ全件割り当てる索引 |
| `CATALOG_MANIFEST.md` | knowledge base inventory |

---

## 新しい知識ラベル規格

旧来の `OFFICIAL_FACT / COMMUNITY_JA_STRONG / HOLD...` の一列labelはcurrent管理では使わず、二軸へ分ける。

### SOURCE_CLASS
- `OFFICIAL_MODEL`
- `AUTHOR_GUIDE`
- `OFFICIAL_RUNTIME`
- `SEMANTIC_AUTHORITY`
- `PROJECT_FACT`
- `CONTROLLED_PRACTICAL`
- `RESEARCH`
- `COMMUNITY`
- `LEGACY`

### STATUS
- `ACCEPTED`
- `CANDIDATE`
- `HOLD`
- `CONFLICT`
- `REJECTED`
- `HISTORICAL`

さらに `SCOPE` と `VALIDATION_STATE` を持つ。
詳細は `00_KNOWLEDGE_GOVERNANCE.md`。

重要:
**公式情報であることと、production最適化として採用済みであることは別。**

---

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

---

## 旧資料の扱い

`docs/stages/STAGE_10_PROMPT_*.md` は削除・移動しない。

- 新ディレクトリ = 日常的に読む整理済み知識
- Claim Registry = 現在の採用状態
- 旧Stage10文書 = 詳細証拠、監査履歴、個別site coverage、実験backlog

どの旧資料がどこへ属するかは `LEGACY_SOURCE_MAP.md`。
旧labelは `LABEL_MIGRATION_MAP.md` で読み替える。

---

## 更新規則

新しい重要知識が入ったら:

1. 既存Claim IDで表せるか確認
2. `CLAIM_REGISTRY.md` のstatus/source/scope/validationを更新
3. 該当ジャンルへ説明を反映
4. version/freshnessに関係すれば更新
5. 詳細source/provenanceをLegacy mapへ登録
6. HOLD/conflictなら09にも残す
7. material changeならIssue #5 checkpoint

**旧資料だけ増えてIndex/Claim Registryを更新しない状態を作らない。**
