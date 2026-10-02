# Issue #44 automation inbox

This directory is the durable handoff path for the four weekly KNOWLEDGE scouts.

## Purpose

Scout runs must not depend on GitHub Issue comments for persistence.
Each scout writes one small metadata-only receipt under `docs/knowledge/automation/inbox/`.
The weekly Knowledge Integrator consumes those receipts, performs evidence/duplication/version checks, and then updates the canonical knowledge corpus.

## Receipt naming

`YYYY-MM-DD_<lane>.json`

Allowed lane names:
- `model-watch`
- `tag-behavior`
- `failure-patterns`
- `prompt-examples`

## Receipt content

Receipts contain research metadata only:
- run date
- lane
- status
- models / versions
- new_or_updated_count
- hold_count
- evidence URLs
- short abstract findings
- reproducibility/confidence
- tool impact
- `production_modified: false`

Do not store long source quotations, full prompts, detailed generation recipes, or explicit sensitive descriptions. Sensitive findings are represented only by abstract classes such as `ADULT_RELATION`, `INTERACTION`, `BODY_SITE`, and `BINDING`.

## Persistence rule

1. Scout researches.
2. Scout writes/updates its dated inbox receipt on `knowledge/generation-corpus`.
3. Issue comment is optional and must never be the only durable copy.
4. If an Issue comment is rejected, the run remains successful when the inbox receipt was committed.
5. The Integrator reads the inbox receipts first. Missing Issue comments do not trigger a full re-run when a valid receipt exists.
6. After integration, canonical knowledge remains in the existing Claim Registry / HOLD-CONFLICT / freshness / catalog structure. Inbox receipts are evidence handoff artifacts, not production authority.

No scout or Integrator may modify `main`, production runtime, or `data/**` through this pipeline.
