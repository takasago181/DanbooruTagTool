using System.Diagnostics;
using System.Globalization;
using System.Reflection;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Microsoft.VisualBasic.FileIO;

if (args.Length == 2 && args[0] == "--memory-worker")
{
    RunMemoryWorker(args[1]);
    return 0;
}

if (args.Length != 6)
{
    Console.Error.WriteLine("Usage: Issue132ProductionGate <protected-source-root> <live-main-authority-root> <fresh-output-directory> <report.json> <pass_b_full_diff.csv> <route-membership-diff.csv>");
    return 2;
}

var sourceRoot = Path.GetFullPath(args[0]);
var authorityRoot = Path.GetFullPath(args[1]);
var outputDirectory = Path.GetFullPath(args[2]);
var reportPath = Path.GetFullPath(args[3]);
var researchProjectionPath = Path.GetFullPath(args[4]);
var routeMembershipDiffPath = Path.GetFullPath(args[5]);
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
var baselineIntentEntries = Issue118SexualIntentV2Overlay.Bake(new Catalog(unifiedBrowseEntries), authorityRoot, import.SourceHashes);
var baselineEntries = Issue199GeneralFacetOverlay.Bake(new Catalog(baselineIntentEntries));
var issue132ApplyTimer = Stopwatch.StartNew();
var issue132Entries = Issue132RouteOverlay.Bake(new Catalog(unifiedBrowseEntries));
issue132ApplyTimer.Stop();
var candidateIntentEntries = Issue118SexualIntentV2Overlay.Bake(new Catalog(issue132Entries), authorityRoot, import.SourceHashes);
var candidateEntries = Issue199GeneralFacetOverlay.Bake(new Catalog(candidateIntentEntries));
import.SourceHashes[Issue199GeneralFacetOverlay.RelativePath] = Issue199GeneralFacetOverlay.ExpectedSha256;
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

var researchProjection = ReadResearchProjection(researchProjectionPath);
var researchByIdentity = researchProjection.ToDictionary(row => row.IdentityKey, StringComparer.Ordinal);
var beforeBySourceIdentity = beforeIndex.Identities.ToDictionary(
    identity => Issue118SexualIntentOverlay.NormalizeIdentity(identity.Representative.Canonical ?? identity.Representative.English),
    StringComparer.Ordinal);
if (researchByIdentity.Count != 31003 || beforeBySourceIdentity.Count != 31003 ||
    !researchByIdentity.Keys.ToHashSet(StringComparer.Ordinal).SetEquals(beforeBySourceIdentity.Keys))
{
    var onlyResearchIdentities = researchByIdentity.Keys.Except(beforeBySourceIdentity.Keys, StringComparer.Ordinal).Take(10);
    var onlyRuntimeIdentities = beforeBySourceIdentity.Keys.Except(researchByIdentity.Keys, StringComparer.Ordinal).Take(10);
    throw new InvalidDataException($"Research/runtime source-identity population mismatch: research={researchByIdentity.Count}, runtime={beforeBySourceIdentity.Count}, only_research=[{string.Join(',', onlyResearchIdentities)}], only_runtime=[{string.Join(',', onlyRuntimeIdentities)}].");
}

var researchPairs = researchProjection
    .SelectMany(row => row.Routes.Select(route => (Identity: row.IdentityKey, Route: route)))
    .ToHashSet();
var runtimePairs = beforeIndex.Identities
    .SelectMany(identity => identity.RouteIds.Select(route => (Identity: Issue118SexualIntentOverlay.NormalizeIdentity(identity.Representative.Canonical ?? identity.Representative.English), Route: route)))
    .ToHashSet();
var onlyInResearch = researchPairs.Except(runtimePairs).ToHashSet();
var onlyInRuntime = runtimePairs.Except(researchPairs).ToHashSet();
var membershipDiffRows = onlyInResearch.Select(pair => (pair.Identity, pair.Route, ProjectionDiff: "ONLY_IN_RESEARCH"))
    .Concat(onlyInRuntime.Select(pair => (pair.Identity, pair.Route, ProjectionDiff: "ONLY_IN_RUNTIME")))
    .OrderBy(row => row.Route, StringComparer.Ordinal)
    .ThenBy(row => row.Identity, StringComparer.Ordinal)
    .ToArray();
