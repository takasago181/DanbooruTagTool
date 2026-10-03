using System.Net.Http;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using System.IO;

namespace DanbooruTagTool.App.ViewModels;

/// <summary>Owns Forge settings and bridge state; protocol remains in Core.</summary>
public sealed class ForgeViewModel : Observable
{
    public Task<ForgeApiCapabilities> ReadRecipeCapabilitiesAsync() => api.ProbeAsync(ForgeUrl);
    public Task<RecipeSnapshot> PinExperimentBaselineAsync(RecipeSnapshot snapshot) => api.PinRecipeIdentityAsync(ForgeUrl, snapshot);
    private readonly IForgeBridgeClient bridge;
    private readonly Action persist;
    private readonly Func<bool> canMutate;
    private readonly Func<string> english;
    private readonly Action<string> setStatus;
    private readonly IForgeGenerationApiClient api;
    private readonly string? apiOutput;
    private bool recipeBusy, bridgeBusy, experimentBusy;
    public void BeginExperiment()
    { if (!canMutate() || !RecipeExecutionAvailable) throw new InvalidOperationException("Forge is busy / editing unavailable."); experimentBusy = true; RefreshBusy(); }
    public void EndExperiment() { if (recipeBusy || bridgeBusy) throw new InvalidOperationException("Trial still running."); experimentBusy = false; RefreshBusy(); }
    public Task<ForgeApiResult?> ExecuteExperimentTrialAsync(GenerationPreset preset, CancellationToken ct, bool allowDerivative)
    { if (!experimentBusy || recipeBusy || bridgeBusy) throw new InvalidOperationException("Experiment lease required."); return GenerateRecipeCoreAsync(preset, ct, allowDerivative); }
    public bool RecipeBusy => recipeBusy || bridgeBusy || experimentBusy;
    public bool RecipeExecutionAvailable => apiOutput is not null && !RecipeBusy;
    private string connectionStatus = "Forge: 未確認（起動時には通信しません）";
    public string ConnectionStatus { get => connectionStatus; private set => Set(ref connectionStatus, value); }
    public AsyncRelayCommand CheckCapabilities { get; }
    private string capabilityStatus = "capability未確認。生成前に再検証します。";
    public string CapabilityStatus { get => capabilityStatus; private set => Set(ref capabilityStatus, value); }
    private void RefreshBusy()
    {
        Notify(nameof(RecipeBusy)); Notify(nameof(RecipeExecutionAvailable));
        OpenForgeSettings.Refresh(); SaveForgeSettings.Refresh(); GeneratePresetRecipe.Refresh(); CheckCapabilities.Refresh(); SendToForge.Refresh(); GenerateInForge.Refresh(); SendPresetToForge.Refresh(); SendWorkspacePair.Refresh();
    }

    private string recipeStatus = "API生成は1画像。未指定条件はForge既定値。指定条件は実画像で照合し、不一致は失敗として出力を保持します。";
    public string RecipeStatus { get => recipeStatus; private set => Set(ref recipeStatus, value); }
    public Func<string, Task>? IndexRecipeResult { get; set; }
    public Func<string>? CurrentNegative { get; set; }
    public AsyncRelayCommand GeneratePresetRecipe { get; }
    private string forgeUrl = ForgeBridgeProtocol.DefaultUrl, forgeExtensionPath = "";
    public string ForgeUrl { get => forgeUrl; set { if (Set(ref forgeUrl, value)) { ConnectionStatus = "Forge: 未確認（接続先変更）"; CapabilityStatus = "capability未確認。生成前に再検証します。"; } } }
    public string ForgeExtensionPath { get => forgeExtensionPath; set => Set(ref forgeExtensionPath, value); }
    public RelayCommand OpenForgeSettings { get; }
    public RelayCommand SaveForgeSettings { get; }
    public AsyncRelayCommand SendToForge { get; }
    public AsyncRelayCommand GenerateInForge { get; }
    public AsyncRelayCommand SendPresetToForge { get; }
    public AsyncRelayCommand SendWorkspacePair { get; }

