# Hard Fetish Generation Knowledge — Model-Family Matrix

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `DEEP_RESEARCH_V1`

## 1. Purpose

特殊・ハード系の知識を「Illustrious系なら全部同じ」で流用しないため、現在の主要familyごとに **exact fact / plausible implication / HOLD** を分離する。

## 2. WAI Illustrious v17

### Exact facts
Source: official v17 model card.

- SDXL / Illustrious-derived checkpoint
- Steps 15–30
- CFG 5–7
- Euler a
- original resolution area above 1024² recommended; examples include 1024×1344
- positive quality baseline `masterpiece, best quality, amazing quality`
- negative baseline `bad quality, worst quality, worst detail, sketch, censor`
- rating/safety tags include `general / sensitive / nsfw / explicit`
- author warns too many quality/aesthetic tags or overly long Negative can reduce quality/blur
- Hires workflow is documented and v17 specifically attempts to repair limbs/hands/feet.

### Hard-fetish implications — ADOPT as audit discipline
- unusual anatomy/count scenes must start from minimal exact author baseline rather than inherited giant Negative stacks;
- pre-Hires image is required evidence for anatomy/geometry claims;
- final Hires success can be `POSTPROCESS_RESCUE`;
- same-role camera/pose stacking should be treated cautiously due Illustrious composition conflict guidance.

### Hard-fetish implications — TEST_REQUIRED
- exact rare Special trigger response
- anal/body-site binding
- restraint topology
- sex-machine functional relation
- tentacle ownership/body-site relation
- multiple penetration/count ceiling
- exact advantage of broad + specific.

### Practical expectation
WAI has strong broad Booru vocabulary and adult illustration capability, but hard-fetish success should not be inferred from broad tag exposure. Relation and count are the dominant unknowns.

## 3. Illustrious XL baseline

### Exact/general facts
- Booru-oriented model family
- refined/multi-level captioning includes tag and natural-language information
- official guidance warns against overusing conflicting critical composition tags.

### Hard-fetish implications
- bag-of-independent-tags is not a sufficient mental model for relation-heavy scenes;
- a failed hard scene with `full body + close-up + cowboy shot`-like conflict is Prompt conflict before Special failure;
- downstream derivative behavior must be revalidated rather than inherited as exact Illustrious truth.

### HOLD
- exact relation ceiling by downstream checkpoint
- transferability of author camera guidance to each derivative
- rare current tag exposure.

## 4. NoobAI XL 1.1 EPS

### Exact facts
- trained on full Danbooru + e621 with native tag captions
- CFG 5–6
- Steps 25–30
- Euler a
- approximately 1MP SDXL resolutions
- caption organization: `count -> character -> series -> artists -> special tags -> general tags -> other tags`
- official examples contain SFW-oriented safety defaults.

### Hard-fetish implications — strong
- Special-before-General matches exact training/caption organization;
- e621 component may increase broad nonhuman/anatomy/fetish vocabulary exposure relative to pure-Danbooru assumptions;
- SFW `safe`/`nsfw negative` recipe must not be copied into adult hard-fetish stress evaluation.

### Important non-conclusion
`full Danbooru + e621` does NOT prove every current Special2788 phrase was an exact training token:
- tags can be renamed after cutoff
- Semantic terms may never have been exact tags
- aliases may have changed
- frequency can remain extremely low.

### TEST_REQUIRED
- canonical vs Alias response
- rare e621/Danbooru trigger choice
- actor-target/body-site relation
- multiple/count ceiling
- camera/visibility support position
- anatomy Negative effects.

## 5. NoobAI V-Pred 1.0

### Exact facts
- prediction regime is explicitly different from EPS
- CFG 4–5
- Steps 28–35
- Euler recommended/required by author guidance
- Special-before-General caption structure remains relevant.

### Hard-fetish implication
Never pool EPS and V-Pred hard-fetish outcomes without prediction-regime identity. A relation or anatomy failure under EPS cannot be counted as V-Pred evidence.

### Current evidence state
`MEDIUM / exact inference strong, hard-fetish practical weak`.

## 6. Anima Base / Aesthetic / Turbo

### Exact family facts
- tag + natural-language + mixed caption training
- language-model-based text encoder architecture
- lowercase tags; spaces preferred over underscores except score tags
- Gelbooru form preferred when Danbooru/Gelbooru forms differ
- random tag dropout: every related tag need not be present
- multiple-character prompting benefits from identifying characters and describing basic features
- Base/Aesthetic/Turbo differ materially
- Aesthetic strips quality tags in its fine-tuning; Turbo uses very different fast inference regime.

