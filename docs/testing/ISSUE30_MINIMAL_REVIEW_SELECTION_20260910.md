# Issue #30 — Minimal human review selection

## Scope

This is a non-production follow-up to the 128-image screening pilot. It does not generate images, rerun WD14/Kagami/CL, change `data/**`, alter #32 or canonical data, or start Stage10 A/B.

The source is the local pilot run `issue30_pilot_20260910`. The per-row evaluator artifact pointers in `calibration_results.json` were inconsistent for 127/128 rows. The selection tool therefore addressed the already-existing raw files directly by `image_id`; it did not treat the inconsistent pointers as evidence and did not rerun evaluators.

## Reduction

- Current human-review queue: 58 images.
- Minimal set: 19 images.
- Selected from the current queue: 18 images.
- Additional mandatory HIGH candidate: 1 image, `CAL-001__target_present_seed_b`, which was outside the 58-image queue.
- Deferred within the current queue: 40 images.

The minimal set is a review priority, not a new ground-truth dataset. Unreviewed images remain `NOT_REVIEWED`.

## Review order

1. The single `HIGH_CONFIDENCE_AUTO_LIKELY` image.
2. Three nearest non-relation AUTO candidates.
3. Two disagreement-pattern representatives.
4. Two threshold-boundary representatives.
5. Two blocked/rare-tail controls.
6. One non-relation component-only proxy control.
7. Eight relation/binding safety anchors covering relation, actor/subject/object, body-site/insertion, quantity, spatial, compound, restraint, and component-binding risk.

The machine score, vote, screening class, and route must be hidden while the image judgment is made. The ordered blinded contact sheet is written to the local pilot `review_queue` directory. The review manifest contains the order and image path for an existing viewer.

## Early-stop rule

Stop the AUTO-focused review and mark `AUTO_CALIBRATION_HOLD` if any of these occurs in review orders 1–4:

- the mandatory HIGH candidate is a clear human false positive;
- two false positives are found among the first four AUTO-viability candidates; or
- a non-relation simple class has two clear human-negative images despite unanimous positive evaluator votes.

When early stop fires, do not open deferred redundant images. Keep relation/binding classes `HUMAN_REVIEW_ONLY`; this pilot cannot promote them to AUTO. A clean first block does not promote production AUTO. It only leaves the represented class as a candidate for a separately approved targeted validation.

## Minimal label input

For every opened image, record `yes`, `no`, or `unclear` for target presence, unwanted extra interpretation, and Stage10 preference usability. For relation/binding rows, also record only the applicable dimensions: actor/subject, target/object, body-part ownership/site, count, spatial relation, compound retention, and insertion/contact/restraint correctness. Use `UNRESOLVED` when an unclear judgment is not resolved. Exclude `UNRESOLVED` from threshold fitting and AUTO promotion.

## Why the other 40 are deferred

The mapping CSV retains every current queue row. Deferred rows are not silently passed. They are omitted because they repeat a capability, agreement pattern, threshold band, blocked/rare-tail failure, or relation dimension already represented by a higher-information row. They can be reopened only if the selected row for that same pattern produces a false positive, unresolved judgment, or a new evaluator-specific failure pattern.

## Files

- `ISSUE30_MINIMAL_REVIEW_MANIFEST_20260910.csv`: 19 ordered review rows.
- `ISSUE30_REVIEW_QUEUE_MAPPING_20260910.csv`: all 58 current queue rows and their selected/deferred status.
- `ISSUE30_MINIMAL_REVIEW_INPUT_SCHEMA_20260910.json`: machine-readable minimal human-label format.
- `ISSUE30_MINIMAL_REVIEW_SELECTION_SUMMARY_20260910.json`: counts, early-stop rule, and audit note.

This selection is evidence triage only. It does not establish precision/recall and does not authorize Stage10 production use.
