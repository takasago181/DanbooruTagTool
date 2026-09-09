# Persistent Generation Knowledge Corpus

Owner: Issue #44 `[KNOWLEDGE][ONGOING] Persistent generation knowledge corpus for dictionary audit and Stage10`

Status: ONGOING / evidence corpus

This document consolidates durable generation knowledge for future dictionary audit, Prompt review, Stage10 design and failure diagnosis.

It is not a production specification. Model-family observations remain scoped. HOLD stays HOLD until evidence resolves it.

---

# 1. Evidence discipline

## 1.1 Claim classes

Use these labels whenever a claim can affect an audit or Prompt rule.

### FACT_EXACT_MODEL
Exact checkpoint/version information from the author/model card/repository or exact-version controlled evidence strong enough to support the stated claim.

### FACT_GENERAL
Primary research or mechanism evidence that is broadly useful but does not define exact settings for one checkpoint.

### CONTROLLED_PRACTICAL
A practical test with enough control to isolate a meaningful variable: same model/settings/seed where possible, exact Prompt/settings shown, only the tested factor changed.

### PRACTICAL
Useful real-world evidence but with weaker controls, small samples, or multiple changing variables.

### COMMUNITY
Community observation. Useful to generate hypotheses or identify likely failure modes, not to certify production rules.

### HOLD
Evidence is missing, conflicting, model-scope is unclear, or image testing is required.

### REJECT
A proposed universal rule is contradicted by stronger evidence, conflates separate concepts, or is too unsafe to use as a default.

## 1.2 Authority order

For exact model behavior:

1. exact checkpoint/version author information
2. author/team statement for same family/version
3. exact-version controlled practical test
4. primary research for mechanism/risk
5. practical corroboration
6. community observation
7. hypothesis

A broad paper can justify why a failure mode is plausible, but cannot define WAI v17 or NoobAI 1.1 exact Prompt grammar unless the paper actually studies that model.

## 1.3 Multilingual rule

Do not treat English as the only serious evidence language.

Actively use Japanese, English, Chinese and Korean sources when they contain useful exact-model or controlled practical evidence.

Evidence rank depends on source authority and experimental quality, not language.

A Japanese same-seed one-variable comparison can be more useful than an English community assertion. It still does not outrank an exact author model card when they conflict.

---

# 2. Core identity separations

## 2.1 Canonical identity vs model trigger

`FACT_GENERAL / audit invariant`

The database canonical tag is a semantic identity. A model trigger is a surface form that happens to activate the learned concept in a particular model.

These are not automatically the same thing.

Consequences:
- never rewrite the canonical merely because another spelling generates better;
- model-specific trigger spelling belongs in Generation/Profile knowledge, not canonical authority;
- Alias -> canonical dictionary equivalence does not prove equal model response;
- Japanese display/search wording does not certify model response;
- model response does not by itself redefine canonical meaning.

Anima gives an especially clear example: the author advises preferring the Gelbooru form when Danbooru and Gelbooru tags differ. This is a model-facing rule, not a reason to replace the database canonical.

## 2.2 Special identity vs support

`audit invariant`

A tag can help the model show or stabilize a Special without being part of the Special's intrinsic definition.

Keep at least these support classes separate:

1. **Meaning support** — constituent/semantic support required to express the concept
2. **Geometry / Kinematic support** — body/object geometry needed to make the relation physically possible
3. **Visibility support** — framing/viewpoint/focus needed to observe the intended result
4. **Resource parking / disambiguation** — assigns hands/arms/objects/actors to reduce binding conflicts
5. **Aesthetic support** — style/lighting/expression/background that improves practical output but not semantic identity
6. **Redundant decoration** — not measurably needed for meaning or observation

Audit rule:
- do not promote frame/viewpoint tags to CORE meaning just because they improve success rate;
- do not treat requirement metadata as an automatic support-insertion command;
- do not treat statistically common co-occurrence as semantic necessity.

## 2.3 Prompt-only vs assisted-control

`FACT_GENERAL`

Prompt-only evidence and spatially assisted evidence are different lanes.

Assisted control includes, depending on workflow:
- ControlNet / OpenPose
- regional prompting / Forge Couple
- pose maps / depth / segmentation
- targeted img2img/inpaint
- ADetailer when its pass materially edits the target

If a target succeeds only under assisted control, that is useful product evidence, but it does not prove Prompt-only reliability.

