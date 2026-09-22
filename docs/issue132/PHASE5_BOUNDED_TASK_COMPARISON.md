# Issue #132 — Phase 5 bounded task comparison

Date: 2026-09-22
Status: **RESEARCH / DATA-LEVEL PROTOTYPE DECISION**

## Goal

Test the simplified #132 v2 idea without asking the user to perform a manual 20–30 task click-through.

This is a bounded **route-coverage benchmark**, not a stopwatch/UI ergonomics study.

Inputs:
- current `UnifiedBrowseTaxonomy` / `UnifiedBrowseIndex` behavior on live main;
- Phase 1 136-row candidate evidence;
- the v2 rule: add only audited secondary discovery routes; do not infer recommendations.

## Important implementation finding

The current app already supports multiple discovery routes per tag.

`CatalogEntry.UnifiedBrowseRouteIds` is unioned into each browse identity by `UnifiedBrowseIndex`.

Therefore the first #132 prototype does **not** need:
- a new scene-builder UI;
- adaptive suggestions;
- a new taxonomy tree;
- an LLM;
- co-occurrence;
- a Prompt workflow rewrite.

The lowest-risk prototype is a **small static route overlay** feeding the existing browse UI.

The existing Special override mechanism is also precedent for audited `ADD_SECONDARY` route enrichment.

## Task set

24 tasks are recorded in `phase5_task_matrix_v1.csv`.

Composition:
- 12 high-confidence targeted route gaps;
- 8 high-confidence controls where the existing natural route must keep working;
- 1 high-confidence case where Unified already collapses the top-level distinction and therefore needs no top-level change;
- 2 medium-confidence candidates deliberately deferred;
- 1 low-confidence unresolved safety control deliberately left unresolved.

The high-confidence cohort deliberately targets known friction and is **not** a population-wide success estimate.

## Result

### High-confidence route cohort: T01–T20

Current:
- HIT: 8
- MISS from the tested natural alternate entrance: 12

With only the audited secondary routes proposed by Phase 1:
- HIT: 20
- MISS: 0

Interpretation:
- all 12 targeted route-coverage gaps become reachable from the tested alternate entrance;
- all 8 existing-route controls stay reachable;
- no adaptive inference is required.

This demonstrates the value of **multi-entry discovery** for the bounded known-gap cohort.

It does **not** prove that every suggested secondary route across the full catalog is correct.

### Negative / safety controls

T21 `off_shoulder`:
- no top-level #132 route addition is justified;
- current General CLOTHING already maps to Unified `CLOTHING_EXPOSURE`;
- the Phase 1 concern is about local classification nuance, not a missing top-level entrance.
- This is evidence that #132 must evaluate the actual Unified projection instead of mechanically copying every Phase 1 suggestion.

T22 `blue_bikini`:
- color secondary route is MEDIUM confidence;
- do not auto-add in the first prototype.

T23 `automatic_door`:
- object/place secondary route is MEDIUM confidence;
- do not auto-add in the first prototype.

T24 proper-name/meme:
- remains UNRESOLVED;
- no attempt to invent a route.

## What this changes in the #132 plan

The previous plan proposed building a visible prototype first.

That is now unnecessarily large.

### New first prototype

1. No UI redesign.
2. Freeze a tiny high-confidence route-overlay sample.
3. Feed it into the existing `UnifiedBrowseRouteIds` mechanism.
4. Add tests proving:
   - target alternate route contains the identity;
   - existing route still contains the identity;
   - content-intent filter still applies;
   - duplicate General/Special identity remains deduplicated;
   - search behavior is unchanged.
5. Compare result counts / route membership mechanically.
6. Only if the existing UI cannot expose the useful route cleanly should #132 add UI.

## Recommended prototype seed

Start from only the strongest repeated rules:

### Rule A — explicit action + explicit body target

For Human-reviewed/HIGH-confidence identities where the canonical concept explicitly encodes an action and body target:

- preserve ACTION_CONTACT;
- add BODY_SITE as discovery-only secondary route.

Do not derive this at runtime from string tokens. The actual accepted rows must be audited/static.

### Rule B — confirmed pose-scene projection gaps

For the five Phase 1 HIGH rows:
- `presenting_own_ass`
- `standing_doggystyle`
- `holding_own_legs_back`
- `holding_own_leg_back`
- `holding_another's_legs_back`

preserve ACTION_CONTACT and add POSE_POSITION in the prototype overlay.

### Rule C — confirmed hair discovery gap

For `sex_hair`:
- preserve BODY_SITE;
- add HAIR_FACE.

## Explicit non-goals

Do not prototype:
- adaptive "next" suggestions;
- co-occurrence;
- semantic similarity;
- automatic Prompt insertion;
- full General reclassification;
- medium/low-confidence secondary routes;
- UI redesign.

## Decision

**Proceed with a data-only bounded prototype before any new UI work.**

This is simpler than the prior plan and directly matches the current architecture.

If the static overlay gives useful multi-entry discovery with no route/search regressions, #132 can remain primarily a data-quality improvement.

If it does not, stop rather than adding a smarter recommendation layer.

## Protected boundaries

Research only. No main merge, production catalog rebuild, UserData mutation, or production runtime apply.
