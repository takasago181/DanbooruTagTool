# BATCH_AY — 実在ワークフローから抽出したローカル成人向け生成の型 — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Scope: clearly adult local anime generation; adult relevance is explicit where sourced, otherwise the workflow is treated as transferable anime-generation evidence  
Mode: 27 public workflow/case-study decomposition

## 0. 目的

流行を「モデル名」で追うのではなく、実際の公開ワークフローを工程に分解する。

各caseで見る:

- input / intent
- base model family
- identity mechanism
- geometry mechanism
- separation mechanism
- edit/repair mechanism
- finishing mechanism
- observed failure
- reusable lesson
- evidence class

長いPromptのコピーではなく、再利用可能な構造を抽出する。

---

# A. Prompt / native-knowledge first

## Case 01 — Anima basic native workflow

Source:
https://www.reddit.com/r/comfyui/comments/1qtl9d5/new_model_anima_workflow/

Stack:
- Anima
- native ComfyUI
- ~1MP
- ordinary sampler/CFG/steps

Pattern:
`native prompt -> base generation`

Value:
Controlを足す前の素のcheckpoint baseline。

Lesson:
新しいtoolを評価する前に plain baselineを保存する。

Evidence:
COMMUNITY, settings aligned with author guidance.

---

## Case 02 — Tags-only vs long NL vs hybrid

Source:
https://huggingface.co/circlestone-labs/Anima/discussions/140

Reported test:
~100 images.

Pattern:
- tags only -> cleaner structure
- long NL -> richer environment/details but more anatomy issues
- hybrid -> compromise, but framing/background can compete

Lesson:
「NL対応 = NLを長くするほど良い」ではない。
subject structureとenvironment proseを分けて評価する。

Evidence:
CONTROLLED_PRACTICAL / COMMUNITY.

---

## Case 03 — Multiple native characters by names/basic appearance

Source:
https://huggingface.co/circlestone-labs/Anima/discussions/93

Pattern:
`count -> character A -> character B -> style`

Observation:
some combinations work from names, others need more detail or fail.

Lesson:
native-known identity is cheaper than LoRA identity, but pair binding is pair-specific.

Evidence:
COMMUNITY.

---

## Case 04 — Japanese natural-language multi-character test

Source:
https://note.com/hkmclab/n/n7611426be16a

Pattern:
`tags + natural language -> multi-character test`

Lesson:
Prompt-only is a useful capability baseline even when later Regional is expected.

Evidence:
PRACTICAL / Japanese community.

---

# B. Multi-character / LoRA separation

## Case 05 — Illustrious/Anima character details swap

Source:
https://www.reddit.com/r/comfyui/comments/1ws23ur/multiple_characters_in_one_single_generated_image/

Stack:
- Illustrious or Anima
- character LoRAs
- regional prompting suggested

Failure:
hair/eyes/details swap between subjects.

Lesson:
presence != identity ownership.
Evaluate attribute ownership separately.

---

## Case 06 — Two character LoRAs merge in SDXL

Source:
https://www.reddit.com/r/comfyui/comments/1v41coi/how_to_create_multiple_characters_in_comfyui_sdxl/

Attempts:
- global LoRA stack
- separate conditioning
- set-area conditioning

Failures:
- merged identity
- side-by-side panel-like split

Fallback reported:
inpainting.

Lesson:
conditioning separation can solve contamination while creating composition fragmentation.

---

## Case 07 — ControlNet + regional area prompts

Source:
https://www.reddit.com/r/comfyui/comments/1jtt9mz

Pattern:
`generate/reference characters -> ControlNet -> regional area prompts -> different LoRAs -> inpaint`

Reported:
ControlNet + regional prompt improved character separation even at low control strength.

Lesson:
geometry scaffold + semantic locality can be more effective than asking regional text to solve geometry too.

Evidence:
COMMUNITY_PRACTICAL.

---

## Case 08 — Native characters smoother than character LoRAs

Source:
https://www.reddit.com/r/comfyui/comments/1pat0j1/how_to_get_multiple_characters_to_work_in_comfyui/

Observation:
user reports model-native booru characters integrate more smoothly than multiple character LoRAs.

Lesson:
LoRA is an extra global conditioning source; if the base knows the identity, native identity is an important control baseline.

---

## Case 09 — Anima multiple LoRAs fail while native identities work

