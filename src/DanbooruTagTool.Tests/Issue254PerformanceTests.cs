using System.Diagnostics;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Microsoft.Data.Sqlite;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue254PerformanceFactAttribute : FactAttribute
{
    public Issue254PerformanceFactAttribute()
    {
        if (Environment.GetEnvironmentVariable("DTT_PERF_CATALOG") is null)
            Skip = "Opt-in full-catalog workstation measurement; set DTT_PERF_CATALOG and DTT_PERF_REPORT.";
    }
}

[CollectionDefinition("Workstation performance", DisableParallelization = true)]
public sealed class WorkstationPerformanceCollection;

[Collection("Workstation performance")]
public sealed class Issue254PerformanceTests(ITestOutputHelper output)
{
    [Issue254PerformanceFact]
    public void MeasureOrdinalIndexCandidateOpen()
    {
        var baseline = Environment.GetEnvironmentVariable("DTT_PERF_CATALOG")!;
        var candidate = Environment.GetEnvironmentVariable("DTT_PERF_INDEX_CATALOG");
        if (candidate is null) return;
        var samples = new List<object>();
        for (var run = 0; run < 3; run++)
            foreach (var side in run == 1 ? new[] { "candidate", "baseline" } : new[] { "baseline", "candidate" }) {
                GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();
                var bytes = GC.GetAllocatedBytesForCurrentThread(); var timer = Stopwatch.StartNew();
                var catalog = CatalogDatabase.Open(side == "baseline" ? baseline : candidate);
                timer.Stop();
                samples.Add(new { side, run, ms = timer.Elapsed.TotalMilliseconds,
                    allocatedBytes = GC.GetAllocatedBytesForCurrentThread() - bytes, count = catalog.Entries.Count });
                GC.KeepAlive(catalog);
            }
        var json = JsonSerializer.Serialize(samples, new JsonSerializerOptions { WriteIndented = true }); output.WriteLine(json);
        if (Environment.GetEnvironmentVariable("DTT_PERF_REPORT") is { } destination)
            File.WriteAllText(Path.ChangeExtension(destination, ".ordinal.json"), json);
    }

