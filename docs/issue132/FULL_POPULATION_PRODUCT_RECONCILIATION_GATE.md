# Issue #132 — Full-population product reconciliation gate

Date: 2026-09-23 JST
Status: **RESEARCH DESIGN / AFTER LUNA PASS A**

## 1. Purpose

Pass A answers:

> Which route is a natural way to think about/find this visual concept?

This document answers a different question:

> Would exposing that route in the actual app make tag discovery better?

A semantically natural route is not automatically a good production route.

---

## 2. Inputs

Join by identity_key:

### Independent Luna result
- discovery_mode
- CORE/SUPPORTING natural routes
- semantic summary
- uncertainty/research depth

### Current product context
- current Unified route IDs
- local subroute IDs
- body-site facets
- theme facets
- #118 content intent
- Japanese search surfaces
- aliases
- post/usage count
- current browseability
- machine/audit families

All 31,003 identities remain present in the joined ledger.

---

## 3. Deterministic diff

For each identity:

```
missing_core = luna_core_routes - current_routes
missing_supporting = luna_supporting_routes - current_routes
current_not_reproduced = current_routes - luna_all_natural_routes
missing_body_facets = luna_body_site_ids - current_body_site_ids
missing_theme_facets = luna_theme_ids - current_theme_ids
```

Derive:

- COVERED
- MISSING_CORE_ROUTE
- MISSING_SUPPORTING_ROUTE
- CURRENT_ROUTE_NOT_REPRODUCED
- MISSING_BODY_FACET
- MISSING_THEME_FACET
- SEARCH_ORIENTED
- SEMANTIC_UNRESOLVED

If an identity has both missing and extra-current routes, preserve both flags.

No semantic decision is made by this diff.

---

## 4. #132 ownership gate

### Already browseable + missing natural route
Eligible for #132 secondary-route consideration.

### Not currently browseable
Not eligible for direct #132 promotion.

Send to:
- upstream #64/#76 review, or
- SEARCH_ONLY.

### Current route not independently reproduced
Do not remove it in #132.

Send to owner-authority review.

This keeps #132 from becoming a second primary taxonomy.

---

## 5. Incremental discovery gate

For each missing natural route, ask:

### A. Unknown-tag usefulness

Would the route help a user who knows the visual goal but not the exact Danbooru term?

### B. Existing search coverage

Assess accepted:
- display_ja;
- search_ja;
- aliases;
- canonical.

Strong search coverage lowers incremental browse value, but does not automatically reject a CORE route.

### C. Existing alternate discovery

Is the same intent already served by:
- another current route;
- local subroute;
- body facet;
- theme facet?

If yes, the new route may be redundant.

### D. User-controlled visual axis

Does the route correspond to something the user intentionally controls in generation?

This favors:
- pose;
- action;
- body target;
- clothing/exposure;
- object;
- scene;
- camera;
- expression;
- lighting;
- style.

Incidental lexical attributes receive less product value.

---

## 6. Shelf-coherence gate

Evaluate **all candidate additions together**, not one row at a time.

For every route, calculate before/after:

- total identities;
- GeneralPurpose-lens count;
- Sexual-lens count;
- candidate additions;
- candidate additions by current route;
- candidate additions by semantic/lexical family;
- multi-route identity count;
- CORE vs SUPPORTING additions.

No fixed percentage is an automatic accept/reject threshold.

Large changes are audit alarms.

---

## 7. Narrowability gate

Current UI exposes:
- local subroutes derived from #64;
- Special body facets;
- Special theme facets;
- #118 content lens;
- text search inside current browse constraints.

A #132 secondary route does not automatically create new local/body/theme metadata.

Therefore calculate per route:

- identities with a local subroute;
- identities with a body facet;
- identities with a theme facet;
- identities with no refinement metadata beyond top-level route/content/search;
- candidate additions that are top-level-only.

This is especially important for broad routes such as:
- BODY_SITE;
- CLOTHING_EXPOSURE;
- ACTION_CONTACT;
- TOOL_OBJECT.

Example risk:

Adding a large General-only action/body family to BODY_SITE may be semantically natural but can enlarge the BODY_SITE shelf without giving those identities BREAST_NIPPLE / BUTTOCK_ANAL / MOUTH_ORAL etc. facet membership.

That can make the route less usable despite semantic correctness.

---

## 7.5. Body/theme facet expansion is a separate architecture gate

Pass A intentionally records body/theme intent for all identities so the adult-generation workflow is not blind to General-only gaps.

However, current runtime body/theme facet metadata is Special-backed.

Therefore:

- missing General body/theme facets are **research findings**;
- do not encode them as fake Special metadata;
- do not silently add another per-query facet engine;
- do not treat them as ordinary #132 route additions.

After the full 31,003 diff, measure:

- number of General-only identities with missing body facets;
- number by each of the six body sites;
- number by each of the three themes;
- overlap with current ACTION_CONTACT / BODY_SITE / CLOTHING_EXPOSURE / POSE_POSITION routes;
- Sexual-lens impact;
- current Japanese-search coverage;
- expected result-size reduction if facets were available.