---

# 3. Model-family exact knowledge

# 3.1 WAI Illustrious v17

## Exact author settings

`FACT_EXACT_MODEL`

Source: `S-WAI-001`

- Steps: 15-30
- CFG: 5-7
- Sampler: Euler a
- author recommends original dimensions larger than the 1024x1024 area; example images use 1024x1344
- example quality prefix: `masterpiece, best quality, amazing quality`
- example Negative: `bad quality, worst quality, worst detail, sketch, censor`
- author warns that too many quality/aesthetic tags and overly long Negative prompts can reduce quality and make output blurrier
- documented Hires example: 1.5 upscale, 20 Hires steps, R-ESRGAN 4x+ Anime6B, denoise 0.35-0.5
- v17 explicitly says Hires Fix was improved to correct limbs and can automatically fix arms/legs/hands/feet with high probability

## Audit consequences

### Quality is not a transparent quality switch

`FACT_EXACT_MODEL + PRACTICAL corroboration`

Do not interpret `masterpiece/best quality/amazing quality` as a pure detail multiplier.

Quality/meta tags are learned image-distribution labels and may correlate with:
- composition
- face shape
- clothing
- color treatment
- camera proximity
- style

Therefore:
- compare quality profile as an experimental variable when semantics are sensitive;
- do not stack generic `8k / ultra detailed / sharp focus / very aesthetic` as a universal default;
- if a Special succeeds only after a large quality stack, do not assume the quality stack is semantically neutral.

Japanese practical evidence (`S-JA-001`) supports the risk that quality tags can change visual structure, not only fidelity.

### Hires is a confounder

Because the author explicitly describes limb correction by Hires:
- final Hires image cannot certify base-pass anatomy correctness;
- for anatomy/limb-related Special evaluation, base image and post-Hires image are different evidence states;
- if only the post-Hires result succeeds, record `POST_PROCESS_RESCUE` rather than `BASE_PROMPT_SUCCESS`.

### WAI v17 exact Negative boundary

The small author example does not include `bad anatomy`, `extra limbs`, or `extra arms`.

Therefore:
- broad anatomy negatives are not exact-v17 mandatory defaults;
- unusual-anatomy/count-changing Specials under broad anatomy negatives are HIGH-risk;
- absence of a Special under an overlapping negative is not evidence that the Special is weak.

## WAI v17 unresolved

`HOLD`

- exact optimal placement/order of frame/viewpoint support
- exact reaction to rare Special aliases or newly renamed Danbooru forms
- universal benefit of broad+specific support
- exact prompt-density breakpoint
- exact multi-Special breakpoint

---

# 3.2 Illustrious XL early release / family baseline

## Official composition guidance

`FACT_EXACT_MODEL`

Source: `S-ILL-001`

Illustrious official examples and guidance use frame concepts such as:
- upper body
- cowboy shot
- portrait
- full body

The author warns against overusing conflicting critical composition tags such as `close-up`, `upside-down`, `cowboy shot`.

## Audit consequence: frame conflict is Prompt conflict

If a Prompt contains mutually competing frame scopes such as:
- close-up
- cowboy shot
- full body

and the target is cropped or composition shifts, first classify this as competing Prompt instructions.

Do not conclude:
- `full body` is ineffective;
- the Special is semantically wrong;
- visibility metadata is wrong;

until the conflict is removed.

Japanese same-seed practical evidence (`S-JA-002`) gives a concrete example where adding conflicting frame tags narrowed the visible body range despite `full body` remaining present.

## Visibility can alter geometry

`CONTROLLED_PRACTICAL / mechanism-aware`

Visibility support is not always a neutral camera-only intervention.

To expose a body site, the model may need to change:
- pose
- limb arrangement
- torso orientation
- spacing between actors

Therefore a support row labeled purely `Visibility` should be reviewed if it deterministically implies major geometry/pose change.

This does not mean every visibility tag becomes Geometry support. It means the causal effect may overlap and image evidence should track both.

## Relation limitation

The Illustrious paper supports a broad distinction between tag representations and richer relational/context representations.

Audit rule:
- independent unary tags may be insufficient for complex actor-target relations;
- this is a general capability warning, not proof that every Illustrious derivative needs natural language.

---

# 3.3 NoobAI XL 1.1 EPS

## Exact inference regime

`FACT_EXACT_MODEL`

Source: `S-NOOB-EPS-001`

