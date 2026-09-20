using System.Collections.ObjectModel;
using System.Globalization;
using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App.ViewModels;

public interface IClipboardService { string Read(); void Write(string text); }

public sealed class EntryViewModel(
    CatalogEntry entry,
    PromptWorkspace workspace,
    Action<CatalogEntry> add,
    Func<bool>? canMutate = null,
    Func<CatalogEntry, string?>? browseBreadcrumb = null,
    Func<CatalogEntry, bool>? deepDiscovery = null,
    Func<CatalogEntry, string?>? relationSummary = null,
    Func<CatalogEntry, int>? relatedCount = null,
    Action<CatalogEntry>? openRelated = null) : Observable
{
    public CatalogEntry Entry => entry;
    public bool IsDeepDiscovery => deepDiscovery?.Invoke(entry) == true;
    public string Label => (IsDeepDiscovery ? "◆ " : "") + entry.Label;
    public string English => entry.Canonical ?? entry.English;
    public string Usage => entry.UsageText;
    public string Category => entry.EffectiveCategory;
    private string? relationSummaryCache;
    private int? relatedCountCache;
    public string RelationSummary => relationSummaryCache ??= relationSummary?.Invoke(entry) ?? "";
    public int RelatedCount => relatedCountCache ??= relatedCount?.Invoke(entry) ?? 0;
    public bool HasRelated => RelatedCount > 0;
    public string RelatedActionLabel => entry.EffectiveCategory switch
    {
        "Character" => "作品を見る",
        "Copyright" => $"キャラを見る ({RelatedCount:N0})",
        _ => "関連を見る"
    };
    private RelayCommand? openRelatedCommand;
    public RelayCommand OpenRelated => openRelatedCommand ??= new(_ => openRelated?.Invoke(entry), _ => (canMutate?.Invoke() ?? true) && HasRelated && openRelated != null);
    public string Breadcrumb
    {
        get
        {
            var current = browseBreadcrumb?.Invoke(entry);
            if (!string.IsNullOrWhiteSpace(current)) return current;
            return string.IsNullOrWhiteSpace(entry.Breadcrumb) ? "—" : entry.Breadcrumb;
        }
    }
    public string Description
    {
        get
        {
            var text = entry.Description;
            var prefix = $"{entry.Label}（{entry.English}）";
            if (text.StartsWith(prefix, StringComparison.Ordinal))
            {
                var remainder = text[prefix.Length..];
                if (remainder.StartsWith('【'))
                {
                    var end = remainder.IndexOf('】');
                    if (end >= 0)
                    {
                        var metadata = remainder[..(end + 1)];
                        if (metadata.Contains("件】", StringComparison.Ordinal) || metadata.Contains("別名", StringComparison.Ordinal))
                            remainder = remainder[(end + 1)..];
                    }
                }
                text = remainder.Trim();
            }
            if (entry.Canonical != null && entry.English != entry.Canonical)
                text = $"別名: {entry.English} → {entry.Canonical}" + (text.Length > 0 ? "\n" + text : "");
            return text;
        }
    }
    private int PromptTokenMatchCount => entry.EffectivePromptToken is { } token ? workspace.FindByCanonical(token).Count : 0;
    public string AddLabel => !entry.CanAdd ? "参照のみ" : PromptTokenMatchCount switch
    {
        0 => "＋ Promptへ追加",
        1 => "✓ 追加済み（クリックで取消）",
        _ => $"✓ {PromptTokenMatchCount}件追加済み（Prompt編集から削除）"
    };
    public string AddSymbol => !entry.CanAdd ? "参照" : PromptTokenMatchCount > 0 ? "✓" : "＋";
    public string DetailAddLabel => AddLabel;
    private RelayCommand? addCommand;
    public RelayCommand Add => addCommand ??= new(_ => TogglePromptItem(), _ => CanTogglePromptItem());
    private bool CanTogglePromptItem() => (canMutate?.Invoke() ?? true) && entry.CanAdd && PromptTokenMatchCount <= 1;
    private void TogglePromptItem()
    {
        if (!CanTogglePromptItem() || entry.EffectivePromptToken is not { } token) return;
        var matches = workspace.FindByCanonical(token);
        if (matches.Count == 0) add(entry);
        else if (matches.Count == 1) workspace.Delete([matches[0].Id]);
    }
    public void Refresh() { Notify(nameof(AddLabel)); Notify(nameof(AddSymbol)); Notify(nameof(DetailAddLabel)); Add.Refresh(); OpenRelated.Refresh(); }
}

public enum DictionarySearchTarget { All, Character, Copyright, Artist }

public sealed record NavigationNode(string Key, string Label, IReadOnlyList<NavigationNode> Children);

public static class DictionaryLayoutMetrics
{
    public const double TwoColumnThreshold = 760;
    public const double MinimumCardWidth = 280;
    public static double CardWidth(double availableWidth)
    {
        var available = Math.Max(MinimumCardWidth, availableWidth);
        return available >= TwoColumnThreshold ? (available - 8) / 2 : available;
    }
    public static int ColumnCount(double availableWidth) => availableWidth >= TwoColumnThreshold ? 2 : 1;
}

public sealed record DictionaryResultRow(EntryViewModel First, EntryViewModel? Second)
{
    public int FirstColumnSpan => Second is null ? 2 : 1;
}

/// <summary>
/// Display-only projection over existing card references. Results remains the
/// flat semantic sequence and is never replaced by this row structure.
/// </summary>
public static class DictionaryResultProjection
{
    public static IReadOnlyList<DictionaryResultRow> Project(IReadOnlyList<EntryViewModel> results, int columnCount)
    {
        if (columnCount is < 1 or > 2) throw new ArgumentOutOfRangeException(nameof(columnCount));
        var rows = new List<DictionaryResultRow>((results.Count + columnCount - 1) / columnCount);
        for (var i = 0; i < results.Count; i += columnCount)
            rows.Add(new(results[i], columnCount == 2 && i + 1 < results.Count ? results[i + 1] : null));
        return rows;
    }
    public static IEnumerable<EntryViewModel> Flatten(IEnumerable<DictionaryResultRow> rows)
    {
        foreach (var row in rows) { yield return row.First; if (row.Second is not null) yield return row.Second; }
    }
}

