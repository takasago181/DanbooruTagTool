# Issue #30 Broad Coverage Wave 1 design

Date: 2026-09-11  
Status: machine-first generation and routing complete; stopped for full ChatGPT visual audit.

## Scope

Wave 1 is bounded to 16 independent experiments and 64 generated images: target-present/contrast A/B for two fixed seeds per experiment. The adaptive budget remains 12–20 experiments and 48–80 images; no additional experiments or blind extra seeds are started after this bounded run.

The manifest covers direct unary, body-site/state, object/tool, pose/composition, relation/binding, multi-person/count, multi-special, nonhuman/unusual, reproductive/body-state, and scene/context strata. Every row has structured `target_prompt`, `contrast_prompt`, `cell_type`, `special_ids`, and an explicit adult-only subject wording.

## Frozen generation profile

- Model route: the already preflight-verified Forge Neo API.
- Sampler: Euler a.
- Steps / CFG: 25 / 5.
- Resolution: 1024×1344.
- Seeds: 51001–51152, fixed in the manifest; two seeds per experiment and no automatic reseeding.
- Source dictionary/profile: read-only local protected input; no source, derived, or runtime data was overwritten.

## Machine-first route and audit package

After generation, every valid image is checked for readability and source hash binding, then WD14, Kagami, and CL artifacts are checked. A/B markers are derived only from structured `cell_type`; pair routes are derived from the two actual image routes. The route is frozen before visual review:

- 192 evaluator runs succeeded: WD14 64, Kagami 64, CL 64.
- 64/64 images and 32/32 pairs are packaged for visual audit.
- The original pilot report contained stale evaluator locators for some rows. Because the expected raw artifacts were present, readable, and bound to the image IDs, the exporter repaired only those report locators in memory and records the original mismatch count and repair count. Missing or unreadable raw artifacts remain fail-closed.
- Final package includes 64 individual image copies, eight four-pair sheets, a complete JSON index, and an ownership manifest.

The package is intentionally stopped at `STOP_FOR_CHATGPT_VISUAL_AUDIT`. Visual verdicts are pending, and Wave 2 is not started.
