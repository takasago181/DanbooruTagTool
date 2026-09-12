# Batch M — Japanese Practical Source Audit: NoobAI / Anima

Owner: Issue #44 `KNOWLEDGE:#44`
Date: 2026-09-13
Status: `JP_SOURCE_AUDIT_COMPLETE`

## Purpose

Japanese practical sources are unusually valuable for this project because they contain:
- Forge Neo-specific operation
- actual local-generation failure modes
- model migration habits
- LoRA ecosystem observations
- Anima multi-character / relation prompting patterns
- current Japanese community tool choices

They are also high-risk for version drift and personal recipes.

This audit classifies sources by **what they are allowed to prove**.

---

# 1. Source ranking

## J-A — high-value current practical reference

Can support practical workflow statements when version/date is preserved.
Cannot override exact author facts.

### としあきdiffusion Wiki — Anima
URL:
https://wikiwiki.jp/sd_toshiaki/Anima

Why valuable:
- recent active maintenance
- Forge Neo-specific current operation
- Base/Aesthetic/Turbo distinction
- natural-language relation examples
- multiple-character failure discussion
- high-resolution and control-tool notes
- community troubleshooting

Important limitations:
- collaborative Wiki; errors are explicitly possible
- some sections lag latest official file versions
- “official recommended” wording must be checked against the actual official card before promotion

Adopt for:
- failure discovery
- practical operator guidance
- Anima-specific Japanese terminology/examples
- current tool routing

Do not use alone for:
- official exact parameter claims
- current file version identity
- universal success-rate claims

### としあきdiffusion Wiki — Illustrious-XL / NoobAI
URL:
https://wikiwiki.jp/sd_toshiaki/Illustrious-XL

Why valuable:
- EPS vs V-Pred distinction
- current runtime pitfalls
- model-merge metadata warning
- long historical context of Illustrious/Noob derivatives
- Japanese adult/niche practical ecosystem awareness

Important limitation:
The page mixes current material with older model history and derivative recommendations.

Adopt for:
- V-Pred setup failure modes
- community model-family context
- derivative discovery

Do not use alone for:
- exact current Noob official settings
- derivative “best model” ranking
- claims that a specific derivative never fails on hard adult targets

### としあきdiffusion Wiki — LoRA / Anima LoRA
URLs:
https://wikiwiki.jp/sd_toshiaki/LoRA
https://wikiwiki.jp/sd_toshiaki/%E5%88%9D%E3%82%81%E3%81%A6%E3%81%AELoRA%E4%BD%9C%E3%82%8A%EF%BC%88anima%E7%B7%A8%EF%BC%89

Adopt:
- base-family compatibility warning
- Anima-specific training ecosystem existence
- practical weight/context-leak troubleshooting as hypotheses

Bound:
- one-image/instant LoRA is an experimental shortcut, not the project default definition of a robust LoRA
- exact image counts / weight bands remain practical heuristics unless independently tested

---

# 2. J-B — detailed individual practical experiments

Useful because the author actually generated images/settings and compares behavior.
Treat as one environment/sample set, not model ground truth.

### Crody — complete Anima generation guide
URL:
https://note.com/crody/n/n937474cf1c23

High-value parts:
- explicit distinction among ComfyUI / Forge Neo / Diffusers-Anima roles
- structured Prompt workflow
- author-used sampler / CFG / resolution habits
- actor/action/camera/background organization
- tag + natural-language hybrid examples
- Illustrious-to-Anima Prompt migration thinking

Do not promote directly:
- personal `CFG 5` preference as official optimum
- personal ~1280-square pixel budget as universal optimum
- long personal Negative list as project default
- exact weighting habits as universal Anima grammar

Project use:
`PRACTICAL_RECIPE / HYPOTHESIS / STRUCTURE_SOURCE`

### 秋葉原IT戦略研究所 — Turbo v1.1 vs Base
URL:
https://note.com/akb428/n/nc794be92ebc2

High-value parts:
- recent Turbo v1.1 local comparison
- exact observed generation-time comparison
- same seed/prompt does not preserve composition between Base and Turbo
- structural example showing Base can outperform Turbo in one sample while other seeds can reverse outcomes
- explicitly avoids claiming Turbo always breaks more

Project use:
- supports the caution that Turbo is a distinct generation regime, not simply Base-at-fewer-steps
- useful motivation for profile-correct comparison

Do not promote:
- one machine's speed multiplier as universal
- one structural example as a general Base-superiority claim

### かみもと — Raw/Turbo/Aesthetic comparison
URL:
https://note.com/sepiablue/n/nc0b2feee1ae8

High-value parts:
- broad visual comparison of official family profiles
- practical speed/VRAM/context comparison

Project use:
`PRACTICAL_COMPARATIVE_EVIDENCE`

Do not treat as author truth.

---

# 3. J-C — ecosystem / installation aids

### EasyForgeNeo Japanese README
URL:
https://github.com/hirorohi03/EasyForgeNeo/blob/main/README_JP.md

High-value parts:
- Japanese current installation convenience
- active tracking of Anima official files and current Forge Neo ecosystem
- useful indicator of what Japanese Forge-Neo users can install easily

Authority boundary:
- installation helper, not model-behavior authority
- exact behavior claims should route to Forge Neo / model author source

### AirMore model comparison
URL:
https://airmore.ai/ja/ai-review/local-anime-ai-image-models-comparison

Useful:
- transparent Civitai API-based approximate ecosystem counts
- NoobAI/Anima/Illustrious/Pony asset-ecosystem comparison

