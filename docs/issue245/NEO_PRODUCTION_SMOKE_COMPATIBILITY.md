# Production smoke: Neo model metadata compatibility

During user-authorized #246 promotion from merged main 94bcb81e63e152067f8794ea76384b01d27b3bb8, production Create generated one bounded 512×640 PNG (seed24520261003,8steps,Euler/Karras,CFG4.75). It entered production Library, but strict name comparison rejected `sd_waiIllustriousSDXL_v170` (API model_name) versus `waiIllustriousSDXL_v170` (PNG). Actual model hash f116b0c78f matched. Positive,Negative,Seed,Steps,Sampler,Scheduler,CFG,Width,Height all matched. Failed output is retained, never relabeled as a successful original trial.

The adapter now permits exactly the basename of the capability-declared checkpoint title only when its nonempty declared model hash exactly matches PNG metadata. It does not strip arbitrary prefixes from received names, use fuzzy/substring matching, accept a hashless basename alias, change request fields, retry a POST or invoke Gradio. The prior exact model_name path remains available. Six regression cases cover matching/mismatching/missing hashes, undeclared names and legacy exact-name behavior. Existing ten-field mismatch tests remain unchanged.

A separate first request returned HTTP500 before rendering because the updated Forge had a stale saved basename and selected Anima as startup fallback; Anima lacked VAE state. Cleanup also rejected the stale original alias. Read-only progress confirmed idle. After backing up Forge config, explicit selection of existing local Noob then original WAI refreshed loading parameters; no model or software was downloaded/installed by DTT. These two failures are distinct.

## External reference

- Project: Haoming02/sd-webui-forge-classic (Forge Neo).
- Exact installed revision: 97b26fb404314a11dad7cdde2706da57ea53f4f2.
- License: GNU AGPLv3 (installed LICENSE).
- Reviewed: modules/api/api.py `text2imgapi`, options route; modules/sysinfo.py `set_config`; modules_forge/main_entry.py `checkpoint_change` / `refresh_model_loading_parameters`; modules/processing.py `process_images` restoration and infotext; backend/loader.py VAE assertion; live sd-models/options/progress and actual PNG/Library metadata.
- Used as behavior/protocol reference only; clean DTT adapter correction. No copied/ported AGPL source.

Scope: close the real production acceptance gap for #228/#245. No new workspace, schema migration, authority/catalog change, parser engine or service.

PNG-derived Recipe resolution also accepts this exact title basename only for one hash-declared capability entry. Duplicate basenames and hashless aliases are rejected before any generation POST. Three integration cases verify one bounded real-PNG readback and both refusals.
