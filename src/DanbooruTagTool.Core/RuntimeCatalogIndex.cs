using System.Collections.ObjectModel;

namespace DanbooruTagTool.Core;

/// <summary>
/// The small runtime query boundary used by the WPF application.  Catalog.db
/// remains the source of truth; this object only freezes lookup and query
/// structures over the entries loaded at startup.
/// </summary>
public interface IRuntimeCatalogQuery : ICatalog
{
    CatalogEntry? FindById(string id);
    IReadOnlyList<CatalogEntry> BrowseCategory(string category, bool canBrowseOnly = true);
    IReadOnlyList<CatalogEntry> BrowseSpecialPath(string pathKey);
    IReadOnlyList<BrowsePath> BrowsePaths(bool special);
    IReadOnlyList<BrowsePath> SpecialNavigationPaths { get; }
    IReadOnlyList<SearchHit> Search(string query);
    IReadOnlyList<CatalogEntry> RelatedByCatalogMetadata(CatalogEntry entry);
}

/// <summary>
/// Immutable-at-runtime indexes built once from the catalog payload.
/// SearchDocument deliberately keeps only normalized search fields and the
/// entry reference; descriptions and other large payloads are not copied.
/// </summary>
public sealed class RuntimeCatalogIndex : IRuntimeCatalogQuery
{
    private readonly IReadOnlyDictionary<string, CatalogEntry> byId;
    private readonly IReadOnlyDictionary<string, CatalogEntry> canonical;
    private readonly IReadOnlyDictionary<string, IReadOnlyList<CatalogEntry>> specialEnglish;
    private readonly IReadOnlyDictionary<string, IReadOnlyList<CatalogEntry>> aliases;
    private readonly IReadOnlyDictionary<string, IReadOnlyList<CatalogEntry>> categories;
    private readonly IReadOnlyDictionary<string, IReadOnlyList<CatalogEntry>> browsableCategories;
    private readonly IReadOnlyDictionary<string, IReadOnlyList<CatalogEntry>> specialByPath;
    private readonly IReadOnlyDictionary<string, IReadOnlyList<CatalogEntry>> copyrightEntries;
    private readonly IReadOnlyDictionary<string, IReadOnlyList<CatalogEntry>> charactersByCopyright;
    private readonly IReadOnlyList<SearchDocument> searchDocuments;
    private readonly IReadOnlyList<BrowsePath> generalPaths;
    private readonly IReadOnlyList<BrowsePath> specialPaths;
    private readonly IReadOnlyList<BrowsePath> specialNavigationPaths;

    public static IRuntimeCatalogQuery Create(ICatalog catalog) =>
        catalog as IRuntimeCatalogQuery ?? new RuntimeCatalogIndex(catalog.Entries);

