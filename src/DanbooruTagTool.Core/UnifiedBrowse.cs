namespace DanbooruTagTool.Core;

public enum UnifiedBrowseScope { Tags, Character, Copyright, Artist }
public enum ContentIntentFilter { All, GeneralPurpose, Sexual }

public sealed record UnifiedBrowseRouteDefinition(string Id, string Label, string Group);
public sealed record UnifiedBrowseLocalDefinition(string Id, string Label, string PrimaryRouteId);

public static class UnifiedBrowseTaxonomy
{
    public static readonly UnifiedBrowseRouteDefinition[] Routes =
    [
        new("PEOPLE_COUNT", "人物・人数", "何を描く"),
        new("RELATION_ROLE", "関係・役割", "何を描く"),
        new("BODY_SITE", "身体・部位", "何を描く"),
        new("HAIR_FACE", "髪・顔", "何を描く"),
        new("CLOTHING_EXPOSURE", "衣装・露出", "何を描く"),
        new("TOOL_OBJECT", "道具・小物", "何を描く"),
        new("LIVING", "生物・植物", "何を描く"),
        new("NONHUMAN_TRANSFORM", "異形・変形", "何を描く"),
        new("ACTION_CONTACT", "行為・接触", "動き・状態"),
        new("POSE_POSITION", "ポーズ・体位", "動き・状態"),
        new("EXPRESSION_GAZE", "表情・視線", "動き・状態"),
        new("FLUID_EXCRETION", "体液・排泄", "動き・状態"),
        new("COMPOSITION_CAMERA", "構図・画角", "画面・表現"),
        new("SCENE_BACKGROUND", "場所・背景・場面", "画面・表現"),
        new("LIGHT_TIME_WEATHER", "光・時間・天候", "画面・表現"),
        new("COLOR_PATTERN_SHAPE", "色・柄・形", "画面・表現"),
        new("STYLE_PROCESSING", "画風・加工", "画面・表現"),
        new("TEXT_SYMBOL", "文字・記号", "画面・表現"),
        new("CONTENT_RATING", "内容区分・レーティング", "画面・表現")
    ];

    public static string Label(string routeId) => Routes.FirstOrDefault(route => route.Id == routeId)?.Label ?? routeId;

    public static string? GeneralRoute(string genreId) => genreId switch
    {
        "PERSON_COUNT" => "PEOPLE_COUNT",
        "BODY_PART" => "BODY_SITE",
        "HAIR_FACE" => "HAIR_FACE",
        "EXPRESSION_EMOTION" or "GAZE_ORIENTATION" => "EXPRESSION_GAZE",
        "POSE_MOVEMENT" => "POSE_POSITION",
        "COMPOSITION_CAMERA" => "COMPOSITION_CAMERA",
        "CLOTHING" or "CLOTHING_STATE_EXPOSURE" => "CLOTHING_EXPOSURE",
        "ACTION_CONTACT" => "ACTION_CONTACT",
        "OBJECT_PROP" => "TOOL_OBJECT",
        "LIVING_NATURE" => "LIVING",
        "PLACE_BACKGROUND" => "SCENE_BACKGROUND",
        "LIGHT_TIME_WEATHER" => "LIGHT_TIME_WEATHER",
        "COLOR_APPEARANCE" => "COLOR_PATTERN_SHAPE",
        "STYLE_QUALITY_META" => "STYLE_PROCESSING",
        "TEXT_SYMBOL" => "TEXT_SYMBOL",
        _ => null
    };

    public static string? SpecialRoute(string kindId) => kindId switch
    {
        "ACTION_CONTACT" => "ACTION_CONTACT",
        "CLOTHING_EXPOSURE" => "CLOTHING_EXPOSURE",
        "TOOL_OBJECT" => "TOOL_OBJECT",
        "BODY_STATE" => "BODY_SITE",
        "FLUID_EXCRETION" => "FLUID_EXCRETION",
        "PERSON_RELATION" => "RELATION_ROLE",
        "NONHUMAN_TRANSFORMATION" => "NONHUMAN_TRANSFORM",
        "META_EXPRESSION" => "CONTENT_RATING",
        _ => null
    };

    public static UnifiedBrowseLocalDefinition? GeneralLocal(BrowsePath path)
    {
        var primary = GeneralRoute(path.GenreId);
        if (primary is null) return null;
        if (path.SubgenreId.Length > 0)
            return new(path.GenreId + "/" + path.SubgenreId, path.Subgenre, primary);
        return path.GenreId switch
        {
            "EXPRESSION_EMOTION" or "GAZE_ORIENTATION" or "CLOTHING_STATE_EXPOSURE"
                => new(path.GenreId + "/", path.Genre, primary),
            _ => null
        };
    }
}

