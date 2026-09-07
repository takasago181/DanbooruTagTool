# Special2788 Generation Family Structural Audit v1

## 結論

現行v2の **Promotion境界 / Alias identity / StaticとModel Observationの分離は維持**する。
一方、25 Family Ruleの `DefaultNeeds*` と `DefaultCompositionRole` は **productionの物理要件としては不承認**。
Family内が不均質で、family単位のtrue/false継承が過剰な構造推測を生むため。

### 監査範囲
- `APPROVED_STATIC`: **1,352 / 1,352件を横断監査**
- 現行Family Rule: **25 / 25件を監査**
- 高確信度のtag-level修正: **175件**
  - Family変更: **151件**
  - Role変更: **160件**
  - PromptUseMode変更: **116件**
- 明示的なtag-level構造overrideを付ける候補: **240件**
- 残り1,177件: 現family/role/modeを暫定の**descriptive metadata**として保持。自動補助・物理要件推定には使わない。

## 現行Family Ruleで確認した問題
現行25 ruleのtrue default数:
- NeedsActor: 9
- NeedsBodypart: 11
- NeedsImplement: 3
- NeedsPose: 6
- NeedsCamera: 6
- NeedsSpatialAssignment: 14

問題はtrueの数ではなく、**同じFamily内に現在進行の行為・事後文脈・物体・身体状態・meme等が混在していること**。
例:
- `after sex` が ACTION_INTERACTION
- `after fingering` が INSERTION_STRUCTURED
- `clitoris peek` / `panty peek` 等が FLUID_STATE_ACTION
- `big belly` が RELATION_ROLE_CONTEXT
- `bdsm` / `sex slave` / `dominatrix` が RESTRAINT_ACTION
- `piledriver (sex)` が POSE_COMPOSITIONなのにPromptUseMode=DIRECT

この状態でFamily defaultを継承すると、タグの意味よりもFamily誤分類の影響が大きくなる。

## v2.1方針
### 1. Familyは分類・表示用
`GenerationFamily` / `GenerationRole` は、検索・整理・説明のためのdescriptive metadataとして維持。
**Family membershipだけでactor/bodypart/implement/pose/camera/spatialを確定しない。**

### 2. Family default requirementsを tri-state にする
`generation_family_rules.csv` の `DefaultNeeds*` / `DefaultCompositionRole` は空欄を許可する。
空欄 = `UNKNOWN / NOT ASSERTED`。
このv1監査では25 familyすべて、物理要件defaultは空欄にする。

`false` と `unknown` を混同しない。
- false = その要件が不要と明示的に分かる
- blank/None = familyだけでは判断しない

### 3. 物理構造はtag-level overrideだけで昇格
高確信度の240件だけ、既存override列へ明示的に入れる。
例:
- MULTI_ACTOR_INTERACTION: `ACTOR_SEPARATION_REQUIRED`, Actor=true, Spatial=true
- CAMERA_INTERNAL_VIEW: Camera=true, CompositionRole=camera
- POSE_COMPOSITION: Pose=true / camera系だけPose=false, Camera=true
- MACHINE_STRUCTURED: Actor=true, Implement=true, Spatial=true, CompositionRole=scene
- INSERTION_STRUCTURED: Actor=true, Bodypart=true。multiple/double/tripleのみSpatial=true
- SELF_ACTION: Actor=true + `SELF_ACTOR_ROLE`
- DIRECT_COMPOSITE: Spatial=true
- 固定拘束設備: `COMPOSITION_OWNER_CANDIDATE`

**Actor=trueは「別人物を追加する」の意味ではない。**
そのSpecialの物理構造にacting/participating roleがある、というinspection metadata。
別人物の分離は `ACTOR_SEPARATION_REQUIRED` と完全に別に扱う。

### 4. 自動Expansionは禁止のまま
`AllowsAutomaticExpansion = false` は維持。
Needs/overrideは「support tagを足す命令」ではない。
Stage 7 UI/Prompt Composerへ接続する前に、explicit overrideだけを参照する。

## Promotion境界への影響
なし。
- Alias 778
- Semantic 336
- audit-only 309
- correction metadata
- model observations
は今回変更対象外。

元Special2788、canonical_target、post_count、Prompt identityも変更しない。

## Stage判定
現行v2コードを破棄する必要はない。
**v2.1でFamily requirement inheritanceを無効化し、175 correction + 240 explicit overrideを適用して回帰が通った後にStage 6 FINAL判定**する。
