# Stage10 PROMPT — AIartrecipe ingestion rules

最終更新: 2026-09-09
Owner: PROMPT / Issue #5
Status: source-ingestion contract candidate. **Not production specification.**

## Purpose

AIアートのレシピを継続的な日本語実践ソースとして利用しつつ、誤記・モデル局所性・安全上の不適合・古いplatform情報をproduction knowledgeへ混入させない。

## 1. Fundamental rule

**記事中に書かれている「Prompt」は1種類ではない。**
抽出時に必ず以下へ分類する。

- `DANBOORU_CANONICAL_VERIFIED`
- `DANBOORU_ALIAS_VERIFIED`
- `MODEL_TRIGGER_OBSERVED`
- `NATURAL_LANGUAGE_PHRASE`
- `SUPPORT_PHRASE`
- `QUALITY_META`
- `NEGATIVE_CANDIDATE`
- `UNKNOWN_TERM`

サイトが「Danbooru tag」と呼んでいても、外部確認までは `UNKNOWN_TERM` または `MODEL_TRIGGER_OBSERVED`。

## 2. Normalization gate

Before semantic import:
1. lowercase / underscore-space normalizing for comparison only
2. typo check
3. singular/plural distinction check
4. canonical/alias lookup
5. accidental merged phrase check
6. obvious English spelling check

Known site errors to use as regression fixtures:
- `collorbone` -> typo fixture
- `ejucalation` / `ejecalation` -> typo fixture
- `beastiality` -> typo + safety quarantine fixture

A failed generation with malformed spelling is **not** evidence of model ignorance.

## 3. Semantic-width gate

Japanese gloss must not be imported as canonical display without checking semantic width.

Regression fixtures:
- `tan` should not be collapsed to generic dark/brown skin
- `flat chest` should not be treated as literal anatomical absence
- `milf` should not be broadened to generic “sexy woman”

Possible uses of loose Japanese:
- `SEARCH_JA_CANDIDATE`
- user-intent colloquial evidence

Not allowed:
- exact display label promotion without semantic audit

## 4. Safety gate

Before all other adoption, classify content.

`SAFETY_QUARANTINE / DO_NOT_IMPORT` if reusable sexual Prompt knowledge involves:
- minors / ambiguous minors
- age-coded school-child sexualization
- non-consensual sexual activity
- sleeping/incapacitated sexual target
- animal-sex/bestiality

Quarantined article may remain in the site coverage ledger so that “we saw and intentionally excluded it” is traceable, but its explicit Prompt details must not enter reusable hard-target corpus.

## 5. Evidence level

### E4 `COMMUNITY_JA_STRONG`
Requirements (several preferred):
- exact model/version
- settings
- fixed/common Prompt
- multiple comparable samples
- explicit failure notes
- comparison design

### E3 `COMMUNITY_JA_USEFUL`
- model known
- useful generated example
- limited samples
- plausible observation

### E2 `COMMUNITY_JA_WEAK`
- single/few image
- settings or seed missing
- causal claim inferred from visual result

### E1 `IDEA_ONLY`
- lexical/scene idea with no generation evidence

No site article can become `OFFICIAL_FACT` solely through this site.

## 6. Model attribution

Every generation observation should record when available:
- model family
- checkpoint/version
- LoRA
- sampler
- steps
- CFG
- resolution
- seed or seed policy
- Hires.fix / ADetailer / ControlNet / Anytest / i2i

If model is missing:
- mark `MODEL_UNSPECIFIED`
- do not generalize effect

If assisted control is used:
- mark `ASSISTED_RESULT`
- do not count as Prompt-only success

## 7. Claim decomposition

Article prose such as “X makes Y happen” is split into:

1. `LEXICAL_CLAIM`
   - what phrase/tag means
2. `GENERATION_OBSERVATION`
   - what image appeared
3. `CAUSAL_HYPOTHESIS`
   - author’s explanation why
4. `RECOMMENDATION`
   - proposed workflow

Only (2) is direct experiment evidence. (3) requires A/B or external support.

## 8. Numeric weights

Site-specific weights are never globally adopted directly.

Store:
- token
- suggested weight
- model/version
- observed side effect

Status:
`LOCAL_WEIGHT_CANDIDATE`

Stage10 promotion requires:
- weight off vs on
- fixed prompt
- multiple seeds when practical
- target score + image quality score

## 9. Negative Prompt handling

Repeated site generic negative is treated as `SITE_BASELINE_NEGATIVE`, not universal optimum.

For each model family compare:
- minimum family baseline
- site baseline
- expanded negative only if targeted

Hard-target negative audit must check `NEGATIVE_COLLISION` with intended concept/body geometry.

## 10. Prompt-only ceiling evidence

When article reports:
- prompt failure followed by Anytest/ControlNet
- i2i correction
- LoRA needed
- manual redraw/edit

record both:
- `PROMPT_ONLY_FAILURE`
- `ASSISTED_SUCCESS`

Never collapse them to one success result.

## 11. Platform/tool pages

SeaArt / RunPod / API / cloud / extension-specific pages:
- classify `TIME_SENSITIVE_TOOL_NOTE`
- revalidate before current recommendation
- do not make them core Prompt semantics

Pages focused on bypassing hosted safeguards:
- classify `OUT_OF_SCOPE_PLATFORM_CIRCUMVENTION`
- do not import bypass procedure

## 12. License / commercial-use claims

Any article claim such as:
- commercial use OK
- no ToS risk
- license allows X

must be rechecked against:
- exact checkpoint
- exact current license
- model source
- derivative license
- current policy if applicable

Classification until verified:
`LEGAL_RECHECK_REQUIRED`

## 13. Promotion state machine

`SITE_OBSERVATION`
→ normalization
→ safety gate
→ canonical/phrase classification
→ semantic-width audit
→ model attribution
→ evidence level
→ conflict search
→ `ADOPT_CANDIDATE | HOLD | REJECT | SAFETY_QUARANTINE`
→ Stage10 A/B if material
→ only then possible production proposal.

## 14. High-value extraction targets

Prefer extracting:
- failure reason
- what exact support changed result
- relation / binding problems
- visibility problems
- model-specific differences
- Prompt-only limit
- negative/quality side effects
- Japanese user-intent vocabulary

De-prioritize:
- clickbait prose
- affiliate recommendations
- generic praise
- uncited legal claims
- copy-paste Prompt blocks without model context

## 15. Revisit policy

Because the site is active and has 2026 updates, a future refresh should:
1. revisit sitemap
2. diff new non-video article URLs/titles
3. audit only delta articles
4. never silently overwrite previous evidence classification
5. record changed claims as `SUPERSEDED` or `CONFLICT`

## Boundary

- PROMPT-only research artifact.
- KNOWLEDGE #44 unchanged.
- production data unchanged.
- video-focused pages excluded per user instruction.
