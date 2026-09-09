# Hard Fetish Generation Knowledge — BDSM / Restraint Topology

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `DEEP_RESEARCH_V1 / evidence-reference`

## 1. Scope

対象は成人・合意下の BDSM / bondage / restraint / dominance-role 系の生成・監査知識。辞書には非合意概念も存在するが、本ファイルでは詳細な生成最適化対象にしない。

Representative project rows:
- `bdsm` Core / 87043
- `ball gag` Core / 13391
- `blindfold` Core / 30114
- `cuffs` Core / 44563
- `handcuffs` Core / 17555
- `spreader bar` Core / 1701
- `bondage` Core / 73216
- `bound` Core / 110985
- `bound arms` Core / 22580
- `bound legs` Core / 13475
- `bound wrists` Core / 29733
- `bound together` Core / 1836
- `box tie` Extended / 998
- `frogtie` Core / 5441
- `hogtie` Core / 1437
- `legs bound apart` Extended / 874
- `predicament bondage` Extended / 421
- `reverse prayer` Extended / 335
- `shibari` Core / 23873
- `shrimp tie` Extended / 82
- `strappado` Extended / 144
- `suspension` Core / 5870
- `breast bondage` Core / 4713
- `dominatrix` Core / 3124
- `femdom` Core / 21529

## 2. Core distinction: theme, device, topology, role

BDSM success must not be reduced to one `bdsm` confidence.

### Theme
Broad scene class such as BDSM/bondage.

### Device presence
Cuffs, rope, gag, spreader bar, clamp, leash etc.

### Body-site attachment
Which body part is actually restrained.

### Topology
How the restraints connect body parts to each other or to an anchor.

### Pose consequence
Some restraint concepts intrinsically imply a pose/geometry configuration.

### Role/dominance
Dominant/submissive role is conceptually separate from physical restraint topology.

An image can have rope, cuffs, and BDSM styling while failing the requested topology.

## 3. Restraint graph model

For difficult concepts, audit as a graph.

### Nodes
- left/right wrist
- left/right ankle
- elbows/knees/thighs/torso
- neck/collar
- fixed anchor/device
- actor controlling restraint if intrinsic

### Edges
- rope segment
- cuff connection
- chain/leash connection
- spreader bar attachment
- suspension line

### Constraints
- correct body parts connected
- correct relative positions
- restraint actually limits motion
- no unexplained free limb when the target requires it
- no extra/missing anchor that changes the concept

This graph is an audit abstraction, not a required runtime representation.

## 4. Main failure modes

### `DECORATIVE_ROPE_ONLY`
Rope appears on/around the body but does not physically create the requested restraint.

### `WRONG_LIMB_BINDING`
Requested wrists/arms/legs are not the parts actually bound.

### `TOPOLOGY_COLLAPSE`
Specific tie collapses to generic bondage/shibari.

### `POSE_WITHOUT_RESTRAINT`
The model copies the pose but omits/loosens the restraint mechanism.

### `RESTRAINT_WITHOUT_POSE`
The device is present but the geometry required by the specific tie is wrong.

### `LEFT_RIGHT_AMBIGUITY`
For asymmetric binding, side ownership is swapped or inconsistent.

### `SMALL_STRUCTURE_FAILURE`
Chains, connectors, buckles, cuffs or rope intersections become fused/incorrect.

### `ROLE_BLEED`
Dominance/submission appearance is produced while physical action/ownership is wrong.

### `OCCLUSION_BY_RESTRAINT`
Rope/device hides a body site needed to judge another Special.

### `ANATOMY_COLLATERAL`
Hard poses create joint/limb collapse; adding broad anatomy Negative may then suppress the intended unusual configuration.

## 5. Dedicated LoRA evidence and what it means

Niche restraint LoRA pages are useful practical evidence because they expose failure modes that persist even after concept specialization.

A particularly useful Illustrious practical example for a bound-from-behind concept reports that chain structure can still fail and recommends inpainting/post-generation correction. This supports two durable rules:

1. small connector/topology correctness is not guaranteed by a dedicated LoRA;
2. inpaint success must be marked `POSTPROCESS_RESCUE`, not base Prompt success.

Other BDSM LoRA reports indicate that reducing LoRA weight can improve anatomy in difficult poses. This supports treating adapter weight as a confound/intervention rather than a transparent concept-strength knob.

LoRA trigger bundles often contain both:
- the concept trigger;
- broad bondage words;
- pose/framing/support tags;
- style/quality tags.

Never infer that the whole bundle is the canonical definition or universally required support.

## 6. Role of camera / visibility

Restraint topology often needs a wider frame than a simple object close-up, but `full body` is not universally correct.

Potential conflict:
- tight crop improves rope/cuff detail but hides anchor/limb topology;
- wide shot shows topology but reduces small-device recognizability;
- rear view helps some ties but may hide front devices/role cues.

Therefore camera is a test variable tied to the audit question.

Suggested visibility questions:
- Are all required attachment points visible?
- Is the anchor visible when intrinsic?
- Can the judge distinguish generic rope decoration from actual restraint?

