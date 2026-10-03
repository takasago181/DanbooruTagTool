# #256 Batch 3 — local LoRA execution provenance

Baseline: `d742c7e5ef26c4a71719f6237a161b9c9d3020e0`, after PR #266 merge.
Merge-main CI passed (run `37113012935`); Batch 2's valid verification was reused.

## Bounded decision and reuse

Batch 1's model hash identity and Batch 2's source-parameter persistence make
LoRA execution identity the next useful dependency for image → Library → Recipe
→ Create → derivative generation. The existing 35-checkpoint reconciliation and
142-row reuse matrix remain the planning basis; no new general survey was run.

Reuse: installed Forge Neo `/sdapi/v1/loras`, PNG `Lora hashes`, safetensors/Kohya
embedded hash conventions, existing DTT token parser/ordered source parameters,
Library parameter storage, and .NET JSON/SHA256/file sharing. No dependency,
external API, Civitai lookup, schema redesign, or copied upstream code was added.
Upstream behavior reference: https://github.com/Haoming02/sd-webui-forge-classic
at installed commit `97b26fb404314a11dad7cdde2706da57ea53f4f2` (network.py,
networks.py, extra_networks_lora.py, lora_script.py, hashes.py).

## Behavior

- Resolve simple Positive `<lora:name:weight>` tokens against Forge name/alias;
  reject missing, ambiguous, duplicate, unsupported dialect or Negative LoRA
  tokens before generation POST. Bound selection to 32 local safetensors files.
- Hold selected local files read-locked through generation; independently compute
  full-file SHA256 and authenticate embedded tensor SHA256 when present. Reject
  stale API metadata and inherited backend/full-file hash mismatches.
- Keep backend 12-character fingerprint distinct from full-file SHA256. Compare
  actual PNG LoRA fingerprints with selected identities, alongside existing
  model/Prompt/recipe checks. Failure retains output and never retries POST.
- On successful comparison only, add a bounded, CRC-checked, unsigned
  `DTT LoRA provenance v1` PNG iTXt receipt with name/backend hash/full-file hash/
  sent weight. Preserve original image chunks, Forge parameters and raw infotext.
- Existing Library and Recipe source parameters persist the receipt. Display the
  inherited identity in Library/Create. Explicit release renames original fields
  as historical evidence and requires derivative consent; Prompt is not rewritten.

An imported legacy PNG can retain only the hashes it contains; missing full-file
identity is shown explicitly. These are local observations plus backend metadata,
not signed provenance, an independent proof of tensor application, model/LoRA
compatibility, or pixel-identical reproduction. Same-name collisions fail closed.

## Final verification

- Clean Release solution build: PASS, 0 warnings/errors.
- Targeted: 133 PASS / 1 existing live opt-in SKIP / 0 FAIL.
- Final local full regression, once: 406 PASS / 25 existing SKIP / 0 FAIL.
- Isolated real WPF: PASS at widths 900/1400; identity display and explicit
  derivative controls rendered. Live generation used current Create command.
- Real Forge already running: two generation POSTs, model `f116b0c78f`, selected
  `AddMicroDetails_Illustrious_v7`, weights 0.35 → 0.45, seeds
  25420261005 → 25420261006, Euler/Karras, steps 8, CFG 4.75, 512×640.
  Sent payloads, PNG model/LoRA hashes/conditions, separate receipt, isolated
  Library save, raw-infotext readback, preset restart/restoration and derivative
  identity continuity: PASS. Wrong full-file pin rejected before another POST.
- LoRA backend `f80f73e9687d`; authenticated embedded tensor hash
  `f80f73e9687d4fed45475377f0ff0b9bf385e5c87c8fb47eb63523eec5834996`;
  full-file SHA256
  `ea7c78d35d465961cda9b9b99b25c1403192204712e391bcb8d6dd014bda9e67`.
- Production file inventory unchanged; all 21 protected files byte-identical
  (5 managed runtime + 14 real UserData + 2 Forge settings). Forge left running.
  This snapshot/result is reused after source/docs-only work; no production applied.
- Local evidence: `_local/task-artifacts/issue256-batch3` (TRX, real sent payloads,
  isolated images/DB, WPF screenshots, before/after protection evidence).
  PR CI result and final commit are recorded in the live Issue checkpoint.

## Schema, rollback and stop

No new migration: UserState schema 4, Library schema 1 and LoRA inventory schema 1
remain unchanged. Reverting this bounded source change restores the previous DEV
implementation; receipt source parameters remain historical evidence.

**Future production gate retained:** before applying Batch 2's schema 2 → 4
migration, back up real UserData and databases. Returning to an older runtime
after migration requires that matching pre-migration backup; source/runtime revert
alone is insufficient. This Batch neither migrates nor publishes production.

Batch 4 may be selected after this PR review; it is not started. No #230/#231,
ComfyUI expansion, full Model Profiles, semantic authority or Foundation changes.
