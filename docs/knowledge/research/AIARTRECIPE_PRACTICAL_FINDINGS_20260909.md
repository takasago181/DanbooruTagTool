# AIアートのレシピ — Practical Generation Findings for DanbooruTagTool

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-09

Status: `PRACTICAL_EXTRACTION_V1 / VIDEO_EXCLUDED`

Source audit companion:
`docs/knowledge/research/AIARTRECIPE_SITE_AUDIT_20260909.md`

## 0. Purpose

AIアートのレシピの記事群から、DanbooruTagToolの現在目的に再利用可能な **実生成の失敗パターン・support候補・モデル差仮説**を抽出する。

これは Prompt recipe collection ではない。

採用基準:
- canonical意味と独立していること
- exact model scopeを可能な限り保持すること
- 成功例より failure mechanism を優先すること
- free-English phraseは alternate surfaceとして保持すること
- LoRA/control/postprocessをbase capabilityから分離すること

動画記事は使用しない。

---

# 1. Repeated pattern: source/target/body-site binding is a dominant failure

## Evidence from site

複数記事で、画像内に必要componentが存在しても **作用先が間違う**。

Examples:
- peeing: 人物とfluidは出るが、visible penisに引っ張られてwrong sourceになる。
- enema: device/medical-like objectは出るがwrong body-siteやIV-like relationへ崩れる。
- natural-language Anima comparison: hand side / nipple side / urine destination等は指定しても完全ではない。
- object insertion: insertion themeは出てもimplement identityが曖昧。

## Durable decision

`ADOPT_PRACTICAL -> reinforces FACT_GENERAL binding model`

Adult/niche generationの評価では最低限:

`component presence -> source -> actor/owner -> target -> body-site -> action/state`

を分離する。

### Audit rule

`all nouns visible` は successではない。

For relation-specific Special:
- wrong source = FAIL
- wrong target = FAIL
- wrong body-site = FAIL
- relation invisible = UNCLEAR

### Prompt hypothesis

Tag-onlyでsource-targetが崩れる場合、特にAnimaでは concise factual English relation clauseをA/B候補にできる。

Example pattern only, not production grammar:
`[actor/source] + [action] + [target/body-site]`

This is `TEST_REQUIRED`, not mandatory support.

---

# 2. Repeated pattern: abstract play/theme words can be weaker than visible decomposition

## Site observations

- `wax play` のようなabstract play wordが弱く、visible action/material/locationへ分解した例。
- generic `object insertion` はimplement identityを固定せず、specific objectが重要になる例。
- enema conceptはdevice/body-site/actionが一語に圧縮され、wrong-siteへ崩れる。
- machine/tentacle scenes also benefit in examples from relation/location phrases rather than only broad theme label.

## Durable decision

`ADOPT_PRACTICAL`

When a Special is composite in meaning, failure should trigger **semantic-preserving visual decomposition**, not synonym stacking.

Candidate decomposition roles:
- actor/source
- implement/material
- action
- target/body-site
- topology/contact
- count
- visibility

### Critical boundary

Decomposition support is generation scaffolding, **not canonical definition**.

Do not rewrite one Special into its helper phrases silently.

---

# 3. Repeated pattern: category tags do not enforce exact count

## Site observations

Group-sex article explicitly reports requested multi-person counts drifting despite `orgy/gangbang` style tags.
Double-penetration examples add actor/count context because concept tag alone does not guarantee exact number/ownership.

## Durable decision

`ADOPT_PRACTICAL -> aligns with FACT_GENERAL composition limits`

Tags describing a social/sexual category are not reliable exact-count constraints.

### Audit

Separate:
- category/event presence
- actor count
- implement count
- target count
- simultaneous relation count

### Support hypothesis

Explicit count is `COUNT_SUPPORT`, not redundant decoration where count is intrinsic.

But repeated count tokens should not be stacked blindly; test minimal explicit count first.

---

# 4. Repeated pattern: learned trigger carries scene priors beyond its literal gloss

## Site observations

- `tentacles` may pull scene toward restraint/sexual contact even without separately spelling every action.
- `piledriver` may pull sexual pose/partner prior beyond generic “upside-down/folded” geometry.
- `peeing` plus visible penis can pull source toward the penis.
- broad group/sex concept can change number and layout rather than acting as an isolated semantic bit.

## Durable decision

`ADOPT_PRACTICAL`

Generation trigger should have two descriptions:
1. canonical/search meaning
2. empirical generation prior under exact model/version

Do not confuse them.

### New audit field candidate

For future local empirical history, record:
`observed_context_prior` such as:
- partner prior
- restraint prior
- source prior
- camera prior
- style prior
- body-site prior
- count/layout prior

This field is empirical/model-specific only.

---

# 5. Viewpoint / visibility support is not neutral

## Site observations

