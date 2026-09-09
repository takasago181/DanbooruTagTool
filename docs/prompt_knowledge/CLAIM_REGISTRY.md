# PROMPT Claim Registry

Owner: PROMPT / Issue #5
Status: **current claim-status authority for PROMPT knowledge**. Not production specification.
Last normalized: 2026-09-09

## How to read

This registry answers **「いま、その知識をどう扱うか」**。

- `SOURCE` = 根拠の種類
- `STATUS` = 現在の採用状態
- `SCOPE` = 適用範囲
- `VALIDATION` = 追加検証の要否

Label definitions: `00_KNOWLEDGE_GOVERNANCE.md`.

Detailed explanation remains in `01`–`10` category docs.
Detailed evidence/provenance remains in `docs/stages/STAGE_10_PROMPT_*.md` and mapped sources.

---

## A. Product purpose / doctrine

| ID | Claim | SOURCE | STATUS | SCOPE | VALIDATION | Evidence / notes |
|---|---|---|---|---|---|---|
| K-PURPOSE-001 | PROMPT側の目的は単なるtag整形ではなく、制作意図を保持し、model-appropriateな高品質hard-target Promptへ変換し、user repairを減らすこと | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 01; CURRENT_PURPOSE_AUDIT |
| K-PURPOSE-002 | `minimum prompt` は最短文字列ではなく `minimum sufficient structure` | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 01/03/06 |
| K-PURPOSE-003 | 実験分離Promptと実戦Stress Promptは別モードとして扱う | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 01/07; REPLACEMENT_REFERENCE |
| K-PURPOSE-004 | Beautiful image alone is not success if intended target/relation is missing | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 01/07 |
| K-PURPOSE-005 | PROMPT班は未検証知識をproduction ruleへ単独昇格させない | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | PERMANENT_RULES / 01 |
| K-PURPOSE-006 | UserへSpecial探索・Prompt再構築を標準で戻さず、必要なreplacement slotを最小化する | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | PERMANENT_RULES; REPLACEMENT_REFERENCE |

---

## B. Semantic / render-surface separation

| ID | Claim | SOURCE | STATUS | SCOPE | VALIDATION | Evidence / notes |
|---|---|---|---|---|---|---|
| K-SEM-001 | Danbooru canonical meaningとmodel-facing render surfaceは別レイヤー | SEMANTIC_AUTHORITY | ACCEPTED | GLOBAL_PRINCIPLE | NOT_REQUIRED | 03/08; semantic authority ledger |
| K-SEM-002 | Alias/implicationはsemantic relationであり、model response equivalenceの証明ではない | SEMANTIC_AUTHORITY | ACCEPTED | GLOBAL_PRINCIPLE | NOT_REQUIRED | 08; semantic authority ledger |
| K-SEM-003 | `tag exists` と `checkpoint recognizes it` は別 | SEMANTIC_AUTHORITY | ACCEPTED | GLOBAL_PRINCIPLE | NOT_REQUIRED | 03/08 |
| K-SEM-004 | canonical vs approved Alias vs alternate triggerの生成反応差 | PROJECT_HYPOTHESIS | HOLD | MODEL_VERSION:exact | STAGE10_REQUIRED | 09 A1 |
| K-SEM-005 | broad vs specificのsemantic hierarchyは保持するが、generationでどちらが強いかはtarget/model dependent | SEMANTIC_AUTHORITY | ACCEPTED | GLOBAL_PRINCIPLE | NOT_REQUIRED | 03/04/08 |
| K-SEM-006 | e621はDanbooru canonicalの代替ではなくnon-human taxonomyの補助 | SEMANTIC_AUTHORITY | ACCEPTED | GLOBAL_PRINCIPLE | NOT_REQUIRED | 08 |
| K-SEM-007 | e621 training exposureがNoobAIのnon-human hard-target性能を高めるか | OFFICIAL_MODEL | CANDIDATE | MODEL_VERSION:NoobAI-XL-1.1 | STAGE10_REQUIRED | 02; 09 A3 |

---

## C. WAI Illustrious v17

