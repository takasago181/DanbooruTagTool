# Issue #49 rollback instructions

Do not run these instructions as part of the promotion audit. They are provided
for an authorized rollback on this task branch.

1. Confirm the checkout is `codex/issue49-dict-promotion-latest-main` and verify the current
   HEAD `484bf928a1b1c8c07f349bcc1bc77681d72e2160` and profile SHA against
   `docs/issue49/applied_diff_report.json`.
2. To remove this branch's committed implementation, use a reviewed
   `git revert <issue49-final-commit-sha>` and preserve the resulting evidence.
3. If a byte-exact profile restoration is required before review, restore from
   the recorded production base with:

   `python tools/issue49_promotion.py --restore-baseline-ref origin/main --manifest docs/issue49/effective_candidate_manifest.json`

4. Verify 2,788 rows, identity/order, and the before SHA from the completion
   report. Re-run the integrity checks before any further action.

This procedure does not delete quarantine data, protected raw data, or evidence
artifacts. Main merge and any subsequent promotion decision remain with DEV/AUDIT.
