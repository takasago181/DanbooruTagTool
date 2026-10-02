# 05 — Hard / Niche Adult Generation

## 範囲

成人・合意下のBDSM/sexual activity、または明確な成人ファンタジーの生成監査知識。

ここでは「性癖ジャンル名」でなく、**生成上必要な能力**へ分解する。

重要: 2026-09-17 の棚卸しで、**canonical意味 / 人間のシーン組み立て順 / Browse入口 / model-specific Prompt順 / 生成評価・失敗診断**を別レイヤーとして扱うことを明示した。

最新のscene-planning synthesis:
`research/BATCH_N_SCENE_INTENT_DISCOVERY_WORKFLOW_20260917.md`

## Structural classes

- `UNARY_OBJECT_OR_STATE`
- `BODY_SITE_STATE`
- `SIMPLE_RELATION`
- `BINDING_RELATION`
- `RESTRAINT_TOPOLOGY`
- `DEVICE_RELATION`
- `MULTI_PENETRATION_OR_COUNT`
- `NONHUMAN_APPENDAGE_RELATION`
- `ANATOMY_CHANGING`
- `COMPOSITE_HARD`

## Risk dimensions

- exposure / rarity
- binding
- visibility
- geometry
- count
- Negative collision
- style/context leak
- evaluator blindness
- LoRA confound
- postprocess rescue

## Scene planning layer — 2026-09-17 synthesis

既存のhard/niche各領域を横断すると、画像を組み立てる時に確認する意味軸はほぼ共通化できる。

1. **subjects** — 人数 / identity / 必要な識別特徴
2. **core action/state** — 何をしている・どんな状態か
3. **relation/role/ownership** — 誰が誰に、誰の部位・道具・appendageか
4. **target/body-site** — 対象部位
5. **geometry/position/topology** — 体位・相対配置・接続関係
6. **implement/device/appendage** — 何を使うか
7. **state/timing/count/source-destination** — 個数・同時性・前中後・source/destination
8. **visibility/framing** — 必要な関係が観察できるか
9. **appearance/clothing/exposure/expression** — 人物・外見の調整
10. **setting/background/light/style** — 場面・仕上げ

これは**分析・計画用のsemantic skeleton**であり、必須タグ列・canonical定義・model共通Prompt文法ではない。

### Default human planning sequence

人間側の初期仮説としては:

`subjects -> action/state -> relation/role -> body-site -> geometry/position -> implement -> state/count/timing -> visibility -> appearance -> setting/style`

を使える。

ただしこれは固定wizardではない。ユーザーが部位・道具・体位・テーマから入りたい場合は、その強いintentを入口として保持し、**不足している意味軸を次に見せる**方が自然という研究仮説を持つ。

### Browse axisとPrompt順を混ぜない

- Danbooru側でも explicit content は body parts / sexual actions / sexual positions / sexual themes / sexual objects のように別の発見軸を持つ。
- e621 tag groupは1タグの複数group所属を許し、発見しやすさを目的としている。e621はDanbooru canonical authorityではないが、multi-axis browseのsecondary evidenceになる。
- NoobAI XL 1.1 EPS は author-defined caption order `count -> character -> series -> artist -> special -> general -> other` を持つ。
- Animaは別のgroupingを持ち、general section内は任意順、tag + natural language混在も許す。

したがって、**人間の操作順やBrowse順をそのままmodel共通Prompt順として出力しない。**

## 領域別の現在知識

### 挿入・body-site系
成功条件を分離:
`site / action / implement / count / ownership`

object存在だけで成功判定しない。

原本: `research/HARD_FETISH_ANAL_INSERTION_20260909.md`

Scene completionの典型:
`site -> action/state -> implement -> actor/target -> count/timing -> visibility`

### BDSM / restraint
拘束はrope/cuff存在ではなく、必要に応じて**接続topology**を見る。

`device / body-site / topology / pose / role`

原本: `research/HARD_FETISH_BDSM_RESTRAINT_20260909.md`

Scene completionの典型:
`theme/target -> role -> device -> body-site -> topology/pose -> visibility`

### machine / device
machineが画面にあるだけでは不足。

`device type / target / body-site / functional contact`

原本: `research/HARD_FETISH_MACHINE_DEVICE_20260909.md`

Scene completionの典型:
`device -> target -> body-site -> functional relation -> geometry -> count/visibility`

### tentacle / nonhuman appendage
`source / ownership / appendage role / target / relation / count`

hair/tail/clothing/external actor/machine appendageとの混線を疑う。

原本: `research/HARD_FETISH_TENTACLE_FANTASY_20260909.md`

Scene completionの典型:
`source/ownership -> target -> body-site -> relation -> appendage role -> count/density -> visibility`

