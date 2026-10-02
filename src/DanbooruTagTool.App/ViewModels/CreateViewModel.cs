using System.Globalization;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App.ViewModels;

/// <summary>Session-only working conditions. Shared Prompt workspaces remain the only P/N owners.
/// Loading is explicit; saved presets and their management draft never silently sync here.</summary>
public sealed class CreateViewModel : Observable
{
    private readonly MainViewModel main;
    private GenerationPreset? selectedPreset;
    private string model = "", seed = "", steps = "", sampler = "", scheduler = "", cfg = "", width = "", height = "";
    private string origin = "未保存の現在設定", baselinePositive = "", baselineNegative = "";
    private GenerationRecipe? baselineRecipe;
    private bool loading;
    public CreateViewModel(MainViewModel main)
    {
        this.main = main;
        Generate = new(_ => GenerateAsync(), _ => CanGenerate);
        LoadPreset = new(_ => { if (SelectedPreset is { } p) Load(p, "Preset「" + p.Name + "」"); }, _ => main.CanEditPrompt && SelectedPreset is not null && !main.Forge.RecipeBusy);
        Save = new(_ => SaveCurrent(), _ => main.CanEditPrompt && !main.Forge.RecipeBusy);
        main.Workspace.Changed += Refresh;
        main.NegativeWorkspace.Changed += Refresh;
        main.Forge.PropertyChanged += (_, _) => Refresh();
        main.Prompt.PropertyChanged += (_, _) => Refresh();
        main.Negative.PropertyChanged += (_, _) => Refresh();
    }
    public GenerationPreset? SelectedPreset { get => selectedPreset; set { Set(ref selectedPreset, value); LoadPreset.Refresh(); } }
    public string SaveName { get; set; } = "";
    public string Model { get => model; set { Set(ref model, value); Refresh(); } }
    public string Seed { get => seed; set { Set(ref seed, value); Refresh(); } }
    public string Steps { get => steps; set { Set(ref steps, value); Refresh(); } }
    public string Sampler { get => sampler; set { Set(ref sampler, value); Refresh(); } }
    public string Scheduler { get => scheduler; set { Set(ref scheduler, value); Refresh(); } }
    public string Cfg { get => cfg; set { Set(ref cfg, value); Refresh(); } }
    public string Width { get => width; set { Set(ref width, value); Refresh(); } }
    public string Height { get => height; set { Set(ref height, value); Refresh(); } }
    public string Positive => main.Prompt.English;
    public string Negative => main.Negative.English;
    public string SourceSummary => origin + (Changed ? " → 現在値は変更済み・未保存" : " → 現在値") + "（Positive / Negative / 生成条件）";
    public bool Changed => origin != "未保存の現在設定" &&
        (Positive != baselinePositive || Negative != baselineNegative || !TryRecipe(out var r, out _) || r != baselineRecipe);
    public string ConditionsSummary => $"Model: {Value(Model)} · Seed: {Value(Seed)} · Steps: {Value(Steps)} · {Value(Sampler)} / {Value(Scheduler)} · CFG: {Value(Cfg)} · {Value(Width)}×{Value(Height)}";
    public string Validation => !TryRecipe(out var r, out var error) ? error : !Complete(r) ? "生成条件が不足または無効です。「生成条件 / Preset」で全項目を確認してください。" : "入力OK。生成前にForge capabilityを再確認し、実画像metadataで照合します。";
    public bool CanGenerate => main.CanEditPrompt && main.Forge.RecipeExecutionAvailable && !main.PresetManagementOpen && TryRecipe(out var r, out _) && Complete(r);
    public AsyncRelayCommand Generate { get; }
    public RelayCommand LoadPreset { get; }
    public RelayCommand Save { get; }
    private static string Value(string s) => string.IsNullOrWhiteSpace(s) ? "未指定" : s;
    private static bool Complete(GenerationRecipe? r) => r is { Model: not null, Seed: >= 0, Steps: not null, Sampler: not null, Scheduler: not null, Cfg: not null, Width: not null, Height: not null } && r.Width % 8 == 0 && r.Height % 8 == 0;
    public bool TryRecipe(out GenerationRecipe? r, out string error) => GenerationRecipeInput.TryBuild(Model, Seed, Steps, Sampler, Scheduler, Cfg, Width, Height, out r, out error);
    public void Load(GenerationPreset p, string source)
    {
        if (!main.CanEditPrompt || main.Forge.RecipeBusy || main.PresetManagementOpen) return;
        loading = true;
        try
        {
            main.Workspace.Replace(p.Positive); main.NegativeWorkspace.Replace(p.Negative);
            var r = p.Recipe;
            Model = r?.Model ?? ""; Seed = Number(r?.Seed); Steps = Number(r?.Steps); Sampler = r?.Sampler ?? "";
            Scheduler = r?.Scheduler ?? ""; Cfg = Number(r?.Cfg); Width = Number(r?.Width); Height = Number(r?.Height);
            origin = source; baselinePositive = Positive; baselineNegative = Negative; baselineRecipe = r?.HasAny == true ? r : null;
            main.WorkspaceIndex = 1; main.CreatePageIndex = 0;
            main.Status = "作成で使う: Positive / Negative / 生成条件を置換しました。両PromptのUndo・回復は独立です。";
        }
        finally { loading = false; Refresh(); }
    }
    private static string Number<T>(T? n) where T : struct, IFormattable => n?.ToString(null, CultureInfo.InvariantCulture) ?? "";
    public async Task GenerateAsync()
    {
        if (!CanGenerate || !TryRecipe(out var r, out _)) return;
        // Capture before await: edits/selection changes cannot change this trial's source.
        var snapshot = new GenerationPreset(Guid.NewGuid(), SourceSummary, "現在の未保存snapshot", Positive, Negative, r);
        await main.Forge.GenerateRecipeAsync(snapshot);
    }
    private void SaveCurrent()
    {
        if (!main.CanEditPrompt || main.Forge.RecipeBusy || main.PresetManagementOpen) return;
        if (string.IsNullOrWhiteSpace(SaveName)) { main.Status = "Preset名を入力してください。既存Presetを上書きせず新しく保存します。"; return; }
        if (!TryRecipe(out var r, out var error)) { main.Status = error; return; }
        var p = new GenerationPreset(Guid.NewGuid(), SaveName.Trim(), "作成の現在snapshot", Positive, Negative, r);
        main.Presets.Add(p); if (!main.TryPersist()) { main.Presets.Remove(p); return; } SelectedPreset = p;
        origin = "Preset「" + p.Name + "」"; baselinePositive = Positive; baselineNegative = Negative; baselineRecipe = r;
        main.Status = "現在のPositive / Negative / 生成条件を新しいPresetに保存しました。"; Refresh();
    }
    public void Refresh()
    {
        if (loading) return;
        foreach (var n in new[] { nameof(Positive), nameof(Negative), nameof(SourceSummary), nameof(ConditionsSummary), nameof(Validation), nameof(CanGenerate), nameof(Changed) }) Notify(n);
        Generate?.Refresh(); LoadPreset?.Refresh(); Save?.Refresh();
    }
}
