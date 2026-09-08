# Issue #36 one-shot remaining UI-JA completion contract

## Goal
Finish the remaining UI-JA display/search-assistance coverage without returning intermediate batches to the user. Treat this as a bounded completion campaign, not another endless evidence campaign.

Authoritative Phase 0 baseline:
- measurable General/runtime proxy: 30,629 canonicals
- P0: 1,025
- P1: 4,910
- P2: 24,694

Reuse and deduplicate the already completed 556-row table at `translation_quarantine/r3_final_uija_completion_20260909/final_translation_table.csv`.

## User intent
Japanese here is human-facing UI display/search assistance. A concise label that lets the user understand the tag at a glance is sufficient. Perfect wording is not required.

Canonical English identity remains authoritative. This contract does not relax semantic, generation, recommendation, ranking, or co-occurrence data rules.

## Execution route
For every still-uncovered canonical, use this order:
1. Existing exact-canonical Japanese assets, existing search terms, or already accepted exact-canonical wording.
2. Existing deterministic lexical/compositional rules.
3. If those do not quickly produce a concise understandable label, generate a direct Japanese rendering and continue. Do not start another prolonged source chase for ordinary display wording.
4. Apply lightweight QA.
5. Route only genuinely ambiguous, meaning-changing, relation-heavy, symbol-like, or Danbooru-specific cases to bounded strict review.
6. If strict review still cannot establish a safe Japanese label, use explicit English canonical fallback and continue.

No row may remain pending only because exact external authority is unavailable for a display-only label.

## Lightweight acceptance
Accept when:
- a Japanese user can understand the intended tag at a glance;
- there is no obvious mistranslation or inversion;
- there is no material change in actor, target, location, direction, count, ownership, or relation;
- there is no material broadening/narrowing that would cause the wrong tag to be selected;
- wording is a concise label rather than explanatory prose;
- canonical English remains unchanged and authoritative.

Minor awkwardness and orthographic preference do not block completion.

## Strict-only triggers
Use strict review only for:
- Danbooru-specific nonliteral concepts;
- symbols/emoticons where Japanese wording may mislead;
- actor/target/relation/location/direction/count/ownership ambiguity;
- action-vs-state ambiguity;
- competing candidates with materially different meanings;
- known regression-style explanatory wording.

Strict review is bounded. If unresolved, use English fallback.

## Priority and scope
Recompute current coverage against the Phase 0 measurable universe and current branch artifacts before generation. Deduplicate the completed 556 rows.

Process in priority order:
1. remaining P0
2. remaining P1
3. remaining P2

Do not stop after P0 or P1 for user handback. Continue through the measurable universe in the same Codex run until every reachable row is terminal, unless a true repository/environment blocker prevents progress.

Allowed final states only:
- `JA_ACCEPT_EXISTING`
- `JA_ACCEPT_MACHINE`
- `JA_ACCEPT_STRICT`
- `ENGLISH_FALLBACK_EXCEPTION`

Generic `REVIEW`, `PENDING`, `NEEDS_USER`, or equivalent are forbidden in the final result.

## No user handback
Do not stop for small batches, wording questions, approval samples, or manual choices. Resolve ordinary wording autonomously. If a label cannot be safely chosen, use English fallback instead of waiting for user input.

## Boundaries
Do not modify:
- canonical English identities;
- Prompt syntax;
- co-occurrence data/counts;
- recommendation ranking/scoring/order;
- semantic-support relations/classes/slots;
- generation metadata;
- #32 verdicts;
- #35 UI code/tests;
- `CURRENT_DEV_TASK.md`;
- main;
- Stage10 production A/B state.

Until independent promotion audit, writes stay under `translation_quarantine/**` and focused tests only.

## Current-state recount
Before translation, create a deterministic report with:
- measurable universe size;
- already terminal/covered count;
- remaining P0/P1/P2 counts;
- overlap/dedup count with the completed 556-row table;
- exact input paths/hashes.

## Required outputs
Create a new quarantine run directory containing at least:
- `campaign_manifest.json`
- `coverage_recount.json`
- `source_candidate_ledger.jsonl`
- `lightweight_decisions.jsonl`
- `strict_decisions.jsonl`
- `fallback_exceptions.jsonl`
- `final_rows.jsonl`
- `final_translation_table.csv`
- `final_translation_table.md`
- `protected_boundary.json`
- `replay_verification.json`
- `FINAL_REPORT.md`

Final table columns should include:
- canonical
- display_ja
- search_ja
- priority_class
- final_state
- route
- reason
- risk_class

Include all measurable-universe rows, or provide an equivalent complete materialized table proving final coverage across the universe.

## Final report
Report:
- measurable universe count;
- already covered before this run;
- rows newly processed;
- P0/P1/P2 terminal counts;
- counts for each final state;
- generic REVIEW/PENDING count = 0;
- Japanese display final coverage count/percentage;
- Japanese search-assistance final coverage count/percentage;
- corrected obvious mistranslations;
- `production_modified: NO`;
- protected-boundary verdict;
- replay/reproducibility verdict;
- focused/full-test results with environment failures separated from assertion failures.

## Tests
Add focused tests for:
- completed 556 rows are reused/deduplicated;
- ordinary transparent tags accept existing wording;
- ordinary uncovered tags can pass direct rendering;
- obvious mistranslation/inversion is rejected;
- ambiguous relation-heavy rows cannot silently pass lightweight route;
- unresolved strict rows become English fallback, not generic REVIEW;
- all final rows are terminal;
- canonical English remains authoritative;
- protected/production files remain unchanged;
- deterministic replay.

If full pytest is blocked by the known Windows TEMP/ACL setup issue, record it separately and do not spend the campaign repairing the environment. Focused campaign tests must still pass.

## Stop condition
Stop only when:
- current coverage recount is complete;
- all reachable remaining P0/P1/P2 rows are processed;
- no generic REVIEW/PENDING remains;
- complete final table is produced;
- focused tests complete;
- replay/protected boundary checked;
- commit created and pushed;
- Issue #36 receives a completion checkpoint with commit SHA, counts, test results, and final table paths.

Do not merge to main and do not promote production data. Independent ChatGPT audit follows Codex completion.
