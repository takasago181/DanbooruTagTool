# Issue #132 — Current ChatGPT Automation operation

Date: 2026-09-24 JST
Status: **ACTIVE / ACCURACY-PRESERVING FAST PATH**
Scope: **operational execution only**

This file records the live execution method for Pass A. It does not change the frozen semantic contract.

Frozen authority remains the files pinned by:
`docs/issue132/parallel/pass_a_contract_manifest_v1.json`

Normal worker execution now uses the compact operational cache:
`docs/issue132/parallel/WORKER_EXECUTION_CARD_V1.md`

If the compact card/manifest conflicts with a frozen file, the frozen file wins and the worker stops for reconciliation.

---

## 1. Execution model

- 3 normal ChatGPT Automation workers + 1 coordinator
- branch: `research/taxonomy-usability-audit`
- lane rule: `((review_seq - 1) % 3) + 1`
- assigned counts: Lane1 10,335 / Lane2 10,334 / Lane3 10,334
- semantic sharding: **false**
- worker ceiling: **300 new identities/run**
- persistence checkpoint: **25 completed rows**
- cumulative QA boundary: **every lane-local 100 rows**

300 is a ceiling, not a quality quota.

---

## 2. Why the previous method was inefficient

Observed Worker 2 comparison:
- earlier operation: about 100 rows in roughly 2.5 minutes;
- later 25-row two-pass operation: only 25 rows before self-declared EXECUTION_LIMIT.

The later batch was not obviously four times harder. The operating prompt itself had accumulated large fixed overhead:

- about 60k characters of frozen/handoff/operation documents reread every run;
- full neutral verification/retrieval work;
- classify 25 rows, then reread the same 25 rows from scratch;
- checkpoint write;
- frequent status write;
- repeated CI/status checking;
- permission to self-stop when the worker merely estimated that time might become short.

This made operational caution consume semantic-review capacity.

The solution is **not** to relax semantics. It is to remove redundant work and make ambiguity handling stricter at the exact point each row is finalized.

---

## 3. Compact preflight

Normal worker run first performs one metadata/directory read and verifies the pinned blob SHAs for:
1. `WORKER_EXECUTION_CARD_V1.md`
2. frozen `pass_a_contract_manifest_v1.json`
3. `parallel_plan_v1.json`

If the pinned SHAs match, their bodies are **not reread**. The worker then reads only:
4. its lane `status.json`
5. checkpoint filenames/latest exact prefix
6. only the neutral rows actually needed for the next work window

Full frozen semantic/handoff/protocol documents are reread only when:
- manifest/card mismatch;
- contract drift;
- instruction contradiction;
- a case cannot be resolved from the card + semantic research.

The latest successful Issue132 CI is allowed to carry the repeated proof that the frozen neutral population/SHA/order remains unchanged. Workers do not spend every run recomputing the full 31,003-row proof unless an actual drift signal exists.

### Stable neutral acquisition (mandatory)

Semantic authority remains the frozen neutral input:

`docs/issue132/parallel/input/luna_neutral_review_input_v2.csv`

with manifest:

`docs/issue132/parallel/input/luna_neutral_review_input_v2.manifest.json`

Expected invariants:

- rows: `31,003`
- neutral CSV SHA-256: `ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d`
- identity-order SHA-256: `f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b`

Workers MUST NOT depend on fetching the 31,003-row file directly. The primary operational input is the deterministic lane-local shard set:

`docs/issue132/parallel/input-shards/lane-N/shard_XXXXXX_YYYYYY.csv`

Each shard contains at most 300 lane-local rows and has a sibling `.manifest.json` binding it to:
- lane/local start and end;
- exact shard CSV SHA-256;
- shard identity-order SHA-256;
- parent neutral SHA-256;
- parent identity-order SHA-256;
- parent population 31,003.

The shard set is generated only by `scripts/issue132/build_worker_neutral_shards.py` from the frozen neutral authority and validated by `scripts/issue132/validate_worker_neutral_shards.py`. The full-discovery CI publishes the generated shard set to the research branch only after those checks pass.

For lane-local next index `k`, compute `start = floor((k-1)/300)*300+1` and use exactly the shard whose range contains `k`. Read that small shard plus its sidecar manifest only. Do not read, materialize, or semantically ingest all 31,003 neutral rows during normal worker execution.

