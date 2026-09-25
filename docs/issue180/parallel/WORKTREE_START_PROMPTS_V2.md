# Issue #180 — Authority-campaign Worktree prompts v2

v2 is the active execution model. v1 assignment/epoch prompts are historical.

## Forward N (N = 0..3)

Branch: `research/issue180-forward-N`

Read root AGENTS.md, live Issue #180 latest comment, `PARALLEL_EXECUTION_V2.md`, `PARALLEL_EXECUTION_V2.json`, `AUTHORITY_BATCH_SCHEMA_V2.md`, and v3 README.

Fetch canonical before selecting new work. Run full v3 and `build_parallel_campaigns_v2.py` when starting a new campaign wave. Process only Forward campaigns whose owner_slot=N.

Research by reusable authority, not by Character count. Family/roster/base authority must stay together. Check the actual page and exhaust all exact Issue #180 relations safely proved by that source. If the same page proves additional exact current Characters outside the starting campaign, include them in the same AUTHORITY_BATCH. Do not infer unlisted members or HOME.

Write only under `docs/issue180/parallel/proposals-v2/fwd-N/`. One checked source should normally produce one batch JSON, not one JSON per Character.

Canonical advancing while a real source is being reviewed does not invalidate positive evidence. Finish the source batch, push it, then refresh canonical/campaign queue before selecting the next campaign.

Use TERMINAL_BATCH only for a genuinely reviewed Forward residual and bind it to exact current unit_id + member_ids_sha256. Do not terminalize QA-owned policy/identity/structural/conflict buckets.

Commit/push coarse source batches and continue. Routine duplicates, regenerated campaigns, safe unresolved results and technical retries are not user blockers.

## QA / Integrator

Branch: `research/issue180-qa-integrator`

Read root AGENTS.md, live Issue #180 latest comment, v2 runbook/config/schema, v3 README, migration ledgers and current Research Units.

You are the only canonical writer.

First process QA-owned deterministic buckets in bulk. Rebuild v3 + authority campaigns. Fetch all Forward branches directly.

For each new AUTHORITY_BATCH, independently verify the source/claim and apply each exact relation against current canonical state. Accept valid still-useful relations, deduplicate already-covered relations, and reject obsolete/conflicting relations individually. Do not discard an otherwise valid source batch merely because canonical advanced after the worker researched it.

For TERMINAL_BATCH, require exact current unit_id + member fingerprint. Reject stale terminal conclusions and review the regenerated remainder separately.

Record QA decisions in `QA_REVIEW_LEDGER_V2.csv`. Rebuild immediately after accepted family/member/variant evidence that can reshape the graph. Direct-HOME-only batches may be accumulated into a coherent source wave before one rebuild.

After a canonical integration wave run full v3/tests/guards/#179 freshness, push QA, require green CI, then fast-forward the exact green QA HEAD to canonical. Continue until OPEN/PENDING=0. No force push, main merge, production apply, or #70/#179/#132 mutation.
