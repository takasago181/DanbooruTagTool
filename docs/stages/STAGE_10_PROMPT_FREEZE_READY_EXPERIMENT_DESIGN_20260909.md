# Stage10 PROMPT — freeze-ready experiment design

最終更新: 2026-09-09  
Owner: PROMPT / Issue #5  
Status: **PRE-FREEZE DESIGN / NOT STAGE10 EXECUTION AUTHORIZATION**

## 1. Purpose

#32辞書freeze後、PROMPT側の設計検討をやり直さず、残るID/evaluator/routingだけを差し込んでStage10準備を完了できる状態まで実験契約を詰める。

この文書は以下を**確定しない**。

- final representative Special IDs
- final Tagger/evaluator allocation
- production `AUTO / REVIEW` thresholds
- production Prompt rules
- Stage10 production A/B start

Current project order is:

`dictionary/data freeze -> Issue #42 product-purpose improvement pass -> READY_FOR_STAGE10_EVALUATION -> Stage10 production A/B`

したがって「freeze-ready」は「freeze直後に実験設計を再構築しなくてよい」という意味であり、#42を飛ばして実画像生成を開始する意味ではない。

Machine-readable companion:
`docs/testing/ISSUE30_PROMPT_EXPERIMENT_SPEC_PRE_FREEZE_20260909.json`

## 2. Authority / source set

Use without re-research unless a concrete evidence gap is found:

- `docs/stages/STAGE_10_PREP.md`
- `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md`
- `docs/testing/ISSUE30_SPECIAL_REPRESENTATIVE_ROUTING_DESIGN_20260908.md`
- `docs/stages/STAGE_10_PROMPT_HARD_TARGET_TEST_BACKLOG_20260909.md`
- `docs/stages/STAGE_10_PROMPT_HIGH_QUALITY_AUDIT_SCORECARD_20260909.md`
- `docs/prompt_knowledge/CLAIM_REGISTRY.md`
- `docs/prompt_knowledge/10_WAI17_LOCAL_FIRST_PROFILE.md`

HOLD/CANDIDATEをこの設計だけでFACTへ昇格しない。

## 3. Experiment invariant — one experiment = one question

各A/B pairは必ず:

1. 人間が一文で答えられるquestionを1つ持つ。
2. `independent_variable`を1つだけ持つ。
3. それ以外のPrompt要素・生成条件を固定する。
4. actual resolved Positive / Negative / actual runtime metadataを保存する。
5. A/B winnerだけでなく、何が改善/悪化したかをfailure/evaluation vectorで残す。

一度に `Frame + Viewpoint + Geometry + Visibility` を全部追加する比較は禁止。
supportを評価する場合は1 role / 1 deltaずつ追加する。

## 4. A/Bで固定する項目

同一pair内で固定:

- exact model checkpoint + SHA-256
- exact runtime/build
- seed
- resolution/aspect ratio
- sampler
- scheduler
- Steps
- CFG
- batch size
- VAE state
- LoRA state
- Hires.fix state
- ADetailer state
- Forge Couple / Regional state
- ControlNet state
- Negative Prompt（Negativeが独立変数の実験を除く）
- 宣言した独立変数以外のPositive Prompt component
- actor/count/identity
- target intent / semantic identity
- output metadata capture path

A/Bでruntime更新、model hash変更、seed変更、resolution変更が混ざった場合はそのpairを因果比較として扱わず `BLOCKED`。

## 5. Minimum sufficient Prompt

`minimum` = 最短文字列ではなく **minimum sufficient structure**。

Causal testの基本構造:

1. subject / count / identity
2. Special / ACT core
3. 必要なら SITE / OBJECT / ownership / relation
4. 必要な pose / geometry を1系統
5. 必要な frame / visibility を1系統
6. family適合のminimum quality
7. short target-safe Negative

Supportは以下の役割を分離:

