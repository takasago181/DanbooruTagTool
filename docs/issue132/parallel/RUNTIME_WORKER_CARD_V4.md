# Issue132 Runtime Worker Card V4 — single hot-path card

Normal forward workers use this card as the only body-level operational/semantic card.

Pinned source cache:
- WORKER_EXECUTION_CARD_V1.md blob: 3c54b646f2f5d780efce2dc9a21d0e3f7cdf3ac9
- pass_a_contract_manifest_v1.json blob: 3bd09dde3a0fd15b9a3f86b22f294135f96a707c
- parallel_plan_v1.json blob: 0b751f9551589bde153b3e1e14bd341f738d005c

At run start verify these SHAs by metadata only. If any differs, or CI reports frozen-contract/neutral drift, fall back to the full frozen authority and stop normal fast-path execution. Otherwise do not fetch those bodies.

## Mission
For each identity: if an image-generation user wants the visible concept but does not know the exact Danbooru tag, where would they naturally look? Optimize unknown-tag discovery and semantic accuracy. Current app placement is not evidence.

## Discovery
- BROWSE_WORTHY: stable visual/category shelf is natural.
- MIXED: both visual browse and name/reference search are materially natural.
- SEARCH_ORIENTED: understood name/reference/provenance lookup; no routes/locals/body/theme; gap=NO.
- SEMANTIC_UNRESOLVED: meaning remains materially uncertain after research; RESEARCHED + direct evidence + uncertainty; no routes/locals/body/theme; gap=NO.

## Routes
PEOPLE_COUNT(count); RELATION_ROLE(role/relation); BODY_SITE(anatomical site central); HAIR_FACE(hair/facial appearance); CLOTHING_EXPOSURE(garment/accessory/state/exposure); TOOL_OBJECT(prop/tool/weapon/vehicle/food/device); LIVING(animal/plant); NONHUMAN_TRANSFORM(nonhuman/altered anatomy); ACTION_CONTACT(action/contact/interaction/object manipulation); POSE_POSITION(body geometry/posture/position); EXPRESSION_GAZE(expression/emotion/gaze); FLUID_EXCRETION(intrinsic body fluids/excretion); COMPOSITION_CAMERA(view/crop/framing); SCENE_BACKGROUND(location/environment); LIGHT_TIME_WEATHER(light/time/weather); COLOR_PATTERN_SHAPE(color/pattern/shape when itself a meaningful control); STYLE_PROCESSING(style/render/medium/process); TEXT_SYMBOL(independent visible text/symbol/layout); CONTENT_RATING(true meta/content presentation only).

Normally one CORE. Add SUPPORTING only when it is an independent realistic browse axis.

Hard lint:
- color/pattern adjective alone != COLOR_PATTERN_SHAPE;
- object/clothing placement alone != POSE_POSITION;
- action alone != POSE unless geometry independently matters;
- animal/plant print, motif, emblem, likeness != LIVING;
- object/fixture presence alone != SCENE_BACKGROUND;
- sexual content != CONTENT_RATING.

## Local refinements
Only when parent route is selected and exact meaning entails it:
ACTION_CONTACT/INTERACTION, ACTION_CONTACT/INTIMATE, ACTION_CONTACT/OBJECT_USE;
CLOTHING/ACCESSORY, CLOTHING/COSTUME, CLOTHING/EVERYDAY, CLOTHING/UNIFORM, CLOTHING_STATE_EXPOSURE/;
LIVING_NATURE/CREATURE, LIVING_NATURE/PLANT;
OBJECT_PROP/DAILY, OBJECT_PROP/FOOD, OBJECT_PROP/VEHICLE, OBJECT_PROP/WEAPON;
TEXT_SYMBOL/LAYOUT, TEXT_SYMBOL/SYMBOL, TEXT_SYMBOL/TEXT;
EXPRESSION_EMOTION/, GAZE_ORIENTATION/.
Zero is valid. Normally max one local per selected parent.

Body facets intrinsic/explicit only: MALE_GENITAL, BREAST_NIPPLE, FEMALE_GENITAL, MOUTH_ORAL, BUTTOCK_ANAL, URETHRA.
Theme facets intrinsic only: BDSM_RESTRAINT, INJURY_R18G, REPRO_PREGNANCY_LACTATION.

