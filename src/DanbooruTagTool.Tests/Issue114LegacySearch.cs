using DanbooruTagTool.Core;

namespace DanbooruTagTool.Tests;

/// <summary>
/// Frozen test-local copy of the pre-#114 SearchEngine algorithm. It must not
/// call Catalog.Search or SearchEngine so equivalence remains independent.
/// </summary>
internal static class Issue114LegacySearch
{
    public static IReadOnlyList<SearchHit> Search(IReadOnlyList<CatalogEntry> entries, string query)
    {
        var q = SearchEngine.Normalize(query);
        if (q.Length == 0) return [];
        var hits = entries.Where(entry => entry.CanSearch).Select(entry => new SearchHit(entry, Rank(entry, q)))
            .Where(hit => hit.Rank < 100).ToArray();
        if (hits.Any(hit => hit.Rank <= 3)) hits = hits.Where(hit => hit.Rank <= 3).ToArray();
        hits = hits.GroupBy(hit => hit.Entry.Canonical ?? hit.Entry.Id, StringComparer.Ordinal)
            .Select(group => group.OrderBy(hit => hit.Rank)
                .ThenByDescending(hit => hit.Entry.IsSpecial)
                .ThenByDescending(hit => hit.Entry.Usage).First()).ToArray();
        return hits.OrderBy(hit => hit.Rank)
            .ThenBy(hit => PrefixDistance(hit.Entry, q))
            .ThenByDescending(hit => hit.Entry.Usage)
            .ThenBy(hit => hit.Entry.English, StringComparer.Ordinal).ToArray();
    }

    private static int PrefixDistance(CatalogEntry entry, string query)
    {
        var words = new[] { entry.Canonical ?? "", entry.English }.Concat(entry.Aliases)
            .SelectMany(value => SearchEngine.Normalize(value).Split(' ', StringSplitOptions.RemoveEmptyEntries));
        return words.Where(word => word.StartsWith(query, StringComparison.Ordinal))
            .Select(word => word.Length - query.Length).DefaultIfEmpty(1000).Min();
    }

    private static int Rank(CatalogEntry entry, string query)
    {
        var english = new[] { entry.Canonical ?? "", entry.English }.Concat(entry.Aliases).Concat(entry.JapaneseSearch.Where(term => !HasJapanese(term)))
            .Select(SearchEngine.Normalize).Where(term => term.Length > 0).ToArray();
        var japanese = new[] { entry.Japanese ?? "" }.Concat(entry.JapaneseSearch.Where(HasJapanese))
            .Select(SearchEngine.Normalize).Where(term => term.Length > 0).ToArray();
        if (english.Contains(query)) return 0;
        if (japanese.Contains(query)) return 1;
        if (english.Any(term => (" " + term + " ").Contains(" " + query + " ", StringComparison.Ordinal))) return 2;
        var parts = query.Split(' ', StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length > 1 && parts.All(part => english.Any(term => term.Split(' ').Contains(part)) || japanese.Any(term => term.Contains(part, StringComparison.Ordinal)))) return 3;
        if (HasJapanese(query) && japanese.Any(term => term.Contains(query, StringComparison.Ordinal))) return 3;
        if (english.Any(term => term.Split(' ').Any(word => word.StartsWith(query, StringComparison.Ordinal)))) return 4;
        if (query.Length >= 3 && english.Any(term => term.Contains(query, StringComparison.Ordinal))) return 5;
        if (query.Length >= 4 && DistanceOne(english, query)) return 6;
        return 100;
    }

    private static bool HasJapanese(string value) => value.Any(c => c is >= '\u3040' and <= '\u30ff' or >= '\u3400' and <= '\u9fff');

    private static bool DistanceOne(IEnumerable<string> terms, string query) => terms.Any(term => DistanceOne(term, query));

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