| ID | Claim | SOURCE | STATUS | SCOPE | VALIDATION | Evidence / notes |
|---|---|---|---|---|---|---|
| K-WAI-001 | WAI17 author guidance: Forge Neo, Euler a, Steps 15–30, CFG 5–7 | AUTHOR_GUIDE | ACCEPTED | MODEL_VERSION:WAI-v17 | NOT_REQUIRED | 02/10; WAI17 detailed profile |
| K-WAI-002 | WAI17 has integrated VAE; external VAE is not baseline requirement | AUTHOR_GUIDE | ACCEPTED | MODEL_VERSION:WAI-v17 | NOT_REQUIRED | 10 |
| K-WAI-003 | WAI17 author warns against excessive quality/aesthetic tags | AUTHOR_GUIDE | ACCEPTED | MODEL_VERSION:WAI-v17 | NOT_REQUIRED | 02/06/10 |
| K-WAI-004 | WAI17 author warns overly long Negative can reduce quality / add blur | AUTHOR_GUIDE | ACCEPTED | MODEL_VERSION:WAI-v17 | NOT_REQUIRED | 02/06/10 |
| K-WAI-005 | Project starting grammar `LEAN_TAG_FIRST` is likely suitable for WAI17 hard-target tests | PROJECT_HYPOTHESIS | CANDIDATE | PROFILE:WAI17_LOCAL_FIRST_20260909 | STAGE10_REQUIRED | 02/10 |
| K-WAI-006 | Practical baseline Steps 25 / CFG 6 / Euler a for first causal tests | PROJECT_HYPOTHESIS | CANDIDATE | PROFILE:WAI17_LOCAL_FIRST_20260909 | STAGE10_REQUIRED | 10 |
| K-WAI-007 | 1024x1024 causal square and 1024x1344 practical portrait are separate test uses | PROJECT_HYPOTHESIS | CANDIDATE | PROFILE:WAI17_LOCAL_FIRST_20260909 | STAGE10_REQUIRED | 10 |
| K-WAI-008 | Hires should be evaluated as separate confirmation pass, not folded into base Prompt success | AUTHOR_GUIDE | ACCEPTED | MODEL_VERSION:WAI-v17 / PROJECT_ONLY | NOT_REQUIRED | 05/06/10 |
| K-WAI-009 | WAI17 exact author primary source should be rechecked before final production promotion | AUTHOR_GUIDE | HOLD | MODEL_VERSION:WAI-v17 | LOCAL_RECHECK | 09 D1 |
| K-WAI-010 | Issue #30 plumbing fixture settings are not WAI17 Prompt-optimum settings | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 07/10; Issue #30 |

---

## D. NoobAI XL 1.1

| ID | Claim | SOURCE | STATUS | SCOPE | VALIDATION | Evidence / notes |
|---|---|---|---|---|---|---|
| K-NOOB-001 | Official caption structure places special tags before general tags | OFFICIAL_MODEL | ACCEPTED | MODEL_VERSION:NoobAI-XL-1.1 | NOT_REQUIRED | 02/08 |
| K-NOOB-002 | Official generation baseline: Euler a, CFG ~5–6, Steps ~25–30, ~1024² area | OFFICIAL_MODEL | ACCEPTED | MODEL_VERSION:NoobAI-XL-1.1 | NOT_REQUIRED | 02 |
| K-NOOB-003 | `SPECIAL_FIRST_NATIVE_CAPTION` is the strongest initial hard-target baseline | PROJECT_HYPOTHESIS | CANDIDATE | MODEL_VERSION:NoobAI-XL-1.1 | STAGE10_REQUIRED | 02 |
| K-NOOB-004 | Exact camera block position is officially known | LEGACY | REJECTED | MODEL_VERSION:NoobAI-XL-1.1 | NOT_REQUIRED | 09 D7: official camera placement not established |
| K-NOOB-005 | Canonical/Alias response difference should be tested without changing semantic identity | PROJECT_HYPOTHESIS | HOLD | MODEL_VERSION:NoobAI-XL-1.1 | STAGE10_REQUIRED | 02/09 |

---

## E. Illustrious XL