### fluid / excretion
`material / source / destination / state / quantity`

fluid存在だけでrelation成功としない。

原本: `research/HARD_FETISH_FLUID_EXCRETION_20260909.md`

Scene completionの典型:
`material -> source -> destination -> state/timing -> quantity -> actor/target -> visibility`

### rare / anatomy-changing
- one-seed failureでモデル未学習と断定しない
- common priorへのcollapseを疑う
- broad/frequent constituentはA/B候補
- generic anatomy/count Negativeは高リスク

原本: `research/HARD_FETISH_RARE_EXTREME_20260909.md`

## 複合hard case

必ずA_ONLY/B_ONLYを先に確認し、ABで初めて崩れるならcomposition/binding問題を優先。

原本: `research/HARD_FETISH_COMPOSITE_FAILURE_MATRIX_20260909.md`

## モデル差

WAI17 / NoobAI / Animaを同一扱いしない。

原本: `research/HARD_FETISH_MODEL_FAMILY_MATRIX_20260909.md`

特にscene planning順とPrompt serialization順は分離する。

- NoobAI: exact author caption structureあり
- Anima:別grouping + general内任意順 + mixed tag/NL
- Illustrious系: critical composition tagの過剰stackはconflict候補

## 重要な評価原則

- presence != relation
- exact body-site/countはfirst-class predicate
- rare tagがTagger vocabulary外ならmachine failure扱いしない
- LoRA-assisted / Control-assisted / postprocess-rescuedは別レーン
- anatomy-changing caseはNegative ON/OFFを分離
- human planning order != browse taxonomy != model Prompt order
- visibility/cameraは通常、意味そのものではなく観察可能性を支えるrole

## 2026-09-17 open usability questions

以下はまだcurrent Claimとして「最適」と確定していない。

- `SW-01`: default human selection orderが現行WPFで実際に最も少ない戻り操作になるか
- `SW-02`: body-site/device/theme等の入口後に、次にどのfacetを優先すると最も探しやすいか
- `SW-03`: hard/niche以外のordinary adult scenesでも同じsemantic skeletonで十分か
- `SW-04`: General/Specialを将来UI統合する場合、#64 + #76既存metadataだけでscene-oriented discoveryを表現できるか

これらはproduct/UX検証を要する。Web情報だけで「最適」と断定しない。

## 出典原本

- `research/HARD_FETISH_SOURCES_20260909.md`
- `research/BATCH_N_SCENE_INTENT_DISCOVERY_WORKFLOW_20260917.md`

---

## Adult-generation mastery layer — 2026-10-02

The adult knowledge lane now has a practical learning architecture, not only a hard-tag audit.

Core flow:

`adult validity -> subjects -> relation/role -> target/body-site -> geometry/topology -> state/count/material -> visibility -> presentation -> model serialization -> evaluation`

### Adult validity
Generation optimization is limited to clearly adult, consensual/adult-fantasy scope. Ambiguous age/consent is invalid before Prompt tuning.

### Model intent boundary
Content-rating/safety defaults are model-specific:
- NoobAI author defaults are SFW-oriented;
- WAI exposes explicit rating surfaces;
- Anima has its own safety-tag conventions.

Do not use a SFW content-filter Negative unchanged for an adult-target capability test and then call the target unsupported.

### Adult failure axes
Keep separate:
- count
- identity
- role
- body-site ownership
- contact/relation
- geometry/topology
- visibility
- state/timing/material
- anatomy collateral
- censor/style context leakage
- Negative collision
- LoRA contamination
- assisted/postprocess rescue

### Relation-focused learning
For difficult multi-subject scenes:
- stable subject IDs/names are a useful experimental aid;
- keep relation descriptions focused on who is where and how they relate;
- unrelated style/background/clothing prose can be serialized separately;
- helper LLM/VLM captions remain editable suggestions, not semantic authority.

### Censor/context prior
If censor/watermark-like artifacts persist:
- test whether an artist/concept surface imports them;
- do not assume stronger Negative is the only solution;
- treat as possible learned context/style prior.

Full research:
`../research/BATCH_Y_ADULT_GENERATION_STRUCTURAL_MASTERY_20261002.md`.

---

## Hard-domain continuity guarantee — 2026-10-02

The current adult-generation expansion does not replace the earlier hard/niche research.

The following remain first-class knowledge domains and must continue to be researched independently where relevant:

- body-site-specific states and relations
- insertion/contact relation families
- exact count / simultaneity
- restraint topology
- machine/device relation
- nonhuman-appendage relation
- material/fluid source-destination-state
- unusual/anatomy-changing cases
- composite hard scenes
- model-specific Negative collisions
- LoRA/context leakage
- evaluator blindness on rare relation concepts
- Prompt-only vs assisted-control vs postprocess success

