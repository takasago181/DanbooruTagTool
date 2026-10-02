# BATCH_P — Community tag / Negative / runtime harvest — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Mode: controlled community evidence + current runtime documentation  
Status: no production behavior change

## Goal

Continue the broad individual-user harvest, but prioritize studies that preserve seeds, settings, sample counts or A/B structure. This batch focuses on the gap between canonical meaning and generation effect, Negative Prompt side effects, model-derivative instability, and current regional-prompt runtime behavior.

## 1. Anima sampler / CFG — 21-image user measurement

Source:
- Nora, 2026-09-28  
  https://note.com/stray_dog0012/n/n949c921640f8

Design:
- same character / prompt / random seeds / remaining settings;
- sampler and CFG changed;
- 21 generated images;
- image-line strength and detail-count measurements reported.

Reported:
- Euler a line strength 5.95 vs er_sde 6.86;
- detail measure 965 vs 1219;
- CFG movement from 6 -> 4 was only about 3–4% on the author's measures in this setup, much smaller than the sampler change.

Treatment:
- CANDIDATE only.
- Useful confirmation of the author's qualitative sampler description.
- Do not generalize “CFG does not matter”; target style/composition/profile can alter the outcome.

Promoted: K-COMM-ANIMA-007.

## 2. Compact tags vs descriptive English — 36 images

Source:
- Nora, 2026-09-26  
  https://note.com/stray_dog0012/n/naea7965570c5

Design:
- 6 categories: eyes / clothing / hair / camera / pose / lighting;
- tag vs descriptive-English pair;
- 3 repetitions per pair;
- same character/settings/random seed.

Reported:
- compact tags succeeded in all six tested categories;
- descriptive English succeeded in four;
- `weight` in a pose sentence was interpreted as a weight/barbell object;
- `light` in lighting wording produced a visible light-like object instead of the intended backlighting;
- `contrapposto` and `backlighting` avoided those failures in the tested prompts.

Treatment:
- evidence for lexical literalization risk, not “tags always beat language”.
- CANDIDATE.

Promoted: K-COMM-ANIMA-008.

## 3. Uniform-tag behavior — 194 images

Source:
- mono. works, 2026-09-13  
  https://note.com/tasty_cougar8018/n/nfc1d6a8cf973

Profile:
- Anima Aesthetic v1.1.
Method:
- garment tag added one at a time under fixed seed/base conditions;
- 15 overall forms + 55 components;
- 194 examples;
- initial entire run was repeated after the author noticed a style sentence was dominating the sparse-tag tests.

Notable reported examples:
- `school uniform` yielded shirt/skirt or blazer rather than sailor uniform in the shown eight samples;
- `sailor collar`, semantically a collar component, could trigger a full sailor-uniform prior;
- `white serafuku` did not necessarily color the entire uniform white;
- when explicit garment parts already defined the outfit, adding a broad parent label sometimes changed little;
- a strong style block could swamp single-tag effects enough to invalidate the first run.

Interpretation:
- canonical Danbooru semantics and learned generation effect must stay separate;
- narrow tags can invoke correlated whole-concept priors;
- parent/child semantic relations do not predict visual marginal effect;
- controlled tag behavior should be measured under representative prompt context.

Promoted: K-COMM-TAG-001.

## 4. Fisheye/perspective — 30-image fixed-seed study

Source:
- mono. works, 2026-08-17  
  https://note.com/tasty_cougar8018/n/n8264b41bc5fa

Profile/settings:
- Anima Aesthetic v1.1;
- er_sde/simple, CFG4, 30 steps, 1152×1536, shift 3.0;
- 5 scenes × 3 conditions × 2 seeds.

Conditions:
- no perspective block;
- existing Danbooru tags: fisheye / perspective / foreshortening;
- descriptive wide-angle / barrel-distortion natural-language block.

Reported:
- existing tags produced the stronger peripheral-distortion metric and the same directional result across the five scenes;
- the author's first test originally concluded the opposite because the fixed pose prompt already contained a strong perspective/exaggeration sentence;
- removing that confound reversed the result;
- `bad_perspective` in Negative had almost no measured effect in this particular test;
- excessively strong fisheye + barrel-distortion combination broke background structure in a separate batch.

Interpretation:
- candidate evidence for these exact tags/profile;
- more importantly, evidence that “fixed” prompt context can already contain the tested concept and reverse an A/B conclusion.

Promoted: K-COMM-TAG-002.

## 5. Negative Prompt — 12 fixed-seed pairs on WAI-Anima v1.0

Source:
- 机の上のAI, 2026-09-08  
  https://note.com/ai_on_desk/n/nfa078139f8c6

Environment:
- Windows 11 / RTX 5060 8GB;
- ComfyUI Desktop 1.0.46 / ComfyUI 0.34.0;
- WAI-Anima v1.0;
- euler_ancestral / normal;
- 30 steps / CFG4.5 / 832×1216;
- fixed seeds 3101–3104;
- baseline Negative held fixed, then one target Negative term added.

