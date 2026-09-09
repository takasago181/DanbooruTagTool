# Hard Fetish Generation Knowledge — Composite Failure Matrix

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `DEEP_RESEARCH_V1`

## 1. Purpose

複数の特殊・ハード系Specialを同時に要求した時、失敗を「modelがタグを知らない」でまとめないための分解表。

Hard compositeでは、Special数よりも **independent relation/binding/count/geometry requirements** の数が重要。

## 2. Complexity dimensions

For each Prompt, count or classify:
- actor count
- Special count
- target body-site count
- independent relation count
- exact-count requirements
- device/implement count
- restraint attachment points
- nonhuman appendage source count
- visibility requirements
- geometry constraints
- natural-language relation clauses
- loaded LoRA/adapters
- assisted-control interventions.

Raw token count is secondary.

## 3. Pairwise composite matrix

| Pair class | Typical primary risk | Secondary risk | First diagnostic split |
|---|---|---|---|
| insertion + restraint | geometry/topology competition | target-site occlusion | each Special alone -> AB minimal |
| insertion + machine | device-body functional binding | wrong site/count | machine-only relation -> insertion-only -> AB |
| insertion + tentacle | appendage ownership + target site | count explosion | tentacle relation alone -> site relation alone |
| insertion + fluid state | destination/source binding | visibility | insertion success vs fluid destination separately |
| restraint + machine | anchor/device/resource competition | pose collapse | restraint graph vs machine relation separately |
| restraint + tentacle | restraint-source ambiguity | occlusion | generic restraint vs tentacle grab relation |
| restraint + fluid | body-site visibility | role/context leak | restraint topology first, then fluid target |
| machine + tentacle | organic/mechanical identity fusion | actuator count | mechanical identity then relation |
| machine + fluid | tube/source/destination binding | background-machine false pass | device relation then source-destination |
| tentacle + fluid | source ownership | visual clutter | tentacle ownership then material target |
| hard concept + multi-actor | actor-target swap | feature bleed | actor identities/positions before hard relation |
| hard concept + exact count | count collapse | anatomy error | 1-unit baseline -> 2 -> 3 |

## 4. Three failure layers

### Layer A — concept activation
Does each requested component appear when tested alone?

### Layer B — composition/binding
Do the independently working concepts bind correctly when combined?

### Layer C — observability/usability
Can the intended relation actually be judged and is collateral damage acceptable?

A composite cannot be diagnosed at Layer B until Layer A is known.

## 5. Escalation protocol

For A+B:

1. `A_ONLY`
2. `B_ONLY`
3. `AB_MINIMAL`
4. `AB + one Frame support`
5. `AB + one Viewpoint support`
6. `AB + one targeted Geometry/Binding support`
7. `AB + one Resource separation support`
8. Negative ON/OFF if overlap risk
9. predetermined multi-seed repeat
10. regional/pose-assisted lane
11. LoRA-assisted lane separately.

Do not add several support roles at once; it destroys causal attribution.

## 6. Resource competition model

A useful mental model for difficult scenes is that the generator has limited visual/attention resources for:
- hands/limbs
- openings/body sites
- tools/devices
- appendages
- actor identity
- camera space.

When two Specials require the same resource in incompatible ways, failure may be structural even when both tags are individually learned.

Examples:
- two actions competing for the same hand
- restraint hiding the body site required by another relation
- multiple devices competing for the same target site
- tentacle count obscuring machine contact
- full-body frame reducing small-site observability.

This is a diagnosis heuristic, not a literal model architecture claim.

## 7. Compatibility classes

### `COMPATIBLE_INDEPENDENT`
Concepts can coexist without sharing critical resources.

### `COMPATIBLE_BUT_BINDING_HEAVY`
Semantically compatible, but actor/site ownership must be correct.

### `RESOURCE_COMPETING`
Both concepts demand the same limb/body site/object/camera resource.

### `GEOMETRY_COMPETING`
Each concept imposes a different pose/orientation.

### `VISIBILITY_COMPETING`
One concept's ideal framing hides the other.

