# Issue132 Write Request Protocol V1

Status: ACTIVE persistence transport for Flat Pass-A Workers.

## Why this exists

A Worker may be able to complete a legitimate research classification but have a direct repository write rejected by an upstream platform safety layer because the source identity is sensitive.

The persistence path therefore follows data minimization:
- the Worker writes only the minimum classification codes needed to represent the research result;
- source identity text is never copied into the write request;
- GitHub Actions, inside the repository, joins the request to the already-pinned neutral input and materializes the canonical staging v2 file.

This is not an alternate semantic engine. It does not change or hide the classification. It only removes unnecessary source text from the ChatGPT -> GitHub write payload.

## Paths

Worker request:
docs/issue132/parallel/lane-N/write-requests/request_SSSSSS_EEEEEE.json

Materialized canonical output:
docs/issue132/parallel/lane-N/staging/window_SSSSSS_EEEEEE.json

## Request schema

schema_version = issue132-pass-a-write-request-v1

Top-level:
- schema_version
- lane
- lane_local_start
- lane_local_end
- parent_neutral_sha256
- parent_identity_order_sha256
- rows
- holds

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

The request MUST NOT contain:
- identity_key
- identity_sha256
- source_surfaces
- copied source tag text
- free-form semantic prose

The materializer derives identity_sha256 from the pinned neutral input.

## Semantics

The Worker must make the same semantic decision as Worker V9.
The request is not accepted Pass-A output by itself.
Only the materialized canonical staging file counts as accepted output after flat validation.

## Policy-sensitive writes

If a normal code-only request with required evidence URLs is explicitly rejected by the platform, do not encode, disguise, fragment, or retransmit the rejected content through another route.

A non-semantic deferred marker may be written so the range is not silently lost.

## Idempotence

A request path is immutable.
A materialized staging path is immutable.
The materializer skips an already existing canonical staging path.
