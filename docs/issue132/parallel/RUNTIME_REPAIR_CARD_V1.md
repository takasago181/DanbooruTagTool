# Issue132 Staging Repair Card V1

Purpose: remove historical invalid staging debt without burdening forward workers.

## Authority
Read WORKER_EXECUTION_CARD_V1.md plus latest Issue132 staging-validator diagnostics. Work only on research/taxonomy-usability-audit. Never edit immutable checkpoints, main, production, UserData, #64/#76/#118.

## Priority
1. Structural INVALID_STAGING from latest CI: identity shift, gap, duplicate, wrong review_seq/key, malformed JSON, wrong window coverage, parent-route/local structural errors.
2. Definite semantic lint in staging.
3. Lane 3 historical route-family debt (751-1050) after structural debt is clean.

Process at most 3 oldest invalid windows per run, preferring the earliest promotion-blocking windows across lanes.

## Rebuild method
For each selected invalid 25-window:
- load exact authoritative shard tuples for that lane/range;
- treat the old invalid staging as non-authoritative hints only;
- rebuild the window from the source tuples under the semantic card;
- bounded research for genuine ambiguity; unresolved identity becomes a hold at its exact original slot;
- pre-write exact tuple gate;
- update/create staging;
- re-fetch and repeat exact tuple gate;
- if validation fails, repair/delete the same window before moving on.

Never fix identity-shift by renumbering or sliding existing rows. Never mutate immutable checkpoints.

## Lane-specific semantic debt
When structural debt is exhausted, continue Lane 3 751-1050 focused audit:
- remove route2 COLOR caused only by simple color/pattern adjective;
- remove POSE caused only by object/clothing placement;
- remove LIVING caused only by motif/print/ornament;
- challenge weak SCENE/TOOL secondaries;
- retain secondaries that pass independent-browse usefulness.

## Status
Maintain docs/issue132/parallel/repair_status.json with:
- latest CI run examined;
- windows repaired this run;
- remaining known invalid windows;
- structural debt count trend;
- route-family debt state;
- any genuine blocker.
