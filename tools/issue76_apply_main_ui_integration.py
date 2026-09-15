#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one match in {path}: {count}\n--- needle ---\n{old[:500]}")
    path.write_text(text.replace(old, new), encoding="utf-8")


vm = ROOT / "src/DanbooruTagTool.App/ViewModels/MainViewModel.cs"
app = ROOT / "src/DanbooruTagTool.App/App.xaml.cs"
xaml = ROOT / "src/DanbooruTagTool.App/MainWindow.xaml"
tests = ROOT / "src/DanbooruTagTool.Tests/Issue76MainUiIntegrationTests.cs"

replace_once(vm,
'''public sealed class EntryViewModel(CatalogEntry entry, PromptWorkspace workspace, Action<CatalogEntry> add, Func<bool>? canMutate = null) : Observable''',
'''public sealed class EntryViewModel(CatalogEntry entry, PromptWorkspace workspace, Action<CatalogEntry> add, Func<bool>? canMutate = null, Func<CatalogEntry, string?>? browseBreadcrumb = null) : Observable''')

replace_once(vm,
'''    public string Breadcrumb => string.IsNullOrWhiteSpace(entry.Breadcrumb) ? "—" : entry.Breadcrumb;''',
'''    public string Breadcrumb
    {
        get
        {
            var current = browseBreadcrumb?.Invoke(entry);
            if (!string.IsNullOrWhiteSpace(current)) return current;
            return string.IsNullOrWhiteSpace(entry.Breadcrumb) ? "—" : entry.Breadcrumb;
        }
    }''')

replace_once(vm,
'''    private readonly IGeneralBrowseProvider general;
    private readonly IForgeBridgeClient forgeBridge;
    public PromptWorkspace Workspace { get; }
    public ObservableCollection<ChipViewModel> Chips { get; } = [];''',
'''    private readonly IGeneralBrowseProvider general;
    private readonly IForgeBridgeClient forgeBridge;
    private readonly SpecialBrowseV2Index? specialBrowse;
    private SpecialBrowseV2Filter specialFilter = SpecialBrowseV2Filter.Empty;
    public PromptWorkspace Workspace { get; }
    public ObservableCollection<ChipViewModel> Chips { get; } = [];
    public ObservableCollection<SpecialBrowseFacetOptionViewModel> SpecialKindOptions { get; } = [];
    public ObservableCollection<SpecialBrowseFacetOptionViewModel> SpecialBodyOptions { get; } = [];
    public ObservableCollection<SpecialBrowseFacetOptionViewModel> SpecialThemeOptions { get; } = [];''')

replace_once(vm,
'''    public string BrowseKey => browse;
    public bool CanGoBack => back.Count > 0;''',
'''    public string BrowseKey => browse;
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
    }''')

replace_once(vm,
'''    public int DetailsTabIndex { get => detailsTabIndex; set => Set(ref detailsTabIndex, value); }
    public string BrowseLabel => browse.StartsWith("general:", StringComparison.Ordinal) ? general.Paths.FirstOrDefault(p => "general:" + p.Key == browse)?.Label ?? general.Paths.FirstOrDefault(p => "general:" + p.GenreId + ">" == browse)?.Genre ?? "General" : browse == "general" ? "General" : browse == "special" ? "◆ Special" : catalog.Entries.SelectMany(e => e.Paths).FirstOrDefault(p => "special:" + p.Key == browse)?.Label ?? "◆ Special";''',
'''    public int DetailsTabIndex { get => detailsTabIndex; set => Set(ref detailsTabIndex, value); }
    public string BrowseLabel
    {
        get
        {
            if (browse.StartsWith("general:", StringComparison.Ordinal))
                return general.Paths.FirstOrDefault(p => "general:" + p.Key == browse)?.Label
                    ?? general.Paths.FirstOrDefault(p => "general:" + p.GenreId + ">" == browse)?.Genre ?? "General";
            if (browse == "general") return "General";
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
            return browse == "special" ? "◆ Special" : catalog.Entries.SelectMany(e => e.Paths).FirstOrDefault(p => "special:" + p.Key == browse)?.Label ?? "◆ Special";
        }
    }''')

replace_once(vm,
'''    public RelayCommand Back { get; }
    public RelayCommand ClearQuery { get; }
    public RelayCommand FindPrevious { get; }''',
'''    public RelayCommand Back { get; }
    public RelayCommand ClearQuery { get; }
    public RelayCommand ToggleSpecialFacet { get; }
    public RelayCommand ClearSpecialFacets { get; }
    public RelayCommand FindPrevious { get; }''')

