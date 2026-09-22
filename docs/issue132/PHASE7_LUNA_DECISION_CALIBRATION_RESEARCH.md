# Issue #132 — Phase 7 Luna decision-calibration research

Date: 2026-09-23 JST
Status: **RESEARCH / PRE-HANDOFF CALIBRATION / DO NOT START FULL CODEX RUN YET**

## 1. Why this phase exists

The full 31,003-identity semantic census remains the completion scope.

The unresolved problem is not coverage. It is **decision calibration**.

If the instructions overemphasize safety:
- Luna can collapse toward KEEP / SEARCH_ONLY / UNRESOLVED;
- genuine multi-entry discovery improvements will be missed.

If the instructions overemphasize discoverability:
- Luna can add every technically related route;
- color variants, body-token families, object/place fixtures, and other combinatorial families can flood browse shelves;
- the app becomes noisier rather than easier.

The goal is therefore:

> first-pass high recall for plausible usability improvements, followed by a stricter precision gate before anything becomes production metadata.

This separates **finding candidates** from **approving runtime changes**.

---

## 2. Research findings that affect the protocol

### A. Task framing matters as much as individual ambiguity

Annotation research repeatedly shows that disagreement can come from the way the task is formulated, not only from inherently ambiguous examples.

Implication for #132:

Do not ask one vague question such as:
> "Is this tag correctly classified?"

Instead ask separate questions about:
1. semantic meaning;
2. current discovery fit;
3. whether a missing route is a natural starting point;
4. whether that route adds useful discovery rather than technical overlap.

### B. Guidelines should be iterated on disagreement examples

Recent LLM-assisted annotation research reports that improving the guideline from observed disagreements can substantially improve annotation agreement.

Implication for #132:

Before the 31,003-row run, use a bounded calibration pack to expose:
- false KEEP bias;
- over-eager secondary-route bias;
- misuse of SEARCH_ONLY;
- family-wide copy decisions.

The calibration pack is **not** used to discover all #132 gaps. Full review still covers all 31,003 identities.

### C. Prior suggestions can anchor later judgments

Research on LLM-assisted annotation shows that exposing annotators to prior model suggestions can shift the final label distribution.

Implication for #132:

The Luna first-pass queue should **not expose normative machine verdicts** such as:
- machine_bucket=OK;
- Phase 1 suggested classification;
- prior ADD_SECONDARY proposal;
- prototype route suggestion;
- "high-risk" / "safe" labels.

It may expose factual current state:
- current routes;
- current #64 path;
- current #76 facets;
- #118 content intent;
- Japanese/search surfaces;
- usage count.

Machine heuristics should be revealed only in a later consistency/audit pass.

### D. Danbooru itself uses multiple discovery mechanisms

Danbooru discovery is not based on a single exhaustive directory. Search/autocomplete, aliases, and tag groups coexist.

Implication for #132:

Not every tag needs a browse route.

A searchable proper noun, meme, event, or highly idiosyncratic identity can legitimately remain search-oriented.

At the same time, curated subject-group discovery is valuable when the user knows the concept area but not the exact tag.

### E. "Technically related" is not enough

Danbooru's implication guidance explicitly warns against over-creating broad/frivolous relationships because they add bloat without useful value.

#132 discovery routes are not Danbooru implications, but the product lesson transfers:

> do not add a secondary route merely because the relationship is logically true.

The route must improve actual lookup.

External research references are listed at the end of this document.

---

## 3. Problem in the current draft protocol

The current `FULL_SEMANTIC_REVIEW_PROTOCOL.md` is intentionally conservative, but three parts can bias Luna too far toward no-change:

1. any secondary-route proposal is automatically RESEARCHED;
2. KEEP is described as the preferred outcome over speculative improvement;
3. Luna is currently asked to emit a final production-like decision on the first pass.

This mixes two different jobs:
- candidate discovery;
- production approval.

They should be separated.

---

## 4. Proposed two-stage semantic decision model

### Stage A — Luna full census: discovery-oriented first pass

Every one of the 31,003 identities is reviewed.

Luna outputs a **first-pass disposition**, not a production verdict.

Allowed first-pass dispositions:

- `KEEP_STRONG`
- `SECONDARY_CANDIDATE`
- `BORDERLINE_DISCOVERY`
- `SEARCH_ORIENTED`
- `UPSTREAM_CANDIDATE`
- `SEMANTIC_UNRESOLVED`

This pass should favor **recall without auto-promotion**.

A plausible improvement should not be forced into KEEP merely because the evidence is not yet strong enough for production.

