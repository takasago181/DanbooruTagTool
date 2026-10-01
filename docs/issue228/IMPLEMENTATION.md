# Issue #228 — API-first recipe execution

## Contract

`ForgeGenerationApiClient` is a separate C# HTTP adapter. The legacy bridge and `GenerationRecipe.HasAutomaticSettings == false` remain intact; that flag only governs the retired bridge settings path. No Gradio DOM recipe automation is reintroduced.

Explicit Library/selected saved Preset actions send that item's Positive, Negative and nullable recipe. Probe OpenAPI plus installed model/sampler/scheduler lists first. Unsupported/ambiguous values are rejected before POST. Numeric request bounds: fixed nonnegative seed, steps 1..150, CFG 0..30, dimensions 64..2048 in multiples of 8. Omitted fields use Forge defaults. Batch size and iterations are always one; no automatic retries. Requests are serialized in the shared client/view model. Generation has a ten-minute timeout; uncertain completion is reported and requires inspection before resending.

HTTP is loopback only, without credentials, query, fragment, subpath, proxy or redirects. No startup network probe. No POST to options. Per-request checkpoint override requests restoration; before/after options are checked.

The one returned PNG is saved with a unique create-new name in portable `UserData/ForgeResults`. The existing PNG reader parses actual image metadata; every explicitly requested field is compared, including checkpoint name/hash when advertised and PNG dimensions. No success if metadata is missing, differs, output count differs, or model restoration differs. Saved mismatching images remain evidence. The existing #226 Library indexes saved results; failed indexing is explicitly reported with the retained file path. No second history DB or UserData schema migration.

## Actual Forge Neo spike

Target installed source: `Haoming02/sd-webui-forge-classic`, revision `0b1783c79b397e73818c3d8432b25cc3cbb5ca50`, runtime `neo-2.29.1`. Original Forge is `http://127.0.0.1:7860`, launched without `--api`; API options returned 404. Spike used copied UI/config files and an existing installed Python/model environment, no install/download, at explicit `--server-name 127.0.0.1 --nowebui --port 7861`. The first attempt used Forge's unexpected wildcard bind and was immediately stopped; the restarted listener was verified as 127.0.0.1 before generation. Original Forge was not restarted or reconfigured.

Three bounded requests each returned exactly one image. All ten fields round-tripped through actual PNGs and #226 Library. WAI checkpoint options were restored after each Chenkin Noob override. First: seed 123456789, 9 steps, Euler/Karras, CFG 5.5, 512x640. Remaining two: seeds 123456790/791, 3 steps, Euler/Karras, CFG 4.75, 256x320. Exact evidence: `SPIKE_ROUNDTRIP_2026-10-02.json`.

Scope of verified runtime behavior is these requests. Other runtime/version/sampler/model combinations always undergo the same output checks, never inherit a universal verified claim. In particular, an omitted or normalized Scheduler infotext for a requested value fails closed. Random seed -1 is deliberately rejected for explicit recipe execution; use an omitted Seed for Forge defaults. There is no cancel/interrupt endpoint action, because it could interrupt unrelated Forge work.

## External source review

| Project/revision/license | Reviewed functions/files | Usage |
|---|---|---|
| [Forge Neo 0b1783c](https://github.com/Haoming02/sd-webui-forge-classic/tree/0b1783c79b397e73818c3d8432b25cc3cbb5ca50), AGPL-3.0 | `modules/api/api.py`: `text2imgapi`, routes; `modules/api/models.py`: request/response schema; `modules/sd_samplers.py`: `get_sampler_and_scheduler`; `modules/processing.py`: per-request override/restore/infotext; `modules/cmd_args.py`: API/settings/server flags | Protocol/behavior reference; independently written C# adapter, no source copied or ported |

Reviewed installed source files have no diff from the pinned revision. Forge silently normalizes unknown sampler/scheduler and drops unknown checkpoint overrides; DTT therefore validates exact advertised choices before generation and checks the actual output afterwards. Forge owns rendering. DTT reuses its existing Recipe, metadata parser, Library store/scanner and preset persistence.

## Protection and remaining limits

No catalog/overlay/HOME/Browse authority, research or legacy/data changes. No existing UserData reset, migration or production apply. Existing send-only/current-settings-generate behavior remains unchanged. Normal startup stays offline. Portable publish and Windows smoke are separate validation gates recorded in the PR/checkpoint.
