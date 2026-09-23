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

Normal worker run reads only:

1. `WORKER_EXECUTION_CARD_V1.md`
2. frozen `pass_a_contract_manifest_v1.json`
3. `parallel_plan_v1.json`
4. its lane `status.json`
5. checkpoint filenames/latest exact prefix
6. only the neutral rows actually needed for the next work window

Full frozen semantic/handoff/protocol documents are reread only when:
- manifest/card mismatch;
- contract drift;
- instruction contradiction;
- a case cannot be resolved from the card + semantic research.

The latest successful Issue132 CI is allowed to carry the repeated proof that the frozen neutral population/SHA/order remains unchanged. Workers do not spend every run recomputing the full 31,003-row proof unless an actual drift signal exists.

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

Mandatory actual research if any material uncertainty exists, including:
- unfamiliar / transliterated / foreign / specialist terminology;
- proper noun, brand/model, event, meme, title, quote, franchise-specific reference;
- material parenthetical qualifier;
- polysemous common word;
- technical object whose exact definition changes route/refinement;
- cultural/historical reference;
- sexual/anatomical/fetish term where action vs position vs object vs role vs body/theme is not immediately certain;
- any internal reasoning equivalent to “probably”, “seems”, or “likely”;
- any semantic field that would otherwise be guessed from tag spelling.

Use `RESEARCHED` with evidence actually used.

If research still cannot establish the concept confidently, use `SEMANTIC_UNRESOLVED`; do not manufacture a confident browse route.

Batching several ambiguous identities into one research/search phase is allowed for tool efficiency, but every identity still receives an independent decision and evidence trail.

---

## 5. Persistence

New checkpoint:
**25 fully finalized rows**

Path:
`docs/issue132/parallel/lane-N/checkpoints/checkpoint_XXXXXX_XXXXXX.csv`

Before write:
- exact 22 columns;
- JSON arrays parse;
- only allowed IDs;
- SEARCH_ORIENTED / SEMANTIC_UNRESOLVED constraints valid;
- no duplicate/gap;
- exact lane-local deterministic prefix.

Existing checkpoint files are not overwritten.

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

Then deterministically spot-check ordinary single-route CHECKED rows:
- at least every fifth ordinary row;
- or 20 ordinary rows if available.

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

- batch searches for multiple ambiguous terms when practical;
- record per-row evidence actually used;
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
