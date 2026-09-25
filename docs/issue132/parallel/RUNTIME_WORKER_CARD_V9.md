# Issue132 Runtime Worker Card V9 — flat forward review

Status: ACTIVE when selected by RUNTIME_AUTHORITY.json.

## Purpose

Classify neutral identities for the way an image-generation user would naturally discover the wanted visual concept without knowing the exact Danbooru tag.

Adult/sexual content is a normal supported workflow. Accuracy wins over guessing.

## Fixed inputs

Branch: research/taxonomy-usability-audit
Lane rule: ((review_seq-1)%3)+1
Lane lengths: 1=10335, 2=10334, 3=10334
Neutral and identity-order parent hashes come from RUNTIME_AUTHORITY.json.
Input shards are 300 lane-local rows.
Semantic work block is up to 100 consecutive lane-local identities.
Persistence slice is exactly 25 consecutive lane-local identities (except the final short lane tail).
Per-run ceiling is 300 identities.

The 25-row persistence slice exists only to limit the blast radius of a platform write-policy rejection. It is not a semantic boundary and does not reintroduce checkpoint/promotion.

Read only:
1. RUNTIME_AUTHORITY.json
2. this Worker card
3. the frozen machine-readable semantic vocabulary file named by authority
4. own lane staging + write-request + deferred path metadata
5. exact arithmetic input shard(s) needed for the next range
6. WRITE_REQUEST_PROTOCOL_V1.md

Do not read checkpoint prose, Issue history, Repair prose, Coordinator prose, or current product taxonomy.

## Frontier

Forward frontier is the highest end represented by a canonical staging window, a code-only write request, or a policy-deferred marker in this lane, plus 1. A write request is pending materialization, not accepted semantic progress.

Historical checkpoints are seed data, not a gate.
Historical invalid windows are Repair work and do not move the Worker frontier backward.

Use repository path metadata only to find the highest staging/write-request/deferred end.
If one directory listing fails, one recursive branch-tree metadata fallback is allowed.
Do not spend the run reconstructing global status.

## Work loop

Process up to 300 identities.

For each logical work block, inspect up to 100 identities, but persist completed decisions as consecutive 25-row slices as soon as each slice is ready:
- inspect every identity;
- classify obvious identities directly;
- research only when uncertainty can materially change mode, route, strength, local/body/theme facet, or vocabulary-gap decision;
- batch related research when useful;
- after one bounded useful research pass, unresolved meaning becomes terminal SEMANTIC_UNRESOLVED with RESEARCHED and evidence;
- use a hold only when required research itself could not be completed because of a real tool/platform/evidence interruption.

Persist each completed 25-row slice before carrying more than one additional slice of unsaved decisions. Continue within the same logical 100-row block after a successful write.

A smaller persistence slice is allowed only at lane end.

## Semantic rules

Modes:
- BROWSE_WORTHY
- MIXED
- SEARCH_ORIENTED
- SEMANTIC_UNRESOLVED

For browseable rows:
- choose one strongest natural CORE route;
- SUPPORTING only when it is independently realistic as the user's starting browse shelf;
- local/body/theme facets only when intrinsically entailed;
- vocabulary gap only when the frozen route vocabulary genuinely cannot express an important user mental model.

Hard lint:
- color/pattern adjective alone != COLOR_PATTERN_SHAPE
- placement alone != POSE_POSITION
- action alone != POSE unless body geometry independently matters
- animal/plant motif/print/emblem/likeness != LIVING
- object presence alone != SCENE_BACKGROUND
- sexual content != CONTENT_RATING
- optional facets are not inferred from common association

SEARCH_ORIENTED and SEMANTIC_UNRESOLVED carry no routes/locals/body/theme.

## Output schema

The Worker does NOT write canonical staging directly.

Primary persistence path:
docs/issue132/parallel/lane-N/write-requests/request_SSSSSS_EEEEEE.json

Follow WRITE_REQUEST_PROTOCOL_V1.md exactly. The request contains classification codes and indices only. It MUST NOT copy identity_key, source tag text, source_surfaces, free-form semantic prose, or identity_sha256.

GitHub Actions materializes the canonical file:
docs/issue132/parallel/lane-N/staging/window_SSSSSS_EEEEEE.json

The materializer reconstructs identity_sha256 from the pinned neutral input and validates the frozen vocabulary before producing staging v2.

A normal request contains exactly 25 consecutive lane-local slots except the final short lane tail.

Policy-deferred marker path:
docs/issue132/parallel/lane-N/deferred/deferred_SSSSSS_EEEEEE.json

A policy-deferred marker contains only:
- schema_version = issue132-policy-deferred-v1
- lane
- lane_local_start
- lane_local_end
- reason_code = PLATFORM_WRITE_POLICY_BLOCKED

It MUST NOT contain source identity text, semantic decisions, routes, facets, evidence, or a transformed/encoded copy of rejected content.

Before writing a request, validate:
- exact slot coverage;
- review_seq binding;
- frozen mode/route/strength/facet codes;
- local parent-route consistency;
- researched evidence requirement;
- SEMANTIC_UNRESOLVED constraints.

## Writes

Normal write is one immutable code-only write-request file for one completed 25-slot slice.

Do not send canonical staging bytes through ChatGPT's GitHub write path. GitHub Actions owns canonical materialization.

After request creation succeeds, count the slice as REQUESTED/PENDING_MATERIALIZATION and continue. It becomes accepted semantic progress only after the canonical staging file exists and flat validation accepts it.

If request creation fails for an ordinary transport/concurrency reason, retry only the same code-only request through the authorized non-force Git-object fallback when available.

If the code-only request itself receives an explicit policy/content rejection, do not encode, disguise, fragment, or retransmit it through another transport. Create only the non-semantic policy-deferred range marker and continue later independent slices when that marker succeeds.

If a request already exists for the exact range, do not reclassify it. Treat it as pending materialization unless canonical staging already exists.

The automation remains enabled after write/materialization failures.

## Stop/report

Valid stop:
- 300 identities attempted/persisted as far as safely possible;
- lane complete;
- true frozen-contract/input mismatch;
- both authorized metadata/content acquisition routes unavailable;
- current block cannot be persisted.

Report only:
lane, old frontier, requested/materialized range/count, CHECKED/RESEARCHED/SEMANTIC_UNRESOLVED/holds counts, new frontier, pending materialization, blocker.
