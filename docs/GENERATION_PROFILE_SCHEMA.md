# Special2788 Generation Profile v2.1

## 境界

正本は `data/special2788/illustrious_tag_knowledge_base_2788.csv`。
Generation Profileは、正本へ書き戻さないread-only sidecarである。
Tag、日本語、Layer、カテゴリ、canonical_target、post_count、Prompt identityを変更しない。

v2は次の3レイヤーを分離する。

1. `data/generation/special2788_generation_profile.csv`: モデル非依存のstatic metadataとpromotion status。
2. `data/generation/generation_family_rules.csv`: family分類とdefault PromptUseMode。物理要件defaultは未確定。
3. `data/generation/generation_model_observations.csv`: checkpoint・設定・試行に依存する観察。

入力判断資料は `data/generation/audit/PROMOTION_PLAN_v1.csv` と
`docs/decisions/PROFILE_PROMOTION_DECISION.md` に保存する。production loaderはplanを直接使用しない。

## Static Generation Profile

主キーは既存 `SpecialID`。`Tag` は完全一致のdrift guardであり、join keyの代替ではない。

|列|意味|
|---|---|
|SpecialID / Tag|既存Special identity|
|PromotionStatus|下記7状態|
|MeaningStatus / MeaningConfidence / SourceGlossQuality|昇格が承認された意味metadata|
|GenerationFamily / GenerationRole / PromptUseMode|昇格が承認された構造metadata|
|FamilyRuleId|family defaultへの参照|
|CompositionRoleOverride|空欄/role。空欄はtag-levelで未確定|
|ActorRequirementOverride|空欄/true/false。空欄はUNKNOWN / NOT ASSERTED|
|BodypartRequirementOverride|同上|
|ImplementRequirementOverride|同上|
|PoseRequirementOverride|同上|
|CameraRequirementOverride|同上|
|SpatialAssignmentOverride|同上|
|ShapeConflictGroup / SpecialFlags|静的な補助flag。現在ShapeConflictGroupは未設定|
|RecommendedHandling|承認済みmetadataの利用上の注意|
|EvidenceClass / EvidenceRefs|promotion根拠の区分・参照|

PromotionStatus:

- `APPROVED_STATIC`: family/role/mode等をstaticへ昇格。
- `APPROVED_IDENTITY_ONLY`: Alias identityのみ承認。Promptは元Aliasを保持し、modeは`ALIAS_PRESERVE`。
- `APPROVED_SEMANTIC_ROLE`: search/support roleのみ。直接モデル認識やcanonicalを捏造しない。
- `APPROVED_CORRECTION_METADATA`: 正本を直さず、訂正metadataだけをoverlay化。
- `PROVISIONAL` / `PROVISIONAL_CORRECTION`: identity/status/evidenceだけを保持。production意味は空欄。
- `REVIEW_REQUIRED`: identity/status/evidenceだけを保持。意味を補完しない。

件数は順に1352 / 778 / 336 / 13 / 294 / 1 / 14、合計2,788。
audit-only 309件へMeaning/Family/Role/Mode/Rule/Override/RecommendedHandlingを設定するとloaderが拒否する。
全行は検索、Core選択、保存、統計解決、Prompt exportから失われない。

`GenerationClass` S/A/B/Cはv2で保存しない。
`StandaloneVisuality`、`BodypartClarity`、`ActionClarity`、`ActorClarity`、
`CoexistenceScore`、`SupportDependency`、`ModelProfile`、経験的`Confidence`もstaticには保存しない。
特にcoexistenceはタグ単体の固定値にしない。

## Family Rules

`FamilyRuleId`を主キーとし、family、default PromptUseMode、actor/bodypart/implement/
pose/camera/spatial assignment requirement、composition role、notesを保持する。v2.1監査では
25 familyすべての物理要件defaultとcomposition roleを空欄にした。

family defaultとtag overrideはいずれもtri-stateで、空欄は`None`として読む。`false`は明示的な
不要、空欄は未確定であり、相互変換しない。`GenerationProfileStore.effective_profile()`は、
tag override、明示family default、`None`の順でread-onlyなeffective値を返す。

v2.1では監査済み240件だけにtag-level構造overrideを設定した。`NeedsActor=true`はactingまたは
participating roleを構造上解決する必要があるという意味で、別人物の追加を意味しない。
複数actorの分離が必要な場合は独立した`ACTOR_SEPARATION_REQUIRED` flagを使用する。
`SELF_ACTOR_ROLE`と`COMPOSITION_OWNER_CANDIDATE`もinspection metadataである。

requirementは補助候補を考えるための構造情報であり、support tagを自動追加する命令ではない。
`EffectiveGenerationProfile.AllowsAutomaticExpansion` は常にfalse。
このPhaseではPrompt ComposerやUIへ自動接続しない。

## Model Observations

列:

- ObservationID
- ModelProfile / Checkpoint
- Seed / Steps / CFG / Size / Sampler / Scheduler
- TestType (`SINGLE` / `COMBINATION` / `STRESS`)
- SpecialIDs（semicolon区切り。複数ID可）
- SupportTags
- StandaloneRecognition / ActorSeparation / SpatialAssignment / CompositionRetention
- PlacementMode / Result / FailureModes / Notes / EvidenceImagePaths

提供planのLocalTestEvidence 16件を観察行へ移し、checkpoint等が不明なため
`ModelProfile=current_illustrious_test_profile`、`Checkpoint=unknown` と明記した。
数値や成功率は捏造せず、`Result=REPORTED` として原文観察をNotesに保持する。
Phase 1のanal fisting + vaginal object insertion組合せ報告を、複数SpecialIDsの1行として追加した。

観察loaderはSpecialID存在性を検証するが、static profileを変更しない。

## Loader

```python
root = Path("C:/Codex/DanbooruTagTool")
knowledge = TagKnowledgeCore.load(root)
store = knowledge.load_generation_profile_store(root)

status = store.profiles["1117"].PromotionStatus
effective = store.effective_profile("192")
observations = store.observations
```

各CSVは列名・順序を固定し、不正boolean、重複ID、未知family rule、ID/Tag drift、
未知Specialを参照する観察を拒否する。返却mappingとdataclassはread-only。
sidecarが存在しない場合も従来のSpecial検索・保存・統計・exportは変わらない。

## Prompt identityと自動展開禁止

PromptSessionは元 `SpecialTag.term` だけをexportする。
Aliasのchosen canonicalは統計identityとして別に扱い、Prompt表記へ強制置換しない。
Semantic、PROVISIONAL、REVIEW_REQUIREDも手動選択・保存・export可能。

v2 metadataはsearch ranking、statistics count、candidate aggregationを変更しない。
このPhaseではsupport/ExpansionHintを自動注入するコードを追加しない。
内容カテゴリによるfilter、penalty、suppression、censorship fieldは設けない。

## 再生成

`tools/build_generation_profile_v2.py` は正本、promotion plan、family監査25件、分類修正177件、
明示構造override 240件、APPROVED_STATIC監査1,352件のID/Tagと件数を照合して3つのCSVを
再生成する。正本へは書き込まない。
