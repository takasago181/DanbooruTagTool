# DanbooruTagTool Forge bridge companion

The application copies `scripts/dtt_bridge.py` and `javascript/dtt_bridge.js`
into a user-selected Forge `extensions/dtt_bridge/` directory from the
`Forge設定` dialog. Restart Forge after installation so its extension loader
registers the local routes and loads the polling script.

The bridge exposes only loopback routes:

- `GET /dtt-bridge/health`
- `POST /dtt-bridge/prompt`
- `GET /dtt-bridge/pending`
- `POST /dtt-bridge/result`
- `GET /dtt-bridge/result/{request_id}`

Prompt-only requests keep the legacy behavior: the bridge updates the existing
txt2img Positive field and, for `replace` requests, the Negative field.

A `send_and_generate` request uses those same UI fields, waits for the UI to
observe the Prompt changes, then clicks Forge's existing txt2img Generate
button. This deliberately reuses the settings already selected in Forge
(checkpoint, sampler, scheduler, steps, CFG, resolution, seed, LoRA,
ADetailer, and other UI-owned options) instead of duplicating them in
DanbooruTagTool.

Generate requests are acknowledged back to the desktop client so a missing
Prompt field or Generate button is reported instead of silently claiming
success. The bridge still never calls `/sdapi/v1/txt2img` directly.
