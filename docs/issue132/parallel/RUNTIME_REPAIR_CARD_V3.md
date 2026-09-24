# Issue132 Unified Repair Card V3

Purpose: clear historical non-authoritative staging debt across all three lanes without burdening forward workers or coordinator.

Scope:
- branch research/taxonomy-usability-audit only
- never edit immutable checkpoints, main, production, UserData, #64/#76/#118
- forward workers own NEW frontier; Repair owns historical invalid staging and historical Lane3 751-1050 route-family debt

Hot-path reads:
1. this card;
2. RUNTIME_WORKER_CARD_V4.md for semantic/exact-gate rules;
3. coordinator_status.json;
4. repair_status.json if present;
5. latest Issue132 staging-validator logs only when CI run_id/head/failure class changed.

If latest CI identity is unchanged from repair_status.json, continue the stored queue without refetching/reparsing the same logs.

## Unified repair queue

Maintain three queues:
- L1 structural/semantic staging debt
- L2 structural/semantic staging debt
- L3 structural staging debt
and one secondary queue:
- L3 historical 751-1050 route-family remediation

Per run, use a balanced work-conserving schedule:
1. repair up to 2 oldest invalid windows from Lane 1;
2. repair up to 2 oldest invalid windows from Lane 2;
3. repair up to 2 oldest invalid windows from Lane 3;
4. any unused structural slots may be borrowed by another lane with remaining older promotion-blocking debt;
5. if Lane3 has no structural window left for its share, spend that capacity on the targeted 751-1050 route-family audit.

Hard ceiling: normally 6 historical windows per run. Do not lower semantic/research quality to reach six. A difficult window may consume more time; persist each repaired window immediately.

This quota is for fairness, not a stop rule: if fewer than six valid repair targets exist, finish what exists. Do not invent work.

## Structural repair

For validator errors involving identity shift, wrong review_seq/key, gap, duplicate, extra identity, malformed coverage, or row/hold overlap:
- load exact authoritative 25 source tuples from validated lane shard;
- old invalid staging is hints only, never authority;
- rebuild the full 25-window from those tuples;
- never renumber, slide, compress, or copy neighboring identities;
- genuine ambiguity may become an exact-slot hold after bounded research;
- pre-write exact tuple + 22-field + parent/local gate;
- write;
- re-fetch;
- repeat exact tuple + 22-field + parent/local gate;
- if post-write validation fails, repair/delete the same window before moving on.

For a window whose tuple structure is already exact and validator reports only definite semantic/structural lint:
- patch only the affected fields when the correct value is certain;
- research only if materially uncertain;
- do not rebuild unaffected rows.

## Lane 3 historical route-family audit

Only after that run's Lane3 structural share is clean or absent, use remaining Lane3 capacity on finalized rows 751-1050 carrying route2/route3 or related locals.

Challenge only:
- COLOR_PATTERN_SHAPE added merely from color/material/pattern adjective;
- POSE_POSITION added merely from object/clothing placement;
- LIVING/LIVING_NATURE added where animal/plant is only motif/print/ornament/emblem/likeness;
- weak SCENE_BACKGROUND or TOOL_OBJECT secondary.

Keep a secondary only if it is independently useful as a realistic unknown-tag browse axis and semantically entailed.
Do not full-reread all 300. Do not treat known seeds as automatic rewrites.

## Promotion and holds

If a repaired staging window becomes complete and lies exactly at checkpoint prefix+1, mechanical promotion is allowed under existing immutable rules.
Inspect genuine promotion-blocking holds only when they directly prevent such promotion; bounded research, max 3 holds per run after structural repair work. Do not let hold research displace the historical invalid-window queue.

## Status

Maintain docs/issue132/parallel/repair_status.json with:
- latest CI run/head/failure class examined;
- remaining invalid windows by lane;
- windows repaired this run;
- structural debt trend per lane;
- Lane3 route-family audit state;
- holds attempted/resolved;
- concrete blocker if any.

Keep status compact; no repeated narrative history.
