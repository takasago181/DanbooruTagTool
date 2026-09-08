# Issue #6 PNG metadata recheck — Luna boundary

Observed: 2026-09-08. Read-only inspection of the user-specified folder:
`C:\Users\takas\Downloads\StabilityMatrix-win-x64\Data\Packages\Stable Diffusion WebUI Forge - Neo\output\txt2img-images`.

## Latest PNG

- File: `Walnut_Beginner_Baseline_Benchmark_00003_.png`
- Last write: `2026-09-03T09:48:27.0976880+09:00`
- Size: `1,516,735` bytes
- SHA256: `E903217B0585D9DFB461FF3E5BFE897590C8E9A31F9C2106E1FC2DE1BE85DB1B`
- PNG signature: valid
- IHDR: `1024 x 1024`, 8-bit RGB
- PNG text chunks: `prompt`, `workflow`

## Metadata recovered from the PNG

- Positive prompt: `1girl, portrait, simple background, soft lighting`
- Negative prompt: `lowres, blurry, bad anatomy, text, watermark`
- Checkpoint name in workflow: `plantMilkModelSuite_walnut.safetensors`
- Seed: `5072` (`fixed` in the workflow node)
- Steps: `28`
- CFG: `3.0`
- Sampler / scheduler: `euler` / `normal`
- Width / height / batch: `1024 / 1024 / 1`
- Workflow contains an explicit ComfyUI graph (`CheckpointLoaderSimple`, `KSampler`, `SaveImage`) and frontend version `1.49.6`.

## Boundary and result

**Confirmed:** the latest PNG has complete prompt, seed, generation-setting, checkpoint-name, and workflow traceability metadata. The four PNGs in the folder were enumerated read-only.

**Not proven:** Forge Neo generated this image. The embedded graph is ComfyUI-formatted, and `plantMilkModelSuite_walnut.safetensors` was not found under the Forge Neo `models` tree or the Stability Matrix `Data` tree. The saved Forge Neo config remains `sd\\waiIllustriousSDXL_v170.safetensors` with the previously observed SHA256 `1FCD5EACA58DABF87A62C9317A257D9A765CC5E168329453FC7C937BA319E3C4`.

The artifact-level metadata check therefore passes, while the Issue #6 Forge Neo/Luna baseline-generation and Japanese-UI checks remain unverified. No installation, update, configuration change, or new generation was performed.
