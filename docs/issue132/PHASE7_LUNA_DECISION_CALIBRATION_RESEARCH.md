# Issue #132 — Phase 7 Luna full-population method

Date: 2026-09-23 JST
Status: **PRE-HANDOFF RESEARCH FREEZE / DO NOT START FINAL CODEX RUN YET**

## 1. User goal

#132 exists to make the app more useful for **image generation**.

The target flow is:

> 作りたい見た目・行為・部位・体位・衣装・構図などがある  
> → Danbooruタグ名を知らなくても自然な入口から探せる  
> → 正しいcanonical tagを選べる  
> → Promptへ追加できる

The objective is not:
- taxonomy completeness;
- a beautiful ontology;
- maximizing classified rows;
- maximizing route count.

The UI/runtime must remain understandable and lightweight.

Adult/sexual image-generation use is an explicit target workflow and must be measured, not treated as an edge case.

---

## 2. Why the older method was insufficient

Earlier #132 research used:
- bounded candidate samples;
- machine OK/REVIEW/NO_AUTHORITY buckets;
- explicit KEEP/ADD-style first-pass judgments.

Those remain useful historical evidence, but they can bias a reviewer toward:
- confirming the current taxonomy;
- overfitting to known examples;
- becoming too conservative;
- or adding every technically related route.

The final semantic census therefore separates:

1. independent semantic discovery;
2. current-product comparison;
3. product-value reconciliation;
4. production approval.

---

## 3. No sample calibration

There is no 32/64/100-row calibration pack.

The **31,003-identity population itself** is the calibration/evaluation surface.

Do not approve the instruction because it looks good on a curated subset.

After the full pass, diagnose instruction bias from:
- route-selection distribution;
- CORE/SUPPORTING distribution;
- body/theme distribution;
- family inconsistency;
- modifier-family concentration;
- unresolved rate;
- repeated route combinations.

If the instruction is materially biased, revise it and rerun the affected stage over the full population.

No fixed percentage quota is used.

---

## 4. Pass A — independent semantic discovery map

Luna reviews **all 31,003 identities**.

Pass A is intentionally blind to the current product classification.

The question is:

> If I wanted to generate this visual concept but did not know the Danbooru tag, which existing discovery shelf would I naturally open?

Luna does **not** answer:
- KEEP;
- ADD_SECONDARY;
- CHANGE_ROUTE;
- whether the current taxonomy is correct.

Those are later questions.

### Pass-A input

Generated from tracked #118 authority only:

`scripts/issue132/build_luna_neutral_input.py`

Fields:
- review_seq;
- identity_key;
- source_surfaces.

The input intentionally excludes:
- current #64 path;
- current #76 kind/body/theme;
- current Unified routes;
- #118 sexual-intent verdict;
- General/Special membership;
- Japanese production overlay;
- aliases;
- usage/post count;
- machine audit labels;
- prior proposals.

This makes the pass GitHub-reproducible and avoids uploading local protected data.

### Ordering

Deterministic:

`SHA256("issue132-pass-a-v2|" + identity_key)`

Do not group by current taxonomy or prior issue family.

---

## 5. Pass-A semantic output

Per identity:

- manual_seen = YES
- semantic_summary_ja
- discovery_mode:
  - BROWSE_WORTHY
  - MIXED
  - SEARCH_ORIENTED
  - SEMANTIC_UNRESOLVED
- up to three existing Unified route IDs
- each route strength:
  - CORE
  - SUPPORTING
- short route reason
- local_refinement_ids from the existing fixed General local refinement vocabulary
- body_site_ids from the existing six fixed body facets
- theme_ids from the existing three fixed theme facets
- review_depth:
  - CHECKED
  - RESEARCHED
- evidence URLs when researched
- uncertainty note
- route_vocabulary_gap = YES/NO
- route_vocabulary_gap_note

### Why route_vocabulary_gap exists

