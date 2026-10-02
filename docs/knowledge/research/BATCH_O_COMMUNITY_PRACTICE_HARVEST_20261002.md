# BATCH_O — Community practice harvest — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Mode: public-user/community evidence harvest  
Scope: Anima / WAI-Anima / Illustrious / NoobAI / Forge Neo / LoRA / multi-character / finishing

## Purpose

Collect large amounts of practical information from individual users without flattening anecdotes into facts.

Evidence handling in this batch:
- **C1 controlled community test** — fixed seeds/conditions or explicit A/B structure; useful CANDIDATE evidence.
- **C2 repeated independent observation** — same failure pattern appears in multiple unrelated reports.
- **C3 single-user recipe** — preserved as a hypothesis/recipe only.
- **C4 opinion/showcase** — discovery value only; not promoted.

No community claim here overrides official author guidance, canonical Danbooru semantics, or project HOLD rules.

## Strong community evidence harvested

### 1. Anima multi-character binding: grammar beats flat tag lists in controlled tests

Source:
- Nora, 2026-09-08, 16-image four-condition fixed-seed comparison  
  https://note.com/stray_dog0012/n/n74ad8ac4582f

Design:
- A: flat tags, no colon
- B: natural language, no colon
- C: natural language, colon
- D: flat tags, colon
- same four seeds across all conditions
- scored accessory/ear/color leakage

Reported totals, lower = less leakage:
- A 13
- B 2
- C 2
- D 10

Practical interpretation:
- in that setup, natural-language character sentences mattered far more than colon separators;
- colon/left-side syntax should not be treated as a magic binding operator;
- attributes should be closed into a subject-specific sentence;
- split-panel failures remained separable from attribute-leakage failures.

Evidence: **C1**.  
Promoted as K-COMM-ANIMA-001 / 004, still CANDIDATE because exact checkpoint identity is not pinned in the article extract and replication is absent.

### 2. Anima tag vs natural language: 256-image comparison

Source:
- mono. works, 2026-09-22  
  https://note.com/tasty_cougar8018/n/na0979098fa50

Profile/settings explicitly reported:
- Anima Aesthetic v1.1
- er_sde / simple
- CFG 4
- 30 steps
- 1152×1536
- fixed prompt prefix/negative/LoRAs within each comparison
- 256 images total

Four surfaces:
1. tags only
2. natural language only
3. mixed by element
4. all useful tags + short supplementary sentences only where tags are insufficient

Second-round totals:
- tags only 740 / 896
- natural language 748 / 896
- mixed 746 / 896
- tags + supplementary sentences 781 / 896

Average visual quality:
- tags only 3.95
- natural language 3.68
- mixed 3.79
- tags + supplementary sentences 3.82

Broken images:
- tags only 4
- natural language 9
- mixed 6
- tags + supplementary sentences 3

Scene-level behavior:
- unusual pose topology (backward chair straddle, precise arm direction) improved when expressed in sentences;
- screen-left/screen-right object placement required sentence-level location wording where no equivalent Danbooru tag existed;
- simple standing portrait/clothing/accessory scenes favored tags-only in this sample;
- natural-language-only was not a universal winner.

Evidence: **C1**.  
Promoted as K-COMM-ANIMA-002.

### 3. Multi-character leakage pattern: core traits vs local accessories

Sources:
- HKMC_AILab, 2026-06-06  
  https://note.com/hkmclab/n/n7611426be16a
- Nora controlled 16-image test above
- Reddit multi-character Anima reports  
  https://www.reddit.com/r/StableDiffusion/comments/1r336og/multiple_characters_using_anima_2b/  
  https://www.reddit.com/r/StableDiffusion/comments/1wr9r66/anima_two_characters_work_fine_individually_but/  
  https://www.reddit.com/r/StableDiffusion/comments/1tepgn4/sharing_my_experience_with_anima_comfyui_great/