/// <summary>
/// Owns dictionary browse/search state. MainViewModel composes this feature
/// owner but does not implement catalog queries or result selection itself.
/// </summary>
public sealed class DictionaryWorkspaceViewModel : Observable
{
    private readonly IRuntimeCatalogQuery catalog;
    private readonly PromptWorkspace workspace;
    private readonly IGeneralBrowseProvider general;
    private readonly SpecialBrowseV2Index? specialBrowse;
    private readonly UnifiedBrowseIndex unifiedBrowse;
    private readonly Action persist;
    private readonly Func<bool> canMutate;
    private UnifiedBrowseState unifiedState = UnifiedBrowseState.Neutral;
    private readonly Stack<UnifiedBrowseState> unifiedHistory = new();
    private SpecialBrowseV2Filter specialFilter = SpecialBrowseV2Filter.Empty;
    private readonly Stack<SpecialBrowseV2Filter> specialFilterHistory = new();
    private string query = "", browse = "tags";
    private string? browseSelection;
    private DictionarySearchTarget searchTarget = DictionarySearchTarget.All;
    private CatalogEntry? relatedSource;
    private int sortIndex, detailsTabIndex;
    private double dictionaryCardWidth = 480;
    private double browseScroll;
    private double restoreScroll;
    private IReadOnlyList<EntryViewModel> results = [], related = [];
    private bool relatedDirty = true;
    private IReadOnlyList<DictionaryResultRow> dictionaryRows = [];
    private IReadOnlyList<EntryViewModel> dictionaryFirstColumn = [], dictionarySecondColumn = [];
    private int dictionaryColumnCount = 1;
    private readonly Dictionary<string, List<EntryViewModel>> activeResultIndex = new(StringComparer.Ordinal);
    private Dictionary<string, int> promptCanonicalCounts = new(StringComparer.Ordinal);
    private EntryViewModel? selectedEntry;

