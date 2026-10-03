using System.Collections.ObjectModel;
using System.Globalization;
using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App.ViewModels;

/// <summary>Owns generation preset/recipe editing without changing the Core prompt workspace.</summary>
public sealed class GenerationPresetsViewModel : Observable
{
    private readonly IRuntimeCatalogQuery catalog;
    private readonly PromptWorkspace workspace;
    private readonly IClipboardService clipboard;
    private readonly Action persist;
    private readonly Func<bool> canMutate;
    private readonly Action<string> setStatus;
    private GenerationPreset? selectedPreset;
    private string presetName = "", presetDescription = "", presetPositive = "", presetNegative = "";
    private string presetModel = "", presetSeed = "", presetSteps = "", presetSampler = "", presetScheduler = "", presetCfg = "", presetWidth = "", presetHeight = "";

    public ObservableCollection<GenerationPreset> Presets { get; } = [];
    public PromptWorkspace Workspace => workspace;
    public PromptWorkspace? NegativeWorkspace { get; set; }
    public RelayCommand ApplyPresetNegative { get; }
    public RelayCommand CapturePresetNegative { get; }

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
            LoadRecipe(value?.Recipe);
        }
    }

    public string PresetName { get => presetName; set { if (Set(ref presetName, value)) SavePreset.Refresh(); } }
    public string PresetDescription { get => presetDescription; set => Set(ref presetDescription, value); }
    public string PresetPositive { get => presetPositive; set => Set(ref presetPositive, value); }
    public string PresetNegative { get => presetNegative; set => Set(ref presetNegative, value); }
    public string PresetModel { get => presetModel; set => Set(ref presetModel, value); }
    private string presetModelHash = "";
    private IReadOnlyList<GenerationParameter>? sourceParameters;
    public string RestorationWarning => sourceParameters is null ? "" : "元画像条件を保持しています。未適用条件はCreateで確認してください。\n" + string.Join("\n", sourceParameters.Select(p => p.Name + ": " + p.Value));
    public string PresetModelHash { get => presetModelHash; set => Set(ref presetModelHash, value); }
    public string PresetSeed { get => presetSeed; set => Set(ref presetSeed, value); }
    public string PresetSteps { get => presetSteps; set => Set(ref presetSteps, value); }
    public string PresetSampler { get => presetSampler; set => Set(ref presetSampler, value); }
    public string PresetScheduler { get => presetScheduler; set => Set(ref presetScheduler, value); }
    public string PresetCfg { get => presetCfg; set => Set(ref presetCfg, value); }
    public string PresetWidth { get => presetWidth; set => Set(ref presetWidth, value); }
    public string PresetHeight { get => presetHeight; set => Set(ref presetHeight, value); }

    public RelayCommand NewPreset { get; }
    public RelayCommand ApplyPreset { get; }
    public RelayCommand CopyPresetNegative { get; }
    public RelayCommand CapturePresetPositive { get; }
    public RelayCommand SavePreset { get; }
    public RelayCommand DeletePreset { get; }

    public GenerationPresetsViewModel(IRuntimeCatalogQuery catalog, PromptWorkspace workspace, IClipboardService clipboard,
        Action persist, Func<bool> canMutate, Action<string> setStatus)
    {
        this.catalog = catalog;
        this.workspace = workspace;
        this.clipboard = clipboard;
        this.persist = persist;
        this.canMutate = canMutate;
        this.setStatus = setStatus;

        NewPreset = Normal(_ => BeginNewPreset());
        ApplyPreset = Normal(p => ApplyPresetToPrompt(p as GenerationPreset), p => p is GenerationPreset);
        ApplyPresetNegative = Normal(p => { if (p is GenerationPreset preset) { NegativeWorkspace?.Replace(preset.Negative); setStatus("Preset Negativeを置換しました。NegativeのUndo/回復で戻せます。"); } }, p => p is GenerationPreset && NegativeWorkspace is not null);
        CapturePresetNegative = Normal(_ => PresetNegative = NegativeWorkspace?.English ?? "");
        CopyPresetNegative = Normal(p => CopyPresetNegativeText(p as GenerationPreset), p => p is GenerationPreset);
        CapturePresetPositive = Normal(_ => PresetPositive = PromptParser.Serialize(Workspace.Items));
        SavePreset = Normal(_ => SavePresetValue());
        DeletePreset = Normal(p => DeletePresetValue(p as GenerationPreset ?? SelectedPreset), p => p is GenerationPreset || SelectedPreset != null);
    }

    public void Restore(UserState? state)
    {
        if (state?.Presets is not null)
            foreach (var preset in state.Presets) Presets.Add(preset);
    }

    public void BeginNewPreset()
    {
        SelectedPreset = null;
        PresetName = "";
        PresetDescription = "";
        PresetPositive = "";
        PresetNegative = "";
        LoadRecipe(null);
    }

    public void BeginNewPresetFromSnapshot(GenerationMetadataSnapshot snapshot)
    {
        BeginNewPreset();
        PresetPositive = snapshot.Positive;
        PresetNegative = snapshot.Negative;
        LoadRecipe(GenerationRecipe.FromMetadata(snapshot));
        setStatus("生成PNGのPromptと生成条件を新規プリセットへ取り込みました");
    }

    private void ApplyPresetToPrompt(GenerationPreset? preset)
    {
        if (preset == null) return;
        var result = workspace.AppendPreset(new PromptParser(catalog).Parse(preset.Positive));
        setStatus($"{result.Added}件追加 / {result.Skipped}件スキップ");
    }

    private void CopyPresetNegativeText(GenerationPreset? preset)
    {
        if (preset == null) return;
        try
        {
            clipboard.Write(preset.Negative);
            setStatus("✓ Negativeをコピーしました");
        }
        catch (Exception e) when (e is System.Runtime.InteropServices.ExternalException or IOException)
        {
            setStatus("操作できませんでした: " + e.Message);
        }
    }

    private void SavePresetValue()
    {
        if (!TryBuildRecipe(out var recipe, out var error))
        {
            setStatus(error);
            return;
        }

        var parsed = new PromptParser(catalog).Parse(PresetPositive);
        var saved = new GenerationPreset(
            SelectedPreset?.Id ?? Guid.NewGuid(),
            PresetName.Trim(),
            PresetDescription,
            PromptOutputFormatter.SerializeCanonical(parsed),
            PresetNegative,
            recipe);

        var index = SelectedPreset == null ? -1 : Presets.IndexOf(SelectedPreset);
        if (index < 0) Presets.Add(saved);
        else Presets[index] = saved;

        SelectedPreset = saved;
        persist();
        setStatus(recipe?.HasAny == true ? "生成レシピを保存しました" : "プリセットを保存しました");
    }

    private bool TryBuildRecipe(out GenerationRecipe? recipe, out string error) =>
        GenerationRecipeInput.TryBuild(PresetModel, PresetSeed, PresetSteps, PresetSampler, PresetScheduler,
            PresetCfg, PresetWidth, PresetHeight, out recipe, out error, PresetModelHash, sourceParameters);

    private void LoadRecipe(GenerationRecipe? recipe)
    {
        PresetModel = recipe?.Model ?? "";
        sourceParameters = recipe?.SourceParameters?.ToArray(); Notify(nameof(RestorationWarning));
        PresetModelHash = recipe?.ModelHash ?? "";
        PresetSeed = recipe?.Seed?.ToString(CultureInfo.InvariantCulture) ?? "";
        PresetSteps = recipe?.Steps?.ToString(CultureInfo.InvariantCulture) ?? "";
        PresetSampler = recipe?.Sampler ?? "";
        PresetScheduler = recipe?.Scheduler ?? "";
        PresetCfg = recipe?.Cfg?.ToString(CultureInfo.InvariantCulture) ?? "";
        PresetWidth = recipe?.Width?.ToString(CultureInfo.InvariantCulture) ?? "";
        PresetHeight = recipe?.Height?.ToString(CultureInfo.InvariantCulture) ?? "";
    }

    private void DeletePresetValue(GenerationPreset? preset)
    {
        if (preset == null || !Presets.Remove(preset)) return;
        persist();
        BeginNewPreset();
        setStatus("プリセットを削除しました");
    }

    private RelayCommand Normal(Action<object?> action, Predicate<object?>? enabled = null) =>
        new(p => { if (canMutate() && (enabled?.Invoke(p) ?? true)) action(p); },
            p => canMutate() && (enabled?.Invoke(p) ?? true));
}
