# DanbooruTagTool Forge bridge companion

The application copies `scripts/dtt_bridge.py` and `javascript/dtt_bridge.js`
into a user-selected Forge `extensions/dtt_bridge/` directory from the
`Forge設定` dialog. Restart Forge after installation so its extension loader
registers the local routes and loads the polling script.

The bridge exposes only loopback routes:

- `GET /dtt-bridge/health`
- `POST /dtt-bridge/prompt`
- `GET /dtt-bridge/pending`

It updates the existing txt2img Positive field and, for `replace` requests,
the Negative field. It does not call `/sdapi/v1/txt2img` and never triggers
Generate.
