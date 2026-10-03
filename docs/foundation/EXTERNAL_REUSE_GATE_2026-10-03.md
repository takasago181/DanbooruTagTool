# #247 External implementation / reuse gate — decision STOP

Status: **RESEARCH_COMPLETE_DECISION_STOP**. Baseline main:
`0193cee41c52050e680767f722efcdcef6de481f`, merged PR #261.
P0 + Batch A remain accepted inputs. Safe Batch B work is preserved at
`cad3bc0d`; [checkpoint](BATCH_B_CHECKPOINT_2026-10-03.md).
No external code/package/model was installed, executed, vendored into product,
or adopted in this investigation. Production and UserData are unchanged.
The user required this investigation and a report, followed by STOP. It does
not authorize the proposed replacements, #253, Batch C, #230, or #256 features.

## Recovery before additional inspection

Recovered sources are indexed with exact commit/date/hash in
[recovery ledger](EXTERNAL_REUSE_RECOVERY.json):

- 61 existing repository note snapshots from main and
  `knowledge/generation-corpus`, including Oct 1–2 dated research. Duplicate
  paths on different refs are preserved as separate snapshots, not 61 unique studies.
- All 35 live #256 comments: initial candidates, code comparisons, adoption
  ledger, semantic benchmark ladder, updater and hash-provider findings, scope
  freeze, and subsequent corrections. Historical implementation recipes are
  evidence; the latest autonomy correction makes them nonbinding.
- The latest handoff and checkpoint 23 summary from the existing conversation
  “LLMプロンプト支援調査”, reconciled with #256. No message was sent to that task.
- Older positioning/environment and #30 dry-run records: installed Neo tools,
  JP Tag Assistant/BooruPrompter/co-occurrence positioning, and Agent Scheduler
  HOLD because native Forge API already met the tested generation need.

Timestamps retain UTC. The user requested the Oct 1–2 knowledge; the #256
comments written Oct 2 UTC include Oct 3 JST material and were all retained.
The latest source status was refreshed only for recovered candidates and gaps
in metadata/.NET/CLI/CI reuse. This is not another repository/worktree audit.

The [human decision table](EXTERNAL_REUSE_MATRIX.md) and
[full per-candidate matrix](EXTERNAL_REUSE_MATRIX.json) include original purpose,
historical assessment/source, maintenance, license, stack, Windows suitability,
host compatibility, direct library/API/CLI/design reuse, exact DTT code,
advantages, retained responsibilities, dependency/cost, and final disposition.
[Pinned public evidence](reuse-evidence/INDEX.json) records actual source files,
commits and hashes, rather than merely search-result links. Unresolved original
identities/licenses are explicitly REJECT for direct adoption; they were not
replaced by guessed similarly named repositories.

## Most useful existing implementations

