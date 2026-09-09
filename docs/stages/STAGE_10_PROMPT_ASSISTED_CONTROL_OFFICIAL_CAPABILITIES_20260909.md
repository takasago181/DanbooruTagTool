# Stage10 PROMPT assisted-control official capabilities

最終更新: 2026-09-09  
Owner: PROMPT / Issue #5  
Status: runtime capability ledger. **Not production specification.**

## Purpose

Prompt-onlyでhard-targetが崩れる場合に、どの外部制御を候補にするかを公式実装仕様から整理する。

## Forge Couple

Official: https://github.com/Haoming02/sd-forge-couple
Evidence: `OFFICIAL_RUNTIME_FACT`

Confirmed:
- targets different conditionings at specific regions
- designed to reduce feature/color mixing between subjects
- supports Forge Classic / Forge Neo
- current README states Anima support
- effectiveness depends on how well the checkpoint itself follows the composition
- author recommends still prompting the total amount of subjects within every region

PROMPT use:
- multi-actor identity mixing
- attribute leakage
- left/right or region-specific role separation
- hard-target actor-target binding when Prompt-only repeatedly fails

Caution:
- not a substitute for a checkpoint that cannot understand the requested scene
- success under Couple must be labeled `ASSISTED_CONTROL`, not PROMPT_ONLY

## Regional Prompter

Official: https://github.com/hako-mikan/sd-webui-regional-prompter
Evidence: `OFFICIAL_RUNTIME_FACT`

Confirmed:
- different prompts can be assigned to different regions
- Attention and Latent modes exist
- compatibility differs across A1111 / Forge / reForge and modes
- region-based prompt calculation occurs inside U-Net in Attention mode

PROMPT use:
- spatial separation of actors/objects
- controlled role distribution
- reduce cross-region prompt leakage

Caution:
- exact compatibility with current Forge Neo workflow must be verified before production use
- do not generalize reForge support to Forge Neo without local verification

## ADetailer

Official: https://github.com/Bing-su/adetailer
Evidence: `OFFICIAL_RUNTIME_FACT`

Confirmed:
- automatic detection, masking and inpainting
- effectively performs a later local correction pass

PROMPT use:
- face/hand/local-detail cleanup after scene composition succeeds
- potentially repair local anatomy without re-solving the whole scene

Critical audit rule:
- final ADetailer image cannot automatically prove original Prompt succeeded
- store pre-ADetailer and post-ADetailer evidence separately

## ControlNet WebUI

Official: https://github.com/Mikubill/sd-webui-controlnet
Evidence: `OFFICIAL_RUNTIME_FACT`

Confirmed:
- injects ControlNet-style guidance into Stable Diffusion generation without merging the base model
- supports multiple controls
- supports region masks for some control paths
- pose/depth/canny/line-type guidance families exist depending on model availability

PROMPT use:
- pose/geometry stabilization
- depth/layout control
- hard-target cases where text describes the semantics correctly but geometry repeatedly fails

Caution:
- ControlNet model compatibility is architecture/checkpoint dependent
- use only exact compatible control model/version
- assisted geometry success is not proof of better text semantics

## Dynamic Prompts

Official: https://github.com/adieyal/sd-dynamic-prompts
Evidence: `OFFICIAL_RUNTIME_FACT`

Confirmed:
- random variants
- wildcard files
- combinatorial generation
- nested wildcards
- fixed-seed workflows
- original template can be saved to metadata
- works with X/Y Plot for exhaustive parameter/prompt variation testing

PROMPT use:
- Stage10 experiment generation
- candidate support combinations
- canonical/alias variants
- family baseline matrices
- reproducible batch exploration

Critical rule:
- save both `SOURCE_TEMPLATE` and `RESOLVED_PROMPT`
- a wildcard experiment is invalid for causal comparison if multiple dimensions vary unintentionally

## Escalation ladder candidate

Prompt-side candidate only:
1. `PROMPT_ONLY_BASELINE`
2. `PROMPT_ONLY_TARGETED_SUPPORT`
3. `REGION_CONDITIONING`
4. `POSE/DEPTH_CONTROL`
5. `LOCAL_INPAINT_REPAIR`

Escalate based on diagnosed failure, not because the target is 'hard'.

Mapping:
- identity/attribute leakage -> Forge Couple / Regional
- pose/geometry failure -> ControlNet candidate
- local anatomy/detail failure after semantic success -> ADetailer
- systematic Prompt variants -> Dynamic Prompts

## Evidence separation

Every Stage10 record should be able to say:
- Prompt-only or assisted
- extension name/version/commit
- extension mode
- region/mask/control settings
- pre-control Prompt
- resolved Prompt
- final actual metadata

## Boundary

No extension is mandated for production by this ledger. Exact Forge Neo compatibility and local behavior require Stage10/local validation.