| ID | Claim | SOURCE | STATUS | SCOPE | VALIDATION | Evidence / notes |
|---|---|---|---|---|---|---|
| K-ILL-001 | Illustrious versions must not be flattened; v0.x/v1.x/v2+ and derivatives may differ | OFFICIAL_MODEL | ACCEPTED | FAMILY:Illustrious | NOT_REQUIRED | 02/09 |
| K-ILL-002 | v1.1 is more natural-language focused than v1.0 per official description | OFFICIAL_MODEL | ACCEPTED | MODEL_VERSION:Illustrious-v1.1 | NOT_REQUIRED | 02/08 |
| K-ILL-003 | `Illustrious = booru-only` is not a valid universal rule | OFFICIAL_MODEL | REJECTED | FAMILY:Illustrious | NOT_REQUIRED | 02 |
| K-ILL-004 | Exact-version tag-centered baseline plus short relation support is a reasonable test design | PROJECT_HYPOTHESIS | CANDIDATE | MODEL_VERSION:exact | STAGE10_REQUIRED | 02 |
| K-ILL-005 | WAI derivative behavior should not be generalized to Onoma base models | OFFICIAL_MODEL | ACCEPTED | FAMILY:Illustrious | NOT_REQUIRED | 02/08 |

---

## F. Anima

| ID | Claim | SOURCE | STATUS | SCOPE | VALIDATION | Evidence / notes |
|---|---|---|---|---|---|---|
| K-ANIMA-001 | Anima supports Danbooru-style tags, natural language, and mixtures | OFFICIAL_MODEL | ACCEPTED | FAMILY:Anima | NOT_REQUIRED | 02/08 |
| K-ANIMA-002 | Multiple-character prompts benefit from explicit basic appearance description per official guidance | OFFICIAL_MODEL | ACCEPTED | FAMILY:Anima | NOT_REQUIRED | 02 |
| K-ANIMA-003 | Tag mode officially uses `1girl/1boy/1other` style count tokens | OFFICIAL_MODEL | ACCEPTED | FAMILY:Anima | NOT_REQUIRED | 02/08 |
| K-ANIMA-004 | `1 girl` should replace `1girl` globally | COMMUNITY | REJECTED | FAMILY:Anima | NOT_REQUIRED | Toshiaki correction C1 |
| K-ANIMA-005 | “Qwen has a fixed ~1k token limit, therefore ~300 words” | COMMUNITY | REJECTED | FAMILY:Anima | NOT_REQUIRED | 09 D4; rationale incorrect |
| K-ANIMA-006 | `HYBRID_RELATION_AWARE` is promising for relation/binding hard cases | PROJECT_HYPOTHESIS | CANDIDATE | FAMILY:Anima | STAGE10_REQUIRED | 02/04 |
| K-ANIMA-007 | Appearance anchor ON/OFF is a high-value multi-actor A/B | PROJECT_HYPOTHESIS | CANDIDATE | FAMILY:Anima | STAGE10_REQUIRED | 02/04 |
| K-ANIMA-008 | BREAK behavior is parser/runtime scoped, not a universal Anima grammar fact | OFFICIAL_RUNTIME | ACCEPTED | RUNTIME:exact | LOCAL_RECHECK | 09 D5/E2 |
| K-ANIMA-009 | Exact Forge Neo Anima Turbo CFG=1 × Negative behavior | RESEARCH | HOLD | RUNTIME:Forge-Neo + PROFILE:Anima-Turbo | LOCAL_RECHECK | 09 D6 |

---

## G. Prompt construction / support

| ID | Claim | SOURCE | STATUS | SCOPE | VALIDATION | Evidence / notes |
|---|---|---|---|---|---|---|
| K-STRUCT-001 | hard-target内部診断では ACT/SITE/OBJECT/ACTOR/RELATION/POSE/VISIBILITYを分離する | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 03/04/05 |
| K-STRUCT-002 | 内部構造を細かくしてもuser入力項目を同数に増やさない | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 03 |
| K-STRUCT-003 | support presence is not evidence of support utility | PROJECT_FACT | ACCEPTED | GLOBAL_PRINCIPLE | NOT_REQUIRED | 03/09 B3 |
| K-STRUCT-004 | CORE_SUPPORT+ADDITIVE auto-selectionのgeneration benefit | PROJECT_HYPOTHESIS | HOLD | PROJECT_ONLY | STAGE10_REQUIRED | 09 B1 |
| K-STRUCT-005 | family-specific block order beyond official baseline | PROJECT_HYPOTHESIS | HOLD | MODEL_VERSION:exact | STAGE10_REQUIRED | 09 B2 |
| K-STRUCT-006 | one targeted support at a time is the preferred causal test method | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 07/10 |
| K-STRUCT-007 | simultaneous Special capacity has a fixed universal token threshold | LEGACY | REJECTED | GLOBAL_PRINCIPLE | NOT_REQUIRED | 09 B5 |

