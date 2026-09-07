# Codex Request — Stage8C Finalization Only

Work in canonical repository:
`C:\Codex\DanbooruTagTool`

This task is intentionally narrow. Do not redo earlier audits and do not begin Stage9 implementation.

## Fixed accepted state

- Pilot001 = ACCEPTED
- Exit Pilot = PASS
- Pilot003 = unnecessary
- UNREVIEWED remainder is not a Stage8C extension reason
- coverage/relation count is not a success metric
- NO_SUGGESTION / UNRESOLVED / member non-application / NO_COMMON_RULE / Special-only are permitted normal results
- Stage9 is the next stage after Stage8C FINAL

Use `EXIT_PILOT_PASS.zip` only to synchronize/confirm the Exit Pilot state if it is not already present in the canonical repo. Do not alter its fixed 12-Special selection or semantics merely to make tests pass.

## Required final checks — run once

1. Run the complete repository test suite:
   `python -m pytest -q -p no:cacheprovider`

2. Re-run the canonical Stage6 parity validation using the repository's existing Stage6 parity/audit procedure and artifacts. Do not invent a replacement metric. Confirm the historical Stage6 protected evidence remains reproducible and unchanged.

3. Confirm no regression in:
   - protected hashes
   - Ruleset2 authority
   - source ID + Tag identity
   - Stage8B runtime behavior/invariants
   - deterministic build evidence relevant to Stage8C

## PASS action

If all required checks PASS:

- Mark Stage8C = FINAL.
- Record Pilot001 = ACCEPTED.
- Record Exit Pilot = PASS.
- Record Pilot003 = NOT REQUIRED.
- Record that UNREVIEWED remainder is not an extension criterion.
- Record that coverage/relation count is not a success metric.
- Record NO_SUGGESTION / UNRESOLVED / member non-application / NO_COMMON_RULE / Special-only as valid normal results.
- Set next stage = Stage9.
- Keep Stage9 implementation = NOT STARTED.
- Update the canonical handoff and return `CHATGPT_HANDOFF.zip` containing the final test/parity evidence and changed handoff/report files.

## FAIL action

If full pytest or Stage6 parity fails:

- Do not declare Stage8C FINAL.
- Do not start Stage9.
- Diagnose only the concrete regression introduced by the current Stage8C state.
- Do not reopen old stages or add another pilot merely for coverage.
- Return the exact failure, affected files, and evidence in `CHATGPT_HANDOFF.zip`.
