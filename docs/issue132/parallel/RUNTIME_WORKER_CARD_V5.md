# Issue132 Runtime Worker Card V5 — throughput fast path

Status: ACTIVE FOR FORWARD WORKERS.
Supersedes V4 operationally for Worker 1/2/3 only.
Frozen Pass-A semantic authority is unchanged.

## Goal

Process NEW forward identities accurately and persist useful progress with minimal administrative overhead.

## Fixed authority

Branch: research/taxonomy-usability-audit
Root: docs/issue132/parallel/
Neutral parent SHA256: ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d
Identity-order SHA256: f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b
Lane rule: ((review_seq - 1) % 3) + 1
Shard size: 300 lane-local rows.

Do not search for paths. Deterministic paths:
- staging: docs/issue132/parallel/lane-N/staging/window_XXXXXX_YYYYYY.json
- shard: docs/issue132/parallel/input-shards/lane-N/shard_XXXXXX_YYYYYY.csv
- shard manifest: same basename + .manifest.json

Frontier authority is actual staging/checkpoint filenames, not status.json.

## Per-run hot path

1. List own lane staging/checkpoints once. Derive (a) oldest missing 25-slot gap below the current high-watermark, if any, and (b) new_frontier = highest persisted staging end + 1 (or checkpoint prefix + 1 when no staging exists).
2. Retry at most one old write-gap per run, then spend the remaining budget on NEW windows from new_frontier. A write-gap must not monopolize the lane.
3. Fetch only the one or two 300-row shards + manifests intersecting the actual work span.
4. Verify shard manifest parent neutral/order SHA and exact lane/range.
5. Process up to 300 identities in consecutive 25-slot windows.
6. Persist each completed 25-slot window as NEW compact v2.
7. Continue immediately after a successful create. Do not re-fetch the just-created file merely to prove GitHub preserved the bytes.
8. Do not read/write lane status.json.
9. Do not poll CI.
10. Do not perform 100-row QA. Coordinator owns independent QA.
11. Stop only for actual tool interruption, contract/shard mismatch, lane completion, or the run work budget. One content-rejected window alone is not a lane stop.

## Fast semantic pass

For each 25-slot window:
- scan all 25 identities first;
- finalize obvious/unambiguous identities in one batch;
- collect only materially ambiguous identities;
- batch research for ambiguous identities when practical;
- after one bounded useful research attempt, unresolved may become an exact-slot hold;
- do not repeatedly research the same hold in the same run.

CHECKED is valid for ordinary clear visual concepts. Do not web-search merely for formality.

Research only when material meaning/routing would otherwise be guessed:
- unfamiliar/polysemous/specialist term;
- qualifier/reference whose exact scope affects classification;
- technical/cultural/sexual/anatomical boundary that changes route/local/body/theme;
- any material decision that is genuinely uncertain.

If direct evidence remains insufficient, hold/SEMANTIC_UNRESOLVED rather than guess.

## Classification rules retained

Discovery:
- BROWSE_WORTHY: natural visual/category shelf.
- MIXED: both browse and name/reference search are genuinely useful.
- SEARCH_ORIENTED: understood name/reference lookup; routes/locals/body/theme empty.
- SEMANTIC_UNRESOLVED: meaning remains materially uncertain after bounded research.

Routes remain the frozen 19-route vocabulary.
Normally one CORE. Add SUPPORTING only when independently useful for unknown-tag discovery.

Hard anti-overclassification:
- adjective color/pattern alone != COLOR_PATTERN_SHAPE;
- object/clothing placement alone != POSE_POSITION;
- action alone != POSE_POSITION unless geometry independently matters;
- animal/plant motif/print/emblem/likeness != LIVING;
- object/fixture presence alone != SCENE_BACKGROUND;
- sexual content != CONTENT_RATING.

Local refinements require their parent route and exact semantic entailment.
Body/theme facets must be intrinsic, not merely associated.

## Exact identity / compact v2

Every 25-slot window must cover the authoritative slots exactly once:
lane_local_index + review_seq + SHA256(identity_key).

No gap, duplicate, shift, or extra identity.
finalized + holds = exact window size.

Persist schema issue132-pass-a-staging-window-v2 only.
Rows contain compact classification codes and evidence URLs only.
Holds contain exact identity hashes + coded reason/research-attempt values only.
Never persist identity_key or free-form semantic/research prose.

Before write, validate in memory:
- exact 25-slot coverage;
- exact identity hash binding;
- allowed discovery/route/local/body/theme codes;
- parent/local consistency;
- SEARCH_ORIENTED / unresolved constraints;
- compact field-set shape.

This pre-write gate replaces the old redundant post-write fetch + 22-field reconstruction loop.

## Persistence

Normal NEW window:
create_file only.

After successful create_file, count it persisted and move directly to the next 25-slot window.

If create_file fails:
- transport/concurrency/GitHub operational failure: GIT_OBJECT_WRITE_PROTOCOL_V1 fallback is allowed for the same NEW path, force=false;
- explicit safety/content/policy rejection: do NOT resend the same bytes through Git-object fallback. Count zero for that window, record it as a write-gap, and continue to the next independent 25-slot window in the same run when possible;
- never disguise, fragment, encode, or semantically alter a payload to evade a safeguard.

Forward workers never repair or overwrite historical staging.

## QA ownership

Worker: per-row semantic accuracy + exact pre-write gate only.
Coordinator: 100-row/high-risk/spot-check QA, CI interpretation, drift detection.
Repair: historical invalid staging/repair overlays.

No duplicated QA between Worker and Coordinator.

## Reporting

Return only:
- start frontier;
- persisted NEW count;
- finalized/holds;
- next frontier;
- exact blocker if any.

Do not spend execution budget producing narrative status.
