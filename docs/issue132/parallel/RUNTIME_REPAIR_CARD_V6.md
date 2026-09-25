# Issue132 Runtime Repair Card V6 — canonical append-only repair

Status: ACTIVE for Repair. Supersedes all earlier Runtime Repair cards operationally.
Shared semantic rules: RUNTIME_WORKER_CARD_V7.md.

Goal: clear historical staging debt and promotion-blocking historical holds without rewriting old evidence or consuming forward-worker capacity.

Branch: research/taxonomy-usability-audit
Root: docs/issue132/parallel/

## Ownership
Repair owns only:
- historical invalid staging in Lane 1/2/3;
- promotion-blocking holds in the oldest effective staging window immediately after each lane checkpoint prefix;
- historical Lane 3 751-1050 route-family debt;
- append-only repair overlays;
- mechanical promotion of a fully resolved effective prefix window when safe.

Never edit existing historical staging, immutable checkpoint/correction files, forward NEW windows, main, production, UserData, #64/#76/#118.

## Effective overlay model
Historical source staging is immutable evidence.
Repairs are NEW files under:
docs/issue132/parallel/lane-N/staging/repairs/

Filename: repair_XXXXXX_YYYYYY_vNNN.json
Schema: issue132-pass-a-staging-repair-overlay-v1

Required:
schema_version, lane, lane_local_start, lane_local_end,
source_staging_path, source_staging_blob_sha,
repair_reason_codes, supersedes, effective_window.

Optional:
source_staging_sha256, effective_window_sha256.

effective_window must be a complete valid issue132-pass-a-staging-window-v2 object for exactly the source range. No identity_key or free-form semantic/research prose.

Allowed reasons:
IDENTITY_REBIND, MALFORMED_JSON, STRUCTURAL_REBUILD, SEMANTIC_LINT, ROUTE_FAMILY_REMEDIATION.

Exactly one unsuperseded active overlay may exist per source window. Before selecting a target, inspect existing overlays first: a source with one currently valid active overlay is not unresolved merely because an older CI run still reports the raw source error.

## Minimal run
1. Read this card and Worker V7 only.
2. Reconstruct effective invalid queue from live source staging + active overlays + latest relevant validator/CI evidence. Never blindly inherit a stale raw-CI queue.
3. Structural queue: select up to 6 historical invalid windows, normally up to 2/lane and borrowing unused capacity.
4. For each target fetch only source staging + needed authoritative shard/manifest, rebuild exact 25 slots, apply Worker V7 semantics, pre-validate compact v2, and create a NEW overlay version.
5. A write rejection on one target never blocks another independent target.

## Promotion-blocking hold queue
After structural attempts, or when structural capacity is unused, inspect only the oldest effective staging window at checkpoint prefix+1 in each lane.
- Research at most 3 promotion-blocking hold identities per run total.
- Research only material unresolved meaning; do not reread already resolved rows.
- If a hold resolves, publish a NEW overlay version for that full 25-slot source window, superseding the previous overlay if one exists.
- If evidence remains insufficient after one bounded useful attempt, keep the hold and move on.
- Do not let hold research displace the historical invalid-window queue.

When the effective prefix window has zero holds and passes exact validation, Repair may mechanically promote it to a NEW immutable checkpoint using scripts/issue132/promote_staging_window.py semantics. The promotion implementation must resolve the active repair overlay first. Never overwrite a checkpoint. Consecutive complete effective prefix windows may be promoted mechanically without semantic rereview.

If checkpoint creation itself is explicitly content/policy rejected, do not repackage or resend identical bytes through another transport; leave promotion pending and continue other repair work.

Lane3 spare capacity may service the 751-1050 route-family debt.

## Writes
NEW overlay: contents create_file first.
Transport/concurrency/GitHub operational failure may use GIT_OBJECT_WRITE_PROTOCOL_V1 for the same NEW path, force=false.
Explicit safety/content/policy rejection is not retried through a second transport with identical bytes and is never evaded.

repair_status.json is legacy cache only; do not read/write it on the hot path. No narrative run record is required.

A historical window counts repaired only when the effective validator accepts its active overlay.

## Stop/report
Never stop because one target rejects a write when another independent target exists. Never disable for CI red or one write failure.

Report only overlays created, effective invalid counts by lane, promotion-blocking holds attempted/resolved, checkpoint promotions, Lane3 route-family state, and exact blockers.
