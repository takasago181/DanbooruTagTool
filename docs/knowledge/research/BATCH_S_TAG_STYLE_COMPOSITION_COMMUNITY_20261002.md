# BATCH_S — Tag / style / composition community experiments — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Mode: controlled public-user experiment harvest  
Focus: style surfaces, step convergence, framing tags, Prompt dialect, multi-character grouping, quality/meta effects

## 1. 108-style same-seed Anima comparison

Source:
- おーら, 2026-07-12  
  https://note.com/ai_0049/n/n74ccab5370e0

Method:
- Anima Base v1 template workflow;
- fixed seed `482971048579284`;
- minimal base prompt;
- swap one style phrase at a time;
- 108 style phrases visually evaluated.

High-value methodological result:
- “did the image change?” and “did the named style reproduce correctly?” are different questions.
- several style phrases made large changes but in the wrong semantic direction;
- some different labels converged to near-identical generic outputs;
- some style phrases altered not just rendering but hair, clothes, props, background and pose;
- tags strongly tied to color/motif often showed clearer effects than abstract technique labels in this particular prompt/profile;
- the author had to simplify the base prompt because complex scene content hid weaker style effects.

Treatment:
- the article's subjective top-10 ordering is not copied into project authority;
- the durable finding is the separation of **effect strength** from **semantic fidelity**.

Promoted:
- K-COMM-STYLE-001.

## 2. Anima Base step sweep 5–40

Source:
- メキメキニート, 2026-07-10  
  https://note.com/nobrain/n/ncc77e7c3452b

Environment:
- RTX 5070 12 GB
- Anima Base v1.0
- Qwen3 0.6B encoder
- Qwen-Image VAE
- no LoRA
- er_sde / simple / CFG4
- 1024×1024
- fixed seed
- steps 5,10,15,20,25,30,35,40

Reported:
- VRAM ~8.1 GB from 10–40 steps in that workflow;
- elapsed time increased near-linearly after initial overhead;
- image was visibly underdeveloped at 5;
- gross line/composition stabilized around 15–20;
- later steps mainly changed fine hair/clothing texture, with a visible detail jump reported around 35.

Treatment:
- one seed / one simple prompt, so no global optimal-step conclusion;
- useful for separating “structural convergence” from “detail finishing”.

Promoted:
- K-COMM-ANIMA-011.

## 3. Composition framing: tags vs natural language

Source:
- mono. works, 2026-07-20  
  https://note.com/tasty_cougar8018/n/n713f5a8c1218

Environment:
- Anima-derived novaAnimeAM_v30
- 832×1216
- er_sde / simple / CFG4 / 30 steps
- character/scene held constant
- only framing representation changed.

Reported:
- face close-up: `close-up, face focus` produced a tighter crop than an English close-up sentence;
- bust-up/full-body: little difference between tag and NL in the shown comparison;
- when prompt also described walking barefoot, footprints and ground, close-up became wider;
- removing feet/ground descriptions made close-up obey more strongly.

Treatment:
- reinforces K-PROMPT-003 and support/anti-support logic;
- scope is one derivative and a limited number of framing comparisons.

Promoted:
- K-COMM-ANIMA-012.

## 4. Importing Illustrious Prompt habits into WAI-Anima

Source:
- あおくま, 2026-09-09  
  https://note.com/ai_on_desk/n/n72f6f4e58dfe

Environment:
- ComfyUI Desktop 1.0.46 / core 0.34.0
- WAI-Anima v1.0
- euler_ancestral / normal
- 30 steps
- 832×1216
- fixed seeds
- automatic quality/Negative additions disabled.

One-variable comparisons included:
- WAI quality tags;
- Noob-style quality block;
- WAI Negative terms;
- long generic Negative block;
- CFG7;
- underscore notation;
- emphasis `(red bow:x)`;
- `BREAK`.

Reported:
- all imported quality/Negative/CFG/underscore habits changed output;
- underscores produced one of the largest measured pixel differences in this setup;
- weights 1.4 and 1.8 barely changed tested ribbon size; 3.0 changed it visibly; 0.3 still left the ribbon and changed other clothing;
- `BREAK` changed the image but did not behave like the intended A1111-style semantic separator in the tested ComfyUI Anima path.

