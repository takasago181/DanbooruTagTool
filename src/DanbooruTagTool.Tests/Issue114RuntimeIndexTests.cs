using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue114RuntimeIndexTests
{
    [Theory]
    [InlineData("blue_hair", "blue_hair", 0)]
    [InlineData("青い髪", "blue_hair", 1)]
    [InlineData("blue hair", "blue_hair", 0)]
    [InlineData("青い hair", "blue_hair", 3)]
    [InlineData("anal_sex", "anal", 0)]
    [InlineData("blu", "blue_hair", 4)]
    [InlineData("lue", "blue_hair", 5)]
    [InlineData("blie hair", "blue_hair", 6)]
    public void RuntimeSearchPreservesExistingCharacterization(string query, string expectedCanonical, int expectedRank)
    {
        var catalog = Fixtures.Catalog();
        var hits = catalog.Search(query);
        Assert.NotEmpty(hits);
        var first = hits.First();

        Assert.Equal(expectedCanonical, first.Entry.Canonical);
        Assert.Equal(expectedRank, first.Rank);
        Assert.Equal(
            new SearchEngine(catalog).Search(query).Select(hit => (hit.Entry.Id, hit.Rank)),
            hits.Select(hit => (hit.Entry.Id, hit.Rank)));
    }

    [Fact]
    public void CategoryAndSpecialPathIndexesPreserveSourceOrderAndMembership()
    {
        var first = Fixtures.Entry("first", "最初", 20) with { TagCategory = "Character" };
        var hidden = Fixtures.Entry("hidden", "非表示", 999) with { TagCategory = "Character", ProductFit = "KEEP_REFERENCE_ONLY" };
        var second = Fixtures.Entry("second", "次", 10) with { TagCategory = "Character" };
        var special = Fixtures.Entry("special", "特別", 30, special: true);
        var catalog = new Catalog([first, hidden, second, special]);

        Assert.Equal(new[] { "G:first", "G:hidden", "G:second" }, catalog.BrowseCategory("Character", false).Select(entry => entry.Id));
        Assert.Equal(new[] { "G:first", "G:second" }, catalog.BrowseCategory("Character").Select(entry => entry.Id));
        Assert.Equal(new[] { "S:special" }, catalog.BrowseSpecialPath(Fixtures.HairPath.Key).Select(entry => entry.Id));
        Assert.Equal(new[] { "S:special" }, catalog.BrowseSpecialPath(Fixtures.HairPath.GenreId + ">").Select(entry => entry.Id));
        Assert.Equal(Fixtures.HairPath, Assert.Single(catalog.SpecialNavigationPaths));
    }

    [Fact]
    public void GeneralBrowsePathsAndResultsAreCachedWithoutChangingOrder()
    {
        var firstPath = new BrowsePath("A", "A", "ONE", "One");
        var secondPath = new BrowsePath("B", "B");
        var first = Fixtures.Entry("first", "最初", 10) with { Paths = [firstPath, secondPath], BrowseClassification = BrowseClassificationStatus.Proposed };
        var second = Fixtures.Entry("second", "次", 20) with { Paths = [firstPath], BrowseClassification = BrowseClassificationStatus.Proposed };
        var provider = Assert.IsType<GeneralBrowseProvider>(GeneralBrowseProvider.FromCatalog(new Catalog([first, second])));

        Assert.Same(provider.Paths, provider.Paths);
        Assert.Equal(new[] { firstPath, secondPath }, provider.Paths);
        Assert.Equal(new[] { "G:second", "G:first" }, provider.Browse("").Select(entry => entry.Id));
        Assert.Equal(new[] { "G:first", "G:second" }, provider.Browse(firstPath.GenreId + ">").OrderBy(entry => entry.Id).Select(entry => entry.Id));
    }

    [Fact]
    public void CharacterAndCopyrightRelationsUseIndexedMetadata()
    {
        var copyright = Fixtures.Entry("series", "作品", 100) with { TagCategory = "Copyright" };
        var character = Fixtures.Entry("hero", "主人公", 20) with { TagCategory = "Character", RelatedCopyright = ["series"] };
        var other = Fixtures.Entry("other", "別人物", 30) with { TagCategory = "Character", RelatedCopyright = ["other_series"] };
        var catalog = new Catalog([character, other, copyright]);

        Assert.Equal(new[] { "G:series" }, catalog.RelatedByCatalogMetadata(character).Select(entry => entry.Id));
        Assert.Equal(new[] { "G:hero" }, catalog.RelatedByCatalogMetadata(copyright).Select(entry => entry.Id));
    }
}
