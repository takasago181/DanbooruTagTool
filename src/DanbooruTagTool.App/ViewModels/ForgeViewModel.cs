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
    public AsyncRelayCommand GenerateInForge { get; }
    public AsyncRelayCommand SendPresetToForge { get; }
    public AsyncRelayCommand ApplyPresetRecipeToForge { get; }
    public AsyncRelayCommand GeneratePresetRecipe { get; }

    public ForgeViewModel(IForgeBridgeClient bridge, Action persist, Func<bool> canMutate, Func<string> english, Action<string> setStatus, Action openSettings)
    {
        this.bridge = bridge; this.persist = persist; this.canMutate = canMutate; this.english = english; this.setStatus = setStatus;
        OpenForgeSettings = new(_ => openSettings(), _ => canMutate()); SaveForgeSettings = new(_ => SaveSettings(), _ => canMutate());
        SendToForge = new(_ => SendAsync(null, CancellationToken.None), _ => canMutate());
        GenerateInForge = new(_ => GenerateAsync(null, CancellationToken.None), _ => canMutate());
        SendPresetToForge = new(p => SendAsync(p as GenerationPreset, CancellationToken.None), p => canMutate() && p is GenerationPreset);
        ApplyPresetRecipeToForge = new(p => ApplyRecipeAsync(p as GenerationPreset, CancellationToken.None),
            p => canMutate() && p is GenerationPreset preset && preset.HasRecipe);
        GeneratePresetRecipe = new(p => GenerateRecipeAsync(p as GenerationPreset, CancellationToken.None),
            p => canMutate() && p is GenerationPreset preset && preset.HasRecipe);
    }
    public void Restore(UiState ui) { forgeUrl = ui.ForgeUrl; forgeExtensionPath = ui.ForgeExtensionPath; }
    public Task SendAsync(GenerationPreset? preset, CancellationToken cancellationToken)
    {
        if (!canMutate()) return Task.CompletedTask;
        return SendCoreAsync(preset, ForgeBridgeAction.SendOnly, cancellationToken);
    }
    public Task GenerateAsync(GenerationPreset? preset, CancellationToken cancellationToken)
    {
        if (!canMutate()) return Task.CompletedTask;
        return SendCoreAsync(preset, ForgeBridgeAction.SendAndGenerate, cancellationToken);
    }
    public Task ApplyRecipeAsync(GenerationPreset? preset, CancellationToken cancellationToken)
    {
        if (!canMutate() || preset?.HasRecipe != true) return Task.CompletedTask;
        return SendRecipeCoreAsync(preset, ForgeBridgeAction.ApplyRecipe, cancellationToken);
    }
    public Task GenerateRecipeAsync(GenerationPreset? preset, CancellationToken cancellationToken)
    {
        if (!canMutate() || preset?.HasRecipe != true) return Task.CompletedTask;
        return SendRecipeCoreAsync(preset, ForgeBridgeAction.SendAndGenerate, cancellationToken);
    }
    private async Task SendCoreAsync(GenerationPreset? preset, ForgeBridgeAction action, CancellationToken cancellationToken)
    {
        var result = await bridge.SendAsync(
            ForgeUrl,
            new ForgeBridgeSendRequest(
                english(),
                preset == null ? ForgeNegativeMode.Unchanged : ForgeNegativeMode.Replace,
                preset?.Negative,
                action),
            cancellationToken);
        setStatus(result.Status);
    }
    private async Task SendRecipeCoreAsync(GenerationPreset preset, ForgeBridgeAction action, CancellationToken cancellationToken)
    {
        var result = await bridge.SendAsync(
            ForgeUrl,
            new ForgeBridgeSendRequest(
                preset.Positive,
                ForgeNegativeMode.Replace,
                preset.Negative,
                action,
                preset.Recipe),
            cancellationToken);
        setStatus(result.Status);
    }
    private void SaveSettings() { persist(); setStatus("Forge設定を保存しました"); }
}