replace_once(vm,
'''    public MainViewModel(ICatalog catalog, IUserStateStore store, IClipboardService clipboard, IGeneralBrowseProvider? general = null, IForgeBridgeClient? forgeBridge = null)
    {
        this.catalog = catalog; this.store = store; this.clipboard = clipboard; this.general = general ?? new PendingGeneralBrowseProvider(); this.forgeBridge = forgeBridge ?? new ForgeBridgeClient();
        search = new(catalog); Workspace = new(new(catalog));
        var state = store.Load(); if (state != null) { Workspace.Restore(state.Prompt); ui = state.Ui; foreach (var preset in state.Presets ?? []) Presets.Add(preset); }
        query = ui.Query; browse = ui.Browse; workspaceIndex = ui.Workspace; englishChips = ui.EnglishChips; outputProfile = ui.OutputProfile; forgeUrl = ui.ForgeUrl; forgeExtensionPath = ui.ForgeExtensionPath; RestoreScroll = ui.BrowseScroll; BrowseScroll = ui.BrowseScroll;
        Navigation = [new("special", "◆ Special", catalog.Entries.Where(e => e.IsSpecial).SelectMany(e => e.Paths).GroupBy(p => p.GenreId)
            .Select(g => new NavigationNode("special:" + g.Key + ">", g.First().Genre, g.Where(p => p.SubgenreId.Length > 0).DistinctBy(p => p.Key)
                .Select(p => new NavigationNode("special:" + p.Key, p.Subgenre, [])).ToArray())).ToArray()), new("general", "General", this.general.IsPending ? [] : BuildNavigation(this.general.Paths, "general:"))];''',
'''    public MainViewModel(ICatalog catalog, IUserStateStore store, IClipboardService clipboard, IGeneralBrowseProvider? general = null, IForgeBridgeClient? forgeBridge = null, SpecialBrowseV2Index? specialBrowse = null)
    {
        this.catalog = catalog; this.store = store; this.clipboard = clipboard; this.general = general ?? new PendingGeneralBrowseProvider(); this.forgeBridge = forgeBridge ?? new ForgeBridgeClient(); this.specialBrowse = specialBrowse;
        search = new(catalog); Workspace = new(new(catalog));
        if (specialBrowse != null)
        {
            foreach (var item in SpecialBrowseV2Taxonomy.Kinds) SpecialKindOptions.Add(new(SpecialBrowseV2Axis.Kind, item.Id, item.Label));
            foreach (var item in SpecialBrowseV2Taxonomy.BodySites) SpecialBodyOptions.Add(new(SpecialBrowseV2Axis.BodySite, item.Id, item.Label));
            foreach (var item in SpecialBrowseV2Taxonomy.Themes) SpecialThemeOptions.Add(new(SpecialBrowseV2Axis.Theme, item.Id, item.Label));
        }
        var state = store.Load(); if (state != null) { Workspace.Restore(state.Prompt); ui = state.Ui; foreach (var preset in state.Presets ?? []) Presets.Add(preset); }
        query = ui.Query; browse = ui.Browse; workspaceIndex = ui.Workspace; englishChips = ui.EnglishChips; outputProfile = ui.OutputProfile; forgeUrl = ui.ForgeUrl; forgeExtensionPath = ui.ForgeExtensionPath; RestoreScroll = ui.BrowseScroll; BrowseScroll = ui.BrowseScroll;
        if (specialBrowse != null && browse.StartsWith("special:", StringComparison.Ordinal) && !browse.StartsWith("special-v2:", StringComparison.Ordinal)) browse = "special";
        specialFilter = SpecialFilterFromBrowse(browse);
        Navigation = [new("special", "◆ Special", specialBrowse == null
            ? catalog.Entries.Where(e => e.IsSpecial).SelectMany(e => e.Paths).GroupBy(p => p.GenreId)
                .Select(g => new NavigationNode("special:" + g.Key + ">", g.First().Genre, g.Where(p => p.SubgenreId.Length > 0).DistinctBy(p => p.Key)
                    .Select(p => new NavigationNode("special:" + p.Key, p.Subgenre, [])).ToArray())).ToArray()
            : BuildSpecialNavigation()), new("general", "General", this.general.IsPending ? [] : BuildNavigation(this.general.Paths, "general:"))];''')

