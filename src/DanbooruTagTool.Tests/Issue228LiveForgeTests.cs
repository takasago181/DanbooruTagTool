using System.IO;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class ForgeSpikeFactAttribute : FactAttribute
{
    public ForgeSpikeFactAttribute() { if (Environment.GetEnvironmentVariable("DTT_FORGE_SPIKE_URL") is null) Skip = "Explicit bounded real Forge API spike only."; }
}
public class Issue228LiveForgeTests
{
    [ForgeSpikeFact]
    public async Task TwoBoundedGenerationsRoundTripAndEnterLibrary()
    {
        var url = Environment.GetEnvironmentVariable("DTT_FORGE_SPIKE_URL")!;
        var root = Environment.GetEnvironmentVariable("DTT_FORGE_SPIKE_OUTPUT")!;
        if (Directory.Exists(root) && Directory.EnumerateFileSystemEntries(root).Any()) throw new IOException("Spike output must be fresh.");
        var images = Path.Combine(root, "Images"); var api = new ForgeGenerationApiClient(); var caps = await api.ProbeAsync(url);
        var model = caps.Models.Single(m => m.Name == "chenkinNoobXLCKXL_v05");
        var firstPath = Environment.GetEnvironmentVariable("DTT_FORGE_SPIKE_FIRST_PNG")!;
        var first = ForgePngGenerationMetadata.Read(firstPath);
        var firstRequest = new ForgeApiRequest("a blue ceramic teapot on a wooden table, DTT_RECIPE_SPIKE_POSITIVE", "text, watermark, DTT_RECIPE_SPIKE_NEGATIVE", new(model.Title, 123456789, 9, "Euler", "Karras", 5.5m, 512, 640));
        Assert.Empty(ForgeGenerationApiClient.Compare(firstRequest, model, first));
        Directory.CreateDirectory(images); File.Copy(firstPath, Path.Combine(images, "spike-first.png"));
        var results = new List<ForgeApiResult>();
        for (var i = 0; i < 2; i++)
        {
            var request = new ForgeApiRequest("a blue ceramic teapot on a wooden table, DTT_RECIPE_SPIKE_POSITIVE", "text, watermark, DTT_RECIPE_SPIKE_NEGATIVE", new(model.Title, 123456790 + i, 3, "Euler", "Karras", 4.75m, 256, 320));
            var result = await api.GenerateAsync(url, request, images); results.Add(result); Assert.True(result.Success, result.Status);
        }
        Assert.Equal(3, Directory.GetFiles(images, "*.png").Length);
        var store = new GenerationLibraryStore(Path.Combine(root, "UserData", "generation-library.db")); var scanRoot = store.AddRoot(images);
        var scan = new GenerationLibraryScanner(store, new PngGenerationMetadataReader()).Scan(scanRoot);
        Assert.True(scan.Complete); Assert.Equal(3, scan.Added); Assert.Equal(0, scan.Errors);
        for (var i = 0; i < 3; i++) Assert.Single(store.Query(new(Seed: 123456789 + i)).Images);
        File.WriteAllText(Path.Combine(root, "roundtrip.json"), JsonSerializer.Serialize(new { Result = "PASS", Url = url, First = first, Results = results, Scan = scan, Models = caps.Models, Requests = 3, BatchSize = 1, Iterations = 1 }, new JsonSerializerOptions { WriteIndented = true }));
    }
}
