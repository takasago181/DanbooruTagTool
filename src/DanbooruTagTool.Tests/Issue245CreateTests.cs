using System.IO;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue245CreateTests
{
    private static GenerationPreset Preset() => new(Guid.NewGuid(), "source", "", "blue_hair, BREAK, raw phrase", "lowres", new("sample", 42, 20, "Euler a", "Karras", 5, 512, 768));
    [Theory]
    [InlineData(0, 1, 0)] [InlineData(1, 0, 0)] [InlineData(2, 2, 0)] [InlineData(3, 2, 1)]
    public void OldNavigationRestoresWithoutReinterpretingUserData(int legacy, int shell, int subtype)
    {
        var store = new MemoryStore { State = new(Fixtures.Workspace().Snapshot(), new(Workspace: legacy)) };
        var vm = Fixtures.Vm(store);
        Assert.Equal(shell, vm.ShellWorkspaceIndex); Assert.Equal(subtype, vm.LibrarySubtypeIndex);
        vm.ShellWorkspaceIndex = 0;
        Assert.Equal(1, store.State!.Ui.Workspace);
        vm.ShellWorkspaceIndex = 2; vm.LibrarySubtypeIndex = 1;
        Assert.Equal(3, store.State!.Ui.Workspace);
        Assert.Equal(1, Fixtures.Vm(store).LibrarySubtypeIndex);
    }
    [Fact]
    public void ExplicitLoadUsesSharedWorkspacesAndTracksEditsWithoutMutatingSavedSource()
    {
        var vm = Fixtures.Vm(); var p = Preset();
        vm.Workspace.Replace("smile"); vm.NegativeWorkspace.Replace("old negative");
        vm.Create.SelectedPreset = p;
        Assert.Equal("smile", vm.English); // selection alone does not apply anything
        vm.Create.LoadPreset.Execute(null);
        Assert.Equal(p.Positive, vm.Create.Positive); Assert.Equal(p.Negative, vm.Create.Negative);
        Assert.False(vm.Create.Changed); Assert.Contains("source", vm.Create.SourceSummary);
        vm.Create.Steps = "21"; Assert.True(vm.Create.Changed); Assert.Equal(20, p.Recipe!.Steps);
        vm.Create.Steps = "20"; Assert.False(vm.Create.Changed);
        vm.Negative.Undo.Execute(null); Assert.Equal("old negative", vm.Create.Negative);
        Assert.True(vm.Create.Changed); Assert.Equal(p.Positive, vm.Create.Positive);
        vm.Undo.Execute(null); Assert.Equal("smile", vm.Create.Positive);
    }
    [Fact]
    public async Task CurrentSnapshotGeneratesWithoutSavingPresetAndFailureNeverFallsBack()
    {
        using var d = new TempDirectory(); var api = new RecordingApi();
        var vm = new MainViewModel(Fixtures.Catalog(), new MemoryStore(), new MemoryClipboard(), paths: new(d.Path), generationApi: api);
        vm.Create.Load(Preset(), "画像 fixture.png");
        Assert.True(vm.Create.CanGenerate); Assert.Empty(vm.Presets);
        var task = vm.Create.GenerateAsync();
        Assert.True(vm.Forge.RecipeBusy); Assert.False(vm.Create.Generate.CanExecute(null));
        Assert.Equal("lowres", api.Request!.Negative); Assert.Equal(42, api.Request.Recipe.Seed);
        vm.Create.Seed = "99"; // snapshot already captured even if invoked outside UI
        api.Complete.SetResult(new(false, "round-trip mismatch")); await task;
        Assert.Equal(42, api.Request.Recipe.Seed); Assert.Equal(1, api.Generations);
        Assert.Empty(vm.Presets); Assert.Contains("error", vm.Forge.ConnectionStatus);
        Assert.Contains("round-trip mismatch", vm.Forge.RecipeStatus);
    }
    [Fact]
    public async Task InvalidOrDirectEditingStateNeverGeneratesAndCapabilitiesAreExplicit()
    {
        using var d = new TempDirectory(); var api = new RecordingApi();
        var vm = new MainViewModel(Fixtures.Catalog(), new MemoryStore(), new MemoryClipboard(), paths: new(d.Path), generationApi: api);
        Assert.Equal(0, api.Probes); Assert.False(vm.Create.CanGenerate);
        vm.Create.Load(Preset(), "Preset"); vm.Create.Width = "513";
        await vm.Create.GenerateAsync(); Assert.Equal(0, api.Generations);
        vm.Create.Width = "512"; vm.Negative.StartDirect.Execute(null);
        await vm.Create.GenerateAsync(); Assert.Equal(0, api.Generations);
        vm.Negative.CancelDirect.Execute(null);
        await vm.Forge.CheckCapabilities.ExecuteAsync(null);
        Assert.Equal(1, api.Probes); Assert.Contains("実loaded modelは未確認", vm.Forge.CapabilityStatus);
        vm.PresetManagementOpen = true; Assert.False(vm.Create.CanGenerate);
    }
    [Fact]
    public void SaveCreatesIndependentSnapshotAndManagementDraftNeverSilentlySynchronizes()
    {
        var store = new MemoryStore(); var vm = Fixtures.Vm(store); var p = Preset();
        vm.Presets.Add(p); vm.Create.Load(p, "Preset"); vm.Create.Seed = "43";
        vm.Create.SaveName = "copy"; vm.Create.Save.Execute(null);
        Assert.Equal(2, vm.Presets.Count); Assert.Equal(42, p.Recipe!.Seed);
        Assert.Equal(43, store.State!.Presets!.Last().Recipe!.Seed);
        vm.SelectedPreset = p; vm.PresetSeed = "100";
        Assert.Equal("43", vm.Create.Seed); Assert.Equal(42, p.Recipe.Seed);
        Assert.False(vm.Create.Changed);
    }
    [Fact]
    public void FailedSaveRetainsWorkingValuesAndExistingPresetsWithoutFalseSuccess()
    {
        var vm = new MainViewModel(Fixtures.Catalog(), new FailingStore(), new MemoryClipboard());
        var p = Preset(); vm.Presets.Add(p); vm.Create.Load(p, "Preset");
        vm.Create.Seed = "45"; vm.Create.SaveName = "unsaved"; vm.Create.Save.Execute(null);
        Assert.Single(vm.Presets); Assert.Same(p, vm.Presets.Single()); Assert.Equal("45", vm.Create.Seed);
        Assert.Contains("自動保存できません", vm.Status); Assert.True(vm.Create.Changed);
    }
    private sealed class FailingStore : IUserStateStore
    { public UserState? Load() => null; public void Save(UserState state) => throw new IOException("fixture disk failure"); }
    [Theory]
    [InlineData(false)] [InlineData(true)]
    public async Task WorkingCreateRunsRealApiAdapterPngRoundTripAndIndexesSuccessOrFailure(bool mismatch)
    {
        using var d = new LibraryFixture();
        var server = new Issue228ForgeApiTests.FakeApi(d, (path, info) =>
            typeof(DanbooruTagTool.App.GenerationLibraryValidation).GetMethod("WriteFixture", System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic)!.Invoke(null, [path, info]));
        server.Info = "blue_hair\nNegative prompt: lowres\nSteps: 20, Sampler: Euler a, Schedule type: Karras, CFG scale: " + (mismatch ? "6" : "5") + ", Seed: 42, Size: 512x768, Model: sample, Model hash: abc";
        var api = new ForgeGenerationApiClient(new System.Net.Http.HttpClient(server));
        var vm = new MainViewModel(Fixtures.Catalog(), new MemoryStore(), new MemoryClipboard(), paths: new(d.Path), generationApi: api);
        vm.Create.Load(Preset() with { Positive = "blue_hair" }, "working fixture");
        await vm.Create.GenerateAsync();
        Assert.Equal(1, server.Posts); Assert.Empty(vm.Presets);
        var payload = System.Text.Json.JsonDocument.Parse(server.Payload!).RootElement;
        Assert.Equal("blue_hair", payload.GetProperty("prompt").GetString()); Assert.Equal("lowres", payload.GetProperty("negative_prompt").GetString());
        Assert.Equal(1, payload.GetProperty("batch_size").GetInt32()); Assert.Equal(1, payload.GetProperty("n_iter").GetInt32());
        var store = new GenerationLibraryStore(Path.Combine(d.Path, "UserData", "generation-library.db"));
        var image = store.Query(new(Seed: 42)).Images.Single();
        Assert.True(File.Exists(image.NormalizedPath));
        Assert.Equal(mismatch ? 6m : 5m, GenerationRecipe.FromMetadata(store.Metadata(image.Id)!).Cfg);
        Assert.Equal(mismatch, vm.Forge.RecipeStatus.Contains("照合失敗"));
        Assert.Contains(mismatch ? "error" : "idle", vm.Forge.ConnectionStatus);
    }
    private sealed class RecordingApi : IForgeGenerationApiClient
    {
        public int Probes, Generations;
        public ForgeApiRequest? Request;
        public TaskCompletionSource<ForgeApiResult> Complete = new(TaskCreationOptions.RunContinuationsAsynchronously);
        public Task<ForgeApiCapabilities> ProbeAsync(string url, CancellationToken ct = default)
        { Probes++; return Task.FromResult(new ForgeApiCapabilities([new("sample", "sample", "abc")], ["Euler a"], ["Karras"])); }
        public Task<ForgeApiResult> GenerateAsync(string url, ForgeApiRequest request, string output, CancellationToken ct = default)
        { Generations++; Request = request; return Complete.Task; }
    }
}
