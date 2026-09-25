# Issue132 Runtime Repair Card V5 — append-only, minimal-control repair

Status: ACTIVE for Repair. Supersedes V4 operationally.

Goal: remove historical staging debt without rewriting old evidence and without consuming forward-worker capacity.

Branch: research/taxonomy-usability-audit
Root: docs/issue132/parallel/
Forward semantic rules: RUNTIME_WORKER_CARD_V6.md.

## Ownership

Repair owns only:
- historical invalid staging in Lane 1/2/3;
- historical Lane 3 751-1050 route-family debt;
- append-only repair overlays.

Never edit existing historical staging, checkpoints/corrections, forward NEW windows, main, production, UserData, #64/#76/#118.

## Effective repair model

Historical source staging is immutable evidence.
Repair result is a NEW file under:
docs/issue132/parallel/lane-N/staging/repairs/

Filename:
repair_XXXXXX_YYYYYY_vNNN.json

Schema:
issue132-pass-a-staging-repair-overlay-v1

Required:
schema_version, lane, lane_local_start, lane_local_end,
source_staging_path, source_staging_blob_sha,
repair_reason_codes, supersedes, effective_window.

Optional integrity:
source_staging_sha256, effective_window_sha256.

effective_window is a complete valid compact-v2 25-slot window.
No identity_key or free-form semantic/research prose.

Allowed reasons:
IDENTITY_REBIND, MALFORMED_JSON, STRUCTURAL_REBUILD, SEMANTIC_LINT, ROUTE_FAMILY_REMEDIATION.

Exactly one unsuperseded active overlay may exist per source window.

## Minimal run

1. Read this card and Worker V6 only.
2. Reconstruct current effective invalid queue from latest relevant validator/CI evidence; do not reread unchanged logs if queue identity is unchanged.
3. Select up to 6 windows, normally balancing up to 2 per lane; borrow unused capacity.
4. For each target fetch only source staging + its one authoritative shard/manifest.
5. Rebuild exact 25 slots. Preserve safe classifications where recoverable; source slot identity is never authority when corrupt.
6. Apply Worker V6 semantic rules. Research only material classification uncertainty.
7. Pre-validate compact v2 and create a NEW vNNN overlay.
8. Do not replace the source window.
9. Continue immediately to next target after successful create.

Lane3 spare capacity may audit 751-1050 route-family debt.

## Write failures

Primary write is create_file for the NEW overlay.
Git-object fallback is allowed only for transport/concurrency/GitHub operational failure, force=false.
For explicit safety/content/policy rejection, do not resend identical bytes through another transport and do not alter encoding/shape to evade safeguards. Leave target unrepaired and continue another independent target.

repair_status.json is legacy cache only; do not read/write it on the hot path.
No narrative run record is required.

A historical window counts repaired only when the effective validator accepts its single active overlay.

## Stop/report

Do not stop for one rejected target when another independent target exists.
Never disable the task for CI red or one write failure.

Report only overlays created, effective invalid counts by lane, Lane3 route-family state, and exact blockers.
