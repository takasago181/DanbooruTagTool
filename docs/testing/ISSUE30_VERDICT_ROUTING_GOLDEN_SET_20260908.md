# Issue #30 verdict-routing golden-set dry run — 2026-09-08

Status: `WAITING_HUMAN_GOLDEN_LABELS`

This is a non-production Stage10-prep evidence run. The existing `PASS_PIPELINE` checkpoint `f2fc7acb15f996630c9f008284d80cf3261fb32f` is retained in history. No Stage10 production A/B, winner/scoring decision, model switch, `/sdapi/v1/options` POST, Agent Scheduler, or production scoring was performed.

## Run and infrastructure

- Evidence branch: `codex/issue30-automation-dry-run-20260908`
- Forge API: `http://127.0.0.1:7861`, existing API process PID `36452`; no stop/restart
- Model: `waiIllustriousSDXL_v170`, checkpoint hash `f116b0c78ff441467b0cdc8f1936e1ed18ea31e9997c7b132b1b8db533f0bd04`
- WD14: `wd14-eva02.v3.large`, threshold `0.0`
- Fixed seeds: `5072`, `17027`
- Fixed settings: 24 steps, CFG 4.5, Euler a, Automatic scheduler, 1024x1024, batch 1, iteration 1, no LoRA
- Negative prompt: `lowres, blurry, bad anatomy, text, watermark`
- Manual operation count: `0`
- Infrastructure verdict: `PASS_PIPELINE`

## Automated results

- Experiments: 4 (`standing`, `sitting`, `long_hair`, `smile`)
- A/B comparisons: 8
- Generated PNGs: 16/16
- PNG actual metadata via `/sdapi/v1/png-info`: 16/16 complete
- WD14 raw POST results: 16/16 saved
- WD14 target vocabulary coverage: 16/16 records covered (100%)
- Human golden labels available: 0/8
- Threshold grid: not run; it is prohibited until labels exist
- Candidate routes for the 8 real comparisons: `WAITING_HUMAN_GOLDEN_LABELS`

The generated pair records, PNG SHA-256, PNG-info SHA-256, WD14 raw SHA-256, exact actual Prompt/metadata, and target confidences are in the machine-readable report below. The complete raw responses and images remain in the local evidence directory reported in `golden_set_machine_readable.json`.

| Comparison | Target | Seed | A target confidence | B target confidence | PNG SHA-256 (A / B) |
|---|---|---:|---:|---:|---|
| G1 | standing | 5072 | 0.8034526706 | 0.0014235675 | `6450E42A957D6B7AA94D7DAE61159CA6D0ADFFE53EEEDBD5ABEAA63FB9757099` / `1045E329AC1A4D1F74E844605D76A6FB222ED84B8BB5D7E6178FDC5930DE7F6C` |
| G1 | standing | 17027 | 0.7523885965 | 0.0021948814 | `EF40093EF3C8264EF21834F3988AF7884E5B22BC396767FCFD3C7F0A74596009` / `364B3BAF34BDF62E582814B51289DBDEB0E837E3EE7EC4DBC034018591D2FFED` |
| G2 | sitting | 5072 | 0.0004466772 | 0.9302493334 | `1045E329AC1A4D1F74E844605D76A6FB222ED84B8BB5D7E6178FDC5930DE7F6C` / `4A0FC8F6EB0120EC9F8B3287CA0CB4435AD433FEB64BC0A54CFAB31304D6AFC4` |
| G2 | sitting | 17027 | 0.0005654395 | 0.8995426893 | `364B3BAF34BDF62E582814B51289DBDEB0E837E3EE7EC4DBC034018591D2FFED` / `174A3AACF53023F9CE0999144BE51588F25EB64043437CC3BD8AD70569290913` |
| G3 | long_hair | 5072 | 0.9275865555 | 0.9266760349 | `601BDF26351E465A73A59DC1D1B1A3C9531829531E0685643406B5F78A774E1C` / `8B2608390BBF549435748503D721D06FAAC405CFA5F26B5894A0789F95861452` |
| G3 | long_hair | 17027 | 0.9342532754 | 0.0091109276 | `724F64E9DD36E89C2EF4A9DAF229B118A50EAA6FE1A0F4ABB020139A1F7FD89B` / `2680FC0156EDE79556330842AC7FD6539CCC2ABCBBE68EF83D0FC24113F4CEA9` |
| G4 | smile | 5072 | 0.0053850710 | 0.9754948616 | `8B2608390BBF549435748503D721D06FAAC405CFA5F26B5894A0789F95861452` / `BAFAA82C2C5F70B1F6E05CF8A00FE5B4404EB58897E8DA2DD4078EC5200FC155` |
| G4 | smile | 17027 | 0.0053440630 | 0.9773911238 | `2680FC0156EDE79556330842AC7FD6539CCC2ABCBBE68EF83D0FC24113F4CEA9` / `23889FA98A74FD5A580FC38A6A9FC1C5F831FD409EB4C3E7FEC1FC762BE33054` |

## Coverage and blocking fixtures

- Synthetic nonexistent target `__issue30_nonexistent_target__`: `REVIEW_UNSUPPORTED`; no image-quality inference.
- Synthetic copied record with required traceability fields omitted: `BLOCKED_METADATA`; no scoring.
- Both fixtures are machine-readable in the JSON report and required no additional generation.

## Human review handoff

The compact 8-comparison review sheet contains only A/B image paths and an empty label field with choices `A`, `B`, `TIE/UNCLEAR`, `INVALID`; WD14 target values are omitted from that initial human-label view to avoid anchoring. Review sheet SHA-256: `F6A0BB02D853D99E29417ACD61110C005CC0B56891493170063130EC47AAE683`.

After the eight independent visual labels are supplied, the next run may evaluate the specified confidence/margin grid. No threshold or winner rule is promoted by this dry run.
