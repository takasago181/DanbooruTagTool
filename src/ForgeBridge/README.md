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
button.

DTT recipes may still store Model for reference and PNG round-trip, but Model
is intentionally manual-only and is not sent as an automatic Forge setting.
Select the checkpoint in Forge before applying or generating a recipe.
Generation-recipe requests may automatically carry any subset of Seed, Steps,
Sampler, Scheduler, CFG, Width and Height. Omitted fields are left unchanged.
The `apply_recipe` action applies the saved Prompt, Negative and those
automatic recipe settings without starting Generate. A recipe-backed
`send_and_generate` applies those same values and then triggers Generate once.

Recipe support is capability-gated as `recipe_settings`, so older bridge
installs continue to support Prompt-only send and the previous Generate path
instead of silently misapplying recipe data.

Generate and recipe actions are acknowledged back to the desktop client so a
missing control or Generate failure is reported instead of silently claiming
success. The bridge still never calls
`/sdapi/v1/txt2img` directly.
