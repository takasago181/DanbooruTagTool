# BATCH_AU — RegionalSampler proxy method — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Scope: Anima / ComfyUI-Impact-Pack / multi-subject identity-style replacement

## 1. Official RegionalSampler mechanism

Source:
https://github.com/ltdrdata/ComfyUI-Impact-Pack

Impact Pack documents:
- `RegionalPrompt` = mask + sampler bound to a region;
- multiple regional prompts can be combined;
- `RegionalSampler` runs a base sampler and regional sampling during each step;
- `overlap_factor` blends region boundaries;
- `restore_latent` can restore outside-mask latent during regional sampling.

This is **latent-level regional generation**, distinct from attention-only prompt routing.

Promoted:
- K-TOOL-034.

## 2. Detailed recent Anima practice

Source:
https://huggingface.co/datasets/rouge-kasshoku/anima-crossover-couples-regional-sampler-guide

The guide is a months-of-testing community writeup for two-subject Anima generation.

Its most durable contribution is not a numeric recipe; it is a workflow architecture:

`good native reference -> regional replacement -> minimal localized correction`.

## 3. Native proxy method

Three cases:

### Both characters native
Generate the actual pair natively and fix only residual style/identity bleed regionally.

### One character non-native
Generate:
- the native target character;
- a native proxy for the unsupported target.

Then replace only the proxy region with a LoRA-conditioned regional sampler.

### Both characters non-native
Generate a native proxy pair with similar structural traits, then replace each region separately.

Why it can help:
- global composition and interaction come from the base model;
- the regional stage does less geometry reconstruction;
- LoRA influence is introduced later and more locally.

Promoted as CANDIDATE:
- K-COMM-ANIMA-028
- K-PRACTICAL-029.

## 4. Minimize edit distance

Choose proxy features that reduce later change:

- similar pose
- similar silhouette/body size
- similar hair length/shape when possible
- similar camera visibility
- similar large color/skin/clothing blocks if the region method is sensitive to them

This is analogous to choosing a good initial state for inpainting.

The proxy is not evidence of target identity support; it is a construction scaffold.

## 5. Constraint versus freedom

The recent guide describes a coupled system:

### Smaller/tighter mask
More structure inherited from reference.

### Larger mask
More freedom to regenerate target identity/style, but more risk of geometry drift.

### More base preservation
More reference pose/composition retained.

### Less base preservation
More regional prompt/LoRA freedom.

### Higher regional LoRA pressure
More target identity/style, but more risk of localized/global contamination.

### More overlap
Can soften boundary artifacts.

Exact parameter values are guide-specific.

Promoted:
- K-PRACTICAL-030.

## 6. Sampler caution

The guide strongly recommends deterministic sampling for this specific two-pass/reference-preservation workflow and notes that stochastic/ancestral choices can change composition.

Treat this as:
- current Anima RegionalSampler practice;
- not a universal judgment against Euler a / er_sde.

Promoted as CANDIDATE:
- K-COMM-ANIMA-029.

## 7. Regional prompt should not redundantly rebuild the entire scene

In this workflow, the base latent already provides:
- camera
- pose
- composition
- broad interaction.

The regional branch can focus on:
- target identity traits
- local action/appearance when relevant
- local style/lighting correction.

Learning principle:
Do not ask the regional prompt to re-solve already accepted global structure unless that structure itself is the thing being changed.

## 8. Adult/hard-scene use

For clearly adult multi-subject images:

1. first obtain a base composition where:
   - count
   - role geometry
   - visibility
   - major contact structure
   are acceptable;

2. replace unsupported/contaminated identities locally;

3. re-audit the relation after every regional replacement.

Regional identity correction can still alter:
- hands
- contact
- expression
- local body geometry.

## 9. Metadata synchronization

The guide uses two workflows:
- reference generator;
- regional reconstruction.

Generation metadata is read from the chosen reference so:
- prompt
- sampler
- scheduler
- steps
- CFG
- seed
stay synchronized.

This is an excellent study pattern.

Promoted:
- K-EVID-008.

## 10. Teacher exercise

Use one two-subject scene.

A — final targets globally from scratch  
B — native proxy/reference only  
C — B + regional replacement of subject 1  
D — C + regional replacement of subject 2

Score after every step:
- identity
- role
- relation
- pose
- style
- boundary artifacts.

The learner should be able to say which stage introduced each defect.

## Promotion result

New ACCEPTED:
- K-TOOL-034
- K-PRACTICAL-030
- K-EVID-008

New CANDIDATE:
- K-COMM-ANIMA-028
- K-COMM-ANIMA-029
- K-PRACTICAL-029
