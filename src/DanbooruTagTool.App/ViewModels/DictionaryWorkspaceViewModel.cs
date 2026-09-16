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
    Func<CatalogEntry, string?>? browseBreadcrumb = null) : Observable
{
    public CatalogEntry Entry => entry;
    public string Label => (entry.IsSpecial ? "◆ " : "") + entry.Label;
    public string English => entry.Canonical ?? entry.English;
    public string Usage => entry.UsageText;
    public string Category => entry.EffectiveCategory;
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
    private int CanonicalMatchCount => entry.Canonical is { } canonical ? workspace.FindByCanonical(canonical).Count : 0;
    public string AddLabel => !entry.CanAdd ? "参照のみ" : CanonicalMatchCount switch
    {
        0 => "＋ Promptへ追加",
        1 => "✓ 追加済み（クリックで取消）",
        _ => $"✓ {CanonicalMatchCount}件追加済み（Prompt編集から削除）"
    };
    public string AddSymbol => !entry.CanAdd ? "参照" : CanonicalMatchCount > 0 ? "✓" : "＋";
    public string DetailAddLabel => AddLabel;
    private RelayCommand? addCommand;
    public RelayCommand Add => addCommand ??= new(_ => TogglePromptItem(), _ => CanTogglePromptItem());
    private bool CanTogglePromptItem() => (canMutate?.Invoke() ?? true) && entry.CanAdd && CanonicalMatchCount <= 1;
    private void TogglePromptItem()
    {
        if (!CanTogglePromptItem() || entry.Canonical is not { } canonical) return;
        var matches = workspace.FindByCanonical(canonical);
        if (matches.Count == 0) add(entry);
        else if (matches.Count == 1) workspace.Delete([matches[0].Id]);
    }
    public void Refresh() { Notify(nameof(AddLabel)); Notify(nameof(AddSymbol)); Notify(nameof(DetailAddLabel)); Add.Refresh(); }
}

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
    private readonly Action persist;
    private readonly Func<bool> canMutate;
    private SpecialBrowseV2Filter specialFilter = SpecialBrowseV2Filter.Empty;
    private readonly Stack<SpecialBrowseV2Filter> specialFilterHistory = new();
    private readonly Stack<string> back = new();
    private string query = "", browse = "special";
    private string? browseSelection;
    private int sortIndex, detailsTabIndex;
    private double dictionaryCardWidth = 480;
    private double browseScroll;
    private double restoreScroll;
    private IReadOnlyList<EntryViewModel> results = [], related = [];
    private EntryViewModel? selectedEntry;

    public ObservableCollection<SpecialBrowseFacetOptionViewModel> SpecialKindOptions { get; } = [];
    public ObservableCollection<SpecialBrowseFacetOptionViewModel> SpecialBodyOptions { get; } = [];
    public ObservableCollection<SpecialBrowseFacetOptionViewModel> SpecialThemeOptions { get; } = [];
    public IReadOnlyList<NavigationNode> Navigation { get; }
    public IReadOnlyList<EntryViewModel> Results { get => results; private set => Set(ref results, value); }
    public IReadOnlyList<EntryViewModel> Related { get => related; private set => Set(ref related, value); }
    public EntryViewModel? SelectedEntry
    {
        get => selectedEntry;
        set
        {
            if (!Set(ref selectedEntry, value)) return;
            Notify(nameof(Detail));
            Related = value == null ? [] : RelatedFor(value.Entry);
            persist();
        }
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
            if (Set(ref query, value)) { Notify(nameof(IsSearching)); Notify(nameof(CanBrowseSort)); persist(); }
        }
    }
    public string BrowseKey => browse;
    public int SortIndex { get => sortIndex; set { if (Set(ref sortIndex, value)) RefreshResults(); } }
    public int DetailsTabIndex { get => detailsTabIndex; set => Set(ref detailsTabIndex, value); }
    public bool IsSearching => !string.IsNullOrWhiteSpace(Query);
    public bool CanBrowseSort => !IsSearching;
    public bool CanGoBack => back.Count > 0;
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
            if (browse.StartsWith("general:", StringComparison.Ordinal))
                return general.Paths.FirstOrDefault(p => "general:" + p.Key == browse)?.Label
                    ?? general.Paths.FirstOrDefault(p => "general:" + p.GenreId + ">" == browse)?.Genre ?? "General";
            if (browse == "general") return "General";
            if (browse == "character") return "キャラクター";
            if (browse == "copyright") return "作品";
            if (browse == "artist") return "作者";
            if (specialBrowse != null)
            {
                if (!specialFilter.IsEmpty) return SpecialFacetSummary;
                return browse switch
                {
                    "special-v2:kinds" => "種類から探す",
                    "special-v2:body" => "部位から探す",
                    "special-v2:themes" => "テーマから探す",
                    _ => "◆ Special"
                };
            }
            return browse == "special" ? "◆ Special" : catalog.SpecialNavigationPaths.FirstOrDefault(p => "special:" + p.Key == browse)?.Label ?? "◆ Special";
        }
    }
    public string Pending => browse == "general" && Query.Length == 0 ? general.Status : "";
    public string Detail => selectedEntry == null ? "タグを選ぶと詳細を表示します。" : string.Join("\n\n", new[] {
        selectedEntry.Entry.Label, selectedEntry.Entry.Canonical ?? selectedEntry.Entry.English,
        "使用数 " + selectedEntry.Entry.UsageText, selectedEntry.Breadcrumb, selectedEntry.Entry.Description,
        selectedEntry.Entry.BrowseClassification == BrowseClassificationStatus.Unresolved ? "General分類は未解決のため、カテゴリ閲覧の対象外です。" : "",
        selectedEntry.Entry.ProductFit == "KEEP" ? "" : selectedEntry.Entry.ProductFit == "KEEP_REFERENCE_ONLY" ? "参照用" : "要確認",
        selectedEntry.Entry.Canonical == null ? "canonicalへの安全な追加先が確定していない参照項目です。" : "" }.Where(s => s.Length > 0));
    public string ResultSummary => $"{Results.Count:N0}件";
    public event Action? ResultsRestored;

    public RelayCommand InspectEntry { get; }
    public RelayCommand Navigate { get; }
    public RelayCommand Back { get; }
    public RelayCommand ClearQuery { get; }
    public RelayCommand ToggleSpecialFacet { get; }
    public RelayCommand UndoSpecialFacet { get; }
    public RelayCommand ClearSpecialFacets { get; }

    public DictionaryWorkspaceViewModel(IRuntimeCatalogQuery catalog, PromptWorkspace workspace, IGeneralBrowseProvider general,
        Action persist, Func<bool> canMutate, SpecialBrowseV2Index? specialBrowse = null)
    {
        this.catalog = catalog; this.workspace = workspace; this.general = general; this.persist = persist; this.canMutate = canMutate; this.specialBrowse = specialBrowse;
        if (specialBrowse != null)
        {
            foreach (var item in SpecialBrowseV2Taxonomy.Kinds) SpecialKindOptions.Add(new(SpecialBrowseV2Axis.Kind, item.Id, item.Label));
            foreach (var item in SpecialBrowseV2Taxonomy.BodySites) SpecialBodyOptions.Add(new(SpecialBrowseV2Axis.BodySite, item.Id, item.Label));
            foreach (var item in SpecialBrowseV2Taxonomy.Themes) SpecialThemeOptions.Add(new(SpecialBrowseV2Axis.Theme, item.Id, item.Label));
        }
        Navigation = [new("special", "◆ Special", specialBrowse == null ? BuildNavigation(catalog.SpecialNavigationPaths, "special:") : BuildSpecialNavigation()),
            new("general", "General", general.IsPending ? [] : BuildNavigation(general.Paths, "general:")),
            new("character", "キャラクター", []), new("copyright", "作品", []), new("artist", "作者", [])];
        InspectEntry = new(p => { if (p is EntryViewModel row) { SelectedEntry = row; DetailsTabIndex = 0; } }, p => canMutate() && p is EntryViewModel);
        Navigate = new(p => { if (p is NavigationNode n && !IsSpecialAxisHeading(n.Key)) NavigateTo(n.Key); }, p => canMutate() && p is NavigationNode);
        Back = new(_ => { if (back.TryPop(out var key)) { Notify(nameof(CanGoBack)); Back?.Refresh(); NavigateTo(key, false); } }, _ => canMutate() && CanGoBack);
        ClearQuery = new(_ => { Query = ""; RefreshResults(); }, _ => canMutate());
        ToggleSpecialFacet = new(ToggleFacet, p => canMutate() && specialBrowse != null && p is SpecialBrowseFacetOptionViewModel);
        UndoSpecialFacet = new(_ => UndoFacet(), _ => canMutate() && specialBrowse != null && !specialFilter.IsEmpty);
        ClearSpecialFacets = new(_ => ClearFacets(), _ => canMutate() && specialBrowse != null && !specialFilter.IsEmpty);
    }

    public void Restore(UiState ui)
    {
        query = ui.Query; browse = ui.Browse; restoreScroll = ui.BrowseScroll; browseScroll = ui.BrowseScroll;
        if (specialBrowse != null && browse.StartsWith("special:", StringComparison.Ordinal) && !browse.StartsWith("special-v2:", StringComparison.Ordinal)) browse = "special";
        specialFilter = SpecialFilterFromBrowse(browse);
    }

    public void RefreshResults()
    {
        var selected = SelectedEntry?.Entry.Id;
        IEnumerable<CatalogEntry> entries;
        if (!string.IsNullOrWhiteSpace(Query))
        {
            entries = catalog.Search(Query).Select(h => h.Entry);
            if (specialBrowse != null && !specialFilter.IsEmpty) entries = specialBrowse.IntersectInInputOrder(entries, specialFilter);
        }
        else if (browse == "general" || browse.StartsWith("general:", StringComparison.Ordinal))
        {
            entries = general.Browse(browse == "general" ? "" : browse[8..]);
            entries = SortIndex == 1 ? entries.OrderBy(e => e.Label, StringComparer.Create(CultureInfo.GetCultureInfo("ja-JP"), false)) : entries.OrderByDescending(e => e.Usage);
        }
        else if (browse is "character" or "copyright" or "artist")
        {
            var category = browse switch { "character" => "Character", "copyright" => "Copyright", _ => "Artist" };
            entries = catalog.BrowseCategory(category);
            entries = SortIndex == 1 ? entries.OrderBy(e => e.Label, StringComparer.Create(CultureInfo.GetCultureInfo("ja-JP"), false)) : entries.OrderByDescending(e => e.Usage);
        }
        else if (specialBrowse != null)
        {
            entries = catalog.BrowseCategory("Special");
            entries = SortIndex == 1 ? entries.OrderBy(e => e.Label, StringComparer.Create(CultureInfo.GetCultureInfo("ja-JP"), false)) : entries.OrderByDescending(e => e.Usage);
            entries = specialBrowse.IntersectInInputOrder(entries, specialFilter);
        }
        else
        {
            entries = browse == "special" ? catalog.BrowseCategory("Special") : catalog.BrowseSpecialPath(browse[8..]);
            entries = SortIndex == 1 ? entries.OrderBy(e => e.Label, StringComparer.Create(CultureInfo.GetCultureInfo("ja-JP"), false)) : entries.OrderByDescending(e => e.Usage);
        }
        Results = Rows(entries); Notify(nameof(ResultSummary));
        SelectedEntry = Results.FirstOrDefault(e => e.Entry.Id == (Query.Length == 0 ? browseSelection ?? selected : selected));
        RefreshSpecialFacetOptions();
        Notify(nameof(Pending)); Notify(nameof(BrowseLabel)); Notify(nameof(SpecialFacetSummary)); Notify(nameof(HasSpecialFacets)); Notify(nameof(ShowSpecialFacetBar)); Notify(nameof(ShowSpecialKindOptions));
        UndoSpecialFacet.Refresh(); ClearSpecialFacets.Refresh();
        if (Query.Length == 0) ResultsRestored?.Invoke();
    }

    public void NavigateTo(string key, bool remember = true)
    {
        if (!canMutate()) return;
        if (remember && browse != key) { back.Push(browse); Notify(nameof(CanGoBack)); Back.Refresh(); }
        browse = key;
        if (specialBrowse != null)
        {
            if (key.StartsWith("special-v2:kind:", StringComparison.Ordinal) || key.StartsWith("special-v2:body:", StringComparison.Ordinal) || key.StartsWith("special-v2:theme:", StringComparison.Ordinal)) ApplySpecialFilter(SpecialFilterFromBrowse(key), remember);
            else if (key == "special" || key.StartsWith("general", StringComparison.Ordinal) || key is "character" or "copyright" or "artist") { if (remember) specialFilterHistory.Clear(); specialFilter = SpecialBrowseV2Filter.Empty; }
        }
        Notify(nameof(BrowseKey)); browseSelection = null; RestoreScroll = 0; Query = ""; RefreshResults(); persist();
    }

    public void Add(CatalogEntry entry) { if (canMutate()) workspace.Add(entry); }
    public void InspectChip(ChipViewModel chip)
    {
        var entry = chip.Item.CatalogId is { } catalogId ? catalog.FindById(catalogId) : null;
        entry ??= catalog.Resolve(chip.Item.StructuredName ?? chip.Item.Surface.Trim());
        if (entry == null) { Query = chip.Item.StructuredName ?? chip.Item.Surface.Trim(); RefreshResults(); return; }
        SelectedEntry = new(entry, workspace, Add, canMutate, SpecialBreadcrumb); DetailsTabIndex = 0;
    }

    public void RefreshPromptState()
    {
        foreach (var row in Results.Concat(Related)) row.Refresh();
        SelectedEntry?.Refresh();
    }

    private IReadOnlyList<EntryViewModel> Rows(IEnumerable<CatalogEntry> entries) => entries.Select(e => new EntryViewModel(e, workspace, Add, canMutate, SpecialBreadcrumb)).ToArray();
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
    private string? SpecialBreadcrumb(CatalogEntry entry)
    {
        if (specialBrowse == null || !entry.IsSpecial) return null;
        var route = specialBrowse.Get(entry.Id); if (route == null || !route.CanBrowse) return null;
        var parts = new List<string>();
        if (route.KindId is { } kind) parts.Add("種類 > " + SpecialBrowseV2Taxonomy.Label(SpecialBrowseV2Axis.Kind, kind));
        if (route.BodySiteIds.Count > 0) parts.Add("部位 > " + string.Join(" + ", route.BodySiteIds.Select(id => SpecialBrowseV2Taxonomy.Label(SpecialBrowseV2Axis.BodySite, id))));
        if (route.ThemeIds.Count > 0) parts.Add("テーマ > " + string.Join(" + ", route.ThemeIds.Select(id => SpecialBrowseV2Taxonomy.Label(SpecialBrowseV2Axis.Theme, id))));
        return parts.Count == 0 ? null : string.Join(" / ", parts);
    }
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
    private static bool IsSpecialAxisHeading(string key) => key is "special-v2:kinds" or "special-v2:body" or "special-v2:themes";
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