Piledriver/full-nelson articles show adding terms such as `from above`, feet/body visibility-related cues can materially alter composition.

## Durable decision

`ADOPT_PRACTICAL`

Visibility/framing support must be judged on two axes:
- does it make target predicate observable?
- does it alter geometry/pose enough to damage target?

### Audit

A target becoming visible after framing support does not prove support is semantically required.

Classify as:
- `VISIBILITY_HELPFUL_NO_COLLATERAL`
- `VISIBILITY_HELPFUL_GEOMETRY_CHANGED`
- `VISIBILITY_NEUTRAL`
- `VISIBILITY_HARMFUL`

---

# 6. Negative Prompt hacks can hide errors instead of solving them

## Site examples

- group scene article uses `eyes` negative to reduce visible face artifacts.
- enema article uses broad anatomy/sex-specific suppression to force body-site direction.
- site-wide recipes often contain generic quality/negative terms inherited across examples.

## Durable decision

`MIXED`

Useful observation: Negative can materially redirect output.

Rejected generalization: if a negative removes evidence of a failure, the underlying semantic/composition problem is not necessarily solved.

### Audit labels

- `NEGATIVE_TARGET_HELP`
- `NEGATIVE_COLLATERAL`
- `NEGATIVE_MASKED_FAILURE`
- `NEGATIVE_NO_EFFECT`
- `NEGATIVE_COLLISION_SUSPECTED`

For unusual anatomy/hard targets, broad anatomy/count negatives stay `TEST_REQUIRED`.

---

# 7. Anima practical evidence strengthens hybrid relation testing, not universal superiority

## Article evidence

The Anima-vs-Illustrious article tests:
- right-side body/hand ownership
- source→target urination
- real-world vs smartphone-screen separation
- specific environment relation
- two-character clothing/expression assignment

Several examples are better separated in Anima, while side-specific relation remains imperfect.

## Official corroboration

Anima author documentation supports:
- natural language
- tags
- hybrid prompts
- multi-character identity/appearance description
- tag dropout

## Durable decision

`ADOPT_PRACTICAL_MODEL_SPECIFIC`

For relation-heavy current project cases, a valuable Anima experiment is:

A: tag-only
B: same tags + one concise factual relation clause

Keep:
- same seed
- same profile (Base/Aesthetic/Turbo)
- same settings
- same concept set

Judge:
- target presence
- actor ownership
- body-site
- relation
- collateral composition

Do not infer Anima > WAI globally from site examples.

---

# 8. Anima Turbo site settings are independently corroborated

Site practical setup uses approximately:
- CFG 1
- 12 steps
- Euler

Official Anima documentation says Turbo is intended around:
- CFG 1
- 8–12 steps

## Decision

The **settings** are strongly corroborated.
The site's subjective ranking/quality statements remain practical.

Important:
Never merge Turbo outcome into Base/Aesthetic evidence.

---

# 9. WAI article knowledge must be version-tagged

Site history spans older WAI versions, including explicit V12 examples.
Current project target includes WAI v17.

## Durable decision

`ADOPT_VERSION_DISCIPLINE`

Every site-derived WAI claim receives:
- exact vX if article gives it
- `WAI_VERSION_UNKNOWN` otherwise
- no direct promotion to WAI v17 unless official/current test corroborates

### Example
`full nelson` article under WAI V12 demonstrates historical trigger ability, not v17 reliability.

---

# 10. Site confirms why prompt dictionary and generation trigger dictionary must stay separate

The encyclopedia mixes:
- exact Booru-like tags
- aliases/slang
- ordinary English phrases
- compositional phrases
- spelling errors

## Durable decision

This strongly supports a four-layer representation:

1. `canonical_identity`
2. `search_alias / UI wording`
3. `model_trigger_surface`
4. `free_relation_support_phrase`

A phrase may be useful in layer 3/4 without entering layer 1.

---

# 11. Internal contradiction example creates a source-quality rule

Older fluid article tests misspelled `ejucalation / ejecalation` and reports little/no effect.
Later article correctly uses `ejaculation` and obtains a visible effect.

## Durable decision

Before accepting a `DOES_NOT_WORK` claim:

1. spellcheck
2. canonical/alias lookup
3. exact model/version
4. ensure token is in intended language/syntax
5. check prompt conflict
6. only then treat as negative generation evidence

### Evidence consequence

A typo-based failure is `INVALID_EXPERIMENT`, not `MODEL_UNSUPPORTED`.

This rule should apply to all community/practical sources, not only this site.

---

# 12. Semantic gloss must be independently validated

Cross-section/internal-anatomy article contains a Japanese semantic mapping that conflates `impregnation` with implantation/着床-like meaning.

## Durable decision

`REJECT_SITE_GLOSS_AS_CANONICAL`

Even when generation screenshots are useful, article translation/meaning explanation can be wrong.

