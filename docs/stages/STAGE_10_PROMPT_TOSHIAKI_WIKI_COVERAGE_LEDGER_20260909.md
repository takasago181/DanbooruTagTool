# Stage10 PROMPT Toshiaki diffusion Wiki coverage ledger

最終更新: 2026-09-09  
Owner: PROMPT / Issue #5  
Status: coverage/evidence ledger. **Not production specification.**

## Scope

Source root: `https://wikiwiki.jp/sd_toshiaki/`

User instruction:
- Prompt knowledgeを学習・監査・記録
- 動画は対象外

The Wiki page list contains hundreds of pages. This ledger records the **Prompt-relevant and generation-control surfaces audited for Stage10/PROMPT use**, not every unrelated infrastructure/history page.

---

## A. Root / navigation / trust context

### FrontPage
Status: `COVERED`
Use:
- site structure
- self-declared research/community nature
- explicit warning that old/wrong information may exist
Decision:
- whole site cannot be ground truth.

### page list / RecentChanges
Status: `COVERED`
Use:
- page inventory
- recency triage
Decision:
- page last-modified is metadata only; claim date still needed.

---

## B. Prompt syntax / semantics

### Danbooru語
Status: `COVERED / HIGH_VALUE`
Last-modified observed: 2026-07-28
Knowledge:
- canonical Danbooru search surface vs AI Prompt surface
- underscore/space distinction
- escaping parenthesized tags
Labels:
- `COMMUNITY_VALIDATED`
- `UI_PARSER_SCOPED`

### 特殊なPrompt指定
Status: `COVERED / HIGH_VALUE`
Last-modified observed: 2026-07-12
Knowledge:
- weighting
- schedule/prompt editing
- alternating
- escape
- AND
- BREAK
Decision:
- A1111 syntax confirmed independently where applicable.
- cross-architecture behavior remains parser/environment-scoped.

### Negative Prompt / ネガティブプロンプト
Status: `COVERED / MIXED`
Knowledge:
- CFG/negative interaction
- generic negative concepts
Decision:
- model-specific profile overrides generic advice.
- old boilerplates not auto-ingested.

### prompt / Prompt / prompt(呪文)解説 family
Status: `PARTIALLY COVERED THROUGH CURRENT/SUBPAGES`
Note:
- some legacy/redirect surfaces were not independently retrievable as stable pages during crawl.
- relevant active knowledge was covered through Danbooru語, 特殊なPrompt指定, model pages, Tips and prompt-sharing pages.

---

## C. Experiment / variation / automation

### Dynamic Prompts
Status: `COVERED / HIGH_VALUE`
Last-modified observed: 2026-08-13
Knowledge:
- wildcard
- variant syntax
- combinatorial generation
- nested structures
- scene variation
Independent verification:
- official `adieyal/sd-dynamic-prompts`
Decision:
- `ADOPT_CANDIDATE` for Stage10 automation, resolved Prompt required.

### X/Y/Z plot
Status: `COVERED / HIGH_VALUE_CONCEPT`
Knowledge:
- Prompt S/R
- same-seed controlled comparison
Decision:
- experimental principle useful.
- operational implementation may be superseded by #30 automation.

### Prompt matrix
Status: `SURFACE_REVIEWED`
Decision:
- useful as historical/alternative matrix mechanism.
- Dynamic Prompts combinatorial + #30 automation likely better fit for current workflow.

---

## D. Model-family pages

### Illustrious-XL
Status: `COVERED / HIGH_VALUE_WITH_VERSION_RISK`
Last-modified observed: 2026-07-31
Critical note:
- page itself indicates substantial content remains early/v0.1-derived.
Knowledge:
- Danbooru tag exposure
- rare/weak tag limitations
- tag ordering / quality conventions
- support-tag heuristics
Decision:
- `VERSION_SCOPED` mandatory.
- generic negative guidance must not override WAI v17 author instructions.

### Anima
Status: `COVERED / HIGH_VALUE_WITH_CORRECTIONS`
Last-modified observed: 2026-07-30
Knowledge:
- official-like tag/meta scheme
- NL/hybrid usage
- appearance/role relation tips
- Base/Aesthetic/Turbo distinctions
Corrections:
- count tag spacing claim conflicts with official `1girl/1boy` examples.
- Qwen “1k token limit” rationale not accepted.
- BREAK claims environment scoped.
Decision:
- strong Japanese practical supplement, never above official card.

### 初めてのanima
Status: `COVERED / ORIENTATION`
Last-modified observed: 2026-07-28
Use:
- Forge Neo workflow orientation
- beginner current environment
Decision:
- setup guidance only, not model grammar authority.

### SDXL / Animagine XL / Pony-related pages
Status: `SURFACE_REVIEWED / CONTEXT`
Use:
- historical family differences
- why generic SDXL advice exists
Decision:
- not primary Stage10 target; use only when tracing inherited practices.

---

## E. Forge / assisted control