Repeated pattern:
- hair/eye/skin/basic silhouette often bind more reliably;
- earrings, tiaras, necklaces, face paint, ears or other local features leak more readily;
- direct interaction increases difficulty;
- natural-language identity+appearance grouping often helps but does not guarantee separation.

Evidence: **C1 + C2**.  
Promoted as K-COMM-ANIMA-003.

### 4. Spatial wording can create a different failure: panel splitting

Sources:
- Nora 2026-06 / 2026-09 tests  
  https://note.com/stray_dog0012/n/n6576baad72c1  
  https://note.com/stray_dog0012/n/n74ad8ac4582f
- Anima Hugging Face discussion  
  https://huggingface.co/circlestone-labs/Anima/discussions/86

Observed:
- wording such as `left side of the image` can sometimes be interpreted like a separate panel/region rather than one shared scene;
- attribute separation and image-panel splitting are different failure axes;
- relationship/action wording between characters may help keep one scene in some community tests.

Evidence: **C1 + C2**, exact frequency unknown.  
Promoted as K-COMM-ANIMA-004.

### 5. Multiple character LoRAs can compete

Sources:
- Reddit  
  https://www.reddit.com/r/StableDiffusion/comments/1tcf5y6/multiple_characters_using_loras_with_anima_model/  
  https://www.reddit.com/r/StableDiffusion/comments/1wr9r66/anima_two_characters_work_fine_individually_but/

Reported failure modes:
- one LoRA dominates;
- identities blend;
- character appears on wrong side;
- area conditioning separates identities better but overlap zones can damage faces/hands.

Reported mitigations:
- reduce LoRA strengths;
- more explicit actor/position wording;
- area/regional conditioning;
- staged composition + img2img.

Do **not** promote reported numeric LoRA strengths as universal.

Evidence: **C2/C3**.  
Promoted as K-COMM-ANIMA-005.

## Prompt structure / composition observations

### 6. NoobAI V-Pred count wording test

Source:
- robai104, 2025-02-09  
  https://note.com/robai104/n/na0fb1ae3bc6b

Environment explicitly reported:
- `noobaiXLNAIXL_vPred10`

Author's observations:
- roughly three subjects were comparatively stable;
- four+ became harder to count reliably;
- connected forms such as `1boy and 1girl` / `with` worked better than some separated alternatives in their testing;
- `side-by-side`, `face-to-face`, etc. were useful relationship/layout cues.

Evidence: **C1-ish single-user test**, but sample size and seed design not fully reported.  
Promoted as K-COMM-NOOB-001 only as CANDIDATE.

### 7. Illustrious/Noob multi-character regional practice

Sources:
- Reddit Illustrious prompting discussion  
  https://www.reddit.com/r/StableDiffusion/comments/1j50o89
- broader multi-character discussion  
  https://www.reddit.com/r/StableDiffusion/comments/1l75afz
- Japanese community experience  
  https://note.com/sd_space/n/n3407ee77a43e

Repeated practice:
- natively known identities can often be generated together;
- distinct outfit/attribute ownership becomes the hard part;
- regional prompting is frequently recommended when plain prompting starts mixing properties.

Evidence: **C2**.  
Promoted as K-COMM-ILL-001.

## Anima finishing / upscale observations

Sources:
- Reddit Forge Neo Anima settings  
  https://www.reddit.com/r/StableDiffusion/comments/1t87xbc/anima_settings_in_forge_neo/
- high-resolution artifact discussion  
  https://www.reddit.com/r/StableDiffusion/comments/1syfirz/is_there_a_way_to_fix_this_anima/
- Anima showcase/refinement notes  
  https://www.reddit.com/r/StableDiffusion/comments/1tmrh0l/the_not_so_anime_anima/

Repeated reports:
- aggressive Hires/upscale can introduce grain/blur/grid-like patterning or change structure;
- some users prefer lower scale factors and low-denoise img2img/tiled passes;
- sampler choice during img2img can materially change smearing/smoothness;
- exact threshold depends on checkpoint/profile/VAE/upscaler/runtime.

