# Issue #70 — Full-population 2D scope pass

## Purpose

Classify every Character and Copyright row in Issue #70 before the remaining semantic-name audit is closed.

Population:
- Character: 35,890
- Copyright: 8,536
- Total scope population: 44,426
- Artist: excluded from media-scope filtering and remains in product scope.

## Scope labels

- `IN_2D`: fictional / illustrated content in the user's target scope.
- `REAL_3D`: real-world or live-action-only identity outside the target scope.
- `UNCERTAIN`: insufficient evidence for a safe exclusion.

The rule is about media / identity scope, not rendering technology. Games and fictional properties remain `IN_2D` even when they use 3D CG.

Examples of `IN_2D`:
- anime, manga, games, visual novels, webcomics/webtoons
- VTubers and virtual characters
- illustrated fictional IP
- original fictional characters / original illustration identities

Examples of `REAL_3D`:
- real people / celebrities / idol groups
- real sports / tournaments
- real-world events
- live-action-only film / TV properties
- companies / services / general commercial brands
- photographs / real-world media identities

Mixed-media franchises, ambiguous brands/IP, and uncertain identities MUST remain `UNCERTAIN` until reviewed. Never exclude on a weak heuristic.

## Ordering

1. Build an exact 44,426-row ledger from the immutable Issue #70 source chunks.
2. Import already-confirmed `REAL_3D` decisions from the #115 audit as seeds.
3. Apply only high-precision deterministic `IN_2D` markers to Copyright.
4. Propagate a Copyright decision to Character only when Character↔Copyright co-occurrence is dominant enough to be safe.
5. Put every remaining row into an explicit review queue, Copyright first.
6. Resolve Copyright scope first, then regenerate the ledger so most Character rows can inherit a dominant Copyright decision.
7. Review residual Character rows directly.
8. Only after scope classification is accepted, resume/close the remaining #115 semantic-name audit for rows still in scope.

## Residual review batching discipline

For residual manual review, batches MUST be formed from a fixed queue slice rather than by selecting rows to reach a preferred class balance.

1. Freeze the next queue slice first (normally 100 rows).
2. Inspect every row in that slice in queue order.
3. Assign `IN_2D` or `REAL_3D` only when the identity is clear under this protocol.
4. Leave ambiguous or mixed-media rows `UNCERTAIN`; do not replace them with easier rows merely to fill a quota.
5. Use external evidence for identities that are not self-evident from the canonical tag / primary copyright.
6. Report the natural result distribution. Never target, balance, or normalize the IN_2D / REAL_3D ratio.
7. If a prior batch was assembled by cherry-picking high-confidence rows, audit it before relying on its class distribution.

## Production boundary

This lane is audit-only.

Do not:
- modify runtime/catalog production data;
- modify General or Special;
- modify UserData;
- merge PR #115;
- merge this lane before its ledger and review decisions are accepted.

`REAL_3D` rows are recorded as exclusion candidates only. Raw source rows are never deleted.

## Authority

Branch: `audit/issue70-2d-scope-full`

Generated artifacts:
- `docs/issue70/scope/full_scope_ledger.csv`
- `docs/issue70/scope/scope_summary.json`
- `docs/issue70/scope/scope_review_queue.csv`
- `docs/issue70/scope/runtime_exclude_real3d_candidates.csv`

Confirmed manual/previous-audit decisions:
- `docs/issue70/scope/confirmed_real3d_seed.csv`

The generated ledger must contain exactly 44,426 unique rows and exactly:
- 35,890 Character
- 8,536 Copyright