    public ObservableCollection<SpecialBrowseFacetOptionViewModel> SpecialKindOptions { get; } = [];
    public ObservableCollection<SpecialBrowseFacetOptionViewModel> SpecialBodyOptions { get; } = [];
    public ObservableCollection<SpecialBrowseFacetOptionViewModel> SpecialThemeOptions { get; } = [];
    public ObservableCollection<BrowseFacetOptionViewModel> LocalOptions { get; } = [];
    public ObservableCollection<BrowseFacetOptionViewModel> BodyOptions { get; } = [];
    public ObservableCollection<BrowseFacetOptionViewModel> ThemeOptions { get; } = [];
    public IReadOnlyList<NavigationNode> Navigation { get; }
    public IReadOnlyList<EntryViewModel> Results
    {
        get => results;
        private set
        {
            if (!Set(ref results, value)) return;
            RebuildActiveResultIndex(); RebuildDictionaryRows();
        }
    }
    public IReadOnlyList<DictionaryResultRow> DictionaryRows => dictionaryRows;
    public IReadOnlyList<EntryViewModel> DictionaryFirstColumn => dictionaryFirstColumn;
    public IReadOnlyList<EntryViewModel> DictionarySecondColumn => dictionarySecondColumn;
    public int DictionaryColumnCount => dictionaryColumnCount;
    public IReadOnlyList<EntryViewModel> Related
    {
        get
        {
            if (!relatedDirty) return related;
            related = selectedEntry == null ? [] : RelatedFor(selectedEntry.Entry);
            relatedDirty = false;
            RebuildActiveResultIndex();
            return related;
        }
    }
    public EntryViewModel? SelectedEntry
    {
        get => selectedEntry;
        set => SetSelectedEntry(value);
    }
    public double DictionaryCardWidth { get => dictionaryCardWidth; set => Set(ref dictionaryCardWidth, value); }
    public double BrowseScroll { get => browseScroll; set => Set(ref browseScroll, value); }
    public double RestoreScroll { get => restoreScroll; private set => Set(ref restoreScroll, value); }
    public string Query
    {
        get => query;
        set
        {
            if (query.Length == 0 && value.Length > 0) { browseSelection = SelectedEntry?.Entry.Id; RestoreScroll = BrowseScroll; }
            if (Set(ref query, value)) { Notify(nameof(IsSearching)); Notify(nameof(CanBrowseSort)); Notify(nameof(ShowNeutralGuidance)); }
        }
    }
    public string BrowseKey => browse;
    public UnifiedBrowseScope Scope => unifiedState.Scope;
    public DictionarySearchTarget SearchTarget => searchTarget;
    public bool IsSearchAll => SearchTarget == DictionarySearchTarget.All;
    public bool IsSearchCharacter => SearchTarget == DictionarySearchTarget.Character;
    public bool IsSearchCopyright => SearchTarget == DictionarySearchTarget.Copyright;
    public bool IsSearchArtist => SearchTarget == DictionarySearchTarget.Artist;
    public bool ShowRelationBanner => relatedSource is not null;
    public string RelationBannerText => relatedSource switch
    {
        { EffectiveCategory: "Copyright" } => $"作品「{relatedSource.Label}」のキャラクター",
        { EffectiveCategory: "Character" } => $"キャラクター「{relatedSource.Label}」の作品",
        _ => ""
    };
    public string? PrimaryRouteId => unifiedState.PrimaryRouteId;
    public string? LocalSubrouteId => unifiedState.LocalSubrouteId;
    public IReadOnlySet<string> BodySiteIds => unifiedState.BodySiteIds;
    public IReadOnlySet<string> ThemeIds => unifiedState.ThemeIds;
    public bool DeepOnly => unifiedState.DeepOnly;
    public ContentIntentFilter ContentIntent => unifiedState.ContentIntent;
    public bool IsNeutralTags => unifiedState.IsNeutralTags;
    public bool ShowNeutralGuidance => IsNeutralTags && !IsSearching;
    public bool ShowUnifiedRefinement => Scope == UnifiedBrowseScope.Tags;
    public bool ShowLocalOptions => ShowUnifiedRefinement && LocalOptions.Any(option => option.IsVisible);
    public bool ShowBodyOptions => ShowUnifiedRefinement && BodyOptions.Any(option => option.IsVisible);
    public bool ShowThemeOptions => ShowUnifiedRefinement && ThemeOptions.Any(option => option.IsVisible);
    public bool IsContentAll => ContentIntent == ContentIntentFilter.All;
    public bool IsContentGeneralPurpose => ContentIntent == ContentIntentFilter.GeneralPurpose;
    public bool IsContentSexual => ContentIntent == ContentIntentFilter.Sexual;
    public int SortIndex { get => sortIndex; set { if (Set(ref sortIndex, value)) RefreshResults(); } }
    public int DetailsTabIndex { get => detailsTabIndex; set => Set(ref detailsTabIndex, value); }
    public bool IsSearching => !string.IsNullOrWhiteSpace(Query);
    public bool CanBrowseSort => !IsSearching;
    public bool CanGoBack => relatedSource is not null || unifiedHistory.Count > 0;
    public bool HasSpecialFacets => specialBrowse != null && !specialFilter.IsEmpty;
    public bool ShowSpecialFacetBar => HasSpecialFacets && !browse.StartsWith("general", StringComparison.Ordinal);
    public bool ShowSpecialKindOptions => ShowSpecialFacetBar && specialFilter.KindId is null;
    public string SpecialFacetSummary
    {
        get
        {
            var labels = new List<string>();
            if (specialFilter.KindId is { } kind) labels.Add(SpecialBrowseV2Taxonomy.Label(SpecialBrowseV2Axis.Kind, kind));
            labels.AddRange(specialFilter.BodySiteIds.Select(id => SpecialBrowseV2Taxonomy.Label(SpecialBrowseV2Axis.BodySite, id)));
            labels.AddRange(specialFilter.ThemeIds.Select(id => SpecialBrowseV2Taxonomy.Label(SpecialBrowseV2Axis.Theme, id)));
            return labels.Count == 0 ? "◆ Special" : string.Join(" × ", labels);
        }
    }
    public string BrowseLabel
    {
        get
        {
            if (Scope == UnifiedBrowseScope.Character) return "キャラクター";
            if (Scope == UnifiedBrowseScope.Copyright) return "作品";
            if (Scope == UnifiedBrowseScope.Artist) return "作者";
            if (LocalSubrouteId is { } local)
                return LocalOptions.FirstOrDefault(option => option.Id == local)?.Label
                    ?? UnifiedBrowseTaxonomy.Label(PrimaryRouteId ?? "");
            if (PrimaryRouteId is { } route) return UnifiedBrowseTaxonomy.Label(route);
            return "すべてのタグ";
        }
    }
    public string Pending => browse == "general" && Query.Length == 0 ? general.Status : "";
    public string Detail => selectedEntry == null ? "タグを選ぶと詳細を表示します。" : string.Join("\n\n", new[] {
        selectedEntry.Entry.Label, selectedEntry.Entry.Canonical ?? selectedEntry.Entry.English,
        "使用数 " + selectedEntry.Entry.UsageText, selectedEntry.Breadcrumb, selectedEntry.Entry.Description,
        selectedEntry.Entry.BrowseClassification == BrowseClassificationStatus.Unresolved ? "General分類は未解決のため、カテゴリ閲覧の対象外です。" : "",
        selectedEntry.Entry.ProductFit == "KEEP" ? "" : selectedEntry.Entry.ProductFit == "KEEP_REFERENCE_ONLY" ? "参照用" : "要確認",
        selectedEntry.Entry.Canonical == null ? "canonical同一性は未確定ですが、Promptには元の英語tokenを追加できます。" : "" }.Where(s => s.Length > 0));
    public string ResultSummary => $"{Results.Count:N0}件";
    public event Action? ResultsRestored;

    public RelayCommand InspectEntry { get; }
    public RelayCommand Navigate { get; }
    public RelayCommand Back { get; }
    public RelayCommand ClearQuery { get; }
    public RelayCommand ToggleSpecialFacet { get; }
    public RelayCommand UndoSpecialFacet { get; }
    public RelayCommand ClearSpecialFacets { get; }
    public RelayCommand ToggleBrowseFacet { get; }
    public RelayCommand ToggleDeepOnlyCommand { get; }
    public RelayCommand SetContentIntentCommand { get; }
    public RelayCommand UndoUnifiedBrowseCommand { get; }
    public RelayCommand ClearUnifiedBrowseCommand { get; }
    public RelayCommand SetSearchTargetCommand { get; }
    public RelayCommand ClearRelatedBrowseCommand { get; }

