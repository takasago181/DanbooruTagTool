# Batch E — Existing Prompt Surface Classification

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-13

Backlog item: `K-RB-01 Existing-Prompt surface/type interpretation`

Status: `RESEARCH_PASS_V1 / NO_PRODUCT_PROMOTION`

## Purpose

Beginner-first v1 starts from **understanding an existing Prompt**. A pasted Prompt cannot safely be interpreted as a flat comma-separated list of Danbooru tags.

The same Prompt field may contain:

- Danbooru-origin semantic tags
- historical/Alias surfaces
- model-specific quality/rating/trigger surfaces
- free natural-language fragments
- runtime weighting/control syntax
- LoRA / hypernetwork references
- textual-inversion embedding names
- extension template syntax such as Dynamic Prompts wildcards
- raw/unknown text

This batch defines a **non-destructive surface-classification model**. It does not define final UI, does not optimize/rewrite Prompt text, and does not claim generation effectiveness.

---

## 1. Primary evidence

### Danbooru / Safebooru current help

Current `help:tags` states that Danbooru has five tag categories:

- artist
- character
- copyright
- general
- meta

Important category meanings:

- **artist** — creator of the individual artwork
- **character** — character identity
- **copyright** — source work/series/franchise material
- **meta** — information generally beyond image-content semantics
- **general** — other objective image-content descriptors

`howto:tag` also preserves the `Tag what you see` principle.

Sources:
- https://safebooru.donmai.us/wiki_pages/help%3Atags
- https://safebooru.donmai.us/wiki_pages/howto%3Atag
- existing project audit: `DANBOORU_WIKI_SEMANTIC_AUDIT_20260909.md`

### AUTOMATIC1111 WebUI prompt/runtime syntax

Current A1111 feature documentation confirms that Prompt text can also contain runtime syntax that is not a Danbooru tag identity:

- attention/emphasis wrappers: `(word)`, `[word]`, `(word:1.5)`
- long-prompt chunking and uppercase `BREAK`
- Prompt editing: `[from:to:when]`, `[to:when]`, `[from::when]`
- alternating text: `[a|b]`
- composable-prompt operator `AND`
- LoRA reference: `<lora:filename:multiplier>`
- hypernetwork reference: `<hypernet:filename:multiplier>`
- textual inversion: embedding filename used directly in Prompt text

Sources:
- https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Features
- https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Textual-Inversion

### Forge Neo

Forge Neo describes itself as a continuation/fork of Forge built on A1111 and states that most base features of the original Automatic1111 WebUI should still function.

Source:
- https://github.com/gi0baro/forge-neo

Boundary:
This is compatibility evidence, not proof that every A1111 parser behavior is identical in the user's exact local Forge Neo build. Exact promotion-critical runtime claims still require local remote/commit pinning (`H-K-017`).

### Dynamic Prompts Neo

Dynamic Prompts Neo has its own template language, including:

- wildcard references such as `__folder/name__`
- alternatives/combinations such as `{a|b|c}` and counted forms
- variables such as `$${...}`

These are **template surfaces before resolution**, not Danbooru canonical tags.

Source:
- https://github.com/RJSprod/sd-dynamic-prompts_neo/blob/main/helptext.html

---

## 2. Core conclusion

### Do not use one flat `TAG` type

Existing Prompt interpretation needs at least three axes:

1. **surface class** — what kind of text/runtime object this is;
2. **semantic identity** — whether it maps to a canonical/Alias concept;
3. **wrapper/execution behavior** — whether runtime syntax changes how/when the payload is conditioned.

Example:

`(looking_at_viewer:1.2)`

should not be reduced to either:
- one unknown raw token, or
- plain `looking_at_viewer` with the weighting silently discarded.

Instead retain:
- semantic payload candidate: `looking_at_viewer`
- wrapper: A1111 attention weight `1.2`
- original raw surface: `(looking_at_viewer:1.2)`

This separation is essential for explanation without destructive rewriting.

---

## 3. Proposed surface classes

These are KNOWLEDGE interpretation classes, not production schema yet.

### S1 — `DANBOORU_CANONICAL`

Exact current canonical lookup succeeds.

Subcategory should remain available:
- GENERAL
- CHARACTER
- COPYRIGHT
- ARTIST
- META

Rules:
- canonical identity is preserved exactly;
- category says what Danbooru considers the tag, not what a model will do with it;
- Meta is not automatically a `quality tag`, and General is not automatically generation-effective.

### S2 — `DANBOORU_ALIAS_OR_HISTORICAL`

The surface resolves through an approved current Alias or is explicitly retained as a historical surface with provenance.

Rules:
- display canonical target separately;
- preserve raw source surface;
- implication/related/co-occurrence must not enter this class;
- historical model-trigger usefulness is a separate generation claim.

### S3 — `MODEL_OR_RECIPE_TRIGGER`

Known Prompt surface whose role comes from exact model author guidance, training/caption convention, or explicitly scoped project evidence rather than Danbooru canonical identity.

