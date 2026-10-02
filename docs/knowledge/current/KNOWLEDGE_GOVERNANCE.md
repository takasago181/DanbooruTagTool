# KNOWLEDGE ガバナンス — Claim単位の現在ルール

Owner: Issue #44 `KNOWLEDGE:#44`

## 1. 現在判定の正本

`CLAIM_REGISTRY.csv` を、知識班のClaim単位の現在判定正本とする。

Registryで確認する:
- Claimの現在内容
- 出典の種類
- ACCEPTED / CANDIDATE / HOLD / CONFLICT / REJECTED / HISTORICAL
- 適用範囲
- 必要な再検証
- 根拠の場所
- downstream用途

Catalogは読みやすい説明、researchは根拠・履歴。
どちらもRegistryを勝手に上書きしない。

旧PROMPT班は2026-09-12にKNOWLEDGE #44へ統合済み。
`PROMPT`という文字列が残っていても、独立したteam authorityを意味しない。

## 2. Claim ID

形式:
`K-<DOMAIN>-<NNN>`

例:
- `GOV`
- `MODEL-WAI`
- `MODEL-ILL`
- `MODEL-NOOB`
- `MODEL-ANIMA`
- `SEM`
- `PROMPT`
- `SUPPORT`
- `BIND`
- `HARD`
- `NEG`
- `TOOL`
- `LORA`
- `EVAL`
- `EVID`
- `SOURCE`
- `HIST`
- `REJECT`

IDは再利用しない。

同じ意味のClaimを更新する場合は同IDを更新。
意味が別物になった場合は新IDを作り、`supersedes/contradicted_by`で関係を残す。

## 3. Registryの固定列

1. `ID`
2. `Claim`
3. `SOURCE_CLASS`
4. `STATUS`
5. `SCOPE`
6. `VALIDATION_STATE`
7. `source/evidence`
8. `last_checked`
9. `supersedes/contradicted_by`
10. `downstream_relevance`

列構造を変える時は、既存CSV/将来JSON変換への影響を確認する。

## 4. 出典種類（SOURCE_CLASS）

- `OFFICIAL_MODEL` — モデル公式の事実
- `AUTHOR_GUIDE` — 作者推奨の使い方・設定
- `OFFICIAL_RUNTIME` — runtime/extension公式挙動
- `SEMANTIC_AUTHORITY` — canonical / Alias / implication等の意味 authority
- `PROJECT_FACT` — project内で採用したルール・確認済み状態
- `CONTROLLED_PRACTICAL` — 条件を揃えた実践比較
- `RESEARCH` — 論文・一般研究
- `COMMUNITY` — communityの実践報告
- `LEGACY` — 旧前提・履歴

`SOURCE_CLASS`は「採用済みか」を表さない。

公式情報でも、そこから一歩進んだ解釈はCANDIDATE/HOLDになり得る。

## 5. 現在状態（STATUS）

- `ACCEPTED` — 現在の知識班判定として採用
- `CANDIDATE` — 有力だがcurrent ruleとしては未確定
- `HOLD` — 未解決。どちらかへ勝手に寄せない
- `CONFLICT` — scope/versionを分けても信頼できる根拠が食い違う
- `REJECTED` — 現在ルールとして明示的に不採用
- `HISTORICAL` — 履歴として保存し、現在の案内には使わない

ACCEPTEDでもscopeを外して一般化してはいけない。

## 6. 適用範囲（SCOPE）

代表:
- `GLOBAL_PRINCIPLE`
- `FAMILY:<name>`
- `MODEL_VERSION:<name>`
- `PROFILE:<name>`
- `RUNTIME:<name>`
- `EVALUATOR:<name>`
- `PROJECT_ONLY`

handoffや要約でもscopeを落とさない。

## 7. 検証状態（VALIDATION_STATE）

- `NOT_REQUIRED` — その狭い主張には追加ローカル検証不要
- `LOCAL_RECHECK` — local環境変更時に再確認
- `CONTROLLED_TEST_REQUIRED` — 生成効果Claimなので条件統制した試験が必要
- `STAGE10_REQUIRED` — 旧ラベルを含む画像依存検証。広範囲Stage10を自動承認する意味ではない
- `SOURCE_RECHECK_REQUIRED` — source/versionが変わり得るので重要利用前に再確認

STATUSと鮮度は別。

## 8. 混ぜてはいけない層

1. canonical tag identity
2. Alias
3. implication / hierarchy
4. related / co-occurrence
5. UI日本語・検索語
6. model trigger
7. generation support
8. Prompt-only能力
9. LoRA / Control / Edit後の能力
10. evaluator / human judgement
11. product/runtime採用

「意味が正しい」と「このモデルがよく反応する」は別Claim。

## 9. Claimを昇格する条件

CANDIDATE / HOLD / CONFLICTからACCEPTEDへ動かす時:
- exact scopeを維持
- 根拠identityを記録
- VALIDATION_STATEの要件を満たす
- 対立根拠を消さず整理
- `last_checked`更新
- Registry変更後に必要な説明正本だけ更新

画像依存の検証はClaimに必要な範囲へ絞る。
未解決を見つけたからといって、全件大規模試験へしない。

## 10. productionとの境界

KNOWLEDGEでACCEPTEDになっても自動では:
- production `data/**` を変更しない
- DEV実装を変えない
- runtime/UI behaviorを変えない
- AUDIT判定を変えない
- Stage10の大規模試験を承認しない
- v1必須要件へしない

product採用はmainのproduct/DEV routingが決める。

## 11. 旧ラベル

旧research文書を整理目的だけで一括書換えしない。

- 旧STATUS
- 旧PROMPT班名
- 旧Stage10
等は履歴として残し、現在解釈はRegistry / Legacy Mapから行う。

## 12. Source IDの一意性

`GENERATION_KNOWLEDGE_SOURCES.md` のSource IDは**全entryで一意**。

追加前:
1. 予定IDが既存にないか確認
2. 同一sourceを既存IDで参照できるなら再登録しない
3. 別entryへ同じIDを使わない
4. migrationでは先行entryを維持し、後発entryを新IDへ移す
5. 参照済みIDを変更する時は全参照を更新

2026-10-02修復:
`SOURCE_ID_MIGRATION_20261002.md`

## 13. research文書のidentity

researchの正式identityは**full filename**。

`BATCH_AN`のようなprefixだけを一意IDとして使わない。

既存のprefix衝突はprovenance保護のためrenameしない。
新規batchは既存prefixとの衝突を避ける。

## 14. current文書の重複禁止

現在結論は**最も適切な正本1か所**へ置く。

例:
- 基礎理論 -> `IMAGE_GENERATION_FOUNDATIONS_JA.md`
- モデル固有設定 -> `PRACTICAL_GENERATION_NOOB_ANIMA.md`
- 失敗診断 -> `ADULT_IMAGE_GENERATION_DECISION_TREE.md`
- 学習順 -> `ADULT_IMAGE_GENERATION_TEACHING_CURRICULUM.md`
- 教師の進め方 -> `ADULT_IMAGE_GENERATION_TEACHER_REFERENCE.md`
- workflow型 -> `LOCAL_ADULT_WORKFLOW_PLAYBOOK_20261002.md`

他文書では詳細を再掲せず、正本へリンクする。

## 15. 日本語-first

人間向け説明:
- 日本語を主
- 英語は技術原語・UI名・model名の補助
- 初出は日本語で役割説明
- 英単語の列挙だけで説明を済ませない

Claim / Source Registryの内部英語を無理に翻訳する規則ではない。
ユーザー向けに出す時は日本語へ咀嚼する。
