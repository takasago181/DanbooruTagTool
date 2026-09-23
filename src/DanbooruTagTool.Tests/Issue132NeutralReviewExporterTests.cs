using System.IO;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue132NeutralReviewExporterTests
{
    [Fact]
    public void FullSizedSyntheticCatalogProducesNeutralDeterministicIdentityProjection()
    {
        var entries = BuildSyntheticOrdinaryPopulation();
        var catalog = new Catalog(entries);

        var first = Issue132NeutralReviewExporter.Build(catalog);
        var second = Issue132NeutralReviewExporter.Build(catalog);

        Assert.Equal(Issue118SexualIntentV2Overlay.IdentityCount, first.Count);
        Assert.Equal(first.Select(row => row.IdentityKey), second.Select(row => row.IdentityKey));
        Assert.Equal(Enumerable.Range(1, first.Count), first.Select(row => row.ReviewSeq));
        Assert.Equal(first.Count, first.Select(row => row.IdentityKey).Distinct(StringComparer.Ordinal).Count());

        var shared = Assert.Single(first, row => row.IdentityKey == "shared_tag");
        Assert.Equal("shared_tag", shared.Canonical);
        Assert.Equal("特別表示", shared.DisplayJa);
        Assert.Equal("", shared.NeutralDescriptionJa);

        var english = JsonSerializer.Deserialize<string[]>(shared.EnglishSurfaces)!;
        Assert.Equal(new[] { "shared_general_surface", "shared_special_surface" }, english);
        var search = JsonSerializer.Deserialize<string[]>(shared.SearchTerms)!;
        Assert.Equal(new[] { "共有検索", "特別検索" }, search);
        var aliases = JsonSerializer.Deserialize<string[]>(shared.Aliases)!;
        Assert.Equal(new[] { "shared_alias", "special_alias" }, aliases);

        var csv = Issue132NeutralReviewExporter.SerializeCsv(first);
        var header = csv.Split('\n', 2)[0];
        Assert.Equal("review_seq,identity_key,canonical,english_surfaces,display_ja,search_terms,aliases,neutral_description_ja", header);
        Assert.DoesNotContain("ACTION_CONTACT", csv, StringComparison.Ordinal);
        Assert.DoesNotContain("SEXUAL", csv, StringComparison.Ordinal);
        Assert.DoesNotContain("999999999", csv, StringComparison.Ordinal);
        Assert.DoesNotContain("machine_bucket", header, StringComparison.Ordinal);
        Assert.DoesNotContain("general_paths", header, StringComparison.Ordinal);
        Assert.DoesNotContain("unified_route", header, StringComparison.Ordinal);
    }

    [Fact]
    public void PopulationDriftFailsClosed()
    {
        var entry = new CatalogEntry(
            "G:only_tag", "only_tag", "only_tag", "唯一", false, 1,
            [], ["唯一"], [], BrowseClassification: BrowseClassificationStatus.Proposed);

        var ex = Assert.Throws<InvalidDataException>(() =>
            Issue132NeutralReviewExporter.Build(new Catalog([entry])));

        Assert.Contains("identity count drift", ex.Message, StringComparison.Ordinal);
    }

    private static CatalogEntry[] BuildSyntheticOrdinaryPopulation()
    {
        var entries = new List<CatalogEntry>(Issue118SexualIntentV2Overlay.IdentityCount + 1);
        for (var i = 0; i < Issue118SexualIntentV2Overlay.IdentityCount - 1; i++)
        {
            var tag = $"neutral_tag_{i:D5}";
            entries.Add(new CatalogEntry(
                "G:" + tag,
                tag,
                tag,
                "中立" + i,
                false,
                999_999_999,
                [],
                ["検索" + i],
                [new BrowsePath("ACTION_CONTACT", "行為・接触", "INTERACTION", "接触・しぐさ・活動")],
                BrowseClassification: BrowseClassificationStatus.Proposed)
            {
                UnifiedBrowseRouteIds = ["ACTION_CONTACT"],
                SexualIntent = SexualIntentClass.Sexual,
                SexualIntentStatus = SexualIntentClassificationStatus.HumanReviewed,
                SexualIntentSource = "FORBIDDEN_SOURCE",
                SexualIntentEvidence = "FORBIDDEN_EVIDENCE"
            });
        }

        entries.Add(new CatalogEntry(
            "G:shared_tag",
            "shared_tag",
            "shared_general_surface",
            "一般表示",
            false,
            999_999_999,
            ["shared_alias"],
            ["共有検索"],
            [new BrowsePath("ACTION_CONTACT", "行為・接触")],
            BrowseClassification: BrowseClassificationStatus.Proposed)
        {
            UnifiedBrowseRouteIds = ["ACTION_CONTACT"],
            SexualIntent = SexualIntentClass.Sexual
        });

        entries.Add(new CatalogEntry(
            "S:99999",
            "shared_tag",
            "shared_special_surface",
            "特別表示",
            true,
            999_999_999,
            ["special_alias"],
            ["特別検索"],
            [],
            ProductFit: "KEEP",
            Description: "CURRENT_ROUTE_NOT_REPRODUCED",
            BrowseClassification: BrowseClassificationStatus.NotApplicable,
            SpecialBrowseV2: new SpecialBrowseV2Classification(
                "ACTION_CONTACT", [], [], SpecialBrowseV2Status.HumanResolved))
        {
            UnifiedBrowseRouteIds = ["ACTION_CONTACT"],
            SexualIntent = SexualIntentClass.Sexual
        });

        return entries.ToArray();
    }
}
