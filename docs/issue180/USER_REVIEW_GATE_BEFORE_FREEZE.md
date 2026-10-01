# #180 User review gate before final freeze

## Mandatory stop rule

Before any final freeze, merge, accepted-source promotion, or production apply, present the complete review population to the user in a human-readable form.

The user must be able to inspect **all rows**, not only summaries or samples.

Required review export:
- UTF-8 Japanese text file (or equivalently easy-to-read artifact)
- one entry per Character row in the full 35,890-row population
- Japanese display name when available
- canonical tag
- proposed/confirmed HOME Copyright when any
- Japanese Copyright display name when available
- decision/state (confirmed candidate / unresolved / not official if applicable)
- short plain-Japanese reason/evidence class
- unresolved/conflict items clearly marked
- no freezing before explicit user review

A compact summary may accompany the full file, but must not replace it.

This gate is user-facing and is in addition to CI/precision gates.
