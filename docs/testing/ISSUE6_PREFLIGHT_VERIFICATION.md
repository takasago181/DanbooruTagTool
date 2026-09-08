# Issue #6 preflight verification only

Observed: 2026-09-08, approximately 02:27–02:34 UTC (11:27–11:34 JST).
Repository base: `b115b3c0e514c17ad5e3b5c9d48032aab92ac518`.
Source: live Issue #6 body and all four comments, read with the GitHub connector.
Execution checkpoint: https://github.com/takasago181/DanbooruTagTool/issues/6#issuecomment-5578172567
SHA approval: https://github.com/takasago181/DanbooruTagTool/issues/6#issuecomment-5575904528
Scope: user-requested TEMP verification and repository evidence, not a new DEV implementation. Current DEV mirror is inactive after #28 completion.

## 1. Baseline verification

**BLOCKED / not verified. No baseline-generation PASS or FAIL is asserted.**

- Initially only Stability Matrix PID 8264 was running; no Python process / 7860–7870 listener was found and localhost:7860 refused connection.
- The user then started Forge Neo. Python PIDs 24272 and 26112 appeared, and PID 26112 listened on 127.0.0.1:7860. GET `/config` succeeded and reported Gradio 4.40.0 with 3,933 components.
- Published txt2img component values: width 1024 (ID 107), height 1024 (108), batch size 1 (114), steps 20 (57), CFG 6 (118). These are server UI configuration values, not a verified current browser-session state or successful generation.
- Read saved config: checkpoint `sd\waiIllustriousSDXL_v170.safetensors`, preset `xl`, localization `ja_JP`. Actual checkpoint loading/inference and functioning Japanese UI were not verified.
- LoRA tab definitions were present (IDs 1099 and 2392); 26 `.safetensors` files were present at the top level of the shared Lora directory. Full browser list health was not verified.
- No image was generated and no newly generated PNG metadata was inspected. This is not a generation failure; execution coverage is incomplete.

## 2. Existing five extensions

Forge directory: `C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Packages\Stable Diffusion WebUI Forge - Neo`.

| Extension | Directory present | Read-only runtime evidence | Health verdict |
|---|---|---|---|
| TagComplete Neo | `extensions/sd-webui-tagcomplete-neo` | Tag Autocomplete settings tab, ID 3648 | Startup traceback and operation not verified |
| WD14 Tagger | `extensions/stable-diffusion-webui-wd14-tagger` | Tagger tab, ID 3937; settings tab 3723 | Startup traceback and operation not verified |
| ADetailer Neo | `extensions/ADetailer-Neo` | txt2img checkbox ID 148 is false | OFF-state generation not verified |
| Forge Couple | `extensions/sd-forge-couple` | ForgeCouple callbacks present in published configuration | Enable state/startup/operation not verified |
| Dynamic Prompts Neo | `extensions/sd-dynamic-prompts` | Published checkbox ID 513 false; ID 1744 true | Defaults left intact; OFF-state generation not verified |

The different Dynamic Prompts checkbox values were not changed. Extension presence is not equivalent to operational health. No startup-log capture was available through the failed UI tooling; no assertion of traceback-free startup is made.

## 3. Multi Prompt Slots

- Exact approved repository: https://github.com/Isna2026/sd-webui-forge-multi-prompt-slots
- Command: `git ls-remote --symref https://github.com/Isna2026/sd-webui-forge-multi-prompt-slots HEAD`
- Remote HEAD: `b3f45b17e5a24a20b4fa04edac74e6a4fec23dfe`, `refs/heads/main`.
- Reviewed HEAD: `b3f45b17e5a24a20b4fa04edac74e6a4fec23dfe`.
- Commit date from live GitHub commit metadata: `2026-06-24T05:42:37Z`; title `Update`.
- **INSTALLATION_CANDIDATE_OK**: identical SHA. No diff/re-review required at observation time. This is not installation authorization.

## 4. Forge Neo Infinite Image Browsing

- Exact approved repository: https://github.com/Dusky-dev/sd-forge_neo-infinite-image-browsing-xl
- Command: `git ls-remote --symref https://github.com/Dusky-dev/sd-forge_neo-infinite-image-browsing-xl HEAD`
- Remote HEAD: `ced039479c2e1463c9bdb136d355e01b3dfc9279`, `refs/heads/main`.
- Reviewed HEAD: `ced039479c2e1463c9bdb136d355e01b3dfc9279`.
- Commit date from live GitHub commit metadata: `2026-08-29T22:18:33Z`; title `Update index-84bce5f9.js`.
- **INSTALLATION_CANDIDATE_OK**: identical SHA. No repository/fork substitution, clone or install occurred.

## 5. Built-in X/Y/Z availability

**Present; actual interaction/usability not verified.** `scripts/xyz_grid.py` exists. Runtime `/config` Script dropdown IDs 969 and 2247 both offer `X/Y/Z plot`, with current published value `None`. No plot or comparison was executed.

## 6. Fixed Seed and metadata traceability

**Partial / unverified end to end.** Published numeric Seed control ID 121 exists with value -1. No Seed value was changed. A fixed-seed UI input is exposed, but actual operation and generated-image Prompt / Negative / Seed / Steps / CFG / Sampler / Checkpoint / resolution metadata were not verified.

## 7. Blockers / warnings / evidence boundary

- Browser-control initialization failed twice; native computer-use initialization also failed with `node_repl kernel exited unexpectedly` and `windows sandbox failed: helper_unknown_error: setup refresh had errors`.
- GET `http://127.0.0.1:7860/sdapi/v1/options` returned HTTP 404. No API-enabling flags/settings were changed and no custom Gradio runner or glue tool was created.
- Therefore the mandatory normal generation, Japanese UI, startup-log and PNG traceability checks could not be completed. Public `/config` definitions and file presence cannot replace those checks.
- The early unavailable-process finding was superseded by the user's startup; Forge Neo is not reported as still stopped.
- Read-only config inventory at 02:33:48 UTC: `config.json` SHA256 `1fcd5eaca58dabf87a62c9317a257d9a765cc5e168329453fc7c937ba319e3c4`, mtime `2026-09-08T02:31:05.9613011Z`; `ui-config.json` SHA256 `2ec310c66bc8c7f3863e0dbaaafb7a6fc59c9254bdf8c051fd64479d5af568ffc`, mtime `2026-09-05T14:34:54.1599265Z`. These are observed hashes, not a claim of equality with an unavailable historical baseline. The user started the app during the check.
- No installs, updates, patches, removals, persistent-setting changes, model/dependency changes or generation requests were made by Codex. Forge Neo, Stability Matrix, five existing extensions and local/protected data were not modified by Codex. The only intended repository change is this report.
- Verification used GitHub issue/commit reads, remote ref reads, OS process/listener inventory, selected local file/config reads and HTTP GETs. No pytest was needed for this evidence-only change; `git diff --check` is the repository formatting check.
- Resume the unverified GUI/log/generation checks once the existing UI-control path is available, while preserving the same no-install boundary. Recheck remote SHAs before any later install decision.

## 8. Final verdict

**BLOCKED**. Both approved remote SHAs match, but the required baseline and traceability evidence is incomplete. Not SAFE_TO_PROCEED_WITH_INSTALL. No Stage10 production A/B started and Issue #6 is not marked complete.
