using System.Collections.ObjectModel;
using System.IO;
using DanbooruTagTool.Core;

namespace DanbooruTagTool.App.ViewModels;

public sealed record GenerationParameterRow(string Name, string Value);

public sealed class GenerationImportViewModel : Observable
{
    private static readonly string[] CommonNames =
    [
        "Steps", "Sampler", "Schedule type", "Scheduler", "CFG scale", "Seed", "Size",
        "Model", "Model hash", "VAE", "VAE hash", "Clip skip", "Denoising strength",
        "Hires upscale", "Hires steps", "Hires upscaler"
    ];

    private readonly PromptWorkspace workspace;
    private readonly IClipboardService clipboard;
    private readonly Action<string> setStatus;
    private readonly Action<GenerationMetadataSnapshot> createPreset;
    private GenerationMetadataSnapshot? snapshot;

    public GenerationMetadataSnapshot? Snapshot
    {
        get => snapshot;
        private set
        {
            if (!Set(ref snapshot, value)) return;
            RebuildRows();
            Notify(nameof(HasSnapshot));
            Notify(nameof(SourceFileName));
            Notify(nameof(SourcePath));
            Notify(nameof(Positive));
            Notify(nameof(Negative));
            Notify(nameof(NegativeDisplay));
            Notify(nameof(HasNegative));
            Notify(nameof(RawInfotext));
            Notify(nameof(DimensionSummary));
            RefreshCommands();
        }
    }

    public bool HasSnapshot => Snapshot is not null;
    public string SourceFileName => Snapshot is null ? "" : Path.GetFileName(Snapshot.SourcePath);
    public string SourcePath => Snapshot?.SourcePath ?? "";
    public string Positive => Snapshot?.Positive ?? "";
    public string Negative => Snapshot?.Negative ?? "";
    public string NegativeDisplay => HasNegative ? Negative : "（Negative Promptなし）";
    public bool HasNegative => !string.IsNullOrWhiteSpace(Negative);
    public string RawInfotext => Snapshot?.RawInfotext ?? "";
    public string DimensionSummary => Snapshot is { Width: { } width, Height: { } height } ? $"{width} × {height}" : "";

    public ObservableCollection<GenerationParameterRow> CommonRows { get; } = [];
    public ObservableCollection<GenerationParameterRow> AdditionalRows { get; } = [];

    public RelayCommand RestorePositive { get; }
    public RelayCommand CopyNegative { get; }
    public RelayCommand CopyInfo { get; }
    public RelayCommand CreatePreset { get; }

    public GenerationImportViewModel(PromptWorkspace workspace, IClipboardService clipboard, Action<string> setStatus,
        Action<GenerationMetadataSnapshot> createPreset)
    {
        this.workspace = workspace;
        this.clipboard = clipboard;
        this.setStatus = setStatus;
        this.createPreset = createPreset;

        RestorePositive = new(_ => Restore(), _ => HasSnapshot && !string.IsNullOrWhiteSpace(Positive));
        CopyNegative = new(_ => Copy(Negative, "Negative Promptをコピーしました"), _ => HasNegative);
        CopyInfo = new(_ => Copy(RawInfotext, "生成情報をコピーしました"), _ => HasSnapshot);
        CreatePreset = new(_ => CreatePresetFromSnapshot(), _ => HasSnapshot);
    }

    public void Load(GenerationMetadataSnapshot value) => Snapshot = value;

    private void Restore()
    {
        if (Snapshot is null || string.IsNullOrWhiteSpace(Snapshot.Positive)) return;
        workspace.Replace(Snapshot.Positive);
        setStatus("✓ 生成PNGのPositive Promptを復元しました");
    }

    private void CreatePresetFromSnapshot()
    {
        if (Snapshot is null) return;
        createPreset(Snapshot);
    }

    private void Copy(string text, string success)
    {
        try
        {
            clipboard.Write(text);
            setStatus("✓ " + success);
        }
        catch (Exception ex) when (ex is System.Runtime.InteropServices.ExternalException or IOException)
        {
            setStatus("操作できませんでした: " + ex.Message);
        }
    }

    private void RebuildRows()
    {
        CommonRows.Clear();
        AdditionalRows.Clear();
        if (Snapshot is null) return;

        var commonSet = CommonNames.ToHashSet(StringComparer.OrdinalIgnoreCase);
        foreach (var name in CommonNames)
        {
            foreach (var parameter in Snapshot.Parameters.Where(item => item.Name.Equals(name, StringComparison.OrdinalIgnoreCase)))
                CommonRows.Add(new(DisplayName(parameter.Name), parameter.Value));
        }

        foreach (var parameter in Snapshot.Parameters.Where(item => !commonSet.Contains(item.Name)))
            AdditionalRows.Add(new(parameter.Name, parameter.Value));
    }

    private static string DisplayName(string name) => name switch
    {
        "Schedule type" => "Scheduler",
        "CFG scale" => "CFG",
        _ => name
    };

    private void RefreshCommands()
    {
        RestorePositive.Refresh();
        CopyNegative.Refresh();
        CopyInfo.Refresh();
        CreatePreset.Refresh();
    }
}
