# Special2788 Production Profile Promotion Decision v1

## 結論
Deep Audit v1をそのまま2,788件すべてproductionへ流し込まない。
高確信度の情報だけを昇格し、モデル依存・曖昧・auto-gloss由来は別レイヤーに残す。

- 全件: 2,788
- productionへ安全に昇格可能: 2479 (88.9%)
- provisional: 295
- review required: 14

### Promotion内訳
- APPROVED_STATIC: 1352
- APPROVED_IDENTITY_ONLY: 778
- APPROVED_SEMANTIC_ROLE: 336
- PROVISIONAL: 294
- REVIEW_REQUIRED: 14
- APPROVED_CORRECTION_METADATA: 13
- PROVISIONAL_CORRECTION: 1

## 1. production構造

### A. Source of Truth — 変更禁止
`illustrious_tag_knowledge_base_2788.csv`

Tag / 日本語 / Layer / 元カテゴリ / canonical_target / post_count はそのまま保持。
Deep Auditを理由に原本を上書きしない。

### B. Static Generation Profile
`special2788_generation_profile.csv`

役割: モデル非依存の意味・構造・Prompt利用法。

保持する推奨列:
- SpecialID
- Tag
- ApprovalStatus
- MeaningStatus
- MeaningConfidence
- SourceGlossQuality
- GenerationFamily
- GenerationRole
- PromptUseMode
- FamilyRuleId
- CompositionRoleOverride
- ActorRequirementOverride
- BodypartRequirementOverride
- ImplementRequirementOverride
- PoseRequirementOverride
- CameraRequirementOverride
- SpatialAssignmentOverride
- ShapeConflictGroup
- SpecialFlags
- RecommendedHandling
- EvidenceClass
- EvidenceRefs

重要: Override列は空欄=family default継承。2,788件へ同じNeeds値を複製しない。

### C. Generation Family Rules
`generation_family_rules.csv`

役割: familyごとのdefault rule。

例:
- INSERTION_STRUCTURED
- MULTI_ACTOR_INTERACTION
- MACHINE_STRUCTURED
- RESTRAINT_IMPLEMENT
- POSE_COMPOSITION
- CAMERA_INTERNAL_VIEW
- NONHUMAN_INTERACTION
- CONTEXT_MODIFIER

保持する列:
- FamilyRuleId
- GenerationFamily
- DefaultPromptUseMode
- DefaultNeedsActor
- DefaultNeedsBodypart
- DefaultNeedsImplement
- DefaultNeedsPose
- DefaultNeedsCamera
- DefaultNeedsSpatialAssignment
- DefaultCompositionRole
- Notes

### D. Model Observation — Staticと分離
`generation_model_observations.csv`

ここにのみ保存するもの:
- ModelProfile / Checkpoint
- Seed / Steps / CFG / Size / Sampler / Scheduler
- TestType (SINGLE / COMBINATION / STRESS)
- SpecialIDs
- SupportTags
- StandaloneRecognition
- ActorSeparation
- SpatialAssignment
- CompositionRetention
- PlacementMode
- Result
- FailureModes
- Notes
- EvidenceImagePaths

`StandaloneVisuality`, `BodypartClarity`, `ActionClarity`, `ActorClarity`, `CoexistenceScore`, `ModelProfile`, `Confidence` はStatic Profileから外す。
特に `CoexistenceScore` はtag単体の固定値にしない。

## 2. GenerationClass S/A/B/Cは保存しない
S/A/B/Cは情報を潰しすぎるためproductionのSource of Truthにしない。
UIで必要なら `PromptUseMode` から派生表示する。

推奨PromptUseMode:
- DIRECT
- STRUCTURED
- SUPPORT
- REFERENCE_ONLY
- ALIAS_PRESERVE
- MODEL_DEPENDENT

## 3. Promotion Rule

### APPROVED_STATIC
高確信度のsource clear / official web verified。
GenerationFamily / Role / PromptUseMode等をproductionへ昇格。

### APPROVED_IDENTITY_ONLY
Alias。canonical_targetは統計・意味解決に使うが、Prompt identityは元Aliasを保持。

### APPROVED_SEMANTIC_ROLE
Semantic。support/search roleだけ昇格し、直接モデル認識は確定しない。

### APPROVED_CORRECTION_METADATA
高確信度で誤訳・誤分類を確認したもの。原本を直さずcorrected metadataとしてoverlayする。

### PROVISIONAL / PROVISIONAL_CORRECTION
UIの確定意味や自動Prompt展開に使わない。Deep Audit表示・警告のみ。

### REVIEW_REQUIRED
意味を勝手に補完しない。raw Special identityはそのまま利用可能。

## 4. Prompt Composerへの反映

自動追加は最小限にする。

1. Special Coreを最優先
2. Family Ruleで必要条件を確認
3. 欠けているactor/bodypart/implement/pose/cameraだけ補助候補を出す
4. 補助は自動追加せず、ユーザー選択
5. Composition Ownerは原則1つ
6. Multi-actorはActor Separationを別問題として扱う
7. Spatial Assignmentは組み合わせ側で扱う
8. Shape Conflict (tentacle/cable/pipe等) を警告候補にする
9. Conditional Rateはstable reinforcement、Raw Liftはrare derivativeの別ビュー
10. candidateを大量投入しない

## 5. 今回の実測をproduction意味へ混ぜない
`stationary restraints`, `sex machine`, `tentacle sex`, `cross-section`, `piledriver (sex)` 等の成功観察、
multi-actor融合、pose-vs-equipment競合などは Model Observation側へ移す。

## 6. Stage 6 Finalへの扱い
このPromotion設計を実装・回帰確認したら、Special2788生成知識の基盤はStage 6で十分と判断できる。
未精査309件をStage 6完了のブロッカーにはしない。raw Specialは失われず、provisionalとして安全に残るため。

Stage 6.5へ進む条件:
- source不変
- static / family / model observation分離
- promotion statusが読み込める
- provisionalが自動展開されない
- alias identity保持
- 既存pytest全green