Source:
https://www.reddit.com/r/StableDiffusion/comments/1tcf5y6/multiple_characters_using_loras_with_anima_model/

Pattern suggested:
- reduce adapter pressure
- build composition in Illustrious
- img2img/reconstruct in Anima

Lesson:
cross-model proxy/reference construction is a real workaround pattern, but belongs to assisted generation.

---

## Case 10 — Anima multi-LoRA bleed report

Source:
https://huggingface.co/circlestone-labs/Anima/discussions/202

Observed:
- side-by-side can work
- physical interaction degrades faster
- LoRA identity bleed / dominance

Lesson:
interaction workload is a separate stress level from coexistence.

---

## Case 11 — Six-character scaling failure

Source:
https://www.reddit.com/r/comfyui/comments/1wkh6if/how_to_generate_6_characters_in_a_single_image/

Observed:
more subjects -> identity loss / merge / lower face detail; Regional alone not sufficient for user.

Lesson:
subject count should be treated as workload escalation, not a small extension of two-subject success.

---

# C. Regional / spatial control

## Case 12 — Forge Couple

Source:
https://github.com/Haoming02/sd-forge-couple/blob/main/README.md

Mechanism:
different conditioning by region.
Current support includes Anima.

Author warning:
effectiveness depends on checkpoint composition understanding.

Lesson:
Regional provides locality, not semantic competence.

Evidence:
OFFICIAL_RUNTIME.

---

## Case 13 — Anima Regional Conditioning

Sources:
- https://github.com/Sen-sou/Comfyui-Anima-Regional-Conditioning
- https://note.com/hkmclab/n/n1526e44f4df9

Pattern:
`common/background -> character A mask -> character B mask -> sampler`

Tradeoff:
strong self-attention isolation can damage cross-region awareness.

Lesson:
separation and interaction must be scored independently.

---

## Case 14 — Anima LLLite Regional ControlNet

Sources:
- https://www.reddit.com/r/StableDiffusion/comments/1u3q7mn/regional_controlnet_for_anima/
- https://note.com/hirorohi03/n/nf5f99d66eb71

Pattern:
mask-driven Regional ControlNet.

Observation:
subject can leak mask bounds; stronger control may reduce leak.

Lesson:
mask locality itself has a strength/boundary tuning problem.

---

## Case 15 — Regional mask prompt for Illustrious/SDXL

Source:
https://github.com/dr1610/ComfyUI-Regional-Mask-Prompt/blob/main/README.md

Recommended:
- shared base prompt
- short per-region prompt
- feather boundaries
- pose/small body part handled by other controls

Lesson:
regional text is appropriate for large semantic zones, not precise pose/body-site geometry.

Evidence:
TOOL_DOC.

---

## Case 16 — MoonNodes advanced regional patching

Source:
https://github.com/m0rtus59/ComfyUI-MoonNodes

Mechanism:
early self-attention limitation + regional patching + mask UI.

Lesson:
current advanced regional workflows increasingly expose **when** separation applies, not only **where**.

Evidence:
TOOL_DOC.

---

# D. Reference / IP-Adapter / Edit

## Case 17 — Anima Character Reference controlled test

Source:
https://note.com/ai_on_desk/n/na2d11eeb39e3

Design:
- one reference image
- strengths 0 / 0.5 / 0.7 / 1.0
- multiple scenes
- outfit change
- multiple seeds
- 12 outputs

Observed:
- hair/face/eyes/major clothing transfer
- small mole/accessory less reliable
- outfit change possible while identity partly retained

Lesson:
reference identity has feature tiers; do not treat identity as one scalar.

Evidence:
CONTROLLED_PRACTICAL.

---

## Case 18 — One reference subject in a two-person scene

Source:
https://note.com/ai_on_desk/n/n6939918eef7f

Design:
40 images across strengths/seeds/scenes.

Observed:
- other subject stayed present
- unspecified attributes were filled from reference character
- background/time could also drift toward reference

Lesson:
reference conditioning may act as a prior for **unspecified fields** across the image.
When a second subject becomes a twin, add explicit counter-description before only lowering weight.

Evidence:
CONTROLLED_PRACTICAL.

---

## Case 19 — IP-Adapter identity + LLLite geometry

Source:
https://note.com/ai_on_desk/n/n95177c63c942