    public DictionaryWorkspaceViewModel(IRuntimeCatalogQuery catalog, PromptWorkspace workspace, IGeneralBrowseProvider general,
        Action persist, Func<bool> canMutate, SpecialBrowseV2Index? specialBrowse = null)
    {
        this.catalog = catalog; this.workspace = workspace; this.general = general; this.persist = persist; this.canMutate = canMutate; this.specialBrowse = specialBrowse;
        unifiedBrowse = new UnifiedBrowseIndex(catalog, specialBrowse);
        if (specialBrowse != null)
        {
            foreach (var item in SpecialBrowseV2Taxonomy.Kinds) SpecialKindOptions.Add(new(SpecialBrowseV2Axis.Kind, item.Id, item.Label));
            foreach (var item in SpecialBrowseV2Taxonomy.BodySites) SpecialBodyOptions.Add(new(SpecialBrowseV2Axis.BodySite, item.Id, item.Label));
            foreach (var item in SpecialBrowseV2Taxonomy.Themes) SpecialThemeOptions.Add(new(SpecialBrowseV2Axis.Theme, item.Id, item.Label));
        }
        foreach (var item in SpecialBrowseV2Taxonomy.BodySites)
            BodyOptions.Add(new(BrowseFacetKind.BodySite, item.Id, item.Label));
        foreach (var item in SpecialBrowseV2Taxonomy.Themes)
            ThemeOptions.Add(new(BrowseFacetKind.Theme, item.Id, item.Label));

        Navigation = UnifiedBrowseTaxonomy.Routes
            .GroupBy(route => route.Group, StringComparer.Ordinal)
            .Select((group, index) => new NavigationNode(
                "group:" + index,
                group.Key,
                group.Select(route => new NavigationNode("route:" + route.Id, route.Label, [])).ToArray()))
            .Concat([
                new NavigationNode("identity-group", "キャラクター・作品",
                [
                    new NavigationNode("copyright", "作品から探す", []),
                    new NavigationNode("character", "キャラクターから探す", [])
                ]),
                new NavigationNode("artist", "作者", [])
            ])
            .ToArray();
        InspectEntry = new(p => { if (p is EntryViewModel row) { SelectedEntry = row; DetailsTabIndex = 0; } }, p => canMutate() && p is EntryViewModel);
        Navigate = new(p => { if (p is NavigationNode n && !IsNavigationHeading(n.Key)) NavigateTo(n.Key); }, p => canMutate() && p is NavigationNode n && !IsNavigationHeading(n.Key));
        Back = new(_ => { if (relatedSource is not null) ClearRelatedBrowse(); else UndoUnifiedBrowse(); }, _ => canMutate() && CanGoBack);
        ClearQuery = new(_ => { Query = ""; RefreshResults(); persist(); }, _ => canMutate());
        SetSearchTargetCommand = new(p =>
        {
            if (p is DictionarySearchTarget target) SetSearchTarget(target);
            else if (p is string text && Enum.TryParse<DictionarySearchTarget>(text, true, out var parsed)) SetSearchTarget(parsed);
        }, _ => canMutate());
        ClearRelatedBrowseCommand = new(_ => ClearRelatedBrowse(), _ => canMutate() && relatedSource is not null);
        ToggleSpecialFacet = new(ToggleFacet, p => canMutate() && specialBrowse != null && p is SpecialBrowseFacetOptionViewModel);
        UndoSpecialFacet = new(_ => UndoFacet(), _ => canMutate() && specialBrowse != null && !specialFilter.IsEmpty);
        ClearSpecialFacets = new(_ => ClearFacets(), _ => canMutate() && specialBrowse != null && !specialFilter.IsEmpty);
        ToggleBrowseFacet = new(p =>
        {
            if (p is not BrowseFacetOptionViewModel option) return;
            if (option.Kind == BrowseFacetKind.Local) SetLocalSubroute(LocalSubrouteId == option.Id ? null : option.Id);
            else if (option.Kind == BrowseFacetKind.BodySite) ToggleBodySite(option.Id);
            else ToggleTheme(option.Id);
        }, p => canMutate() && Scope == UnifiedBrowseScope.Tags && p is BrowseFacetOptionViewModel);
        ToggleDeepOnlyCommand = new(_ => ToggleDeepOnly(), _ => canMutate() && Scope == UnifiedBrowseScope.Tags);
        SetContentIntentCommand = new(p =>
        {
            if (p is ContentIntentFilter value) SetContentIntent(value);
            else if (p is string text && Enum.TryParse<ContentIntentFilter>(text, true, out var parsed)) SetContentIntent(parsed);
        }, _ => canMutate() && Scope == UnifiedBrowseScope.Tags);
        UndoUnifiedBrowseCommand = new(_ => UndoUnifiedBrowse(), _ => canMutate() && unifiedHistory.Count > 0);
        ClearUnifiedBrowseCommand = new(_ => ClearUnifiedBrowse(), _ => canMutate() && Scope == UnifiedBrowseScope.Tags && !unifiedState.IsNeutralTags);
    }

    public void Restore(UiState ui)
    {
        query = ui.Query;
        restoreScroll = ui.BrowseScroll;
        browseScroll = ui.BrowseScroll;
        unifiedState = RestoreUnifiedState(ui);
        browse = BrowseKeyForState(unifiedState);
        specialFilter = SpecialBrowseV2Filter.Empty;
        unifiedHistory.Clear();
        promptCanonicalCounts = CaptureCanonicalCounts(workspace.Items);
        RefreshUnifiedFacetOptions();
        NotifyUnifiedState();
    }

    public void RefreshResults()
    {
        var selected = SelectedEntry?.Entry.Id;
        IEnumerable<CatalogEntry> entries;

        if (!string.IsNullOrWhiteSpace(Query))
        {
            var hits = catalog.Search(Query);
            if (Scope == UnifiedBrowseScope.Tags)
                entries = unifiedBrowse.FilterSearchHits(hits, unifiedState).Select(hit => hit.Entry);
            else
            {
                var category = CategoryForScope(Scope);
                entries = hits.Select(hit => hit.Entry).Where(entry => entry.EffectiveCategory == category);
            }
        }
        else if (Scope == UnifiedBrowseScope.Tags)
        {
            if (unifiedState.IsNeutralTags)
                entries = [];
            else
            {
                entries = unifiedBrowse.Browse(unifiedState);
                entries = SortIndex == 1
                    ? entries.OrderBy(entry => entry.Label, StringComparer.Create(CultureInfo.GetCultureInfo("ja-JP"), false))
                    : entries.OrderByDescending(entry => entry.Usage);
            }
        }
        else
        {
            entries = catalog.BrowseCategory(CategoryForScope(Scope));
            entries = SortIndex == 1
                ? entries.OrderBy(entry => entry.Label, StringComparer.Create(CultureInfo.GetCultureInfo("ja-JP"), false))
                : entries.OrderByDescending(entry => entry.Usage);
        }

        Results = Rows(entries);
        Notify(nameof(ResultSummary));
        SetSelectedEntry(Results.FirstOrDefault(entry => entry.Entry.Id == (Query.Length == 0 ? browseSelection ?? selected : selected)), persist: false);
        Notify(nameof(Pending));
        Notify(nameof(BrowseLabel));
        NotifyUnifiedState();
        if (Query.Length == 0) ResultsRestored?.Invoke();
    }