replace_once(vm,
'''        ClearQuery = Normal(_ => { Query = ""; RefreshResults(); });
        FindPrevious = Normal(_ => FindNext(true), _ => Chips.Any(c => c.Match));''',
'''        ClearQuery = Normal(_ => { Query = ""; RefreshResults(); });
        ToggleSpecialFacet = Normal(p =>
        {
            if (specialBrowse == null || p is not SpecialBrowseFacetOptionViewModel option) return;
            specialFilter = option.Axis switch
            {
                SpecialBrowseV2Axis.Kind => specialFilter.WithKind(specialFilter.KindId == option.Id ? null : option.Id),
                SpecialBrowseV2Axis.BodySite => specialFilter.ToggleBodySite(option.Id),
                SpecialBrowseV2Axis.Theme => specialFilter.ToggleTheme(option.Id),
                _ => specialFilter
            };
            RefreshResults(); Persist();
        }, p => specialBrowse != null && p is SpecialBrowseFacetOptionViewModel);
        ClearSpecialFacets = Normal(_ =>
        {
            if (specialBrowse == null) return;
            specialFilter = SpecialBrowseV2Filter.Empty;
            browse = "special";
            Notify(nameof(BrowseKey));
            RefreshResults(); Persist();
        }, _ => specialBrowse != null && !specialFilter.IsEmpty);
        FindPrevious = Normal(_ => FindNext(true), _ => Chips.Any(c => c.Match));''')

replace_once(vm,
'''    private static NavigationNode[] BuildNavigation(IEnumerable<BrowsePath> paths, string prefix) => paths
        .GroupBy(p => p.GenreId).Select(g => new NavigationNode(prefix + g.Key + ">", g.First().Genre,
            g.Where(p => p.SubgenreId.Length > 0).DistinctBy(p => p.Key)
                .Select(p => new NavigationNode(prefix + p.Key, p.Subgenre, [])).ToArray())).ToArray();''',
'''    private static NavigationNode[] BuildNavigation(IEnumerable<BrowsePath> paths, string prefix) => paths
        .GroupBy(p => p.GenreId).Select(g => new NavigationNode(prefix + g.Key + ">", g.First().Genre,
            g.Where(p => p.SubgenreId.Length > 0).DistinctBy(p => p.Key)
                .Select(p => new NavigationNode(prefix + p.Key, p.Subgenre, [])).ToArray())).ToArray();
    private static NavigationNode[] BuildSpecialNavigation() =>
    [
        new("special-v2:kinds", "種類から探す", SpecialBrowseV2Taxonomy.Kinds.Select(item => new NavigationNode("special-v2:kind:" + item.Id, item.Label, [])).ToArray()),
        new("special-v2:body", "部位から探す", SpecialBrowseV2Taxonomy.BodySites.Select(item => new NavigationNode("special-v2:body:" + item.Id, item.Label, [])).ToArray()),
        new("special-v2:themes", "テーマから探す", SpecialBrowseV2Taxonomy.Themes.Select(item => new NavigationNode("special-v2:theme:" + item.Id, item.Label, [])).ToArray())
    ];
    private static SpecialBrowseV2Filter SpecialFilterFromBrowse(string key)
    {
        if (key.StartsWith("special-v2:kind:", StringComparison.Ordinal)) return SpecialBrowseV2Filter.Empty.WithKind(key[16..]);
        if (key.StartsWith("special-v2:body:", StringComparison.Ordinal)) return SpecialBrowseV2Filter.Empty.ToggleBodySite(key[16..]);
        if (key.StartsWith("special-v2:theme:", StringComparison.Ordinal)) return SpecialBrowseV2Filter.Empty.ToggleTheme(key[17..]);
        return SpecialBrowseV2Filter.Empty;
    }''')

replace_once(vm,
'''        foreach (var command in new[] { Copy, Import, New, Recover, Undo, Redo, Delete, DeleteOne, Inspect, InspectEntry, Navigate, Back, ClearQuery, FindPrevious, FindNextCommand, OpenEditor, StartDirect, ApplyDirect, CancelDirect, ApplyWeight, OpenPresets, NewPreset, ApplyPreset, CopyPresetNegative, CapturePresetPositive, SavePreset, DeletePreset, OpenForgeSettings, SaveForgeSettings }) command.Refresh();''',
'''        foreach (var command in new[] { Copy, Import, New, Recover, Undo, Redo, Delete, DeleteOne, Inspect, InspectEntry, Navigate, Back, ClearQuery, ToggleSpecialFacet, ClearSpecialFacets, FindPrevious, FindNextCommand, OpenEditor, StartDirect, ApplyDirect, CancelDirect, ApplyWeight, OpenPresets, NewPreset, ApplyPreset, CopyPresetNegative, CapturePresetPositive, SavePreset, DeletePreset, OpenForgeSettings, SaveForgeSettings }) command.Refresh();''')