### Forge neo
Status: `COVERED / HIGH_VALUE`
Last-modified observed: 2026-07-28
Knowledge:
- architecture support
- extension compatibility
- Forge Couple / Regional / WD tagger orientation
Decision:
- current environment-relevant.
- verify exact compatibility against extension repos/version before operational dependence.

### 初めてのForge-Neo
Status: `COVERED / ORIENTATION`
Last-modified observed: 2026-07-31
Use:
- UI/workflow context
- Wiki explicitly prioritizes ease over strict technical completeness
Decision:
- operational orientation only.

### 初めての拡張機能
Status: `COVERED / USEFUL`
Knowledge:
- TagComplete
- Dynamic Prompts Neo
- extension discovery
Decision:
- extension identity/version must be independently checked.

### Forge Couple surfaces
Status: `COVERED + OFFICIAL VERIFIED`
Independent verification:
- `Haoming02/sd-forge-couple`
Knowledge:
- regional conditioning
- Forge Neo + Anima support
- checkpoint-following limitation
Decision:
- high-value assisted-control escalation candidate.

### Regional Prompter / Composable LoRA / ControlNet
Status: `SURFACE_REVIEWED`
Decision:
- relevant to assisted-control architecture, but not promoted from Wiki alone.
- exact Anima compatibility must be version checked.

---

## F. Evaluator / interrogation / tools

### WD1.4 Tagger
Status: `COVERED / DATED_RANKING`
Last-modified observed: 2026-04-13
Knowledge:
- tagger/interrogator workflow
- model variants
Decision:
- useful tool orientation.
- ranking claims are time-scoped.
- Tagger is not Special2788 semantic ground truth.

### img2img / Inpaint-related surfaces
Status: `SURFACE_REVIEWED`
Knowledge:
- masked correction
- local negative intervention
Decision:
- assisted control candidate when Prompt-only ceiling reached.

---

## G. Community prompt corpora

### みんなの呪文広場
Status: `COVERED / RAW_HIGH_RECALL`
Last-modified observed: 2026-08-09
Knowledge:
- composition snippets
- camera
- depth
- motion/wind
- prompt randomization
Decision:
- `RAW_COMMUNITY` only.
- candidate discovery, not causal fact.

### 万能便利呪文
Status: `COVERED / HISTORICAL_ONLY`
Last-modified observed: 2022-10-22
Knowledge:
- old NAI/early SD negative/positive templates
Decision:
- quarantine from modern WAI/NoobAI/Anima defaults.

### Tips
Status: `COVERED / PER-ENTRY_ONLY`
Knowledge:
- mixed scratchpad across years
- old ChatGPT/weighted-prompt practices
- current Forge/extension notes mixed together
Decision:
- no page-level trust.
- each entry gets date/model verification.

---

## H. Settings affecting Prompt conclusions

### CFG Scale
Status: `COVERED / TECHNICAL_CONTEXT`
Knowledge:
- model-dependent CFG
- CFG=1 and negative-conditioning implications
- low-step side effects
Decision:
- settings are part of Prompt audit metadata.
- numeric defaults remain model/profile scoped.

### Sampling method / sampler
Status: `COVERED / HISTORICAL_MIXED`
Decision:
- model creator recommendation has priority.

### Seed
Status: `COVERED / STABLE_CONCEPT`
Decision:
- fixed seed remains required for controlled A/B where appropriate.
- exact RNG behavior/environment still traceable.

### Upscaler / Hires.fix
Status: `SURFACE_REVIEWED`
Decision:
- second-pass effects can change semantics/anatomy; Prompt audit should distinguish base generation from Hires-assisted final output.

---

## I. Coverage classes

`HIGH_VALUE`
- Danbooru語
- 特殊なPrompt指定
- Dynamic Prompts
- X/Y/Z plot concept
- Illustrious-XL (version scoped)
- Anima (with corrections)
- Forge neo
- Forge Couple evidence

`USEFUL_CANDIDATE`
- 初めての拡張機能
- CFG Scale
- WD1.4 Tagger
- img2img/Inpaint guidance
- related support-tag practices

`RAW_COMMUNITY`
- みんなの呪文広場
- model-unspecified Tips entries

`HISTORICAL_ONLY`
- 万能便利呪文
- old sampler/negative/weighting defaults
- pre-SDXL generic recipes unless independently revalidated

`CONTRADICTED/HOLD`
- Anima count spacing global rule
- Anima Qwen 1k-limit rationale
- WAI v17 inheritance of generic Illustrious long-negative advice
- universal BREAK-on-Anima rule

---

## J. Exclusions / limitations

- Videos excluded by user instruction.
- Unrelated infra/history/theory pages were not exhaustively converted into Prompt knowledge.
- Comments are low-trust unless they contain reproducible/version-pinned evidence.
- The Wiki changes over time; this ledger represents the 2026-09-09 audit snapshot and must not be treated as frozen external truth.
