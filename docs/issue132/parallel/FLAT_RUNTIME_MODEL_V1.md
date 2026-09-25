# Issue132 Flat Runtime Model V1

Status: ACTIVE FLAT DATA/VALIDATION MODEL. The original five-automation scheduler is paused; current execution driver and role cards are selected by live `RUNTIME_AUTHORITY.json`.

## Goal

Review all 31,003 neutral identities for real image-generation discoverability while keeping the execution path simple, auditable, and resilient.

The semantic method remains:
neutral identity -> independent discovery decision -> full-population comparison -> product reconciliation -> minimal static production delta.

The execution method is rebuilt from scratch.

## Five-task topology

Exactly five automations:
1. Worker 1 — lane 1 forward review
2. Worker 2 — lane 2 forward review
3. Worker 3 — lane 3 forward review
4. Repair — only invalid/pending historical output
5. QA-Coordinator — validation, selective semantic QA, completion

No sixth helper, promoter, watchdog, or migration task.

## Canonical progress model

There is no checkpoint-prefix progress gate.

A record range is accepted when:
- it binds exactly to the frozen neutral identity slots;
- its compact schema and semantic codes validate;
- it contains no unresolved operational hold.

Accepted ranges after a bad range remain accepted.

Example:
- 1-700 valid
- 701-800 invalid
- 801-1200 valid

Progress is 1,100 accepted rows, with 100 rows of repair debt.
It is not capped at 700.

Historical immutable checkpoints remain accepted seed data.
Historical staging remains immutable evidence and is validated in place.
Historical repair overlays remain append-only.
No checkpoint promotion is required or performed.

## Forward persistence

Workers reason in logical blocks of up to 100 identities, but persist in 25-row slices to limit the blast radius of any upstream write-policy rejection.

Workers write only code-only request files under each lane write-requests directory. Requests intentionally omit identity text and identity hashes. GitHub Actions joins the request with the pinned neutral input and materializes the canonical staging v2 file.

Existing 25-row staging files remain valid history. A request is pending work until canonical staging exists and validates.

Worker run ceiling: 300 identities.

## Semantic record

The compact decision is the authority:
- lane_local_index
- review_seq
- identity_sha256
- discovery_mode
- routes with CORE/SUPPORTING
- local_refinement_ids
- body_site_ids
- theme_ids
- route_vocabulary_gap
- review_depth
- evidence_urls

Do not claim a per-row free-form semantic explanation was manually authored when it was mechanically reconstructed later.

CHECKED means the identity was semantically inspected and the compact decision was made directly.
RESEARCHED means bounded external research was required.

Completed bounded research that remains uncertain is terminal SEMANTIC_UNRESOLVED.
A hold is only for an actual interruption that prevented required research or persistence from being completed.

## Repair

Repair never promotes checkpoints and never rereviews valid ranges.

Repair owns only:
- structurally invalid historical windows;
- semantically invalid historical windows;
- windows containing genuine operational holds;
- append-only replacement overlays for those exact windows.

One invalid window never blocks another lane or later valid output.

## QA

Mechanical validation covers 100% of accepted output.

Semantic second-pass QA is risk-based, prioritizing:
- RESEARCHED
- MIXED
- SEMANTIC_UNRESOLVED
- route_vocabulary_gap=YES
- multiple routes
- SUPPORTING routes
- body/theme facets
- sibling/family inconsistency signals

Ordinary obvious CHECKED rows receive a deterministic small sample, not a full duplicate review.

## Completion

Pass A completes only when:
- accepted unique identities = 31,003;
- missing identities = 0;
- invalid windows = 0;
- operational hold windows = 0;
- duplicate identity coverage = 0;
- frozen vocabulary/identity contract drift = 0;
- required risk-based QA has no unresolved systematic defect.

Then build Pass B deterministically.

## Protected boundaries

No merge.
No production apply.
No mutation of main, UserData, #64, #76, #118, Character/Copyright/Artist authority, or search ranking.
