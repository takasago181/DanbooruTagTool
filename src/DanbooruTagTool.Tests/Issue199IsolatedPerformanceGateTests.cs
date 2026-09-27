using System.Diagnostics;
using System.IO;
using System.Runtime.CompilerServices;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue199PerformanceFactAttribute : FactAttribute
{
    public Issue199PerformanceFactAttribute()
    {
        if (Environment.GetEnvironmentVariable("ISSUE199_BASELINE_CATALOG") is null ||
            Environment.GetEnvironmentVariable("ISSUE199_CANDIDATE_CATALOG") is null)
            Skip = "Requires isolated live-main and candidate catalog paths; see Issue #199 performance gate instructions.";
    }
}

public sealed class Issue199IsolatedPerformanceGateTests(ITestOutputHelper output)
{
    [Issue199PerformanceFact]
    public void FreshLiveMainBaselineVersusFacetCandidatePerformanceGate()
    {
        var baselinePath = Environment.GetEnvironmentVariable("ISSUE199_BASELINE_CATALOG");
        var candidatePath = Environment.GetEnvironmentVariable("ISSUE199_CANDIDATE_CATALOG");
        if (string.IsNullOrWhiteSpace(baselinePath) || string.IsNullOrWhiteSpace(candidatePath)) return;

        WarmFileCache(baselinePath);
        WarmFileCache(candidatePath);
        var baselineRuns = new List<GateSide>();
        var candidateRuns = new List<GateSide>();
        for (var run = 0; run < 3; run++)
        {
            if (run == 1)
            {
                candidateRuns.Add(MeasureCatalog(candidatePath));
                baselineRuns.Add(MeasureCatalog(baselinePath));
            }
            else
            {
                baselineRuns.Add(MeasureCatalog(baselinePath));
                candidateRuns.Add(MeasureCatalog(candidatePath));
            }
        }
        var baseline = Aggregate(baselineRuns);
        var candidate = Aggregate(candidateRuns);
        var comparisons = Compare(baseline, candidate);
        var report = new
        {
            measurementCondition = "Both catalog files were read into the OS file cache before timed open/load; managed GC was forced before each side.",
            measurementRunsPerSide = 3,
            executionOrder = "baseline/candidate, candidate/baseline, baseline/candidate",
            fullCatalogBuildMs = new
            {
                baseline = ParseOptionalDouble("ISSUE199_BASELINE_BUILD_MS"),
                candidate = ParseOptionalDouble("ISSUE199_CANDIDATE_BUILD_MS")
            },
            baseline = baseline with { DatabasePath = null },
            candidate = candidate with { DatabasePath = null },
            catalogDbBytesDelta = candidate.CatalogDbBytes - baseline.CatalogDbBytes,
            comparisons
        };
        var json = JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true });
        output.WriteLine(json);
        var reportPath = Environment.GetEnvironmentVariable("ISSUE199_PERF_REPORT_PATH");
        if (!string.IsNullOrWhiteSpace(reportPath))
            File.WriteAllText(reportPath, json + Environment.NewLine);

        Assert.False(comparisons.SearchBlocked, "Search median regression exceeds both #132 thresholds.");
        Assert.False(comparisons.FilterSearchHitsBlocked, "FilterSearchHits median regression exceeds both #132 thresholds.");
        Assert.False(comparisons.BrowseBlocked, "Browse median regression exceeds both #132 thresholds.");
        Assert.False(comparisons.ManagedMemoryBlocked, "Combined retained managed memory exceeds the #132 threshold.");
    }

    private static double? ParseOptionalDouble(string name)
        => double.TryParse(Environment.GetEnvironmentVariable(name), System.Globalization.NumberStyles.Float,
            System.Globalization.CultureInfo.InvariantCulture, out var value) ? value : null;

    private static void WarmFileCache(string path)
    {
        using var stream = File.OpenRead(path);
        var buffer = new byte[1024 * 1024];
        while (stream.Read(buffer, 0, buffer.Length) > 0) { }
    }

    private static GateSide MeasureCatalog(string path)
    {
        GC.Collect();
        GC.WaitForPendingFinalizers();
        GC.Collect();
        return MeasureCatalogNoInline(path);
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    private static GateSide MeasureCatalogNoInline(string path)
    {
        var retainedBefore = GC.GetTotalMemory(forceFullCollection: true);
        var loadWatch = Stopwatch.StartNew();
        var catalog = (IRuntimeCatalogQuery)CatalogDatabase.Open(path);
        loadWatch.Stop();

        GC.Collect();
        var retainedBeforeIndex = GC.GetTotalMemory(forceFullCollection: true);
        var allocatedBeforeIndex = GC.GetAllocatedBytesForCurrentThread();
        var indexWatch = Stopwatch.StartNew();
        var index = new UnifiedBrowseIndex(catalog);
        indexWatch.Stop();
        var indexAllocatedBytes = GC.GetAllocatedBytesForCurrentThread() - allocatedBeforeIndex;
        var indexRetainedBytes = GC.GetTotalMemory(forceFullCollection: true) - retainedBeforeIndex;
        var combinedRetainedBytes = GC.GetTotalMemory(forceFullCollection: true) - retainedBefore;
        var filterHits = catalog.Search("breast");

        var facets = new[]
        {
            ("SearchEnglish", (Func<int>)(() => catalog.Search("blue_hair").Count)),
            ("SearchJapanese", () => catalog.Search("青い髪").Count),
            ("SearchMixed", () => catalog.Search("blue_hair 青い髪").Count),
            ("FilterSearchHits", () => index.FilterSearchHits(filterHits,
                UnifiedBrowseState.Neutral.ToggleBodySite("BREAST_NIPPLE")).Count),
            ("BrowseNeutral", () => index.Browse(UnifiedBrowseState.Neutral).Count),
            ("BrowseLargeRoute", () => index.Browse(UnifiedBrowseState.Neutral with { PrimaryRouteId = "BODY_SITE" }).Count),
            ("BrowseBodyFacet", () => index.Browse(UnifiedBrowseState.Neutral.ToggleBodySite("BREAST_NIPPLE")).Count),
            ("BrowseThemeFacet", () => index.Browse(UnifiedBrowseState.Neutral.ToggleTheme("BDSM_RESTRAINT")).Count),
            ("BrowseSexualBodyTheme", () => index.Browse((UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual })
                .ToggleBodySite("BREAST_NIPPLE").ToggleTheme("REPRO_PREGNANCY_LACTATION")).Count),
            ("BrowseGeneralPurposeBodyTheme", () => index.Browse((UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.GeneralPurpose })
                .ToggleBodySite("FEMALE_GENITAL").ToggleTheme("REPRO_PREGNANCY_LACTATION")).Count)
        };
        var timings = facets.ToDictionary(item => item.Item1, item => MedianMilliseconds(item.Item2), StringComparer.Ordinal);
        var rowCount = catalog.Entries.Count;
        var catalogDbBytes = new FileInfo(path).Length;
        GC.KeepAlive(index);
        GC.KeepAlive(catalog);
        return new(path, catalogDbBytes, rowCount, loadWatch.Elapsed.TotalMilliseconds,
            indexWatch.Elapsed.TotalMilliseconds, indexAllocatedBytes, indexRetainedBytes,
            combinedRetainedBytes, timings);
    }

    private static double MedianMilliseconds(Func<int> action)
    {
        for (var i = 0; i < 5; i++) _ = action();
        var samples = new double[21];
        for (var i = 0; i < samples.Length; i++)
        {
            var watch = Stopwatch.StartNew();
            _ = action();
            watch.Stop();
            samples[i] = watch.Elapsed.TotalMilliseconds;
        }
        Array.Sort(samples);
        return samples[samples.Length / 2];
    }

    private static GateSide Aggregate(IReadOnlyList<GateSide> runs)
    {
        static double MedianDouble(IEnumerable<double> values)
        {
            var sorted = values.Order().ToArray();
            return sorted[sorted.Length / 2];
        }
        static long MedianLong(IEnumerable<long> values)
        {
            var sorted = values.Order().ToArray();
            return sorted[sorted.Length / 2];
        }
        var first = runs[0];
        var queryKeys = first.QueryMedianMs.Keys;
        return new(first.DatabasePath, first.CatalogDbBytes, first.CatalogEntryCount,
            MedianDouble(runs.Select(run => run.CatalogOpenMs)),
            MedianDouble(runs.Select(run => run.UnifiedBrowseIndexBuildMs)),
            MedianLong(runs.Select(run => run.UnifiedBrowseIndexAllocatedBytes)),
            MedianLong(runs.Select(run => run.UnifiedBrowseIndexRetainedBytes)),
            MedianLong(runs.Select(run => run.CombinedRetainedManagedBytes)),
            queryKeys.ToDictionary(key => key,
                key => MedianDouble(runs.Select(run => run.QueryMedianMs[key])), StringComparer.Ordinal));
    }

    private static GateComparisons Compare(GateSide baseline, GateSide candidate)
    {
        static (double Percent, double Delta) Delta(double baseline, double candidate)
            => (baseline <= 0 ? 0 : (candidate - baseline) / baseline * 100, candidate - baseline);

        var search = new[] { "SearchEnglish", "SearchJapanese", "SearchMixed" }
            .Select(key => Delta(baseline.QueryMedianMs[key], candidate.QueryMedianMs[key])).ToArray();
        var filter = Delta(baseline.QueryMedianMs["FilterSearchHits"], candidate.QueryMedianMs["FilterSearchHits"]);
        var browse = new[] { "BrowseNeutral", "BrowseLargeRoute", "BrowseBodyFacet", "BrowseThemeFacet", "BrowseSexualBodyTheme", "BrowseGeneralPurposeBodyTheme" }
            .Select(key => Delta(baseline.QueryMedianMs[key], candidate.QueryMedianMs[key])).ToArray();
        var memoryDelta = candidate.CombinedRetainedManagedBytes - baseline.CombinedRetainedManagedBytes;
        return new(
            search.Any(value => value.Percent > 15 && value.Delta > 2.0),
            filter.Percent > 20 && filter.Delta > 0.5,
            browse.Any(value => value.Percent > 20 && value.Delta > 0.25),
            memoryDelta > Math.Max(baseline.CombinedRetainedManagedBytes * 0.01, 1_000_000),
            memoryDelta,
            baseline.QueryMedianMs.ToDictionary(pair => pair.Key,
                pair => new QueryDelta(pair.Value, candidate.QueryMedianMs[pair.Key], Delta(pair.Value, candidate.QueryMedianMs[pair.Key]).Percent), StringComparer.Ordinal));
    }

    private sealed record QueryDelta(double BaselineMedianMs, double CandidateMedianMs, double PercentIncrease);
    private sealed record GateComparisons(bool SearchBlocked, bool FilterSearchHitsBlocked, bool BrowseBlocked,
        bool ManagedMemoryBlocked, long CombinedRetainedMemoryDeltaBytes, IReadOnlyDictionary<string, QueryDelta> QueryDeltas);
    private sealed record GateSide(string? DatabasePath, long CatalogDbBytes, int CatalogEntryCount,
        double CatalogOpenMs, double UnifiedBrowseIndexBuildMs, long UnifiedBrowseIndexAllocatedBytes,
        long UnifiedBrowseIndexRetainedBytes, long CombinedRetainedManagedBytes,
        IReadOnlyDictionary<string, double> QueryMedianMs);
}
