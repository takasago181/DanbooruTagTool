# Issue #226 production promotion — COMPLETE

Captured 2026-10-02 JST after the user-authorized promotion of merged PR #238.

Production `C:\Codex\DanbooruTagTool-App` is a clean Release self-contained win-x64 publish from main `49963dc129a1725c8a74d7f29aeb960884b67569`. Documentation commits after this source do not change build provenance. Runtime code, catalog, #179 overlay, #180/#216 HOME authority, Browse Groups, research and knowledge were not changed by this promotion record. #228 implementation is not started.

## Gates

Full Release **276 PASS / 3 opt-in SKIP / 0 FAIL**; focused **35 PASS**; existing performance Gate **1 PASS**, isolated from heavy tests with unchanged thresholds. Actual portable EXE validation passed schema1/FTS5, DB/scan/search/annotation/restore/Undo/preset/mock Bridge/diff/backup and WPF render with zero network calls. Fresh-folder normal Windows launch passed before applying any production UserData.

The canonical publisher and promoter were used. The entire prior runtime/UserData and complete hashes/manifest were backed up. An initial apply attempt correctly rolled back managed files when first startup created an empty Library DB absent from the pre-apply inventory. That new DB was preserved and backed up; the retry passed strict UserData byte identity. No protection gate was relaxed. Only the five managed payload files were applied; local files and UserData were never mirrored or overwritten.

## Installed runtime smoke

Native MainWindow/Browse/Prompt/Presets/Forge UI and dedicated 生成画像 workspace passed. Two roots contain **5 PNGs: 4 metadata OK and 1 metadata_missing**, with five bounded thumbnails. Three existing Forge PNGs and the metadata-missing image are safe copies; original images remained untouched. Root registration used the existing public LibraryStore/Scanner API; installed UI performed rescans and displayed the resulting images and metadata.

Favorite ON / rating 4 / Japanese note survived application exit and restart. Positive restore used PromptWorkspace; Undo returned the original 13-tag Prompt and Recovery remained unchanged. Existing Preset editor prefilled Positive/Negative, Model/Seed/Steps/Sampler/Scheduler/CFG/Width/Height; cancelled without adding a preset. `HasAutomaticSettings == false` remains the contract. Two-image diff displayed changed and same fields plus unknown RNG/Version rows.

Actual UI filters passed: Prompt `hatsune miku` -> 3 PNGs; Model `waiIllustriousSDXL_v170` -> 3; Seed `2347422866` -> 1; Sampler `Euler a` -> 3; favorite -> 1 annotated PNG. The metadata-missing image stayed registered.

Existing Bridge SendOnly passed. **DTT Library Forgeで生成 produced one successful real image** on loopback `127.0.0.1:7860`, batch count/size 1, Script None, Dynamic/Combinatorial generation off. Forge UI completed in 18.9 s and saved `output/txt2img-images/2026-10-02/00000-1466020031.png`. It appeared in the installed Library with a thumbnail and actual Positive/Negative metadata: Model waiIllustriousSDXL_v170 / hash f116b0c78f / Seed 1466020031 / Steps 24 / Euler a / Automatic / CFG 4.5 / 1024x1024 / RNG CPU / Version neo-2.29.1. Empty LoRA was preserved correctly; token parsing remains fixture-covered.

The source image had Steps 25 / CFG 5; actual output retained Forge's current 24 / 4.5 and random Seed, proving Recipe settings were not automatically applied. The first generate request produced no image because the smoke-started Forge lacked its existing shared checkpoint directory. Restoring that directory and the persisted Forge checkpoint fixed model discovery; no package install/download or runtime code change was needed. The retry created exactly one image.

Missing-file smoke used only the annotated safe copy: app closed -> move outside root -> installed UI scan shows missing with favorite/rating/note intact -> restore copy, hash identical -> installed UI scan shows available with annotations intact. The original file state is restored.

## Final storage protection and hashes

Both DB integrity checks and Library foreign keys passed; Library schema **1**, roots 2 / images 5 / metadata 4 / annotation 1. Complete final UserData inventory and consistent Library backup are retained locally. No original UserData file is missing; README is byte-identical. Final user.db Prompt **and Recovery**, and both original Presets, exactly equal the apply-before backup. Only explicitly manipulated UI Workspace/PromptWidth changed. user.db was never reset/recreated. Catalog is byte-identical to the prior production catalog and matches the manifest.

| Item | SHA256 |
| --- | --- |
| EXE | `A805FBBD80B735F354AB0CC2FBFE7F4B24A93436243888A6C6A1A4EAE8431FBE` |
| catalog.db | `D91A68186661127F16E2AE102B4DD9F3A96EAE578B3C989A8B4F17169639FC6F` |
| runtime-manifest.json | `776F9733B3DC1181117910400DB337716BD97ACDDFF2A9B9406D6CC4E6C640E9` |
| user.db after explicit smoke | `4D1DF299F4E91BC29D7C8612DFF6F86C6E14F02CDDA36AF0D9A1AC704466B5A1` |
| generation-library.db after smoke | `5728C62A87FCE8D20D6EA7461FDF4AAC288694B941817DD33D48DC3BF8DA2B98` |

Private Prompt/Preset payloads, DBs, images and backup manifests remain local. Legacy/data paths were not moved/deleted. Runtime shape is 13 total files including intentional UserData/cache, 5 managed payload files, root DLL/PDB 0; total bytes are a local snapshot, not an immutable distribution guarantee.

## Performance and remaining limits

Implementation benchmark: 5,000 tiny metadata PNG fixtures / 20,000 DB rows; cold 1,462 ms, warm 231 ms, 10 changed 203 ms, 10 missing 191 ms; common query 5.8 ms, favorite 2.5 ms, last page 6.5 ms. These are synthetic observations, not a machine-independent SLA. Promotion performance measurements and summarized test counters are in `validation/`.

Manual scan; no automatic rename merge/prune UI. WebP preview is WIC-dependent; actual JPEG/WebP images, different PC and physical network disconnect remain unverified. Isolated no-service/proxy-unavailable startup and PNG real smoke passed; JPEG/WebP parsers remain fixture-covered. Full Recipe apply, A/B Lab, LoRA Library and Region Composer are separate issues. No #228 work was started.

Exact structured evidence: `PRODUCTION_CHECKPOINT_2026-10-02.json`; current deployed provenance: `../project/LAST_KNOWN_GOOD.json`.
