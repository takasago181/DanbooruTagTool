# Generation Profile v2.1 Family Structural Audit Report

## 実施内容

- Family rule 25件の`DefaultNeedsActor`、`DefaultNeedsBodypart`、`DefaultNeedsImplement`、
  `DefaultNeedsPose`、`DefaultNeedsCamera`、`DefaultNeedsSpatialAssignment`、
  `DefaultCompositionRole`を空欄へ変更した。
- family loaderをtri-state対応にし、空欄を`None`、`false`を明示falseとして保持した。
- `HIGH_CONFIDENCE_CORRECTIONS_v1.csv`指定の177件だけにFamily / Role / PromptUseMode修正を適用した。
  実変更数はFamily 153件、Role 162件、PromptUseMode 116件。
- `EXPLICIT_STRUCTURAL_OVERRIDES_240_v1.csv`指定の240件だけにtag-level構造metadataを適用した。
- `ACTOR_SEPARATION_REQUIRED`、`SELF_ACTOR_ROLE`、`COMPOSITION_OWNER_CANDIDATE`を
  inspection metadataとして保持した。
- builderは監査4表と正本・promotion planのID/Tag、件数、現行値、提案値を照合してから生成する。

## レビュー判断

監査内容はPromotionStatus境界、Alias Prompt identity、statistics canonical、model observation、
検索・統計・Candidate Aggregationを変更しないため、既存仕様と両立する。Family単位の物理要件を
無効化し、tag-levelの明示判断だけを昇格するため、未確定値をfalseやtrueへ推測しない。

最終監査でSpecialID 152と697を追加修正した。`multiple anal`は同一bodypartへの複数挿入として
`INSERTION_STRUCTURED`へ、`multiple penis fellatio`は複数別actorを必須と断定しない
`ACTION_INTERACTION`へ修正した。両者から`ACTOR_SEPARATION_REQUIRED`を外した。

## 保持した境界

- 元Special2788は変更していない。
- PromotionStatus件数は1,352 / 778 / 336 / 13 / 294 / 1 / 14を維持した。
- PROVISIONAL / PROVISIONAL_CORRECTION / REVIEW_REQUIRED 309件へproduction semantic / structural値を設定していない。
- Alias 778件は元Tag identityのままPrompt exportする。
- `AllowsAutomaticExpansion`は常にfalse。auto support injection、auto expansion、UI接続は追加していない。
- model observation 17件は変更していない。

## 監査入力

- `data/generation/audit/FAMILY_RULE_AUDIT_25_v1.csv`
- `data/generation/audit/HIGH_CONFIDENCE_CORRECTIONS_v1.csv`
- `data/generation/audit/EXPLICIT_STRUCTURAL_OVERRIDES_240_v1.csv`
- `data/generation/audit/APPROVED_STATIC_1352_REVIEW_v1.csv`
- `data/generation/audit/FAMILY_AUDIT_VALIDATION_v1.json`
- `docs/decisions/GENERATION_FAMILY_STRUCTURAL_AUDIT_v1.md`

## 検証項目

- 2,788 profileと7 PromotionStatus件数
- 25 familyの物理default / compositionが全て空欄
- 177 correctionのID/Tag・現行値・提案値と変更件数
- 240 explicit overrideのID/Tag・提案分類・構造値
- APPROVED_STATIC 1,352件の全監査表との一致
- 文脈tag、peek系、big belly、piledriver (sex)、cross-section、multi-actor flagの代表例
- audit-only、Alias export、検索・統計・PromptSession回帰
- builder再実行時のbyte-level idempotence
- 元Special2788 SHA-256

## 未解決事項

Family ruleとtag-level構造metadataは引き続きinspection-onlyで、Stage 7 UI / Prompt Composerへ
接続しない。

## 最終結果

- Generation Profile対象pytest: 33 passed
- 全回帰pytest: 106 passed in 10.28s
- builder連続2回の3 production CSVはそれぞれ同一SHA-256
- Special2788 SHA-256: `07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3`
- production profile SHA-256: `3d3b7c16bee23c34892c6ac1a40b69208ef14199c5bae749ac8a22151c8dc835`
- family rules SHA-256: `0f0e2e9f1f001d12e421324a6356bab42293fb206fe53a3e642495d5765c6936`
- model observations SHA-256: `ee036aac810ef94b9f0376a23d0159f4275d6d2feac7ccd689ca297d361164c8`（v2から不変）
