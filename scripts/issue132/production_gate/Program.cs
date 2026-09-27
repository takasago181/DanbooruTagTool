using System.Diagnostics;
using System.Globalization;
using System.Reflection;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Microsoft.VisualBasic.FileIO;

if (args.Length != 4)
{
    Console.Error.WriteLine("Usage: Issue132ProductionGate <protected-source-root> <live-main-authority-root> <fresh-output-directory> <report.json>");
    return 2;
}

var sourceRoot = Path.GetFullPath(args[0]);
var authorityRoot = Path.GetFullPath(args[1]);
var outputDirectory = Path.GetFullPath(args[2]);
var reportPath = Path.GetFullPath(args[3]);
var baselinePath = Path.Combine(outputDirectory, "baseline", "Data", "catalog.db");
var candidatePath = Path.Combine(outputDirectory, "candidate", "Data", "catalog.db");
if (Directory.Exists(outputDirectory) && Directory.EnumerateFileSystemEntries(outputDirectory).Any())
    throw new IOException("Output directory must be empty: " + outputDirectory);
Directory.CreateDirectory(outputDirectory);
Directory.CreateDirectory(Path.GetDirectoryName(baselinePath)!);
Directory.CreateDirectory(Path.GetDirectoryName(candidatePath)!);
Directory.CreateDirectory(Path.GetDirectoryName(reportPath)!);

var acceptedPairs = ReadAcceptedPairs();
var sourceBuildTimer = Stopwatch.StartNew();
var import = AcceptedAssetImporter.Read(sourceRoot, authorityRoot, CatalogBuildProfile.Full);
var specialBrowseEntries = SpecialBrowseV2Overlay.Bake(new Catalog(import.Entries));
var unifiedBrowseEntries = UnifiedBrowseOverlay.Bake(new Catalog(specialBrowseEntries), authorityRoot);
var baselineEntries = Issue118SexualIntentV2Overlay.Bake(new Catalog(unifiedBrowseEntries), authorityRoot, import.SourceHashes);
var issue132ApplyTimer = Stopwatch.StartNew();
var issue132Entries = Issue132RouteOverlay.Bake(new Catalog(unifiedBrowseEntries));
issue132ApplyTimer.Stop();
var candidateEntries = Issue118SexualIntentV2Overlay.Bake(new Catalog(issue132Entries), authorityRoot, import.SourceHashes);
sourceBuildTimer.Stop();
var baselineBuildTimer = Stopwatch.StartNew();
CatalogDatabase.Build(baselinePath, baselineEntries, JsonSerializer.Serialize(import.SourceHashes));
baselineBuildTimer.Stop();
var candidateBuildTimer = Stopwatch.StartNew();
CatalogDatabase.Build(candidatePath, candidateEntries, JsonSerializer.Serialize(import.SourceHashes));
candidateBuildTimer.Stop();
var baselineOpen = Time(() => CatalogDatabase.Open(baselinePath));
var baselineCatalog = new Catalog(baselineOpen.Value.Entries);
var candidateOpen = Time(() => CatalogDatabase.Open(candidatePath));
var candidateCatalog = new Catalog(candidateOpen.Value.Entries);

var baselineSpecialBrowse = SpecialBrowseV2Overlay.FromCatalog(baselineCatalog);
var candidateSpecialBrowse = SpecialBrowseV2Overlay.FromCatalog(candidateCatalog);
var beforeIndex = new UnifiedBrowseIndex(baselineCatalog, baselineSpecialBrowse);
var afterIndex = new UnifiedBrowseIndex(candidateCatalog, candidateSpecialBrowse);
var beforeByKey = beforeIndex.Identities.ToDictionary(identity => identity.IdentityKey, StringComparer.Ordinal);
var afterByKey = afterIndex.Identities.ToDictionary(identity => identity.IdentityKey, StringComparer.Ordinal);
if (!beforeByKey.Keys.ToHashSet(StringComparer.Ordinal).SetEquals(afterByKey.Keys))
    throw new InvalidDataException("Candidate changed ordinary identity coverage.");

var sourceIdentityMap = beforeIndex.Identities
    .SelectMany(identity => identity.BackingEntries.Select(entry =>
        (SourceKey: Issue118SexualIntentOverlay.NormalizeIdentity(entry.Canonical ?? entry.English), IdentityKey: identity.IdentityKey)))
    .GroupBy(row => row.SourceKey, StringComparer.Ordinal)
    .ToDictionary(group => group.Key, group => group.Select(row => row.IdentityKey).Distinct(StringComparer.Ordinal).ToArray(), StringComparer.Ordinal);
