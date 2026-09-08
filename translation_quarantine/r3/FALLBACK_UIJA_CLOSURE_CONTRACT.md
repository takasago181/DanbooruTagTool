# Issue #36 fallback UI-JA closure contract

Status: ACTIVE fallback-closure handoff
Branch: `ui-ja/issue36-machine-convergence`
Start from current branch HEAD after the one-shot campaign.

## Goal
Close the remaining `ENGLISH_FALLBACK_EXCEPTION` rows from the one-shot UI-JA campaign without returning small batches to the user. The current measurable universe is 30,629 rows and the one-shot report records 8,048 English fallbacks.

## Product intent
This lane is display/search assistance only. Canonical English remains authoritative. Prompt syntax, cooccurrence data, recommendation logic, semantic-support relations, generation metadata, model behavior and ranking are out of scope.

Target quality is glanceable Japanese for UI display. Perfect literary wording is not required. Minor awkwardness is acceptable. Material mistranslation, inversion, semantic broadening/narrowing, added actor/target/relation/body-site/direction/count/action-state, or nonsense is not acceptable.

## Execution policy
Process all current English-fallback rows autonomously in one run.

For each fallback canonical, use this bounded route:
1. Reuse exact existing Japanese assets/search terms/dictionaries when they clearly match the same canonical meaning.
2. If unresolved, generate a concise direct Japanese display label from the canonical. Deterministic lexical composition or machine translation is allowed and expected.
3. Run a lightweight safety audit. Transparent ordinary labels should pass here.
4. Route only genuinely ambiguous, nonliteral, Danbooru-specific, relation/count/direction/action-state, or otherwise materially risky rows to bounded strict review.
5. If strict review still cannot produce a safe concise Japanese label, retain English fallback explicitly. Do not invent explanatory prose merely to eliminate fallback.

Do not stop for small-batch approval. Do not ask the user to adjudicate individual rows during the run.

## Important implementation note
The previous one-shot report claimed `fallback_exceptions.jsonl` but that file was absent from commit `ec928afb98ced272e59f753f11732aab9d75c75e`. This closure run must produce an actual committed machine-readable fallback ledger and validate its existence/count against the final summary.

## Required terminal states
Every input fallback row must end in exactly one terminal state such as:
- `JA_ACCEPT_MACHINE`
- `JA_ACCEPT_STRICT`
- `ENGLISH_FALLBACK_EXCEPTION`

Generic `REVIEW` / `PENDING` must be 0.

## Required artifacts
Create a new quarantine run directory containing at least:
- source fallback ledger with exact input count
- candidate/provenance ledger
- lightweight audit decisions
- strict-review decisions
- final rows for all processed fallbacks
- actual `fallback_exceptions.jsonl` for any residual English rows
- final merged 30,629-row translation table
- coverage recount before/after
- replay/reproducibility evidence
- protected-boundary evidence
- final report and run summary

The summary must report:
- input fallback count
- machine accepted count
- strict accepted count
- residual English fallback count
- generic review/pending count
- final Japanese display coverage count/rate over 30,629
- final Japanese search coverage count/rate over 30,629
- obvious mistranslation corrections count/list
- production_modified: NO
- replay verdict
- protected-boundary verdict
- test results
- exact path of committed fallback ledger

## Tests
Add/run focused tests covering:
- transparent fallback -> Japanese accepted
- ambiguous/risky fallback does not bypass strict route
- obvious mistranslation/inversion rejected
- canonical authority preserved
- residual English fallback remains explicit and traceable
- fallback ledger exists and count matches summary
- final merged table remains exactly 30,629 unique canonicals
- protected/production files unchanged

If full pytest is blocked by the known Windows TEMP ACL setup errors, separate environment setup failures from product assertion failures and do not spend unbounded time repairing the environment.

## Hard boundaries
No edits to production `data/**`, #32 validation data, #35 UI code/tests, `CURRENT_DEV_TASK.md`, main, or Stage10 production A/B. Do not merge main or promote production in this run.

## Stop condition
Only stop after all 8,048 current fallback rows are terminal, artifacts/tests/replay/protected-boundary checks are complete, the branch is committed/pushed, and Issue #36 receives one completion checkpoint with branch, commit SHA, counts, tests, and artifact paths.
