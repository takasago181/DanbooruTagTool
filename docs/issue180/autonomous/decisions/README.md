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


## Review-only discovery groups

`DISCOVERY_GROUP` is a review-progress scope for unqualified Characters grouped by their support-only Copyright hint.

- It never grants HOME directly.
- Use `DIRECT_CHARACTER` PASS rows for members actually proven by an official/curated roster.
- Finish a group with `UNRESOLVED` or `NEEDS_HIGHER_REASONING` only after actual group/roster research.
- A terminal DISCOVERY_GROUP row requires grounded evidence and a substantive note.


## Review-only variant patterns

`VARIANT_PATTERN` is review-progress only.

- key = `pattern_id` from `VARIANT_PATTERN_GROUPS_V2.csv`
- it never grants HOME directly;
- use explicit `VARIANT_CHARACTER PASS` rows for variants proven by the reviewed official pattern;
- finish the pattern with `UNRESOLVED` or `NEEDS_HIGHER_REASONING` plus grounded evidence and a substantive note.


## Frozen execution rule

Once `docs/issue180/autonomous/CODEX_EXECUTION_BASE_V2.json` exists:

- create/commit only new decision shard CSVs in this directory;
- do not modify `AUTHORITY_DECISIONS_BASE_V2.csv`;
- do not modify the compatibility ledger outside this directory;
- do not edit compiler/validator/policy/workflow/runbook to make a gate pass;
- if a genuine harness defect is found, report it as a blocker for deliberate unfreeze/re-audit.

Terminal `UNRESOLVED` / `NEEDS_HIGHER_REASONING` rows are review conclusions, not shortcuts. Every terminal review requires grounded evidence plus substantive notes. This applies to family, Character, discovery-group and variant-pattern reviews.
