namespace DanbooruTagTool.Core;

/// <summary>
/// Issue #76 isolated prototype model for Special v2 faceted browsing.
/// This type is intentionally not wired into production navigation yet.
/// </summary>
public enum SpecialBrowseV2Status
{
    AutoCandidate,
    HumanResolved,
    ReferenceOnlyNoDirectBrowse,
    DeferProductFitReview,
    OutOfScopeNoBrowse
}

public sealed record SpecialBrowseV2Entry(
    string CatalogId,
    string? KindId,
    IReadOnlySet<string> BodySiteIds,
    IReadOnlySet<string> ThemeIds,
    SpecialBrowseV2Status Status)
{
    public bool CanBrowse => Status is SpecialBrowseV2Status.AutoCandidate or SpecialBrowseV2Status.HumanResolved;
}

public sealed record SpecialBrowseV2Filter(
    string? KindId,
    IReadOnlySet<string> BodySiteIds,
    IReadOnlySet<string> ThemeIds)
{
    public static SpecialBrowseV2Filter Empty { get; } = new(
        null,
        new HashSet<string>(StringComparer.Ordinal),
        new HashSet<string>(StringComparer.Ordinal));

    public bool IsEmpty => KindId is null && BodySiteIds.Count == 0 && ThemeIds.Count == 0;

    public SpecialBrowseV2Filter WithKind(string? kindId) => this with { KindId = kindId };

    public SpecialBrowseV2Filter ToggleBodySite(string bodySiteId)
    {
        var next = BodySiteIds.ToHashSet(StringComparer.Ordinal);
        if (!next.Add(bodySiteId)) next.Remove(bodySiteId);
        return this with { BodySiteIds = next };
    }

    public SpecialBrowseV2Filter ToggleTheme(string themeId)
    {
        var next = ThemeIds.ToHashSet(StringComparer.Ordinal);
        if (!next.Add(themeId)) next.Remove(themeId);
        return this with { ThemeIds = next };
    }

    public SpecialBrowseV2Filter Clear() => Empty;
}

public sealed class SpecialBrowseV2Index
{
    private readonly Dictionary<string, SpecialBrowseV2Entry> byCatalogId;

    public SpecialBrowseV2Index(IEnumerable<SpecialBrowseV2Entry> entries)
    {
        byCatalogId = entries.ToDictionary(e => e.CatalogId, StringComparer.Ordinal);
    }

    public bool Matches(string catalogId, SpecialBrowseV2Filter filter)
    {
        if (!byCatalogId.TryGetValue(catalogId, out var entry) || !entry.CanBrowse) return false;
        if (filter.KindId is not null && !string.Equals(entry.KindId, filter.KindId, StringComparison.Ordinal)) return false;
        if (!filter.BodySiteIds.All(entry.BodySiteIds.Contains)) return false;
        if (!filter.ThemeIds.All(entry.ThemeIds.Contains)) return false;
        return true;
    }

    /// <summary>
    /// Intersects an already ordered result sequence with the active facets.
    /// Input order is preserved so existing SearchEngine relevance is untouched.
    /// </summary>
    public IReadOnlyList<CatalogEntry> IntersectInInputOrder(
        IEnumerable<CatalogEntry> entries,
        SpecialBrowseV2Filter filter)
        => entries.Where(entry => entry.IsSpecial && Matches(entry.Id, filter)).ToArray();

    public IReadOnlyList<string> FilterIdsInInputOrder(
        IEnumerable<string> catalogIds,
        SpecialBrowseV2Filter filter)
        => catalogIds.Where(id => Matches(id, filter)).ToArray();

    public int Count(SpecialBrowseV2Filter filter)
        => byCatalogId.Values.Count(entry => entry.CanBrowse && Matches(entry.CatalogId, filter));

    public int CountWithKind(SpecialBrowseV2Filter current, string kindId)
        => Count(current.WithKind(kindId));

    public int CountWithBodySite(SpecialBrowseV2Filter current, string bodySiteId)
    {
        var next = current.BodySiteIds.Contains(bodySiteId) ? current : current.ToggleBodySite(bodySiteId);
        return Count(next);
    }

    public int CountWithTheme(SpecialBrowseV2Filter current, string themeId)
    {
        var next = current.ThemeIds.Contains(themeId) ? current : current.ToggleTheme(themeId);
        return Count(next);
    }
}