replace_once(vm,
'''    private IReadOnlyList<EntryViewModel> Rows(IEnumerable<CatalogEntry> entries) => entries.Select(e => new EntryViewModel(e, Workspace, Add, () => CanEditPrompt)).ToArray();
    public void RefreshResults()
    {
        var selected = SelectedEntry?.Entry.Id;
        IEnumerable<CatalogEntry> entries;
        if (!string.IsNullOrWhiteSpace(Query)) entries = search.Search(Query).Select(h => h.Entry);
        else
        {
            entries = browse == "general" || browse.StartsWith("general:", StringComparison.Ordinal) ? general.Browse(browse == "general" ? "" : browse[8..]) : catalog.Entries.Where(e => e.IsSpecial && e.CanBrowse &&
                (browse == "special" || e.Paths.Any(p => "special:" + p.Key == browse || (browse.EndsWith('>') && browse == "special:" + p.GenreId + ">"))));
            entries = SortIndex == 1 ? entries.OrderBy(e => e.Label, StringComparer.Create(CultureInfo.GetCultureInfo("ja-JP"), false)) : entries.OrderByDescending(e => e.Usage);
        }
        Results = Rows(entries); Notify(nameof(ResultSummary)); SelectedEntry = Results.FirstOrDefault(e => e.Entry.Id == (Query.Length == 0 ? browseSelection ?? selected : selected));
        Notify(nameof(Pending)); Notify(nameof(BrowseLabel));
        if (Query.Length == 0) ResultsRestored?.Invoke();
    }
    public void NavigateTo(string key, bool remember = true)
    { if (!CanEditPrompt) return; if (remember && browse != key) { back.Push(browse); Notify(nameof(CanGoBack)); Back.Refresh(); } browse = key; Notify(nameof(BrowseKey)); browseSelection = null; RestoreScroll = 0; Query = ""; RefreshResults(); Persist(); }
    public void Add(CatalogEntry entry) { if (CanEditPrompt) Workspace.Add(entry); }''',
'''    private IReadOnlyList<EntryViewModel> Rows(IEnumerable<CatalogEntry> entries) => entries.Select(e => new EntryViewModel(e, Workspace, Add, () => CanEditPrompt, SpecialBreadcrumb)).ToArray();
    public void RefreshResults()
    {
        var selected = SelectedEntry?.Entry.Id;
        IEnumerable<CatalogEntry> entries;
        if (!string.IsNullOrWhiteSpace(Query))
        {
            entries = search.Search(Query).Select(h => h.Entry);
            if (specialBrowse != null && !specialFilter.IsEmpty) entries = specialBrowse.IntersectInInputOrder(entries, specialFilter);
        }
        else if (browse == "general" || browse.StartsWith("general:", StringComparison.Ordinal))
        {
            entries = general.Browse(browse == "general" ? "" : browse[8..]);
            entries = SortIndex == 1 ? entries.OrderBy(e => e.Label, StringComparer.Create(CultureInfo.GetCultureInfo("ja-JP"), false)) : entries.OrderByDescending(e => e.Usage);
        }
        else if (specialBrowse != null)
        {
            entries = catalog.Entries.Where(e => e.IsSpecial && e.CanBrowse);
            entries = SortIndex == 1 ? entries.OrderBy(e => e.Label, StringComparer.Create(CultureInfo.GetCultureInfo("ja-JP"), false)) : entries.OrderByDescending(e => e.Usage);
            entries = specialBrowse.IntersectInInputOrder(entries, specialFilter);
        }
        else
        {
            entries = catalog.Entries.Where(e => e.IsSpecial && e.CanBrowse &&
                (browse == "special" || e.Paths.Any(p => "special:" + p.Key == browse || (browse.EndsWith('>') && browse == "special:" + p.GenreId + ">"))));
            entries = SortIndex == 1 ? entries.OrderBy(e => e.Label, StringComparer.Create(CultureInfo.GetCultureInfo("ja-JP"), false)) : entries.OrderByDescending(e => e.Usage);
        }
        Results = Rows(entries); Notify(nameof(ResultSummary)); SelectedEntry = Results.FirstOrDefault(e => e.Entry.Id == (Query.Length == 0 ? browseSelection ?? selected : selected));
        RefreshSpecialFacetOptions();
        Notify(nameof(Pending)); Notify(nameof(BrowseLabel)); Notify(nameof(SpecialFacetSummary)); Notify(nameof(HasSpecialFacets)); Notify(nameof(ShowSpecialFacetBar)); Notify(nameof(ShowSpecialKindOptions));
        ClearSpecialFacets.Refresh();
        if (Query.Length == 0) ResultsRestored?.Invoke();
    }
    public void NavigateTo(string key, bool remember = true)
    {
        if (!CanEditPrompt) return;
        if (remember && browse != key) { back.Push(browse); Notify(nameof(CanGoBack)); Back.Refresh(); }
        browse = key;
        if (specialBrowse != null)
        {
            specialFilter = key.StartsWith("special-v2:", StringComparison.Ordinal) ? SpecialFilterFromBrowse(key)
                : key == "special" ? SpecialBrowseV2Filter.Empty
                : key.StartsWith("general", StringComparison.Ordinal) ? SpecialBrowseV2Filter.Empty : specialFilter;
        }
        Notify(nameof(BrowseKey)); browseSelection = null; RestoreScroll = 0; Query = ""; RefreshResults(); Persist();
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
        var route = specialBrowse.Get(entry.Id);
        if (route == null || !route.CanBrowse) return null;
        var parts = new List<string>();
        if (route.KindId is { } kind) parts.Add("種類 > " + SpecialBrowseV2Taxonomy.Label(SpecialBrowseV2Axis.Kind, kind));
        if (route.BodySiteIds.Count > 0) parts.Add("部位 > " + string.Join(" + ", route.BodySiteIds.Select(id => SpecialBrowseV2Taxonomy.Label(SpecialBrowseV2Axis.BodySite, id))));
        if (route.ThemeIds.Count > 0) parts.Add("テーマ > " + string.Join(" + ", route.ThemeIds.Select(id => SpecialBrowseV2Taxonomy.Label(SpecialBrowseV2Axis.Theme, id))));
        return parts.Count == 0 ? null : string.Join(" / ", parts);
    }
    private IReadOnlyList<EntryViewModel> RelatedFor(CatalogEntry entry)
    {
        if (specialBrowse == null || !entry.IsSpecial)
            return Rows(catalog.Entries.Where(e => e.IsSpecial && e.CanBrowse && e.Id != entry.Id && e.Paths.Any(p => entry.Paths.Any(v => v.Key == p.Key))).OrderByDescending(e => e.Usage).Take(6));
        var route = specialBrowse.Get(entry.Id);
        if (route == null || !route.CanBrowse) return [];
        var candidates = catalog.Entries.Where(e => e.IsSpecial && e.CanBrowse && e.Id != entry.Id).Where(e =>
        {
            var other = specialBrowse.Get(e.Id);
            return other != null && other.CanBrowse &&
                ((route.KindId != null && route.KindId == other.KindId)
                 || route.BodySiteIds.Overlaps(other.BodySiteIds)
                 || route.ThemeIds.Overlaps(other.ThemeIds));
        }).OrderByDescending(e => e.Usage);
        return Rows(specialBrowse.IntersectInInputOrder(candidates, SpecialBrowseV2Filter.Empty).Take(6));
    }
    public void Add(CatalogEntry entry) { if (CanEditPrompt) Workspace.Add(entry); }''')