Important caution:
- article's implementation explanation must be verified against exact ComfyUI code/version before promotion as mechanism fact;
- observations are still useful as scoped behavioral evidence;
- official Anima guidance already independently supports spaces rather than underscores and stronger weighting than typical SDXL.

Promoted:
- K-COMM-ANIMA-013.

## 5. 48-image two-character grouping comparison + three-character extension

Source:
- 机の上のAI, 2026-09-14  
  https://note.com/ai_on_desk/n/n462ad57df450

Environment:
- Windows 11 / RTX 5060 8GB
- ComfyUI 0.34.0
- WAI-Anima v1.0
- 30 steps / CFG4.5
- both 832×1216 and 1216×832
- fixed quality/Negative
- no LoRA/reference
- original characters using tags.

Two-character design:
- same black hair to prevent easy color separation;
- distinguish by eyes, hairstyle, skin, accessories and clothes;
- 4 grouping schemes:
  1. positional labels;
  2. names;
  3. relative clauses;
  4. foreground/background;
- tags-only vs one English sentence;
- 3 seeds × portrait/landscape = 48 main images.

Reported tags-only:
- positional labels: 6/6;
- names: 0/6;
- relative clauses: 0/6;
- foreground/background: 3/6.

With subject-specific English sentence:
- all four schemes: 6/6.

Fragility test:
- replacing left/right labels with A/B or first/second, removing `girl`, removing colon, or swapping content caused failures in 15 additional images.

Three-character extension:
- positional tags-only kept count/position but leaked center girl's eye/skin to left in 5/6;
- adding one sentence per character: 6/6 correct by the author's visual criterion.

Treatment:
- high-value C1 community evidence;
- not universal grammar because it is one derivative/runtime, visual scoring and limited seeds;
- directly supports subject-specific binding sentences as a strong test candidate.

Promoted:
- K-COMM-ANIMA-014.

## 6. Quality/meta surfaces and default-face prior

Source:
- 机の上のAI, 2026-09-07  
  https://note.com/ai_on_desk/n/na0edcfbebe28

Environment:
- WAI-Anima v1.0, same seed/settings across conditions;
- broad tendency reportedly rechecked on Aesthetic v1.1.

Conditions:
1. baseline;
2. remove quality tags/default negatives;
3. add `safe`;
4. add explicit face descriptors.

Reported:
- removing `masterpiece, best quality, score_7` changed eye/mouth/hair/body/rendering;
- `safe` left the face closer to baseline in that run;
- explicit face descriptors changed identity strongly.

Treatment:
- does not prove a single universal “default face mechanism”;
- useful evidence that quality/meta surfaces can alter face/rendering priors, consistent with K-QUALITY-001.

Promoted:
- K-COMM-QUALITY-002.

## 7. Artist/style tag derivative variability

Sources:
- nobin, 2026-05-02 / 2026-09-22  
  https://note.com/nobinlog/n/n98276b4f2596  
  https://note.com/nobinlog/n/n9f99606a81dd

Reported:
- same artist/style surfaces produce different strength/direction across Anima derivatives;
- LoRA sometimes used to stabilize a target style when tag-only effect varies.

Treatment:
- source-map only;
- official/model-specific artist trigger guidance remains higher authority;
- no Claim because controlled details are insufficient and style-fidelity scoring is subjective.

## Durable design implication for DanbooruTagTool

Future “generation behavior” metadata should distinguish at least:
- **semantic identity** — what the tag means canonically;
- **activation/effect strength** — how much output changes when added;
- **semantic fidelity** — whether the change actually matches the intended tag meaning;
- **spillover scope** — whether it changes unrelated pose/clothes/background/identity;
- **context sensitivity** — whether other Prompt content suppresses or reverses the effect;
- **profile/version scope**.

A one-dimensional “effective / ineffective” flag is not sufficient.

## Promotion result

New CANDIDATE:
- K-COMM-STYLE-001
- K-COMM-ANIMA-011
- K-COMM-ANIMA-012
- K-COMM-ANIMA-013
- K-COMM-ANIMA-014
- K-COMM-QUALITY-002

No HOLD closed.