WriteMembershipDiff(routeMembershipDiffPath, membershipDiffRows, researchByIdentity, beforeBySourceIdentity);
var membershipDiffByRoute = UnifiedBrowseTaxonomy.Routes.Select(route =>
{
    var researchCount = researchPairs.Count(pair => pair.Route == route.Id);
    var runtimeCount = runtimePairs.Count(pair => pair.Route == route.Id);
    var actualBrowseCount = beforeIndex.Count(UnifiedBrowseState.Neutral with { PrimaryRouteId = route.Id });
    var researchOnlyCount = onlyInResearch.Count(pair => pair.Route == route.Id);
    var runtimeOnlyCount = onlyInRuntime.Count(pair => pair.Route == route.Id);
    if (runtimeCount != actualBrowseCount)
        throw new InvalidDataException($"Runtime membership set does not match actual browse shelf for {route.Id}: membership={runtimeCount}, browse={actualBrowseCount}.");
    if (researchCount - runtimeCount != researchOnlyCount - runtimeOnlyCount)
        throw new InvalidDataException("Identity-level route diff does not reconcile the projection count delta for " + route.Id);
    return new
    {
        route = route.Id,
        research_current_route_memberships = researchCount,
        actual_runtime_route_memberships = runtimeCount,
        only_in_research = researchOnlyCount,
        only_in_runtime = runtimeOnlyCount,
        actual_runtime_browse_count = actualBrowseCount,
        count_delta_reconciles = researchCount - runtimeCount == researchOnlyCount - runtimeOnlyCount
    };
}).ToArray();
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
    var shelfMatches = after == before + accepted.Add;
    if (!shelfMatches) shelfDifferences.Add($"{route.Id}: actual runtime {before}->{after}; accepted candidate addition {accepted.Add}.");
    var projection = membershipDiffByRoute.Single(row => row.route == route.Id);
    shelfReport.Add(new
    {
        route = route.Id,
        research_current_route_memberships = projection.research_current_route_memberships,
        actual_runtime_before = before,
        only_in_research = projection.only_in_research,
        only_in_runtime = projection.only_in_runtime,
        accepted_candidate_additions = accepted.Add,
        actual_runtime_after = after,
        production_shelf_arithmetic_matches = shelfMatches
    });
}

var searchInputs = SelectSearchInputs(baselineCatalog, acceptedPairs);
var searchReport = new List<object>();
var performanceRegressions = new List<string>();
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
    var searchTiming = PairedMedianMilliseconds(() => baselineCatalog.Search(query).Count, () => candidateCatalog.Search(query).Count);
    var filterTiming = PairedMedianMilliseconds(
        () => beforeIndex.FilterSearchHits(beforeHits, UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual }).Count,
        () => afterIndex.FilterSearchHits(afterHits, UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual }).Count);
    if (searchTiming.CandidateMedianMs - searchTiming.BaselineMedianMs > Math.Max(2.0, searchTiming.BaselineMedianMs * 0.15))
        performanceRegressions.Add($"{kind} search median regression exceeds 15% and 2 ms: {searchTiming.BaselineMedianMs:F4}->{searchTiming.CandidateMedianMs:F4} ms.");
    if (filterTiming.CandidateMedianMs - filterTiming.BaselineMedianMs > Math.Max(0.5, filterTiming.BaselineMedianMs * 0.20))
        performanceRegressions.Add($"{kind} FilterSearchHits median regression exceeds 20% and 0.5 ms: {filterTiming.BaselineMedianMs:F4}->{filterTiming.CandidateMedianMs:F4} ms.");
    searchReport.Add(new { kind, query, hits = beforeHits.Count, before_ranked = beforeHits.Count, after_ranked = afterHits.Count,
        before_search_median_ms = searchTiming.BaselineMedianMs, candidate_search_median_ms = searchTiming.CandidateMedianMs,
        before_search_samples_ms = searchTiming.BaselineSamplesMs, candidate_search_samples_ms = searchTiming.CandidateSamplesMs,
        before_filter_search_hits_median_ms = filterTiming.BaselineMedianMs, candidate_filter_search_hits_median_ms = filterTiming.CandidateMedianMs,
        before_filter_search_hits_samples_ms = filterTiming.BaselineSamplesMs, candidate_filter_search_hits_samples_ms = filterTiming.CandidateSamplesMs,
        paired_rounds = searchTiming.BaselineSamplesMs.Length });
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
    var browseTiming = PairedMedianMilliseconds(() => beforeIndex.Browse(state).Count, () => afterIndex.Browse(state).Count);
    if (browseTiming.CandidateMedianMs - browseTiming.BaselineMedianMs > Math.Max(0.25, browseTiming.BaselineMedianMs * 0.20))
        performanceRegressions.Add($"{name} Browse median regression exceeds 20% and 0.25 ms: {browseTiming.BaselineMedianMs:F4}->{browseTiming.CandidateMedianMs:F4} ms.");
    browseReport.Add(new { name, before_count = beforeRows.Count, candidate_count = afterRows.Count,
        before_browse_median_ms = browseTiming.BaselineMedianMs,
        candidate_browse_median_ms = browseTiming.CandidateMedianMs,
        before_browse_samples_ms = browseTiming.BaselineSamplesMs,
        candidate_browse_samples_ms = browseTiming.CandidateSamplesMs,
        paired_rounds = browseTiming.BaselineSamplesMs.Length });
}