---

## H. Quality / camera / Negative / density

| ID | Claim | SOURCE | STATUS | SCOPE | VALIDATION | Evidence / notes |
|---|---|---|---|---|---|---|
| K-QUALITY-001 | More quality tags do not monotonically imply better final quality | AUTHOR_GUIDE | ACCEPTED | GLOBAL_PRINCIPLE with model scope | NOT_REQUIRED | 06; WAI evidence |
| K-QUALITY-002 | Generic long Negative is not a universal default | AUTHOR_GUIDE | ACCEPTED | GLOBAL_PRINCIPLE | NOT_REQUIRED | 06/09 |
| K-QUALITY-003 | Exact family-specific Negative profiles remain unresolved | PROJECT_HYPOTHESIS | HOLD | MODEL_VERSION:exact | STAGE10_REQUIRED | 09 C2 |
| K-QUALITY-004 | Anatomy-sensitive Negative collision with unusual target geometry | PROJECT_HYPOTHESIS | HOLD | TARGET_CLASS:geometry-sensitive | STAGE10_REQUIRED | 09 C1 |
| K-QUALITY-005 | Automatic numeric weighting should remain disabled until exact evidence exists | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 06/09 C4 |
| K-QUALITY-006 | Community numeric weights can be generalized globally | COMMUNITY | REJECTED | GLOBAL_PRINCIPLE | NOT_REQUIRED | 06/09 C5 |
| K-QUALITY-007 | Visibility/camera tags can change pose/relation/scale, not just observability | COMMUNITY | CANDIDATE | MODEL_VERSION:exact | STAGE10_REQUIRED | 06/09 B4 |
| K-QUALITY-008 | Prompt density should be measured by competing concepts/relations/support blocks, not raw token count alone | PROJECT_HYPOTHESIS | CANDIDATE | PROJECT_ONLY | STAGE10_REQUIRED | 06/09 B5 |

---

## I. Failure diagnosis / assisted control

| ID | Claim | SOURCE | STATUS | SCOPE | VALIDATION | Evidence / notes |
|---|---|---|---|---|---|---|
| K-FAIL-001 | target omission and wrong binding are distinct failure classes | RESEARCH | ACCEPTED | GLOBAL_PRINCIPLE | NOT_REQUIRED | 05; Attend-and-Excite/T2I-CompBench |
| K-FAIL-002 | multi-object/relation scenes are a distinct compositional difficulty class | RESEARCH | ACCEPTED | GLOBAL_PRINCIPLE | NOT_REQUIRED | 05 |
| K-FAIL-003 | Attribute leakage is a recognized compositional failure mode | RESEARCH | ACCEPTED | GLOBAL_PRINCIPLE | NOT_REQUIRED | 05 |
| K-FAIL-004 | Repeated same-class geometry/binding failure should trigger Prompt-only ceiling review instead of endless support expansion | PROJECT_HYPOTHESIS | CANDIDATE | PROJECT_ONLY | STAGE10_REQUIRED | 05/09 |
| K-CTRL-001 | Forge Couple/Regional are candidates for identity/attribute spatial separation | OFFICIAL_RUNTIME | ACCEPTED | RUNTIME:exact | LOCAL_RECHECK | 05 |
| K-CTRL-002 | ControlNet is a rational separate lane for persistent pose/layout failure | OFFICIAL_RUNTIME | ACCEPTED | RUNTIME:exact | LOCAL_RECHECK | 05 |
| K-CTRL-003 | ADetailer is a later detect/mask/inpaint intervention and must not prove base Prompt success | OFFICIAL_RUNTIME | ACCEPTED | GLOBAL_PRINCIPLE | NOT_REQUIRED | 05 |
| K-CTRL-004 | Hires/ADetailer/Control/regional assisted result is not PROMPT_ONLY evidence | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 05/07 |
| K-CTRL-005 | Automatic assisted-control escalation threshold is known | PROJECT_HYPOTHESIS | HOLD | PROJECT_ONLY | STAGE10_REQUIRED | 09 E6/G5 |

