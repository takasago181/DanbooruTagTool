# BATCH_AQ — Regional learning and reproducibility — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: official regional-control audit + practical study-method synthesis
Scope: Anima / Forge Neo / ComfyUI / multi-subject learning

## 1. Regional text is not Region LoRA

Official Regional Prompter:
https://github.com/hako-mikan/sd-webui-regional-prompter

2026-09-04 support table:
- Anima Latent: supported
- Anima Attention: supported
- Anima Region LoRA: not supported

Reason documented by the project:
the Region LoRA path expects U-Net-style block names and finds no matching targets on Anima.

Practical consequence:
A learner must not conclude:
`regional prompt works -> character LoRA is isolated by region`.

These are different mechanisms.

Promoted:
- K-TOOL-030.

## 2. Anima regional attention mechanics

Same official project explains that for Anima:
- regional prompts are encoded separately;
- cross-attention is blocked/routed by region;
- self-attention is only softly penalized rather than fully closed;
- masking applies primarily in the early part of the sampling schedule;
- later unmasked sampling helps knit the regions into one coherent image.

This follows the ComfyUI Anima Regional Conditioning implementation.

Learning point:
Regional conditioning is not just spatial prompt cropping.
It changes information routing during diffusion.

## 3. Too much separation can break interaction

Official ComfyUI Anima Regional Conditioning:
https://github.com/Sen-sou/Comfyui-Anima-Regional-Conditioning

Current limitations explicitly warn:
- strong self-mask values can create hard region edges;
- regions can lose awareness of each other;
- interactions can become unnatural;
- base/background conditioning and some unpatched global output help coherence.

For adult relation-heavy scenes, this is crucial.

A regional setup can:
- solve identity contamination;
- yet worsen physical interaction.

Promoted:
- K-TOOL-031
- K-PRACTICAL-020.

## 4. Learn regional control in layers

Recommended study ladder:

R0 — plain Prompt
R1 — subject-specific text, no regions
R2 — regional text/attention
R3 — regional text + pose/depth
R4 — separate adapter localization when supported
R5 — per-subject inpaint/reconstruction

At each stage score:
- identity separation
- attribute ownership
- relation
- boundary artifacts
- scene coherence.

Do not jump from R0 directly to a large opaque workflow.

## 5. Adapter localization is a separate lane

If Region LoRA is unavailable for the exact model/runtime:
- use regional text to separate semantic conditioning;
- use masked/scheduled LoRA hooks where supported;
- or generate/reconstruct subjects individually;
- or use inpaint with the relevant character adapter.

This preserves the distinction:
`regional text success`
versus
`regional adapter success`.

Promoted:
- K-PRACTICAL-019.

## 6. Directional language is not ownership

Anima discussion:
https://huggingface.co/circlestone-labs/Anima/discussions/99

User reports:
- “left/right” can be interpreted as frame-relative or subject-relative;
- left/right hand actions vary across seeds;
- directional view descriptions can invert.

Practical lesson:
For hard scenes do not rely on directional words alone to establish:
- body-part owner
- actor/target
- topology.

Use:
- stable subject IDs;
- explicit visible relation;
- pose/reference/control when exact geometry matters.

Promoted:
- K-COMM-ANIMA-025.

## 7. Reproducible images as study artifacts

Official ComfyUI source:
https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_api/latest/_ui.py

SaveImage metadata can include:
- prompt graph data
- extra workflow metadata

Official examples:
https://github.com/comfyanonymous/ComfyUI_examples

Example images are intentionally reloadable into ComfyUI because workflow metadata is embedded.

Practical learning rule:
When doing controlled study, preserve the original PNG with metadata.

Promoted:
- K-EVID-005.

## 8. Evidence hierarchy for shared images

Best:
1. original PNG with embedded workflow/parameters
2. published workflow JSON + exact model/resource list
3. screenshot/text metadata from creator
4. creator description without files
5. VLM/image reverse engineering

A VLM can help describe structure, but it cannot recover hidden generation provenance reliably.

Promoted:
- K-PRACTICAL-021.

## 9. Use two notebooks

### Experiment notebook
Stores:
- exact reproducible settings
- original PNG/workflow
- hypothesis
- result

### Visual failure atlas
Stores:
- representative failure image
- failure label
- likely layer
- known fixes tested

Do not replace the experiment notebook with a folder of favorites.

## 10. Adult multi-subject exercise

For clearly adult subjects, choose one relation-heavy reference.

Run:
A. relation-only minimal prompt
B. A + character identities
C. B + character LoRAs globally
D. B + regional text
E. D + geometry control if needed
F. per-subject reconstruction only if residual failures remain

Score:
- count
- identity
- role/ownership
- contact/relation
- visibility
- region coherence
- anatomy.

The purpose is to identify the first stage where failure appears.

## Promotion result

New ACCEPTED:
- K-TOOL-030
- K-TOOL-031
- K-PRACTICAL-019
- K-PRACTICAL-020
- K-EVID-005
- K-PRACTICAL-021

New CANDIDATE:
- K-COMM-ANIMA-025
