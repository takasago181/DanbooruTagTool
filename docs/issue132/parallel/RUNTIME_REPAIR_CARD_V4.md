# Issue132 Unified Repair Card V4 — append-only historical repair

Purpose: clear historical invalid staging without replacing old staging files.

This card supersedes RUNTIME_REPAIR_CARD_V3.md for Repair execution only.
Forward Worker 1/2/3 semantics and ownership do not change.

## 1. Scope and authority

Branch:
`research/taxonomy-usability-audit`

Repair owns:
- historical invalid staging in Lane 1/2/3;
- historical Lane 3 751-1050 route-family debt;
- append-only repair overlays and append-only repair run records.

Repair must never edit:
- an existing historical staging window;
- immutable checkpoints/corrections;
- forward-worker NEW frontier;
- main, production, UserData, #64/#76/#118.

Existing historical staging is immutable evidence, even when invalid.

## 2. Why V4 exists

Repeated live tests showed that existing-file replacement can be rejected at the write layer even when:
- the target branch/path is correct;
- the current blob SHA was fetched immediately before update;
- exact identity reconstruction is valid;
- compact-v2 payload is valid;
- contents update and Git-object blob fallback are both attempted.

NEW compact-v2 staging files continue to succeed in the same repository.

Therefore V4 changes the data model instead of retrying the same rejected replacement:
historical source staging remains untouched and an append-only repair overlay supplies the effective window.

This is not a safety-check bypass. Do not disguise, fragment, encode, or semantically alter a rejected payload to evade a safeguard.

## 3. Overlay location

For source:
`docs/issue132/parallel/lane-N/staging/window_XXXXXX_YYYYYY.json`

write only NEW files under:
`docs/issue132/parallel/lane-N/staging/repairs/`

Filename:
`repair_XXXXXX_YYYYYY_<effective_window_sha256-prefix>.json`

Use 16 lowercase hex characters of the effective-window SHA-256 by default.
Never overwrite an existing repair overlay.

## 4. Overlay schema

Schema:
`issue132-pass-a-staging-repair-overlay-v1`

Required top-level fields:
- `schema_version`
- `lane`
- `lane_local_start`
- `lane_local_end`
- `source_staging_path`
- `source_staging_blob_sha`
- `source_staging_sha256`
- `repair_reason_codes`
- `supersedes`
- `effective_window_sha256`
- `effective_window`

`effective_window` MUST be a complete valid `issue132-pass-a-staging-window-v2` object for exactly that 25-row source range.

The effective window keeps compact-v2 restrictions:
- exact lane_local_index + review_seq + SHA256(identity_key);
- classification codes/evidence URLs only;
- no identity_key;
- no semantic summary;
- no route-reason prose;
- no free-form hold/research prose.

Allowed repair_reason_codes:
- `IDENTITY_REBIND`
- `MALFORMED_JSON`
- `STRUCTURAL_REBUILD`
- `SEMANTIC_LINT`
- `ROUTE_FAMILY_REMEDIATION`

`source_staging_blob_sha` binds the overlay to the exact original Git blob.
`source_staging_sha256` binds to the exact original bytes independently.

`effective_window_sha256` is SHA-256 of canonical JSON:
UTF-8, ensure_ascii=false, keys sorted, separators `,` and `:`.

## 5. Supersession

Normally there is exactly one overlay for a source window.

If an overlay itself later needs correction:
- do not edit/delete it;
- create a second NEW overlay;
- list the older overlay filename in `supersedes`.

For each source window there must be exactly one unsuperseded active leaf.
The validator fails closed on multiple active leaves, broken supersession, source-byte mismatch, or payload-hash mismatch.

## 6. Repair algorithm

For each historical invalid window:

1. Reconstruct live queue from the latest applicable staging CI/validator evidence.
2. Fetch the exact source staging bytes and current GitHub blob SHA.
3. Fetch the authoritative lane shard + manifest covering the 25 exact slots.
4. Rebuild the effective window from authoritative tuples.
5. Preserve valid existing classifications where safely recoverable; invalid source identity/position is never authority.
6. Apply normal RUNTIME_WORKER_CARD_V4 semantic and exact-identity gates.
7. Produce full compact v2 effective_window.
8. Compute source SHA-256, effective canonical SHA-256, and overlay filename.
9. Create the overlay as a NEW file only.
10. Re-fetch the overlay.
11. Run `validate_parallel_staging.py` semantics conceptually: source binding, exact slots, compact-v2 reconstruction, 22-field gate.
12. Count the historical window repaired only when the effective validator accepts the overlay.

Never call update_file on the historical source window.

## 7. Transport

Primary:
- NEW repair overlay -> contents `create_file`.

Fallback only after a real create failure:
- standard GIT_OBJECT_WRITE_PROTOCOL_V1 fast-forward flow;
- create NEW overlay path;
- force=false only.

If the identical NEW overlay payload is repeatedly rejected by both authorized transports:
- classify `WRITE_RETRY_PENDING_DIAGNOSTIC`;
- do not repackage/obfuscate it;
- leave that target unrepaired;
- continue another independent historical target when safe.

## 8. Queue and throughput

Maintain the existing balanced queue:
- up to 2 oldest invalid Lane 1 windows;
- up to 2 oldest invalid Lane 2 windows;
- up to 2 oldest invalid Lane 3 windows;
- borrow unused capacity;
- Lane 3 spare capacity may service the 751-1050 route-family audit.

Normally max 6 historical windows/run.
Accuracy remains higher priority than quota.

A rejected target must not stop unrelated repair targets.

## 9. Status is no longer a mutable authority

`repair_status.json` is a legacy cache only. Do not depend on updating it.

Persist NEW compact run records when useful:
`docs/issue132/parallel/repair-runs/run_<UTC-basic>_<short-hash>.json`

Run records are append-only and may contain only compact operational metadata:
- branch head observed;
- CI run/head/error count if known;
- queue counts by lane;
- overlay filenames created;
- blocker target + failure class;
- Lane3 route-family audit state.

No semantic free-form payload is required.

Live source staging + active repair overlays + validator result remain the authority.

## 10. Coordinator contract

Coordinator must treat a source staging window with one valid active overlay as its effective repaired state.
It must not keep counting the original source error after the overlay passes validation.

Coordinator reconstructs:
- forward frontier from actual NEW staging/checkpoints;
- historical debt from effective staging validation;
- repair progress from active overlays, not stale repair_status.json.

## 11. Completion

Historical repair is complete only when the effective staging validator has zero historical invalid-window errors and the Lane 3 751-1050 route-family audit is terminal.

Do not merge or production-apply.