Design:
same-seed 8-way comparison.

Pattern:
- IP-Adapter -> face/identity
- lineart/LLLite -> pose/layout

Observed:
lineart also transferred hairstyle/accessories/clothes.
Masking/erasing head from geometry reference reduced unwanted transfer.

Lesson:
geometry controls can carry appearance information.
Preprocess the control image to remove attributes that should not propagate.

Evidence:
CONTROLLED_PRACTICAL.

---

## Case 20 — Anima IP-Adapter public node

Sources:
- https://github.com/Wenaka2004/comfyui-anima-ipadapter
- https://github.com/LuciferTC9527/ComfyUI-Anima_IP-Adapter

Mechanism:
reference embedding injected into Anima with strength and start/end range.

Lesson:
identity/reference is becoming a schedulable resource, not only a constant global condition.

Evidence:
TOOL_ECOSYSTEM.

---

## Case 21 — Anima Edit masked expression/local edit

Source:
https://www.reddit.com/r/StableDiffusion/comments/1twlu8c/anima_edit_with_turbo_lora_and_proper_masking/

Pattern:
`accepted image -> mask -> Anima Edit LoRA -> fast local regeneration`

Reported:
better identity preservation during local facial change than plain inpaint in user's tests.

Lesson:
editing an accepted image is a separate construction lane from regenerating the whole scene.

---

## Case 22 — Anima Edit background extension

Source:
https://www.reddit.com/r/StableDiffusion/comments/1uv4vpp/extend_image_image_edit_anima_edit/

Target:
background extension while preserving original composition.

Lesson:
specialized Edit LoRAs are appearing for narrow image-to-image transformations, reinforcing task-specific post-generation adapters.

---

## Case 23 — Forge Neo Anima-Edit / Cosmos Reference

Source:
https://note.com/hirorohi03/n/na72233a8d6a4

Pattern:
reference image + Anima Edit LoRA inside Forge Neo.

Lesson:
advanced reference/edit workflows are no longer ComfyUI-only.

---

# E. LoRA training / dataset workflow

## Case 24 — All-in-one Anima LoRA builder

Source:
https://www.reddit.com/r/StableDiffusion/comments/1t0yirq/built_a_3step_allinone_lora_builder_for_anima/

Pipeline:
`video -> shot split -> YOLO/CCIP character filter -> duplicate removal -> WD tags + local VLM caption -> manual audit -> train`

Lesson:
LoRA work is shifting toward **data pipeline engineering**, not manual folder+caption work only.

Critical boundary:
auto extraction/tagging still needs human nuisance/identity audit.

---

## Case 25 — Single multi-character LoRA with genuine joint examples

Source:
https://huggingface.co/circlestone-labs/Anima/discussions/220

Advice:
include genuine multi-character images; stitched panels can teach rigid separation.

Lesson:
interaction examples teach a different distribution from solo examples.

Exact dataset ratios remain anecdotal.

---

## Case 26 — Multiple single-character LoRAs trained with joint examples

Source:
https://huggingface.co/circlestone-labs/Anima/discussions/222

Claim:
joint images per variant can improve direct coexistence with separately trained LoRAs.

Boundary:
specific image-count sufficiency is not promoted.

Lesson:
coexistence may need to be represented during training, not solved only at inference.

---

## Case 27 — Anima LoRA overtraining / prompt-response degradation

Sources:
- https://huggingface.co/circlestone-labs/Anima/discussions/106
- https://huggingface.co/circlestone-labs/Anima/discussions/240

Observed:
- more training can increase style fidelity while reducing prompt response / increasing training-image imitation
- some users report trained LoRA responds better to detailed NL than simple tags

Lesson:
checkpoint selection must jointly score fidelity **and editability/prompt response**.

---

# F. Finishing / Hires patterns

## Finishing pattern 1 — Anima tiled/SEGS route

Source:
https://www.reddit.com/r/StableDiffusion/comments/1rye0p1/simple_anima_segs_tiled_upscale_workflow_works/

Pattern:
Anima + ImpactPack + tagger + tiled/local upscale.

Reason:
early Anima latent upscale instability.

---

## Finishing pattern 2 — Hires artifacts remain a current Anima issue