replace_once(vm,
'''    public IReadOnlyList<EntryViewModel> Related { get => related; private set => Set(ref related, value); }
    private EntryViewModel? selectedEntry;
    public EntryViewModel? SelectedEntry { get => selectedEntry; set { if (Set(ref selectedEntry, value)) { Notify(nameof(Detail)); Related = value == null ? [] : Rows(catalog.Entries.Where(e => e.IsSpecial && e.CanBrowse && e.Id != value.Entry.Id && e.Paths.Any(p => value.Entry.Paths.Any(v => v.Key == p.Key))).OrderByDescending(e => e.Usage).Take(6)); Persist(); } } }''',
'''    public IReadOnlyList<EntryViewModel> Related { get => related; private set => Set(ref related, value); }
    private EntryViewModel? selectedEntry;
    public EntryViewModel? SelectedEntry { get => selectedEntry; set { if (Set(ref selectedEntry, value)) { Notify(nameof(Detail)); Related = value == null ? [] : RelatedFor(value.Entry); Persist(); } } }''')

replace_once(vm, '        "使用数 " + selectedEntry.Entry.UsageText, selectedEntry.Entry.Breadcrumb, selectedEntry.Entry.Description,',
                 '        "使用数 " + selectedEntry.Entry.UsageText, selectedEntry.Breadcrumb, selectedEntry.Entry.Description,')