    public RuntimeCatalogIndex(IReadOnlyList<CatalogEntry> entries)
    {
        Entries = Freeze(entries);

        var id = new Dictionary<string, CatalogEntry>(StringComparer.Ordinal);
        var canonicalRows = new Dictionary<string, List<CatalogEntry>>(StringComparer.Ordinal);
        var englishRows = new Dictionary<string, List<CatalogEntry>>(StringComparer.Ordinal);
        var aliasRows = new Dictionary<string, List<CatalogEntry>>(StringComparer.Ordinal);
        var categoryRows = new Dictionary<string, List<CatalogEntry>>(StringComparer.Ordinal);
        var browsableCategoryRows = new Dictionary<string, List<CatalogEntry>>(StringComparer.Ordinal);
        var specialPathRows = new Dictionary<string, List<CatalogEntry>>(StringComparer.Ordinal);
        var copyrightRows = new Dictionary<string, List<CatalogEntry>>(StringComparer.Ordinal);
        var charactersByCopyrightRows = new Dictionary<string, List<CatalogEntry>>(StringComparer.Ordinal);
        var documents = new List<SearchDocument>(Entries.Count);

        foreach (var entry in Entries)
        {
            if (!id.ContainsKey(entry.Id)) id.Add(entry.Id, entry);
            Add(categoryRows, entry.EffectiveCategory, entry);
            if (entry.CanBrowse) Add(browsableCategoryRows, entry.EffectiveCategory, entry);

            string? normalizedCanonical = null;
            string[] normalizedAliases = [];
            if (entry.Canonical is { } canonicalValue)
            {
                normalizedCanonical = SearchEngine.Normalize(canonicalValue);
                Add(canonicalRows, normalizedCanonical, entry);
                if (entry.EffectiveCategory == "Copyright") Add(copyrightRows, canonicalValue, entry);
                normalizedAliases = entry.Aliases.Select(SearchEngine.Normalize).ToArray();
            }

            var normalizedEnglish = entry.IsSpecial || entry.CanSearch ? SearchEngine.Normalize(entry.English) : "";
            if (entry.IsSpecial) Add(englishRows, normalizedEnglish, entry);
            if (entry.Canonical is not null)
            {
                foreach (var alias in normalizedAliases)
                    Add(aliasRows, alias, entry);
            }

            if (entry.IsSpecial && entry.CanBrowse)
            {
                var seenPathKeys = new HashSet<string>(StringComparer.Ordinal);
                foreach (var path in entry.Paths)
                {
                    if (seenPathKeys.Add(path.Key)) Add(specialPathRows, path.Key, entry);
                    var genreKey = path.GenreId + ">";
                    if (seenPathKeys.Add(genreKey)) Add(specialPathRows, genreKey, entry);
                }
            }

            if (entry.EffectiveCategory == "Character")
                foreach (var copyright in entry.RelatedCopyright)
                    Add(charactersByCopyrightRows, copyright, entry);

            if (entry.CanSearch)
            {
                documents.Add(SearchDocument.Create(entry, normalizedCanonical, normalizedEnglish, normalizedAliases));
            }
        }

        byId = FreezeDictionary(id);
        canonical = FreezeDictionary(canonicalRows.ToDictionary(pair => pair.Key, pair => Preferred(pair.Value), StringComparer.Ordinal));
        specialEnglish = FreezeLists(englishRows);
        aliases = FreezeLists(aliasRows);
        categories = FreezeLists(categoryRows);
        browsableCategories = FreezeLists(browsableCategoryRows);
        specialByPath = FreezeLists(specialPathRows);
        copyrightEntries = FreezeLists(copyrightRows);
        charactersByCopyright = FreezeLists(charactersByCopyrightRows);
        searchDocuments = Freeze(documents);
        generalPaths = FreezePaths(false);
        specialPaths = FreezePaths(true);
        specialNavigationPaths = Freeze(Entries.Where(entry => entry.IsSpecial).SelectMany(entry => entry.Paths).Distinct().ToArray());
    }

    public IReadOnlyList<CatalogEntry> Entries { get; }

    public CatalogEntry? FindById(string id) => byId.GetValueOrDefault(id);

    public CatalogEntry? Resolve(string surface)
    {
        var key = SearchEngine.Normalize(surface);
        var exact = new List<CatalogEntry>();
        if (specialEnglish.TryGetValue(key, out var english)) exact.AddRange(english);
        if (canonical.TryGetValue(key, out var canonicalEntry)) exact.Add(canonicalEntry);
        if (exact.Count > 0) return Unique(exact);
        return aliases.TryGetValue(key, out var aliasHits) ? Unique(aliasHits) : null;
    }

    public IReadOnlyList<CatalogEntry> BrowseCategory(string category, bool canBrowseOnly = true)
        => (canBrowseOnly ? browsableCategories : categories).GetValueOrDefault(category) ?? [];

    public IReadOnlyList<CatalogEntry> BrowseSpecialPath(string pathKey)
        => specialByPath.GetValueOrDefault(pathKey) ?? [];

    public IReadOnlyList<BrowsePath> BrowsePaths(bool special) => special ? specialPaths : generalPaths;

    public IReadOnlyList<BrowsePath> SpecialNavigationPaths => specialNavigationPaths;

