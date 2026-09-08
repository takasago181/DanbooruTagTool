# Hard Adult Challenge v1 — Amendment 01

Status: FROZEN QUARANTINE ASSET CORRECTION
Parent: Issue #41
Trigger: first real Codex execution at `3e8c282d91f2470363da7f25e5fb2cfcb2899903`

## Defect discovered

The frozen ambiguity probe `HAP-003` (`アナル`) correctly requires a non-singleton result set containing at minimum:

- `anus`
- `anal`
- `anal fingering`
- `anal object insertion`

However the v1 64-row canonical challenge asset omitted `anal object insertion`, causing the deterministic design validator to fail before the ambiguity behavior itself could be evaluated.

This was an asset referential-integrity defect, not evidence that the probe requirement was too strict.

## Source-of-truth confirmation

`anal object insertion` is an existing Special2788 Core canonical:

- Special ID: 149
- canonical: `anal object insertion`
- Japanese source gloss: `肛門への物体挿入`
- Layer: `C`
- reference count: 19986
- source: `data/special2788/prompt_reference/04_性行為・性的刺激.txt`

Issue #32 has also independently covered Special ID149 and currently records a quarantined generation-metadata FIX candidate (`ImplementRequirementOverride=true`). That #32 generation-side finding is not used here as Japanese semantic authority; it only reinforces that this canonical is an active first-class Special identity that should not be omitted from this collision test.

## Correction

Keep the challenge fixed at exactly 64 canonical rows and preserve all stratum quotas.

Replace only `HAC-009`:

- old: `masturbation` / Special ID88 / MEDIUM
- new: `anal object insertion` / Special ID149 / CRITICAL

The new row remains in the `SEXUAL_ACTION` stratum so the fixed quota remains 10.

Collision axes:
- `BODY_SITE_BINDING`
- `OBJECT_ACTION`
- `SIBLING_COLLISION`

No ambiguity probe wording or expected behavior is weakened.

## Why replacement instead of adding row 65

The challenge is a compact stress slice, not coverage of every adult Special. `masturbation` is a useful but comparatively low-collision control already represented elsewhere in project history, whereas `anal object insertion` is required to test the exact body-site/action/subtype collision that HAP-003 was designed for.

Keeping 64 rows preserves deterministic asset-size and stratum contracts.

## Boundaries

This amendment does not:
- change fresh100 membership or ordinals;
- change production `data/**`;
- alter #32 verdicts or validation assets;
- alter search ranking;
- alter #35 UI or `CURRENT_DEV_TASK.md`;
- start Stage10 production A/B;
- narrow the overall automation to adult tags.

Hard Adult remains an additional stress Gate on top of the general dictionary-wide UI-JA/R3 automation.
