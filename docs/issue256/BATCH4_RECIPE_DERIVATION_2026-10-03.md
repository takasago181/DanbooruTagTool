# #256 Batch 4 — explicit Recipe parent and changed fields

Baseline: `917b04ba2a10ec7d16406d82d6eb1bf1fa4faa5d`, PR #267 merge.
Existing Batch 3 full/Forge/WPF/PR-CI evidence reused. Merge-main CI run
`37115016075` initially failed only the existing Issue80 timeout wall-clock gate
(6.3s vs 5s). That single local test passed; one failed-job retry succeeded.
No unrelated product or timeout-test code was changed.

## Decision and reuse

One direct parent Recipe snapshot plus machine-readable changed fields is the
next dependency after model identity, restoration fidelity and LoRA provenance.
This supports future #230 comparisons without beginning Experiment Lab, batch
generation, rankings, graphs or version-control UI. Existing 35-checkpoint
reconciliation and 142-row adoption matrix remain the inputs; no repeated survey.

Reuse `GenerationRecipe`, ordered source parameters, `MetadataDifference` rows,
current Prompt workspaces, Library storage/readers (PNG/JPEG/WebP), SQLite,
.NET JSON/SHA256 and Forge's existing one-POST/actual-PNG verification. Extend
Batch 3's bounded CRC-checked iTXt transport with a second named receipt rather
than duplicate a PNG writer or add a dependency/external service.

## Representation and behavior

`DTT Recipe derivation v1` is a bounded unsigned source-parameter/PNG iTXt record:

- `ParentId`: SHA256 of the v1 serialized P/N/Recipe snapshot, including ordered
  source evidence; distinct from model/LoRA hashes and image content hash.
- Optional `ParentImageSha256` and human-readable source label. Explicit image
  restoration re-reads metadata under a read lock, rejects stale Library evidence,
  and hashes the image bytes. Old presets can provide a Recipe parent without
  inventing an image identity.
- `Parent` and `Requested`: P/N plus existing typed Recipe snapshots, with prior
  derivation records removed. No recursive ancestry is embedded.
- `Changes`: field/before/after/state rows recomputed from those snapshots.

Track Positive, Negative, Model/hash, fixed Seed, Steps, Sampler, Scheduler, CFG,
Width/Height, simple LoRA additions/removals/weights, and source evidence changes
(including explicit inherited LoRA constraint release). Hires/RNG/other unsupported
fields remain evidence, marked **not sent**, never executable arbitrary overrides.
Such omissions remain distinguishable even when no editable condition changed.

Create displays parent identity and before/after values alongside the existing
source/dirty indicator. Structural snapshot comparison replaces reference equality
for dirty state. Undoing a change clears dirty state; saving clears unsaved dirty
state but retains the original parent/diff. Preset restart also retains that edge.
The current snapshot is captured before await; stale or contradictory receipt
data is rejected before any network request.

Only after actual Forge metadata checks pass is the derivation receipt attached
to the new output. Original Forge raw infotext/parameters/image chunks remain
unchanged. Returned mismatches retain output without attaching a successful edge
or retrying POST. PNG import checks receipt CRC, bounds, parent identity/diff
integrity and requested P/N/typed/hash consistency against actual metadata.

Library persists/displays the edge using its existing parameter table. Loading
that output into Create makes the output itself the next direct parent, rather
than appending a graph or nesting the previous receipt. Unsigned records are local
observations; they do not certify pixel equality or independent tensor application.
Advanced LoRA syntax and unsupported generation conditions retain prior guards.

## Verification

- Clean Release build: PASS, 0 warnings/errors.
- Final relevant targeted tests: 125 PASS / 1 existing live opt-in SKIP / 0 FAIL.
- Final local full regression once: 419 PASS / 25 existing SKIP / 0 FAIL.
- Isolated actual WPF: widths 900/1400 PASS; inspected parent/hash, Seed42→43,
  not-sent conditions and modified-state rendering. No Computer Use needed.
- Real Forge already running: **one** generation POST through current Library /
  Create command. Reused Batch 3's isolated blue-teapot PNG as parent instead of
  generating another baseline. Green-teapot Positive, changed Negative, fixed
  Seed25420261008, Steps6, CFG5 and LoRA weight0.4 generated at 512×640, Euler /
  Karras with model hash `f116b0c78f`. LoRA backend `f80f73e9687d` and full-file
  identity remained intact. Parent/diff, actual PNG, isolated Library raw/receipt
  readback, preset restart and next-parent Create restoration all PASS.
- The smoke helper initially compared CFG's textual `5.0` with `5`. Corrected to
  numeric comparison and completed readback using the already successful output;
  **zero additional POSTs**. The receipt retains the requested snapshot. Raw HTTP
  payload logging was not recovered after that helper exit; evidence uses current
  adapter checks, the stored requested snapshot and actual PNG. No fabricated wire
  capture or duplicate generation was added.
- Production inventory unchanged; all21 protected files byte-identical (5 managed
  runtime, 14 actual UserData, 2 Forge settings). No production apply; Forge left
  running. Reuse that result after source/docs-only closeout.
- Local evidence: `_local/task-artifacts/issue256-batch4` (TRX, isolated source /
  output / DB, receipt/result.json, WPF renders, protection snapshots). Exact PR
  commit and CI result are recorded in the live Issue checkpoint.

## Schema, rollback and STOP

No new schema or migration: DEV UserState4 / Library1 / LoRA inventory1 unchanged.
Older schema4 runtimes retain this receipt as unknown source evidence and block
unconsented execution rather than applying it as backend settings. Revert this
source change to return to Batch 3; unsigned receipt fields remain data evidence.

**Future production gate retained:** back up real UserData/DB before Batch 2's
schema2→4 promotion. Older-runtime rollback after that migration requires the
matching pre-migration backup; runtime/source revert alone is insufficient.
Real production remains Foundation `ad14d45f` with its existing LKG/schema2.

STOP at Batch 4 PR and CI. Batch 5 may be selected after review; it is not started.
No #230/#231, production promotion, Foundation redesign or semantic authority change.