| Priority | Candidate / disposition | Concrete DTT comparison and limit |
|---|---|---|
| 1 | [MetadataExtractor .NET](https://github.com/drewnoakes/metadata-extractor-dotnet), REUSE candidate | `GenerationMetadataReaders.cs` manually traverses JPEG/WebP/EXIF. Library format coverage could remove that binary-parser burden. Keep bounded input and DTT UserComment/infotext normalization. Its PNG decompressor copies to an unrestricted memory stream, so wholesale PNG reader replacement is rejected. LICENSE is Apache-2.0 even though GitHub API says NOASSERTION. |
| 1 | [sd-parsers](https://github.com/d3x-at/sd-parsers), PORT | Current Forge parser does not interpret arbitrary ComfyUI graphs. Upstream separates extractors/parsers, retains unprocessed nodes and returns multiple samplers. Reuse the adapter design after fixed fixtures; preserve ambiguity instead of choosing a sampler silently. Python/Pillow is not a direct C# library. |
| 1 | [tagdb-updater](https://github.com/PYU224/tagdb-updater), PORT | Fetch/retry/backoff/pacing and sanity gates are reusable engineering for #251 source adapters. Distributed capped lists, translation fallback, and automatic push policy are not DTT semantic authority. No new fetch command is implemented here. |
| 2 | [civitai/media-metadata](https://github.com/civitai/media-metadata), PORT | Recent TypeScript implementation preserves raw/unknown data and distinguishes generator metadata. Compare normalization/Comfy graph/AIR rules with DTT safe reader; do not add Node to the desktop runtime just to parse metadata. |
| 2 | [BooruDatasetTagManagerPlus](https://github.com/storyAura/BooruDatasetTagManagerPlus), PORT | Actual `SecretProtector.cs` and `AiOpenAiClient.cs` provide C# security/provider patterns. DTT currently has no comparable LLM client, so this is prevention of future reinvention, not an existing-code replacement. DPAPI CurrentUser secrets cannot transparently move to another PC; preserve UserData and request key re-entry if future portability is needed. |
| 2 | [TagComplete](https://github.com/DominikDoom/a1111-sd-webui-tagcomplete) / [Neo fork](https://github.com/eduardoabreu81/sd-webui-tagcomplete-neo), PORT | Reuse cursor/token/keyboard interaction conventions. Keep `RuntimeCatalogIndex` ranking and `Prompt` raw syntax. Browser JS is not a reusable WPF control. No autocomplete feature is added now. |
| 2 | [CommunityToolkit.Mvvm](https://github.com/CommunityToolkit/dotnet), REUSE candidate | `Observable.cs` is 49 lines of notification and synchronous/asynchronous command plumbing. Cancellation/error/running support can simplify future command behavior, but replacing all ViewModels would not simplify domain orchestration. Benchmark `Refresh`/`ExecuteAsync`/exception behavior first. |
| 2 | [actionlint](https://github.com/rhysd/actionlint), REUSE candidate | A standalone CI-development checker can replace incomplete hand-written YAML/expression checks. No product dependency; no historical workflow resurrection. Installation/CI adoption is not performed by this research. |
| Future | [DiffPlex](https://github.com/mmanela/diffplex), REUSE | Use generic text diff if a separately approved comparison UI needs it. No current DTT diff algorithm needs replacement. Typed Recipe identity, order/weight and controlled-variable meaning remain domain work. |
| Future | [Civitai official hash API](https://github.com/civitai/civitai-developer-docs/blob/main/site/reference/model-versions.md), WRAP | Existing local SHA makes exact version/base-model/AIR lookup straightforward. Narrow opt-in identity provider/cache is preferable to recreating a Civitai browser/downloader. Retain local facts and user overrides. No network enrichment implemented. |

## Re-evaluated old and recent candidates

Still useful: Neo extensions as backend capabilities/UX reference; Dynamic
Prompts as external expansion; Forge Couple/Regional Prompter/ADetailer as
external conditioning/inpaint; Infinite Image Browsing and the exact historical
`laurigates/comfyui-image-browser` as cache/lightbox/XMP references; LoRA Trigger
Toolkit for source precedence; Forge Neo AI helper and prompt-compiler for
optional provider/preview/validation architecture. They do not justify wholesale
replacement of DTT's existing stores/editor/search.

Important updated or qualified conclusions:

- Prompt All-in-One original and Neo fork are separate host targets; WD14,
  ADetailer and Civitai helper forks likewise have different compatibility.
  A compatible README is not a successful local integration test.
- Tag Explorer claims MIT in README but lacks a standalone license in the
  inspected root. JP Tag Assistant and comfyui-suggest-dt also lack confirmed
  reuse terms. Keep interaction observations; do not silently copy code/data.
- Agent Scheduler has queue/result API and an Apache declaration in README,
  but no current Neo parity proof. Prior #30 HOLD remains valid; current
  one-generation, no-POST-retry Forge API is simpler for the accepted behavior.
- digiKam's GitHub mirror is stale; official release 9.1.0 on June 7, 2026 proves
  it is not abandoned. Current source is KDE Invent, whose page returned 403
  in this session. Its photo/XMP UX remains reference, not a DTT DB replacement.
  [Official release record](https://www.digikam.org/news/).
- LM Studio and Eagle are proprietary applications with documented local APIs,
  not libraries whose code can be copied. Ollama/llama.cpp/KoboldCpp should be
  optional external providers, never an inference engine built into DTT.
  [LM Studio API](https://lmstudio.ai/docs/developer), [Eagle API](https://api.eagle.cool/).
- `multilingual-e5-small` is a CPU/ONNX benchmark candidate, after deterministic
  Japanese intent failures are addressed. Do not assume a particular quantized
  AVX512 artifact works on the user's machine. No benchmark/model download was
  performed. Larger Qwen/BGE/Wiki RAG are quality references, not mandatory
  indexes. [Model card](https://huggingface.co/intfloat/multilingual-e5-small).
- Wiki embedding Apache labels do not resolve CC BY-SA upstream wiki terms;
  aggregate CC0 does not remove source attribution obligations. Such datasets
  remain research/HOLD or REJECT for direct adoption. Historical tag lists with
  zeroed counts cannot establish model-cutoff exposure.

## Current custom code to retain

`Prompt.cs`'s lossless top-level comma/bracket/escape parser, Workspace Undo/raw
surface, canonical validation, bilingual/mixed exact-first search, reviewed
Special/General/adult facets and Home/group semantics are DTT-specific. External
autocomplete/LLM/vector tools do not preserve these contracts.

The accepted manifest/NDJSON reader and compiler already use System.Text.Json
and Microsoft.Data.Sqlite. They are small governed code, not a generic dataset
compiler needing replacement. Keep the Batch A App/compiler separation. CSV
libraries and DuckDB are optional source/research tools; neither belongs in
normal startup or replaces catalog.db/user.db.

Keep paged Generation Library, incremental/cancel-safe scanning, independent
LoRA DB, backups/future-schema refusal, local SHA and user overrides. Upstream
generic gallery/history/model management can inform edges without migrating
these records. Keep bounded PNG and loopback API safety checks, confirmed result
metadata, and no blind POST retries. There is no reason to port a generator,
wildcard language, regional attention engine, queue or LLM runtime into DTT.

## Revised #251 / #253 plan

1. **#251:** retain the safe archive/tool routing checkpoint. Do not revive
   obsolete Issue scripts for framework uniformity. Choose one real source
   adapter need, compare updater retry/sanity logic, and keep primary-source,
   authority, derived output and evidence distinct. Current 2-command
   Maintenance entry point can stay simple; System.CommandLine becomes useful
   only after approved command grammar grows. Research Parquet queries may use
   DuckDB externally. Compiler input bytes/semantic values remain governed.
2. **#253:** begin, if later authorized, with metadata envelope/format adapter
   responsibility, not an App/Core/Data rewrite. First compare JPEG/WebP
   MetadataExtractor; separately compare selected Comfy graph adapters with
   sd-parsers/media-metadata. Measure coverage and failure behavior before any
   replacement. MVVM library adoption is a small independent comparison, not
   permission to rewrite the 1,090-line Workspace ViewModel.
3. **Future feature scopes:** local LLM/provider security, autocomplete,
   Recipe diff/lineage, semantic fallback, XMP export, Civitai enrichment and
   batch/regional controls remain outside Foundation implementation here.
   Existing tools prevent duplicate engine work when those scopes become active.

Before a candidate replaces a current adapter: exact license/dependency version,
old/new fixed fixture outputs, malformed/truncated/bomb limits, raw/unknown data,
multiple-sampler ambiguity, latency/memory, cancellation, offline/failed provider,
UserData byte/schema protection and rollback must be compared. These are targeted
future acceptance conditions, not a demand to rerun Batch A's full parity now.

## Verification / stop point

Matrix checks cover required candidates/fields/enums, exact code paths and source
evidence; source snapshots were read only. No .NET project/package, accepted
authority/compiler, user DB or production installation was changed by research.
The preceding [Batch B checkpoint](BATCH_B_CHECKPOINT_2026-10-03.md) records
353 full regression PASS, 22 opt-in SKIP, targeted protected fixture PASS,
archive recovery verification and protected production hashes. PR CI is checked
against the final branch; final run URLs belong in the PR/final report.

Remaining decisions: exact integration/parity measurements, unresolved artifact
licenses/identities, any future write/export behavior, and explicit next scope.
**STOP here after publishing this report/matrix/PR.** Research completion does
not mean all #251 implementation or #253 is completed, and does not release the
implementation Gate automatically.