Luna is not allowed to invent a route ID during row review.

But if the existing 19-route vocabulary clearly cannot express a useful user mental model, that must be recorded rather than forced into:
- an inaccurate existing route;
- SEARCH_ORIENTED;
- or SEMANTIC_UNRESOLVED.

Repeated vocabulary-gap notes are analyzed only after the full pass.

---

## 6. CHECKED vs RESEARCHED

### CHECKED

Use when:
- the identity meaning is clear from the tag/source surface;
- route intent is obvious;
- no subtle domain/reference knowledge is required.

### RESEARCHED

Use when:
- meaning is unclear;
- a meme/event/proper reference must be understood;
- a subtle distinction changes the route;
- the route vocabulary may be insufficient;
- confidence would otherwise be weak.

Preferred evidence:
1. Danbooru wiki/tag documentation;
2. authoritative source/reference material;
3. other reliable semantic evidence.

Do not infer a confident meaning only from token shape.

Web lookup is not mandatory for every obvious row.

---

## 7. Route semantics

The authoritative Pass-A route definitions are:

`docs/issue132/LUNA_DISCOVERY_ROUTE_SEMANTIC_CONTRACT.md`

Key principle:

A route is a **discovery intent**, not exclusive ontology membership.

Multi-entry is valid when the user could naturally approach the same visual from different axes.

Examples of potentially legitimate multi-axis concepts:
- action + body target;
- action + pose/sexual position;
- clothing + exposure/state;
- action + object;
- body state + hair/face appearance.

Technical relatedness alone is insufficient.

---

## 7.5. Existing local-refinement capture

Pass A also records the existing General local-refinement vocabulary independently from current assignment.

Purpose:

- detect cases where the user can reach the correct top-level route but the next narrowing step is wrong or missing;
- audit current #64 consistency without exposing current #64 placement to Luna.

Examples:
- ACTION_CONTACT/INTIMATE
- CLOTHING/UNIFORM
- OBJECT_PROP/WEAPON
- EXPRESSION_EMOTION/

This does **not** authorize a #132 local-refinement runtime overlay.

A missing/misleading local refinement is routed to upstream #64 review.

---

## 8. Adult/sexual refinement capture

Pass A also records the existing body/theme facet vocabulary independently.

Body:
- MALE_GENITAL
- BREAST_NIPPLE
- FEMALE_GENITAL
- MOUTH_ORAL
- BUTTOCK_ANAL
- URETHRA

Theme:
- BDSM_RESTRAINT
- INJURY_R18G
- REPRO_PREGNANCY_LACTATION

This ensures the full review can detect whether important General-only adult concepts are currently missing useful refinement.

It does **not** authorize General facet expansion.

Facet expansion, if justified, receives a separate architecture/performance gate.

---

## 9. Pass B — deterministic diff

After Pass A is frozen, compare it to current #64/#76/Unified metadata.

Derive mechanically:

- COVERED
- MISSING_CORE_ROUTE
- MISSING_SUPPORTING_ROUTE
- CURRENT_ROUTE_NOT_REPRODUCED
- MISSING_LOCAL_REFINEMENT
- MISSING_BODY_FACET
- MISSING_THEME_FACET
- SEARCH_ORIENTED
- SEMANTIC_UNRESOLVED
- ROUTE_VOCABULARY_GAP

No product edit is made by this diff.

---

## 10. Pass C — full-population product reconciliation

Only now join actual product context:

- current #64 paths;
- current #76 kind/body/theme;
- current Unified routes/local routes;
- #118 content intent;
- accepted Japanese display/search terms;
- approved aliases;
- usage/post count;
- current result counts;
- machine pattern families.

The accepted local production catalog is the right source for Japanese/search/product context.

Do not commit ignored protected input data merely to perform Pass A.

Evaluate each missing route on:

