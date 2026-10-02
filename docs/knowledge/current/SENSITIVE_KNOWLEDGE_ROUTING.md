# Sensitive-domain knowledge routing

Owner: Issue #44 KNOWLEDGE  
Purpose: preserve durable technical knowledge when a cross-cutting summary or issue-comment payload is rejected by an external safety layer.

## Principle

Do not try to bypass external safety checks.

Instead, separate storage by role so that one rejected summary write cannot block the knowledge corpus.

## Storage layers

### 1. Detailed research
Location:
- `docs/knowledge/research/BATCH_*.md`

Store:
- source URLs
- exact model/runtime scope
- experimental design
- sample counts
- observed failure classes
- technical interpretation
- unresolved questions

Avoid:
- copying long source passages
- unnecessary raw prompt examples
- duplicating explicit scene wording when a structural description is sufficient

### 2. Claim Registry
Location:
- `docs/knowledge/current/CLAIM_REGISTRY.csv`

Store only atomic, reusable claims:
- scope
- evidence class
- status
- validation state
- source pointer

Use structural vocabulary such as:
- subject_count
- identity_binding
- role_binding
- target_site
- geometry
- topology
- visibility
- state_count
- context_leak
- negative_collision
- assisted_control

### 3. Source Registry
Location:
- `docs/knowledge/GENERATION_KNOWLEDGE_SOURCES.md`

Store:
- source URL
- language
- evidence class
- short technical value
- limitations

Do not mirror source text.

### 4. Catalog
Location:
- `docs/knowledge/catalog/*.md`

Store domain-level learning structure and diagnostic taxonomy.
Point to research files for detail.

### 5. Corpus / Quick Reference
Locations:
- `docs/knowledge/GENERATION_KNOWLEDGE_CORPUS.md`
- `docs/knowledge/current/CURRENT_QUICK_REFERENCE.md`

These are indexes/syntheses only.

For sensitive-domain material, keep only:
- capability area
- diagnostic axes
- current Claim IDs
- research-file pointer
- unresolved test list

Do not duplicate detailed source examples here.

### 6. GitHub Issue checkpoint

Issue comments are optional checkpoints, not the source of truth.

If a comment payload is rejected:
- do not retry by obfuscating it;
- keep the branch commit as authority;
- post only a neutral checkpoint later if useful: HEAD, changed files, Claim counts, validation result.

## Failure tolerance

A blocked write must never leave knowledge only in chat.

Minimum durable set for a research batch:
1. research file
2. Claim rows when warranted
3. source registry entries
4. File Map entry

Corpus/Quick/Issue comments are secondary and can be added as neutral pointers.

## Restore order

`CLAIM_REGISTRY -> relevant catalog -> research batch -> source registry -> version ledger`

Cross-cutting summaries are convenience views, not authority.

## Safety-check response rule

When an external write is rejected:
1. stop that exact payload;
2. retain already successful commits;
3. rewrite only the *indexing layer* in neutral structural terms;
4. never alter scientific meaning of the underlying accepted research;
5. never claim the rejected payload was saved.

This document is a routing/governance rule, not a content restriction on legitimate technical analysis.