- CFG: 5-6
- Steps: 25-30
- Sampler: Euler a
- recommended area around 1024^2 with listed SDXL portrait/square/landscape sizes
- recommended positive prefix: `masterpiece, best quality, newest, absurdres, highres, safe`
- official Negative includes `bad hands`, `mutated hands` among other content/style filters

## Native caption structure

`FACT_EXACT_MODEL`

The model card gives:

`count -> character -> series -> artists -> special tags -> general tags -> other tags`

This is strong evidence that Special-before-General matches the native caption organization for NoobAI XL 1.1.

Audit consequence:
- if a proposed NoobAI-specific profile places Special after a large General block, this deserves review;
- do not turn this into a universal order for WAI/Illustrious/Anima;
- exact camera placement inside the General block remains unproven.

## Negative boundary

The official exact-model negative includes `bad hands` and `mutated hands`, but does not establish broad `bad anatomy / extra limbs / extra arms` as required defaults.

Audit consequence:
- do not certify broad anatomy negatives as mandatory NoobAI 1.1 behavior;
- anatomy-sensitive Special tests need controlled ON/OFF evidence.

## Exposure / dataset caution

The model card says it uses full Danbooru and e621 datasets with native tag captions and describes the v1.0 training date approximately before 2024-10-23.

Do not infer exact 1.1 tag exposure from today's Danbooru post_count alone.

A current tag can be:
- renamed after training
- aliased differently
- underrepresented
- represented by an older spelling

Therefore current post_count is not a direct model-knowledge probability.

## NoobAI EPS unresolved

`HOLD`

- exact optimal frame/viewpoint placement
- canonical vs alias response equality
- exact relation-sentence benefit
- exact broad+specific benefit
- exact multi-Special and prompt-density breakpoint

---

# 3.4 NoobAI XL V-Pred 1.0

## Exact inference separation

`FACT_EXACT_MODEL`

Source: `S-NOOB-VP-001`

The author explicitly warns that V-Pred works differently from EPS.

Recommended:
- CFG 4-5
- Steps 28-35
- Sampler: Euler
- other samplers are explicitly warned as not working properly in the model card
- recommended area around 1024^2
- native caption order still places Special before General

Audit consequences:
- `NoobAI` without EPS/V-Pred identity is incomplete for inference claims;
- a controlled result without prediction regime/sampler/CFG cannot safely support a family-wide rule;
- EPS success/failure should not be copied as V-Pred evidence.

---

# 3.5 Anima

## Versions are meaningfully different

`FACT_EXACT_MODEL`

Source: `S-ANIMA-001`

### Base
- unrefined base model
- maximum flexibility/diversity/style adherence
- author recommends Base for LoRA training

### Aesthetic
- fine-tuned for consistency and higher-quality default style
- quality tags were stripped during its fine-tuning
- author says quality tags are not required; `masterpiece, best quality` is safe but not necessary
- author recommends avoiding score_* tags in positive and negative when they push output too hard

### Turbo
- distilled for speed
- CFG 1
- 8-12 steps
- stronger default style / increased stability / reduced diversity

Audit rule:
- never store one generic `Anima` parameter profile when the claim is version-sensitive.

## Base/Aesthetic generation regime

`FACT_EXACT_MODEL`

The current author card says:
- 512^2 to 1536^2 supported range
- 30-50 steps, CFG 4-5 for the non-Turbo general regime
- multiple samplers are viable with different stylistic behavior

Sampler differences are explicitly described by the author, so sampler is not merely a speed implementation detail.

## Prompt format

`FACT_EXACT_MODEL`

- trained on Danbooru-style tags, natural-language captions, and mixtures
- lowercase tags
- spaces instead of underscores except score_* tags
- when Danbooru/Gelbooru forms differ, prefer Gelbooru form
- Prompt weighting works but may need stronger weights than typical SDXL; author example `(chibi:2)`

### Tag order

`quality/meta/year/safety -> count -> character -> series -> artist -> general`

Within each block the author allows arbitrary tag order.

### Artist tags

Artist tags require `@`; the effect is described as very weak without it.

### Tag dropout

Random tag dropout was used in training. The author says every relevant tag does not need to be included.

Audit consequence:
- a production support policy that assumes every implied constituent must always be injected is not supported by Anima training guidance;
- redundancy may increase Prompt competition rather than help.

## Natural language