Only if the full-population benefit is substantial should a separate **Unified facet overlay** architecture be considered.

That decision must include catalog-size, startup-memory, index-build and filter-latency measurements.

---

## 8. Family-concentration gate

Detect repeated patterns across the full candidate population.

Examples:
- color + target;
- action + body;
- object + fixture;
- clothing + placement;
- pose + action.

For each family report:

- total affected identities;
- missing route;
- CORE/SUPPORTING split;
- current search coverage;
- current facet/local coverage;
- post-count distribution;
- contribution to route growth.

Do not bulk-accept or bulk-reject from the family label alone.

The family view exists to detect:
- accidental explosion;
- inconsistent sibling decisions;
- a useful reusable rule.

---

## 9. Adult/sexual image-generation lens

The user's image-generation workflow materially uses adult/sexual tags.

Therefore the reconciliation must report route usability under the #118 Sexual lens separately.

At minimum calculate candidate impact for:

- ACTION_CONTACT
- POSE_POSITION
- BODY_SITE
- CLOTHING_EXPOSURE
- FLUID_EXCRETION
- RELATION_ROLE
- TOOL_OBJECT
- NONHUMAN_TRANSFORM

and Special body/theme facets.

This does not mean sexual tags receive lower evidence standards.

It means the actual target workflow is measured explicitly rather than being diluted by the much larger non-sexual population.

---

## 10. Search-vs-browse balance

External tag tools show a useful pattern:
- direct Japanese/alias/autocomplete search;
- optional category/tree exploration;
- post-count/result ordering.

#132 should preserve this balance.

A production addition is strongest when:
- the tag wording is not obvious;
- the route is a natural visual intent;
- existing browse misses that intent;
- route addition does not create an undifferentiated shelf.

A production addition is weakest when:
- the candidate is only a modifier relation;
- Japanese/alias search already makes the exact tag trivial;
- the route becomes dominated by a combinatorial family;
- no useful narrowing remains after route selection.

---

## 10.5. Prefer systemic fixes over thousands of row overrides

A large disagreement cluster can indicate a problem in the discovery layer itself rather than thousands of bad identities.

After the full independent diff, inspect whether repeated mismatches come from:

- a Unified route label that does not describe its actual accepted population;
- one General->Unified mapping that collapses meanings too aggressively;
- one Special->Unified mapping that hides an important distinction;
- a missing refinement axis;
- or genuinely identity-specific multi-entry gaps.

Example already visible in the current design:

- #64 `POSE_MOVEMENT` means "ポーズ・動き";
- Unified maps it to `POSE_POSITION`;
- the current Unified label is "ポーズ・体位".

If the full Pass-A map repeatedly treats locomotion/movement as mismatched because the user-facing shelf sounds position-only, the first solution to inspect is **route wording/mapping**, not thousands of per-tag overrides.

Resolution preference:

1. clear user-facing label correction, if semantics already match;
2. small deterministic Unified mapping correction, if one mapping is the root cause and authority remains intact;
3. owner-authority review (#64/#76), if accepted taxonomy itself is wrong;
4. identity-level #132 secondary overlay only for genuinely multi-entry exceptions.

This order directly supports:
- simpler code;
- smaller runtime metadata;
- easier Japanese UI;
- lower maintenance cost.

Do not use one global fix merely because it is smaller; it must be semantically correct across the affected full population.

---

## 11. Final reconciliation states

After full-population product analysis:

### ADD_SECONDARY_READY
- already browseable;
- missing route is CORE or exceptionally strong SUPPORTING;
- incremental discovery value is real;
- population-scale shelf remains useful;
- no owner-authority conflict.

### HOLD_BORDERLINE
- semantically natural;
- product value or shelf cost remains uncertain.

### KEEP_CURRENT
- current discovery is sufficient.

### UPSTREAM_REVIEW
- primary classification/browseability/current route authority may be wrong.

### SEARCH_ONLY
- understood identity, but browse placement is not worthwhile.

### UNRESOLVED
- semantics or route intent cannot be established safely.

Only ADD_SECONDARY_READY is eligible for #132 runtime overlay.

---

## 12. No quota

There is no required count for ADD_SECONDARY_READY.

However the full-population distribution is inspected for instruction/pathology signals.

Examples:
- near-zero missing routes despite obvious multi-axis concept populations;
- thousands of color additions;
- route growth dominated by one trivial modifier family;
- major sibling inconsistency.

These trigger review of the process, not quota-based relabeling.

---

## 13. Performance compatibility

Before production promotion, simulate the complete ADD_SECONDARY_READY overlay and rebuild the normal runtime representation.

Measure:
- UnifiedBrowseIndex construction;
- allocations/retained memory;
- Browse() latency;
- FilterSearchHits() latency;
- UI category/facet interaction;
- long-list scrolling;
- idle after operations.

Use the existing runtime index/performance test infrastructure as baseline.

No new cache/service is allowed as the first response to a regression.
