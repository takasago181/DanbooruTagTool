# Issue #180 — Autonomous Completion v2

Status: RESEARCH ONLY / NO MAIN MERGE / NO PRODUCTION APPLY

This is the execution contract for completing the remaining Character → HOME Copyright audit with a low-cost Codex model without allowing the model to edit the generated master directly.

## Target

`Character -> HOME_COPYRIGHT (0..1)`

Allowed final states:

- `HOME_CONFIRMED`
- `HOME_UNRESOLVED`
- `NOT_OFFICIAL_CHARACTER`

No `MULTI_HOME` state exists.

## Architecture

The v2 pipeline separates evidence collection from deterministic application.

1. `build_autonomous_foundation_v2.py`
   - preserves all currently validated v1 HOME rows;
   - reconstructs the old 1,456 qualifier-family mappings with provenance;
   - fast-paths reviewed first-party family authority and exact qualifier==Copyright authority;
   - refuses to bulk-apply nested/variant identities;
   - isolates normalized mappings for fast semantic revalidation;
   - generates family, variant, unqualified, and higher-reasoning queues.

2. `docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv`
   - this is the only persistent input Codex should normally add to;
   - Codex writes evidence decisions, not final master rows.

3. `compile_character_home_v2.py`
   - applies foundation authority plus PASS rows from the decision ledger;
   - resolves direct and family authority deterministically;
   - applies reviewed variant inheritance only from a HOME-confirmed base;
   - never chooses between conflicting HOME roots;
   - generates the 35,890-row v2 master and applied authority ledger.

4. `validate_autonomous_completion_v2.py`
   - checks population, state accounting, root existence, HOME cardinality, conflict count, production flags, and authority/master consistency.

5. `build_user_review_v2.py`
   - creates the complete 35,890-row Japanese pre-freeze review text.

## Why fast-path exact qualifier authority is allowed

Issue #180 authority policy already accepts a verified final Copyright qualifier as A1 authority.

Therefore an already second-reviewed family where:

- the final qualifier exactly equals an in-catalog Copyright root,
- known broad/generic families were excluded by the prior semantic gate,
- the Character tag is not a nested/variant identity,

may be reused without requiring an individual official Character page.

This prevents the audit from becoming needlessly strict.

## Why normalized mappings are not automatically reused

Historical normalized matches include semantically weak examples. They are useful candidates but are not automatically equivalent to reviewed root normalization.

Those mappings go to `FAST_REVALIDATE_NORMALIZATION`.

Codex should validate the family mapping once and then write one `FAMILY_QUALIFIER` decision for the family instead of researching every Character separately.

## Nested and variant identities

A tag whose final IP qualifier is preceded by another qualifier is not bulk-confirmed by family authority alone.

Example shape:

`character_(costume)_(copyright)`

These rows enter `VARIANT_WORK_QUEUE_V2.csv`.

A variant may inherit HOME when:

- its base Character is HOME_CONFIRMED;
- the variant is confirmed official, or the franchise has a sufficiently reviewed official variant pattern;
- no fanmade/parody/crossover contradiction exists.

Codex records the result as `VARIANT_CHARACTER` with `base_character`.

## Unqualified Characters

`UNQUALIFIED_WORK_QUEUE_V2.csv` is roster/discovery work.

Old relation/co-occurrence, if present, is explicitly stored as `support_only_old_relation_hint` and is never authority.

Use it only to choose where to search.

## Decision ledger schema

File:

`docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv`

Columns:

- `scope`
- `key`
- `home_copyright`
- `base_character`
- `authority_type`
- `evidence_url`
- `evidence_claim`
- `validation_state`
- `officiality_state`
- `notes`

Supported scopes:

### FAMILY_QUALIFIER

`key` is the final qualifier family.

A PASS row applies one HOME to every non-nested Character in that family unless the Character is explicitly blocked.

Use for reviewed family/root authority.

### DIRECT_CHARACTER

`key` is one canonical Character tag.

Use official/curated roster or direct Character authority.

### VARIANT_CHARACTER

`key` is the variant canonical tag.

`base_character` is mandatory.

The compiler only applies the row after the base Character has a confirmed HOME. An explicitly supplied HOME must equal the base HOME.

### BLOCK_CHARACTER

Keeps one Character unresolved instead of allowing family bulk application.

Use for fanmade/ambiguous/crossover exceptions.

A block that contradicts existing direct authority is a conflict and must be reviewed.

### NOT_OFFICIAL_CHARACTER

Use only for a second-reviewed Character identity proven fan-created/non-official/out of product scope.

No HOME is allowed on this row.

## validation_state

- `PASS` — compiler may consume it.
- `UNRESOLVED` / `PENDING` — retained as work, not applied.
- `NEEDS_HIGHER_REASONING` — explicitly deferred without blocking unrelated work.

Do not invent any other state.

## Codex work order

Use this order to maximize completion per token:

1. `FAMILY_WORK_QUEUE_V2.csv`
   - `FAST_REVALIDATE_NORMALIZATION`
   - `FAST_REVIEW_NEW_EXACT`
   - `REVIEW_NORMALIZATION`
   - `DISCOVERY_RESEARCH`
   - broad/ambiguous cases last

2. `VARIANT_WORK_QUEUE_V2.csv`
   - rows with `BASE_HOME_READY_OFFICIALITY_REVIEW` first
   - then rows whose base becomes confirmed after family/direct work
   - unresolved nontrivial bases last

3. `UNQUALIFIED_WORK_QUEUE_V2.csv`
   - direct roster candidates and high-post Characters first
   - use one official/curated roster to cover many Characters whenever possible
   - do not perform one web search per Character when a roster can answer a whole group

4. `NEEDS_HIGHER_REASONING_REVIEW_V2.csv`
   - do not stop the whole run for these;
   - append NEEDS_HIGHER_REASONING decisions and continue.

## Evidence balance

Do not require an individual official page for every Character.

Reusable evidence is preferred:

- official Character/member roster;
- approved curated roster;
- clean Copyright qualifier;
- reviewed root normalization;
- reviewed official variant pattern.

Do not use as final authority:

- old RelatedCopyright;
- post co-occurrence;
- search-term similarity;
- generic wiki-body links;
- majority vote.

## Piapro / Hatsune Miku policy

The current repository contains conflicting policy history for Piapro Characters versus the `vocaloid` root.

Keep these cases in higher-reasoning/policy review unless the project policy is explicitly resolved.

Do not stop unrelated work.

## Mandatory invariants

Every run must preserve:

- Character population = 35,890
- unique Character canonical tags = 35,890
- HOME per Character <= 1
- every confirmed HOME exists in Copyright catalog
- no conflict silently selected
- no production_approved=true
- accepted Issue #70 source unchanged
- production unchanged

## Protected areas

Do not:

- merge main;
- apply production;
- mutate Issue #70 accepted source;
- write to Issue #179 branch;
- audit Artist;
- edit the generated master by hand.

## Completion output

A completion attempt should finish with:

- `CHARACTER_HOME_MASTER_V2.csv`
- `APPLIED_AUTHORITY_LEDGER_V2.csv`
- queue summaries and remaining higher-reasoning cases
- `ISSUE180_ALL_35890_USER_REVIEW_V2.txt`
- CI PASS

Final freeze still requires explicit user review of the complete 35,890-row review artifact.
