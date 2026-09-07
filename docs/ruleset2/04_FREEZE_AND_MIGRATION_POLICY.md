# FREEZE AND MIGRATION POLICY

## Old problem

`FINAL/FIXED` was doing two jobs:

1. guaranteeing reproducibility of a historical result, and
2. forbidding future design improvement.

Only the first is always required.

## New definition

A frozen artifact is immutable **as an artifact**. Its bytes/hash and historical interpretation do not change.
A new version may supersede it when there is:

1. an explicit reason,
2. old -> new mapping,
3. affected rows/rules listed,
4. regression checks,
5. preserved historical artifact/hash,
6. no silent mutation of unrelated stages.

## Freeze classes

### SNAPSHOT_FREEZE
Historical bytes/results are immutable, but a successor version is allowed.
Examples: Stage8A v2, Stage8B v3, dictionary v2.9.

### EVIDENCE_FREEZE
Raw evidence/source/math input remains immutable for reproducibility. New derived interpretation may coexist.
Example: Stage6 raw counts/math/source snapshot.

### ACCEPTANCE_BASELINE_FREEZE
A test's expected counts/conditions stay fixed for that test version. New product behavior requires a new test version.
Example: Stage8C Pilot001 expectations.

### HARD_RUNTIME_INVARIANT
Not merely historical; current product must obey it until user explicitly changes policy.
Examples: runtime no-LLM/offline; severity not used as completeness filter.

## Migration rule

Never mutate a frozen artifact in place. Create vNext plus a migration record.
