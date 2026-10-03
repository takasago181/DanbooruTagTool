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
    public PromptWorkspace NegativeWorkspace { get; }
    public PromptEditorViewModel Negative { get; }
    public PromptIntelligenceViewModel Intelligence { get; }
    public DictionaryWorkspaceViewModel Dictionary { get; }
    public PromptEditorViewModel Prompt { get; }
    public GenerationPresetsViewModel PresetEditor { get; }
    public GenerationImportViewModel GenerationImport { get; }
    public GenerationLibraryViewModel? GenerationLibrary { get; }
    public LoraLibraryViewModel? LoraLibrary { get; }
    public ForgeViewModel Forge { get; }
    public CreateViewModel Create { get; }
    public ExperimentLabViewModel? Experiments { get; }
    public RegionComposerViewModel? Regions { get; }
    public TemplateViewModel? Templates { get; }
    public ImageTagAnalysisViewModel? ImageTagAnalysis { get; }
    public PersonalRulesViewModel? PersonalRules { get; }
    private bool presetManagementOpen;
    public bool PresetManagementOpen { get => presetManagementOpen; set { Set(ref presetManagementOpen, value); Notify(nameof(CreateEditingAvailable)); Create.Refresh(); } }
    public bool CreateEditingAvailable => CanEditPrompt && !PresetManagementOpen && !Forge.RecipeBusy;
    // Keep persisted legacy indices: dictionary=0, Create=1, images=2, LoRA=3.
    // No schema/index migration; only the shell presentation changes.
    public int ShellWorkspaceIndex
    {
        get => WorkspaceIndex == 0 ? 1 : WorkspaceIndex == 1 ? 0 : 2;
        set => WorkspaceIndex = value == 0 ? 1 : value == 1 ? 0 : (LibrarySubtypeIndex == 1 ? 3 : 2);
    }
    private int librarySubtypeIndex;
    public int LibrarySubtypeIndex
    {
        get => WorkspaceIndex == 3 ? 1 : WorkspaceIndex == 2 ? 0 : librarySubtypeIndex;
        set { librarySubtypeIndex = value == 1 ? 1 : 0; if (ShellWorkspaceIndex == 2) WorkspaceIndex = librarySubtypeIndex + 2; Notify(nameof(LibrarySubtypeIndex)); }
    }
    private int createPageIndex;
    public int CreatePageIndex { get => createPageIndex; set { if (Set(ref createPageIndex, value)) { if (value < 2) Intelligence.ActiveSide = value; Notify(nameof(CreateComposerVisible)); } } }

    public bool CreateComposerVisible => CreatePageIndex < 4;
    public UserStateCoordinator UserState { get; }
    private string status = "";
    public string Status { get => status; set => Set(ref status, value); }
    public UiState Ui => UserState.Ui;
    public event Action? PresetsRequested;
    public event Action? ForgeSettingsRequested;
    public event Action? GenerationImportRequested;
    public event Action? ResultsRestored { add => Dictionary.ResultsRestored += value; remove => Dictionary.ResultsRestored -= value; }
    public event Action<Guid>? ScrollToChip { add => Prompt.ScrollToChip += value; remove => Prompt.ScrollToChip -= value; }

    public MainViewModel(ICatalog catalog, IUserStateStore store, IClipboardService clipboard,
        IGeneralBrowseProvider? general = null, IForgeBridgeClient? forgeBridge = null, SpecialBrowseV2Index? specialBrowse = null, PortablePaths? paths = null, IForgeGenerationApiClient? generationApi = null)
    {
        var runtime = RuntimeCatalogIndex.Create(catalog);
        Workspace = new(new PromptParser(runtime));
        NegativeWorkspace = new(new PromptParser(runtime));
        UserState = new(store);
        var state = UserState.Load();
        if (state != null) Workspace.Restore(state.Prompt);
        if (state?.Negative is { } negative) NegativeWorkspace.Restore(negative);
        var canMutate = () => !(Prompt?.DirectEditing ?? false) && !(Negative?.DirectEditing ?? false) && !(Forge?.RecipeBusy ?? false);
        Prompt = new(runtime, Workspace, clipboard, Persist, canMutate, message => Status = message,
            chip => Dictionary?.InspectChip(chip), () => PresetsRequested?.Invoke()) { SideLabel = "Positive" };
        Negative = new(runtime, NegativeWorkspace, clipboard, Persist, canMutate, message => Status = message,
            chip => Dictionary?.InspectChip(chip), () => PresetsRequested?.Invoke()) { SideLabel = "Negative" };
        Dictionary = new(runtime, Workspace, general ?? new PendingGeneralBrowseProvider(), Persist, canMutate, specialBrowse);
        Forge = new(forgeBridge ?? new ForgeBridgeClient(), Persist, canMutate, () => Prompt?.English ?? "", message => Status = message, () => ForgeSettingsRequested?.Invoke(), paths is null ? null : Path.Combine(paths.Root, "UserData", "ForgeResults"), generationApi);
        Forge.CurrentNegative = () => Negative.English;
        Create = new(this);
        Intelligence = new(Workspace, NegativeWorkspace, () => Forge.ForgeUrl, positiveText: () => Prompt.English, negativeText: () => Negative.English);
        Intelligence.PropertyChanged += (_, e) => { if (e.PropertyName == nameof(Intelligence.ActiveSide) && CreatePageIndex < 2) CreatePageIndex = Intelligence.ActiveSide; };
        PresetEditor = new(runtime, Workspace, clipboard, Persist, canMutate, message => Status = message);
        PresetEditor.NegativeWorkspace = NegativeWorkspace;
        GenerationImport = new(Workspace, clipboard, message => Status = message, snapshot =>
        {
            PresetEditor.BeginNewPresetFromSnapshot(snapshot);
            PresetsRequested?.Invoke();
        });
        GenerationImport.NegativeWorkspace = NegativeWorkspace;
        GenerationImport.CanMutate = canMutate;
        if (paths is not null) GenerationLibrary = new(paths, Workspace, snapshot =>
        {
            PresetEditor.BeginNewPresetFromSnapshot(snapshot);
            PresetsRequested?.Invoke();
        }, Forge, canMutate);
        if (GenerationLibrary is not null && paths is not null) { ImageTagAnalysis = new(this, paths); GenerationLibrary.TagAnalysis = ImageTagAnalysis; }
        if (GenerationLibrary is not null) Forge.IndexRecipeResult = GenerationLibrary.IndexRecipeResultAsync;
        if (paths is not null) { Experiments = new(this, paths); Regions = new(this, paths); Templates = new(this, paths); Forge.RegionalWorkflowActive = () => Regions.RestoredRegional is not null; }
        if (GenerationLibrary is not null)
        {
            GenerationLibrary.NegativeWorkspace = NegativeWorkspace;
            GenerationLibrary.UseInCreate = (snapshot, filename) => Create.LoadImage(snapshot, "画像「" + filename + "」");
        }
        GenerationImport.UseInCreate = snapshot => Create.LoadImage(snapshot, "読み込んだPNG");
        if (paths is not null) LoraLibrary = new(paths, Workspace, new PromptParser(runtime), clipboard, canMutate, preset =>
        {
            PresetEditor.BeginNewPreset();
            PresetEditor.PresetPositive = preset.Positive; PresetEditor.PresetNegative = preset.Negative;
            PresetEditor.PresetName = preset.Name; PresetEditor.PresetDescription = preset.Description;
            PresetsRequested?.Invoke();
        });
        if (LoraLibrary is not null) LoraLibrary.NegativeWorkspace = NegativeWorkspace;
        if (paths is not null) PersonalRules = new(this, runtime, paths);
        Prompt.Restore(UserState.Ui); Dictionary.Restore(UserState.Ui); Forge.Restore(UserState.Ui); PresetEditor.Restore(state);

        WireNotifications();
        Workspace.Changed += OnPromptChanged;
        NegativeWorkspace.Changed += () => { Negative.RefreshFromWorkspace(); Intelligence.Refresh(); Persist(); };
        Negative.PropertyChanged += (_, e) => { if (e.PropertyName == nameof(Negative.DirectEditing)) { Prompt.RefreshEditAvailability(); GenerationLibrary?.RefreshCommands(); Notify(nameof(DirectEditing)); Notify(nameof(CanEditPrompt)); } if (e.PropertyName == nameof(Negative.OutputProfile)) Intelligence.Refresh(); };
        Negative.RefreshFromWorkspace(); Intelligence.Refresh();
        Prompt.RefreshFromWorkspace(); Dictionary.RefreshResults();
        if (UserState.Ui.SelectedEntry is { } selected) Dictionary.SelectedEntry = Dictionary.Results.FirstOrDefault(row => row.Entry.Id == selected);
    }

    private void WireNotifications()
    {
        Prompt.PropertyChanged += (_, e) => { Notify(e.PropertyName);
            if (e.PropertyName == nameof(Prompt.WorkspaceIndex)) { if (WorkspaceIndex >= 2) librarySubtypeIndex = WorkspaceIndex - 2; Notify(nameof(ShellWorkspaceIndex)); Notify(nameof(LibrarySubtypeIndex)); } if (e.PropertyName == nameof(Prompt.OutputProfile)) Intelligence.Refresh(); if (e.PropertyName == nameof(Prompt.DirectEditing)) { Negative.RefreshEditAvailability(); GenerationLibrary?.RefreshCommands(); } };
        Dictionary.PropertyChanged += (_, e) => Notify(e.PropertyName);
        Forge.PropertyChanged += (_, e) =>
        {
            Notify(e.PropertyName); Notify(nameof(CreateEditingAvailable));
            if (e.PropertyName == nameof(Forge.RecipeBusy))
            { Prompt.RefreshEditAvailability(); Negative.RefreshEditAvailability(); LoraLibrary?.RefreshEditAvailability(); GenerationLibrary?.RefreshCommands(); Notify(nameof(CanEditPrompt)); }
        };
        PresetEditor.PropertyChanged += (_, e) => Notify(e.PropertyName);
    }
    private void OnPromptChanged() { Prompt.RefreshFromWorkspace(); Dictionary.RefreshPromptState(); GenerationLibrary?.RefreshCommands(); Intelligence.Refresh(); Persist(); }
    public void RefreshResults() => Dictionary.RefreshResults();
    public bool ImportGenerationPng(string path)
    {
        try
        {
            GenerationImport.Load(ForgePngGenerationMetadata.Read(path));
            Status = "✓ 生成PNGの情報を読み込みました";
            GenerationImportRequested?.Invoke();
            return true;
        }
        catch (GenerationMetadataException e)
        {
            Status = e.Message;
            return false;
        }
    }
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
    public void Persist() => TryPersist();
    public bool TryPersist()
    {
        try { UserState.Persist(Workspace, Dictionary, Prompt, PresetEditor, Forge, NegativeWorkspace); Notify(nameof(Ui)); return true; }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or Microsoft.Data.Sqlite.SqliteException) { Status = "自動保存できません: " + e.Message; return false; }
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
    public string BrowseLabel => Dictionary.BrowseLabel; public string Pending => Dictionary.Pending; public string Detail => Dictionary.Detail; public string ResultSummary => Dictionary.ResultSummary;
    public IReadOnlyList<NavigationNode> Navigation => Dictionary.Navigation;
    public RelayCommand InspectEntry => Dictionary.InspectEntry; public RelayCommand Navigate => Dictionary.Navigate; public RelayCommand Back => Dictionary.Back; public RelayCommand ClearQuery => Dictionary.ClearQuery;
    public ObservableCollection<ChipViewModel> Chips => Prompt.Chips; public IReadOnlyList<PromptCategoryGroup> CategoryGroups => Prompt.CategoryGroups; public string English => Prompt.English; public IReadOnlyList<PromptOutputProfileOption> OutputProfiles => Prompt.OutputProfiles;
    public PromptOutputProfile OutputProfile { get => Prompt.OutputProfile; set => Prompt.OutputProfile = value; }
    public int WorkspaceIndex { get => Prompt.WorkspaceIndex; set => Prompt.WorkspaceIndex = value; }
    public bool EnglishChips { get => Prompt.EnglishChips; set => Prompt.EnglishChips = value; }
    public bool IsCategoryView { get => Prompt.IsCategoryView; set => Prompt.IsCategoryView = value; } public bool IsOrderedView { get => Prompt.IsOrderedView; set => Prompt.IsOrderedView = value; }
    public bool CategoryEnglish { get => Prompt.CategoryEnglish; set => Prompt.CategoryEnglish = value; } public bool MultiSelect { get => Prompt.MultiSelect; set => Prompt.MultiSelect = value; }
    public bool HasSelection => Prompt.HasSelection; public string SelectionSummary => Prompt.SelectionSummary; public string Count => Prompt.Count; public bool HasPrompt => Prompt.HasPrompt; public string Unresolved => Prompt.Unresolved;
    public bool CanEditPrompt => Prompt.CanEditPrompt && Negative.CanEditPrompt; public bool CanEditOrderedPrompt => Prompt.CanEditOrderedPrompt; public bool DirectEditing => Prompt.DirectEditing || Negative.DirectEditing;
    public string DirectText { get => Prompt.DirectText; set => Prompt.DirectText = value; } public string Weight { get => Prompt.Weight; set => Prompt.Weight = value; } public bool WeightVisible => Prompt.WeightVisible;
    public string Find { get => Prompt.Find; set => Prompt.Find = value; } public bool HasFindQuery => Prompt.HasFindQuery; public string FindMatchSummary => Prompt.FindMatchSummary;
    public RelayCommand Copy => Prompt.Copy; public RelayCommand Import => Prompt.Import; public RelayCommand New => Prompt.New; public RelayCommand Recover => Prompt.Recover; public RelayCommand Undo => Prompt.Undo; public RelayCommand Redo => Prompt.Redo; public RelayCommand Delete => Prompt.Delete; public RelayCommand DeleteOne => Prompt.DeleteOne; public RelayCommand Inspect => Prompt.Inspect; public RelayCommand FindPrevious => Prompt.FindPrevious; public RelayCommand FindNextCommand => Prompt.FindNextCommand; public RelayCommand OpenEditor => Prompt.OpenEditor; public RelayCommand StartDirect => Prompt.StartDirect; public RelayCommand ApplyDirect => Prompt.ApplyDirect; public RelayCommand CancelDirect => Prompt.CancelDirect; public RelayCommand ApplyWeight => Prompt.ApplyWeight;
    public ObservableCollection<GenerationPreset> Presets => PresetEditor.Presets; public GenerationPreset? SelectedPreset { get => PresetEditor.SelectedPreset; set => PresetEditor.SelectedPreset = value; }
    public string PresetName { get => PresetEditor.PresetName; set => PresetEditor.PresetName = value; } public string PresetDescription { get => PresetEditor.PresetDescription; set => PresetEditor.PresetDescription = value; } public string PresetPositive { get => PresetEditor.PresetPositive; set => PresetEditor.PresetPositive = value; } public string PresetNegative { get => PresetEditor.PresetNegative; set => PresetEditor.PresetNegative = value; }
    public string PresetModelHash { get => PresetEditor.PresetModelHash; set => PresetEditor.PresetModelHash = value; }
    public string PresetModel { get => PresetEditor.PresetModel; set => PresetEditor.PresetModel = value; } public string PresetSeed { get => PresetEditor.PresetSeed; set => PresetEditor.PresetSeed = value; } public string PresetSteps { get => PresetEditor.PresetSteps; set => PresetEditor.PresetSteps = value; } public string PresetSampler { get => PresetEditor.PresetSampler; set => PresetEditor.PresetSampler = value; } public string PresetScheduler { get => PresetEditor.PresetScheduler; set => PresetEditor.PresetScheduler = value; } public string PresetCfg { get => PresetEditor.PresetCfg; set => PresetEditor.PresetCfg = value; } public string PresetWidth { get => PresetEditor.PresetWidth; set => PresetEditor.PresetWidth = value; } public string PresetHeight { get => PresetEditor.PresetHeight; set => PresetEditor.PresetHeight = value; }
    public RelayCommand OpenPresets => Prompt.OpenPresets; public RelayCommand NewPreset => PresetEditor.NewPreset; public RelayCommand ApplyPreset => PresetEditor.ApplyPreset; public RelayCommand CopyPresetNegative => PresetEditor.CopyPresetNegative; public RelayCommand CapturePresetPositive => PresetEditor.CapturePresetPositive; public RelayCommand SavePreset => PresetEditor.SavePreset; public RelayCommand DeletePreset => PresetEditor.DeletePreset;
    public string ForgeUrl { get => Forge.ForgeUrl; set => Forge.ForgeUrl = value; } public string ForgeExtensionPath { get => Forge.ForgeExtensionPath; set => Forge.ForgeExtensionPath = value; }
    public RelayCommand OpenForgeSettings => Forge.OpenForgeSettings; public RelayCommand SaveForgeSettings => Forge.SaveForgeSettings; public AsyncRelayCommand SendToForge => Forge.SendToForge; public AsyncRelayCommand GenerateInForge => Forge.GenerateInForge; public AsyncRelayCommand SendPresetToForge => Forge.SendPresetToForge;
    public Task SendToForgeAsync(GenerationPreset? preset = null, CancellationToken cancellationToken = default) => Forge.SendAsync(preset, cancellationToken);
    public Task GenerateInForgeAsync(GenerationPreset? preset = null, CancellationToken cancellationToken = default) => Forge.GenerateAsync(preset, cancellationToken);
}
