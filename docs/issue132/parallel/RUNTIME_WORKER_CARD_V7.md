# Issue132 Runtime Worker Card V7 — canonical fast path

Status: ACTIVE for Worker 1/2/3. Supersedes all earlier Runtime Worker cards operationally. Frozen Pass-A semantic authority is unchanged.

## Goal lock
For every identity, judge one thing: can an image-generation user who does not know the exact Danbooru tag naturally reach the wanted visible concept from appearance, action/contact, body site, sexual position, clothing/exposure, composition/camera, scene, expression, object, or another genuinely useful browse axis?

Adult/sexual generation is a normal supported workflow. Adult/sexual content alone is never a reason to hold, suppress, reroute, or research. Research only when exact meaning or a classification decision is materially uncertain.

Optimize real discovery usefulness, not taxonomy completeness, route count, edit count, or prose richness.

## Fixed facts
Branch: research/taxonomy-usability-audit
Root: docs/issue132/parallel/
Lane rule: ((review_seq-1)%3)+1
Parent neutral SHA256: ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d
Parent identity-order SHA256: f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b
Shard size: 300 lane-local identities
Semantic work block: up to 100 identities
Persistence slice: 25 identities
Per-run ceiling: 300 identities

Deterministic paths only. Do not search for runtime paths.

## Minimal preflight
1. List own lane checkpoint/staging filenames once.
2. Derive checkpoint prefix, staging high-watermark, and oldest missing 25-slot write-gap below high-watermark.
3. Retry at most one old write-gap per run; it must not monopolize the run.
4. Fetch only shard(s)+manifest(s) intersecting actual work.
5. Manifest checks:
   - schema_version = issue132-worker-neutral-shard-v1;
   - lane/range/row_count/csv_path match the requested shard;
   - parent_neutral_sha256 equals the fixed Parent neutral SHA above;
   - parent_identity_order_sha256 equals the fixed Parent identity-order SHA above.
6. IMPORTANT HASH NAMES:
   - manifest.identity_order_sha256 is SHARD-LOCAL; never compare it to the global Parent identity-order SHA;
   - manifest.csv_sha256 is SHARD-LOCAL file metadata; never compare it to the Parent neutral SHA.
7. Parse the fetched shard and cheaply verify row_count plus deterministic review_seq/lane structure. For lane-local index i in lane N, expected review_seq = N + 3*(i-1). A row that violates this is a real shard conflict.
8. Do not recompute shard-local cryptographic hashes on the hot path unless parse/range structure is anomalous or a current CI/contract signal says the shard set drifted. Exact persisted identity is still checked by review_seq + SHA256(identity_key).

Do not read/write status.json. Do not read older runtime cards, old operation manuals, Issue comments, Coordinator/Repair files, CI logs, or full frozen docs unless a real invariant conflict requires fallback.

## Semantic execution
Work in blocks of up to 100 identities.

For each block:
1. scan the whole block;
2. decide compact classification for clear identities without drafting prose;
3. collect only ambiguities that could change discovery_mode, route strength/id, local refinement, body/theme facet, or route-vocabulary-gap;
4. batch research only those;
5. one bounded useful research pass is enough; unresolved material ambiguity becomes an exact-slot hold/SEMANTIC_UNRESOLVED rather than a guess;
6. split finished compact decisions into consecutive 25-slot persistence files.

CHECKED is correct when classification-relevant meaning is clear. Ignore nuance that cannot change discovery.

Decision order:
1. BROWSE_WORTHY / MIXED / SEARCH_ORIENTED / SEMANTIC_UNRESOLVED.
2. If browseable, choose one strongest natural CORE route.
3. Add SUPPORTING only if it is independently realistic as a user's starting browse axis.
4. Add local/body/theme only when explicitly or intrinsically entailed.
5. route_vocabulary_gap=YES only when an important user mental model is genuinely unrepresentable by the frozen 19 routes.

Hard lint:
- color/pattern adjective alone != COLOR_PATTERN_SHAPE;
- placement alone != POSE_POSITION;
- action alone != POSE unless body geometry independently matters;
- animal/plant motif/print/emblem/likeness != LIVING;
- object/fixture presence alone != SCENE_BACKGROUND;
- sexual content != CONTENT_RATING;
- optional facets are not inferred from common association.
SEARCH_ORIENTED and SEMANTIC_UNRESOLVED carry no routes/locals/body/theme.

## Exact compact-v2 persistence
Each NEW window top level must contain exactly the expected staging metadata:
- schema_version = issue132-pass-a-staging-window-v2
- lane
- lane_local_start
- lane_local_end
- parent_neutral_sha256
- parent_identity_order_sha256
- rows
- holds

The parent fields above use the GLOBAL Parent hashes, not shard-local hashes.

Every 25-slot file covers its authoritative slots exactly once by lane_local_index + review_seq + SHA256(identity_key). No gap, duplicate, shift, or extra identity. finalized + holds = exact window size.

Rows contain only compact-v2 fields. Holds contain only compact-v2 hold fields. Never persist identity_key or free-form semantic/research prose.

Before each write validate in memory:
- exact slot coverage;
- exact review_seq/hash binding;
- allowed codes;
- route/local parent consistency;
- mode constraints;
- exact compact field sets.

No post-write semantic reread/reconstruction.

## Persistence
Normal NEW window: contents create_file.

After success, count persisted and continue immediately. Do not re-fetch the just-created file only to repeat semantic validation.

If create_file fails:
- transport/concurrency/GitHub operational failure: GIT_OBJECT_WRITE_PROTOCOL_V1 fallback may create the SAME NEW path, force=false;
- explicit safety/content/policy rejection: do not resend identical bytes through another transport and never disguise/encode/fragment to evade safeguards; leave that slice as a write-gap and continue later independent NEW slices when safe.

Forward workers never update or replace historical staging.

## Ownership
Worker = NEW classification + exact pre-write validation + persistence.
Coordinator = QA, CI/drift interpretation, effective progress/debt accounting.
Repair = historical invalid staging, promotion-blocking historical holds, append-only repair overlays.

## Stop/report
Continue until the 300-slot run ceiling, lane completion, a true contract/shard mismatch, or actual tool/platform interruption.
A successful 25-row save is never a stop. One rejected 25-row save is not a stop when later independent work is safe.

Report only lane, checkpoint prefix/high-watermark, persisted count, finalized/holds, write-gaps, next high-watermark, and exact blocker.