Use `BORDERLINE_DISCOVERY` for understood concepts where browse usefulness is genuinely arguable.

### Stage B — post-census precision gate

After all identities have been seen:

1. aggregate all SECONDARY_CANDIDATE and BORDERLINE rows;
2. detect inconsistent sibling/family decisions;
3. compute route-load impact;
4. expose prior machine signals only at this stage;
5. deep-review the candidate/change population;
6. produce final:
   - KEEP
   - ADD_SECONDARY
   - UPSTREAM_REVIEW
   - SEARCH_ONLY
   - UNRESOLVED

Destructive changes to #64/#76 never happen in #132 itself.

---

## 5. Balanced admission gate for SECONDARY_CANDIDATE

A missing route should be marked `SECONDARY_CANDIDATE` when the reviewer can answer **YES** to A, B, and D, and does not have a clear NO on C.

### A. Core semantic fit

Does the proposed route describe a **core visible/scene-defining meaning** of the tag?

Good:
- standing_doggystyle -> POSE_POSITION
- biting_breast -> BODY_SITE
- sex_hair -> HAIR_FACE

Weak:
- a route matches only a token/modifier but is not a meaningful way to understand the whole tag.

### B. Independent lookup intent

Could a user who does **not know the tag name** reasonably start from that route?

The question is not:
> "Is this tag related to X?"

It is:
> "If I wanted this visual concept but did not know the Danbooru term, would X be a natural place to look?"

### C. Browse-noise / combinatorial risk

Would adding this route preserve a coherent shelf, or is this mainly a Cartesian-product modifier family?

Examples requiring caution:
- color + target variants;
- generic size + target variants;
- incidental location words;
- object/place relationships where the second interpretation is weak.

A high-volume family is not automatically rejected, but it should become BORDERLINE if the route benefit is mostly mechanical and direct Japanese search is already easy.

### D. Evidence beyond token matching

At least one of the following must exist:

**D1 — two aligned tracked signals**
Examples:
- #64 meaning/path + #76/generation metadata;
- canonical/Japanese meaning + accepted Special facet;
- current path + accepted neighboring semantic family.

or

**D2 — one strong direct semantic source**
Examples:
- Danbooru wiki/official tag documentation clearly describes the relevant semantic axis;
- another authoritative source is necessary for a domain-specific concept.

A canonical string token alone is not sufficient.

---

## 6. The four useful "middle" states

The protocol needs to distinguish cases that the old schema collapses.

### KEEP_STRONG

Current discovery already covers the important user mental model.

A technically possible secondary route is not enough.

### SECONDARY_CANDIDATE

There is a strong, independently useful missing entrance.

This is **not yet production approval**.

### BORDERLINE_DISCOVERY

Meaning is understood, but one of these is uncertain:
- independent lookup value;
- redundancy with search/current facets;
- shelf coherence;
- family-scale noise.

This is a valuable output and should not be treated as review failure.

### SEARCH_ORIENTED

The identity is primarily name-specific:
- proper noun;
- event;
- meme;
- franchise-specific reference;
- idiosyncratic title.

Browse placement would be more confusing than search/autocomplete.

SEARCH_ORIENTED is not the same as semantic uncertainty.

---

## 7. When external web research is actually required

Do **not** require a web lookup for every potential improvement.

That would make the full run slow and can bias Luna toward KEEP merely to avoid research.

### Repository-only CHECKED is allowed when

- meaning is obvious;
- current accepted metadata gives aligned semantic evidence;
- proposed first-pass disposition is not destructive;
- confidence is high.

### RESEARCHED is required when

- meaning itself is unclear;
- proper noun/meme/domain term must be interpreted;
- accepted sources conflict;
- Luna proposes UPSTREAM_CANDIDATE;
- the route choice depends on a subtle distinction not settled by tracked metadata;
- confidence is not high.

A first-pass SECONDARY_CANDIDATE may therefore be CHECKED when it has strong aligned tracked evidence.

Final production ADD_SECONDARY can still receive a stricter second-pass review.

---

## 8. Strong / borderline / negative anchor examples

These are calibration anchors, not bulk rules.

### Strong SECONDARY_CANDIDATE anchors

#### standing_doggystyle -> POSE_POSITION
Current ACTION_CONTACT remains useful.
The standing positional/sexual-position meaning is core and independently discoverable.

#### presenting_own_ass -> POSE_POSITION
Action/contact and pose are distinct natural lookup intents.

#### sex_hair -> HAIR_FACE
The hair state is the visible defining feature; BODY_SITE alone is not the only natural entrance.

