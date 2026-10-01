using System.Diagnostics;
using System.IO;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using DanbooruTagTool.App.ViewModels;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class Issue223BrowseGroupTests(ITestOutputHelper output)
{
    private static string RepositoryRoot()
    {
        var root = new DirectoryInfo(AppContext.BaseDirectory);
        while (root is not null && !File.Exists(Path.Combine(root.FullName, Issue223BrowseGroupImporter.GroupsPath))) root = root.Parent;
        return root?.FullName ?? throw new FileNotFoundException("Issue223 asset root");
    }
    private static CatalogEntry Root(string name) => Fixtures.Entry(name, name) with { TagCategory = "Copyright" };
    private static CatalogEntry Character(string name, string home, string? group = null, long usage = 10)
        => Fixtures.Entry(name, "共通", usage) with { TagCategory = "Character", ReviewedBrowseHome = home,
            BrowseGroup = group is null ? null : new(home, group, group, 1) };
    private static Catalog Fixture() => new([Root("one"), Root("two"), Root("small"),
        Character("one_hero", "one", "a", 100), Character("one_sidekick", "one", "a", 10),
        Character("one_rival", "one", "b", 50), Character("one_unknown", "one"),
        Character("two_hero", "two", "a"), Character("small_hero", "small")]);

    [Fact]
    public void GroupsPartitionHomeAndRejectUnknownRootOrCrossHomeGroup()
    {
        var catalog = Fixture();
        var groups = catalog.BrowseGroups("one");
        Assert.Equal(3, groups.Count);
        var members = groups.SelectMany(g => catalog.BrowseHomeCharacters("one", g.Id)).ToArray();
        Assert.Equal(4, members.Length);
        Assert.Equal(members.Length, members.DistinctBy(e => e.Id).Count());
        Assert.All(groups, g => Assert.Equal(g.Count, catalog.BrowseHomeCharacters("one", g.Id).Count));
        Assert.Equal(new[] { "one_hero", "one_sidekick" }, catalog.BrowseHomeCharacters("one", "a").Select(e => e.Canonical));
        Assert.Single(catalog.BrowseHomeCharacters("one", CharacterBrowseGroups.OtherId));
        Assert.Throws<ArgumentException>(() => catalog.BrowseGroups("absent"));
        Assert.Throws<ArgumentException>(() => catalog.BrowseHomeCharacters("two", "b"));
        Assert.Throws<ArgumentException>(() => catalog.SearchHomeCharacters("one", "absent", "共通"));
        Assert.Empty(catalog.BrowseGroups("small"));
        Assert.Single(catalog.BrowseHomeCharacters("small"));
    }

    [Fact]
    public void ScopedSearchRanksInsideHomeAndGroupBeforeGlobalStrongIntentSuppression()
    {
        var catalog = new Catalog([Root("one"), Root("two"), Character("outside", "two") with { Japanese = "hero" },
            Character("superhero_suffix", "one", "a"), Character("superhero_rival", "one", "b")]);
        Assert.Equal("outside", Assert.Single(catalog.Search("hero")).Entry.Canonical);
        Assert.Equal(2, catalog.SearchHomeCharacters("one", null, "hero").Count);
        Assert.Equal("superhero_suffix", Assert.Single(catalog.SearchHomeCharacters("one", "a", "hero")).Entry.Canonical);
        Assert.All(Fixture().SearchHomeCharacters("one", "a", "共通"), hit =>
        {
            Assert.Equal("one", hit.Entry.EffectiveBrowseHome);
            Assert.Equal("a", hit.Entry.BrowseGroup!.Id);
        });
    }

    [Fact]
    public void GroupNavigationRootSearchOtherBackClearAndSmallIp()
    {
        var catalog = Fixture(); var vm = new MainViewModel(catalog, new MemoryStore(), new MemoryClipboard());
        vm.NavigateTo("copyright");
        vm.Dictionary.OpenRelated(catalog.Resolve("one")!);
        Assert.True(vm.Dictionary.ShowBrowseGroups);
        Assert.Empty(vm.Results);
        vm.Query = "共通"; vm.RefreshResults(); Assert.Equal(4, vm.Results.Count);
        vm.Dictionary.SelectBrowseGroup("a"); Assert.Equal(2, vm.Results.Count);
        vm.Query = "rival"; vm.RefreshResults(); Assert.Empty(vm.Results);
        vm.Dictionary.Back.Execute(null); Assert.Empty(vm.Results); Assert.Null(vm.Dictionary.SelectedBrowseGroupId);
        vm.Dictionary.SelectBrowseGroup(CharacterBrowseGroups.OtherId);
        Assert.Equal("one_unknown", Assert.Single(vm.Results).Entry.Canonical);
        vm.Dictionary.ShowAllHomeCharactersCommand.Execute(null); Assert.Equal(4, vm.Results.Count);
        vm.Dictionary.ClearRelatedBrowse(); Assert.False(vm.Dictionary.ShowBrowseGroups);
        vm.Dictionary.OpenRelated(catalog.Resolve("small")!); Assert.Single(vm.Results);
        Assert.False(vm.Dictionary.ShowBrowseGroups);
        vm.Dictionary.SetSearchTarget(DictionarySearchTarget.Character);
        Assert.False(vm.Dictionary.ShowRelationBanner);
    }

    [Fact]
    public void InvalidMetadataRejectedAndOldDatabaseWithoutGroupsRemainsCompatible()
    {
        Assert.Throws<ArgumentException>(() => new Catalog([Root("one"), Character("bad", "one", "a") with
            { BrowseGroup = new("two", "a", "a", 1) }]));
        Assert.Throws<ArgumentException>(() => new Catalog([Root("one") with { BrowseGroup = new("one", "a", "a", 1) }]));
        Assert.Throws<ArgumentException>(() => new Catalog([Root("one"), Character("bad", "one", CharacterBrowseGroups.OtherId)]));
        using var temp = new TempDirectory();
        var path = Path.Combine(temp.Path, "catalog.db");
        CatalogDatabase.Build(path, Fixture().Entries, "issue223");
        var loaded = RuntimeCatalogIndex.Create(CatalogDatabase.Open(path));
        Assert.Equal(2, loaded.BrowseHomeCharacters("one", "a").Count);
        Assert.Equal("REVIEWED_BROWSE_FALLBACK", loaded.Resolve("one_hero")!.BrowseHomeSource);
        Assert.Empty(loaded.BrowseGroups("small"));
        Assert.Null(JsonSerializer.Deserialize<CatalogEntry>(JsonSerializer.Serialize(Character("old", "one")))!.BrowseGroup);
    }

    [Fact]
    public void FrozenAssetPreservesEveryNonGroupFieldAndEntireHomeAuthority()
    {
        var root = RepositoryRoot();
        var baseline = Issue70CatalogOverlayImporter.Read(Path.Combine(root, Issue70CatalogOverlayImporter.RelativePath));
        baseline = Issue179QualityOverlay.Apply(Path.Combine(root, Issue179QualityOverlay.RelativePath),
            Path.Combine(root, Issue70CatalogOverlayImporter.RelativePath), baseline);
        baseline = Issue216BrowseHomeImporter.Apply(Path.Combine(root, Issue216BrowseHomeImporter.RelativePath), baseline);
        var candidate = Issue223BrowseGroupImporter.Apply(Path.Combine(root, Issue223BrowseGroupImporter.GroupsPath),
            Path.Combine(root, Issue223BrowseGroupImporter.MembersPath), baseline);
        Assert.Equal(baseline, candidate.Select(e => e with { BrowseGroup = null }));
        Assert.Equal(35278, candidate.Count(e => e.EffectiveCategory == "Character"));
        Assert.Equal(7616, candidate.Count(e => e.EffectiveCategory == "Copyright"));
        Assert.Equal(25533, candidate.Count(e => e.FormalHomeCopyright is not null));
        Assert.Equal(7409, candidate.Count(e => e.ReviewedBrowseHome is not null));
        Assert.Equal(2336, candidate.Count(e => e.EffectiveCategory == "Character" && e.EffectiveBrowseHome is null));
        var manifest = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "docs/issue223/MANIFEST_V1.json"))).RootElement;
        Assert.Equal(manifest.GetProperty("grouped_characters").GetInt32(), candidate.Count(e => e.BrowseGroup is not null));
        var catalog = new Catalog(candidate);
        var groupedRoots = candidate.Where(e => e.BrowseGroup is not null).Select(e => e.EffectiveBrowseHome!).Distinct().ToArray();
        Assert.Equal(manifest.GetProperty("selected_home_count").GetInt32(), groupedRoots.Length);
        foreach (var home in groupedRoots)
        {
            var groups = catalog.BrowseGroups(home);
            Assert.Equal(catalog.BrowseHomeCharacters(home).Count, groups.Sum(g => g.Count));
            var all = groups.SelectMany(g => catalog.BrowseHomeCharacters(home, g.Id)).ToArray();
            Assert.Equal(all.Length, all.DistinctBy(e => e.Canonical).Count());
            foreach (var group in groups)
            {
                var members = catalog.BrowseHomeCharacters(home, group.Id);
                Assert.All(members, e => Assert.Equal(home, e.EffectiveBrowseHome));
                var first = members[0];
                foreach (var query in new[] { first.Canonical!, first.Japanese! })
                {
                    var hits = catalog.SearchHomeCharacters(home, group.Id, query);
                    Assert.Contains(hits, h => h.Entry.Canonical == first.Canonical);
                    Assert.All(hits, h => Assert.Contains(h.Entry, members));
                }
            }
        }
        var watch = Stopwatch.StartNew();
        for (var i = 0; i < 1000; i++) _ = catalog.BrowseHomeCharacters("pokemon", "generation_1");
        watch.Stop();
        output.WriteLine($"1000 preindexed group queries: {watch.Elapsed.TotalMilliseconds:F3} ms");
        Assert.True(watch.Elapsed.TotalMilliseconds < 500);
    }
}
