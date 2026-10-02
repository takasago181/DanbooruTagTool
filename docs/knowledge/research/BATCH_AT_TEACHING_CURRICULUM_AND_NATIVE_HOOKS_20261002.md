# BATCH_AT — Teaching curriculum and native hook routing — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: practical pedagogy + current-runtime verification
Scope: clearly adult consensual-fantasy image generation, Anima/Illustrious/ComfyUI/Forge Neo

## 1. Teacher role is a diagnostic role

A useful teacher should not merely provide a finished prompt.

The teacher should be able to:
1. identify the learner's current skill level;
2. isolate the failing layer;
3. choose the lowest-cost next intervention;
4. define an A/B test;
5. explain what a success does and does not prove;
6. preserve the result as reusable evidence.

The teaching target is:
`understanding -> reproduction -> diagnosis -> controlled intervention -> independent practice`.

## 2. Three success levels

### POSSIBILITY
At least one seed/output demonstrates the target.

This proves:
- the pipeline can sometimes produce it.

It does not prove:
- robustness;
- generalization;
- production efficiency.

### RELIABILITY
A fixed seed set and fixed evaluation criteria show repeatable success.

This is the level needed for durable generation guidance.

### SALVAGEABILITY
A failed base image can be converted into an acceptable production image through:
- regional control;
- reference conditioning;
- ControlNet;
- inpaint;
- detailer;
- postprocess.

This is a production skill, not base-model evidence.

Promoted:
- K-PRACTICAL-026.

## 3. ComfyUI core now has native advanced LoRA hook primitives

Source:
https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_hooks.py

Current core contains:
- `Create Hook LoRA`;
- `Set Hook Keyframes`;
- `Create Hook Keyframe`;
- interpolated hook keyframes;
- `Timesteps Range`;
- conditioning nodes accepting:
  - mask;
  - hooks;
  - timestep range.

This means ComfyUI itself provides building blocks for:
- conditioning-bound LoRA hooks;
- spatial masks;
- time scheduling;
- combinations of those controls.

Boundary:
- these nodes are marked experimental;
- generic node availability does not establish exact Anima LoRA compatibility;
- local end-to-end tests are required.

Promoted:
- K-TOOL-033.

## 4. Forge Neo Anima vs ComfyUI control routing

### Forge Neo Regional Prompter
Current:
- Anima regional text/attention supported;
- Region LoRA unsupported.

### ComfyUI
Possible lanes:
- native hooks + masked conditioning;
- native hook scheduling;
- Anima Regional Conditioning;
- inpaint/per-subject reconstruction.

Teaching consequence:
Do not teach “Regional Prompting” as one feature.
Name the mechanism:
- regional text;
- regional attention;
- localized adapter;
- regional reference;
- regional reconstruction.

## 5. Current community confirmation

Recent thread:
https://www.reddit.com/r/comfyui/comments/1ws23ur/multiple_characters_in_one_single_generated_image/

User uses both Illustrious and Anima and reports:
- character details can swap;
- regional prompting is commonly recommended;
- a responder distinguishes model-known characters from LoRA-required characters;
- for LoRA-required characters they recommend a LoRA hook/localization path.

This aligns with current tool architecture:
native identity and adapter identity are different problems.

Promoted:
- K-COMM-ANIMA-027.

## 6. Teaching principle: least invasive intervention

For each failure choose the smallest next step.

### Vocabulary/trigger failure
Change:
- tag/alias/description.

Do not immediately add ControlNet.

### Seed-level composition variation
Change:
- seed.

Do not freeze the whole Prompt.

### Identity leakage
Change:
- simplify identity context;
- isolate LoRA influence;
- regional/reference route.

### Pose/geometry failure
Change:
- pose/depth/line.

Do not add identity tags.

### Local anatomy failure
Change:
- inpaint/detailer.

Do not rebuild the entire scene unless necessary.

## 7. Teaching principle: expose the failure

A lesson should often show:
- the failed image;
- the diagnostic label;
- the corrected image;
- the single change that corrected it.

This teaches causality better than showing only a perfect recipe.

Promoted:
- K-PRACTICAL-027
- K-EVAL-017.

## 8. Adult teaching boundaries

The curriculum is for clearly adult, consensual/adult-fantasy content.

The technical curriculum focuses on:
- relation representation;
- multiple adults;
- visibility;
- body-part ownership;
- pose/geometry;
- identity/style;
- adapter/control behavior;
- anatomy repair.

The reusable teaching knowledge should prefer structural variables over memorized explicit prompt passages.

## 9. When to show assisted rescue

Teaching progression:
1. show prompt-only attempt;
2. diagnose its limitation;
3. add the smallest assisted control;
4. retain both before/after.

This prevents a learner from believing a heavily repaired final image represents plain-checkpoint reliability.

Promoted:
- K-PRACTICAL-028.

## 10. Curriculum artifact

Canonical teaching sequence:
`docs/knowledge/current/ADULT_IMAGE_GENERATION_TEACHING_CURRICULUM.md`

It defines:
- modules;
- exercises;
- pass criteria;
- diagnostic rubrics;
- escalation rules;
- teacher response pattern.

## Promotion result

New ACCEPTED:
- K-TOOL-033
- K-PRACTICAL-026
- K-PRACTICAL-027
- K-EVAL-017
- K-PRACTICAL-028

New CANDIDATE:
- K-COMM-ANIMA-027
