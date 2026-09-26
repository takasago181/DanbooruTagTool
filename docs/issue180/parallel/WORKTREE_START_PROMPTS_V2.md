# Issue #180 — Codex-optimized Worktree prompts v2

v2 is active. The five pre-created #180 Worktrees use the #180 fast-path in root AGENTS.md.

## Forward N (N = 0..3)

Branch: `research/issue180-forward-N`

Read only:
- root `AGENTS.md` section 12;
- live Issue #180 latest comment;
- `AUTHORITY_BATCH_SCHEMA_V2.md`;
- `RESEARCH_STOP_PROTOCOL_V2.md`;
- current canonical lane packet `docs/issue180/parallel/dispatch/fwd-N.csv` (max 200 OPEN campaigns).

Run `git fetch origin --prune`, but do **not** merge or rebase canonical during routine research. Read the current dispatch with `git show origin/research/issue180-single-home-pilot:docs/issue180/parallel/dispatch/fwd-N.csv` or an equivalent read-only command.

Do not run full v3 and do not build campaigns.

Process `research_state=OPEN` first, then `OPEN_WITH_PROGRESS`. For progressed rows, read `prior_checked_routes` and do not repeat those routes. Prefer higher reusable-yield campaigns and any embedded `source_hint_urls` before new web search.

Research by reusable authority, not Character count. Check the actual allowed source and exhaust every exact Issue #180 relation safely proved by that source. Exact spillover relations from the same source may be included. Never infer unlisted members/HOME.

Follow the bounded search routes in `RESEARCH_STOP_PROTOCOL_V2.md`. If no safe positive relation is found within the allowed routes, write RESEARCH_OUTCOME with `checked_routes`. Use `outcome_scope=PARTIAL` for broad/multi-member campaigns unless the exact authority scope was genuinely exhausted; use `EXHAUSTIVE` only for a bounded campaign that was actually exhausted.

Write only under `docs/issue180/parallel/proposals-v2/fwd-N/`. One checked source normally becomes one AUTHORITY_BATCH. TERMINAL_BATCH is only for an exact whole current Research Unit satisfying the terminal contract.

Commit/push about 3–5 coherent source/outcome batches at a time. After a push, refresh the canonical lane packet before selecting the next batch. If the packet is exhausted, stop cleanly for QA to publish the next packet; do not build the full queue locally. Canonical advancement never invalidates already checked positive evidence.

Do not touch canonical ledgers, tracked dispatch, Source Review Ledger, QA ledger, #70/#179/#132, main or production.

## QA / Integrator

Branch: `research/issue180-qa-integrator`

Read:
- root `AGENTS.md` section 12;
- live Issue #180 latest comment;
- v2 runbook/config/schema;
- `SOURCE_REVIEW_LEDGER_V2.csv`;
- `QA_REVIEW_LEDGER_V2.csv`;
- v3 README/current migration and Research Unit state as needed.

You are the only canonical writer.

Run full v3 and build campaigns only on QA/canonical. Refresh tracked dispatch with:

```
python scripts/issue180/refresh_dispatch_snapshot_v2.py --write-tracked
```

Fetch all four Forward mailbox branches directly and skip proposal_ids already recorded in QA ledger.

For AUTHORITY_BATCH:
- verify the exact source/claim;
- reuse an ACCEPTED Source Review Ledger entry when URL + scope + mapping rule are unchanged;
- otherwise perform full source-level review and append/update Source Review Ledger;
- apply each exact relation against current canonical state;
- deduplicate covered relations and isolate conflicts/obsolete rows rather than discarding a good source batch.

For RESEARCH_OUTCOME, first verify current campaign_key + fingerprint. Record PARTIAL as `ACCEPT_PROGRESS` with the checked routes copied into `research_routes_json`; it remains open and future dispatch must carry those routes. Record `ACCEPT_OUTCOME` only for independently verified EXHAUSTIVE scope. It is accounting, not evidence. For TERMINAL_BATCH, require exact current unit fingerprint.

After an integration wave:
1. run full v3;
2. build campaigns;
3. refresh tracked dispatch;
4. run tests/guards/#179 freshness;
5. push QA;
6. require green full-v3 CI, including dispatch freshness;
7. fast-forward the exact green QA HEAD to canonical.

No force push, main merge, production apply, or protected #70/#179/#132 mutation.