`FACT_EXACT_MODEL + practical evidence`

The author allows:
- pure natural language
- tags + natural language
- quality/artist tags preceding prose

For pure NL, the author recommends sufficient description rather than extremely short vague prompts.

For multiple characters, the author explicitly says naming characters plus describing basic appearance is especially important; just listing names can confuse the model.

Audit consequence:
- tag-only, hybrid short-NL, and pure NL are distinct experimental modes;
- do not make `short NL relation sentence` a universal requirement simply because Anima can use it;
- exact relation benefit remains empirical.

## Direction / left-right risk

`COMMUNITY/PRACTICAL, official-hosted`

Anima discussions report:
- left/right ambiguity
- hand-direction ambiguity
- seed sensitivity
- conflicts between natural-language geometry and strong Booru concepts

Audit rule:
- deterministic left/right ownership claims are HIGH-risk;
- if a relation prompt fights an established Booru concept, classify Prompt conflict before declaring the canonical/support metadata wrong.

## Multi-character risk

`COMMUNITY/PRACTICAL`

Reports of 3-4 character generation show attribute bleed and weak binding.

Audit rule:
- ordinary tag-only Prompt should not be assumed to deterministically separate 3-4 actors;
- regional/Forge Couple intervention belongs to assisted-control evidence;
- a support profile claiming guaranteed actor separation needs controlled testing.

## Tag vs NL practical evidence

Japanese same-content tests (`S-JA-006`) and official-hosted community evidence suggest Prompt format can materially alter composition/style.

Current candidate interpretation:
- tags are good anchors for learned visual concepts;
- a short NL relation clause can be useful for gaps not well represented by independent tags;
- long prose can introduce extra concepts, environment pressure and anatomy/binding burden;
- no universal token/paragraph cutoff is established.

Status: `ADOPT candidate / exact-case image test required`.

---

# 4. Cross-cutting generation mechanisms

# 4.1 Concept load and Prompt density

`FACT_GENERAL`

ConceptMix shows that compositional performance drops as the number of requested visual concepts grows, particularly for open models.

Do not reduce this to `long Prompt = bad`.

A long Prompt can contain many compatible details. A short Prompt can contain several mutually demanding relationships.

For audit/test metadata record:
- Special count
- actor count
- object count
- attribute-binding count
- relation count
- body-site count
- frame requirements
- geometry requirements
- support block count
- natural-language relation clause yes/no
- token/tag count as secondary metrics

Audit consequence:
- if a Special fails only in a dense Prompt but works alone, classify composition/competition before `tag unsupported`.

# 4.2 Catastrophic neglect

`FACT_GENERAL`

Attend-and-Excite documents cases where diffusion generation omits requested subjects entirely.

This is important for multiple-Special audit.

Preferred diagnostic sequence:
1. A_ONLY
2. B_ONLY
3. AB minimal
4. BA if order is under study
5. AB + one minimal frame support
6. AB + targeted visibility/geometry
7. AB + actor/resource separation

If A and B work alone but one disappears in AB:
- likely class: composition/competition/binding
- not enough evidence: unknown tag

# 4.3 Attribute binding / concept bleeding

`FACT_GENERAL`

T2I models can attach attributes/actions to the wrong subject.

High-risk structures:
- two or more actors with asymmetric attributes
- left/right ownership
- one actor performing action on another
- body-site target belonging to a specific actor
- two hands with different roles
- multiple objects of same type assigned to different actors

Audit rule:
- support metadata should distinguish actor requirement, target/body-site, and spatial assignment where intrinsically required;
- success of the right broad scene with wrong ownership is not semantic success.

# 4.4 Frame, viewpoint, orientation, visibility, relation

Recommended analysis roles:

### Frame
How much body/scene is shown.
Examples: upper body, cowboy shot, full body.

### Viewpoint
Where the viewer observes from.
Examples: from side, from behind, from above, from below.

### Orientation
Body/torso/head direction.
Examples: torso twist, leaning, shoulders turned.

### Visibility
Whether target body site/object/action can actually be observed.

### Relation
Who acts on what / ownership / contact / spatial relation.

Audit rule:
- do not stack several same-role tags by default;
- avoid contradictory frame tags;
- use the smallest role set needed to observe the test question.

# 4.5 Negative prompts are semantic interventions

`FACT_GENERAL mechanism + exact-family HOLD`

Negative prompts should not be treated as a neutral garbage-disposal list.

