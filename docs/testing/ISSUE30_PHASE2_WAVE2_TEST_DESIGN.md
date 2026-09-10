# Issue #30 Phase 2 Wave 2 test design — 2026-09-10

## RESULT

Wave 2 is bounded to two comparisons and eight new images: two fixed seeds for each A/B pair. `MULTI_SPECIAL_RETENTION` is deferred because Wave 1 did not provide clean compatible relation evidence; adding it now would weaken causal interpretation.

## EVIDENCE

| ID | Priority | Selected Specials | A/B variable | Seeds | New images |
|---|---|---|---|---:|---:|
| P2-004 | EXACT_COUNT_RETENTION | 275 `double dildo`, 269 `dildo` | count-/shape-specific tag vs broader object tag | 42001, 42002 | 4 |
| P2-005 | CANONICAL_VS_ALIAS_OR_ALTERNATE_TRIGGER | 147 `anal`, 1286 `anal penetration` (alias → `anal`) | canonical surface vs legitimate alias surface | 42011, 42012 | 4 |

All settings are fixed: Forge Neo, WAI Illustrious v17, Euler a, Automatic schedule, 25 steps, CFG 5, 1024×1344, Hires OFF, ADetailer OFF, LoRA/ControlNet/regional/Couple OFF. Only the declared Positive token changes between A and B. Negative Prompt remains the same baseline.

### Review plan

- Expected review: 4 pairs / 8 images.
- Review answer: `A / B / both / neither / tie / unclear`.
- Human review remains authoritative for exact count, body-site, binding, and relation semantics.
- Evaluators are assistive triage only.

## DECISION

Use real current Special IDs only. Keep canonical dictionary identity (`147 anal`) separate from alias trigger (`1286 anal penetration`); no alias is promoted or rewritten. Do not reuse Wave 1 images as Wave 2 new images.

## LIMITATION

The exact-count comparison is a proxy for count-/shape-specific retention: `double dildo` names a two-ended object rather than guaranteeing two visible instances. A/B outcomes therefore require human review and do not authorize automatic promotion. Multi-Special retention remains unanswered.

## NEXT

Run the fixed manifest after prerequisite checks, screen the bounded results, create the bilingual contact sheet, and stop for DEV/ChatGPT review without adding seeds or starting Stage 10 production A/B.