## 7. Same-role support conflicts

Illustrious family guidance warns against stacking conflicting critical composition tags. For restraint scenes this is particularly important because topology already imposes strong geometry.

Avoid assuming that more pose words monotonically help.

Preferred escalation:
1. target tie/restraint Special
2. one frame role
3. one viewpoint role
4. one targeted geometry clarification
5. one resource/ownership clarification

Remove/replace before adding a second tag in the same role.

## 8. Negative Prompt interaction

High-risk combinations include:
- reverse-prayer / strappado / suspension / frog-tie-like unusual limb configurations
- multi-limb binding
- bent/folded poses

Broad negatives such as `bad anatomy`, `extra limbs`, `malformed anatomy` may remove unwanted errors, but mechanism research shows negative concepts can actively suppress positive concepts.

Therefore exact-family controlled ON/OFF remains required.

## 9. Model-family notes

### WAI Illustrious v17
- exact author settings and minimal Negative should be baseline;
- author warns against excessive positive/negative stacks;
- Hires may repair limbs, so topology/anatomy must be judged pre-Hires as well as final.

### NoobAI XL 1.1 EPS
- Special-before-General matches native caption structure;
- common bondage/device tags plausibly have strong exposure through Danbooru/e621, but specific rare topology still needs empirical verification;
- do not infer `shrimp tie` or `strappado` reliability from broad `bondage` success.

### Anima
- multiple-character and relation prompting benefits from explicit subject identity/position in practical discussions;
- tags and natural language can coexist;
- concise factual relation clauses are a candidate when a tie involves actor ownership or multiple participants;
- exact superiority over tag-only for BDSM topology remains `TEST_REQUIRED`.

## 10. Assisted-control boundary

DWPose/ControlNet can help impose the body geometry but cannot by themselves guarantee rope/cuff topology semantics.

Forge Couple/regional prompting can separate actors/regions but cannot teach an unknown tie concept to the checkpoint.

Assisted lane sequencing:
1. prove concept/objects in Prompt-only if possible;
2. use pose control for geometry failure;
3. use regional control for actor/resource separation;
4. use inpaint for small connector/topology repair;
5. record intervention type separately.

Do not call an assisted result evidence of unaided Prompt reliability.

## 11. Evaluator design

Unary taggers can help confirm broad concepts such as rope, cuffs, gag, blindfold, bondage if covered.

They cannot certify:
- which wrist is bound
- whether both wrists are bound
- whether a rope line reaches the correct anchor
- whether the topology is hogtie/frogtie/strappado rather than generic bondage
- dominance/ownership relation in a multi-actor scene.

For difficult topology, human review or structure-aware visual predicates remain necessary.

Potential machine side evidence:
- body keypoints from DWPose for limb geometry
- open-vocabulary localization for large devices

But these remain side evidence, not the final semantic judge.

## 12. Test matrix

Representative tiers:

### Tier 1 — device presence
- cuffs / gag / blindfold / spreader bar

### Tier 2 — body-site state
- bound wrists / bound ankles / bound arms

### Tier 3 — topology pose
- hogtie / frogtie / reverse prayer

### Tier 4 — rare topology
- strappado / shrimp tie / predicament bondage

### Tier 5 — composite
- restraint + another Special requiring visible body site or device relation

For each:
- minimal target
- +visibility
- +geometry
- +ownership/resource support if relevant
- Negative ON/OFF when anatomy-sensitive
- predetermined multi-seed repeat
- LoRA/assisted variants separated.

## 13. Audit labels

- `DEVICE_PRESENT`
- `DEVICE_MISSING`
- `BODY_SITE_OK`
- `WRONG_BODY_SITE`
- `TOPOLOGY_OK`
- `TOPOLOGY_PARTIAL`
- `DECORATIVE_ONLY`
- `POSE_ONLY`
- `RESTRAINT_ONLY`
- `CONNECTOR_FAILURE`
- `VISIBILITY_UNCLEAR`
- `ANATOMY_COLLATERAL`
- `POSTPROCESS_RESCUE`
- `ASSISTED_ONLY`

## 14. HOLD backlog

- exact WAI v17 topology success by tie type
- exact NoobAI EPS rare tie trigger exposure
- tag-only vs short relation clause in Anima for topology
- exact camera/viewpoint that maximizes topology observability without hiding devices
- broad anatomy Negative effect by tie
- reliable automatic topology evaluator

## Sources

- Project dictionary: `data/special2788/prompt_reference/06_拘束・BDSM・支配.txt`
- WAI v17 author card: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md
- NoobAI 1.1: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- Anima: https://huggingface.co/circlestone-labs/Anima
- Anima multi-character discussion: https://huggingface.co/circlestone-labs/Anima/discussions/93
- ControlNet: https://arxiv.org/abs/2302.05543
- DWPose: https://github.com/IDEA-Research/DWPose
- T2I-CompBench: https://arxiv.org/abs/2307.06350
- Negative prompt mechanism: https://arxiv.org/abs/2406.02965
