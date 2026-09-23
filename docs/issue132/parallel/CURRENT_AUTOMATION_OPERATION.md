# Issue #132 — Current ChatGPT Automation operation

Date: 2026-09-23 JST
Status: **ACTIVE / 3 WORKERS + 1 COORDINATOR**
Scope: **operational execution only**

This file records the current live automation operating method for Issue #132 Pass A.

It intentionally does **not** modify the frozen semantic contract.

The frozen authority remains:
- `docs/issue132/CURRENT_RECOMMENDED_DIRECTION.md`
- `docs/issue132/FULL_SEMANTIC_REVIEW_PROTOCOL.md`
- `docs/issue132/LUNA_NEUTRAL_INPUT_CONTRACT.md`
- `docs/issue132/LUNA_DISCOVERY_ROUTE_SEMANTIC_CONTRACT.md`
- `docs/issue132/LUNA_PASS_A_LEDGER_CONTRACT.md`
- `docs/issue132/LUNA_PARALLEL_AUTOMATION_PROTOCOL.md`
- `docs/issue132/parallel/pass_a_contract_manifest_v1.json`

Do not edit those frozen files merely to change worker throughput or QA cadence during Pass A.

---

## 1. Live execution model

Normal ChatGPT Automations execute the frozen Pass-A review as:

- Worker 1
- Worker 2
- Worker 3
- Coordinator / watchdog

Repository:
`takasago181/DanbooruTagTool`

Branch:
`research/taxonomy-usability-audit`

Lane assignment remains unchanged:

```
lane = ((review_seq - 1) % 3) + 1
```

Assigned counts remain:

- Lane 1: 10,335
- Lane 2: 10,334
- Lane 3: 10,334
- Total: 31,003

This is operational parallelization only, not semantic sharding.

---

## 2. Current worker ceiling

Current live ceiling:

**up to 300 newly reviewed identities per worker run**

300 is not a quota.

The worker should continue while execution budget and semantic quality permit, but validated smaller progress is acceptable and must be preserved.

If fewer than 300 are completed, the worker records one explicit reason:

- `EXECUTION_LIMIT`
- `TOOL_LIMIT`
- `CONTRACT_DRIFT`
- `GIT_CONFLICT`
- `SEMANTIC_TOOL_BLOCKER`
- `REMAINING_LT_300`

`TARGET_REACHED` is reserved for:
- exactly 300 newly reviewed identities in the run; or
- lane completion with fewer than 300 identities remaining.

Raw speed is not evidence of quality.

---

## 3. Persistence unit

New checkpoints are normally:

**25 rows per immutable checkpoint**

Path:

`docs/issue132/parallel/lane-N/checkpoints/checkpoint_XXXXXX_XXXXXX.csv`

Existing checkpoints remain immutable and are not rewritten merely to match the current 25-row cadence.

Each new checkpoint must:
- use the exact frozen 22-column Pass-A schema;
- preserve global `review_seq`;
- contain the owning lane's next deterministic exact-prefix rows;
- contain no duplicates or skips;
- pass the mandatory 25-row second review before save;
- be structurally valid before write.

A checkpoint is persistence only, not a reason to stop the run.

---

## 4. Mandatory 25-row two-pass review

Every new 25-row checkpoint requires two semantic passes.

### Pass 1 — individual classification

Review each of the 25 identities independently under the frozen Pass-A rules.

Use `CHECKED` only when meaning is genuinely clear.

For ambiguous, proper-noun-dependent, niche, meme/event, or otherwise unsafe-to-infer concepts:
- perform actual semantic research;
- use `RESEARCHED`;
- record the evidence URLs actually used.

### Pass 2 — full 25-row re-read

Before writing the checkpoint, re-read **all 25 rows** and explicitly re-check:

1. semantic meaning vs name-only guess;
2. CORE route as a realistic unknown-tag discovery entry;
3. weak or unnecessary SUPPORTING routes;
4. simple color/pattern modifier inflation;
5. object placement incorrectly promoted to POSE_POSITION;
6. local-refinement omission or forced fit;
7. intrinsic body-site facet omission;
8. intrinsic theme-facet omission;
9. usefulness for actual image generation, including adult/sexual workflows;
10. CHECKED rows that should be RESEARCHED;
11. SEARCH_ORIENTED / SEMANTIC_UNRESOLVED / route_vocabulary_gap consistency;
12. evidence relevance and uncertainty requirements;
13. exact 22-column CSV serialization;
14. valid JSON-valued fields.

Any suspicious row must be corrected or researched before the checkpoint is saved.

---

## 5. Mandatory 100-row cross-batch QA

After every four new 25-row checkpoints in the same run — **100 newly reviewed rows** — perform a cross-batch QA before continuing.