- Meaning
- Geometry / Kinematic
- Visibility
- Resource parking / disambiguation
- Aesthetic
- Redundant

`Special core -> one justified support -> next justified support` の順で増やす。
すでに同じroleがあるのに同義語を足して厚くすることをdefault救済にしない。

## 6. Prompt bloat guard

Prompt肥大化をtoken数だけで判断しない。記録する:

- tag count
- tokenizer token count
- Special count
- support block count
- relation sentence count
- competing instruction count
- camera/pose role count
- aesthetic block count

Pairwise sequence:

- `MINIMUM -> + one justified support`
- `MINIMUM_SUFFICIENT -> + one non-essential block`

後者で改善がなく conflict / target loss / binding loss が増えるなら、追加blockを「supportだから必要」とは扱わない。

同一failure classに対してtargeted supportを試しても改善せず、support追加の方が競合を増やす場合は、無限追加せず `PROMPT_ONLY_LIMIT` reviewへ進む。

## 7. Failure decomposition

「出なかった」を一種類にしない。

| Failure | 問うこと |
|---|---|
| `TARGET_MISSING` | target Special自体が欠落/別概念化したか |
| `SITE_WRONG` | targetはあるが指定body-siteが違うか |
| `BINDING_LOST` | actor/target/ownership/作用先が混線したか |
| `OBJECT_DEGRADES` | object/device/appendage identityや役割が崩れたか |
| `GEOMETRY_FAILURE` | pose/contact/spatial relationが物理的に崩れたか |
| `VISIBILITY_FAILURE` | crop/occlusion/frameで成否判定できないか |
| `ATTRIBUTE_LEAKAGE` | actor間で属性/役割が漏れたか |
| `COUNT_FAILURE` | actor/object/Special相当要素の必要数が崩れたか |
| `OVERPROMPTED_CONFLICT` | support/quality/Negative等の競合で悪化したか |
| `PROMPT_ONLY_LIMIT` | targetedなPrompt修正を続ける合理性が薄いか |

内部診断では最低限:

- actor count
- Special target count
- ACT/target presence
- actor A / actor B role
- body-site
- object/appendage
- relation/ownership
- expected count
- visibility requirement

を別々に保持する。user-facing入力項目を同数に増やす意味ではない。

## 8. Representative case slots — IDs are intentionally unfilled

Freeze前に固定するのは**ケース型**で、Special IDではない。

### Required case slots

1. `SIMPLE_DIRECT`
   - genuine Special 1個
   - relation/bindingを要求しない
   - direct tag evaluatorが成立する可能性を確認するcontrol

2. `REL_ACTOR_TARGET`
   - actor A と target/actor B
   - ownership / action-target relationが必要
   - machine tag presenceだけでは原則不十分

3. `REL_BODY_SITE`
   - specific body-site correctnessが成否に必要
   - target presenceとsite correctnessを分離

4. `COMPOSITE_MULTI_SPECIAL`
   - Special A + B
   - `A_ONLY`, `B_ONLY`を先に確認
   - ABで片方落ちをaverageで隠さない

5. `COMPOSITE_OBJECT_BINDING`
   - actor + object/device/appendage
   - count / ownership / geometryのいずれかが必要

6. `RARE_DIRECT`
   - rare/niche Special direct realization
   - evaluator vocabulary absenceをPrompt FAILへ変換しない

7. `RARE_RELATIONAL`
   - rare/niche + relation/binding
   - human reviewを基本laneとする

8. `VISIBILITY_DEPENDENT`
   - Special identity固定
   - visibility support ON/OFFだけを比較

### Conditional slots

9. `ALIAS_SURFACE_IF_ELIGIBLE`
   - freeze後にcanonical + approved Alias / evidence-backed alternate surfaceがあるケースのみ

10. `NEGATIVE_COLLISION_IF_ELIGIBLE`
   - intended unusual geometryとanatomy-sensitive Negativeが衝突し得るケースのみ

