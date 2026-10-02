# BATCH_AH — Illustrious / NoobAI multi-subject practice and source-conflict audit — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: community synthesis + source-conflict audit
Scope: Illustrious / NoobAI, multi-subject, adult/hard-scene workflow

## 1. Illustrious multi-subject community practice

Sources:
- https://www.reddit.com/r/StableDiffusion/comments/1rg7cpj/how_to_make_multiple_character_on_same_image_but/
- https://www.reddit.com/r/StableDiffusion/comments/1io5yxx
- https://www.reddit.com/r/StableDiffusion/comments/1sla0rq/struggling_to_make_more_than_2_characters/

Recurring observations:
- two distinct subjects can mix traits under one global prompt;
- detail/identity loss becomes worse as subject count rises;
- 3+ subjects are substantially less reliable;
- users frequently escalate to regional prompting or per-character inpainting.

Important contradiction inside the community:
- some users report BREAK helps;
- others report BREAK does not prevent character mixing;
- runtime/parser support differs.

Project treatment:
- no universal BREAK rule;
- retain regional/inpaint escalation as a practical lane;
- preserve exact runtime when testing separators.

Promoted:
- K-COMM-ILL-003.

## 2. Multi-stage masked workflow

Source:
https://www.reddit.com/r/StableDiffusion/comments/1irsq4o

Public workflow idea:
- reference composition;
- per-character masks;
- per-character prompts;
- OpenPose/pose conditioning;
- character LoRAs;
- img2img reconstruction.

Knowledge value:
This is a good example of `divide the global problem into regional subproblems`.

Evidence lane:
- not plain txt2img;
- not plain multi-LoRA;
- not pure regional text;
- combined mask + pose + adapter + img2img.

Promoted:
- K-TOOL-025.

## 3. Adult VN / character consistency signal

Source:
https://www.reddit.com/r/comfyui/comments/1v62676/illustrious_keeping_characters_consistent_for/

User reports:
- ControlNet solves pose/framing more easily than character-style consistency;
- identity/reference control and geometry control can fail independently;
- planned multi-character extension points toward per-character masks/reference plus shared pose control.

Project interpretation:
- pose fidelity and identity fidelity are separate axes;
- stacking more reference adapters is not automatically equivalent to subject-local conditioning.

Source-map only; no extra Claim.

## 4. NoobAI secondary-source conflict

Source:
https://lewdly.ai/blog/noobai-xl-checkpoint-review-anime-nsfw

The article claims:
- V-Pred CFG 6–9;
- CFG rescale 0.2 required;
- Euler/DDIM only;
- specific LoRA-strength defaults;
- exact production-usability percentages.

Current exact author guidance for V-Pred 1.0:
- CFG 4–5
- 28–35 steps
- Euler
- no project-authority support for the article's universal CFG 6–9 + required rescale 0.2 claim.

Therefore:
- the article is useful as community experience;
- its exact V-Pred configuration must not override the author card;
- exact percentage success claims remain private test-set results.

Promoted:
- K-SOURCE-003.

## 5. Noob multi-subject stress signal

The same community review reports:
- single subject strongest;
- two-subject scenes generally better than group scenes;
- 3+ subject interactions substantially weaker;
- dynamic interaction harder than static composition.

Because the article's inference recipe conflicts with author settings, we retain only the broad stress signal as low-authority CANDIDATE evidence.

Promoted:
- K-COMM-NOOB-002.

## 6. Community over-prompting signal

In the Illustrious Reddit thread, multiple users report that adding all known appearance details can worsen cross-character leakage when the checkpoint already knows the identities.

Hypothesis:
- redundant explicit attributes can increase binding pressure;
- identity-known minimal prompts may outperform dense per-character restatement.

This is already represented by project minimum-sufficient Prompt principles and is not promoted separately.

## 7. Source-conflict rule

When secondary source S conflicts with exact author source A:

1. preserve S with date/version;
2. inspect whether S used an older checkpoint/derivative/runtime;
3. do not average the settings;
4. exact current author baseline remains the first test condition;
5. secondary recipe can become a separate experimental condition.

## Promotion result

New CANDIDATE:
- K-COMM-ILL-003
- K-TOOL-025
- K-COMM-NOOB-002

New ACCEPTED project governance:
- K-SOURCE-003
