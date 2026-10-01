using System.IO;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Microsoft.VisualBasic.FileIO;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue199UnifiedGeneralFacetTests
{
    private sealed record CsvRow(string IdentityKey, string Axis, string FacetId);

    [Fact]
    public void FrozenExtractionAndLiveDispositionAreExactAndDeterministic()
    {
        var frozen = ReadCsv("docs/issue199/frozen_facet_extraction_v1.csv");
        var asset = ReadCsv("issue199_general_facets_v1.csv");
        var disposition = ReadDisposition();

        Assert.Equal(370, frozen.Count);
        Assert.Equal(359, frozen.Select(row => row.IdentityKey).Distinct(StringComparer.Ordinal).Count());
        Assert.Equal(257, frozen.Count(row => row.Axis == "BODY"));
        Assert.Equal(113, frozen.Count(row => row.Axis == "THEME"));
        Assert.Equal(370, frozen.Select(row => (row.IdentityKey, row.Axis, row.FacetId)).Distinct().Count());
        Assert.Equal(355, asset.Count);
        Assert.Equal(346, asset.Select(row => row.IdentityKey).Distinct(StringComparer.Ordinal).Count());
        var shippedCounts = asset.GroupBy(row => (row.Axis, row.FacetId))
            .ToDictionary(group => group.Key, group => group.Count());
        Assert.Equal(new Dictionary<(string Axis, string FacetId), int>
        {
            [("BODY", "BREAST_NIPPLE")] = 72,
            [("BODY", "BUTTOCK_ANAL")] = 30,
            [("BODY", "FEMALE_GENITAL")] = 10,
            [("BODY", "MALE_GENITAL")] = 19,
            [("BODY", "MOUTH_ORAL")] = 116,
            [("THEME", "BDSM_RESTRAINT")] = 20,
            [("THEME", "INJURY_R18G")] = 82,
            [("THEME", "REPRO_PREGNANCY_LACTATION")] = 6
        }, shippedCounts);
        Assert.Equal(asset.OrderBy(row => row.IdentityKey, StringComparer.Ordinal)
            .ThenBy(row => row.Axis, StringComparer.Ordinal).ThenBy(row => row.FacetId, StringComparer.Ordinal), asset);
        Assert.All(asset, row => Assert.Contains(row, frozen));
        Assert.Equal(asset, disposition.Where(row => row.Disposition == "SHIP")
            .Select(row => new CsvRow(row.IdentityKey, row.Axis, row.FacetId))
            .OrderBy(row => row.IdentityKey, StringComparer.Ordinal).ThenBy(row => row.Axis, StringComparer.Ordinal)
            .ThenBy(row => row.FacetId, StringComparer.Ordinal));
        Assert.Equal(15, disposition.Count(row => row.Disposition == "EXCLUDE"));
        foreach (var row in disposition)
        {
            Assert.Contains(row.SemanticReviewDepth, new[] { "CHECKED", "RESEARCHED" });
            using var evidence = JsonDocument.Parse(row.SemanticFacets);
            Assert.Contains(evidence.RootElement.EnumerateArray(), value => value.GetString() == row.FacetId);
        }

        var bodyIds = SpecialBrowseV2Taxonomy.BodySites.Select(item => item.Id).ToHashSet(StringComparer.Ordinal);
        var themeIds = SpecialBrowseV2Taxonomy.Themes.Select(item => item.Id).ToHashSet(StringComparer.Ordinal);
        Assert.All(asset.Where(row => row.Axis == "BODY"), row => Assert.Contains(row.FacetId, bodyIds));
        Assert.All(asset.Where(row => row.Axis == "THEME"), row => Assert.Contains(row.FacetId, themeIds));
    }

    [Fact]
    public void BakeAddsGeneralFacetMembershipsThroughExistingIndexAndPreservesOtherBehavior()
    {
        var asset = ReadCsv("issue199_general_facets_v1.csv");
        var byIdentity = asset.GroupBy(row => row.IdentityKey, StringComparer.Ordinal)
            .ToDictionary(group => group.Key, group => group.ToArray(), StringComparer.Ordinal);
        var entries = byIdentity.Keys.Select(identity => General(identity)).ToList();
        entries.Add(General("shared_identity", routes: ["LIVING"]));
        entries.Add(Special("shared-special", "shared_identity", ["MOUTH_ORAL"], ["BDSM_RESTRAINT"]));
        entries.Add(Special("special-only", "special_only", ["MOUTH_ORAL"], ["INJURY_R18G"]));
        var beforeCatalog = new Catalog(entries);
        var beforeIndex = new UnifiedBrowseIndex(beforeCatalog);

        var bakedEntries = Issue199GeneralFacetOverlay.Bake(beforeCatalog);
        var afterCatalog = new Catalog(bakedEntries);
        var afterIndex = new UnifiedBrowseIndex(afterCatalog);

        Assert.Equal(entries.Count, bakedEntries.Length);
        Assert.Equal(beforeIndex.Identities.Count, afterIndex.Identities.Count);
        Assert.Equal(beforeIndex.Browse(UnifiedBrowseState.Neutral).Select(entry => entry.Canonical).OrderBy(value => value, StringComparer.Ordinal),
            afterIndex.Browse(UnifiedBrowseState.Neutral).Select(entry => entry.Canonical).OrderBy(value => value, StringComparer.Ordinal));

        foreach (var (identity, rows) in byIdentity)
        {
            var after = Assert.Single(afterIndex.Identities, item => item.IdentityKey == "C:" + identity);
            var expectedBody = rows.Where(row => row.Axis == "BODY").Select(row => row.FacetId).ToHashSet(StringComparer.Ordinal);
            var expectedTheme = rows.Where(row => row.Axis == "THEME").Select(row => row.FacetId).ToHashSet(StringComparer.Ordinal);
            Assert.Subset(expectedBody, after.BodySiteIds.ToHashSet(StringComparer.Ordinal));
            Assert.Subset(expectedTheme, after.ThemeIds.ToHashSet(StringComparer.Ordinal));
            Assert.False(after.DeepDiscovery);
            Assert.Contains(after.Representative, afterIndex.Browse(UnifiedBrowseState.Neutral with
            {
                BodySiteIds = expectedBody,
                ThemeIds = expectedTheme
            }));
        }

        var specialBefore = Assert.Single(beforeIndex.Identities, item => item.IdentityKey == "C:special_only");
        var specialAfter = Assert.Single(afterIndex.Identities, item => item.IdentityKey == "C:special_only");
        Assert.Equal(specialBefore.BodySiteIds, specialAfter.BodySiteIds);
        Assert.Equal(specialBefore.ThemeIds, specialAfter.ThemeIds);
        Assert.Equal(specialBefore.DeepDiscovery, specialAfter.DeepDiscovery);

        var sharedBefore = Assert.Single(beforeIndex.Identities, item => item.IdentityKey == "C:shared_identity");
        var sharedAfter = Assert.Single(afterIndex.Identities, item => item.IdentityKey == "C:shared_identity");
        Assert.Equal(sharedBefore.BackingEntries.Select(entry => entry.Id), sharedAfter.BackingEntries.Select(entry => entry.Id));
        Assert.Contains("LIVING", sharedAfter.RouteIds);

        foreach (var (before, after) in entries.Zip(bakedEntries))
        {
            Assert.Equal(before with { UnifiedBrowseFacets = null }, after with { UnifiedBrowseFacets = null });
        }

        Assert.Equal(beforeCatalog.Search("self_milking").Select(hit => (hit.Entry.Id, hit.Rank)),
            afterCatalog.Search("self_milking").Select(hit => (hit.Entry.Id, hit.Rank)));
    }

    [Fact]
    public void JapaneseEnglishMixedSearchAndBothContentLensesCombineWithBodyAndThemeFilters()
    {
        var asset = ReadCsv("issue199_general_facets_v1.csv");
        var identities = asset.Select(row => row.IdentityKey).Distinct(StringComparer.Ordinal).ToArray();
        var entries = identities.Select(identity => General(identity,
            japanese: identity == "self_milking" ? "授乳テスト" : identity == "multiple_ovum" ? "複数卵子テスト" : null,
            japaneseSearch: identity == "self_milking" ? ["乳房 授乳テスト"] : identity == "multiple_ovum" ? ["女性生殖 複数卵子テスト"] : [],
            intent: identity == "self_milking" ? SexualIntentClass.Sexual : SexualIntentClass.NonSexual)).ToList();
        var before = new Catalog(entries);
        var after = new Catalog(Issue199GeneralFacetOverlay.Bake(before));
        var index = new UnifiedBrowseIndex(after);

        var sexual = (UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.Sexual })
            .ToggleBodySite("BREAST_NIPPLE").ToggleTheme("REPRO_PREGNANCY_LACTATION");
        var target = Assert.Single(index.Browse(sexual), entry => entry.Canonical == "self_milking");
        Assert.Contains(target, index.FilterSearchHits(after.Search("self_milking"), sexual).Select(hit => hit.Entry));
        Assert.Contains(target, index.FilterSearchHits(after.Search("授乳テスト"), sexual).Select(hit => hit.Entry));
        Assert.Contains(target, index.FilterSearchHits(after.Search("self_milking 授乳テスト"), sexual).Select(hit => hit.Entry));

        var generalPurpose = (UnifiedBrowseState.Neutral with { ContentIntent = ContentIntentFilter.GeneralPurpose })
            .ToggleBodySite("FEMALE_GENITAL").ToggleTheme("REPRO_PREGNANCY_LACTATION");
        var ovum = Assert.Single(index.Browse(generalPurpose), entry => entry.Canonical == "multiple_ovum");
        Assert.Contains(ovum, index.FilterSearchHits(after.Search("複数卵子テスト"), generalPurpose).Select(hit => hit.Entry));
        Assert.Contains(ovum, index.FilterSearchHits(after.Search("multiple_ovum 複数卵子テスト"), generalPurpose).Select(hit => hit.Entry));
    }

    [Fact]
    public void DeepOnlyPromptOutputAndUiStatePersistenceRemainUnchanged()
    {
        var entries = ReadCsv("issue199_general_facets_v1.csv").Select(row => row.IdentityKey).Distinct(StringComparer.Ordinal)
            .Select(identity => General(identity)).ToList();
        var catalog = new Catalog(Issue199GeneralFacetOverlay.Bake(new Catalog(entries)));
        var index = new UnifiedBrowseIndex(catalog);
        var deepOnly = UnifiedBrowseState.Neutral with { DeepOnly = true, BodySiteIds = new HashSet<string>(["BREAST_NIPPLE"], StringComparer.Ordinal) };
        Assert.DoesNotContain(index.Browse(deepOnly), entry => entry.EffectiveCategory == "General");

        var parsed = new PromptParser(catalog).Parse("self_milking,raw");
        Assert.Equal("self_milking,raw", PromptParser.Serialize(parsed));
        Assert.Equal("self_milking,raw", PromptOutputFormatter.SerializeCanonical(parsed));

        var state = new UiState(BrowseBodySites: ["BREAST_NIPPLE"], BrowseThemes: ["REPRO_PREGNANCY_LACTATION"]);
        var restored = JsonSerializer.Deserialize<UiState>(JsonSerializer.Serialize(state));
        Assert.Equal(state.BrowseBodySites, restored!.BrowseBodySites);
        Assert.Equal(state.BrowseThemes, restored.BrowseThemes);
        Assert.NotNull(JsonSerializer.Deserialize<UiState>("{}"));
    }

    [Fact]
    public void NullableFacetMetadataKeepsOldCatalogJsonSmallAndBackwardCompatible()
    {
        var entry = General("old_catalog_row");
        var json = JsonSerializer.Serialize(entry);
        Assert.DoesNotContain("UnifiedBrowseFacets", json, StringComparison.Ordinal);
        Assert.Null(JsonSerializer.Deserialize<CatalogEntry>(json)!.UnifiedBrowseFacets);
    }

    private static CatalogEntry General(string canonical, string[]? routes = null, string? japanese = null,
        string[]? japaneseSearch = null, SexualIntentClass? intent = null)
        => new("G:" + canonical, canonical, canonical, japanese, false, 1, [], japaneseSearch ?? [],
            [new BrowsePath("BODY_PART", "身体")], BrowseClassification: BrowseClassificationStatus.Proposed)
        {
            UnifiedBrowseRouteIds = routes ?? [],
            SexualIntent = intent ?? SexualIntentClass.NonSexual,
            SexualIntentStatus = SexualIntentClassificationStatus.HumanReviewed
        };

    private static CatalogEntry Special(string id, string canonical, string[] body, string[] themes)
        => new("S:" + id, canonical, canonical, null, true, 1, [], [], [],
            SpecialBrowseV2: new(null, body, themes, SpecialBrowseV2Status.HumanResolved));

    private static List<CsvRow> ReadCsv(string relativePath)
    {
        var path = Path.Combine(AppContext.BaseDirectory, relativePath.Replace('/', Path.DirectorySeparatorChar));
        using var parser = new TextFieldParser(path, System.Text.Encoding.UTF8)
        {
            TextFieldType = FieldType.Delimited,
            HasFieldsEnclosedInQuotes = true,
            TrimWhiteSpace = false
        };
        parser.SetDelimiters(",");
        var header = parser.ReadFields()!;
        var fields = header.Select((value, index) => (value, index)).ToDictionary(value => value.value, value => value.index, StringComparer.Ordinal);
        var rows = new List<CsvRow>();
        while (!parser.EndOfData)
        {
            var values = parser.ReadFields()!;
            rows.Add(new(values[fields["identity_key"]], values[fields["axis"]], values[fields["facet_id"]]));
        }
        return rows;
    }

    private sealed record DispositionRow(string IdentityKey, string Axis, string FacetId,
        string SemanticReviewDepth, string SemanticFacets, string Disposition);

    private static List<DispositionRow> ReadDisposition()
    {
        var path = Path.Combine(AppContext.BaseDirectory, "docs", "issue199", "candidate_disposition_v1.csv");
        using var parser = new TextFieldParser(path, System.Text.Encoding.UTF8)
        {
            TextFieldType = FieldType.Delimited,
            HasFieldsEnclosedInQuotes = true,
            TrimWhiteSpace = false
        };
        parser.SetDelimiters(",");
        var header = parser.ReadFields()!;
        var fields = header.Select((value, index) => (value, index)).ToDictionary(value => value.value, value => value.index, StringComparer.Ordinal);
        var rows = new List<DispositionRow>();
        while (!parser.EndOfData)
        {
            var values = parser.ReadFields()!;
            rows.Add(new(values[fields["identity_key"]], values[fields["axis"]], values[fields["facet_id"]],
                values[fields["semantic_review_depth"]], values[fields["semantic_facets"]], values[fields["disposition"]]));
        }
        return rows;
    }
}
