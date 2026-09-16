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
        Assert.Equal(35597, entries.Count(e => e.EffectiveCategory == "Character" && e.RelatedCopyright.Length > 0));
        var miku = entries.Single(e => e.Canonical == "hatsune_miku");
        Assert.Equal("Character", miku.EffectiveCategory);
        Assert.Contains("vocaloid", miku.RelatedCopyright);
        Assert.False(string.IsNullOrWhiteSpace(miku.Japanese));
    }

    [Fact]
    public void CharacterCopyrightArtistSearchBrowseAndRelationsStaySeparateFromGeneralSpecial()
    {
        var character = new CatalogEntry("C:hatsune_miku", "hatsune_miku", "hatsune_miku", "初音ミク", false, 145166, ["miku"], ["ミク"], [])
        { TagCategory = "Character", RelatedCopyright = ["vocaloid"] };
        var copyright = new CatalogEntry("R:vocaloid", "vocaloid", "vocaloid", "VOCALOID", false, 200000, [], ["ボーカロイド"], []) { TagCategory = "Copyright" };
        var artist = new CatalogEntry("A:nagano_mamoru", "nagano_mamoru", "nagano_mamoru", "永野護", false, 1000, [], [], []) { TagCategory = "Artist" };
        var general = Fixtures.Entry("blue_hair", "青い髪", 100);
        var special = Fixtures.Entry("anal", "アナル", 100, special: true);
        var catalog = new Catalog([general, special, character, copyright, artist]);
        var vm = new MainViewModel(catalog, new MemoryStore(), new MemoryClipboard(), GeneralBrowseProvider.FromCatalog(catalog));

        Assert.Equal("General", general.EffectiveCategory);
        Assert.Equal("Special", special.EffectiveCategory);
        Assert.Contains(vm.Navigation, n => n.Key == "character" && n.Label == "キャラクター");
        Assert.Contains(vm.Navigation, n => n.Key == "copyright" && n.Label == "作品");
        Assert.Contains(vm.Navigation, n => n.Key == "artist" && n.Label == "作者");

        vm.NavigateTo("character");
        Assert.Single(vm.Results);
        Assert.Equal("hatsune_miku", vm.Results[0].Entry.Canonical);
        vm.SelectedEntry = vm.Results[0];
        Assert.Contains(vm.Related, r => r.Entry.Canonical == "vocaloid");

        vm.Query = "ミク"; vm.RefreshResults();
        Assert.Contains(vm.Results, r => r.Entry.Canonical == "hatsune_miku");
        vm.Query = "miku"; vm.RefreshResults();
        Assert.Contains(vm.Results, r => r.Entry.Canonical == "hatsune_miku");

        vm.NavigateTo("copyright");
        vm.SelectedEntry = vm.Results.Single(r => r.Entry.Canonical == "vocaloid");
        Assert.Contains(vm.Related, r => r.Entry.Canonical == "hatsune_miku");

        vm.NavigateTo("artist");
        Assert.Contains(vm.Results, r => r.Entry.Canonical == "nagano_mamoru" && r.Entry.Japanese == "永野護");
    }

    private static string FindRepoRoot()
    {
        DirectoryInfo? dir = new(AppContext.BaseDirectory);
        while (dir != null && !File.Exists(Path.Combine(dir.FullName, "AGENTS.md"))) dir = dir.Parent;
        return dir?.FullName ?? throw new DirectoryNotFoundException("Repository root not found");
    }
}
