# Special2788 Generation Profile v2 — Implementation Report

実施日: 2026-09-06

## 事前レビュー

`SPECIAL2788_PROFILE_PROMOTION_v1.zip` の優先3文書と既存Phase 1実装を照合した。

- 指示書が入力として記載する `SPECIAL2788_DEEP_AUDIT_OVERLAY.csv` はZIPに含まれていなかった。
- `PROMOTION_PLAN.csv` には2,788件のSpecialID/Tag/Layer/canonical target、promotion status、
  昇格候補フィールド、evidence、16件のLocalTestEvidenceが含まれ、元SpecialとのID/Tag/Layer順序不一致は0件だった。
- status件数は `PROMOTION_COUNTS.json` とdecision記載に一致した。
- 実装に必要な確定入力はPROMOTION_PLANだけで足りるため、欠落overlayを推測生成せず実装を継続した。
- Decisionの推奨列名 `ApprovalStatus` とtaskの必須名 `PromotionStatus` に差があったため、
  loader参照要件が明示された `PromotionStatus` を採用した。
- family defaultの具体値は入力に存在しなかった。25 familyへ保守的なruleを追加したが、
  inspection専用であり、Promptへの自動追加は常に禁止した。値はChatGPT監査対象とする。

レビューの結果、元辞書変更、Alias置換、model scoreのstatic固定、未確定行の自動昇格を避ければ
既存仕様を破壊せず実装可能と判断した。

## 1. 変更した項目

- `GenerationProfile` をv2 static schemaへ移行。S/A/B/Cとmodel-dependent列を削除。
- `PromotionStatus`、approved static metadata、family rule参照、空欄継承override、evidenceを追加。
- `GenerationFamilyRule`、`GenerationModelObservation`、`GenerationProfileStore`、
  `effective_profile()` inspection APIを追加。
- full static profile 2,788行、family rules 25行、model observations 17行を生成。
- APPROVED_STATIC 1352、APPROVED_IDENTITY_ONLY 778、APPROVED_SEMANTIC_ROLE 336、
  APPROVED_CORRECTION_METADATA 13だけを各promotion ruleの範囲で昇格。
- PROVISIONAL 294、PROVISIONAL_CORRECTION 1、REVIEW_REQUIRED 14はidentity/status/evidenceだけ保持し、
  production semanticsとauto-expansionを空欄/falseに固定。
- PROMOTION_PLANとcountsをaudit入力として保存し、再生成toolを追加。
- Phase 1テストをv2 static/family/observation分離へ更新。

## 2. 変更しなかった項目

- `data/special2788/illustrious_tag_knowledge_base_2788.csv` および他の正本。
- SpecialのTag、日本語、Layer、カテゴリ、canonical_target、post_count、Prompt identity。
- canonical/alias/semantic解決優先、search ranking、statistics、Candidate Aggregation。
- PromptSession export。元Alias表記をchosen canonicalへ置換しない。
- UI、Prompt Composer、support自動追加、region conditioning。
- 内容カテゴリによるfilter、penalty、suppression。

## 3. 新規作成ファイル

- `data/generation/generation_family_rules.csv`
- `data/generation/generation_model_observations.csv`
- `data/generation/audit/PROMOTION_PLAN_v1.csv`
- `data/generation/audit/PROMOTION_COUNTS_v1.json`
- `docs/decisions/PROFILE_PROMOTION_DECISION.md`
- `docs/GENERATION_PROFILE_V2_MIGRATION.md`
- `docs/stage_reports/GENERATION_PROFILE_V2_REPORT.md`
- `tools/build_generation_profile_v2.py`

変更:

- `data/generation/special2788_generation_profile.csv`
- `danbooru_tag_tool/generation_profile.py`
- `danbooru_tag_tool/knowledge.py`
- `danbooru_tag_tool/prompt_session.py`（identity保持をv2用語へ明確化するcommentのみ）
- `docs/GENERATION_PROFILE_SCHEMA.md`
- `tests/test_generation_profile.py`

## 4. バックアップ先

- 入力ZIPと展開内容: `backups/profile_v2_input_20260906_0229/`
- Phase 1変更前実装: `backups/profile_v2_preimplementation_20260906_0235/`

入力ZIPの外部原本とbackupコピーはSHA-256一致。

## 5. 実施したテスト

- 元SpecialとPROMOTION_PLANの2,788件ID/Tag/Layer/canonical_target照合。
- plan、counts JSON、production profileのstatus件数照合。
- builder再実行前後の3生成CSV SHA-256一致（決定的再生成）。
- 元Special SHA-256前後一致と既存FILE_HASHES照合。
- 2,788件left join、approved/audit-only境界、全778 Alias identity export。
- PROVISIONAL/REVIEW_REQUIREDの検索・手動選択・保存・export、auto-expansion=false。
- family default継承、per-tag override優先、family link整合性。
- 16 local observation、unknown checkpoint、複数SpecialID combination、static非変更。
- search/statistics/Candidate Aggregation不変性。
- malformed schema/boolean/status/family/observation/driftの拒否。
- py_compile、pytest全回帰。

## 6. テスト結果

- v2専用: **24 passed**。
- 全回帰: **97 passed in 12.00s**。
- static=2,788、families=25、observations=17。
- generator idempotence、source hash、promotion counts、全回帰すべてPASS。

## 7. 未解決事項

- ZIPにDeep Audit overlayが無かったため、そのファイル独自の追加情報は取り込んでいない。
  PROMOTION_PLAN外の情報を推測していない。
- family defaultの具体値は提供済みdecisionに含まれない実装上の保守的設定であり、ChatGPT監査対象。
- 309 audit-only行の意味確定、model checkpoint/settings、画像evidenceは未解決のまま。
- UI/Composer接続は今回の範囲外。

## 8. 次にChatGPTへ渡す情報

本report、v2 schema、migration note、promotion decision、static profile、family rules、observations、
主要loader/store、builder、knowledge integration、testを渡す。

ChatGPTはpromotion件数、audit-onlyの空欄保証、Alias Prompt identity、family defaults、
observation分離、auto-expansion禁止、元Special不変性を監査する。
