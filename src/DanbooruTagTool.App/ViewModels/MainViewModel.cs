using System.Collections.ObjectModel;
using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App.ViewModels;

/// <summary>
/// Application shell/composition root. Feature behavior lives in child view
/// models; forwarding members are retained for the unsplit MainWindow/dialog
/// and public regression-test surface until the XAML split in Phase 3.
/// </summary>
public sealed class MainViewModel : Observable
{
    public PromptWorkspace Workspace { get; }
    public DictionaryWorkspaceViewModel Dictionary { get; }
    public PromptEditorViewModel Prompt { get; }
    public GenerationPresetsViewModel PresetEditor { get; }
    public ForgeViewModel Forge { get; }
    public UserStateCoordinator UserState { get; }
    private string status = "";
    public string Status { get => status; set => Set(ref status, value); }
    public UiState Ui => UserState.Ui;
    public event Action? PresetsRequested;
    public event Action? ForgeSettingsRequested;
    public event Action? ResultsRestored { add => Dictionary.ResultsRestored += value; remove => Dictionary.ResultsRestored -= value; }
    public event Action<Guid>? ScrollToChip { add => Prompt.ScrollToChip += value; remove => Prompt.ScrollToChip -= value; }

    public MainViewModel(ICatalog catalog, IUserStateStore store, IClipboardService clipboard,
        IGeneralBrowseProvider? general = null, IForgeBridgeClient? forgeBridge = null, SpecialBrowseV2Index? specialBrowse = null)
    {
        var runtime = RuntimeCatalogIndex.Create(catalog);
        Workspace = new(new PromptParser(runtime));
        UserState = new(store);
        var state = UserState.Load();
        if (state != null) Workspace.Restore(state.Prompt);
        var canMutate = () => Prompt?.CanEditPrompt ?? true;
        Prompt = new(runtime, Workspace, clipboard, Persist, canMutate, message => Status = message,
            chip => Dictionary?.InspectChip(chip), () => PresetsRequested?.Invoke());
        Dictionary = new(runtime, Workspace, general ?? new PendingGeneralBrowseProvider(), Persist, canMutate, specialBrowse);
        Forge = new(forgeBridge ?? new ForgeBridgeClient(), Persist, canMutate, () => Prompt?.English ?? "", message => Status = message, () => ForgeSettingsRequested?.Invoke());
        PresetEditor = new(runtime, Workspace, clipboard, Persist, canMutate, message => Status = message);
        Prompt.Restore(UserState.Ui); Dictionary.Restore(UserState.Ui); Forge.Restore(UserState.Ui); PresetEditor.Restore(state);
        WireNotifications();
        Workspace.Changed += OnPromptChanged;
        Prompt.RefreshFromWorkspace(); Dictionary.RefreshResults();
        if (UserState.Ui.SelectedEntry is { } selected) Dictionary.SelectedEntry = Dictionary.Results.FirstOrDefault(row => row.Entry.Id == selected);
    }

    private void WireNotifications()
    {
        Prompt.PropertyChanged += (_, e) => Notify(e.PropertyName);
        Dictionary.PropertyChanged += (_, e) => Notify(e.PropertyName);
        Forge.PropertyChanged += (_, e) => Notify(e.PropertyName);
        PresetEditor.PropertyChanged += (_, e) => Notify(e.PropertyName);
    }
    private void OnPromptChanged() { Prompt.RefreshFromWorkspace(); Dictionary.RefreshPromptState(); Persist(); }
    public void RefreshResults() => Dictionary.RefreshResults();
    public void SetDictionarySurfaceWidth(double availableWidth) => Dictionary.SetSurfaceWidth(availableWidth);
    public void MoveResultSelection(int offset) => Dictionary.MoveResultSelection(offset);
    public void SelectResultBoundary(bool last) => Dictionary.SelectResultBoundary(last);
    public void NavigateTo(string key, bool remember = true) => Dictionary.NavigateTo(key, remember);
    public void Add(CatalogEntry entry) => Dictionary.Add(entry);
    public void InspectChip(ChipViewModel chip) => Dictionary.InspectChip(chip);
    public void Select(Guid id, bool ctrl = false, bool shift = false) => Prompt.Select(id, ctrl, shift);
    public void SelectAll() => Prompt.SelectAll();
    public void ClearSelection() => Prompt.ClearSelection();
    public Guid[] BeginDrag(Guid id) => Prompt.BeginDrag(id);
    public void Move(Guid[] ids, int gap) => Prompt.Move(ids, gap);
    public void FindNext(bool previous) => Prompt.FindNext(previous);
    public void UpdateChipLanguage() => Prompt.UpdateChipLanguage();
    public void SaveUi(UiState value) { UserState.SaveUi(value); Persist(); }
    public void Persist()
    {
        try { UserState.Persist(Workspace, Dictionary, Prompt, PresetEditor, Forge); Notify(nameof(Ui)); }
        catch (Exception e) when (e is IOException or Microsoft.Data.Sqlite.SqliteException) { Status = "自動保存できません: " + e.Message; }
    }