Re-scan all:
- `MIXED`;
- `SEARCH_ORIENTED`;
- `SEMANTIC_UNRESOLVED`;
- `route_vocabulary_gap=YES`;
- `RESEARCHED`;
- rows with route_2 or route_3;
- body-site facets;
- theme facets;
- adult/sexual concepts.

Also spot-check ordinary single-route `CHECKED` rows.

Look specifically for:
- family inconsistency;
- color-only SUPPORTING inflation;
- object-placement-as-pose inflation;
- forced local refinement;
- missing intrinsic body/theme facets;
- weak evidence;
- repeated shortcuts caused by throughput pressure.

Repair issues before proceeding into the next 100-row block.

A 300-row run therefore contains at most three 100-row QA blocks.

There is **no additional mandatory full 300-row re-read** after those checks. The purpose of this operating model is to preserve safely reviewed progress before execution limits erase the whole run.

---

## 6. Quality-over-throughput rule

300 is a ceiling, not a success quota.

Do not:
- guess to reach 300;
- reduce research to increase row count;
- discard safely reviewed 25/50/75/etc. rows merely because 300 cannot be reached;
- treat a short runtime or green structural CI as sufficient semantic proof.

A run that safely persists 25, 50, 75, 100, etc. reviewed identities and then records `EXECUTION_LIMIT` is valid progress.

---

## 7. Coordinator / watchdog current behavior

Coordinator derives progress from immutable checkpoints, not stale status files alone.

Current expectations:
- 300 is the worker ceiling;
- one incomplete cycle with `delta=0` => `WARNING`;
- two consecutive incomplete cycles with `delta=0` => `STALLED`;
- `delta<300` without an allowed stop reason => `UNDERPERFORMING`;
- validated smaller progress with `EXECUTION_LIMIT` / `TOOL_LIMIT` is not automatically failure;
- `TARGET_REACHED` is valid only for 300 rows or lane completion.

Coordinator quality review prioritizes:
- MIXED;
- SEARCH_ORIENTED;
- SEMANTIC_UNRESOLVED;
- route-vocabulary gaps;
- RESEARCHED;
- multi-route rows;
- body/theme facets;
- adult/sexual concepts;
- ambiguous/proper-noun concepts incorrectly left CHECKED.

### Rescue

Coordinator rescue is same-lane only and is now limited to:

**25 identities per affected lane per coordinator run**

The rescue checkpoint must itself pass the mandatory 25-row two-pass review.

No cross-lane reassignment is allowed.

---

## 8. Why the operating unit changed

A fast 200-row Worker 1 run showed that raw throughput was not the main quality signal; structural CSV errors still escaped the first pass.

The next experiment strengthened QA to 50-row two-pass review plus final 300-row QA.

That design proved too coarse for the Automation execution window:
- Worker 1 could not safely finish the next 50-row fully reviewed checkpoint and therefore added 0 rows;
- Worker 3 likewise stopped at 0 new rows rather than save an incompletely reviewed 50-row checkpoint.

The fail-closed behavior was correct, but the persistence unit was too large.

Current response:
- keep 300 only as a ceiling;
- reduce persistence/second-review unit to 25 rows;
- preserve every fully reviewed 25-row unit;
- perform stronger cross-batch semantic QA every 100 rows;
- avoid an extra full 300-row re-read that would recreate the same all-or-nothing execution problem.

This is intended to improve both semantic quality and forward progress.

---

## 8.5. Current integrity checkpoint — 2026-09-23

At the repository-wide routing sync, the valid persisted Pass-A prefix was:

- total: **475 / 31,003**
- Lane 1: **225**
- Lane 2: **150**
- Lane 3: **100**

Lane 2 checkpoint `000101_000150` contained 15 rows with the same extra-empty-column shift seen earlier in Lane 1. The repair was mechanical: remove the extra empty field and restore the frozen 22-column mapping without intentionally changing the semantic decisions.

Repair commit:

`7b50dc6fea17f324177eff01bedba2a717e6c15d`

After restoring the frozen CI compatibility marker in the semantic handoff, Issue132 Full Discovery Coverage Audit run `35879379345` passed with:

- reviewed total: **475**
- checkpoint validator error count: **0**
- Lane 1: 225
- Lane 2: 150
- Lane 3: 100

This reinforces the current rule: validate structure before save and do not treat fast row production as sufficient quality evidence.

---

## 9. Production boundary

This operational document does not authorize any production mutation.

Still prohibited during Pass A:

- merge to main;
- production apply;
- UserData changes;
- changing #64/#76/#118 authority;
- changing canonical/PromptToken identity;
- runtime LLM/embedding/live-web logic;
- converting Issue #132 into a second taxonomy authority.

The current task remains:

**complete the independent 31,003-identity Pass-A discovery audit safely, then generate deterministic Pass B, and stop before Pass C/product acceptance.**
