# Codex Luna request — Issue #180 full autonomous completion

Work only on repository `takasago181/DanbooruTagTool`, branch `research/issue180-single-home-pilot`.

Preflight in this order:

1. Issue #180 body/current state
2. `docs/issue180/autonomous/AUTONOMOUS_COMPLETION_RUNBOOK_V2.md`
3. `docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json`
4. `docs/issue180/AUTHORITY_POLICY_V1.md`
5. `docs/issue180/autonomous/decisions/README.md`
6. `docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv`
7. current v2 scripts/workflow

The v2 foundation is already implemented and CI-validated.

If `docs/issue180/autonomous/CODEX_EXECUTION_BASE_V2.json` exists, the harness is frozen. From that point onward, commit only new `docs/issue180/autonomous/decisions/*.csv` decision shards. Do not modify scripts, policy, workflow, runbook, compatibility ledger, or the base decision CSV to make a gate pass. If a genuine harness defect blocks execution after freeze, report the blocker instead of weakening the gate.

At the start of the task run:

`python scripts/issue180/run_autonomous_v2.py`

After authority-decision batches, use:

`python scripts/issue180/run_autonomous_v2.py --recompile`

Do not spend context reconstructing the historical script order.

Your main job is to complete as much safe authority research as possible by writing coarse decision shards under `docs/issue180/autonomous/decisions/*.csv` and repeatedly recompiling the deterministic master. Use separate large family/variant/roster/exception shards rather than one giant file. The compatibility `AUTHORITY_DECISIONS_V2.csv` is still read but need not be the main target.

Use the generated v2 work queues. Process reusable family authority before individual rows. There are 16,787 unqualified rows, but 16,743 already have a support-only discovery hint and only 44 have no hint. Do not perform 16,787 independent searches. Prioritize the 46 mandatory high-yield DISCOVERY_GROUP roster reviews (50+ rows per group), then use DIRECT_CHARACTER decisions for roster members actually proven. Also process the mandatory ready VARIANT_PATTERN groups (5+ rows) as group-level official-pattern checks, using explicit VARIANT_CHARACTER decisions for proven members. Use old relations/co-occurrence only as discovery hints, never as HOME authority.

Be productive rather than maximally conservative: clean IP qualifier families may be bulk-confirmed after one sound family-level validation; do not require one official page per Character. At the same time, ambiguous/broad/mixed families must not be guessed.

For every PASS decision, provide grounded evidence: either an http(s) evidence_url, or an evidence_claim of `REPO:<existing repository path>`. Internal REPO paths are existence-checked. Do not use free-form unsupported claims as PASS evidence.

Do not FAMILY_QUALIFIER-confirm collaboration/project families such as `project_voltage`. Follow existing canonical-root policy already encoded by the foundation instead of reverting Fate/Pokémon/Splatoon subworks to title-by-title HOME.

For difficult cases, use UNRESOLVED or NEEDS_HIGHER_REASONING and continue all other independent work. Do not stop the whole task for Piapro/Miku, umbrella franchises, or a small number of hard cases.

Do not bloat decision shards with one UNRESOLVED row for every untouched Character. The generated master already keeps untouched rows unresolved with a reason. Persist only meaningful reviewed decisions/escalations and safe PASS authority.

Do not repeatedly ask the user to continue.

Keep main, production, accepted Issue #70 source, #179 branch, and Artist untouched.

Run the full Issue #180 workflow at the end. Fix ordinary CI/code/schema errors yourself and rerun.

Before claiming completion, run:

`python scripts/issue180/check_autonomous_completion_readiness_v2.py --final`

If this reports `issue179_refresh_required_before_freeze=true`, include that fact in the final report. Do not stop the autonomous pass only because #179 advanced after the frozen handoff; live #179 synchronization is mandatory later before user freeze/promotion.

Do not report completion if this final readiness gate fails. It also requires the high-yield unqualified discovery groups, high-yield ready variant patterns, requeued weak legacy direct rows, #179 officiality rows, and mandatory family lanes to have been resolved or explicitly reviewed/deferred. Explicitly researched UNRESOLVED / NEEDS_HIGHER_REASONING cases may remain deferred; untouched mandatory fast/officiality/direct-roster work may not.

Stop only after you have exhausted the safe work available in the generated queues and produced the full 35,890-row v2 review artifact.

Final report must include:

- branch and final HEAD
- HOME_CONFIRMED / HOME_UNRESOLVED / NOT_OFFICIAL_CHARACTER
- authority scope/type counts
- unresolved reason counts
- remaining family / variant / unqualified counts
- NEEDS_HIGHER_REASONING count
- conflicts and missing-root counts
- CI result
- confirmation that main/production/accepted source were not changed
- path to the 35,890-row user review artifact

Do not merge or production-apply.