### `NEGATIVE_CONFLICTING`
One target's usual cleanup Negative can suppress the other target.

### `MODEL_TRIGGER_CONFLICTING`
Strong learned triggers pull incompatible scene/style/context priors.

Compatibility must be tested; semantic compatibility alone is not enough.

## 8. Pair-order testing

For bag-of-tag SDXL-like systems, raw textual order can matter less predictably than semantic competition, but exact family/order effects remain empirical.

If order is suspected:
- compare `AB` vs `BA` while keeping all else constant;
- do not interpret one seed difference as universal ordering law;
- Anima hybrid prose may need explicit sentence-level subject/action structure rather than mere tag reordering.

## 9. Count escalation

For count-sensitive scenes, do not jump directly to a large hard composite.

Recommended:
- count 1 baseline
- count 2 same relation
- count 3 if needed
- then add second Special.

Record:
- exact correct count
- undercount
- overcount
- fused count
- duplicated unrelated anatomy.

## 10. Visibility budget

Every additional actor/device/tentacle/support competes for pixels.

A composite can become impossible to evaluate at a given framing even if the model conceptually follows it.

Audit rule:
- `VISIBILITY_UNCLEAR` is not target FAIL;
- but a Prompt configuration that systematically makes the target unjudgeable is not production-useful and should not be selected as support.

## 11. Assisted control decision

Move from Prompt-only to assisted control when:
- unary components work;
- all relevant functional support roles have been tested one at a time;
- failures remain predominantly geometry/actor-region/resource allocation;
- additional synonyms do not create repeatable benefit.

Then choose the assistance matching the blocker:
- DWPose/ControlNet -> body geometry
- Forge Couple/regional -> actor/resource regions
- inpaint -> local connector/body-site repair.

Do not use assisted control to mask unknown semantic activation.

## 12. Human/evaluator judgement

Composite hard scenes should never receive an AUTO PASS from one unary tag confidence.

Minimum final predicates:
- each Special intrinsic predicate set
- actor-target ownership
- body-site correctness
- exact count where intrinsic
- visibility
- collateral anatomy errors
- intervention lane.

Possible final labels:
- `ALL_TARGETS_SUCCESS`
- `A_SUCCESS_B_FAIL`
- `A_FAIL_B_SUCCESS`
- `BOTH_PRESENT_BINDING_FAIL`
- `COUNT_FAIL`
- `VISIBILITY_UNCLEAR`
- `ASSISTED_ONLY`
- `BOTH_FAIL`
- `UNCLEAR`.

## 13. Model-family considerations

### WAI/Illustrious
High-density Booru Prompting makes tag competition and same-role composition conflicts especially important. Keep support blocks minimal and isolated.

### NoobAI EPS
Native structure puts Special before General. Multiple Specials should stay a compact high-information block before large general context, but exact order among multiple Specials remains empirical.

### Anima
Use explicit stable subject names/IDs and relation clauses as an experimental lane for multi-actor hard composites. Avoid pronoun ambiguity. Strong learned concepts may still bleed across actors.

## 14. Research hypotheses worth testing later

- relation load predicts failure better than total tags
- visibility competition explains a meaningful share of false hard-Special failures
- one frequent constituent improves some rare targets but harms others through parent collapse
- exact count fails before unary recognition fails
- LoRA-assisted composites often increase target presence while also increasing context leakage
- regional control reduces actor-target swaps but not unknown body-site semantics.

All remain experimental until project images support them.

## Sources

- ConceptMix: https://arxiv.org/abs/2408.14339
- T2I-CompBench: https://arxiv.org/abs/2307.06350
- Attend-and-Excite: https://arxiv.org/abs/2301.13826
- Rare concept generation: https://arxiv.org/abs/2304.14530
- Forge Couple: https://github.com/Haoming02/sd-forge-couple
- ControlNet: https://arxiv.org/abs/2302.05543
- Anima multi-character discussion: https://huggingface.co/circlestone-labs/Anima/discussions/93