#### biting_breast -> BODY_SITE
The body target is explicit and central, not incidental.

These examples establish that the protocol must not be so conservative that obvious multi-axis concepts collapse to KEEP.

### Strong KEEP / no-new-top-level anchors

#### off_shoulder
Current General CLOTHING already projects to Unified CLOTHING_EXPOSURE.
Do not add a redundant new top-level route merely because a lower-level state distinction exists.

### BORDERLINE anchors

#### blue_bikini -> COLOR_PATTERN_SHAPE
Color is semantically true and visually important, but this belongs to a large combinatorial color+target family and is generally easy to search directly.
Do not automatically reject or automatically add. Use BORDERLINE unless stronger product evidence resolves it.

#### automatic_door -> SCENE_BACKGROUND
It can function as a fixture/environment element, but object identity may remain the dominant lookup intent.
BORDERLINE is preferable to family-wide object/place expansion.

### SEARCH_ORIENTED anchor

#### atsuko's_grin_(meme)
Do not manufacture a visual category from the name alone.
Research may identify a stable visual pattern, but absent a genuinely useful existing route, search-oriented handling is valid.

---

## 9. Anti-bias rules for the Luna first pass

### Do not show these columns initially

- machine_bucket
- machine_review_signals
- Phase 1 pattern
- Phase 1 suggested classification
- previous confidence
- prototype override target
- prior KEEP/ADD recommendation

They can anchor the reviewer.

### Show factual context

- identity_key
- canonical / English
- Japanese display/search terms
- aliases
- usage/post count
- current #64 paths
- current #76 kind/body/theme
- #118 content intent
- current Unified route IDs
- overlap status

### Row order

Grouping similar rows is useful for consistency.

However, avoid giving one family a "default verdict".

Every row still receives independent reasoning.

---

## 9.5. Current generated queue is not yet suitable for Luna

Inspection of the current generated `codex_full_review_queue.csv` found two problems.

### Problem 1 — it exposes anchoring labels

It currently contains:
- `machine_bucket`
- `review_lane`
- `machine_review_signals`

These are useful for DEV/AUDIT but should not be in the Luna first-pass view.

The first-pass input should use a separate **neutral review view**.

### Problem 2 — it is missing searchability facts

The current queue does not yet carry enough factual search metadata to judge whether browse adds value.

Before the final handoff, the neutral view should include:

- canonical identity;
- display Japanese;
- Japanese search keys;
- approved aliases;
- usage/post count;
- current #64 paths;
- current #76 kind/body/theme;
- #118 intent;
- current Unified routes;
- General/Special overlap.

These facts already exist in the production catalog input chain:
- Danbooru canonical source supplies post count;
- normalized alias index supplies aliases;
- production Japanese overlay supplies General display/search Japanese;
- accepted Special Japanese/promotion metadata supplies Special display/search Japanese.

This metadata should be **joined at research/build time only**.

It does not imply new runtime metadata.

### Recommended separation

Produce two files:

`luna_neutral_review_input.csv`
- factual fields only;
- no prior suggestions or machine risk labels.

`dev_audit_context.csv`
- machine bucket;
- heuristic patterns;
- prior candidate signals;
- route-load context;
- prototype history.

Luna first pass receives only the neutral view.

The DEV/AUDIT comparison pass may join both views after Luna has committed its first-pass disposition.

---

## 10. Cross-census consistency checks

After Luna finishes all rows, machine analysis becomes useful again.

It may flag, but not decide:

### Sibling inconsistency

Example:
- biting_breast -> SECONDARY_CANDIDATE BODY_SITE
- biting_ass -> KEEP_STRONG
- kissing_breast -> BORDERLINE

Flag the family for comparison.

This may be legitimate, but it requires an explanation.

### Route-growth alarm

Compute how many candidate additions each route would gain.

Do not impose a fixed quota.

Instead flag:
- unusually concentrated additions;
- a family that dominates a route;
- large growth caused by one modifier pattern.

The response is semantic review, not automatic rejection.

### Decision-distribution alarm

No percentage is a pass/fail target.

However:
- near-total KEEP;
- near-total SECONDARY_CANDIDATE;
- one route receiving almost all changes;
- widespread LOW confidence

are instruction-calibration warnings.

They trigger review of the guideline, not forced rebalancing of labels.

---

## 11. Why quotas are explicitly rejected

A rule such as:
- "at least 5% must change"
- "no more than 10% may change"

would create the exact wrong incentive.

The correct final number of changes is unknown.

