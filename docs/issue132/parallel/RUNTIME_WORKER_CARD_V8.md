# Issue132 Runtime Worker Card V8 — minimal hot path

Status: ACTIVE for Worker 1/2/3. Supersedes V7 operationally. Frozen Pass-A semantic authority is unchanged.

## Goal
Classify for real image-generation discovery: a user who does not know the exact Danbooru tag should be able to reach the wanted visible concept naturally. Appearance, action/contact, body site, sexual position, clothing/exposure, composition/camera, scene, expression, object and other genuinely useful browse axes matter.

Adult/sexual generation is normal supported use. Adult/sexual content alone never triggers suppression, extra research, hold, or rerouting. Accuracy wins over guessing.

## Fixed contract
Branch: research/taxonomy-usability-audit
Root: docs/issue132/parallel/
Lane rule: ((review_seq-1)%3)+1
Parent neutral SHA256: ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d
Parent identity-order SHA256: f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b
Lane lengths: 1=10335, 2=10334, 3=10334
Shard size: 300 lane-local
Persistence slice: 25
Lookahead/research block: up to 100
Run ceiling: 300

## Mandatory hot path

Do not read checkpoints, status files, CI, Issue history, Repair/Coordinator files, superseded cards, or full frozen docs during a normal Worker run.

Use the fewest possible tool round-trips. When orchestration/Code Mode is available, batch hot-path GitHub reads instead of issuing serial discovery calls.

1. Read RUNTIME_AUTHORITY.json and this active Worker card. Also read ONLY the machine-readable file named by `authority.contracts.semantic_vocabulary_path`; batch these reads when possible.
   - Require its schema_version to equal `authority.contracts.semantic_vocabulary_schema_version`.
   - When the fetch exposes a Git blob SHA, require it to equal `authority.contracts.semantic_vocabulary_git_blob_sha`.
   - Use only these frozen keys from it: route_ids, local_refinement_parent, body_site_ids, theme_ids, allowed_discovery_modes, allowed_route_strengths, allowed_review_depths.
   - Do NOT read the long semantic-contract prose on the normal hot path. The manifest above is sufficient and authoritative for allowed codes and local-parent consistency.
   - If this frozen manifest is missing or mismatched, that is a true contract blocker. Do not guess vocabulary.
2. List only this lane's staging directory once. Filter only `window_XXXXXX_YYYYYY.json` files.
   - A single directory-list 404/timeout/tool error is NOT proof that staging is absent and is NOT by itself a valid run blocker.
   - On such an operational failure, immediately use the metadata-only tree fallback: fetch the branch HEAD/tree and one recursive Git tree, then filter exact paths matching `docs/issue132/parallel/lane-N/staging/window_XXXXXX_YYYYYY.json`.
   - Do not read file contents during this fallback. Do not search Issue history or status caches.
   - Stop for frontier discovery only if BOTH the normal listing and the tree fallback fail to provide authoritative path metadata.
3. Compute from whichever authoritative path listing succeeded:
   - high_watermark = highest persisted window end;
   - new_frontier = high_watermark + 1;
   - any missing 25-slot window below high_watermark = write-gap.
   Do not read checkpoint directories; Coordinator owns checkpoint-prefix accounting.
4. NEW work takes priority. Do not spend the start of a run rebuilding an old write-gap. Persist at least one NEW slice first when safe; retry at most one old write-gap later if budget remains.
5. Determine the authoritative shard path arithmetically; never search:
   - shard_start = floor((lane_local_index-1)/300)*300 + 1
   - shard_end = min(shard_start+299, lane_length)
   - CSV: docs/issue132/parallel/input-shards/lane-N/shard_SSSSSS_EEEEEE.csv
   - manifest: same basename + .manifest.json
6. Fetch that CSV and manifest directly, preferably in the same batched read.
7. Manifest gate:
   - schema_version=issue132-worker-neutral-shard-v1;
   - lane/start/end/row_count/csv_path match;
   - parent_neutral_sha256 equals global Parent neutral above;
   - parent_identity_order_sha256 equals global Parent identity-order above.
   `identity_order_sha256` and `csv_sha256` are SHARD-LOCAL and are never compared with global parent hashes.
8. Cheap CSV gate: parse, row_count matches, and lane-local index i has review_seq = lane + 3*(i-1). Recompute shard cryptographic hashes only if structure is anomalous or current contract evidence explicitly signals drift.

## Streaming semantic pipeline

The 100-row number is a lookahead/research convenience, NOT a persistence barrier.

