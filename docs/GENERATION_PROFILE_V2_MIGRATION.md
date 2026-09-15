# Generation Profile Phase 1 → v2 migration

## 変更

Phase 1の14行static fixtureを、base 2,788行 + Issue #96 accepted 195行の2,983行promotion-aware static profileへ拡張した。
Special Core Dictionary のbase production snapshot（元 `Special2788` corpus）は互換上維持し、accepted canonical expansionはhash-pinned proposalから明示build時に追加する。
v2のprimary keyとPrompt identityもSpecialID/Tagを使用する。既存ID 1..2788は不変、新規IDはappend-onlyの2789..2983。

Phase 1 static列のうち、S/A/B/C、model-dependent score、CoexistenceScore、
ModelProfile、経験的Confidenceはv2 staticから削除した。Phase 1ではscore/classがすべて空欄だったため、
数値データの損失はない。Needs系はfamily default + optional per-tag overrideへ置き換え、
base 2,788行への同値複製を避け、accepted expansion 195行だけを明示的に追加した。

`RecommendedSupport` / `ExpansionHint` はPrompt自動注入へ誤用され得るためstaticから外した。
v2はfamily requirementをinspection APIで返すだけで、supportを追加しない。

## 観察の保存

Phase 1のモデル依存情報は `generation_model_observations.csv` へ分離した。
提供されたPROMOTION_PLANのLocalTestEvidence 16件を移し、Phase 1の
anal fisting + vaginal object insertion共存報告をCOMBINATION観察として保存した。

checkpoint、seed、steps、CFG、size、sampler、schedulerが不明な行は空欄または
`Checkpoint=unknown` とし、推測で補完していない。

## compatibility

既存の `TagKnowledgeCore.load()`、検索、CoreTagSet、PromptSession、statistics APIは変更しない。
`load_generation_profile(path)` のleft joinも維持するが、pathのCSVはv2 schemaを要求する。
Phase 1 CSVそのもののruntime互換loaderは保持しない。移行前ファイルは
`backups/profile_v2_preimplementation_20260906_0235/` に保存され、移行後の正式CSVと混在しない。

PROVISIONAL / PROVISIONAL_CORRECTION / REVIEW_REQUIREDはstatusを読み出せるが、
production semantic fieldsは空欄であり、手動選択・export以外の確定処理を起動しない。

## v2.1 family structural audit

v2.1ではfamily membershipから物理要件を推測しない。25 familyの`DefaultNeeds*`と
`DefaultCompositionRole`を空欄へ変更し、loaderとeffective profileで空欄を`None`として保持する。
明示的な`false`は`None`と区別する。

分類・role・PromptUseModeは監査指定177件だけを修正した。物理構造は監査指定240件だけを
tag-level overrideへ設定した。`ACTOR_SEPARATION_REQUIRED`は`NeedsActor`と独立したflagであり、
いずれのmetadataもsupport追加やPrompt expansionを起動しない。
