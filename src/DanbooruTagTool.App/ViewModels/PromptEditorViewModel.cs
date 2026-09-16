using System.Collections.ObjectModel;
using System.Globalization;
using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App.ViewModels;

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

public sealed record PromptOutputProfileOption(PromptOutputProfile Value, string Label);

/// <summary>
/// Owns Prompt presentation and editing controls around the unchanged Core
/// PromptWorkspace. Dictionary and persistence are supplied as narrow seams.
/// </summary>
public sealed class PromptEditorViewModel : Observable
{
    private readonly IRuntimeCatalogQuery catalog;
    private readonly PromptWorkspace workspace;
    private readonly IClipboardService clipboard;
    private readonly Action persist;
    private readonly Func<bool> canMutate;
    private readonly Action<string> setStatus;
    private readonly Action<ChipViewModel> inspect;
    private readonly Action presetsRequested;
    private IReadOnlyList<PromptCategoryGroup> categoryGroups = [];
    private string find = "", directText = "", weight = "";
    private bool englishChips, multiSelect, directEditing, categoryView, categoryEnglish;
    private int workspaceIndex;
    private PromptOutputProfile outputProfile = PromptOutputProfile.Canonical;
    private Guid? anchor, lastMatch;

    public ObservableCollection<ChipViewModel> Chips { get; } = [];
    public IReadOnlyList<PromptCategoryGroup> CategoryGroups { get => categoryGroups; private set => Set(ref categoryGroups, value); }
    public PromptWorkspace Workspace => workspace;
    public event Action<Guid>? ScrollToChip;
    public string English => PromptOutputFormatter.Serialize(Workspace.Items, OutputProfile);
    public IReadOnlyList<PromptOutputProfileOption> OutputProfiles { get; } =
        [new(PromptOutputProfile.GenerationFriendly, "生成向け"), new(PromptOutputProfile.Canonical, "原形優先")];
    public PromptOutputProfile OutputProfile { get => outputProfile; set { if (Set(ref outputProfile, value)) { Notify(nameof(English)); persist(); } } }
    public int WorkspaceIndex { get => workspaceIndex; set { if (!DirectEditing && Set(ref workspaceIndex, value)) UpdateChipLanguage(); } }
    public bool EnglishChips { get => englishChips; set { if (Set(ref englishChips, value)) { UpdateChipLanguage(); persist(); } } }
    public bool IsCategoryView { get => categoryView; set { if (Set(ref categoryView, value)) { Notify(nameof(IsOrderedView)); Notify(nameof(CanEditOrderedPrompt)); Notify(nameof(SelectionSummary)); Notify(nameof(WeightVisible)); RefreshCommands(); } } }
    public bool IsOrderedView { get => !IsCategoryView; set { if (value != IsOrderedView) IsCategoryView = !value; } }
    public bool CategoryEnglish { get => categoryEnglish; set => Set(ref categoryEnglish, value); }
    public bool MultiSelect { get => multiSelect; set => Set(ref multiSelect, value); }
    public bool HasSelection => Chips.Any(c => c.Selected);
    public string SelectionSummary => IsCategoryView ? "カテゴリ別表示（読み取り専用）" : HasSelection ? $"{Chips.Count(c => c.Selected)}件選択中" : "選択なし";
    public string Count => $"現在のPrompt · {Chips.Count}件";
    public bool HasPrompt => Chips.Count > 0;
    public string Unresolved => Chips.Count(c => c.Item.Kind == PromptItemKind.Raw) is var n && n > 0 ? $"未解決 {n}" : "";
    public bool CanEditPrompt => !DirectEditing;
    public bool CanEditOrderedPrompt => CanEditPrompt && IsOrderedView;
    public bool DirectEditing { get => directEditing; private set { if (Set(ref directEditing, value)) { Notify(nameof(CanEditPrompt)); Notify(nameof(CanEditOrderedPrompt)); RefreshCommands(); } } }
    public string DirectText { get => directText; set => Set(ref directText, value); }
    public string Weight { get => weight; set => Set(ref weight, value); }
    public bool WeightVisible => IsOrderedView && Chips.Count(c => c.Selected) == 1 && Chips.Single(c => c.Selected).Item.CanEditWeight;
    public string Find { get => find; set { if (Set(ref find, value)) { lastMatch = null; Notify(nameof(HasFindQuery)); UpdateMatches(); FindNext(false); } } }
    public bool HasFindQuery => Find.Length > 0;
    public string FindMatchSummary
    {
        get
        {
            if (!HasFindQuery) return "";
            var matches = Chips.Where(c => c.Match).ToArray(); if (matches.Length == 0) return "0件一致";
            var index = Array.FindIndex(matches, c => c.Id == lastMatch); return $"{matches.Length}件一致 · {(index >= 0 ? index + 1 : 0)}/{matches.Length}";
        }
    }