Important freshness defect found:
- article still characterizes Anima as ComfyUI-centered / Forge not recommended
- current maintained Forge Neo explicitly supports Anima 2B and newer variants

Therefore:
- ecosystem count/context can be cited cautiously
- runtime compatibility conclusions are stale and rejected for current project use

### selesteia AI model comparison
URL:
https://prompt.selesteia.com/articles/anime-ai-model-hikaku-2026

Useful:
- practical daily-use perspective
- model-family comparison

Rejected blanket wording:
- “Illustrious / NoobAI / WAI LoRAs can simply all be shared” is too strong for project knowledge

Project rule remains:
`family proximity -> candidate compatibility -> per-LoRA test`.

---

# 4. Japanese-source conclusions worth keeping

## NoobAI

High-confidence practical conclusions:
- EPS and V-Pred must be separated operationally
- V-Pred runtime detection/configuration can fail when model metadata is lost through merging
- the Noob/Illustrious ecosystem is large enough that LoRA search should include both Noob-specific and Illustrious-family candidates
- bare/base Noob checkpoints may not provide a stable preferred art style; artist/style LoRA or derivative checkpoints can be useful when visual consistency matters

Still hypothesis/test-required:
- V-Pred reliably beats EPS at dark scenes/contrast for project targets
- every Illustrious LoRA works on Noob
- one named derivative is universally best for hard adult content

## Anima

High-confidence practical conclusions:
- current Forge Neo is a valid daily GUI runtime
- Anima requires its own prompt-surface habits; blindly carrying SDXL tricks over is risky
- explicit actor descriptions and relation wording are a serious practical lane for multi-character scenes
- Aesthetic and Turbo are not settings presets; they are distinct model files/profiles
- Turbo at CFG1 changes the role of Negative conditioning
- official Anima LoRA training should use Base
- Anima LoRAs are a separate asset family from SDXL/Illustrious/Noob LoRAs

Still hypothesis/test-required:
- exact tag-only vs hybrid win rate
- exact actor-binding ceiling
- exact best high-resolution workflow
- exact optimal LoRA weight bands
- exact Base/Aesthetic/Turbo success rates on hard relation targets

---

# 5. Version-drift traps found

1. **Anima official repository files moved ahead of old profile naming**
   - Base v1.0 remains
   - Aesthetic v1.1 exists
   - Turbo v1.1 exists
   - exact hash should be retained

2. **Forge Neo articles age very quickly**
   - current maintained `Haoming02/sd-webui-forge-classic` supports Anima directly
   - older “ComfyUI only / Forge unsupported” statements are stale

3. **NoobAI generic articles often collapse EPS and V-Pred**
   - any source that gives one sampler/CFG recipe for “NoobAI” without version must be downgraded

4. **Preview-era Anima knowledge remains searchable**
   - settings/examples from preview/pre-release should not become Base/Aesthetic/Turbo defaults

5. **Turbo LoRA vs Turbo checkpoint confusion**
   - early Anima ecosystem used speed LoRAs
   - official Turbo checkpoint now exists; these are not the same evidence state

---

# 6. Recommended source usage policy going forward

For NoobAI/Anima questions:

1. read exact current official model card/file first
2. confirm exact model/profile/version/hash
3. check current Forge Neo/tool source when runtime behavior matters
4. use としあきWiki for Japanese operational/failure knowledge
5. use detailed Note/blog comparisons for practical hypotheses
6. use Reddit/forums only to discover failure patterns or disagreements
7. keep unresolved effectiveness questions in HOLD until controlled local evidence exists

Do not cite a generic “anime model comparison” page as the sole source for exact settings.

---

# 7. Current Japanese practical source shortlist

## Tier A — regularly worth rechecking
- としあきdiffusion Wiki — Anima
- としあきdiffusion Wiki — Illustrious-XL / NoobAI
- としあきdiffusion Wiki — LoRA / Anima LoRA
- EasyForgeNeo Japanese README

## Tier B — comparison / workflow
- Crody Anima guide
- 秋葉原IT戦略研究所 Anima comparisons
- かみもと Anima comparisons

## Tier C — discovery only / verify upstream
- general SEO comparison articles
- Civitai commentary without version pins
- Reddit anecdotes
- old Preview-era blog posts

---

# Sources

Primary upstream sources used to correct Japanese material:
- https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- https://huggingface.co/Laxhar/noobai-XL-Vpred-1.0/blob/main/README.md
- https://huggingface.co/circlestone-labs/Anima/blob/main/README.md
- https://huggingface.co/circlestone-labs/Anima/tree/main/split_files/diffusion_models
- https://github.com/Haoming02/sd-webui-forge-classic/tree/neo
- https://github.com/Haoming02/sd-forge-couple
- https://github.com/Haoming02/ADetailer-Neo

Japanese sources:
- https://wikiwiki.jp/sd_toshiaki/Illustrious-XL
- https://wikiwiki.jp/sd_toshiaki/Anima
- https://wikiwiki.jp/sd_toshiaki/LoRA
- https://wikiwiki.jp/sd_toshiaki/%E5%88%9D%E3%82%81%E3%81%A6%E3%81%AELoRA%E4%BD%9C%E3%82%8A%EF%BC%88anima%E7%B7%A8%EF%BC%89
- https://note.com/crody/n/n937474cf1c23
- https://note.com/akb428/n/nc794be92ebc2
- https://note.com/sepiablue/n/nc0b2feee1ae8
- https://github.com/hirorohi03/EasyForgeNeo/blob/main/README_JP.md
- https://airmore.ai/ja/ai-review/local-anime-ai-image-models-comparison
- https://prompt.selesteia.com/articles/anime-ai-model-hikaku-2026