このslot構造は #37 / #30 の代表性要件を満たすが、件数・ID・family配分はfreeze後まで固定しない。

## 9. Core experiment templates

### E01 — Special only vs one Meaning/Site support
A: Special-centered minimum  
B: A + exactly one Meaning/Site support

Question:
「その1 supportはtarget成立を改善し、新しい競合を増やさないか」

### E02 — no support vs one Geometry/Visibility support
A: no target-specific Geometry/Visibility support  
B: A + exactly one Geometry **or** Visibility support

Question:
「観測性/geometryは改善し、target/bindingを壊さないか」

### E03 — minimum vs sufficient
A: current minimum  
B: A + one justified support

Question:
「追加1 blockはminimum sufficientへ到達するため本当に必要か」

### E04 — sufficient vs oversupported
A: known minimum-sufficient candidate  
B: A + one non-essential block

Question:
「追加blockは利益なし/競合増加になっていないか」

### E05 — multi-Special retention
Prerequisite: `A_ONLY`, `B_ONLY` evidence  
A: A_ONLY  
B: AB minimal

Question:
「B追加時にAを保持し、両者のbindingも壊さないか」

ABが失敗してもA_ONLY/B_ONLYが成功なら、単純なrecognition failureとは分類しない。

### E06 — canonical vs approved model-facing surface
A: canonical  
B: approved Alias / evidence-backed alternate surface

Semantic identity以外を変えない。
Applicable cases only. Freeze前にsurfaceを選定しない。

### E07 — Negative one-delta
A: family-minimal Negative  
B: A + exactly one diagnosed Negative term

Question:
「artifact抑制の利益がtarget/geometry suppressionを上回るか」

### E08 — block order
A/Bは同一token集合。
変更するのはblock orderだけ。

Family evidenceに根拠があるときだけ実施。

### E09 — tag-only vs one short relation sentence
Family evidenceが許す場合のみ。
特にIllustrious exact-version / Anima候補。WAI/Noobへglobalに流用しない。

## 10. Model-family separation

同じcase type / scorecardを使っても、Prompt grammar/settingsを共通化しない。

- **WAI17**: current first lane; `LEAN_TAG_FIRST` candidate
- **NoobAI 1.1**: native caption order baseline; Special-before-General factを尊重
- **Illustrious**: exact version必須; WAI derivativeをbaseへ一般化しない
- **Anima**: tags / hybridを分離; relation sentenceやappearance anchorはfamily-specific test

Cross-family comparisonを行う場合:
- `CONTROLLED_SAME_SETTINGS`
- `FAMILY_OPTIMAL_BASELINE`

を別実験として扱い、結論を混ぜない。

## 11. WAI Illustrious v17 initial experiment profile

Profile ID: `WAI17_LOCAL_FIRST_20260909`  
Status: **CANDIDATE / STAGE10_REQUIRED**, not production fact.

Verified local checkpoint:
- `sd\waiIllustriousSDXL_v170.safetensors`
- SHA-256: `f116b0c78ff441467b0cdc8f1936e1ed18ea31e9997c7b132b1b8db533f0bd04`

Initial causal candidate:
- Forge Neo exact runtime — capture actual build at execution
- Euler a
- Steps 25
- CFG 6
- batch 1
- 1024x1024: causal square
- 1024x1344: portrait stress, separate condition
- seed fixed within A/B
- Seed 5072 may be continuity candidate, not production default
- external VAE OFF
- LoRA OFF
- Hires OFF first semantic pass
- ADetailer OFF
- Forge Couple / Regional OFF
- ControlNet OFF

Schedulerは現在のPrompt optimumとして固定せず、実行時actual runtime valueを記録してpair内で固定する。

Initial order:
1. minimal recognition / traceability control
2. E01 Meaning/Site support
3. E02 Geometry/Visibility support
4. E05 multi-Special only after single results
5. E06 surface when eligible
6. E07 Negative
7. E03/E04 minimum-sufficient / bloat
8. repeated structural failure -> Prompt-only ceiling review
9. assisted-control / Hires are separate lanes after Prompt-only evidence

