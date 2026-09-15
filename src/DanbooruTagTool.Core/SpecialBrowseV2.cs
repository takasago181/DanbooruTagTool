namespace DanbooruTagTool.Core;

public enum SpecialBrowseV2Status
{
    AutoCandidate,
    HumanResolved,
    ReferenceOnlyNoDirectBrowse,
    DeferProductFitReview,
    OutOfScopeNoBrowse
}

public enum SpecialBrowseV2Axis { Kind, BodySite, Theme }

public sealed record SpecialBrowseV2FacetDefinition(string Id, string Label);

public static class SpecialBrowseV2Taxonomy
{
    public static readonly SpecialBrowseV2FacetDefinition[] Kinds =
    [
        new("ACTION_CONTACT", "行為・接触"),
        new("CLOTHING_EXPOSURE", "衣服・露出"),
        new("TOOL_OBJECT", "道具・物"),
        new("BODY_STATE", "身体・状態"),
        new("FLUID_EXCRETION", "体液・排泄"),
        new("POSE_SCENE", "ポーズ・構図・場面"),
        new("PERSON_RELATION", "人物・関係"),
        new("NONHUMAN_TRANSFORMATION", "異形・変形"),
        new("META_EXPRESSION", "表現・メタ")
    ];

    public static readonly SpecialBrowseV2FacetDefinition[] BodySites =
    [
        new("MALE_GENITAL", "男性器"),
        new("BREAST_NIPPLE", "乳房・乳首"),
        new("FEMALE_GENITAL", "女性器"),
        new("MOUTH_ORAL", "口・口内"),
        new("BUTTOCK_ANAL", "尻・肛門"),
        new("URETHRA", "尿道")
    ];

    public static readonly SpecialBrowseV2FacetDefinition[] Themes =
    [
        new("BDSM_RESTRAINT", "拘束・BDSM"),
        new("INJURY_R18G", "損傷・R18G"),
        new("REPRO_PREGNANCY_LACTATION", "生殖・妊娠・授乳")
    ];

    public static string Label(SpecialBrowseV2Axis axis, string id)
    {
        var source = axis switch
        {
            SpecialBrowseV2Axis.Kind => Kinds,
            SpecialBrowseV2Axis.BodySite => BodySites,
            SpecialBrowseV2Axis.Theme => Themes,
            _ => []
        };
        return source.FirstOrDefault(item => item.Id == id)?.Label ?? id;
    }
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

    public IReadOnlyCollection<SpecialBrowseV2Entry> Entries => byCatalogId.Values;

    public SpecialBrowseV2Entry? Get(string catalogId)
        => byCatalogId.GetValueOrDefault(catalogId);

    public bool Matches(string catalogId, SpecialBrowseV2Filter filter)
    {
        if (!byCatalogId.TryGetValue(catalogId, out var entry) || !entry.CanBrowse) return false;
        if (filter.KindId is not null && !string.Equals(entry.KindId, filter.KindId, StringComparison.Ordinal)) return false;
        if (!filter.BodySiteIds.All(entry.BodySiteIds.Contains)) return false;
        if (!filter.ThemeIds.All(entry.ThemeIds.Contains)) return false;
        return true;
    }

    /// <summary>
    /// Intersects an already ordered result sequence with active facets and keeps
    /// the first row for each canonical identity. Input order is preserved so the
    /// existing SearchEngine relevance order is not changed.
    /// </summary>
    public IReadOnlyList<CatalogEntry> IntersectInInputOrder(
        IEnumerable<CatalogEntry> entries,
        SpecialBrowseV2Filter filter)
    {
        var result = new List<CatalogEntry>();
        var seen = new HashSet<string>(StringComparer.Ordinal);
        foreach (var entry in entries)
        {
            if (!entry.IsSpecial || !Matches(entry.Id, filter)) continue;
            var identity = entry.Canonical is { } canonical ? "C:" + canonical : "S:" + entry.Id;
            if (seen.Add(identity)) result.Add(entry);
        }
        return result;
    }

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