Fallback order:
1. primary: validated lane-local tracked shard;
2. if shard is missing/invalid, use the tracked full neutral only when the execution environment can actually access it safely;
3. otherwise discover the latest current Issue132 full-discovery run, list artifacts, require artifact name `issue132-full-discovery-audit` and `expired=false`, then use the returned current artifact ID; the backup artifact now includes `docs/issue132/parallel/input-shards`, so prefer the exact required small shard from that package before attempting the monolithic neutral;
4. if an authorized environment can regenerate from tracked authority, run `scripts/issue132/build_luna_neutral_input.py`, require the exact frozen parent SHA/order, then regenerate the shard with `build_worker_neutral_shards.py`;
5. only if every authorized path is unavailable or fails invariant validation may neutral acquisition be treated as a concrete blocker.

A worker-side inability to fetch the monolithic neutral file is NOT a blocker when the required validated shard exists. Never use a cached temporary artifact download URL as persistent state. Never treat a bare artifact-API 404 as sufficient stop evidence.

---

## 4. Accuracy-preserving per-row finalization

The mandatory full 25-row second reread is removed.

Instead, each identity is finalized once, **before moving to the next identity**.

For every row the worker must establish:

1. exact concept meaning;
2. correct discovery mode;
3. strongest realistic unknown-tag CORE route;
4. whether any second route is independently useful rather than merely related;
5. natural local refinement only;
6. intrinsic body/theme facets only;
7. no field is being inferred from spelling alone;
8. exact 22-column structural validity.

A weak provisional row is not accepted with the intention of fixing it later.

### Ambiguity gate — stricter than before

`CHECKED` is only for genuinely clear ordinary visual concepts.

Mandatory actual research if material uncertainty exists, including:
- unfamiliar / specialist / polysemous terminology;
- obscure proper noun, brand/model, event, meme, title, quote, franchise-specific reference **when the exact referent/scope is not already clear or changes classification**;
- material parenthetical qualifier;
- technical object whose exact definition changes route/refinement;
- cultural/historical reference needed to classify the tag;
- sexual/anatomical/fetish term where action vs position vs object vs role vs body/theme is not immediately certain;
- any internal reasoning equivalent to “probably”, “seems”, or “likely”;
- any semantic field that would otherwise be guessed from tag spelling.

A proper noun or compound tag alone is not a reason to research. If the meaning and classification are genuinely clear, `CHECKED` is correct.

Use `RESEARCHED` with evidence actually used.

If research still cannot establish the concept confidently, use `SEMANTIC_UNRESOLVED`; do not manufacture a confident browse route.

Batch roughly 5–10 independent ambiguous identities per research/search call when practical, but every identity still receives an independent decision and evidence trail.

Evidence specificity:
1. prefer exact Danbooru/Safebooru tag wiki or direct tag evidence;
2. then official source;
3. then a strong reference that directly names/defines the target.

Generic category pages, unrelated wiki pages, model/LoRA-sharing pages, generic image/model sites, or a single example post are not acceptable default semantic authority. If the meaning is already clear, use `CHECKED` rather than manufacturing weak `RESEARCHED` evidence. If direct evidence remains insufficient, use `SEMANTIC_UNRESOLVED`.

---

## 5. Persistence

New checkpoint:
**25 fully finalized rows**

Path:
`docs/issue132/parallel/lane-N/checkpoints/checkpoint_XXXXXX_XXXXXX.csv`

Before write:
- build each row as an ordered 22-value structure;
- serialize with a real CSV writer; never hand-count commas;
- parse the serialized CSV back programmatically;
- exact 22 columns/header;
- JSON arrays parse;
- only allowed IDs;
- SEARCH_ORIENTED / SEMANTIC_UNRESOLVED constraints valid;
- no duplicate/gap;
- exact lane-local deterministic prefix.

Existing checkpoint files are not overwritten.

### Immutable checkpoint correction overlay

If cumulative QA discovers a concrete defect in an already-committed checkpoint, NEVER overwrite that checkpoint and NEVER stop merely because the checkpoint is immutable.

Create a new immutable correction record under:

`docs/issue132/parallel/lane-N/corrections/correction_RRRRRR_<slug>.json`

where `RRRRRR` is the global `review_seq`.

Schema: `issue132-pass-a-correction-v1`

Required fields:
- `lane`
- `lane_local_index`
- `review_seq`
- `identity_key`
- `source_checkpoint`
- `qa_boundary`
- `reason`
- `expected_before` mapping of corrected field(s) to exact raw checkpoint string value(s)
- `patch` mapping of corrected field(s) to complete replacement string value(s)

