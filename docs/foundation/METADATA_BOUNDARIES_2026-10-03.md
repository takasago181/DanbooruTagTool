# #247 / #251 / #253 narrow metadata checkpoint

PR #262 merged at `df38e722fe3b52fa706b87307dc133a9cecdcb27`.
The user explicitly authorized that merge and continuation on 2026-10-03,
superseding the historical research STOP. The 142-row adoption matrix and
recovered Oct 1–2 research remain the investigation inputs; no repeated survey,
197-tool review, worktree audit, cleanup or ordered catalog parity was performed.

## Implemented boundary

- Core owns `GenerationMetadataSnapshot`, the unchanged pure
  `GenerationInfotextParser`, Recipe projection and `IGenerationMetadataReader`.
- Data owns concrete PNG/JPEG/WebP Library readers and one default reader
  registration shared by Library UI and its validation route. Existing PNG-only
  generation-result scans retain their scope.
- `ForgePngGenerationMetadata.Read` remains the bounded PNG compatibility entry
  point for existing import/Forge API callers. Its `Parse` delegates to the pure
  parser. Binary envelope algorithms and their limits are unchanged.
- Library ingest still persists exact raw infotext and ordered unknown/duplicate
  parameters before Recipe projection. Recipe is a partial typed view, never the
  replacement for original metadata. No DB schema/version migration occurs.
- No new image formats, ComfyUI graph interpretation, generation feature,
  metadata writing or new runtime dependency is introduced. Unsupported image
  metadata remains in original read-only source files; this change does not claim
  to index every PNG chunk, XMP field or arbitrary graph.

## #251 disposition

The needed shared production operation is infotext interpretation and adapter
registration, now explicit and reused above. Existing Maintenance verify/compile
commands already cover current authority inputs. There is no demonstrated missing
production source fetch operation, so no speculative fetch command, new one-off
script, archived tool resurrection or CLI framework replacement is warranted.
tagdb-updater remains the matrix's PORT candidate if an actual fetch requirement
arises; capped upstream lists and translation fallback are not runtime authority.
#252 receives no additional changes; branches/worktrees/research remain protected.

## Reuse decision overlay (not a replacement survey)

| Candidate | Decision for this change | Reason |
|---|---|---|
| sd-parsers | PORT design only | Separate file extraction from generator interpretation; no copied Python code or Python runtime. Preserve raw input, not just scalar Recipe values. |
| media-metadata | PORT design only | Separate envelope/normalization and retain opaque input. No copied TypeScript, Node runtime or new graph semantics. |
| MetadataExtractor.NET | REUSE candidate retained; current bounded EXIF reader KEEP | 2.9.3 supports .NET 8+/netstandard, Apache-2.0. Its TIFF traversal is recursive and uses tag-table-sized stack allocation; direct use has not established equivalence to DTT's depth 2 / 4,096-entry limits. Preserve safety instead of introducing a second pre-validation TIFF parser merely to wrap it. |

Only the release/API safety gap was checked:
[package 2.9.3](https://www.nuget.org/packages/MetadataExtractor/2.9.3),
[release TIFF reader](https://github.com/drewnoakes/metadata-extractor-dotnet/blob/2.9.3/MetadataExtractor/Formats/Tiff/TiffReader.cs),
[previous pinned license/source evidence](reuse-evidence/drewnoakes__metadata-extractor-dotnet.json).
`TiffReader.ProcessIfd` uses visited-IFD tracking, recursive sub-IFD calls and
`stackalloc byte[tagTableLength]`; those protect some corruptions but do not
establish the same resource caps as DTT. This is a compatibility reason to defer
direct adoption, not a claim that the library is universally unsafe.

## Verification and stop

Targeted contracts cover PNG/import, Recipe, Library reconciliation/ingest and
Forge API. Additional tests exercise exact Unicode/CRLF raw text, duplicate and
unknown parameters through JPEG/WebP into SQLite, unchanged source image hashes,
unsupported adapters, malformed input, EXIF cycles, WebP 2 MiB envelope limit and
PNG compressed expansion limit. Full regression and clean build are performed
once on the final code; results are recorded in the PR/checkpoint evidence.

Catalog generation/authority and semantic contents are untouched; Batch A parity
remains valid. Production is not installed and its existing 19-file hash baseline,
including 14 UserData files, is reused for final comparison. No GUI acceptance is
needed for unchanged UI behavior. No branches/worktrees are deleted or recreated.

Rollback: revert this metadata PR's commit(s); there is no data migration to undo.
PR #262 can separately be reverted; its recovery tag/manifest/ledger remain valid.
STOP at this PR review, before #254. Remaining broad #253 adoption/architecture
and eventual Foundation production/LKG decision require separate scope; do not
interpret this small boundary checkpoint as completion of all #253.
