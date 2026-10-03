using System.IO;
using System.Net.Http;
using System.Text.Json;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App;

/// <summary>Opt-in real EXE / Forge / WPF gate, with fresh isolated data. 12 required 1D/2D trials + one bounded rerun.</summary>
public static class ExperimentLabValidation
{
    public static async Task RenderExistingAsync(string specPath, string evidenceRoot, string output)
    {
        var spec = JsonSerializer.Deserialize<ForgeWorkflowSpec>(File.ReadAllText(specPath)) ?? throw new InvalidDataException("spec missing");
        var root = Path.GetFullPath(output);
        if (Directory.Exists(root) || root.StartsWith(Path.GetFullPath(AppContext.BaseDirectory).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new IOException("UI validation requires fresh output outside runtime.");
        Directory.CreateDirectory(Path.Combine(root, "UserData"));
        foreach (var name in new[] { "user.db", "generation-library.db", "experiment-lab.db", "lora-library.db" })
        {
            var source = Path.Combine(evidenceRoot, "UserData", name); if (!File.Exists(source)) continue;
            using var from = new Microsoft.Data.Sqlite.SqliteConnection(new Microsoft.Data.Sqlite.SqliteConnectionStringBuilder { DataSource = source, Mode = Microsoft.Data.Sqlite.SqliteOpenMode.ReadOnly, Pooling = false }.ToString());
            using var to = new Microsoft.Data.Sqlite.SqliteConnection(new Microsoft.Data.Sqlite.SqliteConnectionStringBuilder { DataSource = Path.Combine(root, "UserData", name), Pooling = false }.ToString());
            from.Open(); to.Open(); from.BackupDatabase(to);
        }
        var paths = new PortablePaths(root); var catalog = CatalogDatabase.Open(spec.CatalogPath ?? new PortablePaths(AppContext.BaseDirectory).Catalog);
        var vm = new MainViewModel(catalog, new UserStateStore(paths.User), new NullClipboard(), paths: paths);
        var window = new MainWindow(vm) { WindowState = WindowState.Normal, Width = 1400, Height = 900, Left = -30000, Top = -30000, ShowInTaskbar = false };
        window.Show(); vm.WorkspaceIndex = 1; vm.CreatePageIndex = 4;
        try
        {
            var lab = vm.Experiments!; lab.Reload.Execute(null); lab.SelectedExperiment = lab.Experiments.Single(e => e.Name == "isolated 2D"); lab.SelectedSeed = spec.Seed + 1; lab.Selected = lab.Cells.Last();
            Check(lab.Cells.Count == 4 && lab.Columns == 2 && !vm.CreateComposerVisible, "saved matrix / dedicated Lab controls");
            await Render(window, Path.Combine(root, "matrix-1400.png")); window.Width = 900; window.Height = 600; await Render(window, Path.Combine(root, "matrix-900.png"));
            File.WriteAllText(Path.Combine(root, "ui-result.json"), ExperimentPlanner.Json(new { Result = "PASS", Runtime = Environment.ProcessPath, Posts = 0, ReopenedMatrix = true }));
        }
        finally { window.Close(); }
    }
    public static async Task RunAsync(string specPath, string output)
    {
        var spec = JsonSerializer.Deserialize<ForgeWorkflowSpec>(File.ReadAllText(specPath)) ?? throw new InvalidDataException("spec missing");
        var root = Path.GetFullPath(output);
        if (Directory.Exists(root) || root.StartsWith(Path.GetFullPath(AppContext.BaseDirectory).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
            throw new IOException("Experiment validation owns a fresh directory outside runtime.");
        Directory.CreateDirectory(root); var paths = new PortablePaths(root);
        var catalog = CatalogDatabase.Open(spec.CatalogPath ?? new PortablePaths(AppContext.BaseDirectory).Catalog);
        using var wire = new Wire(root); using var http = new HttpClient(wire) { Timeout = Timeout.InfiniteTimeSpan };
        var api = new CaptureApi(new ForgeGenerationApiClient(http));
        MainViewModel NewVM() => new(catalog, new UserStateStore(paths.User), new NullClipboard(), paths: paths, generationApi: api);
        var vm = NewVM(); var window = new MainWindow(vm) { WindowState = WindowState.Normal, Width = 1400, Height = 900, Left = -30000, Top = -30000, ShowInTaskbar = false };
        window.Show(); vm.WorkspaceIndex = 1; vm.CreatePageIndex = 4;
        try
        {
            vm.Workspace.Replace($"1girl, portrait, outdoors, <lora:{spec.LoraName}:0.35>"); vm.NegativeWorkspace.Replace("text, watermark");
            await vm.Create.RefreshCapabilities.ExecuteAsync(null);
            vm.Create.SelectedForgeModel = vm.Create.ForgeModels.Single(m => m.Hash == spec.ModelHash); vm.Create.ApplyForgeModel.Execute(null);
            vm.Create.Seed = spec.Seed.ToString(System.Globalization.CultureInfo.InvariantCulture); vm.Create.Steps = "6"; vm.Create.Cfg = "4.25";
            vm.Create.Sampler = "Euler"; vm.Create.Scheduler = "Karras"; vm.Create.Width = "512"; vm.Create.Height = "640";
            var lab = vm.Experiments!; await lab.CaptureBaseline.ExecuteAsync(null); Check(lab.BaselineSummary.Contains(spec.LoraFileSha256) || lab.Status.Contains("固定"), lab.Status);
            lab.Name = "isolated 1D"; lab.Hypothesis = "Controlled CFG comparison, not accepted knowledge"; lab.XKind = ExperimentVariable.Cfg; lab.XValues = "4.25\n5"; lab.Seeds = $"{spec.Seed}\n{spec.Seed + 1}";
            Check(lab.Preview.Contains("= 4生成"), lab.Preview); lab.Save.Execute(null); var oneId = lab.SelectedExperiment!.Id;
            var store = new ExperimentStore(Path.Combine(root, "UserData", "experiment-lab.db")); var one = store.Load(oneId);
            Check(api.Requests.Count == 0, "no generation before explicit Start"); await lab.Start.ExecuteAsync(null); Check(api.Requests.Count == 4, lab.Status);
            Validate(store, one, spec, paths); lab.Selected = lab.Cells.First(); lab.Rating = 5; lab.Passed = true; lab.Winner = true; lab.Note = "human fixture evaluation"; lab.Evaluate.Execute(null);
            lab.ObservedDirection = "fixture observation only"; lab.Exceptions = "none hidden"; lab.SaveObservation.Execute(null); lab.ExportEvidence.Execute(null);
            await Render(window, Path.Combine(root, "one-dimensional.png"));
            var reopened = NewVM(); var reopenLab = reopened.Experiments!; reopenLab.Reload.Execute(null); reopenLab.SelectedExperiment = reopenLab.Experiments.Single(e => e.Id == oneId);
            Check(ExperimentPlanner.Json(store.Load(oneId)) == ExperimentPlanner.Json(one) && reopenLab.Cells.First().Attempt.Evaluation?.Rating == 5 && reopenLab.ObservedDirection == "fixture observation only", "reopen exact plan/evaluation/observations");
            reopenLab.XValues = "20\n21"; // Rerun must ignore current draft values.
            api.AfterResult = () => reopenLab.Cancel.Execute(null);
            await reopenLab.Rerun.ExecuteAsync(null); api.AfterResult = null;
            Check(api.Requests.Count == 5 && api.Requests.Last().Recipe.Cfg == one.Trials[0].Requested.Recipe.Cfg, "bounded explicit stored-definition rerun");
            Check(store.Attempts(oneId).Count == 8 && store.Attempts(oneId).Count(a => a.Status == "Succeeded") == 5 && store.Attempts(oneId).Count(a => a.Status == "Pending") == 3, "old attempts retained / cancellation between trials");
            lab.Name = "isolated 2D"; lab.UseY = true; lab.YKind = ExperimentVariable.LoraWeight; lab.YTarget = spec.LoraName; lab.YValues = "0.30\n0.40";
            Check(lab.Preview.Contains("= 8生成"), lab.Preview); lab.Save.Execute(null); var matrixId = lab.SelectedExperiment!.Id; var matrix = store.Load(matrixId);
            await lab.Start.ExecuteAsync(null); Check(api.Requests.Count == 13, lab.Status); Validate(store, matrix, spec, paths);
            Check(lab.Cells.Count == 4 && lab.Columns == 2, "same-seed 2x2 matrix"); lab.SelectedSeed = spec.Seed + 1; Check(lab.Cells.Count == 4, "second seed comparison");
            lab.Selected = lab.Cells.Last(); lab.Rating = 3; lab.Passed = false; lab.Note = "explicit fail / exception"; lab.Evaluate.Execute(null);
            await Render(window, Path.Combine(root, "matrix-1400.png")); window.Width = 900; window.Height = 600; await Render(window, Path.Combine(root, "matrix-900.png"));
            lab.XFilter = 0; Check(lab.Cells.Count == 2 && lab.Columns == 1, "variant filter"); lab.XFilter = -1;
            lab.Selected = lab.Cells.Last(); lab.UseInCreate.Execute(null); Check(vm.Create.TryRecipe(out var restored, out _) && restored?.ModelHash == spec.ModelHash && restored.Seed == spec.Seed + 1, "result → Library Recipe → Create");
            var final = NewVM().Experiments!; final.Reload.Execute(null); final.SelectedExperiment = final.Experiments.Single(e => e.Id == matrixId); final.SelectedSeed = spec.Seed + 1;
            Check(final.Cells.Last().Attempt.Evaluation?.Passed == false && final.Cells.Last().Attempt.Evaluation?.Note == "explicit fail / exception", "matrix evaluation persists");
            File.WriteAllText(Path.Combine(root, "result.json"), ExperimentPlanner.Json(new { Result = "PASS", Runtime = Environment.ProcessPath, Posts = wire.Posts, OneDTrials = 4, MatrixTrials = 8, Seeds = matrix.Setup.Seeds, BoundedRerunPosts = 1,
                ExperimentSchema = ExperimentStore.SchemaVersion, UserSchema = UserStateStore.SchemaVersion, LibrarySchema = GenerationLibraryStore.SchemaVersion,
                OneD = oneId, Matrix = matrixId, Requests = api.Requests, Actual = api.Results, Reopen = "PASS", Evaluation = "PASS", ControlledProvenance = "PASS", AutoKnowledgePromotion = false }));
        }
        finally { window.Close(); }
    }
    private static void Validate(ExperimentStore store, ExperimentPlan plan, ForgeWorkflowSpec spec, PortablePaths paths)
    {
        ExperimentPlanner.Validate(plan); var attempts = store.Attempts(plan.Id); Check(attempts.Count == plan.Trials.Count && attempts.All(a => a.Status == "Succeeded" && a.LibraryImageId is not null), "all results linked to Library");
        var library = new GenerationLibraryStore(paths.GenerationLibrary);
        foreach (var a in attempts)
        {
            var t = plan.Trials.Single(t => t.Id == a.TrialId); var actual = library.Metadata(a.LibraryImageId!.Value)!;
            Check(actual.RawInfotext == a.Receipt!.Metadata!.RawInfotext && actual.Value("Model hash") == spec.ModelHash, "PNG/receipt/Library/model identity");
            Check(GenerationLoraProvenance.Expected(actual.Parameters).Single().FileSha256 == spec.LoraFileSha256, "full-file LoRA identity");
            Check(ExperimentPlanner.Json(GenerationRecipeDerivation.Read(actual.Parameters)) == ExperimentPlanner.Json(GenerationRecipeDerivation.Read(t.Requested.Recipe.SourceParameters)), "exact parent/request/changed fields");
        }
    }
    private static async Task Render(MainWindow window, string path)
    {
        await window.Dispatcher.InvokeAsync(() => { }, DispatcherPriority.ContextIdle); window.UpdateLayout();
        var bitmap = new RenderTargetBitmap((int)window.ActualWidth, (int)window.ActualHeight, 96, 96, PixelFormats.Pbgra32); bitmap.Render(window);
        var encoder = new PngBitmapEncoder(); encoder.Frames.Add(BitmapFrame.Create(bitmap)); using var file = File.Create(path); encoder.Save(file);
    }
    private static void Check(bool pass, string gate) { if (!pass) throw new InvalidDataException("Experiment E2E: " + gate); }
    private sealed class NullClipboard : IClipboardService { public string Read() => ""; public void Write(string value) { } }
    private sealed class Wire(string root) : DelegatingHandler(new HttpClientHandler { UseProxy = false, AllowAutoRedirect = false })
    {
        public int Posts;
        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
        { if (request.Method == HttpMethod.Post) await File.WriteAllTextAsync(Path.Combine(root, $"sent-{++Posts}.json"), await request.Content!.ReadAsStringAsync(ct), ct); return await base.SendAsync(request, ct); }
    }
    private sealed class CaptureApi(IForgeGenerationApiClient inner) : IForgeGenerationApiClient
    {
        public List<ForgeApiRequest> Requests = []; public List<ForgeApiResult> Results = []; public Action? AfterResult;
        public Task<RecipeSnapshot> PinRecipeIdentityAsync(string url, RecipeSnapshot snapshot, CancellationToken ct = default) => inner.PinRecipeIdentityAsync(url, snapshot, ct);
        public Task<ForgeApiCapabilities> ProbeAsync(string url, CancellationToken ct = default) => inner.ProbeAsync(url, ct);
        public async Task<ForgeApiResult> GenerateAsync(string url, ForgeApiRequest r, string path, CancellationToken ct = default)
        { Requests.Add(r); var result = await inner.GenerateAsync(url, r, path, ct); Results.Add(result); AfterResult?.Invoke(); return result; }
    }
}
