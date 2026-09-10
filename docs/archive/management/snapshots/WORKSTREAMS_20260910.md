# DanbooruTagTool 作業ダッシュボード

> **HISTORICAL SNAPSHOT — CURRENT ROUTINGには使用しない**
>
> このファイルは 2026-09-10 時点の人間向けスナップショットで、現在地の正本ではありません。
> 内容には現在はsuperseded/completedになった #46 や、当時の #44 -> #30 順序などが残っています。
> **現在地・担当・依存関係は必ず `docs/project/CURRENT_STATE.md` と live GitHub Issueを使用してください。**
>
> 2026-09-11 cleanup auditで、誤routing防止のため現行ダッシュボード用途を終了しました。歴史記録として本文は下に保存しています。

---

## Historical content (2026-09-10)

最終更新: 2026-09-10

> このファイルは **人間向けの見やすい要約** です。
> 正本ではありません。
> 正式な現在地は `docs/project/CURRENT_STATE.md`、実作業の条件・結果は各GitHub Issueを参照してください。

## まずここだけ見ればOK

**現在地:** Stage9完了 / Special Core Dictionary freeze完了 / Stage10準備中。

**current core DEV:** NONE。

今すぐ並列で動かせる主作業は2本です。

1. **UI・日本語最終収束** — `#46 -> #36`
2. **Evaluator coverage調査** — `#44`

その後の正規順序は:

`#44 -> #30 -> #42 -> #5 -> Stage10`

#42を開始する前に、#36/#46と#34のうちStage10評価に影響するUI-JA/data課題を完了するか、明示的に別Gateへ分離します。

---

## 状態の見方

- 🟢 **今進めてよい** — prerequisite satisfied
- ⏸️ **待機 / Gateあり** — 他Issueの結果待ち
- 🛠️ **保守 / 横断課題** — mainlineとは別に放置しない
- ✅ **完了** — 再実行しない

---

# 1. Special Core Dictionary

**状態: ✅ 完了**

関連:
- #32 validation — completed / closed
- #48 independent promotion audit — completed
- #49 production-safe fix promotion — completed / closed
- #43 naming/freeze — `PASS_ISSUE43_FREEZE` / completed / closed

Final production facts:
- 2,788 entries
- 2,788 unique SpecialID
- order unchanged
- production profile SHA-256: `55490940378e15d8e41454e701d0c202abbab307a08fb6e56841171e0edec1fd`

正式用語:
- `Special Core Dictionary` — formal concept
- `Special2788` — historical/snapshot/compatibility identifier
- `Core Tag Set` — user-selected nucleus

Parked evidenceは捨てない:
- REVIEW 305
- Special IMAGE_TEST_REQUIRED 17
- semantic-support IMAGE_TEST_REQUIRED 33

これらは#42/#30/Stage10 controlled testsで必要なものだけ再評価します。

---

# 2. UI・日本語改善

大元: #34

## 2-A. UI本体

**状態: ✅ #35完了**

日本語-first UI本体は完了済み。再実装対象ではありません。

## 2-B. 日本語overlay最終収束

**状態: 🟢 今進めてよい**

関連:
- #46 — `FULL_EXECUTION_AUTHORIZED / PRODUCTION_PROMOTION_NOT_AUTHORIZED`
- #36 — `REEXECUTION_PENDING`

現在の流れ:

`#46 30,629 full orchestration -> #36 V3.1 revalidation -> separate independent production-promotion gate`

重要:
- #46完了だけでproduction反映しない
- #36再検証PASS後も別promotion gateが必要
- 過去の#38/#39/#41等のpilot/旧実装を現行作業として再開しない

## 2-C. #34親Issueの残件

**状態: 🛠️ OPEN / cross-cutting**

#36 translation laneとは別に、以下の親課題を保持:
- 日本語 + 英語 bilingual search
- substring/fuzzy由来の検索ノイズ
- parent-level UI/search concerns

#42開始前に、Stage10評価へ影響する残件を完了するか、明示的に別Gateへ分離します。

---

# 3. KNOWLEDGE / Evaluator coverage

**状態: 🟢 今進めてよい**
**関連: #44**

Special Core Dictionary freeze prerequisiteは完了済み。

