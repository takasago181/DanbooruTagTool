# Hard Fetish Generation Knowledge — Machine / Device-Mediated Relations

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `DEEP_RESEARCH_V1 / evidence-reference`

## 1. Scope

成人・合意下の machine/device-mediated sexual concepts を、単なる物体生成ではなく **device identity + functional relation + target body site + actor/resource binding** の問題として扱う。

Representative project rows:
- `sex machine` ID312 Core / 3343
- `dildo machine` ID315 Alias -> `sex_machine`
- `milking machine` ID310 Core / 2703
- `riding machine` ID311 Extended / 105
- `sybian` ID313 Extended / 148
- `robot sex` ID314 Extended / 136
- `mecha on girl` ID309 Extended / 79
- Semantic candidates: `spanking machine`, `fuck machine`, `machine penetration`, `mechanical sex`, `automatic dildo`, `sex robot`
- related device concepts: vibrator, strap-on, dildo harness, remote-control vibrator, catheter-like/tool-mediated cases.

## 2. Machine concept decomposition

### 2.1 Device identity
What device is depicted?
- fixed machine
- motorized actuator
- riding device
- suction/milking device
- robot/mecha actor
- handheld/remote device

### 2.2 Device role
- background prop
- passive support
- active actuator
- autonomous actor

### 2.3 Functional relation
The device must actually perform the requested action, not merely coexist in the frame.

### 2.4 Target body site
The active component must connect to the correct site/person.

### 2.5 Geometry
- device axis
- subject pose
- actuator direction
- attachment/contact point
- cables/tubes/arms where intrinsic

### 2.6 Resource ownership
In multi-device or multi-actor scenes, each device/actuator must belong to the correct target/action.

## 3. Why machine scenes are evaluator traps

A unary detector/tagger can correctly detect `machine`, `robot`, `sex toy`, `cable`, or `dildo` while the intended relation is completely wrong.

Therefore machine success has at least three nested levels:

1. `DEVICE_PRESENT`
2. `DEVICE_TYPE_CORRECT`
3. `FUNCTIONAL_RELATION_CORRECT`

Only level 3 is sufficient for relation-centric Special success.

## 4. Main failure modes

### `BACKGROUND_MACHINE_ONLY`
Machine-like object exists but functions as scenery.

### `DEVICE_TYPE_COLLAPSE`
Rare machine concept collapses to a common toy/device.

### `MECHA_IDENTITY_DOMINANCE`
`mecha`/`robot` semantics dominate and generate a robot character rather than a functional machine relation.

### `WRONG_INTERFACE`
Actuator/tool is attached to the wrong body site.

### `WRONG_TARGET`
Device acts on the wrong person in a multi-actor scene.

### `ACTUATOR_GEOMETRY_FAIL`
Machine and target are both present but their axes/contact geometry are impossible or disconnected.

### `CABLE_TUBE_BLEED`
Cables/tubes multiply, fuse with limbs, or become unrelated mechanical decoration.

### `DEVICE_REPLACES_ANATOMY`
Mechanical components replace human anatomy instead of interacting with it.

### `RESTRAINT_CONTEXT_LEAK`
A machine LoRA or learned concept imports bondage/restraint context even when not intrinsic to the requested Special.

### `COUNT_COLLAPSE`
Multi-actuator/multi-device request becomes one dominant device or duplicates uncontrolled parts.

## 5. Practical LoRA evidence

Niche Illustrious machine LoRA pages commonly pair machine triggers with restraint, stationary restraints, tubing/cables, object insertion, devices and quality terms.

Interpretation:
- the adapter likely learned a *scene bundle*, not a clean isolated token;
- restraint/cables may improve the adapter's familiar composition but are not automatically intrinsic to `sex machine` identity;
- adapter success does not prove base checkpoint success;
- adapter context leakage should be measured separately from target success.

LoRA evidence should always record:
- adapter name/version
- base family
- weight
- trigger(s)
- whether trigger omitted
- other loaded adapters
- base Prompt comparison on same seed.

## 6. Geometry-first vs semantics-first diagnosis

If a machine scene fails, separate:

### Semantic device failure
Machine/device itself is missing or wrong.

### Relation failure
Machine is correct but interaction wrong.

