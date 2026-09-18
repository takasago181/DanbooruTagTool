using System.Text;
using System.Text.RegularExpressions;

namespace DanbooruTagTool.Core;

public sealed record BrowsePath(string GenreId, string Genre, string SubgenreId = "", string Subgenre = "")
{
    public string Key => GenreId + ">" + SubgenreId;
    public string Label => Subgenre.Length == 0 ? Genre : Genre + " > " + Subgenre;
}

public enum BrowseClassificationStatus { NotApplicable, Proposed, Unresolved }
public enum SexualIntentClass { NonSexual, Contextual, Sexual }
public enum SexualIntentClassificationStatus { Unclassified, AutoHighConfidence, HumanReviewed }

public sealed record SpecialBrowseV2Classification(
    string? KindId,
    string[] BodySiteIds,
    string[] ThemeIds,
    SpecialBrowseV2Status Status);

public sealed record CatalogEntry(string Id, string? Canonical, string English, string? Japanese,
    bool IsSpecial, long? Usage, string[] Aliases, string[] JapaneseSearch, BrowsePath[] Paths,
    string ProductFit = "KEEP", string Description = "",
    BrowseClassificationStatus BrowseClassification = BrowseClassificationStatus.NotApplicable,
    SpecialBrowseV2Classification? SpecialBrowseV2 = null)
{
    // General/Special keep their historical shape; Issue #70 adds the three Danbooru identity categories.
    // EffectiveCategory preserves backward compatibility with older catalog.db JSON that has no TagCategory field.
    public string TagCategory { get; init; } = "";
    public string EffectiveCategory => string.IsNullOrWhiteSpace(TagCategory) ? (IsSpecial ? "Special" : "General") : TagCategory;
    public string[] RelatedCopyright { get; init; } = [];
    public string[] UnifiedBrowseRouteIds { get; init; } = [];
    public SexualIntentClass? SexualIntent { get; init; }
    public SexualIntentClassificationStatus SexualIntentStatus { get; init; } = SexualIntentClassificationStatus.Unclassified;
    public string SexualIntentSource { get; init; } = "";
    public string SexualIntentEvidence { get; init; } = "";
    public string Label => Japanese ?? English;
    public string UsageText => Usage?.ToString("N0", System.Globalization.CultureInfo.InvariantCulture) ?? "—";
    public bool CanBrowse => ProductFit == "KEEP";
    public bool CanSearch => ProductFit != "OUT_OF_SCOPE_PRODUCT";
    public bool CanAdd => Canonical is not null && CanSearch;
    public string Breadcrumb => string.Join(" / ", Paths.Select(p => p.Label));
}

public interface ICatalog { IReadOnlyList<CatalogEntry> Entries { get; } CatalogEntry? Resolve(string surface); }
public sealed class Catalog(IReadOnlyList<CatalogEntry> entries) : IRuntimeCatalogQuery
{
    private readonly RuntimeCatalogIndex index = new(entries);
    public IReadOnlyList<CatalogEntry> Entries => index.Entries;
    public CatalogEntry? Resolve(string surface) => index.Resolve(surface);
    public CatalogEntry? FindById(string id) => index.FindById(id);
    public IReadOnlyList<CatalogEntry> BrowseCategory(string category, bool canBrowseOnly = true) => index.BrowseCategory(category, canBrowseOnly);
    public IReadOnlyList<CatalogEntry> BrowseSpecialPath(string pathKey) => index.BrowseSpecialPath(pathKey);
    public IReadOnlyList<BrowsePath> BrowsePaths(bool special) => index.BrowsePaths(special);
    public IReadOnlyList<BrowsePath> SpecialNavigationPaths => index.SpecialNavigationPaths;
    public IReadOnlyList<SearchHit> Search(string query) => index.Search(query);
    public IReadOnlyList<CatalogEntry> RelatedByCatalogMetadata(CatalogEntry entry) => index.RelatedByCatalogMetadata(entry);
}

public interface IGeneralBrowseProvider
{
    bool IsPending { get; }
    string Status { get; }
    IReadOnlyList<BrowsePath> Paths { get; }
    IReadOnlyList<CatalogEntry> Browse(string path);
}
public sealed class PendingGeneralBrowseProvider : IGeneralBrowseProvider
{
    public bool IsPending => true;
    public string Status => "General分類は準備中です。日本語・English検索は利用できます。";
    public IReadOnlyList<BrowsePath> Paths => [];
    public IReadOnlyList<CatalogEntry> Browse(string path) => [];
}

public sealed record SearchHit(CatalogEntry Entry, int Rank)
{
    // Kept internal so the runtime index can carry precomputed prefix data to
    // the final ordering step without another entry-id index.
    internal IReadOnlyList<string> PrefixWords { get; init; } = [];
}
public sealed class SearchEngine
{
    private readonly Func<string, IReadOnlyList<SearchHit>> search;
    public SearchEngine(ICatalog catalog)
    {
        search = catalog is IRuntimeCatalogQuery indexed
            ? indexed.Search
            : RuntimeCatalogIndex.Create(catalog).Search;
    }
    public static string Normalize(string text) => Regex.Replace(text.Normalize(NormalizationForm.FormKC)
        .ToLowerInvariant().Replace('_', ' ').Trim(), @"\s+", " ");

    public IReadOnlyList<SearchHit> Search(string query) => search(query);
}