    public IReadOnlyList<SearchHit> Search(string query)
    {
        var normalizedQuery = SearchEngine.Normalize(query);
        if (normalizedQuery.Length == 0) return [];

        var hits = new List<SearchHit>();
        foreach (var document in searchDocuments)
        {
            var rank = Rank(document, normalizedQuery);
            if (rank < 100) hits.Add(new SearchHit(document.Entry, rank) { PrefixWords = document.Prefixes });
        }

        // Strong whole-word intent suppresses embedded prefix/substring and
        // fuzzy collisions. This is the existing SearchEngine contract.
        if (hits.Any(hit => hit.Rank <= 3)) hits = hits.Where(hit => hit.Rank <= 3).ToList();

        return hits
            .GroupBy(hit => hit.Entry.Canonical ?? hit.Entry.Id, StringComparer.Ordinal)
            .Select(group => group.OrderBy(hit => hit.Rank)
                .ThenByDescending(hit => hit.Entry.IsSpecial)
                .ThenByDescending(hit => hit.Entry.Usage)
                .First())
            .OrderBy(hit => hit.Rank)
            .ThenBy(hit => PrefixDistance(hit.PrefixWords, normalizedQuery))
            .ThenByDescending(hit => hit.Entry.Usage)
            .ThenBy(hit => hit.Entry.English, StringComparer.Ordinal)
            .ToArray();
    }

    public IReadOnlyList<CatalogEntry> RelatedByCatalogMetadata(CatalogEntry entry)
    {
        if (entry.EffectiveCategory == "Character")
        {
            var result = new List<CatalogEntry>();
            foreach (var canonicalValue in entry.RelatedCopyright)
                if (copyrightEntries.TryGetValue(canonicalValue, out var matches)) result.AddRange(matches);
            return result;
        }

        if (entry.EffectiveCategory == "Copyright" && entry.Canonical is not null)
            return charactersByCopyright.GetValueOrDefault(entry.Canonical)?.OrderByDescending(candidate => candidate.Usage).Take(6).ToArray() ?? [];

        if (!entry.IsSpecial) return [];
        var resultById = new Dictionary<string, CatalogEntry>(StringComparer.Ordinal);
        foreach (var path in entry.Paths)
        {
            if (!specialByPath.TryGetValue(path.Key, out var candidates)) continue;
            foreach (var candidate in candidates)
                if (candidate.Id != entry.Id) resultById.TryAdd(candidate.Id, candidate);
        }
        return resultById.Values.OrderByDescending(candidate => candidate.Usage).Take(6).ToArray();
    }

    private IReadOnlyList<BrowsePath> FreezePaths(bool special)
    {
        var seenGenres = new HashSet<string>(StringComparer.Ordinal);
        var result = new List<BrowsePath>();
        foreach (var entry in Entries)
        {
            if (entry.IsSpecial != special) continue;
            foreach (var path in entry.Paths)
            {
                if (seenGenres.Add(path.GenreId)) result.Add(path);
                if (special) break;
            }
        }
        return Freeze(result);
    }

    private static IReadOnlyList<T> Freeze<T>(IEnumerable<T> values) =>
        new ReadOnlyCollection<T>(values.ToArray());

    private static IReadOnlyDictionary<string, T> FreezeDictionary<T>(Dictionary<string, T> values) =>
        new ReadOnlyDictionary<string, T>(values);

    private static IReadOnlyDictionary<string, IReadOnlyList<CatalogEntry>> FreezeLists(
        Dictionary<string, List<CatalogEntry>> values) =>
        new ReadOnlyDictionary<string, IReadOnlyList<CatalogEntry>>(
            values.ToDictionary(pair => pair.Key, pair => Freeze(pair.Value), StringComparer.Ordinal));

    private static void Add(Dictionary<string, List<CatalogEntry>> index, string key, CatalogEntry entry)
    {
        if (!index.TryGetValue(key, out var rows)) index[key] = rows = [];
        rows.Add(entry);
    }