If the negative semantically overlaps a target, it can suppress or alter the intended concept.

High-risk overlap examples:
- Special intentionally changes limb/body count + `extra limbs/extra arms`
- unusual body configuration + `bad anatomy/malformed anatomy`
- intended blur/motion effects + generic anti-blur
- intended text/logo/signature concepts + text/watermark suppression
- intended old/retro aesthetic + `old` or related quality/date negatives

Audit rule:
- mark overlapping negative as a confounder;
- compare N0 baseline vs targeted negative addition;
- score both intended-concept retention and unwanted-error suppression.

No exact global anatomy-negative list is currently FACT across target families.

# 4.6 Broad + specific support

`PRACTICAL / HOLD for exact family defaults`

A broad parent concept can sometimes help a rarer specific concept by providing learned context.

It can also:
- dilute specificity
- pull the image toward the common parent
- create redundant Prompt pressure

Therefore test separately:
- specific only
- broad only
- broad + specific

Do not automatically convert implications into Prompt synonyms.

# 4.7 Canonical / Alias / Semantic generation response

`HOLD`

Dictionary relation and learned model response are separate.

Candidate controlled comparison:
- canonical surface form
- known Alias surface form
- older/newer tag spelling when historically relevant
- semantic-near term only in a separate non-equivalence test

Rules:
- preserve exact sent Prompt
- never silently normalize both conditions before generation
- do not rank canonical > Alias > Semantic without evidence

---

# 5. Post-processing and intervention confounds

# 5.1 Hires Fix

WAI v17 exact author evidence demonstrates the most important audit point: Hires can repair limbs.

Therefore Hires is not always neutral.

For target-sensitive evidence record:
- base-pass Prompt/settings
- base image if retained
- upscaler
- Hires steps
- denoise strength
- final image

Interpretation classes:
- `BASE_SUCCESS_FINAL_SUCCESS`
- `BASE_FAIL_POSTPROCESS_RESCUE`
- `BASE_SUCCESS_POSTPROCESS_DAMAGE`
- `NO_MATERIAL_CHANGE`

# 5.2 ADetailer

`FACT_GENERAL tool mechanism`

ADetailer performs:
1. generation
2. detection/masking
3. inpainting

It can use its own Prompt/Negative and separate inpainting parameters.

Therefore:
- a face/hand/body-site corrected by ADetailer is not evidence the base Prompt generated it correctly;
- ADetailer may change details relevant to Special judgement;
- detection threshold/mask/inpaint settings are part of evidence identity when the target overlaps the edited region.

Multi-object `[SEP]` prompting also has an explicit warning that detection order is highly arbitrary, so detected-object order should not become actor semantic authority.

# 5.3 img2img / inpaint

`FACT_GENERAL`

Any img2img/inpaint pass can preserve, replace, or repair local structure depending on denoise and mask.

Audit consequence:
- prompt-only capability and edit-assisted capability must be separated;
- final-image success under high-denoise inpaint cannot certify the original generation profile.

# 5.4 ControlNet / OpenPose

`FACT_GENERAL`

ControlNet adds explicit spatial conditioning such as pose/depth/edge/segmentation.

Use it when the product goal benefits from reliable spatial control, but treat it as a separate assisted lane.

Prompt-only ceiling principle:
- do not endlessly add weights/tags when the remaining failure is clearly spatial binding;
- record `PROMPT_ONLY_CEILING` and escalate to assisted control where appropriate.

# 5.5 Regional prompting / Forge Couple

`PRACTICAL product mechanism`

Regional tools can reduce actor/attribute bleed by partitioning prompt influence spatially.

They are useful for:
- multiple actors
- asymmetric clothing/attributes
- actor-target separation

They do not prove the underlying model can achieve the same binding with plain tags.

---

# 6. LoRA interaction knowledge

# 6.1 Loaded LoRA is itself a variable

`PRACTICAL / mechanism`

A trigger word is not necessarily a hard switch.

Practical Illustrious LoRA training guidance recommends comparing:
- LoRA loaded + trigger
- LoRA loaded + no trigger
- different characters/clothes
- simple vs complex background
- fixed Prompt/Seed across checkpoints/weights

Audit consequence:
- record every loaded LoRA and weight even if its trigger text is absent;
- a result generated with LoRA loaded cannot be assumed equivalent to base checkpoint behavior;
- `no trigger` is not automatically `no LoRA effect`.