var expected = acceptedPairs.Select(pair =>
{
    var key = Issue118SexualIntentOverlay.NormalizeIdentity(pair.IdentityKey);
    if (!sourceIdentityMap.TryGetValue(key, out var matches) || matches.Length != 1)
        throw new InvalidDataException("Accepted pair identity did not resolve exactly: " + pair.IdentityKey);
    return (Identity: matches[0], Route: pair.RouteId);
}).ToHashSet();
var actualAdditions = new HashSet<(string Identity, string Route)>();
var actualRemovals = new HashSet<(string Identity, string Route)>();
var changedIdentities = new HashSet<string>(StringComparer.Ordinal);
foreach (var (key, before) in beforeByKey)
{
    var after = afterByKey[key];
    foreach (var route in before.RouteIds.Except(after.RouteIds, StringComparer.Ordinal)) actualRemovals.Add((key, route));
    foreach (var route in after.RouteIds.Except(before.RouteIds, StringComparer.Ordinal)) actualAdditions.Add((key, route));
    if (!before.RouteIds.SetEquals(after.RouteIds)) changedIdentities.Add(key);
}
if (changedIdentities.Count != 273 || actualAdditions.Count != 274 || actualRemovals.Count != 0 || !actualAdditions.SetEquals(expected))
    throw new InvalidDataException($"Route delta mismatch: identities={changedIdentities.Count}, additions={actualAdditions.Count}, removals={actualRemovals.Count}, expected_pairs_match={actualAdditions.SetEquals(expected)}");

if (baselineCatalog.Entries.Count != candidateCatalog.Entries.Count)
    throw new InvalidDataException("Catalog entry count changed.");
for (var index = 0; index < baselineCatalog.Entries.Count; index++)
{
    var before = baselineCatalog.Entries[index];
    var after = candidateCatalog.Entries[index];
    if (before.Id != after.Id ||
        JsonSerializer.Serialize(before with { UnifiedBrowseRouteIds = [] }) !=
        JsonSerializer.Serialize(after with { UnifiedBrowseRouteIds = [] }))
        throw new InvalidDataException("Non-#132 metadata changed at catalog row " + index.ToString(CultureInfo.InvariantCulture));
}

var acceptedShelves = new Dictionary<string, (int Before, int Add)> (StringComparer.Ordinal)
{
    ["ACTION_CONTACT"] = (3928, 18), ["BODY_SITE"] = (2371, 97), ["CLOTHING_EXPOSURE"] = (8972, 11),
    ["COLOR_PATTERN_SHAPE"] = (682, 0), ["COMPOSITION_CAMERA"] = (181, 17), ["CONTENT_RATING"] = (52, 1),
    ["EXPRESSION_GAZE"] = (447, 0), ["FLUID_EXCRETION"] = (217, 15), ["HAIR_FACE"] = (789, 4),
    ["LIGHT_TIME_WEATHER"] = (315, 9), ["LIVING"] = (1330, 0), ["NONHUMAN_TRANSFORM"] = (101, 0),
    ["PEOPLE_COUNT"] = (794, 10), ["POSE_POSITION"] = (809, 52), ["RELATION_ROLE"] = (102, 15),
    ["SCENE_BACKGROUND"] = (1075, 16), ["STYLE_PROCESSING"] = (1027, 4), ["TEXT_SYMBOL"] = (1080, 0),
    ["TOOL_OBJECT"] = (5691, 5)
};
var shelfReport = new List<object>();
var shelfDifferences = new List<string>();
foreach (var route in UnifiedBrowseTaxonomy.Routes)
{
    var before = beforeIndex.Count(UnifiedBrowseState.Neutral with { PrimaryRouteId = route.Id });
    var after = afterIndex.Count(UnifiedBrowseState.Neutral with { PrimaryRouteId = route.Id });
    var accepted = acceptedShelves[route.Id];
    var shelfMatches = before == accepted.Before && after == accepted.Before + accepted.Add;
    if (!shelfMatches) shelfDifferences.Add($"{route.Id}: live-main build {before}->{after}; accepted report {accepted.Before}->{accepted.Before + accepted.Add}.");
    shelfReport.Add(new { route = route.Id, before, additions = after - before, after, accepted_before = accepted.Before, accepted_additions = accepted.Add, shelf_matches = shelfMatches });
}

