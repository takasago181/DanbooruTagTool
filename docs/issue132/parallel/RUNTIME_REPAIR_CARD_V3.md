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

## Authorized staging write path — VERIFIED

Staging repair writes on this research branch are explicitly authorized non-authoritative maintenance. Do NOT self-block merely because an existing staging JSON is being replaced.

A write is authorized when ALL are true:
1. branch is exactly `research/taxonomy-usability-audit`;
2. target is under `docs/issue132/parallel/lane-1/staging/`, `lane-2/staging/`, `lane-3/staging/`, or is `docs/issue132/parallel/repair_status.json`;
3. immutable checkpoint/correction files, main, production, UserData, #64/#76/#118 are untouched.

Write protocol:
- EXISTING staging/status file: fetch that exact path immediately before write, use its current blob SHA with `update_file`.
- NEW staging/status file: use `create_file`.
- Do not use update_file on a path that was not successfully fetched as EXISTING.
- Do not use create_file on a path already confirmed EXISTING.
- After successful write, re-fetch the exact file and run the required exact tuple/22-field validation.
- A semantic replacement of a non-authoritative invalid staging window is permitted when rebuilt from authoritative shard tuples and validated before/after write.
- Large textual diff is NOT by itself a safety blocker. Full-window replacement is expected for identity-shift/gap/duplicate corruption.

Verified connector capability on this branch:
- create + delete in the Issue132 parallel area succeeded;
- fetch current SHA + update existing Lane1 staging succeeded;
- exact original bytes were restored successfully after the write-path probe.

Therefore generic messages such as "staging update is unsafe", "existing staging replacement blocked for safety", or "large rewrite not allowed" are INVALID blocker reasons.

Only classify TOOL_LIMIT/write blocker after an actual applicable GitHub operation fails. Record:
- target path;
- EXISTING vs NEW;
- branch;
- SHA used for EXISTING;
- exact operation attempted;
- exact returned error.

If contents `update_file` genuinely fails despite current SHA and correct branch, the Repair task may use the equivalent authorized Git object blob/tree/commit/ref path if available. Never redirect to main.

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

## Primary write transport — Git object protocol

All Issue132 writes use `docs/issue132/parallel/GIT_OBJECT_WRITE_PROTOCOL_V1.md` as the PRIMARY transport. Do not use contents `create_file/update_file` for normal Issue132 persistence. Use branch-head/tree -> create_blob -> create_tree -> create_commit -> re-fetch head -> update_ref(force=false), with retry on concurrent branch advance exactly as defined there. Contents API is fallback only when the Git-object path is unavailable.

A pre-write runtime safety refusal on contents API is not a blocker and must not stop/disable the task. Only an actually attempted Git-object path failure after the protocol's retries may become a write blocker.


## Compact staging v2 repair rule

For every historical window that Repair rebuilds or materially rewrites, output `issue132-pass-a-staging-window-v2` using the compact v2 contract in `RUNTIME_WORKER_CARD_V4.md`. Existing clean v1 staging may remain untouched; there is no bulk migration requirement.

Repair MUST NOT republish `identity_key`, semantic summaries, route-reason prose, hold-reason prose, or research prose in rebuilt staging. Bind identity only by `lane_local_index + review_seq + identity_sha256`, where the hash is SHA256 of the authoritative UTF-8 identity key.

For structural rebuilds:
- load exact authoritative tuples from shard;
- classify/research exactly as before;
- persist only compact classification codes/evidence URLs and coded holds;
- re-fetch and validate with `validate_parallel_staging.py`.

For tuple-clean semantic patches:
- convert the affected window to v2 if a write is needed;
- preserve unaffected classifications exactly;
- change only fields supported by the repair evidence.

Compact v2 contents writes are preferred because payloads no longer contain repeated identity/free-form semantic text. Git-object write protocol is fallback only after an actual contents API failure. Never disable Repair due to a transient write refusal.