# 6.2 Multiple LoRAs

`HOLD / practical`

Potential interactions include:
- competing style directions
- character/style binding leakage
- decreased Prompt adherence
- changes in anatomy/detail
- order/weight sensitivity depending on implementation

No universal combination rule is currently strong enough for production.

Minimum comparison when interaction matters:
- base model
- A only
- B only
- A+B
- optionally B+A if implementation/order may matter
- same seed/settings/Prompt

# 6.3 Model-family compatibility

Do not assume a LoRA trained for one base/family is semantically neutral or reliable on another derivative.

Audit result should record:
- training base if known
- inference checkpoint
- weight
- trigger
- whether LoRA is style/character/pose/concept

---

# 7. Failure diagnosis taxonomy

When an intended result is missing, do not jump directly to `tag bad`.

Use this order.

## F1. Identity/exposure failure
The model may not have learned the exact surface form/concept strongly enough.

Evidence:
- fails in isolated prompt across multiple seeds
- canonical/alias tests both weak
- target is not merely cropped or assigned to wrong actor

## F2. Single-concept realization failure
The tag is recognized but the model cannot reliably realize the geometry/anatomy/action.

Evidence:
- related visual cues appear but intended configuration repeatedly fails in minimal prompt.

## F3. Composition/competition failure
A and B work alone but one or both degrade in AB.

Possible causes:
- concept load
- attention competition
- conflicting supports
- broad parent overpowering specific child

## F4. Binding/ownership failure
All requested concepts appear, but the wrong actor/object/body site receives them.

This is distinct from missing concept.

## F5. Visibility/crop/occlusion failure
The concept may exist but cannot be judged because the target is outside frame or occluded.

Use minimal visibility support before declaring semantic failure.

## F6. Prompt contradiction
Two Prompt instructions request incompatible frame/pose/relation/style conditions.

Remove contradiction before blaming data.

## F7. Negative collision
Negative conditioning suppresses or distorts the target.

Test with the conflicting negative removed.

## F8. Model-family mismatch
Prompt grammar/settings copied from another family may be inappropriate.

Example: EPS settings copied to NoobAI V-Pred.

## F9. Post-processing confound
Final result differs because Hires/ADetailer/inpaint/control edited the target.

Separate base and final verdicts.

## F10. Evaluator blindness
The image may be correct but the automated evaluator lacks the tag/vocabulary/relation semantics.

Route to REVIEW rather than image-failure.

---

# 8. Stage10 / audit experiment patterns

# 8.1 Single Special baseline

Purpose: establish model exposure / isolated realizability.

- minimal family-correct quality/meta
- one Special
- only visibility support required to judge
- no aesthetic decoration unless the test is practical-stress mode

# 8.2 Multiple Special escalation

A_ONLY
B_ONLY
AB minimal
AB + Frame
AB + Viewpoint if needed
AB + targeted Geometry/Visibility
AB + Resource parking/disambiguation
assisted-control lane only after Prompt-only ceiling

# 8.3 Negative collision test

N0: family baseline without disputed broad negative
N1: + candidate negative

Evaluate separately:
- intended Special retention
- unwanted artifact suppression

# 8.4 Canonical/Alias test

A: exact canonical surface
B: exact Alias surface

Do not normalize before sending.

Possible valid outcomes:
- canonical stronger
- alias stronger
- tie
- both fail
- seed-dependent / REVIEW

# 8.5 Prompt density test

P0: Special core only
P1: + necessary meaning/geometry/visibility
P2: + aesthetic support
P3: + redundant/unrelated/competing additions

Record concept counts as well as tokens.

# 8.6 Assisted-control ceiling

If Prompt-only A/B cannot stabilize precise spatial relation after minimal structured support:
- record ceiling
- use ControlNet/OpenPose/regional prompting in a separate condition
- never retroactively label assisted success as Prompt-only success

---

# 9. Evaluator/tagger knowledge

## 9.1 Tag classifier role

Danbooru taggers are useful for:
- common unary visual concepts
- attributes
- rough presence/absence screening

They are weak ground truth for:
- rare tags outside vocabulary/training threshold
- compound Specials
- actor-target relations
- body-site ownership
- canonical/Alias semantic equivalence
- multi-Special joint retention

## 9.2 Routing principle

