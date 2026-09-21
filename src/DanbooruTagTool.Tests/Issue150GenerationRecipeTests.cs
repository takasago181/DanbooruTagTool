using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue150GenerationRecipeTests
{
    [Fact]
    public void LegacyPresetJsonWithoutRecipeStillLoads()
    {
        var id = Guid.NewGuid();
        var json = $$"""{"Id":"{{id}}","Name":"legacy","Description":"","Positive":"blue_hair","Negative":"lowres"}""";

        var preset = JsonSerializer.Deserialize<GenerationPreset>(json)!;

        Assert.Equal("legacy", preset.Name);
        Assert.Null(preset.Recipe);
        Assert.False(preset.HasRecipe);
    }

    [Fact]
    public void RecipePersistsThroughUserStateStore()
    {
        using var directory = new TempDirectory();
        var path = new PortablePaths(directory.Path).User;
        var workspace = Fixtures.Workspace();
        var recipe = new GenerationRecipe("waiIllustriousSDXL_v170", 16521, 8, "Euler a", "Automatic", 5m, 1024, 1024);
        var preset = new GenerationPreset(Guid.NewGuid(), "recipe", "test", "blue_hair", "lowres", recipe);

        new UserStateStore(path).Save(new(workspace.Snapshot(), new(), [preset]));
        var restored = Assert.Single(new UserStateStore(path).Load()!.Presets!);

        Assert.True(restored.HasRecipe);
        Assert.Equal(recipe, restored.Recipe);
        Assert.Contains("8 steps", restored.RecipeSummary);
        Assert.Contains("1024×1024", restored.RecipeSummary);
    }

    [Fact]
    public void ChoiceOnlyRecipeIsReferenceOnly()
    {
        var recipe = new GenerationRecipe(
            Model: "manual-model",
            Sampler: "Euler a",
            Scheduler: "Karras");
        var preset = new GenerationPreset(Guid.NewGuid(), "manual choices", "", "blue_hair", "lowres", recipe);

        Assert.True(recipe.HasAny);
        Assert.False(recipe.HasAutomaticSettings);
        Assert.True(preset.HasRecipe);
        Assert.False(preset.HasAutomaticRecipe);
    }

    [Fact]
    public void PngSnapshotPrefillsRecipeWithoutAutoSaving()
    {
        var store = new MemoryStore();
        var vm = Fixtures.Vm(store);
        var snapshot = ForgePngGenerationMetadata.Parse(
            "sample.png",
            "blue_hair, smile\nNegative prompt: lowres\nSteps: 8, Sampler: Euler a, Schedule type: Automatic, CFG scale: 5, Seed: 16521, Size: 1024x1024, Model: waiIllustriousSDXL_v170");

        vm.GenerationImport.Load(snapshot);
        vm.GenerationImport.CreatePreset.Execute(null);

        Assert.Empty(vm.Presets);
        Assert.Equal("blue_hair, smile", vm.PresetPositive);
        Assert.Equal("lowres", vm.PresetNegative);
        Assert.Equal("waiIllustriousSDXL_v170", vm.PresetModel);
        Assert.Equal("16521", vm.PresetSeed);
        Assert.Equal("8", vm.PresetSteps);
        Assert.Equal("Euler a", vm.PresetSampler);
        Assert.Equal("Automatic", vm.PresetScheduler);
        Assert.Equal("5", vm.PresetCfg);
        Assert.Equal("1024", vm.PresetWidth);
        Assert.Equal("1024", vm.PresetHeight);
        Assert.Null(store.State);
    }

    [Fact]
    public void SavingPrefilledRecipePersistsOnlyAfterExplicitSave()
    {
        var store = new MemoryStore();
        var vm = Fixtures.Vm(store);
        vm.NewPreset.Execute(null);
        vm.PresetName = "my recipe";
        vm.PresetPositive = "blue_hair";
        vm.PresetNegative = "lowres";
        vm.PresetSeed = "42";
        vm.PresetSteps = "25";
        vm.PresetSampler = "Euler a";
        vm.PresetScheduler = "Karras";
        vm.PresetCfg = "5.5";
        vm.PresetWidth = "832";
        vm.PresetHeight = "1216";

        vm.SavePreset.Execute(null);

        var preset = Assert.Single(vm.Presets);
        Assert.NotNull(preset.Recipe);
        Assert.Equal(42, preset.Recipe!.Seed);
        Assert.Equal(25, preset.Recipe.Steps);
        Assert.Equal(5.5m, preset.Recipe.Cfg);
        Assert.NotNull(store.State);
        Assert.Equal(preset, Assert.Single(store.State!.Presets!));
    }

    [Fact]
    public void EmptyRecipeFieldsPreservePromptOnlyPreset()
    {
        var vm = Fixtures.Vm();
        vm.NewPreset.Execute(null);
        vm.PresetName = "prompt only";
        vm.PresetPositive = "blue_hair";
        vm.PresetNegative = "lowres";

        vm.SavePreset.Execute(null);

        var preset = Assert.Single(vm.Presets);
        Assert.Null(preset.Recipe);
        Assert.False(preset.HasRecipe);
    }

    [Fact]
    public void InvalidRecipeNumberDoesNotSave()
    {
        var vm = Fixtures.Vm();
        vm.NewPreset.Execute(null);
        vm.PresetName = "bad";
        vm.PresetPositive = "blue_hair";
        vm.PresetSteps = "999";

        vm.SavePreset.Execute(null);

        Assert.Empty(vm.Presets);
        Assert.Contains("Steps", vm.Status);
    }

    [Fact]
    public async Task RecipeApplyRequiresUpdatedBridgeCapability()
    {
        var client = Client((request, _) =>
        {
            Assert.EndsWith("/health", request.RequestUri!.AbsolutePath, StringComparison.Ordinal);
            return Task.FromResult(Json("""{"protocolVersion":1,"ok":true,"ready":true,"capabilities":["prompt","generate","result_ack"]}"""));
        });
        var recipe = new GenerationRecipe(Seed: 42);

        var result = await client.SendAsync(
            ForgeBridgeProtocol.DefaultUrl,
            new ForgeBridgeSendRequest("blue_hair", ForgeNegativeMode.Replace, "lowres", ForgeBridgeAction.ApplyRecipe, recipe));

        Assert.False(result.Success);
        Assert.Equal("upgrade", result.ErrorCode);
        Assert.Contains("生成レシピ", result.Status);
    }

    [Fact]
    public async Task RecipeApplySendsOnlyPresentSettingsAndWaitsForAck()
    {
        string? posted = null;
        string? requestId = null;
        var client = Client(async (request, cancellationToken) =>
        {
            var path = request.RequestUri!.AbsolutePath;
            if (request.Method == HttpMethod.Get && path.EndsWith("/health", StringComparison.Ordinal))
                return Json("""{"protocolVersion":1,"ok":true,"ready":true,"capabilities":["prompt","generate","result_ack","recipe_settings"]}""");

            if (request.Method == HttpMethod.Post && path.EndsWith("/prompt", StringComparison.Ordinal))
            {
                posted = await request.Content!.ReadAsStringAsync(cancellationToken);
                using var document = JsonDocument.Parse(posted);
                requestId = document.RootElement.GetProperty("requestId").GetString();
                return Json($$"""{"protocolVersion":1,"accepted":true,"requestId":"{{requestId}}"}""");
            }

            if (request.Method == HttpMethod.Get && path.EndsWith("/result/" + requestId, StringComparison.Ordinal))
                return Json("""{"protocolVersion":1,"result":{"success":true,"error":""}}""");

            throw new InvalidOperationException(path);
        });

        var recipe = new GenerationRecipe(
            Model: "manual-model",
            Seed: 42,
            Steps: 20,
            Sampler: "Euler a",
            Scheduler: "Karras",
            Cfg: 5m);
        var result = await client.SendAsync(
            ForgeBridgeProtocol.DefaultUrl,
            new ForgeBridgeSendRequest("blue_hair", ForgeNegativeMode.Replace, "lowres", ForgeBridgeAction.ApplyRecipe, recipe));

        Assert.True(result.Success);
        Assert.Equal("Forgeへレシピを適用しました", result.Status);
        using var payload = JsonDocument.Parse(posted!);
        Assert.Equal("apply_recipe", payload.RootElement.GetProperty("action").GetString());
        var settings = payload.RootElement.GetProperty("settings");
        Assert.Equal(42, settings.GetProperty("seed").GetInt64());
        Assert.Equal(20, settings.GetProperty("steps").GetInt32());
        Assert.Equal(5m, settings.GetProperty("cfg").GetDecimal());
        Assert.False(settings.TryGetProperty("model", out _));
        Assert.False(settings.TryGetProperty("sampler", out _));
        Assert.False(settings.TryGetProperty("scheduler", out _));
        Assert.False(settings.TryGetProperty("width", out _));
    }

    [Fact]
    public async Task ManualChoiceOnlyRecipeCannotRunAutomaticApply()
    {
        var client = Client((_, _) => throw new InvalidOperationException("HTTP must not be called"));
        var result = await client.SendAsync(
            ForgeBridgeProtocol.DefaultUrl,
            new ForgeBridgeSendRequest(
                "blue_hair",
                ForgeNegativeMode.Replace,
                "lowres",
                ForgeBridgeAction.ApplyRecipe,
                new GenerationRecipe(Model: "manual-model", Sampler: "Euler a", Scheduler: "Karras")));

        Assert.False(result.Success);
        Assert.Equal("recipe_empty", result.ErrorCode);
        Assert.Contains("自動適用", result.Status);
    }

    [Fact]
    public async Task RecipeGenerateUsesSavedPositiveNegativeAndSettings()
    {
        var fake = new RecordingBridge();
        var vm = new ForgeViewModel(fake, () => { }, () => true, () => "current_prompt", _ => { }, () => { });
        var recipe = new GenerationRecipe("model", 99, 12, "Euler a", "Automatic", 5m, 1024, 1024);
        var preset = new GenerationPreset(Guid.NewGuid(), "r", "", "saved_positive", "saved_negative", recipe);

        await vm.GenerateRecipeAsync(preset, CancellationToken.None);

        var request = Assert.IsType<ForgeBridgeSendRequest>(fake.Request);
        Assert.Equal("saved_positive", request.Positive);
        Assert.Equal("saved_negative", request.Negative);
        Assert.Equal(ForgeBridgeAction.SendAndGenerate, request.Action);
        Assert.Equal(recipe, request.Recipe);
    }

    private static ForgeBridgeClient Client(Func<HttpRequestMessage, CancellationToken, Task<HttpResponseMessage>> handler) =>
        new(new HttpClient(new StubHandler(handler)));

    private static HttpResponseMessage Json(string json) =>
        new(HttpStatusCode.OK) { Content = new StringContent(json, Encoding.UTF8, "application/json") };

    private sealed class StubHandler(Func<HttpRequestMessage, CancellationToken, Task<HttpResponseMessage>> handler) : HttpMessageHandler
    {
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken) =>
            handler(request, cancellationToken);
    }

    private sealed class RecordingBridge : IForgeBridgeClient
    {
        public ForgeBridgeSendRequest? Request { get; private set; }

        public Task<ForgeBridgeResult> SendAsync(string baseUrl, ForgeBridgeSendRequest request, CancellationToken cancellationToken = default)
        {
            Request = request;
            return Task.FromResult(new ForgeBridgeResult(true, "ok"));
        }
    }
}