    public void NavigateTo(string key, bool remember = true)
    {
        if (!canMutate()) return;
        ApplyUnifiedState(StateForNavigationKey(key), remember);
    }

    public void SetScope(UnifiedBrowseScope scope)
    {
        if (!canMutate()) return;
        ApplyUnifiedState(unifiedState.WithScope(scope), true);
    }

    public void SetPrimaryRoute(string? routeId)
    {
        if (!canMutate()) return;
        if (routeId is not null && UnifiedBrowseTaxonomy.Routes.All(route => route.Id != routeId))
            throw new ArgumentOutOfRangeException(nameof(routeId));
        ApplyUnifiedState(unifiedState.WithScope(UnifiedBrowseScope.Tags).WithPrimary(routeId), true);
    }

    public void SetLocalSubroute(string? localId)
    {
        if (!canMutate()) return;
        ApplyUnifiedState(unifiedState.WithScope(UnifiedBrowseScope.Tags).WithLocal(localId), true);
    }

    public void ToggleBodySite(string bodySiteId)
    {
        if (!canMutate()) return;
        ApplyUnifiedState(unifiedState.WithScope(UnifiedBrowseScope.Tags).ToggleBodySite(bodySiteId), true);
    }

    public void ToggleTheme(string themeId)
    {
        if (!canMutate()) return;
        ApplyUnifiedState(unifiedState.WithScope(UnifiedBrowseScope.Tags).ToggleTheme(themeId), true);
    }

    public void ToggleDeepOnly()
    {
        if (!canMutate()) return;
        ApplyUnifiedState(unifiedState.WithScope(UnifiedBrowseScope.Tags) with { DeepOnly = !unifiedState.DeepOnly }, true);
    }

    public void SetContentIntent(ContentIntentFilter contentIntent)
    {
        if (!canMutate()) return;
        ApplyUnifiedState(unifiedState.WithScope(UnifiedBrowseScope.Tags) with { ContentIntent = contentIntent }, true);
    }

    public void UndoUnifiedBrowse()
    {
        if (!canMutate() || unifiedHistory.Count == 0) return;
        var previous = unifiedHistory.Pop();
        ApplyUnifiedState(previous, false);
    }

    public void ClearUnifiedBrowse()
    {
        if (!canMutate()) return;
        ApplyUnifiedState(unifiedState.ClearBrowseConstraints(), true);
    }

    private void ApplyUnifiedState(UnifiedBrowseState next, bool remember)
    {
        if (SameUnifiedState(unifiedState, next)) return;
        if (remember) unifiedHistory.Push(CloneState(unifiedState));
        unifiedState = CloneState(next);
        browse = BrowseKeyForState(unifiedState);
        browseSelection = null;
        RestoreScroll = 0;
        Notify(nameof(BrowseKey));
        RefreshUnifiedFacetOptions();
        NotifyUnifiedState();
        RefreshResults();
        persist();
    }

    private UnifiedBrowseState RestoreUnifiedState(UiState ui)
    {
        UnifiedBrowseState state;
        if (Enum.TryParse<UnifiedBrowseScope>(ui.BrowseScope, true, out var explicitScope))
            state = UnifiedBrowseState.Neutral.WithScope(explicitScope);
        else
            state = LegacyStateFromBrowse(ui.Browse);

        var hasExplicitUnifiedState =
            !string.IsNullOrWhiteSpace(ui.BrowseScope) ||
            ui.BrowsePrimaryRoute is not null ||
            ui.BrowseLocalSubroute is not null ||
            (ui.BrowseBodySites?.Length ?? 0) > 0 ||
            (ui.BrowseThemes?.Length ?? 0) > 0 ||
            ui.BrowseDeepOnly ||
            !string.Equals(ui.ContentIntent, "ALL", StringComparison.OrdinalIgnoreCase);

        if (hasExplicitUnifiedState)
        {
            state = state with
            {
                PrimaryRouteId = ui.BrowsePrimaryRoute,
                LocalSubrouteId = ui.BrowseLocalSubroute,
                BodySiteIds = new HashSet<string>(ui.BrowseBodySites ?? [], StringComparer.Ordinal),
                ThemeIds = new HashSet<string>(ui.BrowseThemes ?? [], StringComparer.Ordinal),
                DeepOnly = ui.BrowseDeepOnly,
                ContentIntent = ParseContentIntent(ui.ContentIntent)
            };
        }
        return CloneState(state);
    }

    private UnifiedBrowseState LegacyStateFromBrowse(string key)
    {
        if (key == "character") return UnifiedBrowseState.Neutral.WithScope(UnifiedBrowseScope.Character);
        if (key == "copyright") return UnifiedBrowseState.Neutral.WithScope(UnifiedBrowseScope.Copyright);
        if (key == "artist") return UnifiedBrowseState.Neutral.WithScope(UnifiedBrowseScope.Artist);
        if (key.StartsWith("general:", StringComparison.Ordinal))
        {
            var token = key[8..];
            var path = general.Paths.FirstOrDefault(item => item.Key == token || item.GenreId + ">" == token);
            if (path is not null)
            {
                var primary = UnifiedBrowseTaxonomy.GeneralRoute(path.GenreId);
                var local = UnifiedBrowseTaxonomy.GeneralLocal(path);
                return UnifiedBrowseState.Neutral with { PrimaryRouteId = primary, LocalSubrouteId = local?.Id };
            }
        }
        if (key.StartsWith("special-v2:kind:", StringComparison.Ordinal))
        {
            var primary = UnifiedBrowseTaxonomy.SpecialRoute(key[16..]);
            return primary is null
                ? UnifiedBrowseState.Neutral
                : UnifiedBrowseState.Neutral with { PrimaryRouteId = primary, DeepOnly = true };
        }
        if (key.StartsWith("special-v2:body:", StringComparison.Ordinal))
            return UnifiedBrowseState.Neutral.ToggleBodySite(key[16..]);
        if (key.StartsWith("special-v2:theme:", StringComparison.Ordinal))
            return UnifiedBrowseState.Neutral.ToggleTheme(key[17..]);
        return UnifiedBrowseState.Neutral;
    }

