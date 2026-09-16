from pathlib import Path

root=Path.cwd()

def patch(rel,old,new):
    p=root/rel
    text=p.read_text(encoding='utf-8-sig')
    if old not in text: raise SystemExit(f'patch anchor missing: {rel}')
    if text.count(old)!=1: raise SystemExit(f'patch anchor non-unique: {rel} {text.count(old)}')
    p.write_text(text.replace(old,new),encoding='utf-8')

patch('src/DanbooruTagTool.Core/Catalog.cs',
'''{
    public string Label => Japanese ?? English;''',
'''{
    // General/Special keep their historical shape; Issue #70 adds the three Danbooru identity categories.
    // EffectiveCategory preserves backward compatibility with older catalog.db JSON that has no TagCategory field.
    public string TagCategory { get; init; } = "";
    public string EffectiveCategory => string.IsNullOrWhiteSpace(TagCategory) ? (IsSpecial ? "Special" : "General") : TagCategory;
    public string[] RelatedCopyright { get; init; } = [];
    public string Label => Japanese ?? English;''')

patch('src/DanbooruTagTool.Data/Storage.cs',
'''        var mappings = catalog.Entries
            .Where(e => !e.IsSpecial && e.Canonical != null && e.BrowseClassification == BrowseClassificationStatus.Proposed && e.Paths.Length > 0)''',
'''        var mappings = catalog.Entries
            .Where(e => e.EffectiveCategory == "General" && e.Canonical != null && e.BrowseClassification == BrowseClassificationStatus.Proposed && e.Paths.Length > 0)''')
patch('src/DanbooruTagTool.Data/Storage.cs',
'''    public IReadOnlyList<CatalogEntry> Browse(string path) => catalog.Entries.Where(e => !e.IsSpecial && e.CanBrowse && e.Canonical != null''',
'''    public IReadOnlyList<CatalogEntry> Browse(string path) => catalog.Entries.Where(e => e.EffectiveCategory == "General" && e.CanBrowse && e.Canonical != null''')

patch('src/DanbooruTagTool.Data/AcceptedAssetImporter.cs',
'''        for (int i = 0; i < entries.Count; i++)
            if (!entries[i].IsSpecial && specialGroups.TryGetValue(entries[i].Canonical!, out var related) && related.All(e => !e.CanSearch))
                entries[i] = entries[i] with { ProductFit = "OUT_OF_SCOPE_PRODUCT" };
        return new(entries.ToArray(), hashes);''',
'''        for (int i = 0; i < entries.Count; i++)
            if (!entries[i].IsSpecial && specialGroups.TryGetValue(entries[i].Canonical!, out var related) && related.All(e => !e.CanSearch))
                entries[i] = entries[i] with { ProductFit = "OUT_OF_SCOPE_PRODUCT" };

        var issue70Path = Authority(Issue70CatalogOverlayImporter.RelativePath);
        var issue70 = Issue70CatalogOverlayImporter.Read(issue70Path);
        var existingCanonical = entries.Where(e => e.Canonical != null).Select(e => e.Canonical!).ToHashSet(StringComparer.Ordinal);
        var overlap = issue70.Where(e => e.Canonical != null && existingCanonical.Contains(e.Canonical)).Select(e => e.Canonical!).Take(5).ToArray();
        if (overlap.Length > 0) throw new InvalidDataException("Issue #70 canonical overlaps existing General/Special: " + string.Join(", ", overlap));
        entries.AddRange(issue70);
        return new(entries.ToArray(), hashes);''')

patch('src/DanbooruTagTool.App/App.xaml.cs',
'''                    Total = result.Entries.Length,
                    General = result.Entries.Count(x => !x.IsSpecial),
                    Special = result.Entries.Count(x => x.IsSpecial),''',
'''                    Total = result.Entries.Length,
                    General = result.Entries.Count(x => x.EffectiveCategory == "General"),
                    Special = result.Entries.Count(x => x.EffectiveCategory == "Special"),
                    Character = result.Entries.Count(x => x.EffectiveCategory == "Character"),
                    Copyright = result.Entries.Count(x => x.EffectiveCategory == "Copyright"),
                    Artist = result.Entries.Count(x => x.EffectiveCategory == "Artist"),''')

