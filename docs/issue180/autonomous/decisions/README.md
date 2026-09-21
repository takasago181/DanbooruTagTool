# Issue #180 autonomous decision shards

Codex may write large autonomous review results as multiple CSV files in this directory instead of continuously rewriting one monolithic ledger.

Every `.csv` in this directory must use exactly this schema:

`scope,key,home_copyright,base_character,authority_type,evidence_url,evidence_claim,validation_state,officiality_state,notes`

Recommended coarse shards:

- `family_*.csv`
- `variant_*.csv`
- `roster_*.csv`
- `exceptions_*.csv`

Use substantial checkpoints rather than one file per family.

The compiler and validator read these shards together with the compatibility ledger:

`docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv`

The same `(scope,key)` may appear only once across all ledgers. Duplicate/conflicting entries fail validation.

No generated artifact belongs in this directory.