replace_once(vm,
'''        SelectedEntry = new(entry, Workspace, Add, () => CanEditPrompt); DetailsTabIndex = 0;''',
'''        SelectedEntry = new(entry, Workspace, Add, () => CanEditPrompt, SpecialBreadcrumb); DetailsTabIndex = 0;''')

replace_once(app,
'''            var vm = new MainViewModel(catalog, new UserStateStore(paths.User), new ClipboardService(), GeneralBrowseProvider.FromCatalog(catalog));''',
'''            var specialBrowse = warning == null ? SpecialBrowseV2Overlay.Load(catalog) : null;
            var vm = new MainViewModel(catalog, new UserStateStore(paths.User), new ClipboardService(), GeneralBrowseProvider.FromCatalog(catalog), specialBrowse: specialBrowse);''')

replace_once(xaml,
'''        <Style x:Key="CompactSecondaryButton" TargetType="{x:Type Button}" BasedOn="{StaticResource SecondaryButton}">
            <Setter Property="Padding" Value="10,5"/>
            <Setter Property="MinHeight" Value="30"/>
            <Setter Property="FontSize" Value="13"/>
            <Setter Property="Margin" Value="0,0,6,0"/>
        </Style>''',
'''        <Style x:Key="CompactSecondaryButton" TargetType="{x:Type Button}" BasedOn="{StaticResource SecondaryButton}">
            <Setter Property="Padding" Value="10,5"/>
            <Setter Property="MinHeight" Value="30"/>
            <Setter Property="FontSize" Value="13"/>
            <Setter Property="Margin" Value="0,0,6,0"/>
        </Style>
        <Style x:Key="SpecialFacetButton" TargetType="{x:Type Button}" BasedOn="{StaticResource CompactButton}">
            <Setter Property="Padding" Value="8,4"/>
            <Setter Property="MinHeight" Value="27"/>
            <Setter Property="Margin" Value="0,0,5,4"/>
            <Style.Triggers>
                <DataTrigger Binding="{Binding IsVisible}" Value="False"><Setter Property="Visibility" Value="Collapsed"/></DataTrigger>
                <DataTrigger Binding="{Binding Selected}" Value="True"><Setter Property="Background" Value="{StaticResource PrimaryBrush}"/><Setter Property="BorderBrush" Value="{StaticResource PrimaryBrush}"/><Setter Property="Foreground" Value="White"/></DataTrigger>
            </Style.Triggers>
        </Style>''')

replace_once(xaml,
'''        <DataTemplate x:Key="EntryTemplate">''',
'''        <DataTemplate x:Key="SpecialFacetOptionTemplate">
            <Button Content="{Binding Label}" ToolTip="{Binding ToolTip}" Command="{Binding DataContext.ToggleSpecialFacet, RelativeSource={RelativeSource AncestorType=Window}}" CommandParameter="{Binding}" Style="{StaticResource SpecialFacetButton}"/>
        </DataTemplate>
        <DataTemplate x:Key="EntryTemplate">''')

replace_once(xaml, 'Specialはジャンルから発見できます。', 'Specialは種類・部位・テーマから探せます。')

replace_once(xaml,
'''                            <Grid.RowDefinitions><RowDefinition Height="Auto"/><RowDefinition Height="Auto"/><RowDefinition Height="Auto"/><RowDefinition Height="*"/></Grid.RowDefinitions>''',
'''                            <Grid.RowDefinitions><RowDefinition Height="Auto"/><RowDefinition Height="Auto"/><RowDefinition Height="Auto"/><RowDefinition Height="Auto"/><RowDefinition Height="*"/></Grid.RowDefinitions>''')