patch('src/DanbooruTagTool.App/ViewModels/MainViewModel.cs',
'''    public string Category => entry.IsSpecial ? "Special" : "General";''',
'''    public string Category => entry.EffectiveCategory;''')
patch('src/DanbooruTagTool.App/ViewModels/MainViewModel.cs',
'''        Navigation = [new("special", "◆ Special", specialBrowse == null
            ? catalog.Entries.Where(e => e.IsSpecial).SelectMany(e => e.Paths).GroupBy(p => p.GenreId)
                .Select(g => new NavigationNode("special:" + g.Key + ">", g.First().Genre, g.Where(p => p.SubgenreId.Length > 0).DistinctBy(p => p.Key)
                    .Select(p => new NavigationNode("special:" + p.Key, p.Subgenre, [])).ToArray())).ToArray()
            : BuildSpecialNavigation()), new("general", "General", this.general.IsPending ? [] : BuildNavigation(this.general.Paths, "general:"))];''',
'''        Navigation = [new("special", "◆ Special", specialBrowse == null
            ? catalog.Entries.Where(e => e.IsSpecial).SelectMany(e => e.Paths).GroupBy(p => p.GenreId)
                .Select(g => new NavigationNode("special:" + g.Key + ">", g.First().Genre, g.Where(p => p.SubgenreId.Length > 0).DistinctBy(p => p.Key)
                    .Select(p => new NavigationNode("special:" + p.Key, p.Subgenre, [])).ToArray())).ToArray()
            : BuildSpecialNavigation()),
            new("general", "General", this.general.IsPending ? [] : BuildNavigation(this.general.Paths, "general:")),
            new("character", "キャラクター", []), new("copyright", "作品", []), new("artist", "作者", [])];''')
patch('src/DanbooruTagTool.App/ViewModels/MainViewModel.cs',
'''            if (browse == "general") return "General";
            if (specialBrowse != null)''',
'''            if (browse == "general") return "General";
            if (browse == "character") return "キャラクター";
            if (browse == "copyright") return "作品";
            if (browse == "artist") return "作者";
            if (specialBrowse != null)''')
patch('src/DanbooruTagTool.App/ViewModels/MainViewModel.cs',
'''        else if (browse == "general" || browse.StartsWith("general:", StringComparison.Ordinal))
        {
            entries = general.Browse(browse == "general" ? "" : browse[8..]);
            entries = SortIndex == 1 ? entries.OrderBy(e => e.Label, StringComparer.Create(CultureInfo.GetCultureInfo("ja-JP"), false)) : entries.OrderByDescending(e => e.Usage);
        }
        else if (specialBrowse != null)''',
'''        else if (browse == "general" || browse.StartsWith("general:", StringComparison.Ordinal))
        {
            entries = general.Browse(browse == "general" ? "" : browse[8..]);
            entries = SortIndex == 1 ? entries.OrderBy(e => e.Label, StringComparer.Create(CultureInfo.GetCultureInfo("ja-JP"), false)) : entries.OrderByDescending(e => e.Usage);
        }
        else if (browse is "character" or "copyright" or "artist")
        {
            var category = browse switch { "character" => "Character", "copyright" => "Copyright", _ => "Artist" };
            entries = catalog.Entries.Where(e => e.EffectiveCategory == category && e.CanBrowse);
            entries = SortIndex == 1 ? entries.OrderBy(e => e.Label, StringComparer.Create(CultureInfo.GetCultureInfo("ja-JP"), false)) : entries.OrderByDescending(e => e.Usage);
        }
        else if (specialBrowse != null)''')
