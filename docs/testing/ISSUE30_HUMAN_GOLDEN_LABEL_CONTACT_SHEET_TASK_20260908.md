# Issue #30 blinded human golden-label contact-sheet task — 2026-09-08

## Purpose

Prepare the smallest possible human-review surface for the already-generated Issue #30 golden set.

This task must not regenerate images, rerun Forge/WD14, infer labels, evaluate thresholds, or start Stage10 production. It only turns the existing 16 local PNGs into a blinded visual review artifact so the user can provide 8 independent labels with minimal effort.

## Verified input

Evidence branch:
- `codex/issue30-automation-dry-run-20260908`

Accepted golden-set evidence commit:
- `33215269cfeb33b3afab0c36a6a8bd52cb55952e`

Status:
- `WAITING_HUMAN_GOLDEN_LABELS`
- 4 experiments × 2 seeds = 8 A/B comparisons / 16 images
- metadata 16/16
- WD14 raw 16/16
- target coverage 100%
- threshold grid not run

Existing local evidence directory is recorded in the golden-set JSON/report. Reuse those exact PNGs and verify their SHA-256 against the accepted report before composing the review artifact.

## Hard boundaries

Do not:
- regenerate any image
- call `/sdapi/v1/txt2img`
- rerun WD14
- show WD14 confidence values in the blinded review artifact
- show which side's Prompt explicitly contains the target tag
- infer or prefill a human label
- modify the accepted PNGs
- update Forge Neo/extensions/dependencies
- switch model/checkpoint
- run threshold/margin grid
- create production scoring
- edit `CURRENT_DEV_TASK.md`, Issue #35-owned files, `data/**`, or `validation_quarantine/**`

## Required visual artifact

Create **two PNG contact sheets**, 4 comparisons per sheet, to remain readable on a phone.

Suggested names:
- `golden_set_contact_sheet_1.png` — G1 and G2 (both seeds)
- `golden_set_contact_sheet_2.png` — G3 and G4 (both seeds)

Each comparison row must show:
- experiment ID
- target concept
- seed
- A image on the left, clearly labeled `A`
- B image on the right, clearly labeled `B`
- no WD14 values
- no side-specific Prompt text
- no expected-side hint
- no machine recommendation

Preserve image aspect ratio. Use sufficiently large thumbnails that pose / hair / expression differences remain visually judgeable. Avoid lossy recompression when practical; PNG output is preferred.

Target concepts:
- G1: `standing`
- G2: `sitting`
- G3: `long_hair`
- G4: `smile`

Seeds:
- `5072`
- `17027`

## Label template

Also create a tiny text/JSON label template with exactly these 8 keys and null labels:

- `G1-5072`
- `G1-17027`
- `G2-5072`
- `G2-17027`
- `G3-5072`
- `G3-17027`
- `G4-5072`
- `G4-17027`

Allowed labels only:
- `A`
- `B`
- `TIE/UNCLEAR`
- `INVALID`

Do not fill any label automatically.

## Evidence / completion report

Record:
- contact-sheet local paths
- contact-sheet SHA-256 values
- exact source PNG path/hash mapping for each row
- confirmation accepted source PNG hashes matched before composition
- label-template path/hash
- changed repository files, if any
- final status: `WAITING_HUMAN_GOLDEN_LABELS`

Do not commit generated contact-sheet PNGs into the repository unless they are already small and repository policy explicitly allows it; local evidence paths + hashes are sufficient. Repository changes should remain evidence/docs only.

The user-facing review order must be exactly:
1. G1-5072 — standing
2. G1-17027 — standing
3. G2-5072 — sitting
4. G2-17027 — sitting
5. G3-5072 — long_hair
6. G3-17027 — long_hair
7. G4-5072 — smile
8. G4-17027 — smile

After the contact sheets exist, stop. Do not run threshold exploration until all 8 human labels are supplied.