Evidence: **C2**.  
Promoted as K-COMM-ANIMA-006. No numeric threshold promoted.

## LoRA training observations

### 8. Dataset diversity vs concept welding

Sources:
- Illustrious training discussion  
  https://www.reddit.com/r/StableDiffusion/comments/1r318l/helpquestion_sdxl_lora_training_on_illustriousxl/
- Windows Illustrious LoRA guide  
  https://zenn.dev/bananaotoko/articles/3ec0f02e900725
- WAI vs Anima same-dataset report  
  https://zenn.dev/ojisan_ai_lab/articles/lora-wai-anima-howto-20260722
- Anima character-LoRA questions  
  https://www.reddit.com/r/StableDiffusion/comments/1wela3n/questions_about_training_a_character_lora_for/

Repeated lesson:
- small or compositionally narrow datasets can weld pose/background/clothing/style into identity;
- viewpoint, crop, pose, clothing and background variation are practical anti-entanglement measures;
- caption strategy determines what remains associated with the trigger.

Evidence: **C2**.  
Promoted as K-COMM-LORA-001.

### 9. Style LoRA captioning remains unsettled

Sources:
- Reddit Anima style-LoRA discussion  
  https://www.reddit.com/r/StableDiffusion/comments/1tdobjq/anima_loras_cant_learn_the_characters_style_no/
- recent tagging discussion  
  https://www.reddit.com/r/StableDiffusion/comments/1wq972q/training_a_style_lora_for_anima_a_few_tagging/
- Japanese Anima LoRA deep-dive  
  https://note.com/studiomasakaki/n/nf39775327336
- auto-tag vs manual-tag experiment  
  https://note.com/azrakuc/n/n3d6d5eaa850e

Community disagreement:
- some users report good style capture with very sparse captions/explicit style triggers;
- others use richer tags/NL captions;
- when dropout is used, keeping the style trigger is common advice;
- there is no accepted project recipe for style-LoRA caption density.

Evidence: **C2 with disagreement**.  
Promoted as K-COMM-LORA-002, still CANDIDATE.

### 10. Anima training-timestep parameters deserve their own test axis

Source:
- 久遠ノイズ, 2026-08-11  
  https://note.com/kuon_noise/n/na40804c255b5

The author highlights `sigmoid_scale` / `discrete_flow_shift` as important Anima LoRA training variables and notes prior GUI misconfiguration.

Treatment:
- preserved as a research lead, **not promoted** to a Claim yet;
- needs source-code/trainer confirmation + controlled dataset comparison.

## Style / artist consistency observations

Sources:
- Reddit artist-mix experiment  
  https://www.reddit.com/r/StableDiffusion/comments/1tj2rcl/stabilizing_mix_of_artist_tags_in_anima/
- Reddit seed/style variability discussion  
  https://www.reddit.com/r/StableDiffusion/comments/1tiu6kc/the_main_downside_with_anima_is_that_its_almost/

Community reports:
- Anima can vary style strongly across seeds;
- `@` prefix is repeatedly rediscovered as important (already official);
- stronger block weights are used by some practitioners (already consistent with official guidance that Anima weighting may need stronger values);
- exact shift/weight recipes remain user-specific.

No new Claim promoted because official K-MODEL-ANIMA-007 already covers the durable part.

## Runtime / regional findings

### Regional Prompter current support
Source:
- https://github.com/hako-mikan/sd-webui-regional-prompter

As of 2026-09-04:
- Anima Latent mode supported;
- Anima Attention mode supported;
- Region LoRA mode unsupported for Anima;
- prompt chunk assumptions differ from SD/SDXL.

This is stronger than ordinary community evidence because it is runtime documentation. It should be considered in a future official-runtime batch rather than mixed into community claims.

### Forge Couple
Already promoted in BATCH_N:
- Anima support;
- total-subject-count recommendation;
- preprocessor compatibility concerns;
- Hires pass may disable Couple.