    public ForgeViewModel(IForgeBridgeClient bridge, Action persist, Func<bool> canMutate, Func<string> english, Action<string> setStatus, Action openSettings, string? apiOutput = null, IForgeGenerationApiClient? api = null)
    {
        this.bridge = bridge; this.persist = persist; this.canMutate = canMutate; this.english = english; this.setStatus = setStatus;
        this.api = api ?? new ForgeGenerationApiClient(); this.apiOutput = apiOutput;
        CheckCapabilities = new(async _ =>
        {
            if (RecipeBusy) return;
            bridgeBusy = true; RefreshBusy(); ConnectionStatus = "Forge: capability確認中";
            try
            {
                var caps = await this.api.ProbeAsync(ForgeUrl);
                CapabilityStatus = $"対応: Model {caps.Models.Count} / Sampler {caps.Samplers.Count} / Scheduler {caps.Schedulers.Count}。実loaded modelは未確認。生成時も再検証。";
                ConnectionStatus = "Forge: 接続確認済み / 処理状態は未確認";
            }
            catch (Exception e) when (e is HttpRequestException or ArgumentException or InvalidDataException or OperationCanceledException or System.Text.Json.JsonException or KeyNotFoundException)
            { ConnectionStatus = "Forge: unreachable / capability error"; CapabilityStatus = "確認失敗: " + e.Message; }
            finally { bridgeBusy = false; RefreshBusy(); }
        }, _ => !RecipeBusy);
        GeneratePresetRecipe = new(p => GenerateRecipeAsync((GenerationPreset)p!), p => canMutate() && apiOutput is not null && !RecipeBusy && p is GenerationPreset { Recipe.HasAny: true });
        OpenForgeSettings = new(_ => openSettings(), _ => canMutate() && !RecipeBusy); SaveForgeSettings = new(_ => SaveSettings(), _ => canMutate() && !RecipeBusy);
        SendToForge = new(_ => SendAsync(null, CancellationToken.None), _ => canMutate() && !RecipeBusy);
        GenerateInForge = new(_ => GenerateAsync(null, CancellationToken.None), _ => canMutate() && !RecipeBusy);
        SendPresetToForge = new(p => SendAsync(p as GenerationPreset, CancellationToken.None), p => canMutate() && !RecipeBusy && p is GenerationPreset);
        SendWorkspacePair = new(_ => SendPayloadAsync(english(), CurrentNegative?.Invoke() ?? "", ForgeNegativeMode.Replace, ForgeBridgeAction.SendOnly, CancellationToken.None), _ => canMutate() && !RecipeBusy && CurrentNegative is not null);
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
    private async Task SendCoreAsync(GenerationPreset? preset, ForgeBridgeAction action, CancellationToken cancellationToken)
        => await SendPayloadAsync(english(), preset?.Negative, preset is null ? ForgeNegativeMode.Unchanged : ForgeNegativeMode.Replace, action, cancellationToken);

    // Image-library sends explicit Positive/Negative without mutating PromptWorkspace.
    public Task SendImageAsync(GenerationPreset preset, CancellationToken cancellationToken = default)
        => canMutate() ? SendPayloadAsync(preset.Positive, preset.Negative, ForgeNegativeMode.Replace, ForgeBridgeAction.SendOnly, cancellationToken) : Task.CompletedTask;
    public Task GenerateImageAsync(GenerationPreset preset, CancellationToken cancellationToken = default)
        => canMutate() ? SendPayloadAsync(preset.Positive, preset.Negative, ForgeNegativeMode.Replace, ForgeBridgeAction.SendAndGenerate, cancellationToken) : Task.CompletedTask;
    public async Task GenerateRecipeAsync(GenerationPreset preset, CancellationToken cancellationToken = default, bool allowDerivative = false)
    {
        if (!canMutate() || apiOutput is null || RecipeBusy) return;
        await GenerateRecipeCoreAsync(preset, cancellationToken, allowDerivative);
    }
    private async Task<ForgeApiResult?> GenerateRecipeCoreAsync(GenerationPreset preset, CancellationToken cancellationToken, bool allowDerivative)
    {
        if (apiOutput is null) return null;
        ForgeApiResult? result = null;
        if (preset.Recipe?.RequiresDerivativeConsent == true && !allowDerivative)
        {
            RecipeStatus = "元画像の未適用条件があります。Createで確認し、派生生成を了承してください。生成要求は送信していません。";
            setStatus(RecipeStatus); return new(false, RecipeStatus);
        }
        recipeBusy = true; RefreshBusy(); ConnectionStatus = "Forge: busy（1画像生成・照合中）"; RecipeStatus = "Forge APIで1画像生成中。完了するまで再送信しないでください。";
        try
        {
            result = await api.GenerateAsync(ForgeUrl, new(preset.Positive, preset.Negative, preset.Recipe ?? new(), allowDerivative), apiOutput, cancellationToken);
            ConnectionStatus = result.Success ? "Forge: idle（生成・照合完了）" : "Forge: error（詳細を確認）";
            RecipeStatus = result.Status + (result.ImagePath is null ? "" : "\n出力: " + result.ImagePath);
            // Failed round-trips remain real evidence too, never discarded or called successful.
            if (result.ImagePath is not null && IndexRecipeResult is not null) await IndexRecipeResult(result.ImagePath);
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or InvalidDataException or Microsoft.Data.Sqlite.SqliteException)
        { ConnectionStatus = "Forge: error（画像保持・Library登録未完了）"; RecipeStatus += "\nLibrary登録を完了できません。出力は保持しています: " + e.Message; result = new(false, RecipeStatus, result?.ImagePath, result?.Metadata); }
        finally { setStatus(RecipeStatus); recipeBusy = false; RefreshBusy(); }
        return result;
    }
    private async Task SendPayloadAsync(string positive, string? negative, ForgeNegativeMode negativeMode, ForgeBridgeAction action, CancellationToken cancellationToken)
    {
        if (RecipeBusy || !canMutate()) return;
        bridgeBusy = true; RefreshBusy(); ConnectionStatus = "Forge: busy（互換操作）";
        try
        {
            var result = await bridge.SendAsync(ForgeUrl, new ForgeBridgeSendRequest(positive, negativeMode, negative, action), cancellationToken);
            ConnectionStatus = "Forge: 互換操作終了（実loaded modelは未確認）";
            setStatus(result.Status);
        }
        catch (Exception e) when (e is HttpRequestException or IOException or ArgumentException or OperationCanceledException)
        { ConnectionStatus = "Forge: unreachable / error"; setStatus(e.Message); }
        finally { bridgeBusy = false; RefreshBusy(); }
    }
    private void SaveSettings() { persist(); setStatus("Forge設定を保存しました"); }
}