## Research gate
CHECKED only when meaning and all material route/local/facet choices are clear.
Research when unfamiliar/polysemous/specialist; obscure proper noun or material qualifier; technical/cultural reference affecting classification; sexual/anatomical/fetish boundary; or any material field would otherwise be guessed from spelling.
Batch 5–10 independent ambiguities in one search call when practical, but record evidence per identity.
Evidence preference: exact Danbooru/Safebooru definition/direct tag evidence > official > strong direct reference. Reject generic adjacent pages, model/LoRA pages, unrelated image hosts, and single-example evidence as default semantic authority.
If still uncertain: SEMANTIC_UNRESOLVED, never guess.

## Output
Exactly 22 fields:
review_seq, identity_key, manual_seen, semantic_summary_ja, discovery_mode,
route_1_id, route_1_strength, route_1_reason_ja,
route_2_id, route_2_strength, route_2_reason_ja,
route_3_id, route_3_strength, route_3_reason_ja,
local_refinement_ids, body_site_ids, theme_ids,
route_vocabulary_gap, route_vocabulary_gap_note,
review_depth, evidence_urls, uncertainty_note.
manual_seen=YES. Array fields are valid JSON arrays. No invented IDs.

## Authorized forward write path — VERIFIED

Forward staging writes are explicitly authorized on this research branch. Do NOT self-block merely because a staging JSON is new, existing, large, or semantically replaced.

A forward write is authorized when ALL are true:
1. branch is exactly `research/taxonomy-usability-audit`;
2. the worker writes only its own lane path under `docs/issue132/parallel/lane-N/staging/` or its own lane status file;
3. immutable checkpoints/corrections, other lanes, main, production, UserData, #64/#76/#118 are untouched.

Write protocol:
- EXISTING staging/status file: fetch that exact path immediately before write and use its current blob SHA with `update_file`.
- NEW staging/status file: use `create_file`.
- Full 25-window JSON creation/replacement is expected behavior and is NOT a safety blocker.
- After write, re-fetch the exact file and run the required exact tuple + 22-field gate.

Invalid blocker reasons:
- "staging generation/write blocked by safety check";
- "large write not allowed";
- "existing staging replacement is unsafe";
- "multiple 25-window writes in one run are unsafe";
when no actual GitHub operation has been attempted and failed.

Only classify TOOL_LIMIT/write blocker after an actual applicable GitHub operation fails. Record exact target path, NEW/EXISTING, branch, SHA when EXISTING, attempted operation, and exact returned error.
If contents `update_file` genuinely fails despite current SHA and correct branch, the worker may use the equivalent authorized Git object blob/tree/commit/ref path if available. Never redirect to main.

Verified capability on this branch already includes successful create/delete in the Issue132 parallel area and successful SHA-bound update of an existing staging file.

## Fixed run algorithm
1. Read own lane status. Determine forward next_new.
2. Set run_target_end=min(next_new+299,lane_end): exactly 12 consecutive 25-identity windows unless final partial.
3. Preload the authoritative source span for the whole run once. Fetch only the validated lane shard(s)+manifest(s) intersecting next_new..run_target_end (normally one or two <=300-row shards). Do not refetch a shard per window.
4. For each of the 12 windows:
   a. take the exact authoritative tuples (lane_local_index, review_seq, identity_key);
   b. finalize clear rows once; collect ambiguous rows and batch research where practical;
   c. genuine unresolved => hold at its exact original tuple; later rows never shift;
   d. pre-write exact tuple gate: every expected tuple exactly once; no gap/duplicate/extra; exact review_seq/key; finalized+holds=window size; parent/local constraints and 22-field structure valid;
   e. write NEW path with create, EXISTING with current SHA update;
   f. re-fetch the exact file and repeat the tuple/structure gate;
   g. if post-write gate fails, repair/delete that window before any later window and count zero progress until fixed;
   h. immediately continue. There is no continue/stop decision at a 25-row boundary.
5. After windows 4, 8, 12 perform due cumulative 100-row QA, then immediately continue if windows remain.

## 100-row QA
Re-review all high-risk rows in the completed block: RESEARCHED, MIXED, SEARCH_ORIENTED, SEMANTIC_UNRESOLVED, gap=YES, route2/3, body/theme, adult/sexual.
Also deterministic soft-risk sweep up to 15 ordinary CHECKED rows and at least 10 low-risk ordinary CHECKED rows.
If a systematic family error is found, expand that family only across current + immediately preceding 100 block unless broader drift evidence exists. Do not turn QA into a full second pass when clean.

