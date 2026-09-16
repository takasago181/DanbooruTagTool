using System.Collections.ObjectModel;
using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App.ViewModels;

/// <summary>Owns generation preset editing without changing the Core prompt model.</summary>
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

    public ObservableCollection<GenerationPreset> Presets { get; } = [];
    public PromptWorkspace Workspace => workspace;
    public GenerationPreset? SelectedPreset
    {
        get => selectedPreset;
        set
        {
            if (!Set(ref selectedPreset, value)) return;
            PresetName = value?.Name ?? ""; PresetDescription = value?.Description ?? ""; PresetPositive = value?.Positive ?? ""; PresetNegative = value?.Negative ?? "";
        }
    }
    public string PresetName { get => presetName; set { if (Set(ref presetName, value)) SavePreset.Refresh(); } }
    public string PresetDescription { get => presetDescription; set => Set(ref presetDescription, value); }
    public string PresetPositive { get => presetPositive; set => Set(ref presetPositive, value); }
    public string PresetNegative { get => presetNegative; set => Set(ref presetNegative, value); }
    public RelayCommand NewPreset { get; }
    public RelayCommand ApplyPreset { get; }
    public RelayCommand CopyPresetNegative { get; }
    public RelayCommand CapturePresetPositive { get; }
    public RelayCommand SavePreset { get; }
    public RelayCommand DeletePreset { get; }

    public GenerationPresetsViewModel(IRuntimeCatalogQuery catalog, PromptWorkspace workspace, IClipboardService clipboard,
        Action persist, Func<bool> canMutate, Action<string> setStatus)
    {
        this.catalog = catalog; this.workspace = workspace; this.clipboard = clipboard; this.persist = persist; this.canMutate = canMutate; this.setStatus = setStatus;
        NewPreset = Normal(_ => BeginNewPreset());
        ApplyPreset = Normal(p => ApplyPresetToPrompt(p as GenerationPreset), p => p is GenerationPreset);
        CopyPresetNegative = Normal(p => CopyPresetNegativeText(p as GenerationPreset), p => p is GenerationPreset);
        CapturePresetPositive = Normal(_ => PresetPositive = PromptParser.Serialize(Workspace.Items));
        SavePreset = Normal(_ => SavePresetValue());
        DeletePreset = Normal(p => DeletePresetValue(p as GenerationPreset ?? SelectedPreset), p => p is GenerationPreset || SelectedPreset != null);
    }
    public void Restore(UserState? state) { if (state?.Presets is not null) foreach (var preset in state.Presets) Presets.Add(preset); }
    private void BeginNewPreset() { SelectedPreset = null; PresetName = ""; PresetDescription = ""; PresetPositive = ""; PresetNegative = ""; }
    private void ApplyPresetToPrompt(GenerationPreset? preset)
    {
        if (preset == null) return; var result = workspace.AppendPreset(new PromptParser(catalog).Parse(preset.Positive)); setStatus($"{result.Added}件追加 / {result.Skipped}件スキップ");
    }
    private void CopyPresetNegativeText(GenerationPreset? preset)
    {
        if (preset == null) return;
        try { clipboard.Write(preset.Negative); setStatus("✓ Negativeをコピーしました"); }
        catch (Exception e) when (e is System.Runtime.InteropServices.ExternalException or IOException) { setStatus("操作できませんでした: " + e.Message); }
    }
    private void SavePresetValue()
    {
        var parsed = new PromptParser(catalog).Parse(PresetPositive);
        var saved = new GenerationPreset(SelectedPreset?.Id ?? Guid.NewGuid(), PresetName.Trim(), PresetDescription, PromptOutputFormatter.SerializeCanonical(parsed), PresetNegative);
        var index = SelectedPreset == null ? -1 : Presets.IndexOf(SelectedPreset); if (index < 0) Presets.Add(saved); else Presets[index] = saved;
        SelectedPreset = saved; persist(); setStatus("プリセットを保存しました");
    }
    private void DeletePresetValue(GenerationPreset? preset)
    {
        if (preset == null || !Presets.Remove(preset)) return; persist(); BeginNewPreset(); setStatus("プリセットを削除しました");
    }
    private RelayCommand Normal(Action<object?> action, Predicate<object?>? enabled = null) => new(p => { if (canMutate() && (enabled?.Invoke(p) ?? true)) action(p); }, p => canMutate() && (enabled?.Invoke(p) ?? true));
}
