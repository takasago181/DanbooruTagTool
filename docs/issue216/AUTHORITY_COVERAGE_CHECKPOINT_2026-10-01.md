# Issue #216 authority coverage checkpoint — 2026-10-01

Branch: `codex/issue216-unresolved-coverage-7073`
Parent checkpoint HEAD: `00c279917a1bd8d3f845987c0931ac7ba39f073e`
Frozen cohort: 13,983 Characters
Frozen #180 master SHA-256: `135463a5225b6501db923322284f8e309f217eb5359538088eb6de6d78b77071`

## Current accounting

| State | Count |
|---|---:|
| HOME_CONFIRMED | 3,625 |
| SOURCE_RESEARCHED_NO_SAFE_EVIDENCE | 68 |
| POLICY_BLOCKED | 2 |
| IDENTITY_BLOCKED | 12 |
| EVIDENCE_CONFLICT | 1 |
| UNRESEARCHED | 10,275 |
| Terminalized total | 3,708 / 13,983 (26.52%) |

Top500 UNRESEARCHED: 145. Top2000 UNRESEARCHED: 1,049. Missing Copyright roots: 0. Existing #180 confirmed HOME changes: 0. Current evidence conflicts: 1.

## Efficiency wave

- Integrated 73 exact members from the Danbooru Final Fantasy Character list, split across nine source scopes and mapped only through frozen #180 validated title-family routes. Six identities without validated normalization and two multi-title identities were withheld.
- Integrated 13 exact Hololive mascot members from one explicit curated roster scope.
- This wave added 86 terminal decisions from 10 root/source scopes and two unique source URLs: 8.6 terminalized per reviewed scope and 43 per new URL. The old 76/29 recovery batch remains excluded from new-source efficiency.
- Source registry: 1,056; reusable accepted roster sources: 909; exact member mappings: 3,748; source reuse ratio: 0.879851.

## Scheduling change

`SOURCE_YIELD_QUEUE_V2` now separates `KNOWN_POSITIVE`, `KNOWN_ZERO`, `ESTIMATED`, and `UNKNOWN`. It prioritizes current exact open joins, measured exact roster overlap, and empirical source-family yield. `expected_safe_yield` v1 remains for compatibility but no longer drives v2 ordering. Partial-roster absence stays UNKNOWN. A complete roster may exhaust only its reviewed scope; it does not decide HOME.

The 15-root roster scout reviewed 17 scopes / 17 distinct URLs: 15 found, two unknown; 13 scopes had zero exact open overlap and four remained unknown for current open overlap. It recorded 101 previously validated cohort member rows, all already terminal. Scout outputs are rejoined with the live decision ledger before scheduling. Previously reviewed source URLs are skipped by the Danbooru wiki harvester.

## Validation

- Issue #216 focused suite: 51/51 PASS.
- Issue #180 regression suite: 60/60 PASS.
- Deterministic semantic-membership rebuild: PASS.
- Frozen-input/current queue rebuild and queue v2 reproducibility: PASS.
- Authority coverage accounting: valid; intentionally incomplete while 10,275 rows remain UNRESEARCHED.
- `git diff --check`: PASS.

This is a continuation checkpoint only. No main merge or production apply is authorized.