var memoryReport = MeasureIsolatedProcesses(baselinePath, candidatePath, 5);
var memoryReportJson = JsonSerializer.SerializeToElement(memoryReport);
var materialMemoryRegression = memoryReportJson.GetProperty("material_managed_regression").GetBoolean();
if (materialMemoryRegression) shelfDifferences.Add("Isolated-process retained managed memory exceeded the material growth limit.");
shelfDifferences.AddRange(performanceRegressions);

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
    known_allocated_bytes_from_production_build_gate = new
    {
        baseline_and_candidate_catalog_construction_median = 247520632,
        baseline_unified_browse_index_construction_median = 78246136,
        candidate_unified_browse_index_construction_median = 78258136,
        source = "same-condition full production build gate recorded in prior gate report"
    },
    research_vs_runtime_projection = new
    {
        research_authority = "Pass-B current_routes in product-reconciliation/pass_b_full_diff.csv",
        runtime_authority = "live-main full catalog -> UnifiedBrowseIndex identities and RouteIds",
        research_identity_count = researchByIdentity.Count,
        runtime_identity_count = beforeByKey.Count,
        only_in_research_membership_count = onlyInResearch.Count,
        only_in_runtime_membership_count = onlyInRuntime.Count,
        membership_diff_csv = Path.GetFileName(routeMembershipDiffPath),
        all_route_count_deltas_reconciled = membershipDiffByRoute.All(row => row.count_delta_reconciles),
        routes = membershipDiffByRoute
    },
    isolated_process_memory = memoryReport,
    material_performance_regressions = performanceRegressions,
    performance_regression_thresholds = new
    {
        search = "greater than both 15% and 2.0 ms median increase",
        filter_search_hits = "greater than both 20% and 0.5 ms median increase",
        browse = "greater than both 20% and 0.25 ms median increase"
    },
    search_and_filter_search = searchReport,
    browse = browseReport,
    shelf_validation = shelfReport,
    user_data_touched_at_gate = false,
    production_apply_at_gate = false,
    main_modified_at_gate = false
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

static IReadOnlyList<(string IdentityKey, string[] Routes)> ReadResearchProjection(string path)
{
    using var stream = File.OpenRead(path);
    using var parser = new TextFieldParser(stream, System.Text.Encoding.UTF8)
    {
        TextFieldType = FieldType.Delimited,
        HasFieldsEnclosedInQuotes = true,
        TrimWhiteSpace = false
    };
    parser.SetDelimiters(",");
    var header = parser.ReadFields() ?? throw new InvalidDataException("Empty Pass-B full diff.");
    var identityIndex = Array.IndexOf(header, "identity_key");
    var routesIndex = Array.IndexOf(header, "current_routes");
    if (identityIndex < 0 || routesIndex < 0) throw new InvalidDataException("Pass-B full diff lacks identity_key/current_routes columns.");
    var rows = new List<(string IdentityKey, string[] Routes)>();
    while (!parser.EndOfData)
    {
        var fields = parser.ReadFields() ?? [];
        if (fields.Length != header.Length || string.IsNullOrWhiteSpace(fields[identityIndex]))
            throw new InvalidDataException("Pass-B current route row is malformed.");
        var identity = Issue118SexualIntentOverlay.NormalizeIdentity(fields[identityIndex]);
        var routes = JsonSerializer.Deserialize<string[]>(fields[routesIndex]) ?? [];
        if (routes.Distinct(StringComparer.Ordinal).Count() != routes.Length)
            throw new InvalidDataException("Pass-B current route row contains duplicates for " + identity);
        rows.Add((identity, routes));
    }
    return rows;
}

