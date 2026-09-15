# Issue #76 buttock/anal site audit v0.3

Status: **DESIGN EVIDENCE / NOT PRODUCTION AUTHORITY**

## Purpose

Resolve the provisional `臀部・肛門` body-site bucket without reintroducing overly fine visible navigation.

The Phase B review queue contained 62 rows whose v1 evidence used the mixed `BODY_ANATOMY>BUTTOCK_ANUS` route. Each row was re-read against the real Special prompt-reference identity and classified internally as `ANAL_RECTAL`, `BUTTOCK`, or `BOTH`.

## Result

- audited rows: 62 / 62
- `ANAL_RECTAL`: 44
- `BUTTOCK`: 17
- `BOTH`: 1
- unresolved after this site audit: 0

The only `BOTH` row is Special ID 1809 `ass spread` (`臀部を開いて肛門周辺を見せる描写`).

## Visible browse decision

**Do not split this into separate permanent `尻` and `肛門・直腸` buttons.**

Use one coarse visible body-site facet:

- internal candidate ID: `BUTTOCK_ANAL`
- Japanese label: `尻・肛門`

Reason:

- the current combined v2 candidate contains 111 memberships;
- 49 were already explicit anal-site routes before this audit;
- the 62 mixed rows resolve to 44 anal/rectal, 17 buttock, 1 both;
- a visible split would therefore create an anal/rectal route of about 94 memberships but a buttock-only route of only about 18 memberships;
- that extra small visible shelf would work against the user's explicit requirement to keep classification coarse and easy to browse.

`直腸` / `アナル` wording remains discoverable through tag identity, Japanese/English search and row metadata. It does not need another permanent visible node.

## Practical examples

- `anal beads` -> `道具・物` + `尻・肛門`
- `butt plug` -> `道具・物` + `尻・肛門`
- `anus` -> `身体・状態` + `尻・肛門`
- `rectum` -> `身体・状態` + `尻・肛門`
- `ass` -> `身体・状態` + `尻・肛門`
- `ass focus` -> `ポーズ・構図・場面` + `尻・肛門`
- `ass cutout` -> `衣服・露出` + `尻・肛門`

The semantic home and body-site browse entrance remain independent.

## Queue reduction

Before this audit, the bounded v2 review queue had 126 rows:

- 43 v1 unresolved
- 21 chastity/control mixed-family rows
- 62 buttock/anal site rows

After this audit, the site rows are resolved and removed from the queue.

Remaining review queue: **64**

- `REVIEW_V1_UNRESOLVED`: 43
- `REVIEW_MIXED_FAMILY` (`CHASTITY_CONTROL`): 21

## Artifacts

- `issue76_buttock_anal_site_audit_v0_3.csv` — exact 62-row audit
- `issue76_v2_site_facet_patch_v0_3.csv` — 111-row provisional-site rename/patch evidence
- `issue76_v2_review_queue_v0_3.csv` — reduced 64-row remaining queue

## Verdict

`BUTTOCK_ANAL_COARSE_FACET_SUPPORTED`

This resolves the original buttock/anus boundary without adding another fine-grained visible browse category.

No production taxonomy, canonical Special data, search ranking or WPF code is changed by this checkpoint.