replace_once(xaml,
'''                            <DockPanel Grid.Row="2" Margin="0,0,0,6"><TextBlock Text="{Binding BrowseLabel}" FontWeight="SemiBold" VerticalAlignment="Center"/><TextBlock Text="  ·  " Foreground="{StaticResource MutedInkBrush}" VerticalAlignment="Center"/><TextBlock Text="{Binding Pending}" Style="{StaticResource HintText}" VerticalAlignment="Center"/></DockPanel>
                            <Border Grid.Row="3" Style="{StaticResource WorkSurfaceCard}" Padding="4"><ListBox x:Name="DictionaryList"''',
'''                            <DockPanel Grid.Row="2" Margin="0,0,0,6"><TextBlock Text="{Binding BrowseLabel}" FontWeight="SemiBold" VerticalAlignment="Center"/><TextBlock Text="  ·  " Foreground="{StaticResource MutedInkBrush}" VerticalAlignment="Center"/><TextBlock Text="{Binding Pending}" Style="{StaticResource HintText}" VerticalAlignment="Center"/></DockPanel>
                            <Border Grid.Row="3" Background="#F8FBFD" BorderBrush="{StaticResource BorderBrushSoft}" BorderThickness="1" CornerRadius="8" Padding="7,5" Margin="0,0,0,6" Visibility="{Binding ShowSpecialFacetBar, Converter={StaticResource BoolVisibility}}">
                                <StackPanel>
                                    <DockPanel Margin="0,0,0,2"><TextBlock Text="追加で絞り込み" Style="{StaticResource HintText}" FontWeight="SemiBold" VerticalAlignment="Center"/><Button DockPanel.Dock="Right" Content="すべて解除" Command="{Binding ClearSpecialFacets}" Style="{StaticResource CompactButton}" Padding="8,3" MinHeight="25" Margin="8,0,0,0"/></DockPanel>
                                    <DockPanel Visibility="{Binding ShowSpecialKindOptions, Converter={StaticResource BoolVisibility}}"><TextBlock DockPanel.Dock="Left" Text="種類" Style="{StaticResource HintText}" Width="42" Margin="0,5,4,0"/><ItemsControl ItemsSource="{Binding SpecialKindOptions}" ItemTemplate="{StaticResource SpecialFacetOptionTemplate}"><ItemsControl.ItemsPanel><ItemsPanelTemplate><WrapPanel/></ItemsPanelTemplate></ItemsControl.ItemsPanel></ItemsControl></DockPanel>
                                    <DockPanel><TextBlock DockPanel.Dock="Left" Text="部位" Style="{StaticResource HintText}" Width="42" Margin="0,5,4,0"/><ItemsControl ItemsSource="{Binding SpecialBodyOptions}" ItemTemplate="{StaticResource SpecialFacetOptionTemplate}"><ItemsControl.ItemsPanel><ItemsPanelTemplate><WrapPanel/></ItemsPanelTemplate></ItemsControl.ItemsPanel></ItemsControl></DockPanel>
                                    <DockPanel><TextBlock DockPanel.Dock="Left" Text="テーマ" Style="{StaticResource HintText}" Width="42" Margin="0,5,4,0"/><ItemsControl ItemsSource="{Binding SpecialThemeOptions}" ItemTemplate="{StaticResource SpecialFacetOptionTemplate}"><ItemsControl.ItemsPanel><ItemsPanelTemplate><WrapPanel/></ItemsPanelTemplate></ItemsControl.ItemsPanel></ItemsControl></DockPanel>
                                </StackPanel>
                            </Border>
                            <Border Grid.Row="4" Style="{StaticResource WorkSurfaceCard}" Padding="4"><ListBox x:Name="DictionaryList"''')