## Chinese-language harvest

Sources:
- Illustrious LoRA user build/report  
  https://www.bilibili.com/opus/1181478497372078082
- Anima + Illustrious + LoRA workflow showcase  
  https://www.bilibili.com/video/BV1mk5f6UEaq/
- NoobAI author/community explainer clips  
  https://www.bilibili.com/video/BV1CYCAYFE2a/  
  https://www.bilibili.com/video/BV1DCkCYDE5v/
- Forge Neo Anima package/workflow community  
  https://www.bilibili.com/video/BV1HJXKBJEge/

Useful leads:
- Illustrious-trained LoRAs are often tested cross-derivative and on Noob, but authors themselves warn strength/CFG adjustment is required and compatibility is not guaranteed;
- current Chinese community workflows frequently combine Anima with prior Illustrious assets through staged/img2img or retrained-LoRA workflows;
- these are preserved as ecosystem observations, not compatibility facts.

## Japanese-language harvest

Additional sources:
- Anima 3-person consistency experiment  
  https://note.com/ulyssesx00/n/n8f6a2c961e7c
- Anima LoRA 7-way comparison  
  https://note.com/stray_dog0012/n/n21534228bbfd
- Illustrious prompt failure / >100 image learning diary  
  https://note.com/nifty_dunlin2337/n/n9fdf86bfe92c
- Illustrious-to-Anima style LoRA migration, ~80 images  
  https://note.com/rockey2799m/n/n05159f2fcc96
- Anima character LoRA material-selection example, 60/773 curated images  
  https://note.com/tasty_cougar8018/n/nbdb27a6b7b6d
- Anima 2.9B comparison  
  https://note.com/akirau338/n/n04964cbb2904

Treatment:
- preserve exact environment/sample size when known;
- do not turn paid-article teaser claims into accepted facts;
- use these to design future controlled tests.

## Conflicts / cautions discovered

1. **Natural language is not always better.**  
   Controlled 256-image evidence argues for task-dependent composition: tags remain strong for canonical attributes/common poses; supplementary sentences add value for geometry/relations not encoded well by tags.

2. **Left/right syntax is not a magic separator.**  
   One controlled test found colon separators irrelevant once grammar was explicit.

3. **Community recipes frequently bundle multiple variables.**  
   CFG, sampler, shift, weight, LoRA, resolution and Negative often move together. Those recipes are not causal evidence.

4. **LoRA style-training advice conflicts.**  
   Sparse-caption and detailed-caption camps both report success. Dataset and target concept likely dominate.

5. **Cross-family LoRA compatibility is highly variable.**  
   Successful load ≠ faithful concept transfer.

6. **Negative stacks are especially confounded.**  
   Many community examples use large generic negatives; this batch does not use them to close K-NEG-002.

## Suggested local experiments from this harvest

Highest value, low image count:
1. Anima Aesthetic v1.1: tags-only vs tags+supplementary sentence on 4 scene families × fixed 4 seeds.
2. Anima Base/Aesthetic: two-character core-trait vs accessory binding, 4 seeds.
3. Noob EPS: count wording `2girls` vs `two girls` vs linked relational phrase, 4 seeds.
4. Anima: base pass vs low-denoise img2img finishing on the same source, sampler held fixed.
5. One character LoRA + one style LoRA: 0/A/B/A+B at two weights, fixed seeds.

## Promotion result

Added 10 new CANDIDATE Claims:
- K-COMM-ANIMA-001..006
- K-COMM-LORA-001..002
- K-COMM-NOOB-001
- K-COMM-ILL-001

No HOLD was closed.

## Boundary

Public user reports are harvested aggressively for discovery, but:
- usernames are not treated as authority credentials;
- follower/upvote count is not evidence quality;
- one recipe is not a default;
- public examples do not become canonical semantic facts;
- production behavior remains unchanged.