var searchInputs = SelectSearchInputs(baselineCatalog, acceptedPairs);
var searchReport = new List<object>();
foreach (var (kind, query) in searchInputs)
{
    var beforeHits = baselineCatalog.Search(query);
    var afterHits = candidateCatalog.Search(query);
    if (!beforeHits.Select(hit => (hit.Entry.Id, hit.Rank)).SequenceEqual(afterHits.Select(hit => (hit.Entry.Id, hit.Rank))))
        throw new InvalidDataException("Search ordering changed for " + kind + " query.");
    foreach (var filterState in new[]
    {
        UnifiedBrowseState.Neutral,
        UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.GeneralPurpose },
        UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual },
        UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual, BodySiteIds = new HashSet<string>(["MOUTH_ORAL"]), ThemeIds = new HashSet<string>(["BDSM_RESTRAINT"]) }
    })
    {
        var beforeFiltered = beforeIndex.FilterSearchHits(beforeHits, filterState);
        var afterFiltered = afterIndex.FilterSearchHits(afterHits, filterState);
        if (!beforeFiltered.Select(hit => (hit.Entry.Id, hit.Rank)).SequenceEqual(afterFiltered.Select(hit => (hit.Entry.Id, hit.Rank))))
            throw new InvalidDataException("Browse/content/body/theme search filtering changed for " + kind + " query.");
    }
    var beforeTiming = MedianMilliseconds(() => baselineCatalog.Search(query).Count);
    var afterTiming = MedianMilliseconds(() => candidateCatalog.Search(query).Count);
    var beforeFilterTiming = MedianMilliseconds(() => beforeIndex.FilterSearchHits(beforeHits, UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual }).Count);
    var afterFilterTiming = MedianMilliseconds(() => afterIndex.FilterSearchHits(afterHits, UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual }).Count);
    searchReport.Add(new { kind, query, hits = beforeHits.Count, before_ranked = beforeHits.Count, after_ranked = afterHits.Count,
        before_search_median_ms = beforeTiming, candidate_search_median_ms = afterTiming,
        before_filter_search_hits_median_ms = beforeFilterTiming, candidate_filter_search_hits_median_ms = afterFilterTiming });
}

var browseReport = new List<object>();
var browseStates = new List<(string Name, UnifiedBrowseState State)>
{
    ("long_neutral", UnifiedBrowseState.Neutral),
    ("sexual_neutral", UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual }),
    ("generalpurpose_neutral", UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.GeneralPurpose }),
    ("sexual_body_theme", UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual, BodySiteIds = new HashSet<string>(["MOUTH_ORAL"]), ThemeIds = new HashSet<string>(["BDSM_RESTRAINT"]) })
};
foreach (var routeId in new[] { "BODY_SITE", "POSE_POSITION", "ACTION_CONTACT", "COMPOSITION_CAMERA", "FLUID_EXCRETION", "RELATION_ROLE" })
{
    browseStates.Add((routeId + "_all", UnifiedBrowseState.Neutral with { PrimaryRouteId = routeId }));
    browseStates.Add((routeId + "_sexual", UnifiedBrowseState.Neutral with { PrimaryRouteId = routeId, ContentIntent = ContentIntentFilter.Sexual }));
}
foreach (var (name, state) in browseStates)
{
    var beforeRows = beforeIndex.Browse(state);
    var afterRows = afterIndex.Browse(state);
    var expectedAdds = state.PrimaryRouteId is { } route && acceptedShelves.TryGetValue(route, out var value) ? value.Add : 0;
    if (state.PrimaryRouteId is null && !beforeRows.Select(row => row.Canonical).ToHashSet(StringComparer.Ordinal).SetEquals(afterRows.Select(row => row.Canonical)))
        throw new InvalidDataException("Unconstrained browse result changed for " + name);
    if (state.PrimaryRouteId is not null && afterRows.Count - beforeRows.Count != expectedAdds && state.ContentIntent == ContentIntentFilter.All)
        throw new InvalidDataException("Browse delta does not match accepted route additions for " + name);
    browseReport.Add(new { name, before_count = beforeRows.Count, candidate_count = afterRows.Count,
        before_browse_median_ms = MedianMilliseconds(() => beforeIndex.Browse(state).Count),
        candidate_browse_median_ms = MedianMilliseconds(() => afterIndex.Browse(state).Count) });
}

