# Issue #36 post-#41 controlled bulk automation contract

Status: AUTHORIZED CANARY DESIGN / QUARANTINE ONLY
Owner: UI-JA DATA lane (#36)
Validated predecessor: Issue #41 `PASS_PILOT`
Base branch/head: `ui-ja/issue41-pilot` @ `1c5a2cba7f8a0c5cd7c15ad510317c75d07d8851`
Execution branch: `ui-ja/issue36-r3-bulk-canary`

## 1. Authority and purpose

Issue #41 proved the R3 safety model on a fresh100 + independent blind30:

- semantic false READY = 0
- search-scope false READY = 0
- silent #32 contradiction = 0
- deterministic three-way replay = PASS
- production modified = NO

This contract does **not** change R3 semantic rules. It exists only to convert the validated pilot machinery into a deterministic repeated quarantine-batch workflow and to prove that the orchestration itself is safe before the remaining P0 queue is processed automatically.

The intended long-run model remains:

`authorized queue -> deterministic batch selection -> evidence freeze -> unchanged R3 evaluator -> #32 controlled bridge -> verifier -> quarantine outputs -> REVIEW/CONTRADICTION stop paths -> later independent promotion audit`

## 2. Hard boundaries

Forbidden in this contract:

- production `data/**` writes
- production Japanese overlay promotion
- #32 verdict/candidate/generation-support writes
- #35 UI code/tests changes
- search-ranking/fuzzy/recommendation changes
- `docs/project/CURRENT_DEV_TASK.md` takeover
- main merge
- Stage10 production A/B
- weakening or bypassing R3 fail-closed rules
- silently converting REVIEW/CONTRADICTION to READY to improve throughput
- using Japanese wording as canonical semantic authority

All new outputs remain under `translation_quarantine/**`.

## 3. Required implementation — generic batch orchestration only

Add the smallest possible reusable batch layer around the already-validated R3 engine.

Preferred new files:

- `translation_quarantine/r3/r3_bulk_select.py`
- `translation_quarantine/r3/r3_bulk_run.py`
- `translation_quarantine/r3/r3_bulk_verify.py`
- focused tests under `tests/`

Do not fork or duplicate the semantic evaluator. Reuse the existing R3 functions/contracts. If a semantic behavior change appears necessary, STOP and report it as a separate rule-change/revalidation requirement rather than hiding it inside the bulk runner.

### Required runner properties

1. deterministic source-queue identity/hash
2. deterministic exclusion set
3. deterministic batch membership/order
4. resumable batch IDs
5. no canonical processed twice within the same bulk campaign
6. frozen evidence input per batch
7. same #32 controlled-bridge behavior as Issue #41
8. fail closed on missing/invalid bridge snapshot or evidence schema
9. semantic outputs independent of timestamps/filesystem paths
10. original == rerun1 == rerun2 verification for each completed batch
11. production/protected boundary check
12. machine-readable campaign ledger showing processed / READY / REVIEW / STALE_REVIEW / CONTRADICTION without promoting anything

## 4. Source pool and exclusions

Use the deterministic P0 queue from the frozen #36/R3 inputs.

Exclude at minimum:

- the original Phase1A 100 regression canonicals
- the Issue #41 fresh100 canonicals

Do not silently switch to a newly regenerated queue. Record the exact source file/content hash and the exact exclusion-set hash before selecting the canary.

If the current queue materially differs from the frozen source expected by the validated R3 baseline, STOP and report the difference before processing.

## 5. Evidence acquisition/freeze contract

Bulk orchestration may automate evidence acquisition, but evidence authority does not change.

Allowed approval-capable semantic evidence remains the R3 hierarchy:

- exact-canonical authoritative wiki/definition evidence
- trusted canonical/alias identity only for identity claims
- transparent LOW/MEDIUM composition only under the existing R3 rules
- #32 snapshot only as a consistency bridge

Existing Japanese overlay/search data is candidate wording evidence only.
Related/implication/co-occurrence data is context only.

For HIGH/CRITICAL without concrete exact-canonical scope evidence: REVIEW.

If live public evidence is acquired, freeze it into a batch evidence manifest before evaluation. Deterministic replay must consume only the frozen manifest and never re-fetch live pages.

Evidence acquisition failure is not permission to guess; it becomes REVIEW or a batch HOLD according to the existing engine contract.

## 6. Canary run

Before authorizing automatic processing of the remaining unseen P0 queue, run exactly one bounded canary campaign.

Canary size: **200 previously unseen P0 canonicals**, unless fewer than 200 eligible unseen rows exist.

Selection seed:

`UIJA-R3-BULK-CANARY-20260909-V1`

Stable key:

`sha256(seed + "\0" + canonical)` ascending, canonical ascending tie-breaker.

Do not tune membership manually after seeing results.

Record the natural effective-risk distribution. If the canary unexpectedly contains no rows from an applicable risk class that exists in the eligible pool, do not claim representativeness; report and stop for selection review.

Preferred output directory:

`translation_quarantine/r3_bulk_canary/`

At minimum persist:

- `campaign_manifest.json`
- `canary_selection.json`
- `evidence_manifest.jsonl`
- `rows.jsonl`
- `search_terms.jsonl`
- `bridge32.jsonl`
- `run_summary.json`
- `replay_verification.json`
- `masked_audit20_input.jsonl`
- `masked_audit20_key.json`

## 7. Canary independent audit20

The canary is the last additional blind safety sample before unattended/repeated P0 quarantine batches.

Build a deterministic masked sample of **20** from the canary, using effective-risk stratification and prioritizing READY rows because false READY is the safety target. Include available #32-overlap rows where they fit naturally.

Reviewer-visible input must contain no automation state, risk, reason code, key, prior verdict, or hidden scoring field.

Keep `masked_audit20_key.json` separate until reviewer judgements are frozen.

Gate:

- semantic false READY = 0
- search-scope false READY = 0
- silent #32 contradiction = 0
- original == rerun1 == rerun2 = PASS
- production modified = NO

REVIEW rate is not failure.

Any false READY requires reusable root-cause classification + pattern-wide revalidation. No one-row patching.

## 8. Stop point for this Codex task

Codex must stop after:

1. generic bulk layer implemented and focused tests pass
2. 200-row canary processed in quarantine
3. three-way deterministic replay passes
4. masked audit20 input + separate key are generated and leakage-checked
5. production/protected boundaries are confirmed unchanged
6. an execution report is committed and pushed

Codex must **not** self-grade the masked audit20 if it has access to the key or automation states.

After the independent audit20 is frozen and scored by a separate context, a PASS may authorize repeated automatic quarantine batches for the remaining unseen P0 queue. That later authorization still does not authorize production promotion.

## 9. Required completion report

Report/commit:

- branch + commit SHA
- changed files
- exact validated R3 base/head
- source queue hash + exclusion hash
- canary membership hash and row count
- effective-risk distribution
- evidence acquisition/freeze counts and failures
- READY / REVIEW / STALE_REVIEW / CONTRADICTION counts
- #32 AVAILABLE / NOT_REQUIRED / BLOCKED counts
- deterministic three-way replay result
- masked audit20 row count + leakage check
- production modified: NO
- remaining full P0 bulk processed: NO
- Stage10 production A/B started: NO
- any semantic-rule change required: YES/NO; if YES, STOP/HOLD instead of proceeding
