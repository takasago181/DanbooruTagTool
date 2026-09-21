using System.IO;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue70IntegrationTests
{
    [Fact]
    public void RuntimeOverlayHasExactCoverageAndRelations()
    {
        var root = FindRepoRoot();
        var entries = Issue70CatalogOverlayImporter.Read(Path.Combine(root, Issue70CatalogOverlayImporter.RelativePath));
        Assert.Equal(Issue70CatalogOverlayImporter.TotalCount, entries.Length);
        Assert.Equal(Issue70CatalogOverlayImporter.CharacterCount, entries.Count(e => e.EffectiveCategory == "Character"));
        Assert.Equal(Issue70CatalogOverlayImporter.CopyrightCount, entries.Count(e => e.EffectiveCategory == "Copyright"));
        Assert.Equal(Issue70CatalogOverlayImporter.ArtistCount, entries.Count(e => e.EffectiveCategory == "Artist"));
        Assert.Equal(Issue70CatalogOverlayImporter.CharacterWithRelationsCount, entries.Count(e => e.EffectiveCategory == "Character" && e.RelatedCopyright.Length > 0));
        Assert.DoesNotContain(entries, e => e.Canonical == "tenga");
        var miku = entries.Single(e => e.Canonical == "hatsune_miku");
        Assert.Equal("Character", miku.EffectiveCategory);
        Assert.Contains("vocaloid", miku.RelatedCopyright);
        Assert.False(string.IsNullOrWhiteSpace(miku.Japanese));
    }

    [Fact]
    public void CharacterAndCopyrightRemainBrowseableWhileArtistAndCooccurrenceRelationsAreHidden()
    {
        var character = new CatalogEntry("C:hatsune_miku", "hatsune_miku", "hatsune_miku", "初音ミク", false, 145166, ["miku"], ["ミク"], [])
        { TagCategory = "Character", RelatedCopyright = ["vocaloid"] };
        var copyright = new CatalogEntry("R:vocaloid", "vocaloid", "vocaloid", "VOCALOID", false, 200000, [], ["ボーカロイド"], []) { TagCategory = "Copyright" };
        var artist = new CatalogEntry("A:nagano_mamoru", "nagano_mamoru", "nagano_mamoru", "永野護", false, 1000, [], ["artist"], []) { TagCategory = "Artist" };
        var general = Fixtures.Entry("blue_hair", "青い髪", 100);
        var special = Fixtures.Entry("anal", "アナル", 100, special: true);
        var catalog = new Catalog([general, special, character, copyright, artist]);
        var vm = new MainViewModel(catalog, new MemoryStore(), new MemoryClipboard(), GeneralBrowseProvider.FromCatalog(catalog));

        var identity = Assert.Single(vm.Navigation, n => n.Key == "identity-group" && n.Label == "キャラクター・作品");
        Assert.Contains(identity.Children, n => n.Key == "character" && n.Label == "キャラクターから探す");
        Assert.Contains(identity.Children, n => n.Key == "copyright" && n.Label == "作品から探す");
        Assert.DoesNotContain(vm.Navigation, n => n.Key == "artist");

        vm.NavigateTo("character");
        var characterRow = Assert.Single(vm.Results);
        Assert.Equal("hatsune_miku", characterRow.Entry.Canonical);
        Assert.Equal("", characterRow.RelationSummary);
        Assert.False(characterRow.HasRelated);
        vm.SelectedEntry = characterRow;
        Assert.Empty(vm.Related);

        vm.Query = "ミク";
        vm.RefreshResults();
        Assert.Contains(vm.Results, r => r.Entry.Canonical == "hatsune_miku");

        vm.NavigateTo("copyright");
        vm.ClearQuery.Execute(null);
        var copyrightRow = Assert.Single(vm.Results);
        Assert.Equal("vocaloid", copyrightRow.Entry.Canonical);
        Assert.Equal("", copyrightRow.RelationSummary);
        Assert.False(copyrightRow.HasRelated);
        vm.SelectedEntry = copyrightRow;
        Assert.Empty(vm.Related);

        vm.NavigateTo("tags");
        vm.Query = "artist";
        vm.RefreshResults();
        Assert.DoesNotContain(vm.Results, r => r.Entry.EffectiveCategory == "Artist");

        vm.NavigateTo("artist");
        Assert.Equal(UnifiedBrowseScope.Tags, vm.Dictionary.Scope);
        Assert.DoesNotContain(vm.Results, r => r.Entry.EffectiveCategory == "Artist");

        // Data stays intact so a later high-quality Artist/relation implementation
        // can reuse it without rebuilding Issue #70 from scratch.
        Assert.Equal("Artist", artist.EffectiveCategory);
        Assert.Equal(["vocaloid"], character.RelatedCopyright);
    }

    [Fact]
    public void CatalogDatabaseRoundTripPreservesIssue70CategoryRelationsAndSearchMetadata()
    {
        using var temp = new TempDirectory();
        var path = Path.Combine(temp.Path, "catalog.db");
        var character = new CatalogEntry("C:hatsune_miku", "hatsune_miku", "hatsune_miku", "初音ミク", false, 145166, ["miku"], ["ミク"], [])
        { TagCategory = "Character", RelatedCopyright = ["vocaloid"] };
        var copyright = new CatalogEntry("R:vocaloid", "vocaloid", "vocaloid", "VOCALOID", false, 200000, [], ["ボーカロイド"], [])
        { TagCategory = "Copyright" };
        var artist = new CatalogEntry("A:nagano_mamoru", "nagano_mamoru", "nagano_mamoru", "永野護", false, 1000, ["mamoru nagano"], ["ながのまもる"], [])
        { TagCategory = "Artist" };

        CatalogDatabase.Build(path, [character, copyright, artist], "issue70-roundtrip-test");
        var reopened = CatalogDatabase.Open(path);

        var miku = reopened.Entries.Single(e => e.Canonical == "hatsune_miku");
        Assert.Equal("Character", miku.EffectiveCategory);
        Assert.Equal(["vocaloid"], miku.RelatedCopyright);
        Assert.Contains("miku", miku.Aliases);
        Assert.Contains("ミク", miku.JapaneseSearch);
        Assert.Equal("Copyright", reopened.Entries.Single(e => e.Canonical == "vocaloid").EffectiveCategory);
        Assert.Equal("Artist", reopened.Entries.Single(e => e.Canonical == "nagano_mamoru").EffectiveCategory);

        var search = new SearchEngine(reopened);
        Assert.Contains(search.Search("ミク"), hit => hit.Entry.Canonical == "hatsune_miku");
        Assert.Contains(search.Search("miku"), hit => hit.Entry.Canonical == "hatsune_miku");
        Assert.Contains(search.Search("ながのまもる"), hit => hit.Entry.Canonical == "nagano_mamoru");
    }

    private static string FindRepoRoot()
    {
        DirectoryInfo? dir = new(AppContext.BaseDirectory);
        while (dir != null && !File.Exists(Path.Combine(dir.FullName, "AGENTS.md"))) dir = dir.Parent;
        return dir?.FullName ?? throw new DirectoryNotFoundException("Repository root not found");
    }
}
