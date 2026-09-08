# Issue #36 — Autonomous evidence search until safe-or-park

Status: EXECUTION CONTRACT
Lane: UI-JA DATA / quarantine
Branch: `ui-ja/issue36-r3-bulk-canary`

## Goal
Process the remaining unresolved UI-JA translation rows autonomously until each row reaches one of two terminal quarantine states:

- `READY_FOR_WORDING_SEARCH_GATE` when required semantic evidence is sufficient under the unchanged R3 rules, or
- `REVIEW` when all approved evidence routes are exhausted, unavailable, contradictory, ambiguous, or insufficient.

Do not return to the user after every small batch. The user should receive only the final machine-solved / machine-unsolved remainder and durable evidence.

## Starting point
Use current branch state at or after commit `ab06d879ccd68f9a7118da1e31b7f195bd753714`.

Existing reusable mechanism:
- `translation_quarantine/r3/exact_semantic_evidence.py`
- `translation_quarantine/r3/run_exact_semantic_evidence.py`
- frozen-evidence replay, proposition extraction, validation, risk gate, protected snapshot checks

Current baseline from the first real run:
- 556 unresolved rows processed
- semantic gate: 67 READY / 489 REVIEW
- final translation READY: 0
- false READY: 0
- replay: PASS
- verifier: PASS
- production modified: NO

## Required autonomous route order
For every unresolved canonical, exhaust approved routes in this order unless a prior frozen route is already proven exhausted:

1. local exact assets already present in repository-visible quarantine evidence
2. exact Danbooru canonical source
3. additional allow-listed exact-canonical semantic sources implemented through source adapters
4. freeze raw evidence + provenance + content identity
5. deterministic proposition extraction
6. proposition validation
7. unchanged R3 risk gate
8. wording-evidence stage
9. minimal search-term evidence stage
10. unchanged final R3 gate

Do not re-fetch an evidence route that is already frozen and usable. Do not repeatedly retry a route already durably marked exhausted unless the source adapter/version or source revision materially changed.

## Source-adapter requirements
The mechanism must remain generic. New source routes must be implemented as explicit adapters or equivalent source modules, not one-off per-tag logic.

Each source result must record at minimum:
- canonical
- source/adapter id
- exact-canonical match state
- source URL or durable source identifier
- revision/update identity when available
- raw-response/content hash
- acquisition result/status
- frozen provenance
- exhaustion reason when not usable

No fuzzy page-title match may satisfy exact-canonical authority.

## Semantic authority rules
Never use model/Codex prior knowledge as semantic authority.

The following may be used only as context, wording hints, or risk signals, not as authority for canonical meaning:
- existing Japanese overlay
- previous translation proposals
- aliases
- co-occurrence/statistical relationships
- generation behavior
- Prompt/KNOWLEDGE material
- #32 generation/semantic verdicts beyond the existing read-only bridge contract

For HIGH / CRITICAL routes, retain the existing requirement for exact-canonical authority plus required proposition validation.

If actor / target / body-site / direction / count / ownership / relation / action-vs-state / canonical-width is ambiguous or unsupported when required, park `REVIEW`.

## Wording gate
A semantically validated row is not automatically final READY.

The wording stage must independently establish that `proposed_display_ja` is:
- semantically equivalent to the canonical scope
- concise and natural for Japanese UI
- not explanatory prose when a label is expected
- not narrower or broader than supported meaning

If equivalence/naturalness cannot be established from approved evidence, keep REVIEW.

`uncensored` remains a regression fixture: prior explanatory/unnatural wording must not be used as a teacher or silently re-promoted.

## Search-term gate
`proposed_search_ja` is reviewed independently from display wording.

A valid display label does not automatically approve a search synonym.
Search terms must not broaden to a different canonical meaning merely to improve recall.

If only display equivalence is established, display may be marked wording-ready while search remains parked. Final promotion readiness must preserve the display/search separation required by R3.

## Safe-or-park terminal behavior
For each row:

### SAFE
Only mark machine-resolved when every gate required for that row has durable evidence and the unchanged R3 gate passes.

### PARK
Mark REVIEW when:
- source routes are exhausted
- exact authority is unavailable where required
- proposition fields remain incomplete
- evidence conflicts
- semantic width remains uncertain
- wording remains explanatory/unnatural/overbroad/narrow
- search equivalence remains unsupported

False READY is more severe than parked REVIEW. Do not lower thresholds to reduce REVIEW count.

## Determinism / replay
Live acquisition and deterministic replay must remain separate.

- live acquisition may only write a new frozen quarantine snapshot
- replay must use frozen evidence only
- replay must not call network adapters
- at least two replay passes must reproduce the same decision artifacts/hashes
- source exhaustion ledger must also be replay-stable

## Required outputs
Create a new durable run directory under `translation_quarantine/**` containing at least:

- campaign manifest
- frozen evidence/provenance index or references
- source-route exhaustion ledger
- propositions
- validations
- risk gates
- wording decisions/evidence
- search-term decisions/evidence
- terminal state per canonical
- replay verification
- protected-boundary before/after evidence
- final report

Final report must include:
- starting unresolved count
- READY count
- REVIEW count
- CONTRADICTION count
- false READY count
- per-source acquired/usable/exhausted counts
- per-risk-class decision counts
- wording-ready vs search-ready counts
- final machine-unsolved remainder count
- top residual REVIEW reason distribution
- exact list or machine-readable file of remaining REVIEW canonicals
- replay verdict
- protected-boundary verdict
- production_modified: NO

## Tests required
Add/extend deterministic tests for at least:
- cached/frozen source is reused without live fetch
- exhausted route is not redundantly retried
- second source can resolve a row only through its own exact-canonical evidence
- title mismatch cannot satisfy authority
- HIGH/CRITICAL incomplete proposition stays REVIEW
- wording-safe but search-unsafe stays non-final/parked for search
- explanatory wording regression (`uncensored`) stays REVIEW
- contradiction stays CONTRADICTION/REVIEW and never READY
- two frozen replay passes are identical
- production/protected files remain unchanged

Run focused tests for the new mechanism and all feasible existing R3 tests. Record exact commands/results.

## Hard boundaries
- quarantine only until separate promotion audit
- no production `data/**` writes
- no production `data/runtime/japanese_overlay.json` writes
- no #32 writes; official v2 bridge remains read-only
- no #35 UI/code/test changes
- no `CURRENT_DEV_TASK.md` changes
- no main merge
- no Stage10 production A/B
- no recommendation/search-ranking semantic changes
- no weakening of R3 gates
- no new READY row may be used as a teacher for other rows in the same campaign

## Stop condition
Run autonomously until every selected unresolved row is terminal SAFE-or-PARK and all required replay/protected checks complete.

Then commit and push the complete branch result and STOP. Do not merge main and do not promote production Japanese data.

The next action is independent review from ChatGPT/AUDIT using the branch/commit artifacts; the user must not be required to paste Codex output if GitHub artifacts are available.
