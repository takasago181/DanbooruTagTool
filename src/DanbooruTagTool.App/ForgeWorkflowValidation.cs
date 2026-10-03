using System.IO;
using System.Net.Http;
using System.Text.Json;
using System.Windows;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

namespace DanbooruTagTool.App;

public sealed record ForgeWorkflowSpec(string ModelHash, string LoraName, string LoraFileSha256,
    long Seed, string TagQuery = "青い髪", string CanonicalTag = "blue_hair", string? CatalogPath = null);

/// <summary>Explicit opt-in, actual executable workflow gate. Owns only a fresh isolated output.</summary>
public static class ForgeWorkflowValidation
{
    public static async Task RunAsync(string specPath, string output)
    {
        var spec = JsonSerializer.Deserialize<ForgeWorkflowSpec>(File.ReadAllText(specPath)) ?? throw new InvalidDataException("Missing workflow spec.");
        if (spec.Seed < 0 || spec.Seed == long.MaxValue || string.IsNullOrWhiteSpace(spec.ModelHash) || string.IsNullOrWhiteSpace(spec.LoraName) || spec.LoraFileSha256.Length != 64)
            throw new InvalidDataException("Invalid explicit workflow spec.");
        var root = Path.GetFullPath(output);
        if (root.StartsWith(Path.GetFullPath(AppContext.BaseDirectory).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase) || Directory.Exists(root))
            throw new IOException("Workflow validation requires a fresh output outside the runtime.");
        Directory.CreateDirectory(root);
        var paths = new PortablePaths(root);
        var catalog = CatalogDatabase.Open(spec.CatalogPath ?? new PortablePaths(AppContext.BaseDirectory).Catalog);
        using var wire = new Wire(root); using var http = new HttpClient(wire) { Timeout = Timeout.InfiniteTimeSpan };
        var api = new CaptureApi(new ForgeGenerationApiClient(http));
        var vm = new MainViewModel(catalog, new UserStateStore(paths.User), new ProbeClipboard(), paths: paths, generationApi: api);
        var window = new MainWindow(vm) { Left = -30000, Top = -30000, ShowInTaskbar = false, Width = 1200, Height = 800 };
        window.Show(); window.UpdateLayout();
        try
        {
            vm.Workspace.Replace("1girl, portrait, outdoors"); vm.Query = spec.TagQuery; vm.RefreshResults();
            var tag = vm.Results.Single(e => e.English == spec.CanonicalTag);
            tag.Add.Execute(null); Check(vm.English.Contains(spec.CanonicalTag), "Japanese discovery / explicit canonical add");
            vm.Workspace.Replace(vm.English + $", <lora:{spec.LoraName}:0.35>"); vm.NegativeWorkspace.Replace("text, watermark");
            await vm.Create.RefreshCapabilities.ExecuteAsync(null);
            vm.Create.SelectedForgeModel = vm.Create.ForgeModels.Single(m => m.Hash == spec.ModelHash);
            Check(vm.Create.ApplyForgeModel.CanExecute(null), "explicit Forge selection"); vm.Create.ApplyForgeModel.Execute(null);
            vm.Create.Seed = spec.Seed.ToString(System.Globalization.CultureInfo.InvariantCulture); vm.Create.Steps = "8"; vm.Create.Cfg = "4.75";
            vm.Create.Sampler = "Euler"; vm.Create.Scheduler = "Karras"; vm.Create.Width = "512"; vm.Create.Height = "640";
            await vm.Create.GenerateAsync(); var first = api.Results.Single(); Check(first.Success && first.Metadata is not null && wire.Posts == 1, first.Status);
            var library = vm.GenerationLibrary!;
            library.Selected = library.Images.Single(i => i.Image.NormalizedPath == first.ImagePath); library.LoadInCreate.Execute(null);
            Check(vm.Create.TryRecipe(out var restored, out _), "Library → Create");
            var parent = GenerationRecipeDerivation.Read(restored!.SourceParameters)!;
            Check(parent.ParentImageSha256 is not null && parent.Parent.Positive == first.Metadata!.Positive, "image parent identity");
            vm.Workspace.Replace(vm.Create.Positive.Replace(":0.35>", ":0.4>") + ", sunset"); vm.Create.Seed = (spec.Seed + 1).ToString(System.Globalization.CultureInfo.InvariantCulture); vm.Create.Steps = "6";
            Check(vm.Create.Changed && vm.Create.DerivationSummary.Contains("LoRA") && vm.Create.DerivationSummary.Contains("Seed"), "explicit edits/diff");
            vm.Create.SaveName = "isolated derivative"; vm.Create.Save.Execute(null);
            var reopened = new MainViewModel(catalog, new UserStateStore(paths.User), new ProbeClipboard(), paths: paths, generationApi: api);
            reopened.Create.Load(reopened.Presets.Single(), "reopened derivative"); Check(!reopened.Create.AllowDerivative, "consent reset"); Check(reopened.Create.TryRecipe(out var next, out _), "restart snapshot");
            var expected = GenerationRecipeDerivation.Read(next!.SourceParameters)!; Check(expected.ParentId == parent.ParentId, "parent retained");
            reopened.Create.AllowDerivative = true; await reopened.Create.GenerateAsync(); var child = api.Results.Last();
            Check(child.Success && child.Metadata is not null && wire.Posts == 2, child.Status);
            var stored = new GenerationLibraryStore(paths.GenerationLibrary); var image = stored.Query(new(Seed: spec.Seed + 1)).Images.Single(); var readback = stored.Metadata(image.Id)!;
            Check(readback.RawInfotext == child.Metadata!.RawInfotext && JsonSerializer.Serialize(GenerationRecipeDerivation.Read(readback.Parameters)) == JsonSerializer.Serialize(expected), "PNG / Library / parent and changes");
            foreach (var result in api.Results)
            {
                var lora = GenerationLoraProvenance.Expected(result.Metadata!.Parameters).Single();
                Check(lora.FileSha256 == spec.LoraFileSha256 && result.Metadata.Value("Model hash") == spec.ModelHash, "model / full-file LoRA identity");
            }
            reopened.Create.LoadImage(readback, "generated derivative"); Check(reopened.Create.TryRecipe(out var final, out _), "derivative restoration");
            Check(GenerationRecipeDerivation.Read(final!.SourceParameters)!.Parent.Recipe.Seed == spec.Seed + 1, "next direct parent");
            File.WriteAllText(Path.Combine(root, "result.json"), JsonSerializer.Serialize(new { Result = "PASS", Runtime = Environment.ProcessPath,
                Posts = wire.Posts, Discovery = spec.TagQuery, Tag = spec.CanonicalTag, Requested = api.Requests, Actual = api.Results,
                UserSchema = UserStateStore.SchemaVersion, LibrarySchema = GenerationLibraryStore.SchemaVersion, Parent = expected.ParentId }, new JsonSerializerOptions { WriteIndented = true }));
        }
        finally { window.Close(); }
    }
    private static void Check(bool pass, string gate) { if (!pass) throw new InvalidDataException("Forge E2E: " + gate); }
    private sealed class ProbeClipboard : IClipboardService { public string Read() => ""; public void Write(string text) { } }
    private sealed class Wire(string root) : DelegatingHandler(new HttpClientHandler { UseProxy = false, AllowAutoRedirect = false })
    {
        public int Posts;
        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
        {
            if (request.Method == HttpMethod.Post)
            { Posts++; await File.WriteAllTextAsync(Path.Combine(root, $"sent-{Posts}.json"), await request.Content!.ReadAsStringAsync(ct), ct); }
            return await base.SendAsync(request, ct);
        }
    }
    private sealed class CaptureApi(IForgeGenerationApiClient inner) : IForgeGenerationApiClient
    {
        public List<ForgeApiRequest> Requests { get; } = []; public List<ForgeApiResult> Results { get; } = [];
        public Task<ForgeApiCapabilities> ProbeAsync(string url, CancellationToken ct = default) => inner.ProbeAsync(url, ct);
        public async Task<ForgeApiResult> GenerateAsync(string url, ForgeApiRequest request, string path, CancellationToken ct = default)
        { Requests.Add(request); var result = await inner.GenerateAsync(url, request, path, ct); Results.Add(result); return result; }
    }
}