    private static CatalogEntry Preferred(IEnumerable<CatalogEntry> rows) => rows
        .OrderByDescending(entry => entry.IsSpecial && (!string.IsNullOrWhiteSpace(entry.Japanese) || entry.Paths.Length > 0 || entry.Description.Length > 0 || entry.ProductFit.Length > 0))
        .ThenBy(entry => entry.Id, StringComparer.Ordinal).First();

    private static CatalogEntry? Unique(IEnumerable<CatalogEntry> rows)
    {
        var hits = rows.ToArray();
        return hits.Select(entry => entry.Canonical is { } canonical ? "C:" + canonical : "S:" + entry.Id)
            .Distinct(StringComparer.Ordinal).Count() == 1 ? Preferred(hits) : null;
    }

    private static int PrefixDistance(IReadOnlyList<string> words, string query)
    {
        return words.Where(word => word.StartsWith(query, StringComparison.Ordinal))
            .Select(word => word.Length - query.Length).DefaultIfEmpty(1000).Min();
    }

    private static int Rank(SearchDocument document, string query)
    {
        if (document.EnglishTerms.Contains(query)) return 0;
        if (document.JapaneseTerms.Contains(query)) return 1;
        if (document.EnglishTerms.Any(term => (" " + term + " ").Contains(" " + query + " ", StringComparison.Ordinal))) return 2;
        var parts = query.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length > 1 && parts.All(part => document.EnglishTerms.Any(term => term.Split(' ').Contains(part)) || document.JapaneseTerms.Any(term => term.Contains(part, StringComparison.Ordinal)))) return 3;
        if (HasJapanese(query) && document.JapaneseTerms.Any(term => term.Contains(query, StringComparison.Ordinal))) return 3;
        if (document.EnglishTerms.Any(term => term.Split(' ').Any(word => word.StartsWith(query, StringComparison.Ordinal)))) return 4;
        if (query.Length >= 3 && document.EnglishTerms.Any(term => term.Contains(query, StringComparison.Ordinal))) return 5;
        if (query.Length >= 4 && document.EnglishTerms.Any(term => DistanceOne(term, query))) return 6;
        return 100;
    }

    private static bool HasJapanese(string value) => value.Any(c => c is >= '\u3040' and <= '\u30ff' or >= '\u3400' and <= '\u9fff');

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

    private sealed class SearchDocument
    {
        private SearchDocument(CatalogEntry entry, IReadOnlyList<string> englishTerms,
            IReadOnlyList<string> japaneseTerms, IReadOnlyList<string> prefixWords)
        {
            Entry = entry; EnglishTerms = englishTerms; JapaneseTerms = japaneseTerms; Prefixes = prefixWords;
        }

        public CatalogEntry Entry { get; }
        public IReadOnlyList<string> EnglishTerms { get; }
        public IReadOnlyList<string> JapaneseTerms { get; }
        public IReadOnlyList<string> Prefixes { get; }

        public static SearchDocument Create(CatalogEntry entry, string? normalizedCanonical,
            string normalizedEnglish, IReadOnlyList<string> normalizedAliases)
        {
            var englishSearch = entry.JapaneseSearch.Where(term => !HasJapanese(term)).Select(SearchEngine.Normalize);
            var japaneseSearch = entry.JapaneseSearch.Where(HasJapanese).Select(SearchEngine.Normalize);
            var baseTerms = new[] { normalizedCanonical ?? "", normalizedEnglish }.Concat(normalizedAliases).ToArray();
            var englishTerms = baseTerms.Concat(englishSearch).Where(value => value.Length > 0).ToArray();
            var japaneseTerms = new[] { SearchEngine.Normalize(entry.Japanese ?? "") }.Concat(japaneseSearch)
                .Where(value => value.Length > 0).ToArray();
            var prefixWords = baseTerms.Where(value => value.Length > 0)
                .SelectMany(value => value.Split(' ', StringSplitOptions.RemoveEmptyEntries)).ToArray();
            return new(entry, englishTerms, japaneseTerms, prefixWords);
        }
    }
}
