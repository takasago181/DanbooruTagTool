# Issue #132 — Production delta architecture guardrails

Date: 2026-09-23 JST
Status: **RESEARCH DESIGN / NO PRODUCTION IMPLEMENTATION**

## 1. Core rule

#132 may improve **discovery**, but it must not become a second taxonomy authority.

Production #132 is therefore limited to:

> adding confirmed secondary Unified discovery routes to identities that are already browseable through accepted #64/#76 authority.

This boundary keeps the app and data model simple.

---

## 2. What #132 may ship

A minimal identity-level route addition:

```
identity_key
route_id
source = ISSUE132
```

Build-time validation may carry evidence/review metadata, but runtime does not need it.

The route ID must already exist in `UnifiedBrowseTaxonomy.Routes`.

The target identity must already be browseable before the #132 addition.

---

## 3. What #132 must not ship

#132 must not independently:

- make an unresolved General tag browseable;
- make a non-browseable Special tag browseable;
- create a new primary taxonomy classification;
- replace #64 primary/secondary authority;
- replace #76 kind/body/theme authority;
- change #118 content intent;
- create new canonical/PromptToken identity;
- add runtime semantic inference.

If Pass A discovers a strong natural route for a currently non-browseable identity, final disposition is:

- `UPSTREAM_REVIEW` for #64/#76, or
- `SEARCH_ONLY` if browse is not worth upstream work.

This prevents #132 from silently becoming "#64 v2".

---

## 3.5. Body/theme findings do not automatically become #132 runtime metadata

The full Luna census may identify missing body-site/theme refinement for General-only identities.

Those findings are intentionally captured because adult/sexual image generation is a core workflow.

They are **not** automatically eligible for the v1 #132 route overlay.

If full-population reconciliation proves that General facet expansion has large user value, design it as one explicit Unified facet extension with its own:
- data owner;
- schema;
- bake boundary;
- performance measurements;
- migration tests.

Do not:
- encode General rows as Special to gain facets;
- add ad-hoc per-feature facet dictionaries in the ViewModel;
- infer body/theme facets at runtime.

---

## 3.75. New route/facet vocabulary is default-deny

Pass A may report:
- repeated `route_vocabulary_gap=YES`;
- missing body/theme refinement on General identities;
- missing local refinement.

These are **research findings**, not permission to expand the runtime taxonomy.

### New top-level Unified route

Default decision for #132 v1:

**do not add a new route ID.**

A new top-level route may be considered only after the complete 31,003-row reconciliation proves all of the following:

1. the gap is a coherent user-controlled image-generation axis, not a token/modifier family;
2. the same mental model recurs across a meaningful population;
3. renaming an existing route is insufficient;
4. correcting one General/Special->Unified mapping is insufficient;
5. existing local/body/theme refinement is insufficient;
6. Japanese/English/alias search does not already make browse expansion redundant;
7. the new route would reduce user wrong turns rather than merely increase taxonomy coverage;
8. the UI can remain shallow and understandable;
9. the runtime can remain static/index-backed with no new semantic engine;
10. performance validation passes.

Even then, a new route is **not automatically part of the #132 v1 overlay**. It requires an explicit design decision before implementation.

### New facet axis

Do not invent new body/theme/facet axes from Luna row notes.

Existing body/theme vocabularies are fixed during Pass A.

If a repeated missing axis is discovered:
- record it as research;
- reconcile it after the full population;
- require an explicit owner/schema/UI/performance design before implementation.

### General body/theme expansion

Existing six body sites and three themes may be found useful for General-only identities.

That remains a separate explicit architecture decision.

Do not silently convert the finding into:
- Special metadata;
- ViewModel dictionaries;
- runtime inference;
- another filter engine.

### Local refinement gaps

Local refinement remains #64-owned.

#132 does not create a parallel local-subroute overlay.

This default-deny boundary is intentional:

> exhaustive research is allowed to discover structural gaps; production complexity is not allowed to grow automatically from those discoveries.

---

## 4. Existing runtime mechanism

Current architecture already has the desired runtime representation:

`CatalogEntry.UnifiedBrowseRouteIds`

is merged into:

`UnifiedBrowseIdentity.RouteIds`

by:

`UnifiedBrowseIndex`.

Therefore final #132 should reuse this path.

No:
- second route index;
- second search engine;
- semantic service;
- runtime rule evaluator.

---

## 5. Build-time overlay shape

If production integration needs a new asset, prefer **one generic Unified discovery overlay** for #132 additions rather than many feature-specific files.

Conceptual schema:

```
identity_key,route_id,mode,source_authority
C:standing_doggystyle,POSE_POSITION,ADD_SECONDARY,ISSUE132
```

Requirements:

- exact normalized identity match;
- route ID must exist;
- mode is `ADD_SECONDARY` only;
- target must be browseable before overlay;
- duplicate identity+route rows forbidden;
- route already present = redundant/error during build review;
- deterministic sorted output.

Research notes/evidence remain outside the runtime asset.

---

## 6. Existing Special overrides

The current Special-only `UnifiedBrowseOverlay` and its six tracked overrides are existing authority.

Do not casually stack:
- special override file;
- #132 special override file;
- General override file;
- sexual override file;
- UI-only override file.

Before production implementation, choose one of:

### Minimal-risk
Keep existing Special behavior unchanged and add one separate generic #132 build-time overlay.

### Cleanup migration
Only if justified by tests, migrate accepted Special overrides and #132 additions into one validated generic Unified overlay.

Do not perform cleanup merely for aesthetic reasons if it raises migration risk.

Either design must result in **one runtime RouteIds set**, not multiple runtime engines.

---

## 7. Full-review mapping to owner authority

After independent Pass A and reconciliation:

### Missing route on already-browseable identity
Candidate for #132 ADD_SECONDARY.

### No current browse authority
#64/#76 upstream review or SEARCH_ONLY.

### Current route appears misleading
#64/#76 upstream review.
#132 does not mask the problem with an override.

### Japanese/search metadata is wrong
Japanese/search owner lane.
#132 does not compensate by adding routes.

### Canonical/Prompt identity is wrong
identity owner lane.
#132 does not compensate.

This preserves one owner per truth.

---

## 8. Performance rule

The final #132 runtime cost should be approximately the cost of a small number of extra string route memberships during catalog/index construction.

No new work should occur:
- per keystroke;
- per result card;
- per scroll;
- per Prompt mutation.

If profiling shows otherwise, implementation is violating the intended architecture.

---

## 9. Required final performance validation

Reuse accepted runtime evidence and tests, plus add a targeted Unified browse benchmark.

At minimum:

- existing `Issue114RuntimeIndexPerformanceTests`;
- production-sized `UnifiedBrowseIndex` construction timing/allocation;
- Browse() latency with common route/content/body/theme filters;
- FilterSearchHits() latency during Japanese/English/mixed search;
- post-#131 UI smoke:
  - long-result scroll;
  - category switching;
  - body/theme/content filters;
  - idle after operations.

Compare candidate to the exact pre-#132 production baseline.

A material regression blocks promotion.

Do not solve a #132 regression by adding another cache/service before first reducing the shipped overlay.

---

## 10. Outcome

Research can be exhaustive.

Runtime must remain boring.

That is the intended architecture.
