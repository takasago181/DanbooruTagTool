# Issue #30 Special-representative routing design — 2026-09-08

Status: DESIGN ADOPTED / FINAL TEST DATA HOLD

## Why this exists

The accepted generic golden set (`standing / sitting / long_hair / smile`) remains valid as a low-level plumbing/evaluator fixture. It is not representative enough for DanbooruTagTool's actual Special Core Dictionary-centered Stage10 purpose. The production snapshot remains technically identified as `Special2788`.

Joint review source: Issue #37 KNOWLEDGE + PROMPT consensus.

## What is adopted now

Stage10-prep representative calibration must be built around the actual product difficulty, not only WD14-friendly unary tags.

Required representative dimensions:

1. direct Special presence/absence
2. rare / niche Special
3. relation / actor-target / body-site binding
4. multiple-Special simultaneous retention
5. support-tag dependency where observability/visibility changes while Special identity remains fixed
6. canonical/Alias or otherwise identity-sensitive behavior when relevant

Every A/B pair keeps `one experiment = one question` and holds all unrelated generation conditions fixed.

## Routing model

The evaluator is capability-routed, not one universal confidence threshold.

Candidate capability classes:

- `DIRECT_TAG`: machine evaluator may score a real canonical/Core/Extended target if vocabulary and calibration are validated.
- `ALIAS_CANONICAL`: evaluator may map evidence to canonical identity while preserving the actual Alias Prompt input and metadata; this is evaluation mapping, not silent Prompt rewrite.
- `SEMANTIC_DECOMPOSED`: only machine-checkable visual predicates are scored; the rest routes to REVIEW.
- `RELATION_BINDING`: actor-target/body-site/relation semantics require multiple signals or human review when unsupported.
- `MULTI_SPECIAL_RETENTION`: judge both added target presence and preservation of the base Special; do not reduce to one independent target score.
- `VISIBILITY_SUPPORT`: compare observability with/without the intended support while keeping Special identity fixed.
- `HUMAN_ONLY`: unsupported rare/subtle/unusual-anatomy semantics route directly to REVIEW.

Infrastructure or required traceability missing -> `BLOCKED`.
Unsupported vocabulary or insufficient evidence -> `REVIEW`.
Only validated compatible classes may emit candidate `A_WIN` / `B_WIN`.

## Threshold rule

Do not apply one confidence/margin threshold across:

- simple unary tags
- relation/composite cases
- rare/niche Special
- multiple-Special cases
- different model families

Production confidence/margin thresholds remain HOLD until representative human-labeled evidence and post-freeze evaluator coverage are available.

## Negative Prompt boundary

Do not use anatomy-sensitive negatives such as `bad anatomy`, `extra limbs`, `extra arms`, or similar terms as an unconditional baseline for unusual-anatomy Special tests.

Their interaction with unusual anatomy is a separate one-question A/B item. This is an experiment-isolation rule, not a production Negative Prompt rule.

## What remains HOLD until final dictionary freeze

Do not finalize:

- representative Special IDs / exact final case list
- WD14 / Kagami-24k / CL Tagger v2 role allocation
- full Special Core Dictionary evaluator coverage
- per-Special `AUTO` vs `REVIEW` routing
- production confidence/margin thresholds

PROMPT may continue preparing Prompt structures, A/B questions, support-isolation patterns, and replacement workflow without freezing the final IDs.

## Required KNOWLEDGE follow-up after dictionary freeze

Run coverage comparison on the finalized 2,788-entry Special set against:

- WD14 / `wd-eva02-large-tagger-v3`
- Kagami-24k
- CL Tagger v2 stable/fixed release

Report at least:

- raw vocabulary coverage
- coverage by Core / Extended / Alias / Semantic
- coverage by post-count bands
- Alias raw coverage and canonical-target coverage separately
- evaluator disagreement on representative images when available

The returned coverage determines evaluator allocation; it must not be inferred from the current WD14-friendly fixture.

## Existing generic fixture disposition

Accepted evidence commit: `33215269cfeb33b3afab0c36a6a8bd52cb55952e`.

Keep it for:

- API / generation / metadata / Tagger plumbing
- REVIEW fallback sanity checks
- simple concept baseline

Do not use its 8 human labels alone to promote a production threshold.

`docs/testing/ISSUE30_HUMAN_GOLDEN_LABEL_CONTACT_SHEET_TASK_20260908.md` is paused/superseded as the next product-representative step. It may be reused later only as a low-level fixture review if useful.

## Current boundary

- Test method and routing philosophy: may proceed.
- Final representative data and evaluator assignment: HOLD until dictionary freeze + KNOWLEDGE coverage return.
- Stage10 production A/B: not started.