    // Phase 3 will move MainWindow bindings to Dictionary/Prompt/PresetEditor/Forge.
    public IReadOnlyList<EntryViewModel> Results => Dictionary.Results;
    public IReadOnlyList<DictionaryResultRow> DictionaryRows => Dictionary.DictionaryRows;
    public int DictionaryColumnCount => Dictionary.DictionaryColumnCount;
    public IReadOnlyList<EntryViewModel> Related => Dictionary.Related;
    public EntryViewModel? SelectedEntry { get => Dictionary.SelectedEntry; set => Dictionary.SelectedEntry = value; }
    public double DictionaryCardWidth { get => Dictionary.DictionaryCardWidth; set => Dictionary.DictionaryCardWidth = value; }
    public double BrowseScroll { get => Dictionary.BrowseScroll; set => Dictionary.BrowseScroll = value; }
    public double RestoreScroll => Dictionary.RestoreScroll;
    public string Query { get => Dictionary.Query; set => Dictionary.Query = value; }
    public string BrowseKey => Dictionary.BrowseKey;
    public int SortIndex { get => Dictionary.SortIndex; set => Dictionary.SortIndex = value; }
    public int DetailsTabIndex { get => Dictionary.DetailsTabIndex; set => Dictionary.DetailsTabIndex = value; }
    public bool IsSearching => Dictionary.IsSearching; public bool CanBrowseSort => Dictionary.CanBrowseSort; public bool CanGoBack => Dictionary.CanGoBack;
    public bool HasSpecialFacets => Dictionary.HasSpecialFacets; public bool ShowSpecialFacetBar => Dictionary.ShowSpecialFacetBar; public bool ShowSpecialKindOptions => Dictionary.ShowSpecialKindOptions;
    public string SpecialFacetSummary => Dictionary.SpecialFacetSummary; public string BrowseLabel => Dictionary.BrowseLabel; public string Pending => Dictionary.Pending; public string Detail => Dictionary.Detail; public string ResultSummary => Dictionary.ResultSummary;
    public IReadOnlyList<NavigationNode> Navigation => Dictionary.Navigation;
    public ObservableCollection<SpecialBrowseFacetOptionViewModel> SpecialKindOptions => Dictionary.SpecialKindOptions;
    public ObservableCollection<SpecialBrowseFacetOptionViewModel> SpecialBodyOptions => Dictionary.SpecialBodyOptions;
    public ObservableCollection<SpecialBrowseFacetOptionViewModel> SpecialThemeOptions => Dictionary.SpecialThemeOptions;
    public RelayCommand InspectEntry => Dictionary.InspectEntry; public RelayCommand Navigate => Dictionary.Navigate; public RelayCommand Back => Dictionary.Back; public RelayCommand ClearQuery => Dictionary.ClearQuery; public RelayCommand ToggleSpecialFacet => Dictionary.ToggleSpecialFacet; public RelayCommand UndoSpecialFacet => Dictionary.UndoSpecialFacet; public RelayCommand ClearSpecialFacets => Dictionary.ClearSpecialFacets;
    public ObservableCollection<ChipViewModel> Chips => Prompt.Chips; public IReadOnlyList<PromptCategoryGroup> CategoryGroups => Prompt.CategoryGroups; public string English => Prompt.English; public IReadOnlyList<PromptOutputProfileOption> OutputProfiles => Prompt.OutputProfiles;
    public PromptOutputProfile OutputProfile { get => Prompt.OutputProfile; set => Prompt.OutputProfile = value; }
    public int WorkspaceIndex { get => Prompt.WorkspaceIndex; set => Prompt.WorkspaceIndex = value; }
    public bool EnglishChips { get => Prompt.EnglishChips; set => Prompt.EnglishChips = value; }
    public bool IsCategoryView { get => Prompt.IsCategoryView; set => Prompt.IsCategoryView = value; } public bool IsOrderedView { get => Prompt.IsOrderedView; set => Prompt.IsOrderedView = value; }
    public bool CategoryEnglish { get => Prompt.CategoryEnglish; set => Prompt.CategoryEnglish = value; } public bool MultiSelect { get => Prompt.MultiSelect; set => Prompt.MultiSelect = value; }
    public bool HasSelection => Prompt.HasSelection; public string SelectionSummary => Prompt.SelectionSummary; public string Count => Prompt.Count; public bool HasPrompt => Prompt.HasPrompt; public string Unresolved => Prompt.Unresolved;
    public bool CanEditPrompt => Prompt.CanEditPrompt; public bool CanEditOrderedPrompt => Prompt.CanEditOrderedPrompt; public bool DirectEditing => Prompt.DirectEditing;
    public string DirectText { get => Prompt.DirectText; set => Prompt.DirectText = value; } public string Weight { get => Prompt.Weight; set => Prompt.Weight = value; } public bool WeightVisible => Prompt.WeightVisible;
    public string Find { get => Prompt.Find; set => Prompt.Find = value; } public bool HasFindQuery => Prompt.HasFindQuery; public string FindMatchSummary => Prompt.FindMatchSummary;
    public RelayCommand Copy => Prompt.Copy; public RelayCommand Import => Prompt.Import; public RelayCommand New => Prompt.New; public RelayCommand Recover => Prompt.Recover; public RelayCommand Undo => Prompt.Undo; public RelayCommand Redo => Prompt.Redo; public RelayCommand Delete => Prompt.Delete; public RelayCommand DeleteOne => Prompt.DeleteOne; public RelayCommand Inspect => Prompt.Inspect; public RelayCommand FindPrevious => Prompt.FindPrevious; public RelayCommand FindNextCommand => Prompt.FindNextCommand; public RelayCommand OpenEditor => Prompt.OpenEditor; public RelayCommand StartDirect => Prompt.StartDirect; public RelayCommand ApplyDirect => Prompt.ApplyDirect; public RelayCommand CancelDirect => Prompt.CancelDirect; public RelayCommand ApplyWeight => Prompt.ApplyWeight;
    public ObservableCollection<GenerationPreset> Presets => PresetEditor.Presets; public GenerationPreset? SelectedPreset { get => PresetEditor.SelectedPreset; set => PresetEditor.SelectedPreset = value; }
    public string PresetName { get => PresetEditor.PresetName; set => PresetEditor.PresetName = value; } public string PresetDescription { get => PresetEditor.PresetDescription; set => PresetEditor.PresetDescription = value; } public string PresetPositive { get => PresetEditor.PresetPositive; set => PresetEditor.PresetPositive = value; } public string PresetNegative { get => PresetEditor.PresetNegative; set => PresetEditor.PresetNegative = value; }
    public RelayCommand OpenPresets => Prompt.OpenPresets; public RelayCommand NewPreset => PresetEditor.NewPreset; public RelayCommand ApplyPreset => PresetEditor.ApplyPreset; public RelayCommand CopyPresetNegative => PresetEditor.CopyPresetNegative; public RelayCommand CapturePresetPositive => PresetEditor.CapturePresetPositive; public RelayCommand SavePreset => PresetEditor.SavePreset; public RelayCommand DeletePreset => PresetEditor.DeletePreset;
    public string ForgeUrl { get => Forge.ForgeUrl; set => Forge.ForgeUrl = value; } public string ForgeExtensionPath { get => Forge.ForgeExtensionPath; set => Forge.ForgeExtensionPath = value; }
    public RelayCommand OpenForgeSettings => Forge.OpenForgeSettings; public RelayCommand SaveForgeSettings => Forge.SaveForgeSettings; public AsyncRelayCommand SendToForge => Forge.SendToForge; public AsyncRelayCommand GenerateInForge => Forge.GenerateInForge; public AsyncRelayCommand SendPresetToForge => Forge.SendPresetToForge;
    public Task SendToForgeAsync(GenerationPreset? preset = null, CancellationToken cancellationToken = default) => Forge.SendAsync(preset, cancellationToken);
    public Task GenerateInForgeAsync(GenerationPreset? preset = null, CancellationToken cancellationToken = default) => Forge.GenerateAsync(preset, cancellationToken);
}