### Geometry failure
Relation intent is visible but physical alignment is implausible.

### Visibility failure
Contact point is hidden/cropped.

### Resource failure
Multiple arms/cables/devices compete or bind to wrong target.

This distinction prevents overcorrecting a geometry failure with more device synonyms.

## 7. Support roles

### Meaning support
Only if needed to identify a rare machine subtype or constituent.

### Geometry support
Subject posture / machine alignment needed for physical relation.

### Visibility support
Framing needed to show both device and contact point.

### Resource parking
Useful when spare limbs, robot arms, cables or secondary devices cause binding ambiguity.

### Aesthetic support
Industrial/lab/background styling is optional unless intrinsic to the target concept.

Audit rule: scene-style terms must not become mandatory merely because machine LoRAs use them.

## 8. Assisted-control boundary

Machine scenes often need both object localization and body geometry.

Possible side tools:
- DWPose / pose ControlNet for subject geometry
- regional/Forge Couple for actor/device region separation
- open-vocabulary detector for device localization
- inpaint for small contact/connector repair

Limits:
- pose control does not certify device semantics;
- object detector does not certify functional relation;
- regional prompting does not teach an unknown device concept;
- inpaint success is `POSTPROCESS_RESCUE`.

## 9. Model-family notes

### WAI Illustrious v17
- use author minimal baseline; avoid giant generic quality/Negative stacks;
- Hires may repair limbs and mechanical-human contacts indirectly, so retain base evidence;
- exact sex-machine relation reliability is not publicly benchmarked -> `IMAGE_TEST_REQUIRED`.

### NoobAI XL 1.1 EPS
- full Danbooru/e621 caption training gives plausible broad device/sexual-concept exposure;
- Special-before-General matches caption structure;
- current Semantic phrases such as `machine penetration` are not proof of training-token exposure.

### Anima
- relation-oriented natural language/hybrid prompting is structurally plausible because Anima uses a language-model text encoder and supports prose/tags;
- stable explicit subject/device names are preferred over pronouns in complex scenes;
- exact hard-machine improvement over tag-only remains a controlled-test question.

## 10. Evaluator design

### Machine predicates
- `DEVICE_PRESENT`
- `DEVICE_TYPE_OK`
- `TARGET_PERSON_OK`
- `TARGET_SITE_OK`
- `ACTUATOR_CONTACT_OK`
- `RELATION_OK`
- `COUNT_OK`
- `VISIBILITY_OK`

### Automatic evidence
Open-vocabulary detection can support device presence/localization. It cannot alone answer whether the machine is functionally performing the requested relation.

Unary anime taggers are especially vulnerable to false PASS when a machine/toy is visible.

## 11. Representative test ladder

1. common `sex machine` minimal
2. `sex machine + person/count`
3. + one visibility support
4. + one geometry support
5. rare machine subtype vs broad parent
6. robot/mecha actor variant separated from fixed-machine variant
7. multi-seed repeatability
8. machine + restraint composite only after machine-only baseline
9. base vs LoRA-assisted same-seed comparison
10. assisted-control lane after bounded Prompt support.

## 12. Hard composite warnings

High-risk composites:
- machine + restraint topology
- machine + multiple insertion/count
- machine + unusual anatomy
- machine + multiple actors
- mechanical tentacles + machine device

These combine device identity, relation, count, geometry and actor binding. A failure should be decomposed rather than repaired by adding all related tags at once.

## 13. HOLD backlog

- exact WAI v17 `sex machine`/`milking machine` functional-relation reliability
- exact NoobAI EPS rare machine exposure
- Anima tag-only vs short relation prose for device contact
- best model-family-specific visibility/framing support
- reliable automatic functional-relation judge
- LoRA context-leak magnitude and optimal weights by adapter

## Sources

- Project dictionary: `data/special2788/prompt_reference/05_挿入・性具・機械.txt`
- WAI v17: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md
- NoobAI 1.1: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- Anima: https://huggingface.co/circlestone-labs/Anima
- T2I-CompBench: https://arxiv.org/abs/2307.06350
- ControlNet: https://arxiv.org/abs/2302.05543
- DWPose: https://github.com/IDEA-Research/DWPose
