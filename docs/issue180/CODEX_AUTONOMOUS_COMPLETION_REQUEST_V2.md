# Issue #180 — Codex Autonomous Completion Request v2

Use this request for the large remaining audit after the autonomous v2 foundation is present.

Recommended execution model: low-cost Codex/Luna is acceptable because HOME application is deterministic and the model is not allowed to edit the generated master directly.

## Repository / branch

Repository:
`takasago181/DanbooruTagTool`

Work only on:
`research/issue180-single-home-pilot`

Do not merge main.
Do not apply production.
Do not mutate Issue #70 accepted source.
Do not write to the Issue #179 branch.
Do not audit Artist.

## Preflight

Read, in this order:

1. Issue #180 body
2. `docs/issue180/AUTONOMOUS_COMPLETION_V2.md`
3. `scripts/issue180/build_autonomous_foundation_v2.py`
4. `scripts/issue180/compile_character_home_v2.py`
5. `scripts/issue180/validate_autonomous_completion_v2.py`
6. `docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv`

Do not redesign the policy unless a systemic contradiction makes the current contract impossible.

## Current v2 baseline

The validated v2 foundation starts from:

- Character population: 35,890
- v1 HOME preserved: 940
- reviewed fast-path family rows added: 8,832
- foundation HOME_CONFIRMED: 9,772
- foundation HOME_UNRESOLVED: 26,118
- remaining family rows: 5,417 across 2,521 families
- remaining variant/nested rows: 3,921
- remaining unqualified rows: 16,780

The exact counts may improve after new decisions. Never force them back to these numbers.

## Core operating rule

Do not edit:

- `CHARACTER_HOME_MASTER_V2.csv`
- `APPLIED_AUTHORITY_LEDGER_V2.csv`

by hand.

Add reviewed evidence decisions only to:

`docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv`

Then rerun:

`python scripts/issue180/compile_character_home_v2.py`

The compiler is the only authority that creates the final master.

## Decision scopes

Use only:

- `FAMILY_QUALIFIER`
- `DIRECT_CHARACTER`
- `VARIANT_CHARACTER`
- `BLOCK_CHARACTER`
- `NOT_OFFICIAL_CHARACTER`

Use only validation states:

- `PASS`
- `UNRESOLVED`
- `PENDING`
- `NEEDS_HIGHER_REASONING`

## Goal of this run

Do as much of the remaining audit as can be done safely in one autonomous run.

Do not finish by converting every mandatory queue to boilerplate UNRESOLVED. For non-exempt mandatory discovery groups, confirm at least one actually proven member and then continue harvesting all safe roster members. Mandatory family and ready-variant lanes must also produce nonzero PASS yield overall when safe evidence exists. Existing decision-shard rows may be revised in place when stronger evidence justifies replacing an earlier over-conservative terminal result; keep exactly one decision per scope/key.

Do not stop for one hard Character, family, source, policy case, or failed lookup.

If a case cannot be resolved safely:

- record it as UNRESOLVED or NEEDS_HIGHER_REASONING;
- add a concise reason;
- continue all independent work.

The run should stop only after all high-yield safe work has been attempted and the final v2 compiler/validation/review artifact has been generated.

## Pass 1 — Family work

Start with:

`artifacts/issue180-full-preflight/POST_NORMALIZED_REVIEW/MASTER_HOME_V2/REMAINING_FAMILY_WORK_V2.csv`

Any remaining `DISCOVERY_RESEARCH` family with 10 or more unresolved Character rows is mandatory high-yield work. It must be safely HOME-confirmed or explicitly reviewed/deferred with grounded evidence before the autonomous pass can claim completion.

Priority order:

1. `FAST_REVALIDATE_NORMALIZATION`
2. `FAST_REVIEW_NEW_EXACT`
3. `REVIEW_NORMALIZATION`
4. high-count `DISCOVERY_RESEARCH`
5. broad/ambiguous/higher-reasoning families last

One family decision should cover the whole non-nested family when reusable authority is valid.

Do not research every Character individually when one family/root decision is sufficient.

### Normalization caution

Historical normalized matching is candidate evidence only.

Some prior mechanical normalized candidates were semantically weak, so verify the family/root relationship before PASS.

If the mapping is obvious and stable, write one `FAMILY_QUALIFIER` PASS row.

If not, write UNRESOLVED or NEEDS_HIGHER_REASONING and continue.

### Acceptable family evidence

Strong examples:

- official franchise/work site proving the root identity;
- official Character/member roster;
- approved curated roster;
- clear canonical Copyright qualifier/root identity;
- separately reviewed alias/root normalization.

Do not require an individual Character profile for every member of a clean family.

### Forbidden final authority

Never confirm HOME from:

- old RelatedCopyright;
- post co-occurrence;
- name similarity alone;
- generic wiki body links;
- search term overlap;
- majority vote.

These may only help choose a research target.

## Compile checkpoint A

After a meaningful family batch:

1. run `compile_character_home_v2.py`;
2. inspect `remaining_work_v2_summary.json`;
3. continue without asking the user.

Do not create a user-facing stop just because counts changed.

## Pass 2 — Variant / nested work

Use:

`REMAINING_VARIANT_WORK_V2.csv`

Process `BASE_HOME_READY_OFFICIALITY_REVIEW` first.

A `VARIANT_CHARACTER` PASS row must include `base_character`.

The compiler will enforce that:

- the base is HOME_CONFIRMED;
- the inherited HOME is the base HOME;
- a conflicting supplied HOME is rejected.