## Responsibility split
Forward worker does NEW frontier only.
Do not read or repair historical invalid staging, old CI logs, quality_flags, coordinator history, old promotion-blocking holds, or Lane 3 historical 751–1050 remediation. Dedicated Repair tasks own those.
Do not poll CI during the 12-window loop unless an actual frozen/contract/write conflict appears.

## Stop
Terminal only:
- 300 NEW / 12 windows completed;
- lane complete;
- evidenced hard tool/contract/write blocker after applicable fallback;
- actual platform-forced interruption.
Never self-stop for checkpoint success, QA completion, elapsed effort, predicted limits, or report convenience.

Write lane status once at terminal/end boundary. Compact report only: start, end, NEW count, finalized, holds, next_new, blocker.

## Primary write transport — Git object protocol

All Issue132 writes use `docs/issue132/parallel/GIT_OBJECT_WRITE_PROTOCOL_V1.md` as the PRIMARY transport. Do not use contents `create_file/update_file` for normal Issue132 persistence. Use branch-head/tree -> create_blob -> create_tree -> create_commit -> re-fetch head -> update_ref(force=false), with retry on concurrent branch advance exactly as defined there. Contents API is fallback only when the Git-object path is unavailable.

A pre-write runtime safety refusal on contents API is not a blocker and must not stop/disable the task. Only an actually attempted Git-object path failure after the protocol's retries may become a write blocker.


## Compact staging v2 — REQUIRED FOR NEW WRITES

All NEW forward staging windows use `issue132-pass-a-staging-window-v2`. Existing v1 files remain valid and are not mass-rewritten. If an existing window is rebuilt for repair, write it back as v2.

Purpose: keep exact identity/classification quality while avoiding repeated publication of identity text and free-form semantic prose.

Window metadata remains:
- `schema_version`: `issue132-pass-a-staging-window-v2`
- `lane`
- `lane_local_start`
- `lane_local_end`
- frozen parent neutral/order SHA fields
- `rows`
- `holds`

Each finalized v2 row contains EXACTLY:
- `lane_local_index` integer
- `review_seq` integer
- `identity_sha256` = lowercase SHA256 hex of UTF-8 `identity_key`
- `discovery_mode`
- `routes`: ordered list of 0..3 objects, each exactly `{"id": ROUTE_ID, "strength": "CORE"|"SUPPORTING"}`
- `local_refinement_ids`: JSON array value, not a stringified array
- `body_site_ids`: JSON array value
- `theme_ids`: JSON array value
- `route_vocabulary_gap`: `YES` or `NO`
- `review_depth`: `CHECKED` or `RESEARCHED`
- `evidence_urls`: JSON array value

Do NOT persist these in v2 staging rows:
- `identity_key`
- `semantic_summary_ja`
- `route_*_reason_ja`
- `route_vocabulary_gap_note`
- `uncertainty_note`
- any other free-form prose

The validator binds `lane_local_index + review_seq + identity_sha256` back to the authoritative shard identity and deterministically reconstructs the required 22-column checkpoint row. Classification semantics are therefore still validated by the frozen validator.

Each v2 hold contains EXACTLY:
- `lane_local_index`
- `review_seq`
- `identity_sha256`
- `reason_code`
- `research_attempt_codes`

Allowed `reason_code`:
- `DIRECT_EVIDENCE_NOT_FOUND`
- `IDENTITY_AMBIGUOUS`
- `SEMANTIC_SCOPE_AMBIGUOUS`
- `ROUTE_AMBIGUOUS`
- `OTHER_UNRESOLVED`

Allowed research attempt codes:
- `DANBOORU_EXACT`
- `SAFEBOORU_EXACT`
- `OFFICIAL_SOURCE`
- `DIRECT_WEB_SOURCE`
- `OTHER_DIRECT_SOURCE`

Do not place tag names, semantic descriptions, or research prose in v2 holds. The exact slot is preserved by index/seq/hash.

Write preference for compact v2:
1. contents API first: NEW=`create_file`; EXISTING=fetch current blob SHA then `update_file`.
2. Git-object protocol only as fallback on a real contents write failure.
3. Never disable the automation for a write failure; persist `WRITE_RETRY_PENDING` behavior and retry next run.

