using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue141DiscoveryTests
{
    [Fact]
    public void CopyrightBrowseExposesAllCharactersAndSupportsBidirectionalDrilldown()
    {
        var workOne = Identity("R:series_one", "series_one", "作品一", "Copyright", 1000);
        var workTwo = Identity("R:series_two", "series_two", "作品二", "Copyright", 900);
        var characters = Enumerable.Range(1, 8)
            .Select(i => Identity($"C:hero_{i}", $"hero_{i}", $"キャラ{i}", "Character", 100 - i,
                i == 1 ? ["series_one", "series_two"] : ["series_one"]))
            .ToArray();
        var catalog = new Catalog([workOne, workTwo, .. characters]);
        var vm = Workspace(catalog, UnifiedBrowseScope.Copyright);

        var workRow = Assert.Single(vm.Results, row => row.Entry.Canonical == "series_one");
        Assert.Equal(8, workRow.RelatedCount);
        Assert.Contains("関連キャラ 8件", workRow.RelationSummary);

        workRow.OpenRelated.Execute(null);

        Assert.True(vm.ShowRelationBanner);
        Assert.Contains("作品「作品一」のキャラクター", vm.RelationBannerText);
        Assert.Equal(UnifiedBrowseScope.Character, vm.Scope);
        Assert.Equal(8, vm.Results.Count);
        Assert.All(vm.Results, row => Assert.Equal("Character", row.Entry.EffectiveCategory));

        var hero = Assert.Single(vm.Results, row => row.Entry.Canonical == "hero_1");
        Assert.Contains("作品一", hero.RelationSummary);
        Assert.Contains("作品二", hero.RelationSummary);

        hero.OpenRelated.Execute(null);

        Assert.Equal(UnifiedBrowseScope.Copyright, vm.Scope);
        Assert.Equal(new[] { "series_one", "series_two" },
            vm.Results.Select(row => row.Entry.Canonical).OrderBy(value => value).ToArray());

        vm.ClearRelatedBrowse();

        Assert.False(vm.ShowRelationBanner);
        Assert.Equal(UnifiedBrowseScope.Character, vm.Scope);
        Assert.Equal(8, vm.Results.Count);
    }

    [Fact]
    public void SearchTargetCanSwitchBetweenGlobalCharacterCopyrightAndArtist()
    {
        var character = Identity("C:shared_character", "shared_character", "共有キャラ", "Character", 400,
            ["shared_work"], ["共通検索"]);
        var copyright = Identity("R:shared_work", "shared_work", "共有作品", "Copyright", 300, null, ["共通検索"]);
        var artist = Identity("A:shared_artist", "shared_artist", "共有作者", "Artist", 200, null, ["共通検索"]);
        var general = new CatalogEntry("G:shared_general", "shared_general", "shared_general", "共有一般", false, 100, [], ["共通検索"], []);
        var catalog = new Catalog([character, copyright, artist, general]);
        var vm = Workspace(catalog, UnifiedBrowseScope.Tags);

        vm.Query = "共通検索";
        vm.RefreshResults();
        Assert.Equal(4, vm.Results.Count);

        vm.SetSearchTarget(DictionarySearchTarget.Character);
        Assert.Single(vm.Results);
        Assert.Equal("Character", vm.Results[0].Entry.EffectiveCategory);

        vm.SetSearchTarget(DictionarySearchTarget.Copyright);
        Assert.Single(vm.Results);
        Assert.Equal("Copyright", vm.Results[0].Entry.EffectiveCategory);

        vm.SetSearchTarget(DictionarySearchTarget.Artist);
        Assert.Single(vm.Results);
        Assert.Equal("Artist", vm.Results[0].Entry.EffectiveCategory);

        vm.SetSearchTarget(DictionarySearchTarget.All);
        Assert.Equal(4, vm.Results.Count);
    }

    [Fact]
    public void IdentityNavigationGroupsWorksAndCharactersWithoutMixingArtist()
    {
        var catalog = new Catalog([
            Identity("C:hero", "hero", "キャラ", "Character", 10, ["work"]),
            Identity("R:work", "work", "作品", "Copyright", 20),
            Identity("A:artist", "artist", "作者", "Artist", 30)
        ]);
        var vm = Workspace(catalog, UnifiedBrowseScope.Tags);

        var group = Assert.Single(vm.Navigation, node => node.Key == "identity-group");
        Assert.Equal("キャラクター・作品", group.Label);
        Assert.Equal(new[] { "copyright", "character" }, group.Children.Select(node => node.Key).ToArray());
        Assert.Contains(vm.Navigation, node => node.Key == "artist" && node.Label == "作者");
    }

    private static DictionaryWorkspaceViewModel Workspace(Catalog catalog, UnifiedBrowseScope scope)
    {
        var prompt = new PromptWorkspace(new PromptParser(catalog));
        var vm = new DictionaryWorkspaceViewModel(
            catalog,
            prompt,
            new PendingGeneralBrowseProvider(),
            () => { },
            () => true);
        vm.Restore(new UiState(BrowseScope: scope.ToString()));
        vm.RefreshResults();
        return vm;
    }

    private static CatalogEntry Identity(
        string id,
        string canonical,
        string japanese,
        string category,
        long usage,
        string[]? related = null,
        string[]? japaneseSearch = null)
        => new(id, canonical, canonical, japanese, false, usage, [], japaneseSearch ?? [], [])
        {
            TagCategory = category,
            RelatedCopyright = related ?? []
        };
}