Use distributions only as **diagnostics for reviewer bias**.

---

## 12. No sample calibration pack

A fixed 32/64/100-row calibration pack is **rejected** for #132.

Reason:

- hand-picked examples can overrepresent known failure modes;
- the reviewer can become tuned to the examples rather than the real population;
- a small benchmark can look balanced while missing entire semantic families;
- #132 is core product behavior, so the calibration authority must be the actual 31,003-identity population.

Therefore:

- do not use a sample pack to approve the instruction;
- do not infer population-wide quality from a bounded test;
- do not tune Luna to match a curated answer key.

### Full-population calibration loop

Use the actual full review as the calibration surface:

1. generate a neutral factual input for **all 31,003 identities**;
2. Luna performs a first-pass disposition for all identities;
3. run mechanical diagnostics across the complete population:
   - decision distribution;
   - route-growth distribution;
   - family/sibling inconsistency;
   - concentration by token/modifier family;
   - confidence distribution;
   - unresolved/search-oriented distribution;
4. inspect the full-population anomaly clusters, not a curated sample;
5. if the instruction is demonstrably biased, revise it;
6. rerun the affected stage over the **full population**, not a hand-selected subset.

The full population is the calibration set.

The purpose of diagnostics is to detect instruction bias, not to impose quotas.

---

## 13. Recommended final architecture of the review

```
31,003 factual neutral rows
        |
        v
Luna full semantic first pass
(all rows seen)
        |
        +-- KEEP_STRONG
        +-- SECONDARY_CANDIDATE
        +-- BORDERLINE_DISCOVERY
        +-- SEARCH_ORIENTED
        +-- UPSTREAM_CANDIDATE
        +-- SEMANTIC_UNRESOLVED
        |
        v
mechanical consistency + route-load audit
(no semantic auto-decisions)
        |
        v
higher-reasoning review of candidates/conflicts
        |
        v
minimal production delta only
        |
        v
existing UnifiedBrowseRouteIds / UnifiedBrowseIndex
```

This gives Luna room to surface plausible improvements without giving it authority to pollute production browse metadata.

---

## 14. Performance / code-complexity compatibility

This calibration model changes only the **research pipeline**.

No first-pass disposition, reasoning, evidence URL, or review history ships at runtime.

Production still receives only:
- confirmed minimal secondary route metadata;
- upstream fixes separately promoted through their owner authority.

No new runtime recommendation/classification engine is needed.

---

## 15. Current conclusions before writing the final Codex instruction

Recommended changes from the older draft:

1. Keep all-31,003 review.
2. Remove 200-row shard semantics as a reasoning boundary; use continuous review with periodic persistence/checkpoints.
3. Do not expose machine normative labels to Luna on first pass.
4. Replace first-pass production verdicts with six calibrated dispositions.
5. Add explicit BORDERLINE_DISCOVERY.
6. Separate SEARCH_ORIENTED from SEMANTIC_UNRESOLVED.
7. Allow strong repository-evidence SECONDARY_CANDIDATE without mandatory web lookup.
8. Require stricter evidence only at the final production gate.
9. Use a 64-row calibration pack before the full run.
10. Use distribution/family/route-growth checks as bias alarms, never quotas.

The existing Codex handoff should remain inactive until this calibration phase is accepted.

---

## External research references

- Bibal et al. (2025), *Automating Annotation Guideline Improvements using LLMs: A Case Study*  
  https://aclanthology.org/2025.comedi-1.13/

- Dsouza & Kovatchev (2025), *Sources of Disagreement in Data for LLM Instruction Tuning*  
  https://aclanthology.org/2025.comedi-1.3/

- Oortwijn et al. (2021), *Interrater Disagreement Resolution: A Systematic Procedure to Reach Consensus in Annotation Tasks*  
  https://aclanthology.org/2021.humeval-1.15/

- James (2026), *Counting on Consensus: Selecting the Right Inter-Annotator Agreement Metric for NLP Annotation and Evaluation*  
  https://aclanthology.org/2026.lrec-1.347/

- Lee et al. (2025), *Just Put a Human in the Loop? Investigating LLM-Assisted Annotation for Subjective Tasks*  
  https://aclanthology.org/2025.findings-acl.1323/

- Danbooru, *Howto:Get Started* — autocomplete, aliases, and tag groups as complementary discovery mechanisms  
  https://safebooru.donmai.us/wiki_pages/howto%3Aget_started

- Danbooru/Konachan-style implication guidance — avoid frivolous broad relationships that add bloat without useful value  
  https://konachan.net/help/tag_implications