Sources:
- https://huggingface.co/circlestone-labs/Anima/discussions/42
- https://huggingface.co/circlestone-labs/Anima/discussions/53
- https://huggingface.co/circlestone-labs/Anima/discussions/204

Observed:
- latent upscale artifacts
- portrait/aspect-sensitive artifacts
- single-pass high upscale can break down
- tiled/multidiffusion routes used as alternatives

Lesson:
do not import SDXL Hires assumptions into Anima without comparison.

---

## Finishing pattern 3 — Upscale then detail

Source:
https://www.reddit.com/r/comfyui/comments/1sq0a1q/upscale_after_detailer/

Community default:
upscale first, face/detail pass afterward because upscale may alter face.

Boundary:
this is workflow advice, not a universal order for every model/defect.

---

# 1. 27 casesから見える6つの現在型

## Type 1 — Native-first
Use base model knowledge before LoRA.

Best when:
- model already knows character/concept
- simplest pipeline desired

Failure:
binding/load grows with subject count.

## Type 2 — Global LoRA stack
Fast and simple.

Best when:
- one subject
- compatible adapters
- low interaction complexity

Failure:
global adapter competition / style-identity bleed.

## Type 3 — Regional separation
Assign semantic resources by mask/area.

Best when:
- attributes leak across subjects
- large spatial zones are stable

Failure:
hard boundaries / disconnected interaction.

## Type 4 — Reference identity + geometry control
Identity comes from image reference; pose/layout from line/depth/control.

Best when:
- recurring OC
- no time to train LoRA
- exact pose matters

Failure:
reference/control sources can carry unwanted attributes.

## Type 5 — Accepted-base edit
First lock global scene, then edit.

Best when:
- composition/relation already good
- only identity/local area/background needs change

Failure:
edit can still drift relation/local geometry; re-audit after every edit.

## Type 6 — Data-first LoRA engineering
Improve the adapter itself.

Best when:
- recurring character/style
- multi-scene reuse
- inference tricks repeatedly fail

Failure:
dataset correlation/overtraining/context welding.

---

# 2. 成人向けで重要な実用結論

Adult relation-heavy work adds pressure to the same axes:

- actor identity
- target identity
- role
- body-site ownership
- exact count
- contact
- occlusion
- visibility
- local anatomy

Therefore the current expert workflow is usually **axis decomposition**, not one giant prompt.

A common high-control path is:

`minimal base scene`
-> `identity mechanism`
-> `geometry mechanism`
-> `regional separation if needed`
-> `relation audit`
-> `local edit/inpaint`
-> `Hires/detail`
-> `final relation audit`

---

# 3. New teaching rules

## Rule A — one control, one job

Teach each mechanism by primary responsibility:

- tags/NL -> semantics
- Character LoRA/native tag -> identity
- Regional -> locality/separation
- IP-Adapter/reference -> visual identity/style prior
- pose/line/depth -> geometry
- Edit/inpaint -> local reconstruction
- Hires/detailer -> finishing

A mechanism may affect other axes, but those are side effects to audit.

Promoted:
- K-PRACTICAL-035

## Rule B — erase irrelevant information from control sources

If lineart/reference/control image contains:
- wrong hair
- wrong accessory
- wrong clothing
- wrong object
and only pose/layout is desired,
mask/remove those regions/features where possible.

Promoted:
- K-PRACTICAL-036

## Rule C — reference blank-fill diagnostic

If a reference-conditioned multi-subject image turns unspecified traits of the other subject into the reference identity,
first add explicit attributes for the other subject and compare before assuming total subject takeover.

Promoted as CANDIDATE:
- K-TREND-007

## Rule D — interaction is a separate LoRA test

Test:
1. solo
2. coexistence
3. simple interaction
4. relation-heavy interaction

Do not infer interaction capability from solo fidelity.

Promoted:
- K-EVAL-022

## Rule E — Hires is currently especially model-specific for Anima

The 2026 community still reports Anima second-pass/latent-upscale artifact patterns.
Use the accepted base image as control and compare:
- pixel upscale
- tiled/multidiffusion
- second-pass latent/img2img

Promoted as CANDIDATE:
- K-TREND-008

---

# Promotion result

New ACCEPTED:
- K-PRACTICAL-035
- K-PRACTICAL-036
- K-EVAL-022

New CANDIDATE:
- K-TREND-007
- K-TREND-008

No exact community numeric recipe promoted.