Use at least:
- AUTO when evaluator class is compatible and calibrated
- REVIEW when vocabulary/confidence/semantic class is unsupported
- BLOCKED when generation/evidence pipeline is invalid

Do not force A/B winner from a classifier that cannot represent the human question.

## 9.3 Final-dictionary comparison backlog

After the Special dictionary is frozen, compare:
- WD EVA02 v3
- Kagami-24k
- CL Tagger v2

against the full final Special set.

Measure by:
- Core / Extended / Alias / Semantic role
- semantic class
- frequency/rarity
- direct vocabulary availability
- canonical-target resolution
- OOD/low-confidence risk where available

This comparison should guide routing, not redefine dictionary identity.

---

# 10. Audit red flags

A dictionary/generation record deserves deep review if it asserts any of the following without appropriate evidence:

- one universal Prompt order across all families
- mandatory `full body` for every Special
- mandatory broad anatomy negatives for unusual anatomy
- Alias and canonical must generate equally
- current post_count proves training exposure
- any General co-occurrence is automatically semantic support
- Aesthetic/lighting/background is required meaning
- one confidence threshold works for common unary and rare relation tags
- Hires/ADetailer output proves base Prompt anatomy success
- ControlNet/regional result proves Prompt-only support rule
- NoobAI EPS evidence is applied to V-Pred
- Anima Aesthetic/Turbo behavior is stored as generic Anima Base behavior
- a loaded LoRA is ignored because its textual trigger was absent
- a dense AB failure is labeled tag-unknown without A_ONLY/B_ONLY evidence

---

# 11. Current ADOPT / HOLD / REJECT summary

## ADOPT

- family-specific knowledge isolation
- minimal official quality/meta baseline per family
- typed support taxonomy
- role-minimal camera/visibility support
- A_ONLY/B_ONLY before multiple-Special diagnosis
- exact Prompt/Negative/Seed/model/settings traceability
- separate Prompt-only and assisted-control lanes
- base-pass vs post-process distinction when target can be modified
- conservative evaluator REVIEW fallback
- multilingual evidence acquisition

## HOLD

- exact NoobAI EPS camera placement optimization
- anatomy-negative universal rule
- exact canonical/Alias generation ranking
- exact Semantic-near prompt usefulness
- universal prompt length/token threshold
- universal simultaneous Special count limit
- universal multiple-LoRA combination rule
- universal threshold for regional/ControlNet escalation
- exact family-specific benefits of `fully visible / clearly visible / unobstructed / in frame / body part focus`

## REJECT

- one Prompt grammar for WAI/Illustrious/NoobAI/Anima
- giant universal quality stack
- giant universal Negative stack
- `full body` always-on
- support count monotonically improves generation
- alias dictionary equivalence == model response equivalence
- current Danbooru frequency == model exposure probability
- post-processing rescue == base Prompt success
- community observation == production truth

---

# 12. Knowledge acquisition priorities

The corpus is intentionally incomplete. New research should preferentially reduce audit uncertainty rather than add generic Stable Diffusion tips.

## P0 — dictionary audit risk
- unusual anatomy vs anatomy/count negatives by exact family
- actor-target / body-site / hand ownership support
- compound/multiple-Special failure diagnosis
- model trigger spelling vs canonical identity
- support class: intrinsic meaning vs observability/geometry

## P1 — family-specific practical generation
- NoobAI EPS camera/framing
- WAI v17 minimum sufficient support
- Anima tag-only vs hybrid relation behavior
- model-family prompt-density stress
- exact seed sensitivity for relation/left-right cases

## P2 — intervention and evaluator quality
- LoRA interference
- Hires/ADetailer preservation vs rewrite rate
- regional prompting / Forge Couple practical ceiling
- WD/Kagami/CL Tagger final-dictionary coverage and calibration

---

# 13. Durable interpretation rule

When a future chat reads this corpus, it should not simply repeat the current conclusions.

For any decision with material impact:
1. locate the source ID in `GENERATION_KNOWLEDGE_SOURCES.md`;
2. verify model/version scope;
3. check whether a newer exact source supersedes it;
4. distinguish FACT from PRACTICAL/HOLD;
5. compare against the current requesting Issue and frozen dictionary snapshot;
6. if evidence is still insufficient, keep REVIEW/HOLD rather than filling gaps from memory.

The purpose of this corpus is not to make the system certain about everything. It is to make uncertainty explicit, recoverable, and consistently applied.