1. semantic centrality;
2. independent unknown-tag lookup value;
3. incremental value beyond search/current facets;
4. shelf coherence after all candidate additions;
5. whether the resulting shelf remains narrowable;
6. performance/runtime cost.

The full reconciliation contract is:

`docs/issue132/FULL_POPULATION_PRODUCT_RECONCILIATION_GATE.md`

---

## 11. Systemic fixes before row overrides

Large disagreement clusters may indicate a route-label/mapping problem rather than thousands of identity problems.

Examples already worth auditing after Pass A:
- #64 POSE_MOVEMENT = "ポーズ・動き" while Unified label is "ポーズ・体位";
- General role concepts vs Special RELATION_ROLE;
- General BODY_PART states/fluids vs Special FLUID_EXCRETION;
- Special broad POSE_SCENE projection.

Resolution preference:

1. correct user-facing wording if that is the real problem;
2. correct one deterministic projection if the projection is the root cause;
3. send true taxonomy errors to #64/#76 owner authority;
4. use identity-level #132 secondary route only for genuine multi-entry exceptions.

Reference:

`docs/issue132/UNIFIED_ROUTE_SYSTEMIC_RISK_AUDIT.md`

---

## 12. #132 production ownership

#132 must not become a second taxonomy authority.

Default v1 production scope:

> confirmed secondary Unified route additions for identities already browseable through accepted authority.

If an identity has no browse authority:
- upstream #64/#76 review;
- or SEARCH_ONLY.

If a current primary route appears wrong:
- upstream owner review.

If Japanese/search metadata is wrong:
- send to that owner lane.

Body/theme General expansion is not silently included in the route overlay.

Reference:

`docs/issue132/PRODUCTION_DELTA_ARCHITECTURE_GUARDRAILS.md`

---

## 13. Runtime/performance principle

Research can be exhaustive.

Runtime must remain boring.

The 31,003-row Luna ledger, evidence, reasoning, confidence, and diagnostics do not ship.

Expected production representation remains:
- small static accepted delta;
- existing CatalogEntry/UnifiedBrowseIndex path where possible;
- no LLM;
- no embeddings;
- no live web;
- no runtime semantic parsing;
- no second browse/search engine.

Performance comparison uses existing:
- Issue #114 runtime-index benchmarks;
- Issue #117 UnifiedBrowse performance tests;
- post-#131 UI smoke/performance evidence.

A material regression blocks promotion.

Reduce metadata/complexity before adding caches or services.

---

## 14. Protected-data / Codex-cloud constraint

GitHub does not contain the local protected production catalog/source overlays.

Therefore Pass A is intentionally generated entirely from tracked #118 identity authority.

Pass C may require an authorized environment with the actual production catalog.

Do not copy ignored local protected datasets into GitHub merely to unblock Luna semantic review.

This separation also improves methodological independence.

---

## 15. Live-main compatibility

The #132 research branch is intentionally isolated and has diverged from live main.

Current research must therefore distinguish:
- research evidence/contracts on the #132 branch;
- production implementation against the then-current live main.

Do not merge old branch UI/runtime code wholesale.

Before any production implementation:
1. fetch live main;
2. re-read CURRENT_STATE / PERMANENT_RULES / Issue #132;
3. revalidate current UnifiedBrowse/Catalog boundaries;
4. implement only the accepted minimal delta from latest main.

---

## 16. Current technical gate

Before the final Luna/Codex instruction is written:

1. GitHub CI must successfully generate:
   - full population audit;
   - `luna_neutral_review_input_v2.csv`;
   - neutral manifest;
2. validate:
   - 31,003 identities;
   - exact accepted #118 SHA;
   - three allowed input columns only;
   - deterministic order/output SHA;
3. freeze the Pass-A output schema;
4. define restart/persistence mechanics without semantic shards;
5. only then rewrite the final Codex Luna handoff.

The old `CODEX_FULL_SEMANTIC_REVIEW_HANDOFF.md` remains **DRAFT / DO NOT RUN**.