Do not collapse these into a single generic `adult` or `explicit` category.

The purpose of the adult mastery layer is to connect these existing specialized domains into a practical generation/diagnosis workflow, while keeping their detailed semantics intact.

Authority precedence:
1. exact Claim Registry verdict
2. this catalog's structural classes
3. focused hard/niche research files
4. current adult mastery batch
5. cross-cutting summaries

Focused historical/current files remain valid:
- `HARD_FETISH_ANAL_INSERTION_20260909.md`
- `HARD_FETISH_BDSM_RESTRAINT_20260909.md`
- `HARD_FETISH_MACHINE_DEVICE_20260909.md`
- `HARD_FETISH_TENTACLE_FANTASY_20260909.md`
- `HARD_FETISH_FLUID_EXCRETION_20260909.md`
- `HARD_FETISH_RARE_EXTREME_20260909.md`
- `HARD_FETISH_COMPOSITE_FAILURE_MATRIX_20260909.md`
- `BATCH_Y_ADULT_GENERATION_STRUCTURAL_MASTERY_20261002.md`

Future research should deepen these domains rather than replacing them with safer but less useful generalities.

---

## Compositional evaluation/control upgrade — 2026-10-02

Recent compositional T2I research supports the current hard-domain architecture:

- score count separately from presence;
- score attribute/body-site ownership separately;
- score spatial/non-spatial relation separately;
- treat 3+ subjects as a distinct stress class;
- use atomic yes/no predicates instead of one holistic similarity verdict.

New assisted-control axes:
- global LoRA
- spatially masked LoRA
- denoising-scheduled LoRA
- masked + scheduled LoRA
- regional/control
- postprocess/inpaint

ComfyUI supports LoRA/model masking and scheduling natively.
FreeFuse is retained as a research lead for spatial multi-LoRA routing; current public support does not authorize assuming Anima compatibility.

Research:
`../research/BATCH_Z_COMPOSITIONAL_EVAL_AND_CONTROL_20261002.md`.

---

## Multi-subject LoRA dataset design — 2026-10-02

Inference-time binding problems can originate in the training distribution itself.

Current community hypotheses worth controlled testing:
- isolated solo images do not teach coexistence automatically;
- joint/interaction images can reduce feature bleed;
- stitched composites may teach rigid spatial separation;
- uncaptioned constant backgrounds/context can become entangled with identity;
- solo and joint subsets need enough effective sampling balance that joint states are not drowned out;
- viewpoint-count diversity alone does not guarantee generalization.

For hard relation training, vary role/position/context independently where possible.

Research:
`../research/BATCH_AA_MULTI_SUBJECT_LORA_DATASET_DESIGN_20261002.md`.

---

## Negative prior / toolchain escalation — 2026-10-02

Do not collapse all unwanted-content failures into “Negative too weak”.

Separate:
- ordinary Negative response;
- positive artist/concept prior;
- LoRA context contamination;
- NegPiP-assisted suppression;
- edit/postprocess cleanup.

Current Anima/Forge research notes:
- persistent censor/watermark-like artifacts can be tied to positive learned priors;
- the archived Haoming02 Forge NegPiP path documents Anima support;
- NegPiP success is assisted conditioning, not ordinary Negative success;
- TrainTrain currently supports Anima training through Forge Neo, with tool-specific architecture constraints.

Research:
`../research/BATCH_AB_NEGATIVE_PRIOR_AND_TRAINING_TOOLCHAIN_20261002.md`.

---

## Pose/depth/region/inpaint escalation — 2026-10-02

Use the failed predicate to choose assistance:

- skeletal posture -> pose
- front/back/overlap -> depth
- contour/layout -> lineart/edge
- identity/resource locality -> region/mask
- local residual defect -> inpaint

Pose control is not semantic relation control.
A perfect skeleton can still have wrong identity, ownership, contact or target-site binding.

Always keep:
`Prompt-only -> control-assisted -> locally edited`
as separate evidence states.

Research:
`../research/BATCH_AD_POSE_DEPTH_REGION_INPAINT_ESCALATION_20261002.md`.

---

## Count/camera/visibility limits — 2026-10-02

Hard-scene evaluation must keep separate:
- concept presence
- exact count
- ownership
- relation
- camera/viewpoint
- visibility/occlusion

Research shows exact counting remains difficult and simple prompt refinement is not a reliable cure.

Precise camera control is also a distinct problem; text camera phrases are often coarse.

Do not classify a hidden/off-frame relation as semantic concept failure.

