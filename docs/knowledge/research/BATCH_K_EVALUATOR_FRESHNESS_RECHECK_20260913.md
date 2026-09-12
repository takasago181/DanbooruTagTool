# Batch K — Evaluator Source Freshness Recheck

Owner: Issue #44 `KNOWLEDGE:#44`
Date: 2026-09-13
Status: `K-RB-12_EVALUATOR_REFRESH_COMPLETE`

This completes the evaluator portion of K-RB-12. It does not perform project calibration or promote any evaluator to relation ground truth.

## WD EVA02-Large Tagger v3

Current official model card:
- https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3

Current card remains reachable and states support for:
- ratings
- characters
- general tags

Current model config exposes 10,861 output classes.

Project interpretation unchanged:
- useful common/unary side signal;
- vocabulary/coverage limits remain real;
- missing output is not proof of generation failure;
- not accepted as sole relation/body-site/topology/count ground truth.

## Kagami-24k

Current model card:
- https://huggingface.co/Redstonexs/kagami-24k

Current card describes:
- EVA02-L Danbooru tagger
- 24,000-tag General vocabulary
- evaluation against newer held-out posts and ranking-metric comparisons

Project interpretation unchanged:
- wider General vocabulary is valuable for coverage hypotheses;
- model-card benchmark claims do not by themselves establish rare-Special accuracy, calibration for this project, or actor-target/relation correctness;
- remains a candidate evaluator requiring project-specific calibration if reused.

## CL Tagger v2

Current official model card:
- https://huggingface.co/cella110n/cl_tagger_v2

Important freshness change:
- stable: `v2.00`, released 2026-06-14
- latest current release: `v2_01a`, provisional, released 2026-06-18
- model card explicitly says provisional versions with a trailing letter may be updated in place under the same version name
- current `v2_01a` vocabulary is 108,036 outputs according to the card
- card exposes per-tag calibration/threshold information as part of its model specification

Project consequence:
- `CL Tagger v2` is too broad an evidence identity for promotion-critical work;
- record at least stable/provisional sub-version, retrieval date, and ideally artifact identity/hash;
- `v2_01a` cannot be treated as immutable merely from its version label;
- broad vocabulary and per-tag calibration remain useful, but relation/topology judgement is still not established as ground truth.

## Freshness verdict

- WD EVA02 v3: `SOURCE_RECHECK_20260913_PASS`, project calibration unchanged/pending where applicable.
- Kagami-24k: `SOURCE_RECHECK_20260913_PASS`, candidate status unchanged.
- CL Tagger v2: `SOURCE_RECHECK_20260913_PASS_WITH_VERSION_WARNING`; latest provisional version materially strengthens the need to pin exact evaluator identity.

No existing HOLD about evaluator coverage/calibration is closed by this source refresh.
