using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue141DiscoveryTests
{
    [Fact]
    public void CharacterCopyrightBrowseRemainAvailableWhileCooccurrenceDrilldownIsDisabled()
    {
        var workOne = Identity("R:series_one", "series_one", "作品一", "Copyright", 1000);
        var workTwo = Identity("R:series_two", "series_two", "作品二", "Copyright", 900);
        var characters = Enumerable.Range(1, 8)
            .Select(i => Identity($"C:hero_{i}", $"hero_{i}", $"キャラ{i}", "Character", 100 - i,
                i == 1 ? ["series_one", "series_two"] : ["series_one"]))
            .ToArray();
        var catalog = new Catalog([workOne, workTwo, .. characters]);

        var copyrightVm = Workspace(catalog, UnifiedBrowseScope.Copyright);
        var workRow = Assert.Single(copyrightVm.Results, row => row.Entry.Canonical == "series_one");
        Assert.Equal(0, workRow.RelatedCount);
        Assert.Equal("", workRow.RelationSummary);
        Assert.False(workRow.HasRelated);
        Assert.False(workRow.OpenRelated.CanExecute(null));

        copyrightVm.OpenRelated(workRow.Entry);
        Assert.False(copyrightVm.ShowRelationBanner);
        Assert.Equal(UnifiedBrowseScope.Copyright, copyrightVm.Scope);
        Assert.Equal(2, copyrightVm.Results.Count);

        var characterVm = Workspace(catalog, UnifiedBrowseScope.Character);
        var hero = Assert.Single(characterVm.Results, row => row.Entry.Canonical == "hero_1");
        Assert.Equal(0, hero.RelatedCount);
        Assert.Equal("", hero.RelationSummary);
        Assert.False(hero.HasRelated);
        Assert.False(hero.OpenRelated.CanExecute(null));

        characterVm.OpenRelated(hero.Entry);
        Assert.False(characterVm.ShowRelationBanner);
        Assert.Equal(UnifiedBrowseScope.Character, characterVm.Scope);
        Assert.Equal(8, characterVm.Results.Count);

        // Source metadata is deliberately retained for a later high-precision rebuild.
        Assert.Equal(["series_one", "series_two"], hero.Entry.RelatedCopyright);
    }

    [Fact]
    public void SearchTargetKeepsCharacterAndCopyrightWhileArtistFallsBackToHiddenAll()
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
        Assert.Equal(3, vm.Results.Count);
        Assert.DoesNotContain(vm.Results, row => row.Entry.EffectiveCategory == "Artist");

        vm.SetSearchTarget(DictionarySearchTarget.Character);
        Assert.Single(vm.Results);
        Assert.Equal("Character", vm.Results[0].Entry.EffectiveCategory);

        vm.SetSearchTarget(DictionarySearchTarget.Copyright);
        Assert.Single(vm.Results);
        Assert.Equal("Copyright", vm.Results[0].Entry.EffectiveCategory);

        vm.SetSearchTarget(DictionarySearchTarget.Artist);
        Assert.Equal(DictionarySearchTarget.All, vm.SearchTarget);
        Assert.Equal(3, vm.Results.Count);
        Assert.DoesNotContain(vm.Results, row => row.Entry.EffectiveCategory == "Artist");

        Assert.Single(catalog.BrowseCategory("Artist", false));
    }

    [Fact]
    public void IdentityNavigationKeepsCharacterAndCopyrightButHidesArtist()
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
        Assert.DoesNotContain(vm.Navigation, node => node.Key == "artist");
        Assert.Single(catalog.BrowseCategory("Artist", false));
    }

    [Fact]
    public void SpecialSearchDoesNotGainDeadRelatedActionFromIssue177Mitigation()
    {
        var path = new BrowsePath("ACTION", "行動");
        var first = new CatalogEntry("S:first", "special_first", "special_first", "特殊一", true, 100, [], [], [path]);
        var second = new CatalogEntry("S:second", "special_second", "special_second", "特殊二", true, 90, [], [], [path]);
        var catalog = new Catalog([first, second]);
        var vm = Workspace(catalog, UnifiedBrowseScope.Tags);

        vm.Query = "special_first";
        vm.RefreshResults();

        var row = Assert.Single(vm.Results);
        Assert.Equal(0, row.RelatedCount);
        Assert.False(row.HasRelated);
        Assert.False(row.OpenRelated.CanExecute(null));
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
