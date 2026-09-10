# Issue #30 Phase 2 targeted first-wave design — 2026-09-10

## Decision

The frozen 128-image pilot was reused first. Its coverage shows that broad
AUTO calibration is not supported: 92/128 images are relation-sensitive,
84/128 contain component-only evaluator evidence, and only one image reached
the frozen high-confidence screen. The first wave is therefore limited to
three narrow questions and 12 images total.

The wave is prepared, not silently started. Generation requires the local
Forge preflight and the user-visible review asset workflow. A result is not a
production rule or a Stage10 production A/B.

## Selected questions

| ID | Special ID | Canonical | Question | A/B difference | Seeds | Images |
|---|---:|---|---|---|---|---:|
| P2-001 | 264 | `vibrator in anus` | Functional device-to-body-site relation | target relation vs object-only `vibrator` | 41001, 41002 | 4 |
| P2-002 | 750 | `holding sex toy` | Subject-to-object holding relation | holding relation vs object-only `sex toy` | 41011, 41012 | 4 |
| P2-003 | 2024 | `breast expansion` | Negative collision for anatomy-changing target | baseline Negative vs target included in Negative | 41021, 41022 | 4 |

All IDs are present in the current `data/generation/special2788_generation_profile.csv`.
All positive prompts, Negative Prompts, seeds, sampler, checkpoint, and
resolution are recorded in the CSV manifest. The first two questions are
relation-sensitive and remain HUMAN_REVIEW_ONLY even if taggers agree.

## Deferred questions

These were considered from current project data but deferred to keep the first
wave at 12 images:

| Special ID(s) | Canonical | Reason |
|---|---|---|
| 275 | `double dildo` | exact-count/object-shape question is valuable, but can wait for the first-wave review decision |
| 1 + 264 | `anus + vibrator in anus` | simultaneous multi-Special retention compounds the device/site question |
| 1286 | `anal penetration` | Alias-preserve behavior should be tested only after a direct canonical control is understood; `canonical_target=anal` is preserved |

## Fixed generation profile

- Forge Neo, WAI Illustrious v17 (`waiIllustriousSDXL_v170.safetensors`)
- Euler a, Automatic scheduler, 25 steps, CFG 5
- 1024×1344 portrait where appropriate
- Hires OFF, ADetailer OFF, LoRA OFF, ControlNet OFF, regional OFF, Forge Couple OFF
- two predetermined paired seeds per condition; no automatic seed escalation

The existing Phase 1 runner is reused with external manifest support. The
initial test has no evaluator authority over structural success; machine
disagreement, low confidence, and artifact/validity failures route to review
or abstention.

## Review design

The user reviews one numbered contact sheet containing 12 images grouped as
three A/B questions. The answer format is `A / B / both / neither / tie /
unclear`, plus one short note only if the intended relation cannot be seen.
Raw evaluator logs and CSV editing are not required.
