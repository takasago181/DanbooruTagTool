# Generation image library external reference review

Base main: `27b23b0547eb31e109ec1fea78c42eba50c364a1`. Scope: #226 under #225. Production is NOT APPLIED.

| Reference | License | Reviewed code | Use |
|---|---|---|---|
| [Infinite Image Browsing](https://github.com/zanllp/infinite-image-browsing/tree/ac5418772986623d8dfa64ff12cdd54be2459b2b) | MIT | scripts/iib/db/update_image_data.py; datamodel.py; img_cache_gen.py; vue/src/page/TagSearch/MatchedImageGrid.vue | Clean C#/SQLite/WPF reimplementation of incremental stat checks, separate metadata/index/cache, SQL filters and bounded pages. No copied code. |
| [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui/tree/82a973c04367123ae98bd9abdf80d9eda9b910e2) | AGPL-3.0 | modules/images.py save_image_with_geninfo/read_info_from_image; modules/infotext_utils.py parse_generation_parameters | Protocol/format compatibility only: PNG parameters; JPEG/WebP EXIF UserComment with Unicode prefix; infotext field naming. No copied code. Existing DTT parser retained. |
| [Forge](https://github.com/lllyasviel/stable-diffusion-webui-forge/tree/dfdcbab685e57677014f05a3309b48cc87383167) | AGPL-3.0 | modules/images.py save_image_with_geninfo/read_info_from_image | Protocol/format compatibility only; same metadata envelope. Existing DTT Forge bridge reused. No copied code. |

IIB checks directory modification dates before descending and image dates before parsing, commits per folder, preserves custom tags during index rebuild, uses SQL limits/cursors, and uses a recycling grid. Its cache hashes path + modification date and bounds pixel dimensions. DTT deliberately stats every file on full reconciliation (in-place changes need not change directory mtime), keeps stable row IDs/annotations, and never deletes missing rows. Thumbnails are generated on demand for bounded pages rather than during every scan. No Python/Web runtime is introduced.

The published IIB benchmark is prior-art context, not a DTT guarantee or a same-machine comparison. DTT timings must be measured separately. No direct algorithm port or copied source is included; architectural patterns are independently implemented for the existing DTT layers.

Dependency map: PromptWorkspace.Replace owns restore/Undo/Recovery; GenerationPresetsViewModel.BeginNewPresetFromSnapshot owns preset editing; GenerationRecipe.FromMetadata remains reference-only; ForgeViewModel owns SendOnly/SendAndGenerate; ForgePngGenerationMetadata owns PNG/infotext parsing; Library persistence is independent of UserStateCoordinator/user.db and catalog.db.

Portable candidate shape now admits only the explicit new Library DB/journal names, uniquely named migration backups and hash-keyed PNG/temp thumbnail cache paths within UserData. Installed UserData protection still compares the complete baseline and is unchanged. Library state remains excluded from publish payload and runtime manifest hashes.
