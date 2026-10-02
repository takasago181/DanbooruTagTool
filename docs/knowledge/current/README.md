# KNOWLEDGE current 管理層

Owner: Issue #44 `KNOWLEDGE:#44`  
状態: `CURRENT_MANAGEMENT_LAYER / CLAIM_REGISTRY_WINS`

このディレクトリは、知識班の**現在状態を管理する層**。research原本やtopic catalogの代わりではない。

## 正本の役割

| ファイル | 役割 | 書かないこと |
|---|---|---|
| `CLAIM_REGISTRY.csv` | Claim単位の現在判定 | 長い解説 |
| `HOLD_CONFLICT_REGISTER.md` | 未解決・対立 | 解決済み知識の再掲 |
| `VERSION_FRESHNESS_LEDGER.csv` | モデル・runtime・source鮮度 | 一般的な使い方 |
| `KNOWLEDGE_GOVERNANCE.md` | 採用・出典・ID管理規則 | モデル別レシピ |
| `CURRENT_QUICK_REFERENCE.md` | 30〜60秒の入口・索引 | 詳細設定・長い教材 |
| `IMAGE_GENERATION_FOUNDATIONS_JA.md` | 生成の基礎原理 | モデル別の細かい差 |
| `PRACTICAL_GENERATION_NOOB_ANIMA.md` | NoobAI / Animaのモデル固有実践 | 一般基礎・成人向け診断全般 |
| `ADULT_IMAGE_GENERATION_DECISION_TREE.md` | 成人向け生成の失敗診断 | モデルカードの重複 |
| `ADULT_IMAGE_GENERATION_TEACHING_CURRICULUM.md` | 教える順番・演習・合格条件 | 詳細な診断表 |
| `ADULT_IMAGE_GENERATION_TEACHER_REFERENCE.md` | 先生役の進め方・参照先 | モデル設定値の再掲 |
| `LOCAL_ADULT_WORKFLOW_PLAYBOOK_20261002.md` | 実ワークフローの型 | 一般診断の再掲 |
| `READING_ROUTES.md` | 用途別の読む順番 | Claimの再説明 |
| `LEGACY_MAP.md` | 旧資料の扱い | current判定 |
| `SOURCE_ID_MIGRATION_20261002.md` | Source ID修復記録 | 新しい知識 |
| `KNOWLEDGE_HYGIENE_AUDIT_20261002.md` | 整理監査・修復状態 | 技術正本 |

## 外側の層

- `../KNOWLEDGE_CATALOG.md` と `../catalog/*.md` — topic別の読み物
- `../GENERATION_KNOWLEDGE_CORPUS.md` — 横断的な長期統合
- `../GENERATION_KNOWLEDGE_SOURCES.md` — Source Registry
- `../research/*` — 詳細な根拠・実験・履歴
- `../GENERATION_KNOWLEDGE_INDEX.md` — historical coverage index

## 現在のプロダクト関係

v1の正本はmain `docs/PRODUCT_GOAL_LOCK.md`。

`理解 -> 発見 -> 選択 -> 出力`

知識班は生成知識を管理するが、知識があるだけでproduction/UIへ自動採用しない。

## 復元順

固定日付handoffはhistorical snapshotであり、live authorityではない。

1. main `docs/project/CURRENT_STATE.md`
2. main `docs/project/PERMANENT_RULES.md`
3. live Issue #44 本文・最新checkpoint
4. main `docs/PRODUCT_GOAL_LOCK.md`
5. このREADME
6. `CURRENT_QUICK_REFERENCE.md`
7. `CLAIM_REGISTRY.csv`
8. 必要なtopic catalog
9. HOLD / freshness
10. researchは根拠確認が必要な時だけ

## 更新規則

`research -> Source登録 -> Claim確認 -> Registry -> 必要な正本1か所だけ更新 -> HOLD/freshness -> #44 checkpoint`

**同じ現在結論を複数current文書へコピーしない。**

## 言語規則

人間向け説明は**日本語を主、英語は補助**。
モデル名、タグ、Prompt、Sampler名、API名など実体の識別子は原文を保持してよい。

## 恒久境界

- semantic truth と generation effectivenessを分ける
- model/version/profileをClaimの一部として扱う
- HOLDを推測で閉じない
- research原本をcurrent authorityにしない
- production `data/**` は別権限
- 旧PROMPT班はhistorical。新規作業はKNOWLEDGE #44