### Hard-fetish implications — strong candidates
Relation-heavy scenes can be represented as:
- learned tag anchor(s)
- concise factual actor/source/target/body-site relation description

This is especially relevant to:
- multi-actor ownership
- machine-device contact
- tentacle source/target
- restraint actor/resource relation
- fluid source/destination.

### But not universal truth
Community discussions show some subject combinations still fail stubbornly despite explicit descriptions, and strong concepts can bleed across subjects.

Therefore hybrid NL is a candidate intervention, not guaranteed repair.

### Prompt design discipline
- use explicit names/stable identifiers rather than pronouns in multi-actor tests;
- avoid unnecessary background/style prose when the audit target is relation-heavy;
- compare tag-only and concise-hybrid on same predetermined seeds;
- record profile (Base/Aesthetic/Turbo).

### TEST_REQUIRED
- hard relation success delta tag-only vs hybrid
- exact wording length/format
- multi-actor ceiling
- unusual anatomy vs Negative behavior
- rare Gelbooru/Danbooru trigger mapping.

## 7. WAI-ANIMA / downstream Anima derivatives

Current status: `PRACTICAL / FUTURE-CANDIDATE`, not a project-wide exact rule source.

Japanese migration reports indicate:
- WAI-Illustrious prompt habits do not transfer one-for-one to WAI-ANIMA;
- Qwen text encoding makes natural-language relation/layout more relevant;
- Forge Couple is used in practice for multiple characters;
- Hires/postprocess strategy can change due VRAM/workflow constraints.

Chinese secondary guidance likewise emphasizes assigning position/action to each subject and lowering conflict density.

Use only as hypothesis until exact checkpoint/version becomes a project target.

## 8. Cross-family hard-fetish transfer rules

### Safe to transfer as general mechanism
- relation != object presence
- rare concept != one-seed failure proof
- Negative is active intervention
- concept count increases composition burden
- LoRA/postprocess/control are confounds
- evaluator vocabulary/semantic reach must be checked.

### Not safe to transfer
- exact Prompt order
- exact quality prefix
- exact Negative list
- camera tag placement
- weighting strength
- Alias/trigger preference
- broad+specific benefit
- NL-vs-tag superiority
- precise simultaneous Special count ceiling.

## 9. Family-aware evidence key

Every hard-fetish image test should record:
- architecture/family
- exact checkpoint/version
- prediction regime
- model profile if applicable
- sampler/scheduler
- steps/CFG/resolution
- seed
- positive/negative actual Prompt
- LoRA/adapters + weights
- Hires/img2img/ADetailer/control state
- target Special ID/layer
- relation/count/body-site predicates.

Without these, evidence should be downgraded.

## 10. Priority family-specific research gaps

### WAI v17
1. body-site binding
2. restraint topology
3. machine functional relation
4. tentacle ownership
5. hard count / multi-Special
6. anatomy Negative ON/OFF.

### NoobAI EPS 1.1
1. rare/current trigger exposure
2. Alias/canonical
3. actor-target/body-site relation
4. exact camera/visibility support
5. count ceiling.

### Anima
1. tag-only vs concise hybrid for the same hard relation
2. stable-ID actor ownership
3. hard concepts under Base vs Aesthetic
4. strong-tag context bleed
5. multi-character resource separation.

## Sources

- WAI v17: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md
- Illustrious XL: https://huggingface.co/OnomaAIResearch/Illustrious-xl-early-release-v0
- Illustrious paper: https://arxiv.org/abs/2409.19946
- NoobAI XL 1.1 EPS: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- NoobAI V-Pred 1.0: https://huggingface.co/Laxhar/noobai-XL-Vpred-1.0/blob/main/README.md
- Anima: https://huggingface.co/circlestone-labs/Anima
- Anima multiple characters: https://huggingface.co/circlestone-labs/Anima/discussions/93
- Japanese WAI->ANIMA practical: https://note.com/nonb0716/n/nc7644494c360
- Korean Anima practical: https://onebrotravel.tistory.com/entry/ComfyUI-%EC%B4%88%EA%B0%84%EB%8B%A8-%EC%9E%85%EB%AC%B8%EA%B0%80%EC%9D%B4%EB%93%9C-%E2%80%94-Anima%EB%A1%9C-%EC%B2%AB-%EC%9D%B4%EB%AF%B8%EC%A7%80-%EC%83%9D%EC%84%B1
