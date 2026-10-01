using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using System.IO;

namespace DanbooruTagTool.App.ViewModels;

/// <summary>Owns Forge settings and bridge state; protocol remains in Core.</summary>
public sealed class ForgeViewModel : Observable
{
    private readonly IForgeBridgeClient bridge;
    private readonly Action persist;
    private readonly Func<bool> canMutate;
    private readonly Func<string> english;
    private readonly Action<string> setStatus;
    private readonly IForgeGenerationApiClient api;
    private readonly string? apiOutput;
    private bool recipeBusy;
    private string recipeStatus = "API生成は1画像。未指定条件はForge既定値。指定条件は実画像で照合し、不一致は失敗として出力を保持します。";
    public string RecipeStatus { get => recipeStatus; private set => Set(ref recipeStatus, value); }
    public Func<string, Task>? IndexRecipeResult { get; set; }
    public AsyncRelayCommand GeneratePresetRecipe { get; }
    private string forgeUrl = ForgeBridgeProtocol.DefaultUrl, forgeExtensionPath = "";
    public string ForgeUrl { get => forgeUrl; set => Set(ref forgeUrl, value); }
    public string ForgeExtensionPath { get => forgeExtensionPath; set => Set(ref forgeExtensionPath, value); }
    public RelayCommand OpenForgeSettings { get; }
    public RelayCommand SaveForgeSettings { get; }
    public AsyncRelayCommand SendToForge { get; }
    public AsyncRelayCommand GenerateInForge { get; }
    public AsyncRelayCommand SendPresetToForge { get; }

    public ForgeViewModel(IForgeBridgeClient bridge, Action persist, Func<bool> canMutate, Func<string> english, Action<string> setStatus, Action openSettings, string? apiOutput = null, IForgeGenerationApiClient? api = null)
    {
        this.bridge = bridge; this.persist = persist; this.canMutate = canMutate; this.english = english; this.setStatus = setStatus;
        this.api = api ?? new ForgeGenerationApiClient(); this.apiOutput = apiOutput;
        GeneratePresetRecipe = new(p => GenerateRecipeAsync((GenerationPreset)p!), p => canMutate() && apiOutput is not null && !recipeBusy && p is GenerationPreset { Recipe.HasAny: true });
        OpenForgeSettings = new(_ => openSettings(), _ => canMutate()); SaveForgeSettings = new(_ => SaveSettings(), _ => canMutate());
        SendToForge = new(_ => SendAsync(null, CancellationToken.None), _ => canMutate());
        GenerateInForge = new(_ => GenerateAsync(null, CancellationToken.None), _ => canMutate());
        SendPresetToForge = new(p => SendAsync(p as GenerationPreset, CancellationToken.None), p => canMutate() && p is GenerationPreset);
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
        => await SendPayloadAsync(english(), preset?.Negative, preset == null ? ForgeNegativeMode.Unchanged : ForgeNegativeMode.Replace, action, cancellationToken);

    // Image-library sends explicit Positive/Negative without mutating PromptWorkspace.
    public Task SendImageAsync(GenerationPreset preset, CancellationToken cancellationToken = default)
        => canMutate() ? SendPayloadAsync(preset.Positive, preset.Negative, ForgeNegativeMode.Replace, ForgeBridgeAction.SendOnly, cancellationToken) : Task.CompletedTask;
    public Task GenerateImageAsync(GenerationPreset preset, CancellationToken cancellationToken = default)
        => canMutate() ? SendPayloadAsync(preset.Positive, preset.Negative, ForgeNegativeMode.Replace, ForgeBridgeAction.SendAndGenerate, cancellationToken) : Task.CompletedTask;
    public async Task GenerateRecipeAsync(GenerationPreset preset, CancellationToken cancellationToken = default)
    {
        if (!canMutate() || apiOutput is null || recipeBusy) return;
        recipeBusy = true; GeneratePresetRecipe.Refresh(); RecipeStatus = "Forge APIで1画像生成中。完了するまで再送信しないでください。";
        try
        {
            var result = await api.GenerateAsync(ForgeUrl, new(preset.Positive, preset.Negative, preset.Recipe ?? new()), apiOutput, cancellationToken);
            RecipeStatus = result.Status + (result.ImagePath is null ? "" : "\n出力: " + result.ImagePath);
            // Failed round-trips remain real evidence too, never discarded or called successful.
            if (result.ImagePath is not null && IndexRecipeResult is not null) await IndexRecipeResult(result.ImagePath);
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or InvalidDataException or Microsoft.Data.Sqlite.SqliteException)
        { RecipeStatus += "\nLibrary登録を完了できません。出力は保持しています: " + e.Message; }
        finally { setStatus(RecipeStatus); recipeBusy = false; GeneratePresetRecipe.Refresh(); }
    }
    private async Task SendPayloadAsync(string positive, string? negative, ForgeNegativeMode negativeMode, ForgeBridgeAction action, CancellationToken cancellationToken)
    {
        var result = await bridge.SendAsync(
            ForgeUrl,
            new ForgeBridgeSendRequest(
                positive,
                negativeMode,
                negative,
                action),
            cancellationToken);
        setStatus(result.Status);
    }
    private void SaveSettings() { persist(); setStatus("Forge設定を保存しました"); }
}