Process consecutive 25-slot slices. For each slice:
1. classify obvious identities directly into compact decisions;
2. research only identities whose uncertainty could change discovery_mode, route id/strength, local refinement, body/theme facet, or route-vocabulary-gap;
3. batch a few related ambiguities when useful, but never delay a completed 25-slot slice merely to finish later rows;
4. one bounded useful research pass is enough;
5. completed research but still no safe tag-specific meaning => FINALIZE as SEMANTIC_UNRESOLVED, review_depth=RESEARCHED, evidence_urls non-empty, no routes/locals/body/theme, gap=NO;
6. HOLD only when the required research itself could not be completed because of an actual tool/platform/evidence-access interruption;
7. as soon as all 25 exact slots are finalized/held and prevalidated, persist that slice immediately;
8. then continue to the next 25. Do not wait for 50/100/300 decisions before the first write.

If execution budget appears constrained, prioritize finishing and persisting the current exact 25-slot slice over starting research for a later slice.

## Classification
Modes: BROWSE_WORTHY / MIXED / SEARCH_ORIENTED / SEMANTIC_UNRESOLVED.
For browseable rows choose one strongest natural CORE route. Add SUPPORTING only if it is independently realistic as a user's starting browse axis. Add local/body/theme only when explicitly or intrinsically entailed. gap=YES only when an important user mental model is genuinely unrepresentable by the frozen 19 routes.

Hard lint:
- color/pattern adjective alone != COLOR_PATTERN_SHAPE
- placement alone != POSE_POSITION
- action alone != POSE unless body geometry independently matters
- animal/plant motif/print/emblem/likeness != LIVING
- object/fixture presence alone != SCENE_BACKGROUND
- sexual content != CONTENT_RATING
- optional facets are not inferred from common association
SEARCH_ORIENTED and SEMANTIC_UNRESOLVED carry no routes/locals/body/theme.

## Compact v2 exact gate
Each NEW file is `issue132-pass-a-staging-window-v2` with:
schema_version, lane, lane_local_start, lane_local_end,
parent_neutral_sha256, parent_identity_order_sha256, rows, holds.

Parent hashes are GLOBAL parent hashes.

Every slot is bound exactly by lane_local_index + review_seq + SHA256(identity_key). No gap/duplicate/shift/extra. finalized+holds=window size.

Rows and holds use only compact-v2 allowed fields. Never persist identity_key or free-form semantic/research prose.

Before write check exact coverage/binding, allowed codes, route-local consistency, mode constraints, researched evidence, SEMANTIC_UNRESOLVED constraints, and exact compact field sets.

Frozen-code validation is mechanical:
- each route id must be in semantic_manifest.route_ids;
- each route strength must be in semantic_manifest.allowed_route_strengths;
- discovery_mode must be in semantic_manifest.allowed_discovery_modes;
- review_depth must be in semantic_manifest.allowed_review_depths;
- each local_refinement_id must be a key in semantic_manifest.local_refinement_parent AND its mapped parent route must be selected in that row;
- normally at most one local refinement per selected parent route;
- every body_site_id must be in semantic_manifest.body_site_ids;
- every theme_id must be in semantic_manifest.theme_ids.

Compact row fields are exactly:
lane_local_index, review_seq, identity_sha256, discovery_mode, routes, local_refinement_ids, body_site_ids, theme_ids, route_vocabulary_gap, review_depth, evidence_urls.

Compact hold fields are exactly:
lane_local_index, review_seq, identity_sha256, reason_code, research_attempt_codes.

Allowed compact hold reason_code values:
DIRECT_EVIDENCE_NOT_FOUND, IDENTITY_AMBIGUOUS, SEMANTIC_SCOPE_AMBIGUOUS, ROUTE_AMBIGUOUS, OTHER_UNRESOLVED.

Allowed research_attempt_codes:
DANBOORU_EXACT, SAFEBOORU_EXACT, OFFICIAL_SOURCE, DIRECT_WEB_SOURCE, OTHER_DIRECT_SOURCE.

A hold requires a non-empty research_attempt_codes list. Do not invent any code outside these frozen/current compact sets.

## Write
NEW window => contents create_file.
After success: count it and immediately continue. No post-write re-fetch or semantic reconstruction.

Failure:
- transport/concurrency/GitHub operational => same NEW path may use GIT_OBJECT_WRITE_PROTOCOL_V1, force=false;
- explicit safety/content/policy rejection => do not resend identical bytes through another transport and never disguise/encode/fragment; record the write-gap and continue to later independent NEW slices when safe.

Forward Worker never updates historical staging.

## Valid stop
Only: 300 slots attempted as far as safely possible, lane complete, true contract/shard mismatch, or required authoritative state still cannot be recovered after the card's allowed operational fallback(s).

One transient 404/timeout/tool failure is not sufficient when an authorized independent metadata path remains available. Preflight consuming the run is an execution-design failure, not a semantic blocker. The hot path and its fallback must be attempted before optional work.

Automation liveness is separate from run success. A tool failure, write rejection, semantic blocker, or zero-persist run must be reported but MUST NOT disable/pause the scheduled Worker. Disable only after lane completion or explicit user instruction.

## Report
Only: lane, high_watermark, persisted, finalized/holds, write-gaps, next high_watermark, exact blocker.
