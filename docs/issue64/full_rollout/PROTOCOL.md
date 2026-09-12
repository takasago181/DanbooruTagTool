# Issue #64 full rollout persistence protocol

This directory is the recoverable source for the ChatGPT-led 30,629-row General taxonomy candidate build.

## Authority and scope

- Product/project authority remains the normal project docs and Issue #64.
- This branch contains candidate-build work only. It is not production acceptance.
- Accepted taxonomy basis: Issue #64 pilot revision 2 (`PILOT_ACCEPTED`), commit `5064429018123c80c32ac41af715668fb67fb74e`.
- Do not mutate canonical identity, Japanese overlay, Special data, Issue #34 ranking, Issue #42 UI, or Stage10 while this candidate build is in progress.

## Persistence unit

Each completed batch is immutable after checkpointing and is stored under `batches/` as a row ledger containing canonical + proposed/unresolved + primary/secondary path + confidence.

- Batches 1-4 were persisted before this protocol was finalized; their immutable row ledgers plus MANIFEST row ranges and SHA-256 are the accepted recovery record.
- Batch 5 onward additionally stores a summary JSON with counts, unresolved list, and audit notes.
- Normal storage is one xz-compressed CSV ledger (`*.csv.xz`).
- If connector payload handling makes direct binary persistence impractical, the same xz bytes may be split into ordered base64 text fragments (`*.xz.b64.partNNN`). `MANIFEST.json` must then record fragment order, decoded size/hash, base64-text hash, the reconstructed whole-xz SHA-256, and raw CSV SHA-256.
- To restore a fragmented batch: concatenate the base64 text fragments in listed order, base64-decode once, verify the whole xz SHA-256, decompress xz, then verify the raw CSV SHA-256.
- Do not rewrite an older batch merely to make later logic cleaner. If a semantic correction is needed, record it as a later correction/audit artifact that names the affected canonical rows and preserves traceability.

## Checkpoint files

- `MANIFEST.json` is the machine-readable batch ledger: exact global row ranges, row counts, hashes, storage details, and totals.
- `PROGRESS.md` is the human-readable current stop point and routing note.
- Issue #64 receives milestone comments at meaningful checkpoints so the work itself is discoverable from the project management trail.

A batch is considered persisted when:
1. its immutable row ledger (single xz or complete ordered fragment set) is stored,
2. `MANIFEST.json` includes its exact range and verification hashes,
3. `PROGRESS.md` points through the same final global row,
4. for Batch 5 onward, its summary JSON is also stored.

## Resume procedure for a fresh chat

1. Read `docs/project/CURRENT_STATE.md`.
2. Read Issue #64 latest comments.
3. Read this `PROTOCOL.md`.
4. Read `MANIFEST.json` and `PROGRESS.md`.
5. Confirm the latest persisted global row.
6. Continue from the next row only; do not re-run already persisted rows unless doing an explicit audit/correction pass.

## Classification rules

- Use the accepted 17 top-level genres and max depth 2.
- No visible catch-all.
- Prefer practical beginner discovery over substring matching.
- Prefer the tag's object/concept identity over modifier fragments.
- Preserve pilot-v2 boundaries (role/clothing, sky/light, screen/composition, body/exposure, etc.).
- Ambiguous proper names/events/projects remain `UNRESOLVED` when evidence is insufficient.
- `LOW` confidence is not silently promoted to proposed.
- External evidence is used only where ambiguity materially affects the route; no runtime network dependency is introduced.

## Commit cadence

During rollout, persist every 1,000 classified rows or sooner before any chat handoff/continuity risk.

Do not commit a repeatedly regenerated cumulative CSV on every batch. Immutable batch ledgers + `MANIFEST.json` are the canonical recoverable detail. A combined full sidecar/CSV is generated only at major audit checkpoints or at 30,629/30,629 completion.