    private UnifiedBrowseState StateForNavigationKey(string key)
    {
        if (key == "tags" || key is "general" or "special") return unifiedState.WithScope(UnifiedBrowseScope.Tags).WithPrimary(null).WithLocal(null);
        if (key == "character") return unifiedState.WithScope(UnifiedBrowseScope.Character);
        if (key == "copyright") return unifiedState.WithScope(UnifiedBrowseScope.Copyright);
        if (key == "artist") return unifiedState.WithScope(UnifiedBrowseScope.Artist);
        if (key.StartsWith("route:", StringComparison.Ordinal))
            return unifiedState.WithScope(UnifiedBrowseScope.Tags).WithPrimary(key[6..]);
        if (key.StartsWith("local:", StringComparison.Ordinal))
            return unifiedState.WithScope(UnifiedBrowseScope.Tags).WithLocal(key[6..]);

        var legacy = LegacyStateFromBrowse(key);
        return legacy.IsNeutralTags && key is not ("general" or "special")
            ? unifiedState.WithScope(UnifiedBrowseScope.Tags)
            : legacy with { ContentIntent = unifiedState.ContentIntent };
    }

    private static string BrowseKeyForState(UnifiedBrowseState state)
    {
        if (state.Scope == UnifiedBrowseScope.Character) return "character";
        if (state.Scope == UnifiedBrowseScope.Copyright) return "copyright";
        if (state.Scope == UnifiedBrowseScope.Artist) return "artist";
        if (state.LocalSubrouteId is not null) return "local:" + state.LocalSubrouteId;
        if (state.PrimaryRouteId is not null) return "route:" + state.PrimaryRouteId;
        return "tags";
    }

    private static string CategoryForScope(UnifiedBrowseScope scope) => scope switch
    {
        UnifiedBrowseScope.Character => "Character",
        UnifiedBrowseScope.Copyright => "Copyright",
        UnifiedBrowseScope.Artist => "Artist",
        _ => throw new ArgumentOutOfRangeException(nameof(scope))
    };

    private static ContentIntentFilter ParseContentIntent(string value)
        => value.Trim().Replace("_", "", StringComparison.Ordinal).ToUpperInvariant() switch
        {
            "GENERALPURPOSE" => ContentIntentFilter.GeneralPurpose,
            "SEXUAL" => ContentIntentFilter.Sexual,
            _ => ContentIntentFilter.All
        };

    private static UnifiedBrowseState CloneState(UnifiedBrowseState state) => state with
    {
        BodySiteIds = state.BodySiteIds.ToHashSet(StringComparer.Ordinal),
        ThemeIds = state.ThemeIds.ToHashSet(StringComparer.Ordinal)
    };

    private static bool SameUnifiedState(UnifiedBrowseState left, UnifiedBrowseState right)
        => left.Scope == right.Scope
        && left.PrimaryRouteId == right.PrimaryRouteId
        && left.LocalSubrouteId == right.LocalSubrouteId
        && left.DeepOnly == right.DeepOnly
        && left.ContentIntent == right.ContentIntent
        && left.BodySiteIds.SetEquals(right.BodySiteIds)
        && left.ThemeIds.SetEquals(right.ThemeIds);

    private void NotifyUnifiedState()
    {
        Notify(nameof(Scope));
        Notify(nameof(PrimaryRouteId));
        Notify(nameof(LocalSubrouteId));
        Notify(nameof(BodySiteIds));
        Notify(nameof(ThemeIds));
        Notify(nameof(DeepOnly));
        Notify(nameof(ContentIntent));
        Notify(nameof(IsNeutralTags));
        Notify(nameof(ShowNeutralGuidance));
        Notify(nameof(ShowUnifiedRefinement));
        Notify(nameof(ShowLocalOptions));
        Notify(nameof(ShowBodyOptions));
        Notify(nameof(ShowThemeOptions));
        Notify(nameof(IsContentAll));
        Notify(nameof(IsContentGeneralPurpose));
        Notify(nameof(IsContentSexual));
        Notify(nameof(CanGoBack));
        Notify(nameof(BrowseLabel));
        UndoUnifiedBrowseCommand?.Refresh();
        Back?.Refresh();
        ClearUnifiedBrowseCommand?.Refresh();
        ToggleDeepOnlyCommand?.Refresh();
        SetContentIntentCommand?.Refresh();
    }

    private void RefreshUnifiedFacetOptions()
    {
        LocalOptions.Clear();
        foreach (var local in unifiedBrowse.LocalDefinitions(PrimaryRouteId))
        {
            var option = new BrowseFacetOptionViewModel(BrowseFacetKind.Local, local.Id, local.Label)
            {
                Selected = LocalSubrouteId == local.Id,
                Count = unifiedBrowse.CountWithLocal(unifiedState, local.Id)
            };
            LocalOptions.Add(option);
        }

        foreach (var option in BodyOptions)
        {
            option.Selected = BodySiteIds.Contains(option.Id);
            option.Count = unifiedBrowse.CountWithBodySite(unifiedState, option.Id);
        }
        foreach (var option in ThemeOptions)
        {
            option.Selected = ThemeIds.Contains(option.Id);
            option.Count = unifiedBrowse.CountWithTheme(unifiedState, option.Id);
        }
        Notify(nameof(ShowLocalOptions));
        Notify(nameof(ShowBodyOptions));
        Notify(nameof(ShowThemeOptions));
    }