var baselineCatalogMeasure = MeasureRetained(() => new Catalog(baselineCatalog.Entries));
var candidateCatalogMeasure = MeasureRetained(() => new Catalog(candidateCatalog.Entries));
var baselineUnifiedMeasure = MeasureRetained(() => new UnifiedBrowseIndex(baselineCatalog, baselineSpecialBrowse));
var candidateUnifiedMeasure = MeasureRetained(() => new UnifiedBrowseIndex(candidateCatalog, candidateSpecialBrowse));

var report = new
{
    schema_version = "issue132-production-delta-gate-v1",
    status = shelfDifferences.Count == 0 ? "PASS" : "BLOCKED",
    blockers = shelfDifferences,
    live_main_head = "e5d0f7d954ff491c1a5661a0652e6142f2b0d08d",
    semantic_research_head = "d74352be827c52a24888fbfc8bf71b8982627130",
    product_reconciliation_head = "de450958eb598a2c7c3a34b112f139dfba617c6e",
    source_root = "local protected source root; machine path omitted",
    live_main_authority_root = "live-main checkout; machine path omitted",
    protected_source_hashes = import.SourceHashes,
    source_and_overlay_construction_ms = sourceBuildTimer.Elapsed.TotalMilliseconds,
    issue132_overlay_apply_ms = issue132ApplyTimer.Elapsed.TotalMilliseconds,
    baseline_catalog_build_ms = baselineBuildTimer.Elapsed.TotalMilliseconds,
    candidate_catalog_build_ms = candidateBuildTimer.Elapsed.TotalMilliseconds,
    baseline_catalog_sha256 = Hash(baselinePath),
    baseline_catalog_length = new FileInfo(baselinePath).Length,
    source_pair_count = acceptedPairs.Count,
    source_identity_count = acceptedPairs.Select(pair => pair.IdentityKey).Distinct(StringComparer.Ordinal).Count(),
    baseline_entry_count = baselineCatalog.Entries.Count,
    candidate_entry_count = candidateCatalog.Entries.Count,
    ordinary_identity_count_before = beforeByKey.Count,
    ordinary_identity_count_after = afterByKey.Count,
    actual_route_additions = actualAdditions.Count,
    changed_identity_count = changedIdentities.Count,
    unexpected_changed_identity_count = changedIdentities.Count(key => !expected.Any(pair => pair.Identity == key)),
    route_removals = actualRemovals.Count,
    non_issue132_metadata_changes = 0,
    catalog_database_open_ms = new { baseline = baselineOpen.ElapsedMilliseconds, candidate = candidateOpen.ElapsedMilliseconds },
    catalog_build_candidate_ms = candidateBuildTimer.Elapsed.TotalMilliseconds,
    candidate_catalog_path = "isolated temporary candidate catalog; machine path omitted",
    candidate_catalog_sha256 = Hash(candidatePath),
    candidate_catalog_length = new FileInfo(candidatePath).Length,
    catalog_construction = new
    {
        baseline = new { median_ms = baselineCatalogMeasure.median_ms, median_allocated_bytes = baselineCatalogMeasure.median_allocated_bytes, median_retained_heap_delta_bytes = baselineCatalogMeasure.median_retained_heap_delta_bytes },
        candidate = new { median_ms = candidateCatalogMeasure.median_ms, median_allocated_bytes = candidateCatalogMeasure.median_allocated_bytes, median_retained_heap_delta_bytes = candidateCatalogMeasure.median_retained_heap_delta_bytes }
    },
    unified_browse_index_construction = new
    {
        baseline = new { median_ms = baselineUnifiedMeasure.median_ms, median_allocated_bytes = baselineUnifiedMeasure.median_allocated_bytes, median_retained_heap_delta_bytes = baselineUnifiedMeasure.median_retained_heap_delta_bytes },
        candidate = new { median_ms = candidateUnifiedMeasure.median_ms, median_allocated_bytes = candidateUnifiedMeasure.median_allocated_bytes, median_retained_heap_delta_bytes = candidateUnifiedMeasure.median_retained_heap_delta_bytes }
    },
    search_and_filter_search = searchReport,
    browse = browseReport,
    shelf_validation = shelfReport,
    user_data_touched = false,
    production_apply = false,
    main_modified = false
};
File.WriteAllText(reportPath, JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }));
Console.WriteLine(JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }));
return 0;

