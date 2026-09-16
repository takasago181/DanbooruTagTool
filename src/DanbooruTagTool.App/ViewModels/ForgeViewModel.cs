using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App.ViewModels;

/// <summary>Owns Forge settings and bridge state; protocol remains in Core.</summary>
public sealed class ForgeViewModel : Observable
{
    private readonly IForgeBridgeClient bridge;
    private readonly Action persist;
    private readonly Func<bool> canMutate;
    private readonly Func<string> english;
    private readonly Action<string> setStatus;
    private string forgeUrl = ForgeBridgeProtocol.DefaultUrl, forgeExtensionPath = "";
    public string ForgeUrl { get => forgeUrl; set => Set(ref forgeUrl, value); }
    public string ForgeExtensionPath { get => forgeExtensionPath; set => Set(ref forgeExtensionPath, value); }
    public RelayCommand OpenForgeSettings { get; }
    public RelayCommand SaveForgeSettings { get; }
    public AsyncRelayCommand SendToForge { get; }
    public AsyncRelayCommand SendPresetToForge { get; }

    public ForgeViewModel(IForgeBridgeClient bridge, Action persist, Func<bool> canMutate, Func<string> english, Action<string> setStatus, Action openSettings)
    {
        this.bridge = bridge; this.persist = persist; this.canMutate = canMutate; this.english = english; this.setStatus = setStatus;
        OpenForgeSettings = new(_ => openSettings(), _ => canMutate()); SaveForgeSettings = new(_ => SaveSettings(), _ => canMutate());
        SendToForge = new(_ => SendAsync(null, CancellationToken.None), _ => canMutate());
        SendPresetToForge = new(p => SendAsync(p as GenerationPreset, CancellationToken.None), p => canMutate() && p is GenerationPreset);
    }
    public void Restore(UiState ui) { forgeUrl = ui.ForgeUrl; forgeExtensionPath = ui.ForgeExtensionPath; }
    public Task SendAsync(GenerationPreset? preset, CancellationToken cancellationToken)
    {
        if (!canMutate()) return Task.CompletedTask;
        return SendCoreAsync(preset, cancellationToken);
    }
    private async Task SendCoreAsync(GenerationPreset? preset, CancellationToken cancellationToken)
    {
        var result = await bridge.SendAsync(ForgeUrl, new ForgeBridgeSendRequest(english(), preset == null ? ForgeNegativeMode.Unchanged : ForgeNegativeMode.Replace, preset?.Negative), cancellationToken); setStatus(result.Status);
    }
    private void SaveSettings() { persist(); setStatus("Forge設定を保存しました"); }
}
