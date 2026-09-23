# Issue #132 — Full semantic review protocol v2

Date: 2026-09-23 JST
Status: **PRE-HANDOFF RESEARCH CONTRACT / ALL 31,003 IDENTITIES MUST BE SEEN**

## 1. Product objective

#132 exists to make Danbooru tags easier to find for image generation.

The target user may know:
- the visual result;
- body part;
- action;
- pose;
- clothing state;
- prop;
- scene;
- camera;
- style;

without knowing the exact Danbooru tag.

The goal is:

> 作りたい画像から、必要なタグへ迷わず辿り着けること。

This is not a taxonomy-completeness project.

The final UI/runtime must remain simple and lightweight.

---

## 2. Completion scope

The complete ordinary runtime identity population — **31,003 identities** — must receive an explicit semantic review.

No machine label may remove rows from the review.

No bounded sample may be used as proof that the full population is correct.

The full population itself is the evaluation surface.

---

## 3. Four-stage method

### Pass A — independent discovery map

Luna reviews every identity **without seeing current browse placement**.

For each identity, decide:
- what the tag means visually;
- whether browse is useful or name-search is more natural;
- which existing Unified route(s) a user would naturally open before knowing the exact tag;
- CORE vs SUPPORTING strength.

Pass A does **not** decide KEEP / ADD / CHANGE.

Authority:
- `docs/issue132/LUNA_DISCOVERY_ROUTE_SEMANTIC_CONTRACT.md`

### Pass B — deterministic diff

After Pass A is complete, compare the independent map to current #64/#76/Unified behavior.

Machine-derived states:

- COVERED
- MISSING_CORE_ROUTE
- MISSING_SUPPORTING_ROUTE
- CURRENT_ROUTE_NOT_REPRODUCED
- MISSING_LOCAL_REFINEMENT
- MISSING_BODY_FACET
- MISSING_THEME_FACET
- ROUTE_VOCABULARY_GAP
- SEARCH_ORIENTED
- SEMANTIC_UNRESOLVED

These are review queues, not automatic product edits.

### Pass C — full-population product reconciliation

Join:
- current routes;
- #64/#76 metadata;
- #118 content intent;
- Japanese search keys;
- aliases;
- usage/post count;
- route-load counts;
- recurring semantic families;
- current local/body/theme facets.

Determine whether a semantically natural missing route provides enough **incremental discovery value** to justify runtime metadata.

### Pass D — production precision gate

Only confirmed deltas become:
- KEEP
- ADD_SECONDARY
- UPSTREAM_REVIEW
- SEARCH_ONLY
- UNRESOLVED

#132 does not directly rewrite #64/#76 authority.

---

## 4. Pass-A neutral input

Pass A receives only the GitHub-reproducible neutral projection defined by:

`docs/issue132/LUNA_NEUTRAL_INPUT_CONTRACT.md`

Fields:

- review_seq
- identity_key
- source_surfaces

If those surfaces are not enough to understand a tag, Luna must use RESEARCHED rather than rely on hidden current-product metadata.

Current route/taxonomy/search/popularity context is deliberately hidden.

### Explicitly hidden in Pass A

- current Unified route IDs
- #64 primary/secondary path
- #76 kind/body/theme classification
- #118 sexual intent/status/evidence
- General/Special membership
- Japanese production overlay/search keys
- aliases
- usage/post count
- machine_bucket
- heuristic family labels
- Phase 1 proposals
- prototype overrides
- previous KEEP/ADD suggestions
- route-load counts

These return only after the independent map is frozen.

---

## 5. Pass-A output

Every identity produces:

- identity_key
- manual_seen = YES
- semantic_summary_ja
- discovery_mode
  - BROWSE_WORTHY
  - MIXED
  - SEARCH_ORIENTED
  - SEMANTIC_UNRESOLVED
- route_1_id
- route_1_strength = CORE / SUPPORTING
- route_1_reason_ja
- route_2_id
- route_2_strength
- route_2_reason_ja
- route_3_id
- route_3_strength
- route_3_reason_ja
- local_refinement_ids = zero or more existing local refinement IDs
- body_site_ids = zero or more existing fixed body-site IDs
- theme_ids = zero or more existing fixed theme IDs
- route_vocabulary_gap = YES / NO
- route_vocabulary_gap_note
- review_depth = CHECKED / RESEARCHED
- evidence_urls
- uncertainty_note

Zero routes is valid.

Normally use one or two routes.

A third route is valid only when it represents another independently natural image-generation lookup intent.

No new route IDs may be invented during review.

---

## 6. CHECKED vs RESEARCHED

### CHECKED

Allowed when:
- meaning is clear from accepted display/search metadata;
- route intent is obvious;
- no subtle domain knowledge is needed.

### RESEARCHED

Required when:
- canonical/Japanese meaning is unclear;
- meme/event/proper reference must be understood;
- route choice depends on a subtle distinction;
- semantic confidence is not high;
- the identity appears internally contradictory.

Pass A is allowed to research externally when needed.

It is **not** required to browse the web for every row.

---

## 6.5. Local refinement capture

Pass A also records existing local refinement intent independently.

This exists to catch a different class of usability problem:

> 大分類には辿り着けるが、その先の絞り込みが不自然または不足している。

