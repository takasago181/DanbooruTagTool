# Generation image library (#226)

## Ownership

`UserData/generation-library.db` is a separate user-owned SQLite schema v1. The constructor refuses every other DB filename. It never opens `user.db` or `catalog.db`. Root configuration and annotations must be backed up; thumbnail pixels can be reconstructed. Library rows are not embedded in UserState JSON. Prompt restore and explicit preset saving continue to use the existing UserState coordinator.

Tables: `library_root`, `image_asset`, `generation_metadata`, ordered `generation_parameter`, ordered `generation_lora`, `image_annotation`. Asset identity is `(root_id, relative_path)` with Windows case-insensitive comparison. Annotation rows reference stable IDs. Both parsed normalized metadata and original infotext/unknown ordered parameters are retained. Content hash is optional and is not calculated during scan.

`PRAGMA user_version` controls migrations. Schema creation/migration is transactional. A consistent SQLite backup is created before migrating a nonempty older DB; an unsupported newer schema is refused without reset. Failed migrations roll back, keep the original, and provide the DB path and recovery instruction. The UI offers explicit SQLite backup to a new file; overwrite is refused. No scan/rebuild deletes roots, images or annotations.

## Scan and cache

Manual recursive reconciliation is authoritative. There is no watcher authority, startup scan, source rebuild or network service. Reparse points are skipped to avoid cycles. Enumeration failures/cancellation roll back the unfinished root and never infer missing files from an incomplete traversal. Completed roots commit independently.

The root transaction batches writes, streams filenames, and compares path + size + UTC mtime. Unchanged images skip parsing and thumbnail work. Changed assets retain their ID and annotations; new metadata replaces only metadata child rows. Missing files retain all user state and historical metadata. A file changing during read is retryable; failed stat/read does not advance its recorded stat fingerprint.

PNG reuses existing `ForgePngGenerationMetadata` (tEXt/zTXt/iTXt); its parsing algorithms remain unchanged, with a retryable-IO flag added to its exception contract. JPEG APP1 and WebP RIFF EXIF containers use a clean bounded TIFF UserComment reader (ASCII/Unicode, endian/offset/size/cycle checks). Their infotext goes through the same existing parser. Images remain indexed when metadata is absent, invalid or unreadable. Simple numeric `<lora:name:weight>` Positive tokens are indexed; ambiguous extension syntax and `Lora hashes` remain in raw/unknown parameters.

Thumbnail cache: `UserData/Cache/GenerationThumbnails/`. Keys include schema v1, 256px edge, asset ID, absolute path, size and mtime. Two background workers service at most the current 60-row page. WPF decodes to the appropriate bounded width/height. PNG encoding writes unique temp files then atomic replacement. Corrupt cache entries rebuild; decode/cache failures do not affect DB or annotations. WebP pixel decoding uses the OS WIC codec; metadata indexing itself has no codec dependency.

## Search and UI

Dedicated `生成画像` tab: roots/filters on left, SQL-paged thumbnails center, selection/metadata/annotations/actions on right. No all-image materialization or full-resolution grid decoding. SQL queries bound page size to 200 even for non-UI callers; UI uses 60. Text filters escape LIKE wildcard characters; parameterized SQL handles all input. Numeric/exact filters use B-tree indexes. Stable sort ties use image ID.

Search supports Positive, Negative, Model, Seed, Sampler, Scheduler, CFG bounds, resolution, LoRA, favorite, rating, note, root and metadata status. Sorts: newest/oldest/filename/favorite/rating. FTS5 is capability-probed in tests and actual self-contained executable. v1 deliberately uses deterministic SQLite LIKE for literal mixed/Japanese substring semantics; it does not require FTS or a service. Broad substring queries may scan rows, measured with 20,000 fixtures. A future FTS optimization must preserve these semantics.

Annotations persist independently on edit; write errors keep entered state, prevent selection/page replacement, and block closing until a retry succeeds. Scan never writes annotation fields. Roots can be disabled/enabled without erasing history.

Restore calls `PromptWorkspace.Replace`, preserving Undo/Recovery and raw Prompt surface. Preset creation prefills `GenerationPresetsViewModel.BeginNewPresetFromSnapshot`, with no implicit save. Image send/generate uses existing ForgeViewModel and bridge with explicit Positive/Negative. It does not replace the workspace or send any Recipe settings. GenerationRecipe.HasAutomaticSettings remains false. Metadata diff is structural, including ordered duplicate unknown values and LoRA tokens, with same/changed/only-left/only-right states.

## Validation and limits

See `PERFORMANCE.json` and `EXTERNAL_REFERENCE.md`. The 5,000-image fixture is tiny synthetic PNG data, not a production-media throughput promise. 20,000-row filters/pages and cold/warm/changed/missing scans are checked. Normal runtime requires no network; Forge communication remains a separate explicit user action.

The explicit `--validate-library <new-empty-output-directory>` acceptance hook exercises the actual EXE/SQLite/thumbnail/WPF stack against disposable data, uses a mock Forge adapter, renders the real workspace, checks annotations/Undo/preset/backup/missing preservation and records FTS capability. It never executes at normal startup and refuses nonempty outputs. Real Forge rendering is covered by existing protocol/action regressions rather than launching a generation during validation.

Known limits: manual scans; root/path identity (rename creates a new asset and leaves annotated missing history); no automatic duplicate/rename hashing or prune UI; PNG/JPEG preview on standard WPF codecs and WebP preview when WIC supports it; no ComfyUI graph reconstruction; simple explicit Positive LoRA tokens only; broad text search uses LIKE. Recipe full application/A-B/LoRA library/Regional features remain sibling Issues. Different-PC validation and physically disabling the network adapter were not performed; no-service/proxy-unavailable execution and a different-folder copy are the local acceptance scope. Production is NOT APPLIED.