tests.write_text(r'''using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue76MainUiIntegrationTests
{
    private sealed class MemoryStore(UserState? initial = null) : IUserStateStore
    {
        public UserState? State { get; private set; } = initial;
        public UserState? Load() => State;
        public void Save(UserState state) => State = state;
    }

    private sealed class Clipboard : IClipboardService
    {
        public string Text { get; set; } = "";
        public string Read() => Text;
        public void Write(string text) => Text = text;
    }

    private static HashSet<string> Set(params string[] values) => new(values, StringComparer.Ordinal);

    private static CatalogEntry Entry(string id, string canonical, string japanese, long usage) =>
        new(id, canonical, canonical, japanese, true, usage, [], [], [new BrowsePath("OLD", "旧分類", "OLD_CHILD", "旧細分類")], "KEEP");

    private static Catalog Catalog() => new([
        Entry("S:1", "ball_gag", "ボールギャグ", 100),
        Entry("S:2", "ball_gag", "ボールギャグ別表現", 90),
        Entry("S:3", "fellatio", "フェラチオ", 80),
        Entry("S:4", "anal_beads", "アナルビーズ", 70),
        Entry("S:5", "bdsm", "BDSM", 60)
    ]);

    private static SpecialBrowseV2Index Index() => new([
        new("S:1", "TOOL_OBJECT", Set("MOUTH_ORAL"), Set("BDSM_RESTRAINT"), SpecialBrowseV2Status.AutoCandidate),
        new("S:2", "TOOL_OBJECT", Set("MOUTH_ORAL"), Set("BDSM_RESTRAINT"), SpecialBrowseV2Status.AutoCandidate),
        new("S:3", "ACTION_CONTACT", Set("MOUTH_ORAL", "MALE_GENITAL"), Set(), SpecialBrowseV2Status.AutoCandidate),
        new("S:4", "TOOL_OBJECT", Set("BUTTOCK_ANAL"), Set(), SpecialBrowseV2Status.AutoCandidate),
        new("S:5", null, Set(), Set("BDSM_RESTRAINT"), SpecialBrowseV2Status.AutoCandidate)
    ]);

    private static MainViewModel Vm(MemoryStore? store = null)
        => new(Catalog(), store ?? new(), new Clipboard(), specialBrowse: Index());

    [Fact]
    public void Special_navigation_uses_three_shallow_v2_axes_not_old_tree()
    {
        var vm = Vm();
        var special = Assert.Single(vm.Navigation.Where(node => node.Key == "special"));
        Assert.Equal(["種類から探す", "部位から探す", "テーマから探す"], special.Children.Select(node => node.Label).ToArray());
        Assert.DoesNotContain(special.Children.SelectMany(node => node.Children), node => node.Label == "旧細分類");
    }

    [Fact]
    public void Tool_mouth_bdsm_and_filter_keeps_current_cards_and_deduplicates_canonical()
    {
        var vm = Vm();
        vm.NavigateTo("special-v2:kind:TOOL_OBJECT");
        vm.ToggleSpecialFacet.Execute(vm.SpecialBodyOptions.Single(option => option.Id == "MOUTH_ORAL"));
        vm.ToggleSpecialFacet.Execute(vm.SpecialThemeOptions.Single(option => option.Id == "BDSM_RESTRAINT"));

        var row = Assert.Single(vm.Results);
        Assert.Equal("ball_gag", row.English);
        Assert.Equal("道具・物 × 口・口内 × 拘束・BDSM", vm.BrowseLabel);
        Assert.Contains("種類 > 道具・物", row.Breadcrumb);
        Assert.Contains("部位 > 口・口内", row.Breadcrumb);
        Assert.Contains("テーマ > 拘束・BDSM", row.Breadcrumb);
    }

    [Fact]
    public void Active_facets_intersect_existing_search_without_changing_relevance_order()
    {
        var vm = Vm();
        vm.NavigateTo("special-v2:body:MOUTH_ORAL");
        vm.Query = "ball_gag";
        vm.RefreshResults();

        Assert.Equal(["ball_gag"], vm.Results.Select(row => row.English).ToArray());
    }

    [Fact]
    public void Clearing_facets_returns_to_special_root_and_keeps_search_text()
    {
        var vm = Vm();
        vm.NavigateTo("special-v2:theme:BDSM_RESTRAINT");
        vm.Query = "ball_gag";
        vm.RefreshResults();

        vm.ClearSpecialFacets.Execute(null);

        Assert.Equal("special", vm.BrowseKey);
        Assert.Equal("ball_gag", vm.Query);
        Assert.False(vm.HasSpecialFacets);
    }

    [Fact]
    public void Persisted_old_special_path_is_migrated_to_v2_root_without_touching_prompt_state()
    {
        var state = new UserState(new WorkspaceSnapshot([], null), new UiState(Browse: "special:OLD>OLD_CHILD"));
        var vm = Vm(new MemoryStore(state));
        Assert.Equal("special", vm.BrowseKey);
    }
}
''', encoding="utf-8")

# The patcher is intentionally one-shot. The workflow removes it before committing
# the actual product changes so it does not remain as production tooling.
print("Issue #76 current-MainWindow integration patch applied")