patch('src/DanbooruTagTool.App/ViewModels/MainViewModel.cs',
'''            else if (key == "special" || key.StartsWith("general", StringComparison.Ordinal))''',
'''            else if (key == "special" || key.StartsWith("general", StringComparison.Ordinal) || key is "character" or "copyright" or "artist")''')
patch('src/DanbooruTagTool.App/ViewModels/MainViewModel.cs',
'''    private IReadOnlyList<EntryViewModel> RelatedFor(CatalogEntry entry)
    {
        if (specialBrowse == null || !entry.IsSpecial)
            return Rows(catalog.Entries.Where(e => e.IsSpecial && e.CanBrowse && e.Id != entry.Id && e.Paths.Any(p => entry.Paths.Any(v => v.Key == p.Key))).OrderByDescending(e => e.Usage).Take(6));''',
'''    private IReadOnlyList<EntryViewModel> RelatedFor(CatalogEntry entry)
    {
        if (entry.EffectiveCategory == "Character")
        {
            var order = entry.RelatedCopyright.Select((canonical, index) => (canonical, index)).ToDictionary(x => x.canonical, x => x.index, StringComparer.Ordinal);
            return Rows(catalog.Entries.Where(e => e.EffectiveCategory == "Copyright" && e.Canonical != null && order.ContainsKey(e.Canonical))
                .OrderBy(e => order[e.Canonical!]));
        }
        if (entry.EffectiveCategory == "Copyright" && entry.Canonical is { } copyright)
            return Rows(catalog.Entries.Where(e => e.EffectiveCategory == "Character" && e.RelatedCopyright.Contains(copyright, StringComparer.Ordinal))
                .OrderByDescending(e => e.Usage).Take(6));
        if (specialBrowse == null || !entry.IsSpecial)
            return Rows(catalog.Entries.Where(e => e.IsSpecial && e.CanBrowse && e.Id != entry.Id && e.Paths.Any(p => entry.Paths.Any(v => v.Key == p.Key))).OrderByDescending(e => e.Usage).Take(6));''')

patch('src/DanbooruTagTool.Tests/ProductionTests.cs',
'''        Assert.Equal(30629,catalog.Entries.Count(e=>!e.IsSpecial)); Assert.Equal(AcceptedAssetImporter.ProductionSpecialCount,catalog.Entries.Count(e=>e.IsSpecial));''',
'''        Assert.Equal(30629,catalog.Entries.Count(e=>e.EffectiveCategory=="General")); Assert.Equal(AcceptedAssetImporter.ProductionSpecialCount,catalog.Entries.Count(e=>e.EffectiveCategory=="Special"));
        Assert.Equal(Issue70CatalogOverlayImporter.CharacterCount,catalog.Entries.Count(e=>e.EffectiveCategory=="Character"));
        Assert.Equal(Issue70CatalogOverlayImporter.CopyrightCount,catalog.Entries.Count(e=>e.EffectiveCategory=="Copyright"));
        Assert.Equal(Issue70CatalogOverlayImporter.ArtistCount,catalog.Entries.Count(e=>e.EffectiveCategory=="Artist"));''')

