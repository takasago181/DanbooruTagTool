# DanbooruTagTool Forge bridge companion

The application copies `scripts/dtt_bridge.py` and `javascript/dtt_bridge.js`
into a user-selected Forge `extensions/dtt_bridge/` directory from the
`Forge設定` dialog. Restart Forge after installation so its extension loader
registers the local routes and loads the polling script.

The bridge exposes only loopback routes:

- `GET /dtt-bridge/health`
- `POST /dtt-bridge/token-count` (explicit read-only loaded-model counter, `token_count_v1`)
- `POST /dtt-bridge/prompt`
- `GET /dtt-bridge/pending`
- `POST /dtt-bridge/result`
- `GET /dtt-bridge/result/{request_id}`

Prompt-only requests keep the legacy behavior: the bridge updates the existing
txt2img Positive field and, for `replace` requests, the Negative field.

A `send_and_generate` request uses those same UI fields, waits for the UI to
observe the Prompt changes, then clicks Forge's existing txt2img Generate
button.

DTT Generation Recipes use a separate API-first `/sdapi/v1/txt2img` client
for explicit Recipe API generation, with actual PNG metadata round-trip checks.
This bridge's Prompt/current-settings Generate path does not apply recipe settings.

The bridge still keeps its existing protocol compatibility for older clients,
but the desktop does not use the bridge to apply recipe settings.

Recipe support is capability-gated as `recipe_settings`, so older bridge
installs continue to support Prompt-only send and the previous Generate path
instead of silently misapplying recipe data.

Generate and recipe actions are acknowledged back to the desktop client so a
missing control or Generate failure is reported instead of silently claiming
success. The bridge still never calls
`/sdapi/v1/txt2img` directly.

The optional token endpoint delegates to the installed Forge UI counter without
generation/model loading/options mutation. It refuses FakeInitialModel heuristic,
missing loaded checkpoint or busy queue, and reports model/engine/tokenizer and
the actual engine's chunk contract where exposed. Unknown stays unavailable.
Source/license review and verified limits: `docs/issue232/IMPLEMENTATION.md`.
