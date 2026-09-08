# Special2788 Dictionary Validation Quarantine

Issue: #32
Branch: `dict-validation/quarantine`
Status: ACTIVE / NOT FOR PRODUCTION

## Purpose
This directory is the durable workspace for the long-running validation of Special2788 generation metadata and semantic support data.

## Hard boundary
- Production data on `main` is read-only input for this audit.
- Nothing in this directory is production authority.
- Proposed fixes remain quarantined until full coverage, revalidation, and a separate final promotion audit are complete.
- Do not merge this branch into `main` as a bulk change.

## Durable state
The current audit state must be recoverable from files in this directory plus Issue #32 without relying on chat memory.

Files:
- `VALIDATION_RULES.md`: current validation rules and rule-version history. R2 is active after sequence 40.
- `progress.json`: single current restart point and aggregate Special/support-row counts.
- `results.csv`: one durable Special-level result row per validated Special/batch decision.
- `semantic_support_results.csv`: one durable audit record per frozen semantic-support input row.
- `candidate_fixes.csv`: proposed corrections only; never treated as approved production data.
- `revalidation_queue.csv`: prior rows that must be revisited after rule/evidence changes.
- `handoff.md`: current chat-to-chat handoff summary.

## Batch policy
- Deterministic Special order.
- 100 Specials per external batch.
- 20 x 5 internal consistency blocks.
- Fast screening first, targeted deep review second.
- R2 requires complete frozen semantic-support row coverage, not only `CORE_SUPPORT + ADDITIVE` coverage.
- R2 requires generation-evidence cross-checks for high-impact claims instead of allowing production metadata to self-certify image-generation behavior.
- Sample PASS rows every 100-row batch under the numeric escalation rules in `VALIDATION_RULES.md`.

## Valid states
- PASS
- FIX
- REVIEW
- IMAGE_TEST_REQUIRED

Blank/None is not automatically an error. `REVIEW` / `IMAGE_TEST_REQUIRED` may represent audited-but-unresolved rows when evidence is explicitly recorded.

## Restart rule
Before moving to a new ChatGPT chat, update `progress.json` and `handoff.md` at minimum, plus row-level ledgers that changed. The new chat resumes from GitHub state, not conversational recollection.