Use reusable official variant patterns when justified.

For example, an official franchise may have a consistent official costume/form naming pattern. A reviewed pattern may support multiple variants; do not demand a separate official page for every costume if the official pattern is established.

Do not treat:

- fanmade forms;
- parody forms;
- unofficial crossover forms;
- ambiguous nested qualifiers

as official variants without evidence.

After variant decisions, rerun the compiler. Newly confirmed bases may make additional variants ready. Repeat variant review until no meaningful new BASE_HOME_READY work appears.

## Pass 3 — Unqualified Character work

Use:

- `REMAINING_UNQUALIFIED_WORK_V2.csv`
- `UNQUALIFIED_DISCOVERY_GROUPS_V2.csv`

The discovery groups exist to prevent 16k individual searches.

`support_only_old_relation_hint` and `discovery_primary_root_hint` are research-navigation hints only.

They are never HOME authority.

Process groups by:

1. largest/highest-impact group;
2. official/curated roster availability;
3. ability to reuse one roster across many Characters.

When an official/approved roster proves a Character belongs to one canonical HOME, write `DIRECT_CHARACTER` PASS rows for matched Characters.

Automate exact roster matching where safe.

Do not force unmatched Characters into the roster HOME.

If a group has no usable roster, leave those Characters unresolved and continue to the next group.

## Piapro policy

Hatsune Miku / KAITO / related Piapro cases have conflicting historical root policy.

Do not independently decide the project policy.

Keep unresolved or NEEDS_HIGHER_REASONING unless the existing project policy is explicitly reconciled.

Continue all unrelated work.

## NOT_OFFICIAL_CHARACTER

Be conservative here.

Use `NOT_OFFICIAL_CHARACTER` only when the Character identity itself is explicitly confirmed fan-created/non-official/out of product scope and the decision is sufficiently reviewed.

Unknown is not non-official.

Do not manufacture NOT_OFFICIAL rows merely to reduce unresolved count.

## Blocks

Use `BLOCK_CHARACTER` to exclude one Character from family bulk application when evidence shows the family rule should not apply.

If a block contradicts already accepted direct authority, the compiler intentionally reports a conflict.

Do not bypass that gate.

## Iteration loop

Repeat this loop within the same Codex run:

1. inspect current REMAINING_* queues;
2. add a meaningful batch of evidence decisions;
3. compile v2 master;
4. inspect remaining-work summary;
5. continue the highest-yield newly available work.

Do not return to the user after every loop.

Continue until one of these is true:

- remaining work is genuinely authority-limited;
- remaining work is overwhelmingly higher-reasoning/policy cases;
- further progress would require guessing;
- all work is resolved.

## Escalation behavior

When Luna cannot safely resolve a case, do not spend excessive tokens repeatedly reconsidering it.

Write:

`validation_state=NEEDS_HIGHER_REASONING`

with a concise note containing:

- candidate HOME;
- evidence already checked;
- exact ambiguity;
- what a stronger review should decide.

Then continue.

This creates a small high-value handoff for Terra/Sol instead of consuming the full run.

## Required final commands

Before stopping, run:

`python scripts/issue180/compile_character_home_v2.py`

`python scripts/issue180/validate_autonomous_completion_v2.py`

`python scripts/issue180/build_user_review_v2.py`

Then run the Issue #180 GitHub Actions workflow and inspect the actual numeric logs, not only the green status.

## Final gates

Must remain true:

- Character rows = 35,890
- state sum = 35,890
- HOME per Character <= 1
- confirmed HOME root exists in canonical Copyright catalog
- multi-home conflicts = 0
- no silent conflict selection
- production_approved=true rows = 0
- Issue #70 accepted source unchanged
- production unchanged

If a conflict appears, resolve the decision ledger or leave the Character unresolved. Never choose a winner by score or majority.

## Checkpoint policy

Do not commit after every Character or family.

Use a small number of meaningful checkpoints, for example:

1. family authority checkpoint
2. variant checkpoint
3. unqualified roster checkpoint
4. final validated checkpoint

If the run is forced to stop early, commit the current decision ledger plus a concise checkpoint document describing remaining lanes.

## Completion artifacts

Required at the end:

- `POST_NORMALIZED_REVIEW/MASTER_HOME_V2/CHARACTER_HOME_MASTER_V2.csv`
- `POST_NORMALIZED_REVIEW/MASTER_HOME_V2/APPLIED_AUTHORITY_LEDGER_V2.csv`
- `POST_NORMALIZED_REVIEW/MASTER_HOME_V2/remaining_work_v2_summary.json`
- `POST_NORMALIZED_REVIEW/MASTER_HOME_V2/NEEDS_HIGHER_REASONING_REVIEW_V2.csv`
- `ISSUE180_ALL_35890_USER_REVIEW_V2.txt`

Final freeze is forbidden until the complete 35,890-row user review artifact is shown to the user and explicitly accepted.

## Final report

Report only after the autonomous run has gone as far as safely possible.

Include:

- branch
- final HEAD
- HOME_CONFIRMED
- HOME_UNRESOLVED
- NOT_OFFICIAL_CHARACTER
- remaining family rows/families
- remaining variant rows
- remaining unqualified rows
- NEEDS_HIGHER_REASONING count
- authority type counts
- canonical root normalization count
- conflicts
- missing roots
- CI run/result
- accepted source unchanged
- production unchanged
- full 35,890 review artifact path

Do not ask the user to repeatedly send “continue”.
