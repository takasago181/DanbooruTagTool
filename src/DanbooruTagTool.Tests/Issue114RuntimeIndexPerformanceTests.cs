using System.Diagnostics;
using System.Globalization;
using DanbooruTagTool.Core;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue114RuntimeIndexPerformanceTests(ITestOutputHelper output)
{
    [Fact]
    public void SyntheticProductionSizedCatalogMeasuresIndexedRuntimePaths()
    {
        const int total = 126_427;
        var entries = Enumerable.Range(0, total).Select(CreateEntry).ToArray();
        var legacyMeasurement = MeasureLegacyCatalogIndex(entries);
        var (catalog, runtimeMeasurement) = MeasureRuntimeCatalogIndex(entries);

        var indexedSearchTimer = Stopwatch.StartNew();
        var indexedSearchHits = 0;
        foreach (var query in new[] { "synthetic_tag_126426", "synthetic_tag_1", "タグ", "mixed tag" })
            indexedSearchHits += catalog.Search(query).Count;
        indexedSearchTimer.Stop();

        var legacySearchTimer = Stopwatch.StartNew();
        var legacySearchHits = 0;
        foreach (var query in new[] { "synthetic_tag_126426", "synthetic_tag_1", "タグ", "mixed tag" })
        {
            var legacyHits = LegacySearch(entries, query);
            var indexedHits = catalog.Search(query);
            legacySearchHits += legacyHits.Count;
            Assert.Equal(legacyHits.Select(hit => (hit.Entry.Id, hit.Rank)), indexedHits.Select(hit => (hit.Entry.Id, hit.Rank)));
        }
        legacySearchTimer.Stop();

        var indexedBrowseTimer = Stopwatch.StartNew();
        var indexedBrowseCount = catalog.BrowseCategory("Character").Count;
        indexedBrowseTimer.Stop();

        var legacyBrowseTimer = Stopwatch.StartNew();
        var legacyBrowseCount = entries.Where(entry => entry.EffectiveCategory == "Character" && entry.CanBrowse).Count();
        legacyBrowseTimer.Stop();

        output.WriteLine($"entries={catalog.Entries.Count.ToString("N0", CultureInfo.InvariantCulture)}");
        output.WriteLine($"legacy_catalog_index_build_ms={legacyMeasurement.BuildMilliseconds.ToString("F3", CultureInfo.InvariantCulture)}");
        output.WriteLine($"runtime_index_build_ms={runtimeMeasurement.BuildMilliseconds.ToString("F3", CultureInfo.InvariantCulture)}");
        output.WriteLine($"legacy_catalog_index_transient_allocations={legacyMeasurement.TransientAllocations.ToString("N0", CultureInfo.InvariantCulture)}");
        output.WriteLine($"runtime_index_transient_allocations={runtimeMeasurement.TransientAllocations.ToString("N0", CultureInfo.InvariantCulture)}");
        output.WriteLine($"legacy_catalog_index_retained_heap_delta={legacyMeasurement.RetainedHeapDelta.ToString("N0", CultureInfo.InvariantCulture)}");
        output.WriteLine($"runtime_index_retained_heap_delta={runtimeMeasurement.RetainedHeapDelta.ToString("N0", CultureInfo.InvariantCulture)}");
        output.WriteLine($"indexed_search_4_queries_ms={indexedSearchTimer.Elapsed.TotalMilliseconds.ToString("F3", CultureInfo.InvariantCulture)} hits={indexedSearchHits}");
        output.WriteLine($"legacy_search_4_queries_ms={legacySearchTimer.Elapsed.TotalMilliseconds.ToString("F3", CultureInfo.InvariantCulture)} hits={legacySearchHits}");
        output.WriteLine($"indexed_character_browse_ms={indexedBrowseTimer.Elapsed.TotalMilliseconds.ToString("F3", CultureInfo.InvariantCulture)} count={indexedBrowseCount}");
        output.WriteLine($"legacy_character_filter_scan_ms={legacyBrowseTimer.Elapsed.TotalMilliseconds.ToString("F3", CultureInfo.InvariantCulture)} count={legacyBrowseCount}");

        Assert.Equal(total, catalog.Entries.Count);
        Assert.Equal(30_629, catalog.BrowseCategory("General", false).Count);
        Assert.Equal(3_059, catalog.BrowseCategory("Special", false).Count);
        Assert.Equal(35_890, catalog.BrowseCategory("Character", false).Count);
        Assert.Equal(8_536, catalog.BrowseCategory("Copyright", false).Count);
        Assert.Equal(48_313, catalog.BrowseCategory("Artist", false).Count);
        Assert.Equal(legacyBrowseCount, indexedBrowseCount);
    }

    private static (Catalog Catalog, MemoryMeasurement Measurement) MeasureRuntimeCatalogIndex(IReadOnlyList<CatalogEntry> entries)
    {
        ForceFullCollection();
        var baseline = GC.GetTotalMemory(true);
        var allocationsBefore = GC.GetAllocatedBytesForCurrentThread();
        var timer = Stopwatch.StartNew();
        var catalog = new Catalog(entries);
        timer.Stop();
        var transientAllocations = GC.GetAllocatedBytesForCurrentThread() - allocationsBefore;
        ForceFullCollection();
        var retainedHeapDelta = GC.GetTotalMemory(true) - baseline;
        GC.KeepAlive(catalog);
        return (catalog, new MemoryMeasurement(timer.Elapsed.TotalMilliseconds, transientAllocations, retainedHeapDelta));
    }

    private static MemoryMeasurement MeasureLegacyCatalogIndex(IReadOnlyList<CatalogEntry> entries)
    {
        ForceFullCollection();
        var baseline = GC.GetTotalMemory(true);
        var allocationsBefore = GC.GetAllocatedBytesForCurrentThread();
        var timer = Stopwatch.StartNew();
        var canonical = entries.Where(entry => entry.Canonical != null)
            .GroupBy(entry => SearchEngine.Normalize(entry.Canonical!), StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => Preferred(group), StringComparer.Ordinal);
        timer.Stop();
        var transientAllocations = GC.GetAllocatedBytesForCurrentThread() - allocationsBefore;
        ForceFullCollection();
        var retainedHeapDelta = GC.GetTotalMemory(true) - baseline;
        GC.KeepAlive(canonical);
        return new MemoryMeasurement(timer.Elapsed.TotalMilliseconds, transientAllocations, retainedHeapDelta);
    }

    private static CatalogEntry Preferred(IEnumerable<CatalogEntry> entries) => entries
        .OrderByDescending(entry => entry.IsSpecial && (!string.IsNullOrWhiteSpace(entry.Japanese) || entry.Paths.Length > 0 || entry.Description.Length > 0 || entry.ProductFit.Length > 0))
        .ThenBy(entry => entry.Id, StringComparer.Ordinal).First();

    private static void ForceFullCollection()
    {
        GC.Collect(GC.MaxGeneration, GCCollectionMode.Forced, blocking: true, compacting: true);
        GC.WaitForPendingFinalizers();
        GC.Collect(GC.MaxGeneration, GCCollectionMode.Forced, blocking: true, compacting: true);
    }

    private static IReadOnlyList<SearchHit> LegacySearch(IReadOnlyList<CatalogEntry> entries, string query)
    {
        var q = SearchEngine.Normalize(query);
        if (q.Length == 0) return [];
        var hits = entries.Where(entry => entry.CanSearch).Select(entry => new SearchHit(entry, LegacyRank(entry, q)))
            .Where(hit => hit.Rank < 100).ToArray();
        if (hits.Any(hit => hit.Rank <= 3)) hits = hits.Where(hit => hit.Rank <= 3).ToArray();
        hits = hits.GroupBy(hit => hit.Entry.Canonical ?? hit.Entry.Id, StringComparer.Ordinal)
            .Select(group => group.OrderBy(hit => hit.Rank)
                .ThenByDescending(hit => hit.Entry.IsSpecial)
                .ThenByDescending(hit => hit.Entry.Usage).First()).ToArray();
        return hits.OrderBy(hit => hit.Rank)
            .ThenBy(hit => LegacyPrefixDistance(hit.Entry, q))
            .ThenByDescending(hit => hit.Entry.Usage)
            .ThenBy(hit => hit.Entry.English, StringComparer.Ordinal).ToArray();
    }

    private static int LegacyPrefixDistance(CatalogEntry entry, string query)
    {
        var words = new[] { entry.Canonical ?? "", entry.English }.Concat(entry.Aliases)
            .SelectMany(value => SearchEngine.Normalize(value).Split(' ', StringSplitOptions.RemoveEmptyEntries));
        return words.Where(word => word.StartsWith(query, StringComparison.Ordinal))
            .Select(word => word.Length - query.Length).DefaultIfEmpty(1000).Min();
    }

    private static int LegacyRank(CatalogEntry entry, string query)
    {
        var english = new[] { entry.Canonical ?? "", entry.English }.Concat(entry.Aliases).Concat(entry.JapaneseSearch.Where(term => !HasJapanese(term)))
            .Select(SearchEngine.Normalize).Where(term => term.Length > 0).ToArray();
        var japanese = new[] { entry.Japanese ?? "" }.Concat(entry.JapaneseSearch.Where(HasJapanese))
            .Select(SearchEngine.Normalize).Where(term => term.Length > 0).ToArray();
        if (english.Contains(query)) return 0;
        if (japanese.Contains(query)) return 1;
        if (english.Any(term => (" " + term + " ").Contains(" " + query + " ", StringComparison.Ordinal))) return 2;
        var parts = query.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length > 1 && parts.All(part => english.Any(term => term.Split(' ').Contains(part)) || japanese.Any(term => term.Contains(part, StringComparison.Ordinal)))) return 3;
        if (HasJapanese(query) && japanese.Any(term => term.Contains(query, StringComparison.Ordinal))) return 3;
        if (english.Any(term => term.Split(' ').Any(word => word.StartsWith(query, StringComparison.Ordinal)))) return 4;
        if (query.Length >= 3 && english.Any(term => term.Contains(query, StringComparison.Ordinal))) return 5;
        if (query.Length >= 4 && english.Any(term => LegacyDistanceOne(term, query))) return 6;
        return 100;
    }

    private static bool HasJapanese(string value) => value.Any(c => c is >= '\u3040' and <= '\u30ff' or >= '\u3400' and <= '\u9fff');

    private static bool LegacyDistanceOne(string a, string b)
    {
        if (Math.Abs(a.Length - b.Length) > 1) return false;
        int i = 0, j = 0, errors = 0;
        while (i < a.Length && j < b.Length)
        {
            if (a[i] == b[j]) { i++; j++; continue; }
            if (++errors > 1) return false;
            if (a.Length >= b.Length) i++;
            if (b.Length >= a.Length) j++;
        }
        return errors + a.Length - i + b.Length - j <= 1;
    }

    private static CatalogEntry CreateEntry(int index)
    {
        var (category, special) = index switch
        {
            < 30_629 => ("General", false),
            < 33_688 => ("Special", true),
            < 69_578 => ("Character", false),
            < 78_114 => ("Copyright", false),
            _ => ("Artist", false)
        };
        return new CatalogEntry(
            $"synthetic:{index}", $"synthetic_tag_{index}", $"synthetic_tag_{index}", $"タグ{index}",
            special, index, [], [], [] ) with { TagCategory = category };
    }

    private sealed record MemoryMeasurement(double BuildMilliseconds, long TransientAllocations, long RetainedHeapDelta);
}