public sealed record UnifiedBrowseState(
    UnifiedBrowseScope Scope,
    string? PrimaryRouteId,
    string? LocalSubrouteId,
    IReadOnlySet<string> BodySiteIds,
    IReadOnlySet<string> ThemeIds,
    bool DeepOnly,
    ContentIntentFilter ContentIntent)
{
    public static UnifiedBrowseState Neutral { get; } = new(
        UnifiedBrowseScope.Tags,
        null,
        null,
        new HashSet<string>(StringComparer.Ordinal),
        new HashSet<string>(StringComparer.Ordinal),
        false,
        ContentIntentFilter.All);

    public bool HasBrowseConstraints => PrimaryRouteId is not null || LocalSubrouteId is not null ||
        BodySiteIds.Count > 0 || ThemeIds.Count > 0 || DeepOnly || ContentIntent != ContentIntentFilter.All;

    public bool IsNeutralTags => Scope == UnifiedBrowseScope.Tags && !HasBrowseConstraints;

    public UnifiedBrowseState WithScope(UnifiedBrowseScope scope) => this with { Scope = scope };

    public UnifiedBrowseState WithPrimary(string? routeId) => this with
    {
        PrimaryRouteId = routeId,
        LocalSubrouteId = string.Equals(PrimaryRouteId, routeId, StringComparison.Ordinal) ? LocalSubrouteId : null
    };

    public UnifiedBrowseState WithLocal(string? localId) => this with { LocalSubrouteId = localId };

    public UnifiedBrowseState ToggleBodySite(string id)
    {
        var next = BodySiteIds.ToHashSet(StringComparer.Ordinal);
        if (!next.Add(id)) next.Remove(id);
        return this with { BodySiteIds = next };
    }

    public UnifiedBrowseState ToggleTheme(string id)
    {
        var next = ThemeIds.ToHashSet(StringComparer.Ordinal);
        if (!next.Add(id)) next.Remove(id);
        return this with { ThemeIds = next };
    }

    public UnifiedBrowseState ClearBrowseConstraints() => Neutral with { Scope = Scope };
}

public sealed record UnifiedBrowseIdentity(
    string IdentityKey,
    CatalogEntry Representative,
    IReadOnlyList<CatalogEntry> BackingEntries,
    IReadOnlySet<string> RouteIds,
    IReadOnlySet<string> LocalSubrouteIds,
    IReadOnlySet<string> BodySiteIds,
    IReadOnlySet<string> ThemeIds,
    bool DeepDiscovery,
    SexualIntentClass? SexualIntent,
    SexualIntentClassificationStatus SexualIntentStatus);

public sealed class UnifiedBrowseIndex
{
    private readonly IReadOnlyDictionary<string, UnifiedBrowseIdentity> byIdentity;
    private readonly IReadOnlyDictionary<string, string> identityByCatalogId;
    private readonly IReadOnlyDictionary<string, UnifiedBrowseLocalDefinition> localDefinitions;

    public UnifiedBrowseIndex(IRuntimeCatalogQuery catalog, SpecialBrowseV2Index? specialBrowse = null)
    {
        var ordinary = catalog.Entries.Where(IsOrdinary).ToArray();
        var groups = ordinary.GroupBy(IdentityKey, StringComparer.Ordinal);
        var identities = new Dictionary<string, UnifiedBrowseIdentity>(StringComparer.Ordinal);
        var byCatalog = new Dictionary<string, string>(StringComparer.Ordinal);
        var locals = new Dictionary<string, UnifiedBrowseLocalDefinition>(StringComparer.Ordinal);

        foreach (var group in groups)
        {
            var rows = group.ToArray();
            foreach (var row in rows) byCatalog[row.Id] = group.Key;
            var canonical = rows.Select(row => row.Canonical).FirstOrDefault(value => value is not null);
            var representative = canonical is not null ? catalog.Resolve(canonical) ?? rows[0] : rows[0];

            var routeIds = new HashSet<string>(StringComparer.Ordinal);
            var localIds = new HashSet<string>(StringComparer.Ordinal);
            var bodyIds = new HashSet<string>(StringComparer.Ordinal);
            var themeIds = new HashSet<string>(StringComparer.Ordinal);
            var deep = false;

            foreach (var row in rows)
            {
                if (row.EffectiveCategory == "General" && row.CanBrowse && row.BrowseClassification == BrowseClassificationStatus.Proposed)
                {
                    foreach (var path in row.Paths)
                    {
                        var route = UnifiedBrowseTaxonomy.GeneralRoute(path.GenreId);
                        if (route is not null) routeIds.Add(route);
                        var local = UnifiedBrowseTaxonomy.GeneralLocal(path);
                        if (local is not null)
                        {
                            localIds.Add(local.Id);
                            locals.TryAdd(local.Id, local);
                        }
                    }
                }

                if (row.EffectiveCategory == "Special")
                {
                    var baked = row.SpecialBrowseV2;
                    var runtime = specialBrowse?.Get(row.Id);
                    var specialStatus = baked?.Status ?? runtime?.Status;
                    if (row.CanBrowse && (specialStatus is SpecialBrowseV2Status.AutoCandidate or SpecialBrowseV2Status.HumanResolved))
                    {
                        deep = true;
                        var kind = baked?.KindId ?? runtime?.KindId;
                        if (kind is not null)
                        {
                            var route = UnifiedBrowseTaxonomy.SpecialRoute(kind);
                            if (route is not null) routeIds.Add(route);
                        }
                        if (baked is not null)
                        {
                            bodyIds.UnionWith(baked.BodySiteIds);
                            themeIds.UnionWith(baked.ThemeIds);
                        }
                        else if (runtime is not null)
                        {
                            bodyIds.UnionWith(runtime.BodySiteIds);
                            themeIds.UnionWith(runtime.ThemeIds);
                        }
                    }
                }

                if (row.CanBrowse) routeIds.UnionWith(row.UnifiedBrowseRouteIds);
            }

            var intents = rows.Where(row => row.SexualIntent is not null).Select(row => row.SexualIntent).Distinct().ToArray();
            if (intents.Length > 1) throw new InvalidDataException("Conflicting sexual-intent metadata for " + group.Key);
            var statuses = rows.Select(row => row.SexualIntentStatus).Distinct().ToArray();
            var status = statuses.Contains(SexualIntentClassificationStatus.HumanReviewed)
                ? SexualIntentClassificationStatus.HumanReviewed
                : statuses.Contains(SexualIntentClassificationStatus.AutoHighConfidence)
                    ? SexualIntentClassificationStatus.AutoHighConfidence
                    : SexualIntentClassificationStatus.Unclassified;

            identities.Add(group.Key, new(
                group.Key,
                representative,
                rows,
                routeIds,
                localIds,
                bodyIds,
                themeIds,
                deep,
                intents.SingleOrDefault(),
                status));
        }

        byIdentity = identities;
        identityByCatalogId = byCatalog;
        localDefinitions = locals;
    }

