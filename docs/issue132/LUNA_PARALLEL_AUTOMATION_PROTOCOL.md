# Issue #132 — ChatGPT Automation parallel protocol

Date: 2026-09-23 JST
Status: **READY DESIGN / 3 WORKERS + 1 COORDINATOR**

## Purpose

Run the same frozen Pass-A semantic review through normal ChatGPT Automations without using ChatGPT Work.

This is an **operational parallelization only**.

It does not change:
- the 31,003-identity population;
- semantic rules;
- route/local/body/theme vocabulary;
- evidence rules;
- production ownership;
- Pass-B semantics.

## Lane assignment

Neutral input is already hash-shuffled.

Assign each identity mechanically:

```
lane = ((review_seq - 1) % 3) + 1
```

Therefore:

- Lane 1: 10,335 identities
- Lane 2: 10,334 identities
- Lane 3: 10,334 identities

This is not semantic sharding.

Do not regroup by route, sexual intent, tag family, or machine risk.

## Shared branch

All four automations use:

`research/taxonomy-usability-audit`

Workers write only their own lane files.

Coordinator writes only coordinator/global integration files.

Stagger schedules so workers normally do not write concurrently.

## Worker-owned files

Lane N owns only:

`docs/issue132/parallel/lane-N/pass_a_fragment.csv`

`docs/issue132/parallel/lane-N/status.json`

A worker must never edit another lane's files.

Each fragment:
- uses the exact 22-column Pass-A schema;
- contains only assigned identities;
- is an exact prefix of that lane's deterministic assignment;
- preserves global review_seq values.

Validator:

`scripts/issue132/validate_luna_lane.py`

## Worker execution

Each worker run:

1. read final semantic authorities;
2. verify current branch/frozen contract;
3. obtain/regenerate neutral input;
4. read its own fragment/status;
5. continue from the next assigned identity;
6. individually review identities under the same independent Pass-A rules;
7. save frequently;
8. validate its lane;
9. commit/push only its lane files;
10. continue within the same run while execution budget remains.

Target:
- normally advance at least 100 identities per run;
- save every 25–50 completed identities so work is not lost.

The target is operational, not a quality quota.

A worker may finish below 100 only for:
- actual execution/tool limit;
- contract drift;
- Git conflict/save failure;
- concrete semantic/tool failure that prevents safe continuation;
- remaining lane count below 100.

Do not stop merely because a checkpoint was created.

## Coordinator execution

Coordinator runs after the three staggered workers.

It reads all lane statuses and the previous coordinator state.

It must calculate per-lane:
- reviewed_count;
- delta since previous coordinator run;
- remaining_count;
- zero_progress_streak;
- latest lane file SHA/branch HEAD if available.

Coordinator owns:

`docs/issue132/parallel/coordinator_status.json`

`docs/issue132/parallel/merged_progress.json`

It may generate an incomplete merged snapshot for audit, but incomplete merge is not the final Pass-A authority.

Merge tool:

`scripts/issue132/merge_luna_parallel.py`

## Stall detection

A lane is `STALLED` when:

- incomplete; and
- reviewed_count increased by 0 across **two consecutive coordinator cycles**.

One zero-progress run is only a warning.

Reset the streak to zero immediately when progress resumes.

## Stall rescue

When a lane reaches STALLED:

1. verify its fragment still validates;
2. verify no file change occurred after the coordinator read;
3. coordinator may act as a temporary rescue worker for **that lane only**;
4. process the next assigned identities under the exact same semantic rules;
5. append only to that lane's exact prefix;
6. validate before saving;
7. limit rescue work to a small safe unit (normally up to 25 identities);
8. clear/reset stall streak after real progress.

If concurrent change is detected, abandon rescue and re-read next cycle.

Coordinator must never skip identities or reassign identities to a different lane.

This preserves deterministic ownership while allowing self-healing.

## Final merge

When all three lane statuses are complete:

1. run `merge_luna_parallel.py --require-complete`;
2. produce:
   `docs/issue132/full_review/pass_a_independent_discovery.csv`
3. run the normal complete Pass-A validator;
4. run the existing deterministic Pass B;
5. stop before Pass C/product approval.

The full merged ledger must contain exactly:
- 31,003 rows;
- 31,003 unique identities;
- no missing review_seq;
- no duplicates;
- no contract drift.

## Hard stops

Stop and report instead of guessing when:

- frozen semantic contract changed;
- branch authority is contradictory;
- lane fragment fails exact-prefix validation and cannot be mechanically repaired;
- GitHub save conflict cannot be safely reconciled;
- neutral input/contract SHA mismatch occurs.

Normal ambiguous tags are **not** a hard stop; use the normal RESEARCHED / unresolved rules.

## Runtime / production boundary

Parallel automation changes only research execution.

No merge to main.
No production apply.
No #64/#76/#118 mutation.
No new runtime semantic engine.