importer='''using System.Globalization;
using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

public static class Issue70CatalogOverlayImporter
{
    public const string RelativePath = "docs/issue70/data/runtime/issue70_catalog_overlay.csv";
    public const string ExpectedSha256 = "1d346ad75655ea6091f9bce9a4cf58b1cf6f8fac18c7eb441f8edd009ee81433";
    public const int TotalCount = 92739;
    public const int CharacterCount = 35890;
    public const int CopyrightCount = 8536;
    public const int ArtistCount = 48313;

    public static CatalogEntry[] Read(string path)
    {
        if (AcceptedAssetImporter.Hash(path) != ExpectedSha256) throw new InvalidDataException("Issue #70 runtime overlay hash mismatch");
        var rows = AcceptedAssetImporter.Csv(path);
        if (rows.Count != TotalCount) throw new InvalidDataException($"Issue #70 runtime overlay count drift: {rows.Count} != {TotalCount}");
        var required = new[] { "row_id", "canonical_tag", "category", "category_name", "post_count", "display_ja", "search_ja", "aliases", "related_copyright", "translation_status" };
        if (rows.Count == 0 || required.Any(field => !rows[0].ContainsKey(field))) throw new InvalidDataException("Issue #70 runtime overlay schema mismatch");
        var expectedCodes = new Dictionary<string, string>(StringComparer.Ordinal) { ["Character"] = "4", ["Copyright"] = "3", ["Artist"] = "1" };
        var categoryCounts = new Dictionary<string, int>(StringComparer.Ordinal);
        var canonicals = new HashSet<string>(StringComparer.Ordinal);
        var copyrightCanonicals = rows.Where(row => row["category_name"] == "Copyright").Select(row => row["canonical_tag"]).ToHashSet(StringComparer.Ordinal);
        var entries = new List<CatalogEntry>(rows.Count);
        for (var i = 0; i < rows.Count; i++)
        {
            var row = rows[i];
            var expectedRow = $"I70-{i + 1:000000}";
            if (row["row_id"] != expectedRow) throw new InvalidDataException("Issue #70 row order mismatch at " + expectedRow);
            var category = row["category_name"];
            if (!expectedCodes.TryGetValue(category, out var categoryCode) || row["category"] != categoryCode) throw new InvalidDataException("Issue #70 category mismatch at " + row["row_id"]);
            categoryCounts[category] = categoryCounts.GetValueOrDefault(category) + 1;
            var canonical = row["canonical_tag"];
            if (string.IsNullOrWhiteSpace(canonical) || !canonicals.Add(canonical)) throw new InvalidDataException("Issue #70 duplicate/empty canonical: " + canonical);
            if (string.IsNullOrWhiteSpace(row["display_ja"])) throw new InvalidDataException("Issue #70 empty display_ja at " + row["row_id"]);
            if (row["translation_status"] is not ("ACCEPTED_AI" or "REVIEW_REQUIRED")) throw new InvalidDataException("Issue #70 invalid status at " + row["row_id"]);
            if (!long.TryParse(row["post_count"], NumberStyles.Integer, CultureInfo.InvariantCulture, out var postCount) || postCount < 0) throw new InvalidDataException("Issue #70 invalid post_count at " + row["row_id"]);
            var related = SplitPipe(row["related_copyright"]);
            if (category != "Character" && related.Length > 0) throw new InvalidDataException("Issue #70 relation attached to non-Character at " + row["row_id"]);
            if (related.Any(value => !copyrightCanonicals.Contains(value))) throw new InvalidDataException("Issue #70 unknown Copyright relation at " + row["row_id"]);
            var prefix = category switch { "Character" => "C:", "Copyright" => "R:", _ => "A:" };
            entries.Add(new CatalogEntry(prefix + canonical, canonical, canonical, row["display_ja"], false, postCount,
                SplitPipe(row["aliases"]), SplitPipe(row["search_ja"]), [], Description: row["translation_status"] == "REVIEW_REQUIRED" ? "日本語表示は要確認" : "")
            {
                TagCategory = category,
                RelatedCopyright = related
            });
        }
        if (categoryCounts.GetValueOrDefault("Character") != CharacterCount || categoryCounts.GetValueOrDefault("Copyright") != CopyrightCount || categoryCounts.GetValueOrDefault("Artist") != ArtistCount)
            throw new InvalidDataException("Issue #70 runtime category coverage mismatch");
        return entries.ToArray();
    }

    private static string[] SplitPipe(string value) => value.Split('|', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
}
'''
(root/'src/DanbooruTagTool.Data/Issue70CatalogOverlayImporter.cs').write_text(importer,encoding='utf-8')

tests='''using DanbooruTagTool.App.ViewModels;
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
'''
(root/'src/DanbooruTagTool.Tests/Issue70IntegrationTests.cs').write_text(tests,encoding='utf-8')
