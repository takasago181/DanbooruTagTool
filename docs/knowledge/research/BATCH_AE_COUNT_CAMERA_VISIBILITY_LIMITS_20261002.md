# BATCH_AE — Count / camera / visibility limits — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: recent research synthesis
Scope: exact count, camera/viewpoint, visibility for relation-heavy scenes

## 1. Exact count is not ordinary concept recognition

Source:
https://arxiv.org/abs/2503.06884

T2ICountBench isolates numerical adherence from general image quality.

Reported research conclusion:
- state-of-the-art diffusion models frequently generate incorrect object counts;
- performance degrades as requested count rises;
- simple prompt-refinement strategies do not reliably repair numeracy.

Project consequence:
A model can know the concept and still fail the count.

For hard scenes:
- concept presence
- actor count
- implement count
- simultaneous relation count
must be separate predicates.

Promoted:
- K-HARD-011.

## 2. Counting needs explicit evaluation

Do not infer correct count from:
- CLIP/image-text similarity;
- target tagger confidence;
- visual impression at thumbnail size.

Preferred:
- human explicit count;
- object detector/counting evaluator where the target class is supported;
- manual review for rare/anatomical relation counts.

Count correctness does not imply:
- correct ownership;
- correct body site;
- correct simultaneous relation.

Promoted:
- K-EVAL-009.

## 3. Camera/viewpoint is a separate control problem

PreciseCam:
https://arxiv.org/abs/2501.12910

Motivation:
Natural-language phrases such as top-view/low-angle provide only coarse control.

Method:
- explicit intrinsic/extrinsic camera parameters;
- camera-conditioned T2I generation;
- evaluated against prompt-engineering baselines.

2026 viewpoint-token research:
https://arxiv.org/abs/2604.19954

Motivation:
current T2I models still struggle with precise camera control from natural language alone.

Method:
- learned camera/viewpoint tokens;
- explicit geometric conditioning.

Project consequence:
`camera/viewpoint failure != model does not know the semantic target`.

If the required body-site/relation is present but not visible because camera is wrong:
- classify as visibility/camera failure;
- do not add more target synonyms and call it semantic support.

Promoted:
- K-PROMPT-004.

## 4. Visibility is an evaluation predicate

For relation-heavy targets ask:
- is the relevant region in frame?
- is it occluded?
- is the actor/target distinction visible?
- can the required contact be judged?
- is the camera angle sufficient to tell front/back/ownership?

If not:
`VISIBILITY_UNCLEAR`
rather than:
`CONCEPT_FAIL`.

## 5. Camera-support escalation

Prompt-only lane:
- one framing instruction
- one viewpoint instruction
- remove conflicting visibility/body descriptions

Assisted lane:
- pose/depth/reference composition
- explicit camera-control method if compatible
- img2img/inpaint from a geometry-correct source

Do not stack:
- close-up
- full body
- feet visible
- extreme perspective
- overhead
unless those constraints are genuinely compatible.

## 6. Count stress ladder

C1 — one instance
C2 — exactly two
C3 — exactly three
C4 — four+
CR — simultaneous relation count

A concept should not get a single “supported” flag if C1 works and C3 fails.

## 7. Adult/hard-scene implication

A difficult image can fail because:
- target absent;
- target present, count wrong;
- count correct, ownership wrong;
- ownership correct, camera hides relation;
- relation visible, anatomy collateral fails.

Preserve all axes.

## Promotion result

New ACCEPTED:
- K-HARD-011
- K-EVAL-009
- K-PROMPT-004

New CANDIDATE:
- K-TOOL-023
