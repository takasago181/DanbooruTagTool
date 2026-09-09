# Stage10 PROMPT — WAI Illustrious v17 local test profile

最終更新: 2026-09-09
Owner: PROMPT / Issue #5
Status: WAI17-first local test profile / candidate baseline. **Not production specification.**

## 1. Purpose

当面のStage10 Prompt検証を、ユーザーの実環境で既に動作確認されている WAI Illustrious v17 + Forge Neo を主対象に絞って進めるためのPROMPT側復元資料。

この文書は、Issue #30 の既存 automation / plumbing fixture を置き換えない。

- Issue #30 = 自動化パイプラインの動作確認・metadata・WD14・APIのfixture
- 本文書 = WAI17で実際にPrompt品質・hard-target成立性を評価するためのPROMPT baseline候補

両者を混同しない。

---

## 2. Verified local environment facts

Issue #30 のGitHub証跡で確認済み:

- runtime family: Forge Neo
- loaded model: `sd\\waiIllustriousSDXL_v170.safetensors`
- SHA-256: `f116b0c78ff441467b0cdc8f1936e1ed18ea31e9997c7b132b1b8db533f0bd04`
- native Forge API疎通確認済み
- `/sdapi/v1/options`, `/sdapi/v1/txt2img`, `/sdapi/v1/png-info` 使用経路を確認
- WD14 interrogator API使用経路を確認
- Issue #30 pipeline infrastructure verdict: `PASS_PIPELINE`
- fixed Seed `5072` は既存dry-run/golden-setで使用済み

既存導入拡張（Issue #30 / current project stateより）:
- TagComplete Neo
- WD14 Tagger
- ADetailer Neo
- Forge Couple
- Dynamic Prompts Neo

---

## 3. WAI17 author guidance — highest-priority baseline

WAI17 author/mirror guidanceから保持するもの:

- recommended software: Forge Neo
- Steps: 15–30
- CFG: 5–7
- Sampler: Euler a
- VAE integrated
- original size: >1024x1024 recommended
- sample size: 1024x1344
- Hires example: upscale 1.5 / hires steps 20 / denoise 0.35–0.5 / R-ESRGAN 4x+ Anime6B
- positive quality example: `masterpiece, best quality, amazing quality`
- negative example: `bad quality, worst quality, worst detail, sketch, censor`
- do not overload quality/aesthetic tags
- do not use overly long negative prompts
- no trigger word required
- v17 notes include Hires.fix limb-correction improvement attempt

PROMPT interpretation:
- author guidance is **baseline**, not automatic proof of hard-target optimum.
- any behavior-changing promotion still needs controlled local A/B.

---

## 4. WAI17-first practical baseline candidate

