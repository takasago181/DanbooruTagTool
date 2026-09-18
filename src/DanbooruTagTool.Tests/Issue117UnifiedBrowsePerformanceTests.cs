using System.Diagnostics;
using System.Globalization;
using DanbooruTagTool.Core;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue117UnifiedBrowsePerformanceTests(ITestOutputHelper output)
{
    [Fact]
    public void SyntheticFrozenOrdinaryPopulation_CharacterizesUnifiedIndexAndFiltering()
    {
        const int total = 31_752;
        const int generalCount = 28_693;
        var entries = Enumerable.Range(0, total).Select(index =>
        {
            var special = index >= generalCount;
            if (special)
            {
                return new CatalogEntry(
                    $"S:{index}", $"synthetic_tag_{index}", $"synthetic_tag_{index}", $"タグ{index}",
                    true, index, [], [], [], "KEEP",
                    SpecialBrowseV2: new(
                        index % 2 == 0 ? "ACTION_CONTACT" : "TOOL_OBJECT",
                        index % 3 == 0 ? ["MOUTH_ORAL"] : [],
                        index % 5 == 0 ? ["BDSM_RESTRAINT"] : [],
                        SpecialBrowseV2Status.AutoCandidate))
                {
                    TagCategory = "Special",
                    SexualIntent = index % 4 == 0 ? SexualIntentClass.Contextual : SexualIntentClass.Sexual,
                    SexualIntentStatus = SexualIntentClassificationStatus.AutoHighConfidence
                };
            }

            return new CatalogEntry(
                $"G:{index}", $"synthetic_tag_{index}", $"synthetic_tag_{index}", $"タグ{index}",
                false, index, [], [],
                [new BrowsePath(index % 2 == 0 ? "HAIR_FACE" : "ACTION_CONTACT", index % 2 == 0 ? "髪・顔" : "行為・接触")],
                "KEEP",
                BrowseClassification: BrowseClassificationStatus.Proposed)
            {
                TagCategory = "General",
                SexualIntent = index % 7 == 0 ? SexualIntentClass.Contextual : SexualIntentClass.NonSexual,
                SexualIntentStatus = SexualIntentClassificationStatus.AutoHighConfidence
            };
        }).ToArray();

        var catalog = new Catalog(entries);

        var build = Stopwatch.StartNew();
        var unified = new UnifiedBrowseIndex(catalog);
        build.Stop();

        var browseState = UnifiedBrowseState.Neutral with
        {
            PrimaryRouteId = "ACTION_CONTACT",
            ContentIntent = ContentIntentFilter.Sexual
        };
        var browse = Stopwatch.StartNew();
        var browsed = unified.Browse(browseState);
        browse.Stop();

        var searchHits = catalog.Search("synthetic_tag_31751");
        var filter = Stopwatch.StartNew();
        var filtered = unified.FilterSearchHits(searchHits, UnifiedBrowseState.Neutral);
        filter.Stop();

        output.WriteLine($"ordinary_identities={unified.Identities.Count.ToString("N0", CultureInfo.InvariantCulture)}");
        output.WriteLine($"unified_index_build_ms={build.Elapsed.TotalMilliseconds.ToString("F3", CultureInfo.InvariantCulture)}");
        output.WriteLine($"unified_browse_filter_ms={browse.Elapsed.TotalMilliseconds.ToString("F3", CultureInfo.InvariantCulture)} count={browsed.Count}");
        output.WriteLine($"unified_search_filter_ms={filter.Elapsed.TotalMilliseconds.ToString("F3", CultureInfo.InvariantCulture)} input={searchHits.Count} output={filtered.Count}");

        Assert.Equal(total, unified.Identities.Count);
        Assert.NotEmpty(browsed);
        Assert.Single(filtered);
        Assert.Equal("synthetic_tag_31751", filtered[0].Entry.Canonical);
    }
}
