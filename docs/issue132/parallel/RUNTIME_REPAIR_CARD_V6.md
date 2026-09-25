# Issue132 Runtime Repair Card V6 — canonical append-only repair

Status: ACTIVE for Repair. Supersedes all earlier Runtime Repair cards operationally.
Shared semantic rules: RUNTIME_WORKER_CARD_V8.md.

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
IDENTITY_REBIND, MALFORMED_JSON, STRUCTURAL_REBUILD, SEMANTIC_LINT, ROUTE_FAMILY_REMEDIATION, HOLD_RESOLUTION.

Exactly one unsuperseded active overlay may exist per source window. Before selecting a target, inspect existing overlays first: a source with one currently valid active overlay is not unresolved merely because an older CI run still reports the raw source error.

## Minimal run
1. Read this card and Worker V8 only.
2. Reconstruct effective invalid queue from live source staging + active overlays + latest relevant validator/CI evidence. Prefer the latest staging-validator v3 JSON fields `effective_invalid_windows` / `effective_invalid_window_counts` when the run is current for HEAD; only parse detailed logs when those fields are absent/stale. Never blindly inherit a stale raw-CI queue.
3. Structural queue: select up to 6 historical invalid windows, normally up to 2/lane and borrowing unused capacity.
4. For each target fetch only source staging + needed authoritative shard/manifest, rebuild exact 25 slots, and apply Worker V8 semantics.
5. BEFORE creating an overlay, perform the same effective-window checks used by production staging validation, not a weaker local approximation:
   - every finalized row and hold binds to the authoritative slot by lane_local_index + review_seq + SHA256(identity_key);
   - compact finalized row field set equals COMPACT_ROW_FIELDS exactly;
   - compact hold field set equals COMPACT_HOLD_FIELDS exactly (reason_code + research_attempt_codes; never legacy hold_reason_code);
   - finalized + holds covers all 25 slots exactly once;
   - compact_row_to_full / validate_row semantic lint passes for every finalized row;
   - validate_compact_hold passes for every hold.
   If any check fails, fix the candidate in memory and do NOT persist it yet.
6. Only after those exact checks pass, create a NEW overlay version.
7. A write rejection on one target never blocks another independent target.

## Promotion-blocking hold queue
After structural attempts, or when structural capacity is unused, inspect only the oldest effective staging window at checkpoint prefix+1 in each lane.
- Research at most 3 promotion-blocking hold identities per run total.
- Research only material unresolved meaning; do not reread already resolved rows.
- If bounded research completes and meaning becomes clear, finalize normally.
- If bounded research completes but meaning still cannot be established safely, finalize that slot as terminal SEMANTIC_UNRESOLVED (RESEARCHED + evidence URL), not as a recurring hold.
- Keep a hold only when the research itself cannot be completed because of an actual tool/platform/interruption/evidence-access blocker.
- When any hold slot changes to a finalized row, publish a NEW overlay version for that full 25-slot source window with repair_reason_codes including HOLD_RESOLUTION, superseding the previous overlay if one exists.
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
Until that confirmation exists, report the overlay as CREATED_PENDING_VALIDATION and keep the effective-invalid count unchanged. Never report a reduced effective-invalid count with a parenthetical "pending validator confirmation".

## Stop/report
Never stop because one target rejects a write when another independent target exists. A failed/zero-output run must not disable or pause the scheduled Repair. Disable only after all owned debt is complete or explicit user instruction.

Report only overlays created, effective invalid counts by lane, promotion-blocking holds attempted/resolved, checkpoint promotions, Lane3 route-family state, and exact blockers.
