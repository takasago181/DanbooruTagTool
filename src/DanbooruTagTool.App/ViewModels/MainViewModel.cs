using System.Collections.ObjectModel;
using System.Globalization;
using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App.ViewModels;

public interface IClipboardService { string Read(); void Write(string text); }
public sealed class EntryViewModel(CatalogEntry entry, PromptWorkspace workspace, Action<CatalogEntry> add, Func<bool>? canMutate = null) : Observable
{
    public CatalogEntry Entry => entry;
    public string Label => (entry.IsSpecial ? "◆ " : "") + entry.Label;
    public string English => entry.Canonical ?? entry.English;
    public string Usage => entry.UsageText;
    public string Category => entry.IsSpecial ? "Special" : "General";
    public string Breadcrumb => string.IsNullOrWhiteSpace(entry.Breadcrumb) ? "—" : entry.Breadcrumb;
    public string Description
    {
        get
        {
            // Accepted display text sometimes consists solely of metadata
            // already shown above. Remove only that exact generated prefix.
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
            if (entry.Canonical != null && entry.English != entry.Canonical) text = $"別名: {entry.English} → {entry.Canonical}" + (text.Length > 0 ? "\n" + text : "");
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
public sealed class ChipViewModel(PromptItem item) : Observable
{
    public PromptItem Item => item;
    public Guid Id => item.Id;
    private bool selected, match, english;
    public bool Selected { get => selected; set => Set(ref selected, value); }
    public bool Match { get => match; set => Set(ref match, value); }
    public bool English { get => english; set { if (Set(ref english, value)) Notify(nameof(Label)); } }
    public string Label => English ? item.Surface : item.Display;
}
public sealed record NavigationNode(string Key, string Label, IReadOnlyList<NavigationNode> Children);
public sealed record PromptOutputProfileOption(PromptOutputProfile Value, string Label);

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

public sealed class MainViewModel : Observable
{
    private readonly ICatalog catalog;
    private readonly SearchEngine search;
    private readonly IUserStateStore store;
    private readonly IClipboardService clipboard;
    private readonly IGeneralBrowseProvider general;
    public PromptWorkspace Workspace { get; }
    public ObservableCollection<ChipViewModel> Chips { get; } = [];
    public IReadOnlyList<NavigationNode> Navigation { get; }
    private IReadOnlyList<PromptCategoryGroup> categoryGroups = [];
    public IReadOnlyList<PromptCategoryGroup> CategoryGroups { get => categoryGroups; private set => Set(ref categoryGroups, value); }
    private IReadOnlyList<EntryViewModel> results = [], related = [];
    public IReadOnlyList<EntryViewModel> Results { get => results; private set => Set(ref results, value); }
    private double dictionaryCardWidth = 480;
    // The view updates this from the available result surface. It is deliberately
    // transient: layout density is a display concern, not persisted user data.
    public double DictionaryCardWidth { get => dictionaryCardWidth; set => Set(ref dictionaryCardWidth, value); }
    public IReadOnlyList<EntryViewModel> Related { get => related; private set => Set(ref related, value); }
    private EntryViewModel? selectedEntry;
    public EntryViewModel? SelectedEntry { get => selectedEntry; set { if (Set(ref selectedEntry, value)) { Notify(nameof(Detail)); Related = value == null ? [] : Rows(catalog.Entries.Where(e => e.IsSpecial && e.CanBrowse && e.Id != value.Entry.Id && e.Paths.Any(p => value.Entry.Paths.Any(v => v.Key == p.Key))).OrderByDescending(e => e.Usage).Take(6)); Persist(); } } }
    public string Detail => selectedEntry == null ? "タグを選ぶと詳細を表示します。" : string.Join("\n\n", new[] {
        selectedEntry.Entry.Label, selectedEntry.Entry.Canonical ?? selectedEntry.Entry.English,
        "使用数 " + selectedEntry.Entry.UsageText, selectedEntry.Entry.Breadcrumb, selectedEntry.Entry.Description,
        selectedEntry.Entry.BrowseClassification == BrowseClassificationStatus.Unresolved ? "General分類は未解決のため、カテゴリ閲覧の対象外です。" : "",
        selectedEntry.Entry.ProductFit == "KEEP" ? "" : selectedEntry.Entry.ProductFit == "KEEP_REFERENCE_ONLY" ? "参照用" : "要確認",
        selectedEntry.Entry.Canonical == null ? "canonicalへの安全な追加先が確定していない参照項目です。" : "" }.Where(s => s.Length > 0));
    private string query = "", browse = "special", status = "", find = "", directText = "", weight = "";
    private string presetName = "", presetDescription = "", presetPositive = "", presetNegative = "";
    private int workspaceIndex, sortIndex, detailsTabIndex;
    private bool englishChips, multiSelect, directEditing, categoryView, categoryEnglish;
    private PromptOutputProfile outputProfile = PromptOutputProfile.Canonical;
    private GenerationPreset? selectedPreset;
    private Guid? anchor;
    private UiState ui = new();
    private readonly Stack<string> back = new();
    private string? browseSelection;
    public double BrowseScroll { get; set; }
    public double RestoreScroll { get; private set; }
    public string BrowseKey => browse;
    public bool CanGoBack => back.Count > 0;
    public event Action? ResultsRestored;
    public event Action<Guid>? ScrollToChip;
    public event Action? PresetsRequested;
    public UiState Ui => ui;
    public ObservableCollection<GenerationPreset> Presets { get; } = [];
    public GenerationPreset? SelectedPreset
    {
        get => selectedPreset;
        set
        {
            if (!Set(ref selectedPreset, value)) return;
            PresetName = value?.Name ?? "";
            PresetDescription = value?.Description ?? "";
            PresetPositive = value?.Positive ?? "";
            PresetNegative = value?.Negative ?? "";
        }
    }
    public string PresetName { get => presetName; set { if (Set(ref presetName, value)) SavePreset?.Refresh(); } }
    public string PresetDescription { get => presetDescription; set => Set(ref presetDescription, value); }
    public string PresetPositive { get => presetPositive; set => Set(ref presetPositive, value); }
    public string PresetNegative { get => presetNegative; set => Set(ref presetNegative, value); }
    public string Query { get => query; set { if (query.Length == 0 && value.Length > 0) { browseSelection = SelectedEntry?.Entry.Id; RestoreScroll = BrowseScroll; } if (Set(ref query, value)) { Notify(nameof(IsSearching)); Notify(nameof(CanBrowseSort)); Persist(); } } }
    public bool IsSearching => !string.IsNullOrWhiteSpace(Query);
    public bool CanBrowseSort => !IsSearching;
    public int DetailsTabIndex { get => detailsTabIndex; set => Set(ref detailsTabIndex, value); }
    public string BrowseLabel => browse.StartsWith("general:", StringComparison.Ordinal) ? general.Paths.FirstOrDefault(p => "general:" + p.Key == browse)?.Label ?? general.Paths.FirstOrDefault(p => "general:" + p.GenreId + ">" == browse)?.Genre ?? "General" : browse == "general" ? "General" : browse == "special" ? "◆ Special" : catalog.Entries.SelectMany(e => e.Paths).FirstOrDefault(p => "special:" + p.Key == browse)?.Label ?? "◆ Special";
    public string Pending => browse == "general" && Query.Length == 0 ? general.Status : "";
    public int WorkspaceIndex { get => workspaceIndex; set { if (!DirectEditing && Set(ref workspaceIndex, value)) Persist(); } }
    public int SortIndex { get => sortIndex; set { if (Set(ref sortIndex, value)) RefreshResults(); } }
    public bool EnglishChips { get => englishChips; set { if (Set(ref englishChips, value)) { foreach (var c in Chips) c.English = value && WorkspaceIndex == 0; Persist(); } } }
    public bool IsCategoryView { get => categoryView; set { if (Set(ref categoryView, value)) { Notify(nameof(IsOrderedView)); Notify(nameof(CanEditOrderedPrompt)); Notify(nameof(SelectionSummary)); Notify(nameof(WeightVisible)); RefreshCommands(); } } }
    public bool IsOrderedView { get => !IsCategoryView; set { if (value != IsOrderedView) IsCategoryView = !value; } }
    public bool CategoryEnglish { get => categoryEnglish; set => Set(ref categoryEnglish, value); }
    public bool MultiSelect { get => multiSelect; set => Set(ref multiSelect, value); }
    public bool HasSelection => Chips.Any(c => c.Selected);
    public string SelectionSummary => IsCategoryView ? "カテゴリ別表示（読み取り専用）" : HasSelection ? $"{Chips.Count(c => c.Selected)}件選択中" : "選択なし";
    public string English => PromptOutputFormatter.Serialize(Workspace.Items, OutputProfile);
    public IReadOnlyList<PromptOutputProfileOption> OutputProfiles { get; } =
    [new(PromptOutputProfile.GenerationFriendly, "生成向け"), new(PromptOutputProfile.Canonical, "原形優先")];
    public PromptOutputProfile OutputProfile
    {
        get => outputProfile;
        set
        {
            if (Set(ref outputProfile, value)) { Notify(nameof(English)); Persist(); }
        }
    }
    public string Count => $"現在のPrompt · {Chips.Count}件";
    public bool HasPrompt => Chips.Count > 0;
    public string ResultSummary => $"{Results.Count:N0}件";
    public string Unresolved => Chips.Count(c => c.Item.Kind == PromptItemKind.Raw) is var n && n > 0 ? $"未解決 {n}" : "";
    public string Status { get => status; set => Set(ref status, value); }
    public string Find { get => find; set { if (Set(ref find, value)) { lastMatch = null; Notify(nameof(HasFindQuery)); UpdateMatches(); FindNext(false); } } }
    public bool HasFindQuery => Find.Length > 0;
    public string FindMatchSummary
    {
        get
        {
            if (!HasFindQuery) return "";
            var matches = Chips.Where(c => c.Match).ToArray();
            if (matches.Length == 0) return "0件一致";
            var index = Array.FindIndex(matches, c => c.Id == lastMatch);
            return $"{matches.Length}件一致 · {(index >= 0 ? index + 1 : 0)}/{matches.Length}";
        }
    }
    public bool CanEditPrompt => !DirectEditing;
    public bool CanEditOrderedPrompt => CanEditPrompt && IsOrderedView;
    public bool DirectEditing { get => directEditing; private set { if (Set(ref directEditing, value)) { Notify(nameof(CanEditPrompt)); Notify(nameof(CanEditOrderedPrompt)); RefreshCommands(); } } }
    public string DirectText { get => directText; set => Set(ref directText, value); }
    public string Weight { get => weight; set => Set(ref weight, value); }
    public bool WeightVisible => IsOrderedView && Chips.Count(c => c.Selected) == 1 && Chips.Single(c => c.Selected).Item.CanEditWeight;
    public RelayCommand Copy { get; }
    public RelayCommand Import { get; }
    public RelayCommand New { get; }
    public RelayCommand Recover { get; }
    public RelayCommand Undo { get; }
    public RelayCommand Redo { get; }
    public RelayCommand Delete { get; }
    public RelayCommand DeleteOne { get; }
    public RelayCommand Inspect { get; }
    public RelayCommand InspectEntry { get; }
    public RelayCommand Navigate { get; }
    public RelayCommand Back { get; }
    public RelayCommand ClearQuery { get; }
    public RelayCommand FindPrevious { get; }
    public RelayCommand FindNextCommand { get; }
    public RelayCommand OpenEditor { get; }
    public RelayCommand StartDirect { get; }
    public RelayCommand ApplyDirect { get; }
    public RelayCommand CancelDirect { get; }
    public RelayCommand ApplyWeight { get; }
    public RelayCommand OpenPresets { get; }
    public RelayCommand NewPreset { get; }
    public RelayCommand ApplyPreset { get; }
    public RelayCommand CopyPresetNegative { get; }
    public RelayCommand CapturePresetPositive { get; }
    public RelayCommand SavePreset { get; }
    public RelayCommand DeletePreset { get; }
    public MainViewModel(ICatalog catalog, IUserStateStore store, IClipboardService clipboard, IGeneralBrowseProvider? general = null)
    {
        this.catalog = catalog; this.store = store; this.clipboard = clipboard; this.general = general ?? new PendingGeneralBrowseProvider();
        search = new(catalog); Workspace = new(new(catalog));
        var state = store.Load(); if (state != null) { Workspace.Restore(state.Prompt); ui = state.Ui; foreach (var preset in state.Presets ?? []) Presets.Add(preset); }
        query = ui.Query; browse = ui.Browse; workspaceIndex = ui.Workspace; englishChips = ui.EnglishChips; outputProfile = ui.OutputProfile; RestoreScroll = ui.BrowseScroll; BrowseScroll = ui.BrowseScroll;
        Navigation = [new("special", "◆ Special", catalog.Entries.Where(e => e.IsSpecial).SelectMany(e => e.Paths).GroupBy(p => p.GenreId)
            .Select(g => new NavigationNode("special:" + g.Key + ">", g.First().Genre, g.Where(p => p.SubgenreId.Length > 0).DistinctBy(p => p.Key)
                .Select(p => new NavigationNode("special:" + p.Key, p.Subgenre, [])).ToArray())).ToArray()), new("general", "General", this.general.IsPending ? [] : BuildNavigation(this.general.Paths, "general:"))];
        Copy = Normal(_ => Safe(() => { clipboard.Write(English); Status = "✓ コピーしました"; }));
        Import = Normal(_ => Safe(() => { var text = clipboard.Read(); if (string.IsNullOrWhiteSpace(text)) Status = "クリップボードにPrompt文字列がありません"; else Workspace.Replace(text); }));
        New = Normal(_ => Workspace.Replace("")); Recover = Normal(_ => Workspace.Recover(), _ => Workspace.HasRecovery);
        Undo = Ordered(_ => Workspace.Undo(), _ => Workspace.CanUndo); Redo = Ordered(_ => Workspace.Redo(), _ => Workspace.CanRedo);
        Delete = Ordered(_ => Workspace.Delete(Chips.Where(c => c.Selected).Select(c => c.Id)), _ => HasSelection);
        DeleteOne = Normal(p => { if (p is ChipViewModel c) Workspace.Delete([c.Id]); });
        Inspect = Normal(p => { if (p is ChipViewModel c) InspectChip(c); });
        InspectEntry = Normal(p => { if (p is EntryViewModel row) { SelectedEntry = row; DetailsTabIndex = 0; } });
        Navigate = Normal(p => { if (p is NavigationNode n) NavigateTo(n.Key); });
        Back = Normal(_ => { if (back.TryPop(out var key)) { Notify(nameof(CanGoBack)); Back?.Refresh(); NavigateTo(key, false); } }, _ => CanGoBack);
        ClearQuery = Normal(_ => { Query = ""; RefreshResults(); });
        FindPrevious = Normal(_ => FindNext(true), _ => Chips.Any(c => c.Match));
        FindNextCommand = Normal(_ => FindNext(false), _ => Chips.Any(c => c.Match));
        OpenEditor = Normal(_ => { IsOrderedView = true; WorkspaceIndex = 1; UpdateChipLanguage(); });
        StartDirect = Normal(_ => { WorkspaceIndex = 1; UpdateChipLanguage(); DirectText = English; DirectEditing = true; });
        ApplyDirect = new(_ => { if (!DirectEditing) return; Workspace.DirectEdit(DirectText); DirectEditing = false; }, _ => DirectEditing);
        CancelDirect = new(_ => { DirectText = English; DirectEditing = false; }, _ => DirectEditing);
        ApplyWeight = Ordered(_ => { if (WeightVisible && decimal.TryParse(Weight, NumberStyles.Number, CultureInfo.InvariantCulture, out var w)) Workspace.EditWeight(Chips.Single(c => c.Selected).Id, w); else Status = "weightは数値で入力してください。"; });
        OpenPresets = Normal(_ => PresetsRequested?.Invoke());
        NewPreset = Normal(_ => BeginNewPreset());
        ApplyPreset = Normal(p => ApplyPresetToPrompt(p as GenerationPreset), p => p is GenerationPreset);
        CopyPresetNegative = Normal(p => CopyPresetNegativeText(p as GenerationPreset), p => p is GenerationPreset);
        CapturePresetPositive = Normal(_ => PresetPositive = PromptParser.Serialize(Workspace.Items));
        SavePreset = Normal(_ => SavePresetValue());
        DeletePreset = Normal(p => DeletePresetValue(p as GenerationPreset ?? SelectedPreset), p => p is GenerationPreset || SelectedPreset != null);
        Workspace.Changed += OnPromptChanged;
        RefreshChips(); RefreshCategoryGroups(); RefreshResults(); SelectedEntry = Results.FirstOrDefault(e => e.Entry.Id == ui.SelectedEntry);
    }
    private static NavigationNode[] BuildNavigation(IEnumerable<BrowsePath> paths, string prefix) => paths
        .GroupBy(p => p.GenreId).Select(g => new NavigationNode(prefix + g.Key + ">", g.First().Genre,
            g.Where(p => p.SubgenreId.Length > 0).DistinctBy(p => p.Key)
                .Select(p => new NavigationNode(prefix + p.Key, p.Subgenre, [])).ToArray())).ToArray();
    private void Safe(Action action) { try { action(); } catch (Exception e) when (e is System.Runtime.InteropServices.ExternalException or IOException) { Status = "操作できませんでした: " + e.Message; } }
    private RelayCommand Normal(Action<object?> action, Predicate<object?>? enabled = null) => new(p => { if (CanEditPrompt && (enabled?.Invoke(p) ?? true)) action(p); }, p => CanEditPrompt && (enabled?.Invoke(p) ?? true));
    private RelayCommand Ordered(Action<object?> action, Predicate<object?>? enabled = null) => new(p => { if (CanEditOrderedPrompt && (enabled?.Invoke(p) ?? true)) action(p); }, p => CanEditOrderedPrompt && (enabled?.Invoke(p) ?? true));
    private void RefreshCommands()
    {
        foreach (var command in new[] { Copy, Import, New, Recover, Undo, Redo, Delete, DeleteOne, Inspect, InspectEntry, Navigate, Back, ClearQuery, FindPrevious, FindNextCommand, OpenEditor, StartDirect, ApplyDirect, CancelDirect, ApplyWeight, OpenPresets, NewPreset, ApplyPreset, CopyPresetNegative, CapturePresetPositive, SavePreset, DeletePreset }) command.Refresh();
        foreach (var row in Results.Concat(Related)) row.Refresh(); SelectedEntry?.Refresh();
    }
    private IReadOnlyList<EntryViewModel> Rows(IEnumerable<CatalogEntry> entries) => entries.Select(e => new EntryViewModel(e, Workspace, Add, () => CanEditPrompt)).ToArray();
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
    public void Add(CatalogEntry entry) { if (CanEditPrompt) Workspace.Add(entry); }
    private void InspectChip(ChipViewModel chip)
    {
        var entry = catalog.Entries.FirstOrDefault(e => e.Id == chip.Item.CatalogId) ?? catalog.Resolve(chip.Item.StructuredName ?? chip.Item.Surface.Trim());
        if (entry == null) { Query = chip.Item.StructuredName ?? chip.Item.Surface.Trim(); RefreshResults(); return; }
        SelectedEntry = new(entry, Workspace, Add, () => CanEditPrompt); DetailsTabIndex = 0;
    }
    private void OnPromptChanged()
    {
        RefreshChips(); foreach (var row in Results.Concat(Related)) row.Refresh(); SelectedEntry?.Refresh();
        foreach (var command in new[] { Undo, Redo, Recover }) command.Refresh();
        RefreshCategoryGroups(); Notify(nameof(English)); Notify(nameof(Count)); Notify(nameof(HasPrompt)); Notify(nameof(Unresolved)); Persist();
    }
    private void RefreshChips()
    {
        var selection = Chips.Where(c => c.Selected).Select(c => c.Id).ToHashSet(); Chips.Clear();
        foreach (var item in Workspace.Items) Chips.Add(new(item) { Selected = selection.Contains(item.Id), English = EnglishChips && WorkspaceIndex == 0 });
        UpdateMatches(); SelectionChanged();
    }
    private void RefreshCategoryGroups() => CategoryGroups = PromptCategoryProjection.Build(catalog, Workspace.Items);
    public void UpdateChipLanguage() { foreach (var chip in Chips) chip.English = EnglishChips && WorkspaceIndex == 0; }
    public void Select(Guid id, bool ctrl = false, bool shift = false)
    {
        if (!CanEditOrderedPrompt) return;
        int index = Chips.ToList().FindIndex(c => c.Id == id); if (index < 0) return;
        int start = anchor == null ? index : Chips.ToList().FindIndex(c => c.Id == anchor);
        if (shift && start >= 0) { if (!ctrl) foreach (var c in Chips) c.Selected = false; for (int i = Math.Min(start, index); i <= Math.Max(start, index); i++) Chips[i].Selected = true; }
        else if (ctrl || MultiSelect) { Chips[index].Selected = !Chips[index].Selected; anchor = id; }
        else { foreach (var c in Chips) c.Selected = c.Id == id; anchor = id; }
        SelectionChanged();
    }
    public void SelectAll() { if (!CanEditOrderedPrompt) return; foreach (var c in Chips) c.Selected = true; SelectionChanged(); }
    public void ClearSelection() { if (!CanEditOrderedPrompt) return; foreach (var c in Chips) c.Selected = false; anchor = null; SelectionChanged(); }
    public Guid[] BeginDrag(Guid id)
    {
        if (!CanEditOrderedPrompt) return [];
        if (!Chips.Any(c => c.Id == id && c.Selected)) { ClearSelection(); Chips.First(c => c.Id == id).Selected = true; }
        SelectionChanged(); return Chips.Where(c => c.Selected).Select(c => c.Id).ToArray();
    }
    public void Move(Guid[] ids, int gap) { if (CanEditOrderedPrompt) Workspace.Move(ids, gap); }
    private void SelectionChanged()
    {
        Notify(nameof(HasSelection));
        Notify(nameof(SelectionSummary));
        Notify(nameof(WeightVisible));
        Weight = WeightVisible ? Chips.Single(c => c.Selected).Item.Weight?.ToString(CultureInfo.InvariantCulture) ?? "" : "";
        Delete.Refresh();
    }
    private void UpdateMatches()
    {
        foreach (var chip in Chips) chip.Match = Find.Length > 0 && (chip.Item.Display.Contains(Find, StringComparison.OrdinalIgnoreCase) || chip.Item.Surface.Contains(Find, StringComparison.OrdinalIgnoreCase));
        Notify(nameof(FindMatchSummary)); FindPrevious.Refresh(); FindNextCommand.Refresh();
    }
    private Guid? lastMatch;
    public void FindNext(bool previous)
    {
        var matches = Chips.Where(c => c.Match).ToArray(); if (matches.Length == 0) { lastMatch = null; Notify(nameof(FindMatchSummary)); return; }
        int index = Array.FindIndex(matches, c => c.Id == lastMatch); index = (index + (previous ? -1 : 1) + matches.Length) % matches.Length;
        lastMatch = matches[index].Id; Notify(nameof(FindMatchSummary)); ScrollToChip?.Invoke(lastMatch.Value);
    }
    public void SaveUi(UiState value) { ui = value; Persist(); }
    private void BeginNewPreset()
    {
        SelectedPreset = null;
        PresetName = ""; PresetDescription = ""; PresetPositive = ""; PresetNegative = "";
    }
    private void ApplyPresetToPrompt(GenerationPreset? preset)
    {
        if (preset == null) return;
        var parsed = new PromptParser(catalog).Parse(preset.Positive);
        var result = Workspace.AppendPreset(parsed);
        Status = $"{result.Added}件追加 / {result.Skipped}件スキップ";
    }
    private void CopyPresetNegativeText(GenerationPreset? preset)
    {
        if (preset == null) return;
        try { clipboard.Write(preset.Negative); Status = "✓ Negativeをコピーしました"; }
        catch (Exception e) when (e is System.Runtime.InteropServices.ExternalException or IOException) { Status = "操作できませんでした: " + e.Message; }
    }
    private void SavePresetValue()
    {
        var parsed = new PromptParser(catalog).Parse(PresetPositive);
        var saved = new GenerationPreset(SelectedPreset?.Id ?? Guid.NewGuid(), PresetName.Trim(), PresetDescription, PromptOutputFormatter.SerializeCanonical(parsed), PresetNegative);
        var index = SelectedPreset == null ? -1 : Presets.IndexOf(SelectedPreset);
        if (index < 0) Presets.Add(saved); else Presets[index] = saved;
        SelectedPreset = saved;
        Persist(); Status = "プリセットを保存しました";
    }
    private void DeletePresetValue(GenerationPreset? preset)
    {
        if (preset == null || !Presets.Remove(preset)) return;
        Persist(); BeginNewPreset(); Status = "プリセットを削除しました";
    }
    public void Persist()
    {
        ui = ui with { Workspace = WorkspaceIndex, Browse = browse, Query = Query, SelectedEntry = SelectedEntry?.Entry.Id, BrowseScroll = Query.Length == 0 ? BrowseScroll : RestoreScroll, EnglishChips = EnglishChips, OutputProfile = OutputProfile };
        try { store.Save(new(Workspace.Snapshot(), ui, Presets.ToArray())); } catch (Exception e) when (e is IOException or Microsoft.Data.Sqlite.SqliteException) { Status = "自動保存できません: " + e.Message; }
    }
}
