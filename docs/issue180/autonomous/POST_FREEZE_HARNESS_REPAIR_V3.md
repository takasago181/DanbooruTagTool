# Issue #180 — Post-freeze harness repair v3

Status: DELIBERATE HARNESS UNFREEZE / REPAIR / RE-AUDIT REQUIRED

The first frozen Codex decision run completed on:
`be72df86b6d89a96ab8eb154544230b540b76219`

The autonomous run obeyed the original write scope. Compared with freeze marker commit
`bbb157ef9cb2aeb4d4d6dec76f5b2369a80e8586`, it changed only four decision shards:

- `direct_and_exceptions_v2.csv`
- `discovery_roster_reviews_v2.csv`
- `family_terminal_reviews_v2.csv`
- `variant_pattern_reviews_v2.csv`

No main merge, production apply, Issue #70 accepted-source mutation, #179 write, or Artist mutation was authorized.

## Genuine frozen-harness defects

1. `validate_codex_write_scope_v2.py` built the marker relative path with platform-native separators. On Windows this produced backslashes while Git reports forward slashes, causing a false scope violation.
2. `smoke_authority_decision_gate_v2.py` ran synthetic fixtures alongside real persistent decision shards. Its valid `disney` terminal fixture collided with the real `disney` decision and failed CI.

## Quality hole found during audit

The first autonomous decision run technically exhausted mandatory review queues but produced only 9 PASS decisions and blanket-deferred every mandatory discovery group, every mandatory variant pattern, and every family terminal review.

That is safe but too low-yield for the product goal and contradicts the intended no-op protection. The repaired readiness gate therefore adds intentionally small productivity floors without forcing broad guesses:

- every non-exempt mandatory discovery group must produce at least one newly confirmed member;
- `original` and `indie_virtual_youtuber` are explicit zero-yield exemptions;
- mandatory family work must produce at least one autonomous `FAMILY_QUALIFIER PASS` overall;
- mandatory ready-variant work must produce at least one autonomous `VARIANT_CHARACTER PASS` overall.

These are minimum anti-no-op floors, not coverage targets. The next Codex pass is still required to exhaust all safe evidence it can find.

## Refreeze protocol

1. Commit the harness repair without changing any of the four decision shards.
2. Require the full Issue #180 workflow to PASS on the repair commit.
3. Create a new execution marker whose `base_sha` is that validated repair commit and whose `decision_snapshot_sha` is the preserved first-run decision commit above.
4. Require the full workflow to PASS again on the refreeze marker.
5. Only then resume Codex. After refreeze, only `docs/issue180/autonomous/decisions/*.csv` may change.


## Second post-freeze repair (v4)

The second Codex decision run completed at `f295559abbdce01c27290c3e1704b5cf28815780`.

It again respected freeze scope, changing only:
- `direct_and_exceptions_v2.csv`
- `family_terminal_reviews_v2.csv`
- `variant_pattern_reviews_v2.csv`

New findings:
1. `smoke_terminal_review_overrides_v2.py` chose `fate` as a synthetic family even after `fate` became a real FAMILY_QUALIFIER PASS, causing CI failure.
2. The model treated the anti-no-op floor as a target: 43 mandatory discovery groups received exactly two confirmations, despite instructions to continue harvesting safe evidence.
3. Spot audit showed some DIRECT_CHARACTER PASS rows cited generic landing pages whose recorded URL did not itself contain the claimed Character.

Repair v4 therefore:
- makes terminal smoke avoid persistent family decision keys;
- raises the productive minimum to 5 confirmed members per non-exempt mandatory discovery group, 10 family PASS rows, and 5 variant PASS rows;
- blocks known generic direct-evidence URLs found invalid by spot audit;
- flags reuse of one `CURATED_OFFICIAL_CHARACTER_PAGE` URL across multiple Characters.

The preserved second-run decision snapshot is `f295559abbdce01c27290c3e1704b5cf28815780`.