Research:
`../research/BATCH_AE_COUNT_CAMERA_VISIBILITY_LIMITS_20261002.md`.

---

## Anatomy/occlusion/local repair — 2026-10-02

Keep two verdicts:
- relation/scene semantics
- local anatomy quality

A correct relation with a malformed hand is not the same failure as a clean hand attached to the wrong subject/relation.

Occlusion/depth is also separate from pose:
- correct skeleton can still be layered incorrectly;
- a required relation can exist but be hidden.

Local reconstruction is appropriate only after global semantics are acceptable.

Research:
`../research/BATCH_AF_ANATOMY_OCCLUSION_LOCAL_REPAIR_20261002.md`.

---

## Anima interaction stress — 2026-10-02

Community evidence reinforces:
- identities can work alone but fail as a pair;
- strong series/concept priors can leak across subjects;
- 3+ subjects with distinct resources/positions are a separate stress class;
- correct subject presence does not prove correct role/body-site assignment.

Use A_ONLY/B_ONLY/AB before declaring concept ignorance.
Escalate to regional/mask control when pairwise Prompt cleanup cannot stabilize ownership.

Research:
`../research/BATCH_AG_ANIMA_RELATION_STRESS_COMMUNITY_20261002.md`.

---

## Illustrious/Noob multi-subject practice — 2026-10-02

Community signals:
- one global prompt can mix subject traits;
- 3+ subjects are a distinct stress class;
- regional/mask/inpaint workflows are common escalation paths;
- pose fidelity and identity fidelity can fail independently.

Noob secondary sources may contain outdated/conflicting V-Pred settings.
Exact current author guidance wins as the first baseline.

Research:
`../research/BATCH_AH_ILL_NOOB_MULTI_SUBJECT_AND_SOURCE_CONFLICT_20261002.md`.

---

## Practical learning curriculum — 2026-10-02

Adult-generation study should progress from:
- one adult subject
- two distinct adults
- simple contact/interaction
- relation-heavy scene
- multi-subject/multi-LoRA
- assisted control
- finishing

Use structure-only reference descriptions and stable subject IDs to study binding.

Keep failures as evidence.
Do not advance based on one lucky seed.

Prompt-only, global-LoRA, regional/control and locally edited success remain separate skill/evidence levels.

Research:
`../research/BATCH_AP_ADULT_PRACTICAL_LEARNING_METHOD_20261002.md`.

---

## Regional interaction tradeoff — 2026-10-02

Regional control has two competing goals:
- separate identities/attributes
- preserve physical interaction/global coherence

For current Anima regional tools, stronger isolation can reduce cross-region awareness.

Do not treat Regional as a monotonic “more separation is better” control.

Current Forge Neo Regional Prompter supports Anima regional text conditioning but not Region LoRA.

Research:
`../research/BATCH_AQ_REGIONAL_LEARNING_AND_REPRODUCIBILITY_20261002.md`.

---

## Staged conditioning for hard scenes — 2026-10-02

A valid advanced experiment is:
- establish relation/geometry with minimal early conditioning;
- introduce style/quality/adapter pressure later;
- compare against constant conditioning.

Do not use scheduling to mask incorrect count, role, body-site or geometry.

Scheduled success remains a separate assisted runtime configuration.

Research:
`../research/BATCH_AR_STAGED_CONDITIONING_AND_LEARNING_20261002.md`.

---

## Teaching readiness model — 2026-10-02

Adult-generation instruction now uses three result levels:
- possibility
- reliability
- salvageability

A teacher should diagnose:
count / identity / role / body-site ownership / geometry / visibility / local anatomy / style/identity preservation
before choosing an intervention.

Canonical curriculum:
`../current/ADULT_IMAGE_GENERATION_TEACHING_CURRICULUM.md`.



---

## Teacher-ready diagnostic escalation

成人向け生成の実用診断は、完成Promptの収集ではなく次の順で行う。

`reproducibility -> failure label -> minimal prompt -> 4-seed test -> one-variable A/B -> assisted control`

Current Japanese operational artifact:
`../current/ADULT_IMAGE_GENERATION_DECISION_TREE.md`

Key project heuristic:
- concept-alone success
- two concise prompt representations tested
- same primary structural failure in at least 3/4 fixed seeds

なら、Promptの言い換えを続けるよりfailure-specific controlへ進む。

Model-specific caution:
- NoobAI EPS official example is safety-biased (`safe` positive / `nsfw` Negative), so adult capability tests must record/alter that state explicitly.
- Anima supports tags/NL/safety tags but official material does not establish hard adult relation reliability.

Research:
`../research/BATCH_AW_ADULT_DIAGNOSTIC_ESCALATION_AND_MODEL_GAPS_20261002.md`