    public RelayCommand Copy { get; }
    public RelayCommand Import { get; }
    public RelayCommand New { get; }
    public RelayCommand Recover { get; }
    public RelayCommand Undo { get; }
    public RelayCommand Redo { get; }
    public RelayCommand Delete { get; }
    public RelayCommand DeleteOne { get; }
    public RelayCommand Inspect { get; }
    public RelayCommand FindPrevious { get; }
    public RelayCommand FindNextCommand { get; }
    public RelayCommand OpenEditor { get; }
    public RelayCommand StartDirect { get; }
    public RelayCommand ApplyDirect { get; }
    public RelayCommand CancelDirect { get; }
    public RelayCommand ApplyWeight { get; }
    public RelayCommand OpenPresets { get; }

    public PromptEditorViewModel(IRuntimeCatalogQuery catalog, PromptWorkspace workspace, IClipboardService clipboard,
        Action persist, Func<bool> canMutate, Action<string> setStatus, Action<ChipViewModel> inspect, Action presetsRequested)
    {
        this.catalog = catalog; this.workspace = workspace; this.clipboard = clipboard; this.persist = persist; this.canMutate = canMutate; this.setStatus = setStatus; this.inspect = inspect; this.presetsRequested = presetsRequested;
        Copy = Normal(_ => Safe(() => { clipboard.Write(English); setStatus("✓ コピーしました"); }));
        Import = Normal(_ => Safe(() => { var text = clipboard.Read(); if (string.IsNullOrWhiteSpace(text)) setStatus("クリップボードにPrompt文字列がありません"); else Workspace.Replace(text); }));
        New = Normal(_ => Workspace.Replace("")); Recover = Normal(_ => Workspace.Recover(), _ => Workspace.HasRecovery);
        Undo = Ordered(_ => Workspace.Undo(), _ => Workspace.CanUndo); Redo = Ordered(_ => Workspace.Redo(), _ => Workspace.CanRedo);
        Delete = Ordered(_ => Workspace.Delete(Chips.Where(c => c.Selected).Select(c => c.Id)), _ => HasSelection);
        DeleteOne = Normal(p => { if (p is ChipViewModel c) Workspace.Delete([c.Id]); });
        Inspect = Normal(p => { if (p is ChipViewModel c) inspect(c); });
        FindPrevious = Normal(_ => FindNext(true), _ => Chips.Any(c => c.Match)); FindNextCommand = Normal(_ => FindNext(false), _ => Chips.Any(c => c.Match));
        OpenEditor = Normal(_ => { IsOrderedView = true; WorkspaceIndex = 1; UpdateChipLanguage(); });
        StartDirect = Normal(_ => { WorkspaceIndex = 1; UpdateChipLanguage(); DirectText = English; DirectEditing = true; });
        ApplyDirect = new(_ => { if (DirectEditing) { Workspace.DirectEdit(DirectText); DirectEditing = false; } }, _ => DirectEditing);
        CancelDirect = new(_ => { DirectText = English; DirectEditing = false; }, _ => DirectEditing);
        ApplyWeight = Ordered(_ => { if (WeightVisible && decimal.TryParse(Weight, NumberStyles.Number, CultureInfo.InvariantCulture, out var w)) Workspace.EditWeight(Chips.Single(c => c.Selected).Id, w); else setStatus("weightは数値で入力してください。"); });
        OpenPresets = Normal(_ => presetsRequested());
    }

