using System.IO;
using System.IO.Compression;
using System.Text;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public sealed class AuthorityExportFactAttribute : FactAttribute
{
    public AuthorityExportFactAttribute()
    {
        if (Environment.GetEnvironmentVariable("DTT_EXPORT_AUTHORITY") is null) Skip = "One-time migration export; never runs during normal tests.";
    }
}

public sealed class FoundationCatalogTests(ITestOutputHelper output)
{
    [Fact]
    public void ProductionAssembliesDoNotContainHistoricalBuildOwnersOrDeadFacetState()
    {
        var types = typeof(CatalogDatabase).Assembly.GetTypes().Select(t => t.Name).ToArray();
        Assert.DoesNotContain(types, name => name.StartsWith("Issue", StringComparison.Ordinal) || name is "AcceptedAssetImporter" or "SpecialBrowseV2Overlay" or "UnifiedBrowseOverlay");
        var vm = typeof(DanbooruTagTool.App.ViewModels.DictionaryWorkspaceViewModel);
        foreach (var name in new[] { "SpecialKindOptions", "SpecialBodyOptions", "SpecialThemeOptions", "ToggleSpecialFacet", "UndoSpecialFacet", "ClearSpecialFacets" })
            Assert.Null(vm.GetProperty(name));
        Assert.NotNull(vm.GetProperty("BodyOptions"));
        Assert.NotNull(vm.GetProperty("ThemeOptions"));
    }
    internal static string ManifestPath
    {
        get
        {
            var root = new DirectoryInfo(AppContext.BaseDirectory);
            while (root is not null)
            {
                var path = Path.Combine(root.FullName, "authority/catalog/current/manifest.json");
                if (File.Exists(path)) return path;
                root = root.Parent;
            }
            throw new FileNotFoundException("Accepted semantic authority manifest is required for Foundation parity.");
        }
    }

    internal static ImportResult LegacyBuild()
    {
        var root = Environment.GetEnvironmentVariable("DTT_AUTHORITY_ROOT")!;
        var imported = AcceptedAssetImporter.Read(Environment.GetEnvironmentVariable("DTT_SOURCE_ROOT")!, root);
        var special = SpecialBrowseV2Overlay.Bake(new Catalog(imported.Entries));
        var unified = UnifiedBrowseOverlay.Bake(new Catalog(special), root);
        var routes = Issue132RouteOverlay.Bake(new Catalog(unified));
        var intent = Issue118SexualIntentV2Overlay.Bake(new Catalog(routes), root, imported.SourceHashes);
        var facets = Issue199GeneralFacetOverlay.Bake(new Catalog(intent));
        imported.SourceHashes[Issue199GeneralFacetOverlay.RelativePath] = Issue199GeneralFacetOverlay.ExpectedSha256;
        return imported with { Entries = facets };
    }

    internal static void EqualRows(IReadOnlyList<CatalogEntry> expected, IReadOnlyList<CatalogEntry> actual)
    {
        Assert.Equal(expected.Count, actual.Count);
        for (var i = 0; i < expected.Count; i++)
            Assert.True(JsonSerializer.Serialize(expected[i]) == JsonSerializer.Serialize(actual[i]), $"Semantic field/order drift at ordinal {i}: {expected[i].Id} / {actual[i].Id}");
    }

