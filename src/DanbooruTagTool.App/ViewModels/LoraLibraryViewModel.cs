using System.Collections.ObjectModel;
using System.Globalization;
using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App.ViewModels;

public sealed class LoraTriggerEditor : Observable
{
    private bool enabled; private string text;
    public bool Enabled { get => enabled; set => Set(ref enabled, value); }
    public string Text { get => text; set => Set(ref text, value); }
    public string Source { get; }
    public LoraTriggerEditor(LoraTrigger trigger) { enabled = trigger.Enabled; text = trigger.Text; Source = trigger.Source; }
}
public sealed class LoraLibraryViewModel(PortablePaths paths, PromptWorkspace workspace, PromptParser parser, IClipboardService clipboard,
    Func<bool> canMutate, Action<GenerationPreset> createPreset) : Observable
{
    private LoraLibraryStore? store; private bool busy, loaded; private int offset;
    private readonly Dictionary<string, LoraUserMetadata> drafts = new();
    private readonly Dictionary<string, string> draftWeights = new();
    private LoraAsset? selected; private string status = "明示スキャンでlocal LoRAを登録します。通常起動にnetwork/hash処理はありません。";
    public ObservableCollection<LoraAsset> Assets { get; } = [];
    public ObservableCollection<string> Roots { get; } = [];
    public ObservableCollection<LoraTriggerEditor> Triggers { get; } = [];
    public string Search { get; set; } = "";
    public PromptWorkspace? NegativeWorkspace { get; set; }
    public bool FavoriteOnly { get; set; }
    public bool Busy { get => busy; private set { Set(ref busy, value); Notify(nameof(CanEdit)); } }
    public bool CanEdit => !Busy && canMutate();
    public string Status { get => status; private set => Set(ref status, value); }
    public string Category { get; set; } = "Other";
    public bool Favorite { get; set; }
    public string Note { get; set; } = "";
    public string Weight { get; set; } = "1";
    public string Links { get; set; } = "";
    public string BaseModel { get; set; } = "";
    public bool OverrideBaseModel { get; set; }
    public bool OverrideTriggers { get; set; }
    public string PreviewOverride { get; set; } = "";
    public string PositiveAdditions { get; set; } = "";
    public string NegativeAdditions { get; set; } = "";
    public LoraAsset? Selected
    {
        get => selected;
        set
        {
            if (ReferenceEquals(selected, value)) return;
            if (selected is not null) CaptureDraft(selected);
            Set(ref selected, value); if (value is null) return;
            var u = drafts.GetValueOrDefault(value.Sha256) ?? value.User; Category = u.Category; Favorite = u.Favorite; Note = u.Note; Weight = u.PreferredWeight.ToString(CultureInfo.InvariantCulture);
            if (draftWeights.TryGetValue(value.Sha256, out var draftWeight)) Weight = draftWeight;
            Links = string.Join('\n', u.Links ?? []); BaseModel = u.BaseModel ?? value.Facts.BaseModel; OverrideBaseModel = u.BaseModel is not null; OverrideTriggers = u.Triggers is not null;
            PreviewOverride = u.Preview ?? ""; PositiveAdditions = u.Recipe?.Positive ?? ""; NegativeAdditions = u.Recipe?.Negative ?? "";
            Triggers.Clear(); foreach (var t in u.Triggers ?? value.Facts.Triggers) { var editor = new LoraTriggerEditor(t); editor.PropertyChanged += (_, _) => { OverrideTriggers = true; Notify(nameof(OverrideTriggers)); }; Triggers.Add(editor); }
            foreach (var property in new[] { nameof(Category), nameof(Favorite), nameof(Note), nameof(Weight), nameof(Links), nameof(BaseModel), nameof(OverrideBaseModel), nameof(OverrideTriggers), nameof(PreviewOverride), nameof(PositiveAdditions), nameof(NegativeAdditions) }) Notify(property);
        }
    }
    private void EnsureStore() => store ??= new(Path.Combine(paths.Root, "UserData", "lora-library.db"));
    public async Task InitializeAsync() { if (!loaded) { loaded = true; await RefreshAsync(); } }
    public async Task AddRootAsync(string path)
    {
        if (!CanEdit) return;
        try { EnsureStore(); store!.AddRoot(path); await RefreshAsync(); Status = "フォルダー登録済み。「スキャン」で索引化します。"; }
        catch (Exception e) when (StorageError(e)) { Status = e.Message; }
    }
    public async Task ScanAsync(bool verifyHash = false)
    {
        if (!CanEdit) return; Busy = true;
        try { EnsureStore(); var results = await Task.Run(() => store!.Roots().Select(r => store.Scan(r, forceHash: verifyHash)).ToArray()); Status = $"追加 {results.Sum(r => r.Added)} / 更新 {results.Sum(r => r.Refreshed)} / 変更なし {results.Sum(r => r.Unchanged)} / hash {results.Sum(r => r.Hashed)} / missing {results.Sum(r => r.Missing)}" + string.Join("\n", results.Where(r => !r.Complete).Select(r => "未完了（DB保持）: " + r.Error)); }
        catch (Exception e) when (StorageError(e)) { Status = e.Message; }
        finally { Busy = false; }
        await RefreshAsync();
    }
    public async Task RefreshAsync(int delta = 0)
    {
        if (Busy) return; Busy = true;
        try
        {
            EnsureStore(); Roots.Clear(); foreach (var r in store!.Roots()) Roots.Add(r);
            offset = delta == 0 ? 0 : Math.Max(0, offset + delta); var page = await Task.Run(() => store.Query(Search, FavoriteOnly, offset));
            if (page.Length == 0 && offset > 0) { offset = Math.Max(0, offset - 100); page = await Task.Run(() => store.Query(Search, FavoriteOnly, offset)); }
            var prior = Selected?.Id; Selected = null; Assets.Clear(); foreach (var asset in page) Assets.Add(asset); Selected = Assets.FirstOrDefault(a => a.Id == prior);
        }
        catch (Exception e) when (StorageError(e)) { Status = "LoRA Libraryを開けません。DBを保持してください: " + e.Message; }
        finally { Busy = false; }
    }
    private decimal PreferredWeight() => decimal.TryParse(Weight, NumberStyles.Number, CultureInfo.InvariantCulture, out var w) && w is >= -2 and <= 2 ? w : throw new ArgumentException("weightは-2..2の数値を指定してください。");
    private LoraUserMetadata Draft(LoraAsset asset) => new(Category, Favorite, Note, PreferredWeight(), Links.Split('\n', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries), OverrideBaseModel ? BaseModel : null,
        OverrideTriggers ? Triggers.Where(t => !string.IsNullOrWhiteSpace(t.Text)).Select(t => new LoraTrigger(t.Text.Trim(), "user", t.Enabled)).ToArray() : null, PreviewOverride.Length == 0 ? null : PreviewOverride, Recipe(asset));
    private void CaptureDraft(LoraAsset asset)
    {
        // Unsaved valid edits survive selection/search/scan; persistent writes remain explicit.
        var rawWeight = Weight; draftWeights[asset.Sha256] = rawWeight;
        try { PreferredWeight(); } catch (ArgumentException) { Weight = asset.User.PreferredWeight.ToString(CultureInfo.InvariantCulture); }
        drafts[asset.Sha256] = Draft(asset); Weight = rawWeight;
    }
    public void AddTrigger() { if (CanEdit) { OverrideTriggers = true; Notify(nameof(OverrideTriggers)); Triggers.Add(new(new("", "user"))); } }
    private LoraRecipe Recipe(LoraAsset asset) => new(asset.Sha256, PreferredWeight(), Triggers.Where(t => t.Enabled && !string.IsNullOrWhiteSpace(t.Text)).Select(t => t.Text.Trim()).ToArray(), PositiveAdditions, NegativeAdditions, Note);
    public void Save()
    {
        if (!CanEdit || Selected is null) return;
        try
        {
            EnsureStore(); if (PreviewOverride.Length > 0 && !File.Exists(PreviewOverride)) throw new ArgumentException("preview overrideのlocalファイルがありません。");
            var metadata = Draft(Selected); store!.Save(Selected.Sha256, metadata); drafts.Remove(Selected.Sha256); draftWeights.Remove(Selected.Sha256);
            var updated = Selected with { User = metadata }; var index = Assets.IndexOf(Selected); selected = null;
            if (index >= 0) Assets[index] = updated; Selected = updated;
            Status = "SHA256 identityへuser override / recipeを保存しました。scanで上書きされません。";
        }
        catch (Exception e) when (StorageError(e) || e is ArgumentException) { Status = "保存できません。入力を保持しています: " + e.Message; }
    }
    public void Insert(bool recipe)
    {
        if (!CanEdit || Selected is null) return;
        try
        {
            EnsureStore(); if (!store!.CanInsert(Selected)) throw new ArgumentException("missing/変更済み、または同名・別hashのLoRAです。再スキャンまたはForge側の名前解決が必要です。挿入していません。");
            var r = Recipe(Selected); var positive = Selected.Token(r.Weight);
            if (recipe) positive += (r.Triggers.Length == 0 ? "" : ", " + string.Join(", ", r.Triggers)) + (string.IsNullOrWhiteSpace(r.Positive) ? "" : ", " + r.Positive);
            workspace.AppendPreset(parser.Parse(positive)); store.RecordUse(Selected.Sha256);
            Status = recipe ? "LoRAと選択trigger/Positiveを追加しました。Negative追加はPreset化またはコピーしてください。Undoで戻せます。" : "LoRAだけをPromptへ追加しました。triggerの自動挿入はありません。Undoで戻せます。";
        }
        catch (Exception e) when (StorageError(e) || e is ArgumentException) { Status = e.Message; }
    }
    public void CopyNegative() { clipboard.Write(NegativeAdditions); Status = "Recipe Negative追加をコピーしました。"; }
    public void AppendNegative() { if (CanEdit && NegativeWorkspace is not null) { NegativeWorkspace.AppendPreset(parser.Parse(NegativeAdditions)); Status = "Recipe NegativeをNegative Workspaceへ追加しました。NegativeのUndoで戻せます。"; } }
    public void CopyTriggers() { clipboard.Write(string.Join(", ", Triggers.Where(t => t.Enabled && !string.IsNullOrWhiteSpace(t.Text)).Select(t => t.Text.Trim()))); Status = "選択trigger wordsをコピーしました。"; }
    public void CreatePreset()
    {
        if (!CanEdit || Selected is null) return;
        try { EnsureStore(); if (!store!.CanInsert(Selected)) throw new ArgumentException("missing/変更済み、または同名・別hashです。再スキャン/Forge名前解決後にPreset化してください。"); var r = Recipe(Selected); createPreset(new(Guid.NewGuid(), Selected.Name, r.Note, Selected.Token(r.Weight) + (r.Triggers.Length > 0 ? ", " + string.Join(", ", r.Triggers) : "") + (r.Positive.Length > 0 ? ", " + r.Positive : ""), r.Negative)); Status = "既存Preset editorへRecipeを渡しました。"; }
        catch (ArgumentException e) { Status = e.Message; }
    }
    private static bool StorageError(Exception e) => e is IOException or UnauthorizedAccessException or Microsoft.Data.Sqlite.SqliteException or System.Text.Json.JsonException;
}
