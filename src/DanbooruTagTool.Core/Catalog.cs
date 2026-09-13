using System.Text;
using System.Text.RegularExpressions;

namespace DanbooruTagTool.Core;

public sealed record BrowsePath(string GenreId, string Genre, string SubgenreId = "", string Subgenre = "")
{
    public string Key => GenreId + ">" + SubgenreId;
    public string Label => Subgenre.Length == 0 ? Genre : Genre + " > " + Subgenre;
}

public sealed record CatalogEntry(string Id, string? Canonical, string English, string? Japanese,
    bool IsSpecial, long? Usage, string[] Aliases, string[] JapaneseSearch, BrowsePath[] Paths,
    string ProductFit = "KEEP", string Description = "")
{
    public string Label => Japanese ?? English;
    public string UsageText => Usage?.ToString("N0", System.Globalization.CultureInfo.InvariantCulture) ?? "—";
    public bool CanBrowse => ProductFit == "KEEP";
    public bool CanSearch => ProductFit != "OUT_OF_SCOPE_PRODUCT";
    public bool CanAdd => Canonical is not null && CanSearch;
    public string Breadcrumb => string.Join(" / ", Paths.Select(p => p.Label));
}

public interface ICatalog { IReadOnlyList<CatalogEntry> Entries { get; } CatalogEntry? Resolve(string surface); }
public sealed class Catalog(IReadOnlyList<CatalogEntry> entries) : ICatalog
{
    public IReadOnlyList<CatalogEntry> Entries { get; } = entries;
    private readonly Dictionary<string, CatalogEntry> canonical = entries.Where(e => e.Canonical != null)
        .GroupBy(e => SearchEngine.Normalize(e.Canonical!)).ToDictionary(g => g.Key, g => Preferred(g));
    private static CatalogEntry Preferred(IEnumerable<CatalogEntry> rows) => rows
        .OrderByDescending(e => e.IsSpecial && (!string.IsNullOrWhiteSpace(e.Japanese) || e.Paths.Length > 0 || e.Description.Length > 0 || e.ProductFit.Length > 0))
        .ThenBy(e => e.Id, StringComparer.Ordinal).First();
    public CatalogEntry? Resolve(string surface)
    {
        var key = SearchEngine.Normalize(surface);
        var exact = Entries.Where(e => e.IsSpecial && SearchEngine.Normalize(e.English) == key).ToList();
        if (canonical.TryGetValue(key, out var entry)) exact.Add(entry);
        if (exact.Count > 0) return Unique(exact);
        return Unique(Entries.Where(e => e.Canonical != null && e.Aliases.Any(a => SearchEngine.Normalize(a) == key)));
    }
    private static CatalogEntry? Unique(IEnumerable<CatalogEntry> rows)
    {
        var hits = rows.ToArray();
        // Semantic-only Special identities stay distinct; never manufacture a canonical.
        return hits.Select(e => e.Canonical is {} c ? "C:" + c : "S:" + e.Id).Distinct().Count() == 1 ? Preferred(hits) : null;
    }
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

public sealed record SearchHit(CatalogEntry Entry, int Rank);
public sealed class SearchEngine(ICatalog catalog)
{
    public static string Normalize(string text) => Regex.Replace(text.Normalize(NormalizationForm.FormKC)
        .ToLowerInvariant().Replace('_', ' ').Trim(), @"\s+", " ");

    public IReadOnlyList<SearchHit> Search(string query)
    {
        var q = Normalize(query);
        if (q.Length == 0) return [];
        var hits = catalog.Entries.Where(e => e.CanSearch).Select(e => new SearchHit(e, Rank(e, q)))
            .Where(h => h.Rank < 100).ToArray();
        // Strong whole-word intent suppresses embedded prefix/substring and fuzzy collisions.
        if (hits.Any(h => h.Rank <= 3)) hits = hits.Where(h => h.Rank <= 3).ToArray();
        // A canonical identity is one discovery result even when the General
        // overlay and Special dictionary both expose it. Prefer the richer
        // Special row for inspection, while keeping relevance as the primary
        // order.
        hits = hits.GroupBy(h => h.Entry.Canonical ?? h.Entry.Id, StringComparer.Ordinal)
            .Select(group => group.OrderBy(h => h.Rank)
                .ThenByDescending(h => h.Entry.IsSpecial)
                .ThenByDescending(h => h.Entry.Usage).First()).ToArray();
        return hits.OrderBy(h => h.Rank)
            .ThenBy(h => PrefixDistance(h.Entry, q))
            .ThenByDescending(h => h.Entry.Usage)
            .ThenBy(h => h.Entry.English, StringComparer.Ordinal).ToArray();
    }
    private static int PrefixDistance(CatalogEntry entry, string query)
    {
        var words = new[] { entry.Canonical ?? "", entry.English }.Concat(entry.Aliases)
            .SelectMany(value => Normalize(value).Split(' ', StringSplitOptions.RemoveEmptyEntries));
        var length = words.Where(word => word.StartsWith(query, StringComparison.Ordinal))
            .Select(word => word.Length - query.Length).DefaultIfEmpty(1000).Min();
        return length;
    }
    private static int Rank(CatalogEntry e, string q)
    {
        static bool HasJapanese(string s) => s.Any(c => c is >= '\u3040' and <= '\u30ff' or >= '\u3400' and <= '\u9fff');
        var en = new[] { e.Canonical ?? "", e.English }.Concat(e.Aliases).Concat(e.JapaneseSearch.Where(t => !HasJapanese(t)))
            .Select(Normalize).Where(t => t.Length > 0).ToArray();
        var ja = new[] { e.Japanese ?? "" }.Concat(e.JapaneseSearch.Where(HasJapanese)).Select(Normalize).Where(t => t.Length > 0).ToArray();
        if (en.Contains(q)) return 0;
        if (ja.Contains(q)) return 1;
        if (en.Any(t => (" " + t + " ").Contains(" " + q + " ", StringComparison.Ordinal))) return 2;
        var parts = q.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length > 1 && parts.All(p => en.Any(t => t.Split(' ').Contains(p)) || ja.Any(t => t.Contains(p, StringComparison.Ordinal)))) return 3;
        if (HasJapanese(q) && ja.Any(t => t.Contains(q, StringComparison.Ordinal))) return 3;
        if (en.Any(t => t.Split(' ').Any(w => w.StartsWith(q, StringComparison.Ordinal)))) return 4;
        if (q.Length >= 3 && en.Any(t => t.Contains(q, StringComparison.Ordinal))) return 5;
        if (q.Length >= 4 && en.Any(t => DistanceOne(t, q))) return 6;
        return 100;
    }
    private static bool DistanceOne(string a, string b)
    {
        if (Math.Abs(a.Length - b.Length) > 1) return false;
        int i = 0, j = 0, errors = 0;
        while (i < a.Length && j < b.Length)
        {
            if (a[i] == b[j]) { i++; j++; continue; }
            if (++errors > 1) return false;
            if (a.Length >= b.Length) i++;
            if (b.Length >= a.Length) j++;
        }
        return errors + a.Length - i + b.Length - j <= 1;
    }
}