    public void Restore(UiState ui) { workspaceIndex = ui.Workspace; englishChips = ui.EnglishChips; outputProfile = ui.OutputProfile; }
    public void RefreshFromWorkspace()
    {
        var selection = Chips.Where(c => c.Selected).Select(c => c.Id).ToHashSet(); Chips.Clear();
        foreach (var item in Workspace.Items) Chips.Add(new(item) { Selected = selection.Contains(item.Id), English = EnglishChips && WorkspaceIndex == 0 });
        UpdateMatches(); SelectionChanged(); RefreshCategoryGroups(); Notify(nameof(English)); Notify(nameof(Count)); Notify(nameof(HasPrompt)); Notify(nameof(Unresolved));
    }
    public void UpdateChipLanguage() { foreach (var chip in Chips) chip.English = EnglishChips && WorkspaceIndex == 0; }
    public void Select(Guid id, bool ctrl = false, bool shift = false)
    {
        if (!CanEditOrderedPrompt) return; var index = Chips.ToList().FindIndex(c => c.Id == id); if (index < 0) return;
        var start = anchor == null ? index : Chips.ToList().FindIndex(c => c.Id == anchor);
        if (shift && start >= 0) { if (!ctrl) foreach (var c in Chips) c.Selected = false; for (var i = Math.Min(start, index); i <= Math.Max(start, index); i++) Chips[i].Selected = true; }
        else if (ctrl || MultiSelect) { Chips[index].Selected = !Chips[index].Selected; anchor = id; }
        else { foreach (var c in Chips) c.Selected = c.Id == id; anchor = id; }
        SelectionChanged();
    }
    public void SelectAll() { if (!CanEditOrderedPrompt) return; foreach (var c in Chips) c.Selected = true; SelectionChanged(); }
    public void ClearSelection() { if (!CanEditOrderedPrompt) return; foreach (var c in Chips) c.Selected = false; anchor = null; SelectionChanged(); }
    public Guid[] BeginDrag(Guid id)
    {
        if (!CanEditOrderedPrompt) return []; if (!Chips.Any(c => c.Id == id && c.Selected)) { ClearSelection(); Chips.First(c => c.Id == id).Selected = true; }
        SelectionChanged(); return Chips.Where(c => c.Selected).Select(c => c.Id).ToArray();
    }
    public void Move(Guid[] ids, int gap) { if (CanEditOrderedPrompt) Workspace.Move(ids, gap); }
    public void FindNext(bool previous)
    {
        var matches = Chips.Where(c => c.Match).ToArray(); if (matches.Length == 0) { lastMatch = null; Notify(nameof(FindMatchSummary)); return; }
        var index = Array.FindIndex(matches, c => c.Id == lastMatch); index = (index + (previous ? -1 : 1) + matches.Length) % matches.Length; lastMatch = matches[index].Id; Notify(nameof(FindMatchSummary)); ScrollToChip?.Invoke(lastMatch.Value);
    }
    private void RefreshCategoryGroups() => CategoryGroups = PromptCategoryProjection.Build(catalog, Workspace.Items);
    private void SelectionChanged()
    {
        Notify(nameof(HasSelection)); Notify(nameof(SelectionSummary)); Notify(nameof(WeightVisible));
        Weight = WeightVisible ? Chips.Single(c => c.Selected).Item.Weight?.ToString(CultureInfo.InvariantCulture) ?? "" : ""; Delete.Refresh();
    }
    private void UpdateMatches()
    {
        foreach (var chip in Chips) chip.Match = Find.Length > 0 && (chip.Item.Display.Contains(Find, StringComparison.OrdinalIgnoreCase) || chip.Item.Surface.Contains(Find, StringComparison.OrdinalIgnoreCase));
        Notify(nameof(FindMatchSummary)); FindPrevious.Refresh(); FindNextCommand.Refresh();
    }
    private void RefreshCommands()
    {
        foreach (var command in new[] { Copy, Import, New, Recover, Undo, Redo, Delete, DeleteOne, Inspect, FindPrevious, FindNextCommand, OpenEditor, StartDirect, ApplyDirect, CancelDirect, ApplyWeight, OpenPresets }) command.Refresh();
    }
    private RelayCommand Normal(Action<object?> action, Predicate<object?>? enabled = null) => new(p => { if (CanEditPrompt && (enabled?.Invoke(p) ?? true)) action(p); }, p => CanEditPrompt && (enabled?.Invoke(p) ?? true));
    private RelayCommand Ordered(Action<object?> action, Predicate<object?>? enabled = null) => new(p => { if (CanEditOrderedPrompt && (enabled?.Invoke(p) ?? true)) action(p); }, p => CanEditOrderedPrompt && (enabled?.Invoke(p) ?? true));
    private void Safe(Action action) { try { action(); } catch (Exception e) when (e is System.Runtime.InteropServices.ExternalException or IOException) { setStatus("操作できませんでした: " + e.Message); } }
}