Examples may include model-specific quality/rating/control words, but exact membership belongs to later model-family research (`K-RB-07` / `K-RB-10`).

Rules:
- never silently label as canonical Danbooru;
- require model/version/source scope when making behavior claims;
- if only community-known, retain lower evidence status.

### S4 — `FREE_NATURAL_LANGUAGE`

A phrase/sentence fragment that is intentionally natural language or cannot be safely reduced to one canonical tag.

Examples:
- relation clauses
- descriptive prose
- Anima-style mixed text when exact context supports it

Rules:
- preserve text as text;
- do not fuzzy-map each word into unrelated tags merely to maximize coverage;
- semantic explanation may be phrase-level.

### S5 — `RUNTIME_ATTENTION_WRAPPER`

A1111-style weighting/emphasis wrapper.

Recognized examples:
- `(text)`
- `((text))`
- `[text]` when used as attention reduction rather than Prompt editing
- `(text:1.2)`

Important:
The wrapper and inner payload are separate interpretation objects.

### S6 — `RUNTIME_CONTROL_OPERATOR`

Prompt runtime syntax that changes execution/chunking/composition over time rather than naming image content.

Examples from A1111 documentation:
- uppercase `BREAK`
- `AND`
- `[from:to:when]`
- `[to:when]`
- `[from::when]`
- `[a|b]`

Rules:
- do not send these surfaces to Danbooru lookup as ordinary tags first;
- inner text may itself contain semantic surfaces and should be recursively interpreted where safe;
- grammar recognition must happen before naive bracket stripping.

### S7 — `EXTRA_NETWORK_REFERENCE`

Explicit runtime asset reference.

Recognized A1111 examples:
- `<lora:filename:multiplier>`
- `<hypernet:filename:multiplier>`

Rules:
- filename is local asset identity, not canonical tag identity;
- multiplier is runtime parameter;
- the network may have separate trigger words elsewhere in the Prompt, which must not be conflated with the `<lora:...>` token itself.

### S8 — `TEXTUAL_INVERSION_REFERENCE`

Embedding reference.

A1111 textual inversion documentation says a pre-trained embedding is invoked by using its filename in the Prompt.

Critical ambiguity:
Unlike `<lora:...>`, textual inversion may have **no distinctive inline syntax**. A token may look like ordinary text.

Therefore:
- classify as embedding only if local/runtime inventory confirms the name;
- without environment evidence, keep it ambiguous rather than guessing.

### S9 — `EXTENSION_TEMPLATE_SYNTAX`

Preprocessing/template language owned by an extension.

Current local-relevant example: Dynamic Prompts Neo.

Recognizable forms include:
- `__wildcard__`
- `{a|b|c}` / counted combination forms
- `$${variable...}`

Rules:
- unresolved template text is not the same as final resolved Prompt;
- if generation evidence matters, preserve the **resolved Prompt** actually sent to the runtime;
- do not treat every brace/underscore form as Dynamic Prompts without extension/context evidence.

### S10 — `CONTEXT_DEPENDENT_CONTROL_TEXT`

Text whose meaning depends on an enabled extension/UI mode and cannot be inferred safely from Prompt string alone.

Example:
Forge Couple can interpret prompt lines as separate spatial/region conditions depending on mode and configuration. A newline alone is therefore not proof of a region boundary.

Rules:
- require runtime/extension context;
- plain text remains plain text when the required feature is not active/known.

### S11 — `UNKNOWN_OR_AMBIGUOUS`

No confident canonical, Alias, runtime, extension, embedding or natural-language interpretation.

Rules:
- preserve raw text;
- expose uncertainty;
- do not force fuzzy nearest-tag conversion;
- candidate suggestions may be shown separately from the interpreted identity.

This class is a valid result, not parser failure.

---

## 4. Required interpretation order

Recommended knowledge-level order for an existing Prompt segment:

1. preserve exact raw text and source channel (Positive / Negative / other)
2. detect explicit runtime/extension wrappers/operators first
3. parse inner payload without discarding wrapper metadata
4. detect explicit extra-network references
5. check locally known embedding names when environment inventory exists
6. exact canonical lookup
7. exact approved Alias lookup
8. known exact-model/project trigger registry
9. phrase/natural-language interpretation
10. only then consider fuzzy/search candidates
11. unresolved remains `UNKNOWN_OR_AMBIGUOUS`

Why runtime syntax comes first:
`[word]` and `[from:to:when]` are not safely handled by stripping brackets and looking up the remainder as one tag.

Why exact semantic lookup comes before fuzzy:
A raw unknown token must not silently become a visually similar or substring-colliding canonical tag.

---

## 5. Positive vs Negative is a channel, not a tag type

A semantic surface can occur in Positive or Negative Prompt.

Therefore store/interpret:

- surface class
- semantic identity, if any
- **conditioning channel/polarity**

separately.

`bad_hands` in Negative Prompt is not a new semantic category merely because it is negative-conditioned.

