# Issue132 Write Request Protocol V2

Status: **ACTIVE for new Codex forward review after the manual-audit boundary**

Historical `issue132-pass-a-write-request-v1` requests remain readable. New forward work beginning at:
- Lane 1: 1126+
- Lane 2: 1226+
- Lane 3: 1201+

must use V2.

## Why V2 exists

V2 keeps the existing code-only/data-minimized transport, and adds enough audit metadata to answer:
- which semantic-policy version produced the decision;
- which short reasoning family was used;
- whether a later policy change should trigger targeted QA.

It does not add or change taxonomy vocabulary.

## Paths

Worker request:
`docs/issue132/parallel/lane-N/write-requests/request_SSSSSS_EEEEEE.json`

Materialized canonical output:
`docs/issue132/parallel/lane-N/staging/window_SSSSSS_EEEEEE.json`

## Request schema

`schema_version = issue132-pass-a-write-request-v2`

Top-level fields:
- schema_version
- lane
- lane_local_start
- lane_local_end
- parent_neutral_sha256
- parent_identity_order_sha256
- semantic_policy_id
- semantic_policy_git_blob_sha
- decision_reason_codes
- rows
- holds

`semantic_policy_id` and `semantic_policy_git_blob_sha` must match an allowed policy entry in live `RUNTIME_AUTHORITY.json`.

`decision_reason_codes` is an object:
- key: decimal lane-local index as a string;
- value: non-empty array of allowed short reason codes from live authority.

It must cover every semantic row in the request exactly once.
Operational hold slots do not receive decision reason codes.

Each row contains exactly:
- lane_local_index
- review_seq
- discovery_mode
- routes
- local_refinement_ids
- body_site_ids
- theme_ids
- route_vocabulary_gap
- review_depth
- evidence_urls

Each hold contains exactly:
- lane_local_index
- review_seq
- reason_code
- research_attempt_codes

## Data-minimization rule

The request MUST NOT contain:
- identity_key;
- identity_sha256;
- source_surfaces;
- copied source tag text;
- free-form semantic prose;
- an encoded/transformed copy of prohibited source text.

GitHub Actions joins indices to the pinned neutral input and derives identity_sha256.

## Semantics

The Worker follows:
1. the frozen semantic vocabulary;
2. current Worker card;
3. current allowed Codex semantic-guardrail policy.

Reason codes are audit trace only. They never substitute for the actual semantic review.

## QA watermarks

Before creating a request, the Worker must read `CODEX_QA_STATE.json`.

The request's `lane_local_end` must not exceed that lane's current `allowed_forward_end_by_lane`.

This caps the number of un-QA'd new decisions.

## Persistence-debt gate

Before starting another slice, count for the lane:
- slots in write requests with no canonical staging yet;
- slots in policy-deferred ranges.

If unresolved persistence debt is already at the live authority limit, or the next slice would exceed it, do not create more forward semantic work. Stop that lane and surface the debt to CODEX-REPAIR / ChatGPT QA.

## Policy-sensitive writes

If a valid V2 code-only request is explicitly rejected by the platform:
- do not encode, disguise, fragment, or retransmit the rejected content;
- write only the permitted non-semantic deferred marker if possible;
- count that range against persistence debt.

## Idempotence

Request paths are immutable.
Materialized staging paths are immutable.
The materializer may re-check an existing request but never silently replace a different canonical staging file.
