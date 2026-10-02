# BATCH_AF — Anatomy / occlusion / local repair — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: research synthesis
Scope: local anatomy defects, occlusion, human-scene repair

## 1. Relation correctness and anatomy correctness are different

A hard scene can fall into four states:

1. relation correct / anatomy correct
2. relation correct / anatomy locally broken
3. relation wrong / anatomy clean
4. relation wrong / anatomy broken

Do not collapse these states.

This matters because:
- local repair tools can fix state 2;
- fixing hands cannot rescue state 3;
- adding relation Prompt terms is not the first repair for state 2.

Promoted:
- K-HARD-012.

## 2. HandCraft: local hand restoration

Source:
https://arxiv.org/abs/2411.04332

Reported method:
- detect malformed hand regions;
- construct local masks;
- build depth/hand geometry conditioning;
- use diffusion editing to reconstruct the hand;
- preserve surrounding pose/color/style.

Project lesson:
A malformed hand can be treated as a localized geometry defect once the global scene is acceptable.

Evidence lane:
`BASE_RELATION_OK + HAND_FAIL -> LOCAL_HAND_REPAIR`.

Do not report final repaired hand as base-model hand success.

Promoted as CANDIDATE tool/research lead:
- K-TOOL-024.

## 3. Hand-specific structure is richer than one “hand” tag

HanDiffuser source:
https://arxiv.org/abs/2403.01693

The work models:
- 3D hand shape
- joint-level finger positions
- orientations
- articulations

Project implication:
“bad hand” is not one scalar defect.

Useful local labels:
- wrong finger count
- impossible finger orientation
- hand/arm discontinuity
- hand belongs to wrong actor
- contact hand misses target
- hand occluded beyond judgement

No new model-wide Claim is needed; use this as evaluation vocabulary.

## 4. Occlusion-aware human placement

Source:
https://arxiv.org/abs/2505.04052

Person-In-Situ addresses:
- user-specified human pose;
- scene depth;
- natural foreground occlusion.

Motivation:
existing insertion approaches can put the inserted person unrealistically in the frontmost layer.

Project lesson:
Pose and layer/depth/occlusion are separate variables.

A person can have:
- correct skeleton;
- wrong depth layer;
- wrong overlap;
- hidden target relation.

Promoted:
- K-HARD-013.

## 5. Occlusion failure labels

Add:
- `WRONG_DEPTH_ORDER`
- `TARGET_OCCLUDED`
- `RELATION_OCCLUDED`
- `BODY_SITE_OCCLUDED`
- `UNNATURAL_LAYERING`

These differ from:
- target absent
- relation absent
- wrong body-site.

## 6. Local anatomy evaluation

For relevant scenes score:
- hand shape
- finger count
- finger orientation
- hand-to-arm continuity
- limb continuity
- joint plausibility
- body-part ownership
- contact alignment

Keep separate from:
- actor role
- relation semantics
- count
- topology.

Promoted:
- K-EVAL-010.

## 7. Repair ladder

If global semantics are correct:

A. seed/regenerate if reliability test permits
B. local inpaint
C. mask + structural/depth guidance
D. dedicated local anatomy restorer
E. manual edit

If global semantics are wrong:
return to Prompt/control/binding diagnosis instead.

## 8. Adult/hard scene use

In overlapping multi-body scenes, anatomy defects may occur exactly at:
- hands;
- limbs;
- contact regions;
- occlusion boundaries.

Therefore final evaluation needs both:
`RELATION_SCORE`
and
`LOCAL_ANATOMY_SCORE`.

One must not overwrite the other.

## Promotion result

New ACCEPTED:
- K-HARD-012
- K-HARD-013
- K-EVAL-010

New CANDIDATE:
- K-TOOL-024