次の重点:
- WD14 / `wd-eva02-large-tagger-v3`
- Kagami-24k
- CL Tagger v2 stable/fixed release

最終2,788 entriesに対してcoverage/capabilityを整理し、#30へ返します。

目的は「Taggerをground truthにする」ことではなく、
- どのSpecialをAUTO判定候補にできるか
- どれをREVIEWへ送るべきか
- evaluator vocabulary不足を生成FAILと誤認しない

ための能力境界を決めることです。

---

# 4. Forge Neo A/B自動化

**状態: ⏸️ #44 coverage待ち**
**関連: #30**

完了済み:

`Prompt -> Forge Neo API -> fixed-seed A/B -> PNG -> actual metadata -> evaluator raw output`

Infrastructure verdict: `PASS_PIPELINE`

残り:
- #44 evaluator coverage受領
- representative Special case selection
- `AUTO / REVIEW / BLOCKED` calibration
- evidence-supportedな場合のみcandidate `A_WIN / B_WIN`
- REVIEWだけを人間が効率よく見る運用確認

外部/既存ツール優先。大規模な独自GUI・実験プラットフォームは作りません。

---

# 5. Stage10前 product-purpose improvement

**状態: ⏸️ RESERVED / UI-JA-data Gate待ち**
**関連: #42**

Dictionary freezeは完了済み。

開始前に必要:
- #36/#46のmaterialなUI-JA/data課題完了
- #34のStage10評価に影響する残件を完了または明示分離

主な対象:
- 日本語意図の揺れ
- Special/support競合
- model-family差
- failure diagnosis
- Prompt bloat / pruning
- minimum sufficient Prompt
- parked REVIEW/IMAGE_TEST_REQUIREDのうち必要な再評価

#42は単なる仕上げではなく、Stage10で評価する製品状態を固めるGateです。

---

# 6. Prompt正式handoff

**状態: ⏸️ GATED**
**関連: #5**

Formal completionに必要:
1. #44 evaluator coverage
2. #30 representative routing/calibration
3. #42 product-purpose improvement result
4. remaining `STAGE_10_PREP.md` checks

#42の結果を取り込む前に#5をfinalizeしません。

---

# 7. Protected-data保守

**状態: 🛠️ OPEN / safety debt**
**関連: #24**

GitHub外local protected dataについて:
- inventory
- backup location/freshness
- checksum/manifest
- reacquisition/rebuildability分類
- non-destructive restore verification

を完成させます。

Stage10 mainlineとは別枠ですが、今回のprotected-data incidentを踏まえ、見えない技術負債として放置しません。

---

# 8. GitHub管理

GitHub Project管理ボード導入 #47 は **NOT PLANNED / closed**。

管理の正規3層:
1. `CURRENT_STATE.md` — 全体routing/current state
2. 各Issue — task contract/evidence
3. `CURRENT_DEV_TASK.md` — current core DEV mirror

管理正本をこれ以上増やしません。

---

# 今の流れを1本で見る

```text
Stage9 完了
   ↓
Special Core Dictionary
#32 -> #48 -> #49 -> #43
   ✅ 完了 / freeze済み

今は並列:
   ├─ #46 -> #36 -> independent UI-JA promotion gate
   └─ #44 evaluator coverage

横断:
   ├─ #34 remaining UI/search concerns
   └─ #24 protected-data maintenance

その後:
#44
  ↓
#30 representative calibration
  ↓
#42 product-purpose improvement
  ↓
#5 formal Prompt handoff
  ↓
STAGE_10_PREP remaining checks
  ↓
Stage10 production A/B
```

---

# あなた向け超短縮版

**今やる:**
- #46 / #36 UI-JA最終収束
- #44 Tagger/evaluator coverage

**次:**
- #30 A/B自動判定calibration
- #42 Prompt/searchの本質改善
- #5 Stage10正式handoff

**横で忘れない:**
- #34 UI/search親残件
- #24 protected-data backup/restore

**もうやり直さない:**
- #32全件辞書検証
- #35 UI本体
- #43 naming/freeze
- 過去の#38/#39/#41 pilot系

最終的な正本は常に `CURRENT_STATE.md` とlive Issueです。
