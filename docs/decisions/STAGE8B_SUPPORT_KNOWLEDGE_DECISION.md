# Stage 8B Support Knowledge decision

## Decision

Add a third Recommendation tab, `意味から補助`, backed by two small reviewed
sidecars and an explicit-only loader. The existing `よく使われる` and
`珍しい関連` tabs remain the unchanged Stage 6 statistical result. The new tab
states that its candidates come from Special meaning and generation structure
and never presents invented counts, rates, or lift.

The Pilot activates 39 Special-specific rows across ten reviewed Special IDs.
The family-rule file remains empty in production. This keeps the Pilot boundary
exact while preserving a validated Special-over-family merge path for later
reviewed Stage 8C coverage.

Canonical deduplication is presentation-only. An aggregate candidate owns a
deterministically ordered `relations` tuple, and each relation retains its owner
Special ID plus slot, class, reason, intent, combination, evidence, provenance,
and test trace. Selecting multiple Specials therefore never turns one relation's
metadata into a claim about another selected Special.

Pressing `＋追加` uses the existing Manual Auxiliary operation. Viewing support
does not mutate the Special Core or Prompt, and `CORE_SUPPORT` is still never
auto-added. Intent and combination metadata are retained for inspection and are
not used for ranking, filtering, conflict resolution, or Prompt rewriting.

## Production-family precedence

The package Pilot table labels Special ID 416 (`bdsm`) as `RESTRAINT_ACTION`.
The fixed Stage 6 v2.1 production profile has the later reviewed value
`CONTEXT_MODIFIER`. Stage 8B retains the production value and records the
difference in `benchmarks/stage8b/pilot_audit.json`; it does not roll back the
approved Generation Profile.

## Boundary

There is no content-category filter, penalty, or boost. Profileless Specials
return no suggestion. Stage 6 math/order, Stage 7B asynchronous work, Stage 8A
decoration, identities, Prompt order, and offline runtime remain unchanged.
Stage 8C coverage and Stage 9 editing are outside this decision.