    public IReadOnlyCollection<UnifiedBrowseIdentity> Identities => byIdentity.Values.ToArray();

    public UnifiedBrowseIdentity? Get(CatalogEntry entry)
        => identityByCatalogId.TryGetValue(entry.Id, out var key) ? byIdentity.GetValueOrDefault(key) : null;

    public IReadOnlyList<CatalogEntry> Browse(UnifiedBrowseState state)
    {
        if (state.Scope != UnifiedBrowseScope.Tags) return [];
        return byIdentity.Values.Where(identity => Matches(identity, state)).Select(identity => identity.Representative).ToArray();
    }

    public IReadOnlyList<SearchHit> FilterSearchHits(IEnumerable<SearchHit> hits, UnifiedBrowseState state)
    {
        if (state.Scope != UnifiedBrowseScope.Tags) return [];
        var result = new List<SearchHit>();
        var seen = new HashSet<string>(StringComparer.Ordinal);
        foreach (var hit in hits)
        {
            var identity = Get(hit.Entry);
            if (identity is not null && Matches(identity, state) && seen.Add(identity.IdentityKey))
                result.Add(hit);
        }
        return result;
    }

    public bool Matches(UnifiedBrowseIdentity identity, UnifiedBrowseState state)
    {
        if (state.PrimaryRouteId is { } route && !identity.RouteIds.Contains(route)) return false;
        if (state.LocalSubrouteId is { } local && !identity.LocalSubrouteIds.Contains(local)) return false;
        if (!state.BodySiteIds.All(identity.BodySiteIds.Contains)) return false;
        if (!state.ThemeIds.All(identity.ThemeIds.Contains)) return false;
        if (state.DeepOnly && !identity.DeepDiscovery) return false;
        return state.ContentIntent switch
        {
            ContentIntentFilter.All => true,
            ContentIntentFilter.GeneralPurpose => identity.SexualIntent is SexualIntentClass.NonSexual or SexualIntentClass.Contextual,
            ContentIntentFilter.Sexual => identity.SexualIntent is SexualIntentClass.Sexual or SexualIntentClass.Contextual,
            _ => false
        };
    }

    public IReadOnlyList<UnifiedBrowseLocalDefinition> LocalDefinitions(string? primaryRouteId)
        => primaryRouteId is null ? [] : localDefinitions.Values.Where(item => item.PrimaryRouteId == primaryRouteId)
            .OrderBy(item => item.Label, StringComparer.Ordinal).ToArray();

    public int Count(UnifiedBrowseState state) => byIdentity.Values.Count(identity => Matches(identity, state));

    public int CountWithLocal(UnifiedBrowseState state, string localId)
        => Count(state.WithLocal(state.LocalSubrouteId == localId ? null : localId));

    public int CountWithBodySite(UnifiedBrowseState state, string bodySiteId)
        => Count(state.BodySiteIds.Contains(bodySiteId) ? state : state.ToggleBodySite(bodySiteId));

    public int CountWithTheme(UnifiedBrowseState state, string themeId)
        => Count(state.ThemeIds.Contains(themeId) ? state : state.ToggleTheme(themeId));

    private static bool IsOrdinary(CatalogEntry entry) => entry.EffectiveCategory is "General" or "Special";

    public static string IdentityKey(CatalogEntry entry)
        => entry.Canonical is { } canonical ? "C:" + canonical : "I:" + entry.Id;
}
