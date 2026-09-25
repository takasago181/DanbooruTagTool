# Issue132 Runtime Worker Card V6 — goal-locked fast path

Status: ACTIVE for Worker 1/2/3. Supersedes V5 operationally only. Frozen Pass-A semantic authority remains unchanged.

## Product goal lock

Judge every identity for one purpose:

> An image-generation user who does not know the exact Danbooru tag should be able to reach the wanted visible concept naturally from appearance, action/contact, body site, sexual position, clothing/exposure, composition/camera, scene, expression, object, or another genuinely useful browse axis.

Adult/sexual generation is a normal supported workflow. Do not research, hold, suppress, or reroute a concept merely because it is sexual. Research only when its exact meaning or a classification decision is materially uncertain.

Optimize for real discovery usefulness, not taxonomy completeness, number of routes, number of edits, or prose richness.

## Fixed runtime facts

Branch: research/taxonomy-usability-audit
Root: docs/issue132/parallel/
Lane rule: ((review_seq-1)%3)+1
Parent neutral SHA256: ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d
Parent identity-order SHA256: f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b
Shard size: 300 lane-local identities.
Persistence slice: 25 slots.
Semantic work block: up to 100 slots.
Per-run ceiling: 300 slots.

Deterministic paths only. Do not search for runtime paths.

## Minimal preflight

Per run:
1. List own lane staging/checkpoints once.
2. Derive high-watermark from actual persisted filenames.
3. Note oldest missing 25-slot write-gap below high-watermark, if any.
4. Retry at most one old write-gap; never let it monopolize the run.
5. Fetch only shard(s)+manifest(s) intersecting the actual work span.
6. Verify the manifest's `parent_neutral_sha256` equals the fixed Parent neutral SHA256 above and `parent_identity_order_sha256` equals the fixed Parent identity-order SHA256 above. Also verify lane, lane-local range, row_count and csv_path match the requested shard.
7. `identity_order_sha256` inside a shard manifest is SHARD-LOCAL. It is expected to differ between shards and MUST NOT be compared with the global Parent identity-order SHA. Do not stop merely because those two values differ.
8. On the hot path, do not recompute the shard-local identity-order hash when the tracked shard+manifest are from the validated shard set and the parent/lane/range/path metadata above are consistent. Exact per-row identity is still enforced by review_seq + SHA256(identity_key) before persistence.

Do NOT read or update status.json.
Do NOT read old Worker cards, CURRENT_AUTOMATION_OPERATION, Issue comments, CI logs, Coordinator files, Repair files, or full frozen docs unless this card/hash or shard invariants actually conflict.

## Semantic execution

Work in blocks of up to 100 identities, not 25.

For each block:
1. Scan the whole block.
2. Independently decide compact classification for obvious identities without drafting prose.
3. Collect only identities whose uncertainty could change discovery_mode, CORE/SUPPORTING route, local refinement, body facet, theme facet, or route-vocabulary-gap.
4. Batch research only those ambiguous identities.
5. One bounded useful research pass is enough. If material uncertainty remains, use an exact-slot hold/SEMANTIC_UNRESOLVED rather than guessing.
6. Split completed compact decisions into consecutive 25-slot persistence files and save them sequentially.

Do not draft semantic_summary_ja, route-reason prose, or other 22-field narrative during forward work. Compact codes are the operational artifact.

CHECKED is correct when the classification-relevant meaning is clear. Do not research irrelevant nuance that cannot change discovery.

## Classification decision order

For each identity:
1. Is it primarily visual browse, name/reference search, both, or unresolved?
2. If browseable, choose the single strongest natural CORE shelf.
3. Add SUPPORTING only if a user could independently and realistically start there without already knowing the tag.
4. Add local/body/theme only when explicitly/intrinsically entailed.
5. Mark route_vocabulary_gap only when an important user mental model is genuinely unrepresentable by the existing 19 routes.

Prefer one correct CORE over route inflation.

Hard lint:
- color/pattern adjective alone != COLOR_PATTERN_SHAPE;
- placement alone != POSE_POSITION;
- action alone != POSE unless geometry independently matters;
- animal/plant motif/print/emblem/likeness != LIVING;
- object/fixture presence alone != SCENE_BACKGROUND;
- sexual content != CONTENT_RATING;
- a sexual/adult tag is not special-cased merely for being sexual;
- optional facets are not inferred from common association.

SEARCH_ORIENTED and SEMANTIC_UNRESOLVED carry no routes/locals/body/theme.

## Exact identity and compact v2

Every persisted 25-slot file must cover its authoritative slots exactly once by:
lane_local_index + review_seq + SHA256(identity_key).

No gap, duplicate, shift, or extra identity inside a file.
finalized + holds = exact file size.

Persist only issue132-pass-a-staging-window-v2 compact fields. Never persist identity_key or free-form semantic/research prose.

Before each write validate in memory:
- exact slot coverage;
- exact review_seq/hash binding;
- allowed codes;
- route/local parent consistency;
- mode constraints;
- compact field set.

No post-write semantic revalidation.

## Persistence

Normal NEW window: create_file.

After successful create_file: count persisted and continue immediately. Do not re-fetch just-created bytes.

If create_file fails:
- transport/concurrency/GitHub operational failure: Git-object fallback may be used for the same NEW path, force=false;
- explicit safety/content/policy rejection: do not resend identical bytes through another transport, do not disguise/encode/fragment to evade safeguards; leave that 25-slot file as a write-gap and continue to the next independent NEW 25-slot file when possible.

Forward workers never update/replace historical staging.

## Ownership

Worker: NEW semantic classification + exact pre-write validation + persistence.
Coordinator: QA, CI interpretation, drift detection, effective progress/debt accounting.
Repair: historical invalid staging + append-only repair overlays.

No duplicated QA or status bookkeeping in Worker runs.

## Stop

Continue until 300 slots attempted/persisted as far as safely possible, lane completion, a true contract/shard mismatch, or actual tool/platform interruption.

A successful 25-row write is never a stop condition.
A single rejected 25-row write is never a stop condition when later independent work is safe.

## Report

Only: lane, start/high-watermark, persisted count, finalized/holds, write-gaps, next high-watermark, exact blocker if any.