    public void Add(CatalogEntry entry) { if (canMutate()) workspace.Add(entry); }
    public void InspectChip(ChipViewModel chip)
    {
        var entry = chip.Item.CatalogId is { } catalogId ? catalog.FindById(catalogId) : null;
        entry ??= catalog.Resolve(chip.Item.StructuredName ?? chip.Item.Surface.Trim());
        if (entry == null) { Query = chip.Item.StructuredName ?? chip.Item.Surface.Trim(); RefreshResults(); return; }
        SelectedEntry = new(entry, workspace, Add, canMutate, UnifiedBreadcrumb, IsDeepDiscovery); DetailsTabIndex = 0;
    }

    public void SetSurfaceWidth(double availableWidth)
    {
        DictionaryCardWidth = DictionaryLayoutMetrics.CardWidth(availableWidth);
        var columns = DictionaryLayoutMetrics.ColumnCount(availableWidth);
        if (columns == dictionaryColumnCount) return;
        dictionaryColumnCount = columns; Notify(nameof(DictionaryColumnCount)); RebuildDictionaryRows();
    }

    public void MoveResultSelection(int offset)
    {
        if (Results.Count == 0 || offset == 0) return;
        var current = selectedEntry == null ? -1 : Array.FindIndex(Results.ToArray(), row => ReferenceEquals(row, selectedEntry));
        if (current < 0) current = offset > 0 ? -1 : Results.Count;
        SetSelectedEntry(Results[Math.Clamp(current + offset, 0, Results.Count - 1)]);
    }
    public void SelectResultBoundary(bool last) { if (Results.Count > 0) SetSelectedEntry(Results[last ? Results.Count - 1 : 0]); }

    public void RefreshPromptState()
    {
        var next = CaptureCanonicalCounts(workspace.Items);
        var changed = ChangedCanonicals(promptCanonicalCounts, next);
        promptCanonicalCounts = next;
        var refreshed = RefreshRowsForCanonicals(changed);
        if (selectedEntry?.Entry.EffectivePromptToken is { } selectedToken && changed.Contains(selectedToken) && !refreshed.Contains(selectedEntry)) selectedEntry.Refresh();
    }

    private void SetSelectedEntry(EntryViewModel? value, bool persist = true)
    {
        if (!Set(ref selectedEntry, value)) return;
        Notify(nameof(Detail));
        related = [];
        var hadMaterializedRelated = !relatedDirty;
        relatedDirty = true;
        if (hadMaterializedRelated) RebuildActiveResultIndex();
        Notify(nameof(Related));
        if (persist) this.persist();
    }
    private void RebuildDictionaryRows()
    {
        dictionaryRows = DictionaryResultProjection.Project(Results, dictionaryColumnCount);
        dictionaryFirstColumn = dictionaryRows.Select(row => row.First).ToArray();
        dictionarySecondColumn = dictionaryRows.Where(row => row.Second is not null).Select(row => row.Second!).ToArray();
        Notify(nameof(DictionaryRows)); Notify(nameof(DictionaryFirstColumn)); Notify(nameof(DictionarySecondColumn));
    }
    private void RebuildActiveResultIndex()
    {
        activeResultIndex.Clear();
        foreach (var row in Results.Concat(relatedDirty ? [] : related))
        {
            if (row.Entry.EffectivePromptToken is not { } token) continue;
            if (!activeResultIndex.TryGetValue(token, out var rows)) activeResultIndex[token] = rows = [];
            if (!rows.Contains(row)) rows.Add(row);
        }
    }
    private HashSet<EntryViewModel> RefreshRowsForCanonicals(IReadOnlySet<string> changedCanonicals)
    {
        var refreshed = new HashSet<EntryViewModel>();
        foreach (var canonical in changedCanonicals)
            if (activeResultIndex.TryGetValue(canonical, out var rows))
                foreach (var row in rows) if (refreshed.Add(row)) row.Refresh();
        return refreshed;
    }
    private static Dictionary<string, int> CaptureCanonicalCounts(IEnumerable<PromptItem> items)
    {
        var counts = new Dictionary<string, int>(StringComparer.Ordinal);
        foreach (var item in items)
            if (item.Canonical is { } canonical) counts[canonical] = counts.TryGetValue(canonical, out var count) ? count + 1 : 1;
        return counts;
    }
    private static HashSet<string> ChangedCanonicals(IReadOnlyDictionary<string, int> previous, IReadOnlyDictionary<string, int> current)
    {
        var changed = new HashSet<string>(previous.Keys, StringComparer.Ordinal); changed.UnionWith(current.Keys);
        changed.RemoveWhere(c => previous.GetValueOrDefault(c) == current.GetValueOrDefault(c)); return changed;
    }

