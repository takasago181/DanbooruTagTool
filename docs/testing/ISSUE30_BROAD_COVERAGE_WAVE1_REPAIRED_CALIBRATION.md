# Issue #30 Wave 1 repaired calibration — 2026-09-11

Status: `REPAIRED_FROM_EXISTING_RAW_ARTIFACTS_MACHINE_VS_VISUAL_CALIBRATION_COMPLETE_STOPPED`

The stale per-row evaluator serialization was repaired from the existing image-specific WD14/Kagami/CL raw artifacts. No image was regenerated and no evaluator was rerun.

## Repair

- Rebuilt rows: **64**; raw evaluator artifacts consumed: **192**
- Original stale evaluator locators detected: **189**
- Raw evaluator execution state: **64/64 per evaluator; 192/192 total**
- Image hash binding: **PASS**

## Visual calibration

- Visual verdicts: `{'BOTH_PASS': 22, 'B_ONLY_PASS': 4, 'A_ONLY_PASS': 1, 'BOTH_FAIL': 3, 'UNCLEAR': 2}`
- Machine pair routes: `{'HUMAN_REVIEW_REQUIRED_PAIR': 30, 'MACHINE_HANDLED_PAIR': 2}`
- Machine-handled false-safe: **1/2 (50.0%)**
- Machine-handled precision against `BOTH_PASS`: **50.0%**
- Human-route `BOTH_PASS` diagnostic: **21**; protected subset **18**
- Structural/protected human routes are not called over-routing solely from a `BOTH_PASS` visual result.

## Decision

Machine route remains frozen. This calibration evidence is too small to promote structural/pair-delta semantics to AUTO. Wave 2 and Stage10 production A/B remain unstarted.
