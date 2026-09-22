# Issue #132 — Codex full semantic review handoff

Status: **DRAFT / DO NOT RUN**

This handoff predates Phase 7 Luna calibration research and is not the final execution instruction.
Do not start the 31,003-row Codex run from this file.
It will be rewritten only after `PHASE7_LUNA_DECISION_CALIBRATION_RESEARCH.md` is finalized.

## Mission

Review **all 31,003 runtime ordinary-tag identities**, one identity at a time, for actual tag-discovery usability.

Do not use the machine audit to skip identities.

The machine-generated queue exists only to:
- present context;
- group similar concepts;
- assign deterministic shards;
- catch completeness errors.

The final semantic columns must be decided by Codex per identity.

## Read first

1. `docs/issue132/FULL_SEMANTIC_REVIEW_PROTOCOL.md`
2. `docs/issue132/CURRENT_RECOMMENDED_DIRECTION.md`
3. `docs/issue132/PHASE6_FULL_DISCOVERY_COVERAGE_AUDIT.md`
4. live Issue #132 body/latest comments
5. `docs/project/PERMANENT_RULES.md`

If these conflict, the Full Semantic Review Protocol and latest live Issue #132 checkpoint supersede older Phase 5/6 scope statements about reviewing only selected populations.

## Generate the queue

Run:

```bash
python scripts/issue132/full_discovery_coverage_audit.py \
  --root . \
  --out artifacts/issue132/full-discovery-audit
```

Use:

`artifacts/issue132/full-discovery-audit/codex_full_review_queue.csv`

Expected:
- identity rows: 31,003
- shard size: 200
- shards: R001..R156
- every semantic output field initially blank

Do not edit the generated queue in-place as the only copy.

For each shard, create a result file under:

`docs/issue132/full_review/shards/R###.csv`

## Required per-row work

For every owner identity:

1. Read canonical identity and available Japanese metadata.
2. Read current General/Special discovery metadata.
3. Understand what the tag actually means.
4. Decide whether the present search/browse path is good enough.
5. Consider whether another **existing** Unified route is a natural discovery entrance.
6. If meaning or route choice is not obvious, research it.
7. Fill every final review field.

Every output row must have:
- `manual_seen=YES`
- one valid `review_depth`
- a short Japanese semantic summary
- one current-discovery-fit verdict
- one final decision
- confidence
- evidence note
- review note

## Important

A machine `OK` label is not a final KEEP decision.

A regex match is not semantic evidence.

A shared family pattern does not permit bulk-copying a verdict to every row.

Similar rows may be reviewed together for consistency, but each row still needs an explicit independent judgment.

## Research depth

Use `CHECKED` when the meaning and route fit are genuinely obvious after reading the row and accepted repository metadata.

Use `RESEARCHED` whenever:
- meaning is unclear;
- proper noun/meme/domain term matters;
- a route change/addition/removal is proposed;
- accepted metadata disagrees;
- confidence would otherwise be below HIGH.

For a proposed discovery change, prefer direct Danbooru tag/wiki evidence when available. Use other authoritative sources when Danbooru does not explain the concept sufficiently.

## Decision bias

Prefer:
- KEEP over speculative improvement;
- SEARCH_ONLY over forced categorization;
- UNRESOLVED over a wrong route;
- one accurate secondary entrance over many weak entrances.

Do not try to maximize the number of changes.

## Work order

Follow the deterministic queue order.

The queue groups:
1. current review/conflict rows;
2. no-authority rows;
3. current multi-route rows;
4. route-specific lanes;
5. facet-only/other rows.

This order is for consistency only.

## Autonomous execution

Continue shard-by-shard without asking the user to type "continue".

After each shard:
1. validate exactly the assigned owner identities;
2. commit the shard result;
3. continue.

After every 10 shards:
1. rebuild aggregate progress;
2. confirm no missing/duplicate owner identities;
3. comment cumulative progress on Issue #132;
4. continue.

Stop only for:
- an actual authority contradiction that blocks safe review;
- unavailable required evidence/tool access;
- execution quota/resource exhaustion.

Do not stop merely because a batch finished.

## Aggregate validation

Create/update:

`docs/issue132/full_review/FULL_REVIEW_LEDGER.csv`

and:

`docs/issue132/full_review/FULL_REVIEW_SUMMARY.md`

The ledger must have one row per identity.

Final gates are defined in `FULL_SEMANTIC_REVIEW_PROTOCOL.md`.

## No production mutation

This is research only.

Do not change:
- main
- production catalog
- runtime
- UserData
- #64/#76/#118 authorities
- search ranking
- PromptToken
- Japanese overlay
- unrelated lanes

Do not merge or production-apply.

Return to DEV/AUDIT with:
- branch
- HEAD
- reviewed count
- shard range completed
- decision counts
- confidence counts
- RESEARCHED count
- missing/duplicate counts
- blockers
- next shard
