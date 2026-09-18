using System.IO;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using DanbooruTagTool.App.ViewModels;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;
public class TechnicalFixTests(ITestOutputHelper output)
{
    [Fact] public void UnifiedNavigationConsumesAcceptedGeneralPathsWithoutGeneralSpecialRoots()
    {
        var path = new BrowsePath("HAIR_FACE", "髪・顔", "HAIR", "Fixture child");
        var red = Fixtures.Entry("red_hair", "赤い髪") with
        {
            Paths = [path],
            BrowseClassification = BrowseClassificationStatus.Proposed
        };
        var catalog = new Catalog([red]);
        var vm = new MainViewModel(catalog, new MemoryStore(), new MemoryClipboard(), GeneralBrowseProvider.FromCatalog(catalog));

        Assert.DoesNotContain(vm.Navigation, node => node.Key is "general" or "special");
        Assert.Equal(22, vm.Navigation.Count);

        var route = Assert.Single(vm.Navigation, node => node.Key == "route:HAIR_FACE");
        vm.NavigateTo(route.Key);
        Assert.Equal("red_hair", Assert.Single(vm.Results).Entry.Canonical);
        Assert.Equal("髪・顔", vm.BrowseLabel);

        var local = Assert.Single(vm.Dictionary.LocalOptions);
        Assert.Equal("Fixture child", local.Label);
        vm.Dictionary.SetLocalSubroute(local.Id);
        Assert.Equal("red_hair", Assert.Single(vm.Results).Entry.Canonical);
        Assert.Equal("Fixture child", vm.BrowseLabel);
    }
    [Theory]
    [InlineData("data", true)] [InlineData("data/child", true)] [InlineData("DATA/child", true)]
    [InlineData("data/../data", true)] [InlineData("data2", false)] [InlineData("src/artifacts/build", false)]
    public void OutputGuardHandlesEqualityChildrenAndSiblings(string relative, bool reject)
    {
        using var root = new TempDirectory(); using var authority = new TempDirectory();
        foreach (var protectedRoot in new[] { root.Path, authority.Path })
        {
            var path = Path.Combine(protectedRoot, relative);
            if (reject) Assert.Throws<ArgumentException>(() => CatalogOutputGuard.Validate(path, root.Path, authority.Path));
            else Assert.Equal(Path.GetFullPath(path), CatalogOutputGuard.Validate(path, root.Path, authority.Path));
        }
        using var external = new TempDirectory();
        Assert.Equal(external.Path, CatalogOutputGuard.Validate(external.Path, root.Path, authority.Path));
    }
    [Fact] public void OutputGuardRejectsAuthorityIssue56AndAllowsSiblings()
    {
        using var authority = new TempDirectory(); using var source = new TempDirectory(); using var external = new TempDirectory();
        foreach (var relative in new[] { "docs/issue56", "docs/issue56/rollout", "docs/issue56/rollout/reviewed" })
            Assert.Throws<ArgumentException>(() => CatalogOutputGuard.Validate(Path.Combine(authority.Path, relative), source.Path, authority.Path));
        Assert.Equal(Path.GetFullPath(Path.Combine(authority.Path, "docs2")), CatalogOutputGuard.Validate(Path.Combine(authority.Path, "docs2"), source.Path, authority.Path));
        Assert.Equal(Path.GetFullPath(Path.Combine(source.Path, "src", "artifacts", "build")), CatalogOutputGuard.Validate(Path.Combine(source.Path, "src", "artifacts", "build"), source.Path, authority.Path));
        Assert.Equal(external.Path, CatalogOutputGuard.Validate(external.Path, source.Path, authority.Path));
    }
    [Fact] public void SpecialExactCanonicalNullAndPrecedencePreserveSurface()
    {
        var general = Fixtures.Entry("blue_hair", "General display");
        var special = Fixtures.Entry("blue_hair", "Special display", special: true) with { English = "special blue" };
        var semantic = new CatalogEntry("S:only", null, "known concept", "既知の概念", true, null, [], [], []);
        foreach (var rows in new[] { new[] { general, special, semantic }, new[] { semantic, special, general } })
        {
            var catalog = new Catalog(rows);
            Assert.Equal(special, catalog.Resolve("blue_hair")); Assert.Equal(special, catalog.Resolve("special blue"));
            var parser = new PromptParser(catalog); var raw = " special blue ,known concept,blue_hair";
            var items = parser.Parse(raw); Assert.Equal(raw, PromptParser.Serialize(items));
            Assert.Equal(special.Id, items[0].CatalogId); Assert.Equal("blue_hair", items[0].Canonical);
            Assert.Equal(semantic.Id, items[1].CatalogId); Assert.Equal(semantic.Japanese, items[1].Display);
            Assert.Null(items[1].Canonical); Assert.False(semantic.CanAdd);
            var vm = new MainViewModel(catalog, new MemoryStore(), new MemoryClipboard());
            vm.Workspace.Replace(raw); vm.Inspect.Execute(vm.Chips[0]); Assert.Equal(special, vm.SelectedEntry?.Entry);
            vm.Inspect.Execute(vm.Chips[1]); Assert.Equal(semantic, vm.SelectedEntry?.Entry);
        }
    }
    [Fact] public void ConflictingSpecialEnglishAndAmbiguousAliasRemainUnresolved()
    {
        var a = Fixtures.Entry("a", "一", aliases: ["alias"], special: true) with { English = "same" };
        var b = Fixtures.Entry("b", "二", aliases: ["alias"], special: true) with { English = "same" };
        var catalog = new Catalog([a,b]);
        Assert.Null(catalog.Resolve("same")); Assert.Null(catalog.Resolve("alias"));
        Assert.All(new PromptParser(catalog).Parse("same,alias"), i => Assert.Equal(PromptItemKind.Raw, i.Kind));
        Assert.Null(new Catalog([a, b with { Canonical = null }]).Resolve("same"));
    }
    [ProductionFact] public void ProductionExamplesAndAcceptedInputIsolation()
    {
        var catalog = CatalogDatabase.Open(Environment.GetEnvironmentVariable("DTT_PRODUCTION_CATALOG")!);
        foreach (var e in new[] {
            catalog.Entries.First(e => e.IsSpecial && e.Canonical != null && SearchEngine.Normalize(e.English) != SearchEngine.Normalize(e.Canonical) && catalog.Resolve(e.English)?.Id == e.Id),
            catalog.Entries.First(e => e.IsSpecial && e.Canonical == null && catalog.Resolve(e.English)?.Id == e.Id) })
        {
            var item = Assert.Single(new PromptParser(catalog).Parse(e.English));
            Assert.Equal(e.Id, item.CatalogId); Assert.Equal(e.English, item.Surface); Assert.Equal(e.Japanese, item.Japanese);
            Assert.Equal(e.Canonical, item.Canonical);
            output.WriteLine($"Example {e.Id}: English={e.English}, canonical={e.Canonical ?? "null"}, Japanese={e.Japanese}");
        }
        var source = Environment.GetEnvironmentVariable("DTT_SOURCE_ROOT");
        var authority = Environment.GetEnvironmentVariable("DTT_AUTHORITY_ROOT");
        Assert.False(string.IsNullOrEmpty(source)); Assert.False(string.IsNullOrEmpty(authority));
        using var isolated = new TempDirectory();
        var files = Issue56Inputs.MappingHashes.Keys.Concat(new[]
        {
            "data/special2788/product_fit_verdicts.csv", AcceptedAssetImporter.ProductionProfileRelativePath, AcceptedAssetImporter.PromotionRelativePath, AcceptedAssetImporter.Issue107PromotionRelativePath,
            "docs/issue56/rollout/issue56_ui_genre_taxonomy_v1.json",
            AcceptedGeneralTaxonomyImporter.TaxonomyRelativePath, AcceptedGeneralTaxonomyImporter.SidecarRelativePath,
            AcceptedGeneralTaxonomyImporter.ManifestRelativePath
        });
        foreach (var file in files) { var dest = Path.Combine(isolated.Path, file); Directory.CreateDirectory(Path.GetDirectoryName(dest)!); File.Copy(Path.Combine(authority!,file),dest); }
        var before = AcceptedAssetImporter.Read(source!, isolated.Path);
        Assert.Equal(28226,before.Entries.Count(e=>!e.IsSpecial && e.BrowseClassification==BrowseClassificationStatus.Proposed));
        Assert.Equal(2403,before.Entries.Count(e=>!e.IsSpecial && e.BrowseClassification==BrowseClassificationStatus.Unresolved));
        Assert.All(before.Entries.Where(e=>!e.IsSpecial && e.BrowseClassification==BrowseClassificationStatus.Unresolved), e=>Assert.Empty(e.Paths));
        File.WriteAllText(Path.Combine(isolated.Path,"docs/issue56/rollout/reviewed/stray.csv"), "invalid unexpected input");
        var after = AcceptedAssetImporter.Read(source!, isolated.Path);
        Assert.Equal(33688, after.Entries.Length); Assert.Equal(AcceptedAssetImporter.ProductionSpecialCount, after.Entries.Count(e => e.IsSpecial));
        Assert.Equal(JsonSerializer.Serialize(before), JsonSerializer.Serialize(after));
        Assert.DoesNotContain(after.SourceHashes.Keys, k => k.Contains("stray"));
        Assert.All(Issue56Inputs.MappingHashes, p => Assert.Equal(p.Value, after.SourceHashes[p.Key]));
        output.WriteLine($"Accepted mappings: {Issue56Inputs.MappingHashes.Count}; sources: {after.SourceHashes.Count}; stray ignored; hashes unchanged");
    }
}