static void WriteMembershipDiff(
    string path,
    IReadOnlyList<(string Identity, string Route, string ProjectionDiff)> rows,
    IReadOnlyDictionary<string, (string IdentityKey, string[] Routes)> researchByIdentity,
    IReadOnlyDictionary<string, UnifiedBrowseIdentity> runtimeByIdentity)
{
    Directory.CreateDirectory(Path.GetDirectoryName(path)!);
    using var writer = new StreamWriter(path, append: false, new System.Text.UTF8Encoding(false));
    writer.WriteLine("identity_key,route_id,research_current_route_membership,actual_runtime_route_membership,projection_diff,research_source_authority,runtime_source_authority");
    foreach (var row in rows)
    {
        var research = researchByIdentity[row.Identity];
        var runtime = runtimeByIdentity[row.Identity];
        var researchAuthority = "Pass-B full diff current_routes; identity=" + research.IdentityKey;
        var runtimeAuthority = string.Join(";", runtime.BackingEntries
            .Select(entry => entry.Id + ":" + entry.EffectiveCategory + ":" + (entry.Canonical ?? entry.English))
            .OrderBy(value => value, StringComparer.Ordinal));
        var fields = new[]
        {
            row.Identity,
            row.Route,
            research.Routes.Contains(row.Route, StringComparer.Ordinal) ? "YES" : "NO",
            runtime.RouteIds.Contains(row.Route) ? "YES" : "NO",
            row.ProjectionDiff,
            researchAuthority,
            runtimeAuthority
        };
        writer.WriteLine(string.Join(',', fields.Select(Csv)));
    }
}

static string Csv(string value) => "\"" + value.Replace("\"", "\"\"", StringComparison.Ordinal) + "\"";

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

static (double BaselineMedianMs, double CandidateMedianMs, double[] BaselineSamplesMs, double[] CandidateSamplesMs) PairedMedianMilliseconds(Func<int> baseline, Func<int> candidate)
{
    for (var i = 0; i < 2; i++)
    {
        _ = baseline();
        _ = candidate();
    }
    const int rounds = 5;
    const int samplesPerRound = 7;
    var baselineSamples = new double[rounds * samplesPerRound];
    var candidateSamples = new double[rounds * samplesPerRound];
    var sampleIndex = 0;
    for (var round = 0; round < rounds; round++)
    for (var sample = 0; sample < samplesPerRound; sample++)
    {
        var baselineFirst = (round + sample) % 2 == 0;
        baselineSamples[sampleIndex] = TimeAction(baselineFirst ? baseline : candidate);
        candidateSamples[sampleIndex] = TimeAction(baselineFirst ? candidate : baseline);
        sampleIndex++;
    }
    return (MedianDouble(baselineSamples.ToList()), MedianDouble(candidateSamples.ToList()), baselineSamples, candidateSamples);
}

static double TimeAction(Func<int> action)
{
    var timer = Stopwatch.StartNew();
    _ = action();
    timer.Stop();
    return timer.Elapsed.TotalMilliseconds;
}

static (T Value, double ElapsedMilliseconds) Time<T>(Func<T> action)
{
    var timer = Stopwatch.StartNew();
    var value = action();
    timer.Stop();
    return (value, timer.Elapsed.TotalMilliseconds);
}

static object MeasureIsolatedProcesses(string baselinePath, string candidatePath, int repetitions)
{
    var baseline = new List<JsonElement>();
    var candidate = new List<JsonElement>();
    for (var i = 0; i < repetitions; i++)
    {
        if (i % 2 == 0)
        {
            baseline.Add(RunMemoryWorkerProcess(baselinePath));
            candidate.Add(RunMemoryWorkerProcess(candidatePath));
        }
        else
        {
            candidate.Add(RunMemoryWorkerProcess(candidatePath));
            baseline.Add(RunMemoryWorkerProcess(baselinePath));
        }
    }

