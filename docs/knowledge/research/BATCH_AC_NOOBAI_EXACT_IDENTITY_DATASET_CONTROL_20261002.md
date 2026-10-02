# BATCH_AC — NoobAI exact identity / dataset exposure / assisted control — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: exact author/source refresh
Scope: NoobAI XL 1.1 EPS / V-Pred 1.0 / relation-heavy adult and hard-scene testing

## 1. Exact EPS checkpoint identity

Official file:
https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/NoobAI-XL-v1.1.safetensors

Current official SHA256:
`6681e8e4b134c81f16533acedb0d406d7e5e366e1624b4105178c64d00b05d51`

Use:
- remote reference identity;
- local runtime evidence still requires local hash comparison.

## 2. Exact V-Pred checkpoint identity

Official file:
https://huggingface.co/Laxhar/noobai-XL-Vpred-1.0/blame/main/NoobAI-XL-Vpred-v1.0.safetensors

Current official SHA256:
`ea349eeae87ca8d25ba902c93810f7ca83e5c82f920edf12f273af004ae02819`

EPS and V-Pred remain separate evidence families.

## 3. Dataset exposure window

Author card:
https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md

Documented:
- full/native Danbooru-style tag context;
- Danbooru images up to the training date;
- v1.0 approximately before 2024-10-23;
- e621-2024-webp-4Mpixel dataset.

Project consequence:
A current Danbooru tag can be:
- semantically valid today;
- high current post_count;
- yet newer than the relevant training window or renamed after training.

Therefore:
`current canonical identity != guaranteed model trigger exposure`.

For rare/hard/adult tags:
- preserve current canonical identity;
- separately test historical/alias/model surfaces when evidence justifies it;
- never rewrite canonical identity to match guessed training vocabulary.

## 4. Dedicated NoobXL ControlNet

Same author card states:
- dedicated ControlNet training is ongoing;
- normal, depth, and canny models have been released.

Project consequence:
For geometry-limited hard scenes, Noob has a model-family-specific assisted-control lane in addition to generic SDXL controls.

Evidence classification:
- plain-Prompt result
- NoobXL ControlNet-assisted result
must remain separate.

## 5. Adult hard-scene baseline implication

NoobAI is attractive for hard/adult vocabulary research because:
- Danbooru + e621 training gives broad tag-surface candidates;
- exact Special-before-General author order is documented.

But this does NOT establish:
- actor/receiver correctness;
- exact body-site relation;
- exact count;
- topology;
- new/current tag exposure.

Those remain controlled-test questions.

## 6. Trigger-freshness test template

For a suspicious rare/new tag:

A. current canonical surface
B. current Alias if valid
C. historical/old surface only if evidence exists
D. model-adjacent e621 surface only when concept/source warrants
E. descriptive decomposition

Same seeds/settings.

Score:
- concept presence
- semantic fidelity
- relation/body-site/count
- collateral context

Do not auto-select the “winner” as canonical identity.

## Promotion result

New ACCEPTED:
- K-MODEL-NOOB-007
- K-MODEL-NOOB-008
- K-TOOL-019

No Noob hard-relation HOLD closed.