Allowed local IDs and their parent routes are defined in:

`docs/issue132/LUNA_DISCOVERY_ROUTE_SEMANTIC_CONTRACT.md`

Important ownership rule:

- local-refinement mismatch is an upstream #64 consistency signal;
- #132 does not create a parallel local taxonomy overlay;
- the field is research-only and does not increase runtime cost.

---

## 7. Route-selection question

The route question is:

> If the user wanted this visual but did not know its Danbooru tag, which shelf would they naturally open?

Not:
- which words occur in the canonical;
- which concepts are technically related;
- which current route should be confirmed;
- which route would maximize coverage.

A route is a discovery path, not an ontology assertion.

---

## 8. Full-population bias detection

No quota is used.

After Pass A, diagnose across all 31,003 identities:

- route-selection distribution;
- CORE/SUPPORTING distribution;
- SEARCH_ORIENTED distribution;
- SEMANTIC_UNRESOLVED distribution;
- route co-assignment patterns;
- route-vocabulary-gap distribution and repeated missing-axis notes;
- body-site/theme selection distribution;
- body/theme gaps versus current Special-backed facets;
- sibling/family inconsistency;
- concentration caused by modifier families;
- repeated route triples;
- RESEARCHED/CHECKED distribution.

Suspicious distributions trigger guideline review.

They do not trigger forced label balancing.

Examples:
- almost every identity receives exactly its current route after comparison;
- nearly all color-modified tags receive COLOR;
- almost no identity receives multiple routes;
- nearly every sexual-position concept receives only ACTION;
- huge unresolved concentration in one semantic family.

If the guideline is materially biased, revise it and rerun the affected stage over the full population.

Do not validate a correction using only a curated subset.

---

## 9. Product reconciliation dimensions

A missing route is not automatically shipped.

Evaluate it on four separate dimensions.

### A. Semantic centrality

Is this route CORE or merely SUPPORTING?

### B. Independent lookup intent

Would a user reasonably start here before knowing the tag?

### C. Incremental discovery value

Does this route add useful navigation beyond:
- Japanese search;
- aliases;
- current routes;
- body/theme/local facets?

Search sufficiency is evidence, not an automatic rejection.

### D. Shelf coherence / population cost

After adding all similar candidates:
- does the route remain understandable;
- or does one combinatorial family swamp the shelf?

This is measured over the full population.

---

## 10. Important balanced cases

### Multi-axis concepts should survive

The process must be capable of recognizing:
- action + body target;
- action + pose/sexual position;
- body + hair/face state;
- clothing + exposure/state

when each route is independently useful.

### Combinatorial families require population review

Do not automatically expand:
- color + target;
- size + target;
- generic modifier + target;
- weak object/place dual interpretations.

Semantic truth alone is insufficient.

### Search-oriented is a positive decision

Named memes, events, franchise-specific concepts, and idiosyncratic references can be well understood yet better served by search.

SEARCH_ORIENTED is not failure.

---

## 11. Continuous execution

The review is one continuous 31,003-identity job.

Do not use 200-row shards as semantic/reasoning boundaries.

Periodic persistence is allowed only to protect work.

Recommended:
- update the ledger continuously;
- checkpoint/commit periodically;
- resume from the first row without `manual_seen=YES`.

The exact checkpoint interval is operational, not semantic.

No user "continue" input should be required between checkpoints.

---

## 12. Final completeness gates

Before Pass A closes:

- expected identities = 31,003
- unique reviewed identities = 31,003
- manual_seen=YES = 31,003
- duplicate identity = 0
- missing identity = 0
- invalid route ID = 0
- blank discovery_mode = 0

Before production review closes:

- every MISSING_CORE_ROUTE is reconciled;
- every CURRENT_ROUTE_NOT_REPRODUCED is reviewed;
- every final ADD_SECONDARY is supported by a stable existing route ID;
- #64/#76 ownership violations = 0;
- runtime semantic engines added = 0.

---

## 13. Runtime / architecture gate

The exhaustive review ledger does not ship.

Production receives only the minimal confirmed static delta.

Reuse:
- CatalogEntry.UnifiedBrowseRouteIds
- UnifiedBrowseIndex
- current content/body/theme filters
- current search index

Do not add:
- second browse index;
- semantic inference at startup;
- per-query semantic computation;
- embeddings;
- LLM runtime dependency;
- co-occurrence recommendation engine;
- live external lookup.

---

## 14. Performance gate

Compare candidate runtime with the accepted pre-#132 baseline.

Measure:
- catalog/index construction;
- retained memory;
- Japanese search;
- English search;
- mixed search;
- browse/filter operations;
- long-list scroll/responsiveness;
- post-operation idle behavior.

The expected #132 runtime delta is small static route membership.

A material performance regression is evidence that the shipped representation is too large or too complex.

Simplify the metadata before adding caches/services.

---

## 15. Relationship to previous #132 phases

Retain Phase 1–6 as historical evidence.

But:
- bounded tasks are regression evidence only;
- machine OK/NO_AUTHORITY/REVIEW are audit context only;
- prior candidate routes do not appear in Pass A;
- older 200-row-shard handoff is superseded.

The final Codex/Luna instruction must not be written until the neutral-input path and Pass-A contract are ready.