For **Prompt-quality experiments** (not Issue #30 plumbing fixture):

- checkpoint: exact local WAI17 hash above
- runtime: exact current Forge Neo; do not silently update
- sampler: Euler a
- steps: 25 (center of author range)
- CFG: 6 (center of author range)
- test size:
  - causal / fast comparison: 1024x1024 when square framing is suitable
  - user-practical portrait stress test: 1024x1344
- batch: 1 unless experiment explicitly tests batch behavior
- seed: fixed within A/B; Seed 5072 may be reused when continuity with existing fixture is useful, but seed is not a production default
- VAE: no external VAE
- LoRA: OFF for baseline unless the experiment is explicitly a LoRA experiment
- Hires.fix: OFF for first-pass causal Prompt comparison
- assisted controls: OFF for Prompt-only baseline

### Hires confirmation pass

Only after a Prompt candidate is promising:
- Hires.fix ON
- upscale 1.5
- hires steps 20
- denoise start 0.35; compare upward only if needed, max candidate range 0.5

Do not count Hires-rescued semantics as evidence that the original txt2img Prompt alone succeeded.

---

## 5. WAI17 Prompt grammar candidate

Current PROMPT-side candidate: `LEAN_TAG_FIRST`.

Suggested conceptual order:

1. subject / count / character identity
2. Special / ACT core
3. SITE / OBJECT / actor-target relation
4. only-needed pose / geometry
5. only-needed visibility / frame
6. minimal quality / aesthetic finish
7. short family-specific Negative

This is a **WAI17 candidate assembly rule**, not a production rule.

### Why this candidate exists

- WAI17 author warns against excessive quality/aesthetic tags.
- WAI17 author warns against overly long Negative prompts.
- hard-target PROMPT audit shows support accumulation can bury or distort the target.

Therefore do not use generic SDXL “everything good + everything bad” templates as the WAI17 default.

---

## 6. Negative strategy

Baseline candidate:
- start from the author-minimal quality Negative family.
- add only failure-specific terms.
- never inherit a large generic Negative template by default.
- never place a target concept or close semantic neighbor in Negative without explicit controlled reason.

For adult hard-target tests:
- `nsfw` in Negative is **not** a default because it can suppress the intended domain.
- anatomy-sensitive negatives remain controlled ON/OFF candidates when they may collide with unusual anatomy / limb configurations.

---

## 7. Hard-target test decomposition

For difficult adult / niche Special cases, PROMPT internally decomposes into:

- `ACT`
- `SITE`
- `OBJECT`
- `ACTOR_A`
- `ACTOR_B`
- `RELATION`
- `POSE / GEOMETRY`
- `VISIBILITY`

The user should not be forced to fill these manually. They are internal diagnosis dimensions.

Primary failure classes:
- ACT_MISSING
- SITE_WRONG
- BINDING_LOST
- OBJECT_DEGRADES
- VISIBILITY_LOST
- GEOMETRY_BREAK
- PROMPT_INTERFERENCE

---

## 8. WAI17 experiment order

Priority order for the first WAI17-only Stage10 lane:

1. Special alone / minimal baseline recognition
2. canonical vs Alias / alternate trigger where applicable
3. no support vs exactly one meaning/site support
4. no support vs exactly one geometry/visibility support
5. minimal Negative vs expanded Negative
6. single Special vs two-Special composition
7. Prompt-only vs assisted-control escalation for persistent binding/geometry failures
8. Hires OFF vs Hires ON only after semantic candidate selection

Keep one experiment = one question.

---

## 9. Evaluation

Do not collapse into “prettier image wins”.

Track separately:
- TARGET / ACT retention
- SITE accuracy
- BINDING
- OBJECT integrity
- GEOMETRY
- VISIBILITY
- FINISH QUALITY
- conflict / artifacts
- user repair cost
- reproducibility

A beautiful image with the target Special missing is not a product success.
A semantically correct image with unusable anatomy/finish is also not a product success.

---

## 10. WD14 boundary

Existing WD EVA02-Large Tagger v3 remains first-pass machine evidence only.

Known limitation:
- tags with fewer than 600 training images were filtered from its training vocabulary.
- rare / long-tail / relational Special may therefore be unsupported or weakly observable.

Consequences:
- unsupported / low-confidence -> REVIEW, not FAIL
- global validation threshold is not a universal hard-Special threshold
- human/controlled evaluation remains necessary for rare and relational targets

---

## 11. Prompt-only ceiling / assisted control

Escalate instead of endlessly adding tags when a failure repeats across controlled attempts:

- actor/target mixing -> Forge Couple / regional conditioning candidate
- pose / spatial geometry instability -> ControlNet / pose-control candidate
- local face/hand defect after semantic success -> ADetailer candidate
- Hires.fix can be a finish/limb-repair lane but must be recorded as second-pass assistance

Assisted success must remain distinguishable from PROMPT_ONLY success.

---

## 12. Relationship to existing Issue #30 fixture

Issue #30 already proved the automation pipeline can run WAI17 fixed-seed A/B, preserve PNG metadata, call WD14, and complete with zero manual operations.

That fixture is **plumbing evidence**. It is not proof that its exact generation settings are the optimal WAI17 product settings.

PROMPT Stage10 should therefore:
- reuse the proven infrastructure,
- keep fixture evidence intact,
- introduce this WAI17 practical baseline as a separate experiment profile,
- record profile identity in metadata.

---

## 13. Non-actions

- no production promotion yet
- no final winner/scoring threshold yet
- no global model-family grammar change
- no automatic Special weakening/generalization
- no silent Forge Neo/checkpoint update
- no assumption that author defaults are hard-target optimum

---

## 14. Restore pointers

Read in this order when restoring PROMPT:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #5 latest restore checkpoint
4. this file
5. `STAGE_10_PROMPT_CURRENT_PURPOSE_AUDIT_20260909.md` and high-quality audit documents if needed
6. Issue #30 only for automation/plumbing facts