    var metrics = new[]
    {
        "catalog_managed_bytes", "combined_managed_bytes", "index_managed_delta_bytes",
        "catalog_private_bytes", "combined_private_bytes", "index_private_delta_bytes",
        "catalog_working_set_bytes", "combined_working_set_bytes", "index_working_set_delta_bytes"
    };
    var metricReport = new Dictionary<string, object>(StringComparer.Ordinal);
    foreach (var metric in metrics)
    {
        var before = baseline.Select(sample => sample.GetProperty(metric).GetInt64()).ToArray();
        var after = candidate.Select(sample => sample.GetProperty(metric).GetInt64()).ToArray();
        metricReport[metric] = new { baseline_median = MedianLong(before.ToList()), candidate_median = MedianLong(after.ToList()), baseline_samples = before, candidate_samples = after };
    }
    var baselineCombined = MedianLong(baseline.Select(sample => sample.GetProperty("combined_managed_bytes").GetInt64()).ToList());
    var candidateCombined = MedianLong(candidate.Select(sample => sample.GetProperty("combined_managed_bytes").GetInt64()).ToList());
    var baselineIndex = MedianLong(baseline.Select(sample => sample.GetProperty("index_managed_delta_bytes").GetInt64()).ToList());
    var candidateIndex = MedianLong(candidate.Select(sample => sample.GetProperty("index_managed_delta_bytes").GetInt64()).ToList());
    var materialLimitBytes = Math.Max(1_000_000, baselineCombined / 100);
    return new
    {
        process_isolation = true,
        repetitions_per_build = repetitions,
        collection_method = "full blocking compacting GC; objects held alive through measurement",
        material_managed_growth_limit_bytes = materialLimitBytes,
        material_growth_policy = "candidate combined managed retained bytes may not exceed baseline by more than 1% or 1,000,000 bytes, whichever is larger",
        material_managed_regression = candidateCombined - baselineCombined > materialLimitBytes || candidateIndex - baselineIndex > materialLimitBytes,
        metrics = metricReport
    };
}

static void RunMemoryWorker(string catalogPath)
{
    var process = Process.GetCurrentProcess();
    var catalog = new Catalog(CatalogDatabase.Open(catalogPath).Entries);
    ForceCollection();
    var catalogMemory = SampleProcessMemory(process);
    var specialBrowse = SpecialBrowseV2Overlay.FromCatalog(catalog);
    var browseIndex = new UnifiedBrowseIndex(catalog, specialBrowse);
    ForceCollection();
    var combinedMemory = SampleProcessMemory(process);
    var sample = new
    {
        catalog_managed_bytes = catalogMemory.Managed,
        combined_managed_bytes = combinedMemory.Managed,
        index_managed_delta_bytes = combinedMemory.Managed - catalogMemory.Managed,
        catalog_private_bytes = catalogMemory.Private,
        combined_private_bytes = combinedMemory.Private,
        index_private_delta_bytes = combinedMemory.Private - catalogMemory.Private,
        catalog_working_set_bytes = catalogMemory.WorkingSet,
        combined_working_set_bytes = combinedMemory.WorkingSet,
        index_working_set_delta_bytes = combinedMemory.WorkingSet - catalogMemory.WorkingSet
    };
    Console.WriteLine(JsonSerializer.Serialize(sample));
    GC.KeepAlive(browseIndex);
    GC.KeepAlive(specialBrowse);
    GC.KeepAlive(catalog);
}

static (long Managed, long Private, long WorkingSet) SampleProcessMemory(Process process)
{
    var managed = GC.GetTotalMemory(forceFullCollection: true);
    process.Refresh();
    return (managed, process.PrivateMemorySize64, process.WorkingSet64);
}

static JsonElement RunMemoryWorkerProcess(string catalogPath)
{
    var entryAssembly = Assembly.GetEntryAssembly()?.Location ?? throw new InvalidOperationException("Gate assembly path is unavailable.");
    var start = new ProcessStartInfo("dotnet") { UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true, CreateNoWindow = true };
    start.ArgumentList.Add(entryAssembly);
    start.ArgumentList.Add("--memory-worker");
    start.ArgumentList.Add(catalogPath);
    using var process = Process.Start(start) ?? throw new InvalidOperationException("Could not start isolated memory worker.");
    var stdout = process.StandardOutput.ReadToEnd();
    var stderr = process.StandardError.ReadToEnd();
    process.WaitForExit();
    if (process.ExitCode != 0) throw new InvalidOperationException("Memory worker failed: " + stderr);
    return JsonDocument.Parse(stdout).RootElement.Clone();
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
