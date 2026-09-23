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

## 2. Current worker target

Current live target:

**300 newly reviewed identities per worker run**

A worker does not stop normally at 50, 100, 150, 200, or 250.

Those are persistence / QA milestones only.

Normal completion of one worker run is:

- 300 newly reviewed identities safely persisted;
- mandatory per-checkpoint second-pass review completed;
- mandatory final 300-row QA completed;
- repository checkpoint validation clean;
- then `TARGET_REACHED`.

If fewer than 300 are completed, the worker must record an explicit reason:

- `EXECUTION_LIMIT`
- `TOOL_LIMIT`
- `CONTRACT_DRIFT`
- `GIT_CONFLICT`
- `SEMANTIC_TOOL_BLOCKER`
- `REMAINING_LT_300`

Raw speed is not considered sufficient evidence of healthy progress.

---

## 3. Persistence unit

New checkpoints are normally:

**50 rows per immutable checkpoint**

Path:

`docs/issue132/parallel/lane-N/checkpoints/checkpoint_XXXXXX_XXXXXX.csv`

Existing checkpoints are preserved exactly.

Do not overwrite old checkpoint files.

Each checkpoint must:

- use the exact frozen 22-column Pass-A schema;
- preserve global `review_seq`;
- contain only the owning lane's deterministic next prefix;
- contain no duplicates or skipped identities;
- be structurally valid before it is written.

Checkpoint creation is persistence only and is never, by itself, a reason to stop the worker run.

---

## 4. Mandatory 50-row two-pass review

Every 50-row checkpoint now requires two semantic passes before save.

### Pass 1 — individual classification

Review all 50 identities individually under the frozen Pass-A rules.

Use `CHECKED` only when meaning is genuinely clear.

If meaning is ambiguous, proper-noun-dependent, niche, or otherwise unsafe to infer from the tag string alone:

- perform actual semantic research;
- use `RESEARCHED`;
- record evidence URLs actually used.

### Pass 2 — full 50-row re-read

Before writing the checkpoint, re-read **all 50 rows**.

For every row re-check:

1. Was the identity meaning understood, or was it guessed from the tag name?
2. Is the CORE route a realistic starting point for a user who does not already know the tag name?
3. Is any SUPPORTING route genuinely independently useful, rather than merely related?
4. Was a color/pattern modifier incorrectly promoted to `COLOR_PATTERN_SHAPE`?
5. Was object placement incorrectly promoted to `POSE_POSITION` without a useful posture/position concept?
6. Are local refinement IDs naturally applicable, or being forced because a parent route exists?
7. Are body-site facets missing where intrinsic?
8. Are theme facets missing where intrinsic?
9. Is the result useful for real image-generation discovery, including adult/sexual workflows?
10. Should a row marked `CHECKED` actually be `RESEARCHED`?
11. Are `SEARCH_ORIENTED`, `SEMANTIC_UNRESOLVED`, and `route_vocabulary_gap` mutually consistent?
12. Are RESEARCHED evidence URLs relevant and actually used?
13. Are uncertainty requirements satisfied?
14. Does the row serialize to the exact 22-column CSV contract?
15. Are JSON-valued fields syntactically valid?

Any suspicious row must be corrected or researched **before** checkpoint creation.

Do not rely on CI to discover obvious row-shift or malformed-field problems that can be detected before write.

---

## 5. Mandatory final 300-row QA

After the sixth 50-row checkpoint, but before `TARGET_REACHED`, the worker performs a final QA over the whole newly completed 300-row run.

Mandatory re-scan targets:

- all `MIXED`;
- all `SEARCH_ORIENTED`;
- all `SEMANTIC_UNRESOLVED`;
- all `route_vocabulary_gap=YES`;
- all `RESEARCHED`;
- every row with route_2 or route_3;
- every body-site facet;
- every theme facet;
- adult/sexual concepts;
- a spot-check of ordinary single-route `CHECKED` rows for systematic drift.

Final QA explicitly checks for:

- color-only SUPPORTING inflation;
- object-placement-as-pose inflation;
- weak or unnecessary secondary routes;
- forced local refinement;
- missing intrinsic body/theme facets;
- family inconsistency;
- weak evidence;
- malformed 22-column rows;
- systematic shortcuts caused by throughput pressure.

Run the repository checkpoint validator when available.

If QA or validator finds a problem, repair it before the run is marked `TARGET_REACHED`.

---

## 6. Quality-over-throughput rule

The 300-row target is an operational ceiling/goal, not a quality quota.

Do not:

- guess to reach 300;
- reduce research because the run is moving slowly;
- treat a short runtime as proof that more rows should automatically be added;
- mark a batch healthy merely because CI is structurally green.

If a concept is unclear, research it or use the frozen unresolved path.

The purpose of increasing the target is to use available execution capacity while preserving semantic quality, not to maximize raw row count.

---

## 7. Coordinator / watchdog current behavior

Coordinator still derives real progress from immutable checkpoints, not from stale status files alone.

Current expectations:

- worker target: 300 new identities/run;
- `delta < 300` without an allowed stop reason => `UNDERPERFORMING`;
- two incomplete cycles with `delta = 0` => `STALLED`;
- two incomplete cycles with `delta < 150` and no valid reason => `SLOW`.

Coordinator quality watchdog prioritizes newly added rows that are:

- MIXED;
- SEARCH_ORIENTED;
- SEMANTIC_UNRESOLVED;
- route-vocabulary gaps;
- RESEARCHED;
- multi-route;
- body/theme-faceted;
- adult/sexual;
- ambiguous/proper-noun concepts incorrectly left as CHECKED.

Raw throughput must not override semantic-quality warnings.

### Rescue

For a confirmed stalled/slow/underperforming lane, after confirming there is no concurrent checkpoint write, Coordinator may temporarily rescue that same lane.

Current rescue limit:

**up to 50 identities per affected lane per coordinator run**

Rescue work must use the same mandatory 50-row two-pass review.

No cross-lane reassignment is allowed.

---

## 8. Why the stronger QA was added

A 200-row Worker 1 run completed quickly enough that raw execution time was clearly not the main bottleneck.

That run successfully advanced Lane 1 from 25 to 225 reviewed identities, but CI detected malformed CSV rows for:

- `gameplay_mechanics`
- `trolley_problem`
- `endless_eight`

The semantic direction of those rows was retained after re-review, but the rows had an extra empty CSV field that shifted later columns and caused validator failures.

They were repaired and re-researched where appropriate.

The repair commit was:

`2387b0b7d6300bbdfdb186b1d9afac1a2175a5ef`

The post-repair Issue132 CI passed.

This demonstrated that simply lowering the row target would not guarantee better review.

The operational response is therefore:

- keep meaningful batch throughput;
- require a second semantic pass on every 50 rows;
- require explicit structure validation before save;
- require a final 300-row QA before normal completion.

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