This keeps current KNOWLEDGE rule intact:
Negative Prompt is an active semantic intervention, not a bag of harmless cleanup words.

---

## 6. Danbooru categories must remain visible

For beginner explanation, exact canonical matches should retain Danbooru category because the categories answer different questions:

- **General** — what is visibly present/state/action/attribute?
- **Character** — who is this character?
- **Copyright** — which source work/series is this from?
- **Artist** — who created the source artwork identity represented by the tag?
- **Meta** — metadata/technical/context information beyond ordinary image-content description.

Do not collapse Artist into generic `style`.
Do not collapse Copyright into character identity.
Do not explain Meta as ordinary visual attribute by default.

Generation models may respond stylistically or compositionally to some of these surfaces, but that is a separate model-specific claim.

---

## 7. Important ambiguities / failure traps

### Trap A — comma split != tag identity

A comma-separated segment may be:
- one canonical tag
- natural-language text
- weighted text
- an unresolved extension result
- a model trigger
- a local embedding name.

Comma splitting is only segmentation assistance, not semantic proof.

### Trap B — brackets have multiple grammars

A1111 uses brackets for both attention reduction and Prompt editing/alternation forms.

Therefore a parser must recognize structure before deciding that `[...]` is simply negative weighting.

### Trap C — underscore does not prove Danbooru

Dynamic Prompt wildcard notation and local asset names can contain underscores. Conversely many generation Prompts use spaces where Danbooru canonical identity uses underscores.

Exact dictionary lookup/provenance is required.

### Trap D — embedding names are invisible runtime references

Embedding invocation can look like ordinary words. Without local embedding inventory, a confident interpretation may be impossible.

### Trap E — `BREAK` is case/runtime-sensitive

A1111 documentation specifies uppercase `BREAK` as the chunk operator. Do not globally reinterpret every lowercase `break` string as runtime control.

### Trap F — extension state matters

Dynamic Prompts and Forge Couple can preprocess/partition Prompt text. The same raw text can mean something different when the extension/mode is not enabled.

### Trap G — model trigger != canonical meaning

A model accepting a quality/rating/artist-like surface does not make that surface a Danbooru canonical General tag.

---

## 8. Suggested interpretation record shape

Not a production schema; shown to clarify required information separation.

```text
raw_surface
source_channel = POSITIVE | NEGATIVE | OTHER
surface_class
runtime_wrapper/operator
inner_payload
canonical_tag?
danbooru_category?
alias_source?
model_scope?
local_asset_identity?
confidence
notes / ambiguity
```

For nested surfaces, use parent/child structure rather than destructive normalization.

Example:

```text
raw_surface: (looking_at_viewer:1.2)
surface_class: RUNTIME_ATTENTION_WRAPPER
runtime_wrapper: attention_weight=1.2
inner_payload:
  surface_class: DANBOORU_CANONICAL
  canonical_tag: looking_at_viewer
  danbooru_category: general
```

Example:

```text
raw_surface: <lora:Rella_Style:0.7>
surface_class: EXTRA_NETWORK_REFERENCE
local_asset_identity: Rella_Style
runtime_parameter: 0.7
canonical_tag: null
```

Example:

```text
raw_surface: some_unknown_word
surface_class: UNKNOWN_OR_AMBIGUOUS
canonical_tag: null
confidence: low
raw_preserved: true
```

---

## 9. What this batch does NOT establish

This research does not establish:

- final product parsing schema
- exact Forge Neo local parser parity with current A1111
- which quality/rating tokens each model responds to
- Prompt ordering optimum
- whether a particular free phrase improves generation
- automatic Prompt cleanup/removal rules
- automatic conversion of free text into canonical tags
- generation success of any Special

Those remain separate research/product questions.

---

## 10. Durable conclusions proposed for later Claim review

Candidate durable statements after evidence review:

1. Existing Prompt surfaces are heterogeneous; not every comma-separated segment is a Danbooru tag.
2. Runtime/extension syntax must be separated from semantic tag identity before explanation.
3. Wrapper/operator metadata and inner semantic payload should be preserved separately.
4. Textual-inversion references may be indistinguishable from ordinary text without local asset inventory.
5. Unknown/ambiguous is a valid interpretation state and must not be force-mapped by fuzzy search.
6. Danbooru category identity should be retained for exact canonical matches because General/Character/Copyright/Artist/Meta have different semantic roles.
7. Positive/Negative is conditioning-channel metadata, not a semantic tag-category replacement.

No Claim Registry row is promoted in this batch. Consolidate after K-RB-02/K-RB-03 evidence review so the explanation model is coherent rather than fragmented.

---

## 11. Next research dependency

Next backlog item:

`K-RB-02 Prompt semantic-role decomposition for explanation`

K-RB-02 should answer:

> Once a surface has been classified safely, what beginner-facing semantic role does its **content** play in the Prompt?

Keep surface/runtime class and semantic role as separate axes.
