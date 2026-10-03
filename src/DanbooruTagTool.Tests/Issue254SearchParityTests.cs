using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Microsoft.Data.Sqlite;
using System.IO;
using System.Text.Json;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue254SearchParityTests
{
    [Fact]
    public void NewCatalogOrdinalIndexPreservesPayloadOrderAndOldCatalogCompatibility()
    {
        using var fixture = new LibraryFixture();
        var path = Path.Combine(fixture.Path, "catalog.db");
        var entries = Fixtures.Catalog().Entries.Reverse().ToArray();
        CatalogDatabase.Build(path, entries, "fixture");
        using (var c = new SqliteConnection(new SqliteConnectionStringBuilder { DataSource = path, Pooling = false }.ToString())) {
            c.Open(); using var cmd = c.CreateCommand();
            cmd.CommandText = "EXPLAIN QUERY PLAN SELECT payload FROM entries ORDER BY ordinal";
            using (var reader = cmd.ExecuteReader()) {
                var plans = new List<string>(); while (reader.Read()) plans.Add(reader.GetString(3));
                Assert.Contains(plans, p => p.Contains("entries_ordinal", StringComparison.Ordinal));
                Assert.DoesNotContain(plans, p => p.Contains("TEMP B-TREE", StringComparison.Ordinal));
            }
            cmd.CommandText = "SELECT payload FROM entries ORDER BY ordinal";
            using (var reader = cmd.ExecuteReader())
                foreach (var entry in entries) { Assert.True(reader.Read()); Assert.Equal(JsonSerializer.Serialize(entry), reader.GetString(0)); }
            cmd.CommandText = "DROP INDEX entries_ordinal"; cmd.ExecuteNonQuery();
        }
        var bytes = File.ReadAllBytes(path);
        Assert.Equal(entries.Select(e => e.Id), CatalogDatabase.Open(path).Entries.Select(e => e.Id));
        Assert.Equal(bytes, File.ReadAllBytes(path)); // Older catalog open never adds/migrates an index.
    }

    [Fact]
    public void AllocationReductionPreservesWordBoundariesMixedIntentAndGlobalSuppression()
    {
        var entries = Fixtures.Catalog().Entries.Concat(new[] {
            Fixtures.Entry("blue_blue_hair", "青髪") with { JapaneseSearch = ["azure blue locks", "青い hair"] },
            Fixtures.Entry("bluebird_hair", "青い鳥"),
            Fixtures.Entry("artist_anal", "別カテゴリ") with { TagCategory = "Artist", Aliases = ["anal"] },
            Fixtures.Entry("髪_hair", "混在", aliases: ["locks_(blue)"]),
            Fixtures.Entry("aa_aa_b", "境界", aliases: ["a aa b", "a-a", "a(b)"]) }).ToArray();
        var catalog = new Catalog(entries);
        var queries = new[] { "", " ", "anal", "analog", "blu", "blue hair", "blue bird", "azure locks", "azure 青い",
            "髪 hair", "hair 髪", "aa b", "aa", "a aa", "a(b)", "locks_(blue)", " blie hair ", "BLUE__HAIR", "blue\t hair", "a-a" };
        foreach (var query in queries)
            Assert.Equal(Issue114LegacySearch.Search(entries, query).Select(h => (h.Entry.Id, h.Rank)),
                catalog.Search(query).Select(h => (h.Entry.Id, h.Rank)));
    }
}