## 12. Human REVIEW conditions

以下はmachine evaluatorのlow scoreだけでFAILにしない。

- evaluator vocabulary absent
- Alias only / canonical only mismatch
- target too rare for validated coverage
- components detected but target relation not expressed
- actor-target relation not represented by evaluator
- body-site binding not represented
- count ambiguous
- target cropped or occluded
- confidence near calibrated boundary
- evaluator disagreement
- human evaluator disagreement
- multiple-Special partial retention
- target present but wrong/ambiguous binding
- intended unusual geometryとartifactをautomaticに分離できない

Human reviewerには「どちらが綺麗？」ではなく、ケースに必要な質問だけ出す。

例:
- target Aは存在するか
- target Bは存在するか
- actor/target ownershipは正しいか
- body-siteは正しいか
- countは正しいか
- target領域は判定可能に見えるか
- geometryは意図を保ったまま成立しているか
- targetを保った上でfinished qualityはどちらが高いか

## 13. BLOCKED conditions

REVIEWとBLOCKEDを混ぜない。

`BLOCKED`:
- actual resolved Promptなし
- actual Negativeなし
- checkpoint hashなし/不一致
- silent runtime update
- seed/settings欠損
- required PNG/sidecar metadata欠損
- execution時点でfinal caseがfreeze済みdataへ紐付いていない
- production execution要求時にIssue #42が`READY_FOR_STAGE10_EVALUATION`でない

## 14. #30 machine-readable handoff

Companion JSONは#30側がgeneration runnerへ渡す前段のcontract。

必須概念:
- `format_version`
- gate state
- profile
- fixed controls
- case slot
- experiment template
- one human question
- independent variable
- actual-resolved metadata requirements
- evaluator capability class
- REVIEW/BLOCKED policy
- failure taxonomy
- post-freeze placeholders

#30は現時点で:
- schema/field mapping
- runner adapter feasibility
- metadata capture compatibility
- REVIEW/BLOCKED routing representation

を検討できる。

現時点でしてはいけない:
- final Special ID埋め
- production threshold決定
- production A/B実行
- WAI candidate profileをproduction optimumと扱う

## 15. What remains to fill after freeze

- final Special/canonical/Layer IDs per case
- eligible Alias/model-facing surfaces
- representative case count/family allocation
- WD14 / Kagami-24k / CL Tagger v2 coverage return
- evaluator responsibility per case
- AUTO / REVIEW production policy
- threshold if any
- rule-promotion seed count
- #42 resultによるPrompt pruning/conflict/product-purpose corrections

## 16. KNOWLEDGE return questions

New pre-freeze external research blocker: **none identified**.

Existing required post-freeze KNOWLEDGE return:
1. finalized Special corpus vs WD14 / Kagami-24k / CL Tagger v2 coverage comparison
2. Core / Extended / Alias / Semantic別coverage
3. post-count band coverage
4. raw Alias vs canonical-target coverage
5. representative-image evaluator disagreement where available

Additional source research is requested only if:
- exact target/model/version used by a case is not covered by existing Claim/hand-off evidence
- upstream model/runtime guidance materially changed before execution
- a proposed evaluator capability is being promoted beyond evidence already held

Noob camera tuning, canonical/Alias response, Negative collision, density, visibility side effects等は現時点では「追加web調査」ではなくcontrolled image testのHOLDとして維持する。

## 17. Current verdict

PROMPT-side design status:
**FREEZE_READY_DESIGN_DRAFT**

Meaning:
- experiment questions, fixed controls, case classes, failure taxonomy, WAI17 initial profile, #30 input shape, REVIEW/BLOCKED semantics are ready.
- final data/evaluator/threshold/production rules remain intentionally blank.
- no image has been generated by this work.
- Stage10 production A/B remains not started.
