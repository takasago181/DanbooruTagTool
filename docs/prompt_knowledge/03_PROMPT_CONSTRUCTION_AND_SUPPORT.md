# 03 Prompt construction and support

Owner: PROMPT / Issue #5
Status: structured PROMPT knowledge summary. Not production specification.

## 目的

Promptを単なるcomma-separated tag列として扱わず、**何のためのblockか**を分けて組む。

hard imageでは、長さではなく役割・競合・binding・observabilityが重要。

## 内部slot architecture

難しいcaseは内部では最低限次へ分解して診断する。

- `ACT` — target act / Special core
- `SITE` — target body/site
- `OBJECT` — device/tool/appendage/object
- `ACTOR_A` / `ACTOR_B` —主体
- `RELATION` — 誰が誰にどう関係するか
- `POSE / GEOMETRY`
- `VISIBILITY`
- `QUALITY / FINISH`
- `NEGATIVE`

これはuser-facing input項目を増やすためではない。**内部では細かく、ユーザーには第一推奨を完成形で返す。**

## Support taxonomy

### 1. Meaning support
Specialの意味・対象・作用を明確にする補助。

用途:
- broad conceptのspecificity補助
- body-site / object identity補助

注意:
- semantic relationがあるだけでgeneration benefitは証明されない
- `CORE_SUPPORT + ADDITIVE`等の自動挿入効果はStage10で再検証

### 2. Geometry / Kinematic support
身体の向き、姿勢、接触方向、相対配置を成立させる補助。

注意:
- 同roleのpose/orientationを重ねると競合しやすい
- hard caseで無限追加しない

### 3. Visibility support
targetをframe内で観測可能にする補助。

例の役割:
- Frame
- Viewpoint
- crop/subject size
- target-region readability

注意:
- visibility向上はcomposition/pose/target fidelityへ副作用を持つ
- `full body`等を万能supportにしない

### 4. Resource parking / disambiguation
複数actor/object/roleの混線を減らすための構造補助。

用途:
- actor count
- identity separation
- ownership clarification
- competing conceptsの整理

### 5. Aesthetic support
lighting/style/background/mood/detail等、完成度を上げる補助。

原則:
- target成立問題より先に盛らない
- family-specific quality/metaと混同しない

### 6. Redundant decoration
target成立・観測・qualityに寄与せず、競合やPrompt densityだけ増やすもの。

原則:
- minimum sufficientの削減対象

## Hard production caseの組み立て優先順

PROMPT側の現在候補:

1. Special Core / intended concept
2. actor/count/identity/ownership
3. Frame
4. Viewpoint
5. Orientation / Geometry
6. Visibility
7. targeted Relation / Binding support
8. family-appropriate Quality/Meta
9. target-safe Negative
10. Aesthetic support
11. Optional variation / decoration

この順はuniversal model truthではなく、**構造監査の優先順**。
family-specific orderは `02_MODEL_FAMILY_PROFILES.md` を優先する。

## Minimum sufficient structure

良いPromptは「短いPrompt」ではない。

- targetに必要なblockは入れる
- 一つのblockに明確な役割を持たせる
- same-role supportを重複させない
- support追加で何を直すのか説明できる
- hardだからという理由だけで全部盛りしない

Prompt densityはtoken数だけでなく以下を見る。

- Special count
- support block count
- competing camera/pose count
- relation count
- aesthetic block count
- object/actor count

## 段階的support escalation

基本診断順:

`CORE only -> + one Meaning/Site -> + one Geometry/Visibility -> + one targeted Binding/Relation -> family finish`

一回に複数blockを変えない実験を優先。

hard-targetで失敗した時、最初にquality語を増やさない。

## Multiple Special

基本sequence:

`A_ONLY -> B_ONLY -> AB minimal -> AB + one targeted support`

必要ならorderを問うときだけBA。

記録:
- A retained?
- B retained?
- actor/target correct?
- site correct?
- visibility sufficient?
- geometry broken?

片方落ちをaverageで隠さない。

## Canonical / Alias / Semantic / model-facing surface

分離する。

- canonical = identity/semantic authority
- Alias = semantic relation
- Semantic candidate =検索/近接橋渡し
- model-facing surface = exact checkpointが実際に反応する文字列表現

`alias/implicationがある = model response equivalent` ではない。

Stage10では必要時に:
- canonical
- approved Alias
- evidence-backed alternate surface
をcontrolled A/Bする。

provenanceは常に保持する。

## Replacement slot workflow

ユーザーへPrompt設計を丸投げしない。

原則:
- 直接構成できる周辺structureはPROMPT側で完成させる
- 本当に必要な最小coreだけslot化
- 同一概念を複数slotへ無用分割しない
- Special2788候補はPROMPT側が探索
- 原則3候補程度 + 日本語 + ID/Layer/post_count等を可能な範囲で示す
- slot数削減のために意味・強度・specificityを弱めない

詳細:
`docs/stages/STAGE_10_PROMPT_REPLACEMENT_REFERENCE.md`

## 実験分離と実戦Promptを混ぜない

Experimental Isolation:
- causal questionのため余計なblockを削る

Stress/Production-quality candidate:
- 実画像として完成させるため必要なblockを保持

実験用の削りすぎを実戦の設計原則へしない。

## Stage10で再検証する古い仮定

- semantic supportが実生成でも自動的に有効
- current block orderがfamily最適
- canonical surfaceがmodel trigger最適
- visibility supportが透明な補助
- supportを増やせばhard caseが改善

詳細:
`docs/stages/STAGE_10_PROMPT_REVALIDATION_BACKLOG_20260909.md`
