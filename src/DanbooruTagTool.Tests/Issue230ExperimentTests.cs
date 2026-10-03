using System.IO;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue230ExperimentTests
{
    private static RecipeSnapshot Baseline() => new("portrait, blue_hair", "text", new("fixture", 1, 8, "Euler", "Karras", 4, 512, 640, "abc123"));
    private static ExperimentSetup Setup(ExperimentVariable kind = ExperimentVariable.Cfg, string target = "", params string[] values) =>
        new("controlled", "test hypothesis", Baseline(), new(kind, target, values.Length == 0 ? ["4", "6"] : values), null, [1, 2]);
    [Fact]
    public void TwoDimensionalMultipleSeedsFixEveryOtherFieldAndReproduceStoredTrials()
    {
        var s = Setup() with { Y = new(ExperimentVariable.Steps, "", ["6", "8"]), Repetitions = 2 };
        var p = ExperimentPlanner.Build(s); Assert.Equal(16, p.Trials.Count); ExperimentPlanner.Validate(p);
        Assert.Equal(16, p.Trials.Select(t => t.Id).Distinct().Count());
        foreach (var t in p.Trials)
        {
            Assert.Equal(p.BaselineId, GenerationRecipeDerivation.Read(t.Requested.Recipe.SourceParameters)!.ParentId);
            Assert.Equal(p.Setup.Baseline.Positive, t.Requested.Positive); Assert.Equal("abc123", t.Requested.Recipe.ModelHash);
            Assert.Contains(t.Seed, p.Setup.Seeds); Assert.Equal(t.Seed, t.Requested.Recipe.Seed);
        }
        ExperimentPlanner.Validate(System.Text.Json.JsonSerializer.Deserialize<ExperimentPlan>(ExperimentPlanner.Json(p))!);
        var changed = p.Trials[0] with { Requested = p.Trials[0].Requested with { Negative = "different" } };
        Assert.Throws<InvalidDataException>(() => ExperimentPlanner.Validate(p with { Trials = new[] { changed }.Concat(p.Trials.Skip(1)).ToArray() }));
    }
    [Theory]
    [InlineData(ExperimentVariable.Positive, "portrait", "landscape", "landscape, blue_hair")]
    [InlineData(ExperimentVariable.Negative, "text", "watermark", "portrait, blue_hair")]
    [InlineData(ExperimentVariable.TagWeight, "blue_hair", "1.2", "portrait, (blue_hair:1.2)")]
    [InlineData(ExperimentVariable.Sampler, "", "Euler a", "portrait, blue_hair")]
    [InlineData(ExperimentVariable.Scheduler, "", "Automatic", "portrait, blue_hair")]
    public void ExplicitVariablesUseExistingPromptAndRecipe(ExperimentVariable kind, string target, string value, string positive)
    {
        var p = ExperimentPlanner.Build(Setup(kind, target, value)); Assert.Equal(positive, p.Trials[0].Requested.Positive);
        if (kind == ExperimentVariable.Negative) Assert.Equal("watermark", p.Trials[0].Requested.Negative);
        ExperimentPlanner.Validate(p);
    }
    [Theory]
    [InlineData("4", "4.0")]
    [InlineData("4", "{4|6}")]
    [InlineData("4", "__wildcard__")]
    [InlineData("4", "31")]
    public void RejectsDuplicatesTemplatesAndInvalidBoundsBeforeExecution(string a, string b) =>
        Assert.Throws<ArgumentException>(() => ExperimentPlanner.Build(Setup(ExperimentVariable.Cfg, "", a, b)));
    [Fact]
    public void CapAndSeedDuplicatesAreRejectedWithoutExpansion()
    {
        Assert.Throws<ArgumentException>(() => ExperimentPlanner.Build(Setup() with { Seeds = [1, 1] }));
        Assert.Throws<ArgumentException>(() => ExperimentPlanner.Build(Setup() with { Seeds = [-1] }));
        Assert.Throws<ArgumentException>(() => ExperimentPlanner.Build(Setup() with { X = new(ExperimentVariable.Cfg, "", Enumerable.Range(0, 16).Select(i => i.ToString()).ToArray()), Y = new(ExperimentVariable.Steps, "", ["1", "2", "3"]) }));
        Assert.Throws<ArgumentException>(() => ExperimentPlanner.Build(Setup(ExperimentVariable.Steps, "", "1.5")));
        Assert.Throws<ArgumentException>(() => ExperimentPlanner.Build(Setup() with { Baseline = Baseline() with { Positive = "{portrait|landscape}" } }));
        Assert.Throws<ArgumentException>(() => ExperimentPlanner.Build(Setup() with { Baseline = Baseline() with { Negative = "__unbounded__" } }));
    }
    [Fact]
    public void LoRAUsesFullFileConstraintAndChangingPromptCannotChangeFixedLoRA()
    {
        var identity = new GenerationLoraIdentity("fixture", "123456789abc", new string('a', 64), .35m);
        var s = Setup(ExperimentVariable.LoraWeight, "fixture", "0.3", "0.4");
        s = s with { Baseline = s.Baseline with { Positive = s.Baseline.Positive + ", <lora:fixture:0.35>", Recipe = s.Baseline.Recipe with { SourceParameters = [new(GenerationLoraProvenance.ReceiptKey, ExperimentPlanner.Json(new[] { identity }))] } } };
        var p = ExperimentPlanner.Build(s); Assert.Equal(new string('a', 64), GenerationLoraProvenance.Expected(p.Trials[0].Requested.Recipe.SourceParameters).Single().FileSha256);
        Assert.Throws<ArgumentException>(() => ExperimentPlanner.Build(s with { X = new(ExperimentVariable.Positive, "<lora:fixture:0.35>", ["<lora:fixture:0.5>"]) }));
        Assert.Throws<ArgumentException>(() => ExperimentPlanner.Build(s with { Baseline = s.Baseline with { Recipe = s.Baseline.Recipe with { SourceParameters = null } } }));
    }
    [Fact]
    public void StoreClaimsOnceKeepsFailuresRerunsAndHumanEvaluationAcrossReopen()
    {
        using var d = new TempDirectory(); var path = Path.Combine(d.Path, "experiment-lab.db"); var store = new ExperimentStore(path); var p = ExperimentPlanner.Build(Setup()); store.Save(p);
        store.CreateRun(p.Id); var a = store.Attempts(p.Id)[0]; Assert.True(store.Claim(a.Id)); Assert.False(store.Claim(a.Id));
        var png = new GenerationMetadataSnapshot("fixture.png", "raw", "portrait", "text", []);
        store.Complete(a.Id, new(true, "receipt", "fixture.png", png), 99);
        store.Evaluate(p.Id, a.Id, new(5, true, true, "observed direction / exception"));
        store.SaveObservation(p.Id, new("direction", "exceptions retained"));
        var b = store.Attempts(p.Id)[1]; Assert.True(store.Claim(b.Id)); store.Complete(b.Id, new(false, "timeout / no retry"), null);
        store.CreateRun(p.Id); var reopened = new ExperimentStore(path); Assert.Equal(8, reopened.Attempts(p.Id).Count);
        var previous = reopened.Attempts(p.Id).Single(x => x.Id == a.Id); Assert.Equal(99, previous.LibraryImageId); Assert.True(previous.Evaluation!.Winner);
        Assert.Equal(5, previous.Evaluation.Rating); Assert.Equal("Failed", reopened.Attempts(p.Id).Single(x => x.Id == b.Id).Status);
        Assert.Equal(ExperimentPlanner.Json(p), ExperimentPlanner.Json(reopened.Load(p.Id)));
        Assert.Equal("exceptions retained", reopened.Observation(p.Id).Exceptions); Assert.Contains("AutoPromoteToKnowledge\":false", reopened.Evidence(p.Id));
        Assert.Throws<InvalidDataException>(() => reopened.Complete(a.Id, new(false, "overwrite"), null));
    }
    [Fact]
    public void WinnerIsScopedToSameRunSeedAndRepetitionWithoutInferringQuality()
    {
        using var d = new TempDirectory(); var st = new ExperimentStore(Path.Combine(d.Path, "experiment-lab.db")); var p = ExperimentPlanner.Build(Setup()); st.Save(p); st.CreateRun(p.Id);
        var rows = st.Attempts(p.Id); foreach (var a in rows) { st.Claim(a.Id); st.Complete(a.Id, new(true, "ok", "x", new("x", "", "", "", [])), 1); }
        st.Evaluate(p.Id, rows[0].Id, new(Winner: true)); st.Evaluate(p.Id, rows[2].Id, new(Winner: true)); st.Evaluate(p.Id, rows[1].Id, new(Winner: true));
        rows = st.Attempts(p.Id); Assert.False(rows[0].Evaluation!.Winner); Assert.True(rows[1].Evaluation!.Winner); Assert.True(rows[2].Evaluation!.Winner);
    }
    [Fact]
    public async Task FailedTrialStopsBatchWithoutResendAndStartOnlyResumesPendingStoredDefinitions()
    {
        using var d = new TempDirectory(); var api = new FailureApi(); var vm = new MainViewModel(Fixtures.Catalog(), new MemoryStore(), new MemoryClipboard(), paths: new(d.Path), generationApi: api);
        vm.Create.Load(new(Guid.NewGuid(), "baseline", "", Baseline().Positive, Baseline().Negative, Baseline().Recipe), "baseline"); var lab = vm.Experiments!;
        await lab.CaptureBaseline.ExecuteAsync(null); Assert.Equal(0, api.Posts); lab.Save.Execute(null); var id = lab.SelectedExperiment!.Id;
        vm.Workspace.Replace("current editor now different"); await lab.Start.ExecuteAsync(null); Assert.Equal(1, api.Posts); Assert.Equal(Baseline().Positive, api.Requests[0].Positive);
        var st = new ExperimentStore(Path.Combine(d.Path, "UserData", "experiment-lab.db")); Assert.Equal(1, st.Attempts(id).Count(a => a.Status == "Failed")); Assert.Equal(3, st.Attempts(id).Count(a => a.Status == "Pending"));
        await lab.Start.ExecuteAsync(null); Assert.Equal(2, api.Posts); Assert.Equal(2, st.Attempts(id).Count(a => a.Status == "Failed"));
        Assert.All(st.Attempts(id), a => Assert.NotEqual("Running", a.Status)); Assert.False(vm.Forge.RecipeBusy);
    }
    [Fact]
    public async Task AuthoringPreservesRawPromptAxisWhitespace()
    {
        using var d = new TempDirectory(); var vm = new MainViewModel(Fixtures.Catalog(), new MemoryStore(), new MemoryClipboard(), paths: new(d.Path), generationApi: new FailureApi());
        vm.Create.Load(new(Guid.NewGuid(), "baseline", "", Baseline().Positive, Baseline().Negative, Baseline().Recipe), "baseline"); var lab = vm.Experiments!;
        await lab.CaptureBaseline.ExecuteAsync(null); lab.XKind = ExperimentVariable.Positive; lab.XTarget = "portrait"; lab.XValues = "  landscape  "; lab.Save.Execute(null);
        var saved = new ExperimentStore(Path.Combine(d.Path, "UserData", "experiment-lab.db")).Load(lab.SelectedExperiment!.Id);
        Assert.Equal("  landscape  ", saved.Setup.X.Values.Single()); Assert.Equal("  landscape  , blue_hair", saved.Trials[0].Requested.Positive);
    }
    [Fact]
    public async Task ExclusiveExperimentLeaseBlocksSharedCommandsBetweenTrials()
    {
        using var d = new TempDirectory(); var api = new FailureApi(); var vm = new MainViewModel(Fixtures.Catalog(), new MemoryStore(), new MemoryClipboard(), paths: new(d.Path), generationApi: api);
        vm.Forge.BeginExperiment(); Assert.False(vm.Create.Generate.CanExecute(null)); Assert.False(vm.Forge.CheckCapabilities.CanExecute(null));
        await vm.Forge.GenerateRecipeAsync(new(Guid.NewGuid(), "not executed", "", "", "", Baseline().Recipe));
        Assert.Equal(0, api.Posts);
        Assert.Throws<InvalidOperationException>(() => vm.Forge.BeginExperiment()); vm.Forge.EndExperiment(); Assert.True(vm.Forge.RecipeExecutionAvailable);
    }
    [Fact]
    public void AdditiveExperimentSchemaDoesNotMigrateOrWriteExistingUserState()
    {
        using var d = new TempDirectory(); var path = new PortablePaths(d.Path).User; var state = new UserStateStore(path); state.Save(new(Fixtures.Workspace().Snapshot(), new()));
        var bytes = File.ReadAllBytes(path); _ = new ExperimentStore(Path.Combine(d.Path, "UserData", "experiment-lab.db")); Assert.Equal(bytes, File.ReadAllBytes(path));
        using var db = new Microsoft.Data.Sqlite.SqliteConnection("Pooling=False;Data Source=" + Path.Combine(d.Path, "UserData", "experiment-lab.db")); db.Open(); using var command = db.CreateCommand(); command.CommandText = "PRAGMA user_version=99"; command.ExecuteNonQuery(); db.Close();
        Assert.Throws<InvalidDataException>(() => new ExperimentStore(Path.Combine(d.Path, "UserData", "experiment-lab.db")));
    }
    private sealed class FailureApi : IForgeGenerationApiClient
    {
        public int Posts; public List<ForgeApiRequest> Requests = [];
        public Task<ForgeApiCapabilities> ProbeAsync(string url, CancellationToken ct = default) => Task.FromResult(new ForgeApiCapabilities([new("fixture", "fixture", "abc123")], ["Euler"], ["Karras"]));
        public Task<ForgeApiResult> GenerateAsync(string url, ForgeApiRequest r, string dir, CancellationToken ct = default) { Posts++; Requests.Add(r); return Task.FromResult(new ForgeApiResult(false, "fixture failure / no retry")); }
    }
}