static IReadOnlyList<(string IdentityKey, string RouteId)> ReadAcceptedPairs()
{
    var assembly = typeof(Issue132RouteOverlay).Assembly;
    var resourceName = assembly.GetManifestResourceNames().Single(name => name.EndsWith("issue132_secondary_routes_v1.csv", StringComparison.Ordinal));
    using var stream = assembly.GetManifestResourceStream(resourceName)!;
    using var parser = new TextFieldParser(stream, System.Text.Encoding.UTF8)
    {
        TextFieldType = FieldType.Delimited,
        HasFieldsEnclosedInQuotes = true,
        TrimWhiteSpace = false
    };
    parser.SetDelimiters(",");
    _ = parser.ReadFields();
    var rows = new List<(string IdentityKey, string RouteId)>();
    while (!parser.EndOfData)
    {
        var row = parser.ReadFields()!;
        rows.Add((row[0], row[1]));
    }
    return rows;
}

static IReadOnlyList<(string Kind, string Query)> SelectSearchInputs(ICatalog catalog, IReadOnlyList<(string IdentityKey, string RouteId)> pairs)
{
    var target = catalog.Entries.First(entry => entry.EffectiveCategory is "General" or "Special" &&
        string.Equals(entry.Canonical, pairs[0].IdentityKey, StringComparison.Ordinal));
    var japaneseQuery = !string.IsNullOrWhiteSpace(target.Japanese)
        ? target.Japanese
        : target.JapaneseSearch.First(term => term.Any(character => character is >= '\u3040' and <= '\u30ff' or >= '\u3400' and <= '\u9fff'));
    return
    [
        ("english", target.Canonical!),
        ("japanese", japaneseQuery),
        ("mixed", target.Canonical!.Split('_')[0] + " " + japaneseQuery)
    ];
}

static double MedianMilliseconds(Func<int> action)
{
    for (var i = 0; i < 2; i++) _ = action();
    var times = new double[7];
    for (var i = 0; i < times.Length; i++)
    {
        var timer = Stopwatch.StartNew();
        _ = action();
        timer.Stop();
        times[i] = timer.Elapsed.TotalMilliseconds;
    }
    return MedianDouble(times.ToList());
}

static (T Value, double ElapsedMilliseconds) Time<T>(Func<T> action)
{
    var timer = Stopwatch.StartNew();
    var value = action();
    timer.Stop();
    return (value, timer.Elapsed.TotalMilliseconds);
}

static (double median_ms, long median_allocated_bytes, long median_retained_heap_delta_bytes) MeasureRetained<T>(Func<T> factory) where T : class
{
    _ = factory();
    var elapsed = new List<double>();
    var allocations = new List<long>();
    for (var i = 0; i < 5; i++)
    {
        ForceCollection();
        var allocatedBefore = GC.GetAllocatedBytesForCurrentThread();
        var timer = Stopwatch.StartNew();
        var value = factory();
        timer.Stop();
        allocations.Add(GC.GetAllocatedBytesForCurrentThread() - allocatedBefore);
        elapsed.Add(timer.Elapsed.TotalMilliseconds);
        GC.KeepAlive(value);
    }

    ForceCollection();
    var retained = new List<long>();
    for (var i = 0; i < 5; i++)
    {
        ForceCollection();
        var memoryBefore = GC.GetTotalMemory(true);
        var retainedValue = factory();
        ForceCollection();
        retained.Add(GC.GetTotalMemory(true) - memoryBefore);
        GC.KeepAlive(retainedValue);
    }
    return (MedianDouble(elapsed), MedianLong(allocations), MedianLong(retained));
}

static long MedianLong(List<long> values) => values.Order().ElementAt(values.Count / 2);
static double MedianDouble(List<double> values) => values.Order().ElementAt(values.Count / 2);
static void ForceCollection()
{
    GC.Collect(GC.MaxGeneration, GCCollectionMode.Forced, blocking: true, compacting: true);
    GC.WaitForPendingFinalizers();
    GC.Collect(GC.MaxGeneration, GCCollectionMode.Forced, blocking: true, compacting: true);
}
static string Hash(string path)
{
    using var stream = File.OpenRead(path);
    return Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(stream)).ToLowerInvariant();
}