    private IReadOnlyList<EntryViewModel> Rows(IEnumerable<CatalogEntry> entries) => entries.Select(e => new EntryViewModel(e, workspace, Add, canMutate, UnifiedBreadcrumb, IsDeepDiscovery)).ToArray();
    private void ToggleFacet(object? parameter)
    {
        if (specialBrowse == null || parameter is not SpecialBrowseFacetOptionViewModel option) return;
        var next = option.Axis switch
        {
            SpecialBrowseV2Axis.Kind => specialFilter.WithKind(specialFilter.KindId == option.Id ? null : option.Id),
            SpecialBrowseV2Axis.BodySite => specialFilter.ToggleBodySite(option.Id),
            SpecialBrowseV2Axis.Theme => specialFilter.ToggleTheme(option.Id), _ => specialFilter
        };
        ApplySpecialFilter(next, true); RefreshResults(); persist();
    }
    private void UndoFacet()
    {
        if (specialBrowse == null || specialFilter.IsEmpty) return;
        if (specialFilterHistory.TryPop(out var previous)) specialFilter = previous;
        else if (specialFilter.ThemeIds.Count > 0) specialFilter = specialFilter.ToggleTheme(specialFilter.ThemeIds.Last());
        else if (specialFilter.BodySiteIds.Count > 0) specialFilter = specialFilter.ToggleBodySite(specialFilter.BodySiteIds.Last());
        else specialFilter = specialFilter.WithKind(null);
        if (specialFilter.IsEmpty) { browse = "special"; Notify(nameof(BrowseKey)); }
        RefreshResults(); persist();
    }
    private void ClearFacets()
    {
        if (specialBrowse == null) return;
        specialFilterHistory.Clear(); specialFilter = SpecialBrowseV2Filter.Empty; browse = "special"; Notify(nameof(BrowseKey)); RefreshResults(); persist();
    }
    private void RefreshSpecialFacetOptions()
    {
        if (specialBrowse == null) return;
        foreach (var option in SpecialKindOptions) { option.Selected = specialFilter.KindId == option.Id; option.Count = specialBrowse.CountWithKind(specialFilter, option.Id); }
        foreach (var option in SpecialBodyOptions) { option.Selected = specialFilter.BodySiteIds.Contains(option.Id); option.Count = specialBrowse.CountWithBodySite(specialFilter, option.Id); }
        foreach (var option in SpecialThemeOptions) { option.Selected = specialFilter.ThemeIds.Contains(option.Id); option.Count = specialBrowse.CountWithTheme(specialFilter, option.Id); }
    }
    private string? UnifiedBreadcrumb(CatalogEntry entry)
    {
        var identity = unifiedBrowse.Get(entry);
        if (identity is null)
            return string.IsNullOrWhiteSpace(entry.Breadcrumb) ? null : entry.Breadcrumb;

        var parts = new List<string>();
        if (identity.RouteIds.Count > 0)
            parts.Add(string.Join(" / ", identity.RouteIds.Select(UnifiedBrowseTaxonomy.Label).Distinct(StringComparer.Ordinal)));
        if (identity.BodySiteIds.Count > 0)
            parts.Add("部位 > " + string.Join(" + ", identity.BodySiteIds.Select(id => SpecialBrowseV2Taxonomy.Label(SpecialBrowseV2Axis.BodySite, id))));
        if (identity.ThemeIds.Count > 0)
            parts.Add("テーマ > " + string.Join(" + ", identity.ThemeIds.Select(id => SpecialBrowseV2Taxonomy.Label(SpecialBrowseV2Axis.Theme, id))));
        return parts.Count == 0 ? "通常検索" : string.Join("\n", parts);
    }

    private bool IsDeepDiscovery(CatalogEntry entry)
        => unifiedBrowse.Get(entry)?.DeepDiscovery == true;
    private IReadOnlyList<EntryViewModel> RelatedFor(CatalogEntry entry)
    {
        if (entry.EffectiveCategory == "Character" || (entry.EffectiveCategory == "Copyright" && entry.Canonical is not null) || specialBrowse == null || !entry.IsSpecial)
            return Rows(catalog.RelatedByCatalogMetadata(entry));
        var route = specialBrowse.Get(entry.Id); if (route == null || !route.CanBrowse) return [];
        var candidates = catalog.BrowseCategory("Special").Where(e => e.Id != entry.Id).Where(e =>
        {
            var other = specialBrowse.Get(e.Id);
            return other != null && other.CanBrowse && ((route.KindId != null && route.KindId == other.KindId) || route.BodySiteIds.Overlaps(other.BodySiteIds) || route.ThemeIds.Overlaps(other.ThemeIds));
        }).OrderByDescending(e => e.Usage);
        return Rows(specialBrowse.IntersectInInputOrder(candidates, SpecialBrowseV2Filter.Empty).Take(6));
    }
    private static NavigationNode[] BuildNavigation(IEnumerable<BrowsePath> paths, string prefix) => paths.GroupBy(p => p.GenreId).Select(g => new NavigationNode(prefix + g.Key + ">", g.First().Genre,
        g.Where(p => p.SubgenreId.Length > 0).DistinctBy(p => p.Key).Select(p => new NavigationNode(prefix + p.Key, p.Subgenre, [])).ToArray())).ToArray();
    private static NavigationNode[] BuildSpecialNavigation() =>
    [new("special-v2:kinds", "種類から探す", SpecialBrowseV2Taxonomy.Kinds.Select(item => new NavigationNode("special-v2:kind:" + item.Id, item.Label, [])).ToArray()),
     new("special-v2:body", "部位から探す", SpecialBrowseV2Taxonomy.BodySites.Select(item => new NavigationNode("special-v2:body:" + item.Id, item.Label, [])).ToArray()),
     new("special-v2:themes", "テーマから探す", SpecialBrowseV2Taxonomy.Themes.Select(item => new NavigationNode("special-v2:theme:" + item.Id, item.Label, [])).ToArray())];
    private static bool IsNavigationHeading(string key)
        => key.StartsWith("group:", StringComparison.Ordinal)
        || key is "special-v2:kinds" or "special-v2:body" or "special-v2:themes";
    private static bool SameSpecialFilter(SpecialBrowseV2Filter left, SpecialBrowseV2Filter right) => left.KindId == right.KindId && left.BodySiteIds.SetEquals(right.BodySiteIds) && left.ThemeIds.SetEquals(right.ThemeIds);
    private void ApplySpecialFilter(SpecialBrowseV2Filter next, bool remember) { if (SameSpecialFilter(next, specialFilter)) return; if (remember) specialFilterHistory.Push(specialFilter); specialFilter = next; }
    private static SpecialBrowseV2Filter SpecialFilterFromBrowse(string key)
    {
        if (key.StartsWith("special-v2:kind:", StringComparison.Ordinal)) return SpecialBrowseV2Filter.Empty.WithKind(key[16..]);
        if (key.StartsWith("special-v2:body:", StringComparison.Ordinal)) return SpecialBrowseV2Filter.Empty.ToggleBodySite(key[16..]);
        if (key.StartsWith("special-v2:theme:", StringComparison.Ordinal)) return SpecialBrowseV2Filter.Empty.ToggleTheme(key[17..]);
        return SpecialBrowseV2Filter.Empty;
    }
}