---

## J. Evaluation / Stage10 methodology

| ID | Claim | SOURCE | STATUS | SCOPE | VALIDATION | Evidence / notes |
|---|---|---|---|---|---|---|
| K-EVAL-001 | Evaluate target, binding, visibility, geometry, finished quality separately; do not use prettier-only winner | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 07 |
| K-EVAL-002 | WD EVA02 v3 training vocabulary filters tags with fewer than 600 training images | OFFICIAL_MODEL | ACCEPTED | MODEL_VERSION:WD-EVA02-v3 | NOT_REQUIRED | 07/09 |
| K-EVAL-003 | WD/global tagger threshold is not a universal rare/composite semantic threshold | PROJECT_HYPOTHESIS | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 07/09 |
| K-EVAL-004 | Unsupported/low-confidence machine evaluation should route to REVIEW, not automatic FAIL | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 07 |
| K-EVAL-005 | Relation/binding questions are generally not proven by independent tag confidence alone | RESEARCH | ACCEPTED | GLOBAL_PRINCIPLE | NOT_REQUIRED | 07 |
| K-EVAL-006 | Final Special2788 evaluator coverage/allocation is known | PROJECT_FACT | HOLD | PROJECT_ONLY | EXTERNAL_GATE | 09 F4 |
| K-TEST-001 | One experiment = one question | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 07/10 |
| K-TEST-002 | One seed is insufficient to establish a production Prompt rule | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 07/09 H1 |
| K-TEST-003 | Seed-specific failure classes should be preserved instead of reducing everything to win rate | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 07 |
| K-TEST-004 | `CONTROLLED_SAME_SETTINGS` and `FAMILY_OPTIMAL_BASELINE` are different experiment modes | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 07/09 H2 |
| K-TEST-005 | Resolution/aspect ratio is part of semantic test conditions | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 07/09 H3 |

---

## K. User effort / product behavior

| ID | Claim | SOURCE | STATUS | SCOPE | VALIDATION | Evidence / notes |
|---|---|---|---|---|---|---|
| K-UX-001 | More user choices are not automatically safer/better UX | PROJECT_HYPOTHESIS | CANDIDATE | PROJECT_ONLY | STAGE10_REQUIRED | 09 G2 |
| K-UX-002 | Recommended default + secondary alternatives may reduce repair/search burden | PROJECT_HYPOTHESIS | CANDIDATE | PROJECT_ONLY | STAGE10_REQUIRED | 01/09 |
| K-UX-003 | Selected Special must forever use identical surface token | LEGACY | HOLD | PROJECT_ONLY | STAGE10_REQUIRED | 09 G1 |
| K-UX-004 | Identity/provenance must remain traceable even if validated render surface differs | PROJECT_FACT | ACCEPTED | PROJECT_ONLY | NOT_REQUIRED | 01/03/08 |

---

# Current high-priority unresolved claims

The following should be checked before relevant production promotion:

1. `K-STRUCT-004` support auto-selection effectiveness
2. `K-STRUCT-005` family block order beyond official baseline
3. `K-SEM-004` canonical/Alias/render surface response
4. `K-QUALITY-004` anatomy-sensitive Negative collision
5. `K-QUALITY-007` visibility support side effects
6. `K-QUALITY-008` density / simultaneous concept pressure
7. `K-WAI-005/006/007` WAI17 local-first candidate profile effectiveness
8. `K-FAIL-004` Prompt-only ceiling criterion
9. `K-CTRL-005` assisted-control escalation threshold
10. `K-EVAL-006` final evaluator coverage/allocation

For full uncertainty inventory also read `09_HOLD_CONFLICT_AND_REVALIDATION.md`.

---

# Maintenance rule

When changing a claim:

- update this registry first or in the same management action
- update the relevant `0X_*.md` explanation if interpretation changed
- preserve old evidence in legacy source docs
- use Issue #5 checkpoint for material changes

Do not create a second “current claims” file.