    [AuthorityExportFact]
    public void ExportAcceptedAuthorityAfterLegacyAndInstalledParity()
    {
        var legacy = LegacyBuild();
        var installed = CatalogDatabase.Open(Environment.GetEnvironmentVariable("DTT_PRODUCTION_CATALOG")!);
        EqualRows(installed.Entries, legacy.Entries);
        var target = Environment.GetEnvironmentVariable("DTT_EXPORT_AUTHORITY")!;
        Assert.False(Directory.Exists(target));
        Directory.CreateDirectory(target);
        var assets = new List<AuthorityAsset>();
        foreach (var category in legacy.Entries.Select(e => e.EffectiveCategory).Distinct())
        {
            var name = category.ToLowerInvariant() + ".jsonl.gz";
            var rows = legacy.Entries.Select((e, i) => new AuthorityRow(i, e)).Where(r => r.Entry.EffectiveCategory == category).ToArray();
            using (var file = File.Create(Path.Combine(target, name)))
            using (var gzip = new GZipStream(file, CompressionLevel.SmallestSize))
            using (var writer = new StreamWriter(gzip, new UTF8Encoding(false)))
                foreach (var row in rows) writer.WriteLine(JsonSerializer.Serialize(row, CatalogAuthorityReader.Json));
            assets.Add(new(name, CatalogAuthorityReader.Hash(Path.Combine(target, name)), rows.Length, category));
        }
        var manifest = new CatalogAuthorityManifest(CatalogAuthorityReader.Schema, "accepted-2026-10-03",
            assets.ToArray(), legacy.Entries.GroupBy(e => e.EffectiveCategory).ToDictionary(g => g.Key, g => g.Count()),
            CatalogAuthorityReader.IdentityHash(legacy.Entries), CatalogAuthorityReader.IdentityHash(legacy.Entries.Where(e => e.IsSpecial)));
        var pretty = new JsonSerializerOptions(CatalogAuthorityReader.Json) { WriteIndented = true };
        File.WriteAllText(Path.Combine(target, "manifest.json"), JsonSerializer.Serialize(manifest, pretty) + "\n");
        File.WriteAllText(Path.Combine(target, "provenance.json"), JsonSerializer.Serialize(new
        {
            SourceMain = "0d76ee2d6df2af6831f88dbfc56436b7bc7daf66", ProductionSource = "b3f48c359a8473c8bbf02347487cba5d8dacf96c",
            InstalledCatalogSha256 = CatalogAuthorityReader.Hash(Environment.GetEnvironmentVariable("DTT_PRODUCTION_CATALOG")!),
            Migration = "test-only legacy build, same accepted inputs, complete ordered field parity against installed LKG; no semantic changes",
            HistoricalSources = legacy.SourceHashes
        }, new JsonSerializerOptions { WriteIndented = true }) + "\n");
        EqualRows(legacy.Entries, CatalogAuthorityReader.Read(Path.Combine(target, "manifest.json")).Entries);
        output.WriteLine($"PASS migration: {legacy.Entries.Length} complete ordered payloads match installed LKG and accepted snapshot.");
    }

    [Fact]
    public void AcceptedSnapshotCompilesWithoutProtectedSourcesOrHistoricalEvidence()
    {
        using var temp = new TempDirectory();
        var authorityRoot = Path.GetDirectoryName(ManifestPath)!;
        var copy = Path.Combine(temp.Path, "semantic-input"); Directory.CreateDirectory(copy);
        foreach (var file in Directory.EnumerateFiles(authorityRoot)) File.Copy(file, Path.Combine(copy, Path.GetFileName(file)));
        var built = Path.Combine(temp.Path, "compiled");
        var authority = CatalogCompiler.Compile(Path.Combine(copy, "manifest.json"), built);
        EqualRows(authority.Entries, CatalogDatabase.Open(Path.Combine(built, "catalog.db")).Entries);
        Assert.Throws<IOException>(() => CatalogCompiler.Compile(Path.Combine(copy, "manifest.json"), built));
        output.WriteLine($"PASS {authority.Entries.Length} rows compiled using only current semantic inputs; no Issue files or protected source corpus.");
    }

    [ProductionFact]
    public void LegacyNewAndInstalledHaveCompleteSemanticParity()
    {
        var legacy = LegacyBuild();
        var authority = CatalogAuthorityReader.Read(ManifestPath);
        EqualRows(legacy.Entries, authority.Entries);
        EqualRows(CatalogDatabase.Open(Environment.GetEnvironmentVariable("DTT_PRODUCTION_CATALOG")!).Entries, authority.Entries);
        var oldCatalog = new Catalog(legacy.Entries);
        var newCatalog = new Catalog(authority.Entries);
        var beforeSearch = new SearchEngine(oldCatalog);
        var afterSearch = new SearchEngine(newCatalog);
        foreach (var query in new[] { "anal", "アナル", "尿道", "urethral_insertion", "ball gag", "拘束", "触手", "tentacles", "fluid", "restraint", "fellatio", "青い hair" })
            Assert.Equal(beforeSearch.Search(query).Select(h => (h.Entry.Id, h.Rank)), afterSearch.Search(query).Select(h => (h.Entry.Id, h.Rank)));
        var beforeBrowse = new UnifiedBrowseIndex(oldCatalog);
        var afterBrowse = new UnifiedBrowseIndex(newCatalog);
        foreach (var route in UnifiedBrowseTaxonomy.Routes)
        foreach (var intent in Enum.GetValues<ContentIntentFilter>())
        foreach (var deep in new[] { false, true })
        {
            var state = UnifiedBrowseState.Neutral.WithPrimary(route.Id) with { ContentIntent = intent, DeepOnly = deep };
            Assert.Equal(beforeBrowse.Browse(state).Select(e => e.Id), afterBrowse.Browse(state).Select(e => e.Id));
            foreach (var body in SpecialBrowseV2Taxonomy.BodySites) Assert.Equal(beforeBrowse.CountWithBodySite(state, body.Id), afterBrowse.CountWithBodySite(state, body.Id));
            foreach (var theme in SpecialBrowseV2Taxonomy.Themes) Assert.Equal(beforeBrowse.CountWithTheme(state, theme.Id), afterBrowse.CountWithTheme(state, theme.Id));
        }
        output.WriteLine("PASS every persisted and derived CatalogEntry field, ordinal, accepted population, canonical identity, stable Special IDs, adult/hard-niche vocab, SexualIntent, Unified routes/facets, HOME/group, reviewed display/search quality.");
    }