Rules:
- correction files are additive/immutable; checkpoints remain untouched;
- `review_seq` and `identity_key` cannot be patched;
- a correction must bind to the exact original checkpoint value via `expected_before`;
- after creating a correction, run/allow `validate_parallel_effective.py`; it first runs the frozen checkpoint validator and then validates the effective row after overlay;
- final parallel merge applies the same correction overlay before full Pass-A validation;
- discovering and recording a valid correction is NOT a run termination condition: continue to the next identity after the correction is persisted/validated;
- if the semantic fix itself is uncertain, record a quality flag for coordinator review rather than inventing a patch, but the mere existence of the flag still does not stop processing unrelated next identities.

The correction overlay is an audit-preserving semantic amendment layer, not a rewrite of historical checkpoint evidence.

After a valid 25-row save, immediately continue. The checkpoint is persistence, not a stop signal.

### Status writes

Do **not** update status after every checkpoint.

Update status:
- at run end;
- at lane completion;
- or after a cumulative 100-row QA boundary.

Coordinator derives actual counts from checkpoints, so stale status between these points is recoverable.

### CI polling

Do not wait for CI after every checkpoint.

Check CI:
- at run end;
- when a failure signal appears;
- or when contract/prefix integrity is in doubt.

---

## 6. 100-row semantic QA

QA is aligned to cumulative lane-local 100-row blocks, not to one automation run.

When a lane reaches 100, 200, 300, ... reviewed rows, audit the completed 100-row block before continuing.

Re-review **all high-risk rows**:
- RESEARCHED
- MIXED
- SEARCH_ORIENTED
- SEMANTIC_UNRESOLVED
- route_vocabulary_gap=YES
- route_2 / route_3
- body-site facets
- theme facets
- adult/sexual concepts

Then spot-check about 10% of ordinary single-route CHECKED rows, with a minimum of 10 when available.

This preserves protection against systematic drift without rereading every obvious row twice.

If repeated inconsistency is found, expand the review scope for that family/block.

---

## 7. Anti-overclassification remains strict

Do not add a route because it is merely true or word-related.

In particular:
- color + target is not automatically COLOR_PATTERN_SHAPE;
- object placement is not automatically POSE_POSITION;
- an action is not automatically POSE_POSITION unless positional geometry is independently useful;
- object/fixture is not automatically SCENE_BACKGROUND;
- sexual content is not CONTENT_RATING;
- local refinement is optional and must not be forced;
- body/theme facets must be intrinsic.

Prefer one strong CORE over weak route inflation.

---

## 8. Tool-efficiency rules

- batch roughly 5–10 ambiguous searches when practical;
- record per-row evidence actually used and require it to directly support the asserted identity/scope;
- do not research obvious ordinary visual concepts merely for formality;
- do not reread ~60k characters of frozen docs every normal run;
- do not re-prove the entire neutral corpus when successful CI already proves the same frozen hash/order;
- fetch only the next needed neutral range when the connector supports it;
- do not poll CI/status between every 25-row save;
- checkpoint union is the progress authority.

The model's reasoning budget should be spent on semantic uncertainty, not repeated administrative verification.

---

## 9. Stop rule

Continue after each validated 25-row checkpoint.

Do **not** self-stop because the worker predicts that time may become low.

`EXECUTION_LIMIT` is valid only when an actual execution limit/interruption occurs.

Other valid short-run reasons:
- `TOOL_LIMIT`
- `CONTRACT_DRIFT`
- `GIT_CONFLICT`
- `SEMANTIC_TOOL_BLOCKER`
- `REMAINING_LT_300`

`TARGET_REACHED` only:
- delta = 300; or
- lane completed with fewer remaining.

If execution is forcibly interrupted after a checkpoint, persisted 25-row units survive.

---

## 10. Coordinator

Coordinator:
- derives counts from immutable checkpoints;
- treats anticipated-time EXECUTION_LIMIT as invalid;
- watches for missing 100-row QA;
- audits high-risk rows and deterministic CHECKED samples;
- flags semantic drift even when structural CI is green;
- rescue is same-lane only, max 25 rows;
- uses the same ambiguity/research gate.

---

## 11. Production boundary

Pass A still does not authorize:
- merge to main;
- production apply;
- UserData changes;
- #64/#76/#118 authority rewrite;
- canonical/PromptToken changes;
- runtime LLM/embedding/live-web inference;
- a second taxonomy authority.

Mission remains:
**complete the independent 31,003-identity Pass-A review, generate deterministic Pass B, and stop before Pass C/product acceptance.**
