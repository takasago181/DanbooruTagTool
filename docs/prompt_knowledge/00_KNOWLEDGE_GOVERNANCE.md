# 00 PROMPT Knowledge Governance

Owner: PROMPT / Issue #5
Status: PROMPT知識管理規格。production仕様ではない。
Last normalized: 2026-09-09

## 目的

PROMPT班の知識が増えても、

- 何が事実か
- 何が仮説か
- 何が古いか
- どのmodel/versionだけに当てはまるか
- どこを読めばよいか

を人間とChatGPTの両方が同じように復元できるようにする。

この規格は、知識そのものより**知識の読み方**を固定する。

---

## 1. 知識は「出典」と「採用状態」を分ける

旧資料では `OFFICIAL_FACT`、`COMMUNITY_JA_STRONG`、`HOLD` 等が一列のlabelとして混在していた。
今後は必ず2軸に分ける。

### SOURCE_CLASS — 誰/何が根拠か

- `OFFICIAL_MODEL` — exact model/versionの公式model card・作者公式ページ
- `AUTHOR_GUIDE` — 作者/配布者の一次運用説明。mirrorの場合はmirrorを明記
- `OFFICIAL_RUNTIME` — runtime/parser/extensionの公式repo・実装
- `SEMANTIC_AUTHORITY` — Danbooru canonical/alias/implication。e621補助は別scopeを明記
- `PROJECT_FACT` — DanbooruTagToolのexact条件で確認済みの実測/GitHub証跡
- `CONTROLLED_PRACTICAL` — 条件を意図的に固定した比較・再現試験
- `RESEARCH` — 論文・benchmark等。failure mechanismの背景
- `COMMUNITY` — Wiki/blog/Note/Reddit等の実践観察
- `LEGACY` — 過去資料・historical snapshot。現在の採用判断には単独使用しない

### STATUS — 今どう扱うか

- `ACCEPTED` — 現在scope内で採用してよい
- `CANDIDATE` — 有望だがStage10/local evidence等が必要
- `HOLD` — 根拠不足/外部Gate待ち。production rule化禁止
- `CONFLICT` — 根拠が衝突。片方を消さずcontrolled A/B等で解く
- `REJECTED` — 誤り/不適切な一般化として不採用
- `HISTORICAL` — 過去には有用だったがcurrent defaultにはしない

重要:
`OFFICIAL_MODEL`でも`CANDIDATE`になり得る。
例: 作者推奨settingsは公式事実だが、hard-targetに最適という主張は別claimでありStage10候補。

---

## 2. SCOPEを必ず持つ

知識は最低でも次のいずれかへscopeする。

- `GLOBAL_PRINCIPLE`
- `FAMILY:<name>`
- `MODEL_VERSION:<exact>`
- `RUNTIME:<name/version>`
- `PROFILE:<project profile id>`
- `TARGET_CLASS:<class>`
- `PROJECT_ONLY`

禁止:
- WAI17の結果をIllustrious全体へ無断拡張
- Anima Base/Aesthetic/Turboを同じ挙動として扱う
- parser構文をmodel grammarとして扱う
- Danbooru semantic relationをmodel response equivalenceとして扱う

---

## 3. VALIDATION_STATE

実画像/ローカル検証が必要かを別欄で持つ。

- `NOT_REQUIRED` — 語義や公式仕様など、現在のclaim自体にはStage10不要
- `LOCAL_RECHECK` — current local version/environmentで再確認が必要
- `STAGE10_REQUIRED` — production behaviorへ昇格する前にcontrolled image evidenceが必要
- `EXTERNAL_GATE` — dictionary freeze / evaluator allocation / DEV decision等待ち
- `VALIDATED_LOCAL` — exact local conditionsで確認済み

`VALIDATED_LOCAL`をglobal truthへ昇格しない。

---

## 4. CLAIM ID

重要な知識は `CLAIM_REGISTRY.md` で1件1IDを持つ。

形式:
`K-<DOMAIN>-NNN`

Domain例:
- `PURPOSE`
- `SEM`
- `WAI`
- `ILL`
- `NOOB`
- `ANIMA`
- `STRUCT`
- `QUALITY`
- `FAIL`
- `CTRL`
- `EVAL`
- `TEST`
- `UX`

Claim IDの目的:
- 同じ知識を別文書で違う言い方にして矛盾させない
- Issue commentから特定claimを参照できる
- Stage10結果でclaimだけを昇格/降格できる
- 新チャットが「何が確定しているか」を短時間で復元できる

---

## 5. CURRENT AUTHORITYの優先順位

日常判断は次の順で読む。

1. `CURRENT_STATE.md` / `PERMANENT_RULES.md` — project state/rules
2. Issue #5 latest checkpoint — PROMPT current work state
3. `docs/prompt_knowledge/README.md` — navigation
4. `CLAIM_REGISTRY.md` — current claim status
5. 該当ジャンル `0X_*.md` — explanation/context
6. `VERSION_AND_FRESHNESS.md` — version/freshness
7. legacy Stage10 docs / old branch — evidence/provenance only

旧資料が新registryと食い違う場合、**旧資料を現在の採用状態として使用しない**。
証拠内容そのものを再確認する必要があれば旧資料へ戻る。

---

## 6. Claimの必須フィールド

重要claimは最低限以下を持つ。

- Claim ID
- Claim text
- Domain
- SOURCE_CLASS
- STATUS
- SCOPE
- VALIDATION_STATE
- Primary source / evidence pointer
- Last checked
- Notes / conflict if any

model/runtime依存claimでは追加:
- exact model/version
- checkpoint/hash if project-local
- runtime/version where relevant

---

## 7. 更新時のルール

新しい知識を得た場合:

1. 既存Claim IDで表せないか確認
2. 同じ意味のclaimを新規作成しない
3. sourceとstatusを分けて記録
4. exact scopeを付ける
5. conflictなら既存claimを消さず`CONFLICT`へ
6. Stage10/local testが必要ならvalidationを明記
7. 該当ジャンル文書を更新
8. version/freshnessへ影響するなら更新
9. material changeならIssue #5 checkpoint

Stage10で結果が出た場合:
- claim単位でstatus/validationを変更
- test条件をevidence pointerとして残す
- 一つの成功画像でfamily/globalへ昇格しない

---

## 8. 重複の扱い

原則:
- `CLAIM_REGISTRY.md` = 採用状態の正本
- `0X_*.md` = 読みやすい説明
- `docs/stages/STAGE_10_PROMPT_*.md` = 詳細証拠/履歴

同じclaimを3箇所で独立管理しない。
ジャンル文書にはClaim IDを参照できる形を徐々に増やす。

---

## 9. 削除方針

整理目的だけで旧資料を削除しない。

削除候補になるのは:
- 完全重複し、provenance価値もない
- 別文書への参照が完全である
- Issue/commit履歴で復元できる
- PROMPT/AUDIT上の証跡として不要

現段階ではlegacy資料を保持する。

---

## 10. 読解チェック

新チャットが正しく復元できたかは、次を答えられるかで確認する。

1. 今最優先model/profileは何か
2. その設定のどこまでがFACTでどこからがCANDIDATEか
3. hard-target失敗を何種類に分けるか
4. HOLDはどこを見るか
5. WD14が答えられない時にFAILにしてよいか
6. assisted-control成功をPrompt-only成功に数えてよいか
7. old Stage10 docとClaim Registryが矛盾したらどちらをcurrent verdictに使うか

答えられなければknowledge organizationが不十分とみなす。