    [Issue254PerformanceFact]
    public void MeasureMetadataAndExistingLoraFixture()
    {
        using var library = new LibraryFixture();
        var path = Path.Combine(library.Images, "fixture.png");
        Issue226LibraryFoundationTests.WritePng(path);
        var reader = new PngGenerationMetadataReader();
        var metadata = new {
            singleFile = Measure(() => reader.Read(path)),
            parse100 = Measure(() => {
                for (var i = 0; i < 100; i++) _ = GenerationInfotextParser.Parse("fixture", Issue226LibraryFoundationTests.Info);
                return 100;
            }) };
        using var lora = new LoraFixture();
        for (var i = 0; i < 1000; i++) lora.File($"folder/model{i:0000}.safetensors", new() { ["index"] = i.ToString() });
        var timer = Stopwatch.StartNew(); var cold = lora.Store.Scan(lora.Models); var coldMs = timer.Elapsed.TotalMilliseconds;
        timer.Restart(); var warm = lora.Store.Scan(lora.Models); var warmMs = timer.Elapsed.TotalMilliseconds;
        Assert.Equal(1000, cold.Hashed); Assert.Equal(0, warm.Hashed); Assert.Equal(1000, warm.Unchanged);
        var asset = lora.Store.Query("model0999").Single();
        var report = new { metadata, lora = new { coldMs, warmMs, warm.Hashed, warm.Unchanged,
            nameLookup = Measure(() => lora.Store.Query("model0999")),
            insertabilityCheck = Measure(() => lora.Store.CanInsert(asset)),
            lastPage = Measure(() => lora.Store.Query(offset: 900)) } };
        var json = JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }); output.WriteLine(json);
        if (Environment.GetEnvironmentVariable("DTT_PERF_REPORT") is { } destination)
            File.WriteAllText(Path.ChangeExtension(destination, ".supporting.json"), json);
    }

    [Issue254PerformanceFact]
    public void MeasureFullCatalogWithoutWritingIt()
    {
        var path = Environment.GetEnvironmentVariable("DTT_PERF_CATALOG")!;
        var loads = new List<object>();
        Catalog? catalog = null;
        for (var run = 0; run < 3; run++)
        {
            catalog = null;
            GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();
            var retained = GC.GetTotalMemory(true);
            using var connection = new SqliteConnection(new SqliteConnectionStringBuilder
                { DataSource = path, Mode = SqliteOpenMode.ReadOnly, Pooling = false }.ToString());
            var allocated = GC.GetAllocatedBytesForCurrentThread();
            var timer = Stopwatch.StartNew();
            connection.Open();
            using var command = connection.CreateCommand();
            command.CommandText = "SELECT payload FROM entries ORDER BY ordinal";
            var entries = new List<CatalogEntry>();
            using (var reader = command.ExecuteReader())
                while (reader.Read()) entries.Add(JsonSerializer.Deserialize<CatalogEntry>(reader.GetString(0))!);
            var readMs = timer.Elapsed.TotalMilliseconds;
            var readBytes = GC.GetAllocatedBytesForCurrentThread() - allocated;
            allocated = GC.GetAllocatedBytesForCurrentThread(); timer.Restart();
            catalog = new Catalog(entries);
            var indexMs = timer.Elapsed.TotalMilliseconds;
            var indexBytes = GC.GetAllocatedBytesForCurrentThread() - allocated;
            entries = null!;
            allocated = GC.GetAllocatedBytesForCurrentThread(); timer.Restart();
            var browse = new UnifiedBrowseIndex(catalog);
            var browseMs = timer.Elapsed.TotalMilliseconds;
            var browseBytes = GC.GetAllocatedBytesForCurrentThread() - allocated;
            loads.Add(new { readMs, readBytes, indexMs, indexBytes, browseMs, browseBytes,
                retainedBytes = GC.GetTotalMemory(true) - retained,
                workingSetBytes = Process.GetCurrentProcess().WorkingSet64 });
            GC.KeepAlive(browse);
        }
        Assert.True(catalog!.Entries.Count > 120000, "Requires the full production-era catalog.");
        var queries = new[] { "blue_hair", "anal", "青い髪", "髪", "breast", "girl", "blue_hair 青い髪", "hatsune_miku", "touhou", "b", "bl", "blu", "blue", "blue_h", "blue_ha", "blue_hai" }
            .Concat(catalog.Entries.SelectMany(e => e.Aliases).Take(1)).Distinct().ToArray();
        var search = queries.Select(query => new { query, timing = Measure(() => catalog.Search(query)),
            signature = Signature(catalog.Search(query)), count = catalog.Search(query).Count }).ToArray();
        var unified = new UnifiedBrowseIndex(catalog);
        var home = catalog.Entries.Where(e => e.EffectiveCategory == "Character" && e.EffectiveBrowseHome is not null)
            .GroupBy(e => e.EffectiveBrowseHome!).MaxBy(g => g.Count())!.Key;
        var browseTimings = new {
            neutral = Measure(() => unified.Browse(UnifiedBrowseState.Neutral)),
            facet = Measure(() => unified.Browse(UnifiedBrowseState.Neutral.ToggleBodySite("BREAST_NIPPLE"))),
            home, homeNavigation = Measure(() => catalog.BrowseHomeCharacters(home)),
            groups = Measure(() => catalog.BrowseGroups(home)),
            homeSearch = Measure(() => catalog.SearchHomeCharacters(home, null, "re")) };
        using var c = new SqliteConnection(new SqliteConnectionStringBuilder { DataSource = path, Mode = SqliteOpenMode.ReadOnly, Pooling = false }.ToString());
        c.Open();
        var plans = new List<string>();
        using (var cmd = c.CreateCommand()) {
            cmd.CommandText = "EXPLAIN QUERY PLAN SELECT payload FROM entries ORDER BY ordinal";
            using var reader = cmd.ExecuteReader(); while (reader.Read()) plans.Add(reader.GetString(3));
        }
        var report = new { runtime = System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription,
            condition = "Release; sequential; first open OS-cache state uncontrolled, subsequent opens warm; 3 loads, 3 query warmups + 11 samples; no timing SLA", 
            entries = catalog.Entries.Count, categories = catalog.Entries.GroupBy(e => e.EffectiveCategory).ToDictionary(g => g.Key, g => g.Count()),
            catalogBytes = new FileInfo(path).Length, catalogPlan = plans, loads, search, browseTimings };
        var json = JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true });
        output.WriteLine(json);
        if (Environment.GetEnvironmentVariable("DTT_PERF_REPORT") is { } destination) File.WriteAllText(destination, json);
    }

    private static object Measure<T>(Func<T> action)
    {
        for (var i = 0; i < 3; i++) _ = action();
        var ms = new List<double>(); var bytes = new List<long>();
        for (var i = 0; i < 11; i++) {
            var before = GC.GetAllocatedBytesForCurrentThread(); var timer = Stopwatch.StartNew();
            var result = action(); timer.Stop();
            bytes.Add(GC.GetAllocatedBytesForCurrentThread() - before); ms.Add(timer.Elapsed.TotalMilliseconds);
            GC.KeepAlive(result);
        }
        ms.Sort(); bytes.Sort();
        return new { medianMs = ms[5], p95Ms = ms[10], minMs = ms[0], medianAllocatedBytes = bytes[5] };
    }

    private static string Signature(IReadOnlyList<SearchHit> hits) => Convert.ToHexString(SHA256.HashData(
        Encoding.UTF8.GetBytes(string.Join("\n", hits.Select(h => $"{h.Entry.Id}:{h.Rank}")))));
}
