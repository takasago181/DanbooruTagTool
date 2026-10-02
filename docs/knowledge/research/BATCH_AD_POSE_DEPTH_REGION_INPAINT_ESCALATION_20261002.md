# BATCH_AD — Pose / depth / region / inpaint escalation — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: research + official ComfyUI control synthesis
Scope: relation-heavy scenes, human geometry, occlusion, assisted reconstruction

## 1. Control modalities are not interchangeable

ControlNet source:
https://arxiv.org/abs/2302.05543

The original framework demonstrates different conditioning classes:
- edge/canny
- depth
- segmentation
- human pose
- other structural signals

Project consequence:
Do not store `ControlNet=true`.
Store the control modality because each one constrains a different property.

## 2. Official ComfyUI preprocessor separation

Source:
https://blog.comfy.org/p/preprocessor-and-frame-interpolation

2026 official template workflows separate:
- Depth Estimation
- Lineart Conversion
- Pose Detection
- Normals Extraction

ComfyUI explicitly presents these as modular/reusable preprocessing stages.

Evidence consequence:
For a controlled test, preserve:
- source image
- preprocessor name/version
- preprocessor output
- downstream control model
- control strength/schedule

A failed generation can come from bad preprocessing rather than diffusion-model semantics.

## 3. Pose control: what it represents

Whole-body pose research:
- https://arxiv.org/abs/2007.11858
- https://arxiv.org/abs/2307.15880

Whole-body pose estimation includes dense body/hand/face/foot landmarks.

Useful for:
- limb arrangement
- stance
- hand/foot placement
- approximate multi-person skeleton layout

Not encoded by skeleton alone:
- who owns an object
- who acts on whom
- exact contact semantics
- body-site ownership in overlapping people
- source/destination
- restraint/device topology

Therefore:
`pose matches != relation success`.

Promoted:
- K-BIND-003.

## 4. Depth control

Depth maps constrain relative scene distance.

Useful for:
- front/back ordering
- large-scale overlap
- perspective
- subject/background depth separation

Weakness:
Depth does not uniquely encode identity or semantic relation.

A correct depth map can still yield:
- swapped identities
- wrong attributes
- wrong contact
- wrong target ownership.

## 5. Line/edge control

Lineart/edge signals preserve:
- contour
- silhouette
- composition boundaries
- object placement

Use when:
- desired geometry already exists in a sketch/reference;
- pose skeleton is too sparse;
- exact contour/shape matters.

Risk:
It can preserve an incorrect source structure faithfully.

## 6. Region/mask control

Use when failure is:
- character A traits leaking into B;
- LoRA A affecting full image;
- resource ownership mixed across subjects.

Region/mask control addresses **where** conditioning applies.

It does not automatically resolve:
- an unknown concept;
- wrong semantic role;
- impossible topology;
- bad source pose.

## 7. Inpainting

Official ComfyUI examples show mask-driven local editing:
https://docs.comfy.org/tutorials/api-nodes/openai/gpt-image-1

Project use:
- local face/hand/body-region correction;
- identity reconstruction;
- local relation repair when global composition is already acceptable.

Evidence rule:
base pass and inpaint pass are separate.

Record:
- mask geometry;
- prompt used for edit;
- denoise/strength;
- source image;
- changed region;
- whether relation success existed before edit.

## 8. Diagnostic escalation table

### Failure: posture/limb geometry wrong
Try:
1. Prompt simplification
2. pose control
3. pose + depth
4. inpaint if only local region remains wrong

### Failure: front/back/overlap wrong
Try:
1. Prompt spatial wording
2. depth
3. region + depth
4. local reconstruction

### Failure: identity/attribute bleed
Try:
1. remove prompt/LoRA contamination
2. region/mask conditioning
3. masked LoRA
4. per-subject inpaint

### Failure: contour/device shape wrong
Try:
1. concise structural description
2. lineart/edge
3. depth + lineart
4. inpaint

### Failure: semantic relation wrong
Do NOT jump directly to pose.
First verify:
- subject count
- identity
- role
- target site
- relation wording

Then add structural control only if geometry is the bottleneck.

## 9. Adult/hard-scene relevance

Hard scenes commonly combine:
- overlapping bodies
- partial occlusion
- unusual joint configurations
- multiple subjects
- local target-site visibility

Therefore the system should distinguish:
- semantic failure
- geometry failure
- visibility failure
- preprocessing failure
- control-model failure
- edit failure

These are not interchangeable.

## 10. Experimental evidence matrix

For one hard target:

P0 — Prompt-only
P1 — + pose
P2 — + depth
P3 — + pose+depth
P4 — + region/mask
P5 — + local inpaint

Same initial seed where technically meaningful.

Score atomic predicates, not final beauty.

## Promotion result

New ACCEPTED:
- K-TOOL-020
- K-TOOL-021
- K-BIND-003
- K-TOOL-022
- K-HARD-010

No Prompt-only capability Claim is upgraded by assisted success.