Separate:
- visual empirical observation = potentially useful
- semantic definition = verify with canonical evidence

---

# 13. Tagger comparison article is valuable mainly because it exposes hallucination

The image-to-prompt article demonstrates that different caption/tag systems can add:
- absent objects
- incorrect body/material location
- verbose invented details

## Durable decision

`ADOPT_AS_EVALUATOR_FAILURE_EVIDENCE`

Machine caption/tag output should be decomposed into:
- supported visible unary concepts
- uncertain relation/location
- hallucinated detail

Site author's single-image preference for WD14 is not sufficient for Special2788 evaluator selection.

---

# 14. LoRA and assisted control should be used as ceiling probes, not semantic proof

Site articles frequently solve hard concepts using:
- concept LoRA
- AnyTest / ControlNet-like shape assistance
- image edit

## Durable decision

These are useful product lanes but separate evidence identities.

Labels:
- `PROMPT_ONLY_SUCCESS`
- `ASSISTED_CONTROL_SUCCESS`
- `LORA_ASSISTED_SUCCESS`
- `POSTPROCESS_RESCUE`

If only assisted lane works, record that limitation instead of marking the original Prompt rule PASS.

---

# 15. Candidate practical interventions extracted from site

These are **A/B candidates only**, not automatic rules.

| Problem | Candidate intervention | Current status |
|---|---|---|
| wrong source/target | concise explicit source-action-target clause | Anima practical / cross-family TEST_REQUIRED |
| wrong body-site | specific body-site phrase + visibility check | PRACTICAL / TEST_REQUIRED |
| ambiguous object insertion | explicit implement identity | PRACTICAL |
| abstract play not recognized | decompose into visible material/action/site | PRACTICAL |
| exact count drift | explicit count/actor context | PRACTICAL + general support |
| trigger induces unwanted partner | carefully test `solo` or actor-count constraints | SCENARIO_TEST_REQUIRED |
| rare device relation | LoRA ceiling test after base Prompt ladder | ASSISTED_ONLY |
| multi-person count/layout | regional/ControlNet/AnyTest lane | ASSISTED_CONTROL |
| viewpoint hides target | one framing/visibility support | PRACTICAL |
| fluid source reversal | explicit source/body-site relation | PRACTICAL |
| old WAI trigger | re-test under v17 paired seeds | HISTORICAL -> TEST_REQUIRED |

---

# 16. Practical article trust scoring v1

For future aiartrecipe ingestion, calculate a qualitative evidence profile rather than one overall star.

Dimensions:

### Identity
- exact model/version stated: +
- only “Illustrious/WAI” generic: weak
- SeaArt moving snapshot: weak

### Controls
- fixed seed: +
- one variable changed: +
- exact CFG/steps/resolution: +
- several variables changed: weak

### Replication
- multiple predetermined outputs: +
- all failures retained: +
- best-shot only: weak

### Semantic integrity
- canonical/alias verified: +
- free phrase clearly labeled: +
- typo/gloss error: downgrade

### Confound
- no LoRA/control: clean Prompt evidence
- LoRA/control/inpaint explicitly separated: useful assisted evidence
- mixed without separation: downgrade

Possible result:
- `PRACTICAL_STRONG`
- `PRACTICAL`
- `PRACTICAL_WEAK`
- `INVALID_FOR_CLAIM`

Do not auto-map this to FACT.

---

# 17. Cross-domain knowledge gained

The most important cross-article insight is:

> For niche adult generation, **failure is often not lack of vocabulary. It is incorrect relational assignment under a strong learned scene prior.**

This applies to:
- fluid source/destination
- machine/device contact
- body-site insertion
- multi-character assignment
- restraint topology
- tentacle ownership
- exact count

Therefore the product should eventually distinguish:
- `TAG_UNKNOWN`
- `TAG_PRESENT_RELATION_WRONG`
- `RELATION_PARTIAL`
- `VISIBILITY_FAILURE`
- `COUNT_FAILURE`
- `TRIGGER_PRIOR_CONFLICT`

rather than one generic “did not work”.

---

# 18. What was not learned / remains HOLD

Site corpus does not establish:
- exact WAI v17 success probability for hard Specials
- exact NoobAI EPS relation superiority/weakness
- canonical vs Alias response equivalence
- universal broad+specific advantage
- universal natural-language superiority
- exact prompt weighting policy
- exact minimum number of seeds
- reliable automatic evaluator for relation/topology
- model-independent Negative recipe

These remain controlled-image-test questions.

---

# 19. Final extraction verdict

Keep AIアートのレシピ as a **Japanese practical failure-and-intervention corpus**.

Highest priority extraction order:
1. explicit failure description
2. exact model/version/settings
3. changed intervention
4. free relation phrase
5. successful output description
6. author's subjective recommendation

This reverses the usual recipe-site reading order and makes the source much more useful for DanbooruTagTool.
