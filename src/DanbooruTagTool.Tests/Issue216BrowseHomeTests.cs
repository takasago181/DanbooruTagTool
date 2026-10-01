using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using DanbooruTagTool.App.ViewModels;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue216BrowseHomeTests
{
    private static CatalogEntry Character(string name, string? formal = null, string? reviewed = null)
        => Fixtures.Entry(name, name) with { TagCategory = "Character", FormalHomeCopyright = formal,
            ReviewedBrowseHome = reviewed, RelatedCopyright = ["wrong"] };
    private static CatalogEntry Root(string name)
        => Fixtures.Entry(name, name) with { TagCategory = "Copyright" };

    [Fact]
    public void FormalWinsFallbackIsDistinctAndUnresolvedNeverUsesCooccurrence()
    {
        var formal = Character("formal", "one", "two");
        var fallback = Character("fallback", reviewed: "two");
        var unresolved = Character("unresolved");
        var catalog = new Catalog([formal, fallback, unresolved, Root("one"), Root("two"), Root("wrong")]);
        Assert.Equal("FORMAL_HOME", formal.BrowseHomeSource);
        Assert.Equal("REVIEWED_BROWSE_FALLBACK", fallback.BrowseHomeSource);
        Assert.Equal("one", Assert.Single(catalog.RelatedByBrowseHome(formal)).Canonical);
        Assert.Equal("two", Assert.Single(catalog.RelatedByBrowseHome(fallback)).Canonical);
        Assert.Empty(catalog.RelatedByBrowseHome(unresolved));
        Assert.Equal("fallback", Assert.Single(catalog.SearchCharactersByCopyright("two")).Canonical);
        Assert.Empty(catalog.SearchCharactersByCopyright("wrong"));
        Assert.Equal(3, catalog.BrowseCategory("Character").Count);
        Assert.Equal(3, catalog.BrowseCategory("Copyright").Count);
    }

    [Fact]
    public void BrowseAndScopedSearchUseOnlyHome()
    {
        var home = Root("work"); var character = Character("hero", reviewed: "work");
        var catalog = new Catalog([home, character, Character("unknown")]);
        var vm = new MainViewModel(catalog, new MemoryStore(), new MemoryClipboard());
        vm.NavigateTo("copyright");
        Assert.True(Assert.Single(vm.Results).HasRelated);
        vm.Dictionary.OpenRelated(home);
        Assert.Equal("hero", Assert.Single(vm.Results).Entry.Canonical);
        vm.Query = "unknown"; vm.RefreshResults(); Assert.Empty(vm.Results);
        vm.Dictionary.ClearRelatedBrowse();
        vm.Dictionary.SetSearchTarget(DictionarySearchTarget.Character);
        vm.Query = "work"; vm.RefreshResults();
        Assert.Equal("hero", Assert.Single(vm.Results).Entry.Canonical);
    }

    [Fact]
    public void DatabaseRoundTripPreservesProvenance()
    {
        using var temp = new TempDirectory(); var path = Path.Combine(temp.Path, "catalog.db");
        CatalogDatabase.Build(path, [Character("hero", reviewed: "work"), Root("work")], "issue216");
        var entry = CatalogDatabase.Open(path).Resolve("hero")!;
        Assert.Null(entry.FormalHomeCopyright);
        Assert.Equal("work", entry.ReviewedBrowseHome);
        Assert.Equal("REVIEWED_BROWSE_FALLBACK", entry.BrowseHomeSource);
    }

    [Fact]
    public void HomeStringsReuseCanonicalRootWithoutChangingProvenance()
    {
        var name = new string("work".ToCharArray());
        var root = Root(name);
        var character = Character("hero", reviewed: new string("work".ToCharArray()));
        var catalog = new Catalog([character, root]);
        var normalized = catalog.Resolve("hero")!;
        Assert.Same(name, normalized.ReviewedBrowseHome);
        Assert.Equal(character.BrowseHomeSource, normalized.BrowseHomeSource);
        Assert.Equal(character.EffectiveBrowseHome, normalized.EffectiveBrowseHome);
    }

    [Fact]
    public void UnknownRootRejected()
        => Assert.Throws<ArgumentException>(() => new Catalog([Character("hero", reviewed: "absent")]));

    [Fact]
    public void AcceptedProjectionPreservesCountsAndAdds7409Fallbacks()
    {
        var root = new DirectoryInfo(AppContext.BaseDirectory);
        while (root is not null && !File.Exists(Path.Combine(root.FullName, Issue216BrowseHomeImporter.RelativePath))) root = root.Parent;
        Assert.NotNull(root);
        var entries = Issue70CatalogOverlayImporter.Read(Path.Combine(root!.FullName, Issue70CatalogOverlayImporter.RelativePath));
        var result = Issue216BrowseHomeImporter.Apply(Path.Combine(root.FullName, Issue216BrowseHomeImporter.RelativePath), entries);
        Assert.Equal(entries.Length, result.Length);
        Assert.Equal(25533, result.Count(e => e.FormalHomeCopyright is not null));
        Assert.Equal(7409, result.Count(e => e.ReviewedBrowseHome is not null));
        Assert.Equal(2336, result.Count(e => e.EffectiveCategory == "Character" && e.EffectiveBrowseHome is null));
        Assert.All(result.Where(e => e.ReviewedBrowseHome is not null), e => Assert.Null(e.FormalHomeCopyright));
        var catalog = new Catalog(result);
        Assert.Equal(35278, catalog.BrowseCategory("Character").Count);
        Assert.Equal(7616, catalog.BrowseCategory("Copyright").Count);
    }
}