    [Fact]
    public void SameSchemaReplacementNeedsOnlyDataAndManifestChanges()
    {
        using var temp = new TempDirectory();
        var entry = Fixtures.Entry("foundation_example", "差替fixture");
        var name = "renamed-input.jsonl.gz";
        using (var file = File.Create(Path.Combine(temp.Path, name)))
        using (var gz = new GZipStream(file, CompressionMode.Compress))
        using (var writer = new StreamWriter(gz)) writer.WriteLine(JsonSerializer.Serialize(new AuthorityRow(0, entry), CatalogAuthorityReader.Json));
        var manifest = new CatalogAuthorityManifest(CatalogAuthorityReader.Schema, "different-snapshot",
            [new(name, CatalogAuthorityReader.Hash(Path.Combine(temp.Path, name)), 1, "General")],
            new() { ["General"] = 1 }, CatalogAuthorityReader.IdentityHash([entry]), CatalogAuthorityReader.IdentityHash([]));
        var path = Path.Combine(temp.Path, "manifest.json");
        File.WriteAllText(path, JsonSerializer.Serialize(manifest, CatalogAuthorityReader.Json));
        Assert.Equal(entry.Id, Assert.Single(CatalogAuthorityReader.Read(path).Entries).Id);
        File.AppendAllText(Path.Combine(temp.Path, name), "corrupt");
        Assert.Throws<InvalidDataException>(() => CatalogAuthorityReader.Read(path));
    }

    [Fact]
    public void CompilerRefusesAuthorityUserDataLinksAndExistingFilesWithoutMutation()
    {
        using var temp = new TempDirectory();
        var protectedFile = Path.Combine(temp.Path, "keep.txt"); File.WriteAllText(protectedFile, "user-owned");
        Assert.Throws<IOException>(() => CatalogCompiler.Compile(ManifestPath, temp.Path));
        Assert.Equal("user-owned", File.ReadAllText(protectedFile));
        Assert.Throws<ArgumentException>(() => CatalogCompiler.Compile(ManifestPath, Path.GetDirectoryName(ManifestPath)!));
        Assert.Throws<ArgumentException>(() => CatalogCompiler.Compile(ManifestPath, Path.Combine(temp.Path, "UserData", "candidate")));
        Assert.False(Directory.Exists(Path.Combine(temp.Path, "UserData")));
    }

    [Fact]
    public void ManifestRejectsUnknownSchemaPopulationIdentityAndEscapingInput()
    {
        using var temp = new TempDirectory();
        var original = CatalogAuthorityReader.Read(ManifestPath).Manifest;
        var path = Path.Combine(temp.Path, "manifest.json");
        File.WriteAllText(path, JsonSerializer.Serialize(original with { Schema = "future-version" }, CatalogAuthorityReader.Json));
        Assert.Throws<InvalidDataException>(() => CatalogAuthorityReader.Read(path));
        File.WriteAllText(path, JsonSerializer.Serialize(original with { Assets = [original.Assets[0] with { Path = "../outside.gz" }] }, CatalogAuthorityReader.Json));
        Assert.Throws<InvalidDataException>(() => CatalogAuthorityReader.Read(path));
        foreach (var asset in original.Assets) File.Copy(Path.Combine(Path.GetDirectoryName(ManifestPath)!, asset.Path), Path.Combine(temp.Path, asset.Path));
        File.WriteAllText(path, JsonSerializer.Serialize(original with { IdentitySha256 = "incorrect" }, CatalogAuthorityReader.Json));
        Assert.Throws<InvalidDataException>(() => CatalogAuthorityReader.Read(path));
        File.WriteAllText(path, JsonSerializer.Serialize(original with { CategoryCounts = new() { ["General"] = 1 } }, CatalogAuthorityReader.Json));
        Assert.Throws<InvalidDataException>(() => CatalogAuthorityReader.Read(path));
    }
}