Reported:
- targeted concepts such as sparkles/star-like marks, blush and earrings could be reduced/removed in tested cases;
- `text` did not remove pseudo-text on signs in those samples;
- a Negative `hat` did not override an explicitly Positive requested hat;
- adding `glasses`, `hat`, or `earrings` when that object was absent still changed unrelated hair/clothes/body/composition;
- removing the baseline quality Negative stack sometimes changed overall composition without visibly lowering quality;
- hand negatives did not improve already-correct hands in the tested cases.

Interpretation:
- strongly consistent with existing K-NEG-001 principle that Negative is an active semantic intervention;
- does not close K-NEG-002 because this is WAI-Anima v1.0, a derivative, and sample size is limited.

Promoted: K-COMM-NEG-001.

## 6. Unknown/weak garment name vs structural description

Source:
- Nora, 2026-09-24  
  https://note.com/stray_dog0012/n/n7e5ff2f27a5b

Design:
- fixed character/full-body/plain background/black pants/boots/seed;
- six coat names, two attempts each;
- only coat wording changed.

Reported:
- trench/duffle/mods/down names worked in this setup;
- pea coat and chesterfield failed or drifted;
- removing the failed name and retaining structural features such as double-breasted/two rows of buttons or charcoal long coat produced closer target structure;
- color also shifted with the failed lexical item.

Interpretation:
- use as candidate evidence that an unlearned/weak label may interfere rather than act as a harmless unknown token.
- not a universal list of known/unknown garment names.

Promoted: K-COMM-PROMPT-001.

## 7. Derivative sensitivity — 72-image expression-tag comparison

Source:
- あおくま, 2026-09-24  
  https://note.com/ai_on_desk/n/ne6c1f6547d5b

Design:
- one expression tag changed;
- 12 expressions × 3 model conditions × 2 seeds = 72 images.

Reported:
- WAI-Anima changed mostly the expression while hair/orientation remained comparatively stable;
- Hakushi Mix Anima changed face direction/composition/hair brightness much more;
- removing Turbo LoRA did not remove most of the Hakushi instability.

Interpretation:
- strong reminder that “Anima behavior” cannot be inferred safely from one derivative;
- exact derivative identity must remain in evidence scope.

Promoted: K-COMM-ANIMA-009.

## 8. Dataset noise as a generation hypothesis

Source:
- Anima HF community discussion #201  
  https://huggingface.co/circlestone-labs/Anima/discussions/201

Reporter:
- developer of a Danbooru-style ViT tagger;
- reports manually cleaning roughly 2M tag assignments and maintaining a separate golden set.

Reported recurring label issues:
- missing tags;
- overlapping color boundaries;
- inconsistent long/very-long hair boundary;
- noisy continuous-size concepts forced into discrete buckets;
- bow/bowtie/ribbon/ascot/necktie confusion;
- character-dominated concept tags.

Treatment:
- useful high-priority failure hypotheses for Danbooru-trained generators and taggers;
- NOT direct evidence that the exact Anima training set has the same distribution/noise level;
- no canonical semantic change follows from this report.

Promoted: K-COMM-DATA-001.

## 9. Current Regional Prompter / Forge Neo / Anima support

Primary runtime source:
- hako-mikan/sd-webui-regional-prompter README, update 2026-09-04  
  https://github.com/hako-mikan/sd-webui-regional-prompter/blob/main/README.md

Current documented matrix:
- Anima Latent: supported;
- Anima Attention: supported;
- Anima Region LoRA: unsupported.

Important mechanism notes:
- Anima/Z-Image/Krea2 are not processed as SD/SDXL 75-token chunks;
- region prompts are encoded separately;
- Anima-specific Attention mode masks cross-attention and only penalizes self-attention early in the schedule, then removes masking so regions can knit together;
- Region LoRA currently relies on U-Net-style block names and therefore does nothing on Anima.

This is runtime documentation, not anecdote.

Promoted: K-TOOL-011 as ACCEPTED.

## Other community findings preserved but not promoted

### Multi-character LoRA competition
Reddit and HF reports repeatedly describe identity blending or one LoRA dominating when two character LoRAs are combined on Anima. Already represented by BATCH_O K-COMM-ANIMA-005; no duplicate Claim added.

### Upscale artifacts
HF discussion #204 and Reddit reports describe strange noise/pattern artifacts on second-pass Anima upscaling and conflicting workarounds (smaller factor, tiled/multidiffusion, different upscaler, altered denoise). Already represented by K-COMM-ANIMA-006; exact thresholds remain recipe-specific.

### Anima regional control
Community Anima LLLite Regional ControlNet reports are promising, including one user claiming extensive two-character success, but sample-level evidence is too weak for a general effectiveness Claim. Runtime availability is already covered separately.

## Durable methodological lesson

Community tests are most valuable when they publish:
- exact profile/checkpoint;
- exact runtime/settings;
- fixed prompt components;
- changed variable;
- seed count;
- failure cases;
- reruns after discovering confounds.

A 30-image test that finds and corrects its own confound is more useful than hundreds of showcase images with bundled setting changes.

## Promotion result

New CANDIDATE:
- K-COMM-ANIMA-007
- K-COMM-ANIMA-008
- K-COMM-TAG-001
- K-COMM-TAG-002
- K-COMM-NEG-001
- K-COMM-PROMPT-001
- K-COMM-ANIMA-009
- K-COMM-DATA-001

New ACCEPTED runtime:
- K-TOOL-011

No existing HOLD closed.
