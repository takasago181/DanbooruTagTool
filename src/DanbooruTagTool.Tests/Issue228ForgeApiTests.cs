using System.Net;
using System.Net.Http;
using System.IO;
using System.Text;
using System.Text.Json;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue228ForgeApiTests
{
    private static readonly GenerationRecipe Recipe = new("sample", 42, 20, "Euler a", "Karras", 5);
    [Theory]
    [InlineData("https://127.0.0.1:7860")]
    [InlineData("http://example.com")]
    [InlineData("http://127.0.0.1:7860/?next=remote")]
    [InlineData("http://user:pass@localhost:7860")]
    [InlineData("http://127.0.0.1:7860/path")]
    public async Task RemoteCredentialAndAmbiguousUrlsNeverSend(string url)
    {
        using var d = new LibraryFixture(); var server = new FakeApi(d); var client = new ForgeGenerationApiClient(new(server));
        var result = await client.GenerateAsync(url, new("1girl, <lora:detail:0.75>", "lowres", Recipe), d.Images);
        Assert.False(result.Success); Assert.Equal(0, server.Calls);
    }
    [Fact]
    public async Task OnePostBoundedPayloadRealPngReadbackAndLibraryIngest()
    {
        using var d = new LibraryFixture(); var server = new FakeApi(d); var api = new ForgeGenerationApiClient(new(server));
        var result = await api.GenerateAsync("http://127.0.0.1:7860", new("1girl, <lora:detail:0.75>", "lowres", Recipe), d.Images);
        Assert.True(result.Success, result.Status); Assert.Equal(1, server.Posts); Assert.NotNull(result.ImagePath);
        var p = JsonDocument.Parse(server.Payload!).RootElement;
        Assert.Equal(1, p.GetProperty("batch_size").GetInt32()); Assert.Equal(1, p.GetProperty("n_iter").GetInt32());
        Assert.False(p.GetProperty("save_images").GetBoolean()); Assert.True(p.GetProperty("override_settings_restore_afterwards").GetBoolean()); Assert.False(p.TryGetProperty("width", out _));
        var store = d.Store(); var root = store.AddRoot(d.Images); var scan = new GenerationLibraryScanner(store, new PngGenerationMetadataReader()).Scan(root);
        Assert.True(scan.Complete); Assert.Equal("sample", store.Metadata(store.Query(new(Seed: 42)).Images.Single().Id)!.Value("Model"));
    }
    [Theory]
    [InlineData("model")]
    [InlineData("sampler")]
    [InlineData("scheduler")]
    [InlineData("bounds")]
    public async Task UnknownOrUnsafeRecipeRejectedBeforeGeneration(string field)
    {
        using var d = new LibraryFixture(); var server = new FakeApi(d); var r = field switch { "model" => Recipe with { Model = "bogus" }, "sampler" => Recipe with { Sampler = "bogus" }, "scheduler" => Recipe with { Scheduler = "bogus" }, _ => Recipe with { Width = 8192 } };
        var result = await new ForgeGenerationApiClient(new(server)).GenerateAsync("http://localhost:7860", new("1girl", "", r), d.Images);
        Assert.False(result.Success); Assert.Equal(0, server.Posts);
    }
    [Theory]
    [InlineData("Seed")]
    [InlineData("Steps")]
    [InlineData("CFG")]
    [InlineData("Width")]
    [InlineData("Height")]
    [InlineData("Positive")]
    [InlineData("Negative")]
    [InlineData("Model/hash")]
    [InlineData("Sampler")]
    [InlineData("Scheduler")]
    public void EveryAdvertisedFieldMustRoundTrip(string field)
    {
        var r = Recipe with { Width = 32, Height = 24 }; var pos = "1girl, <lora:detail:0.75>"; var neg = "lowres";
        var info = Issue226LibraryFoundationTests.Info;
        info = field switch { "Seed" => info.Replace("Seed: 42", "Seed: 43"), "Steps" => info.Replace("Steps: 20", "Steps: 21"), "CFG" => info.Replace("CFG scale: 5", "CFG scale: 6"), "Width" => info.Replace("32x24", "40x24"), "Height" => info.Replace("32x24", "32x40"), "Positive" => info.Replace("1girl", "1boy"), "Negative" => info.Replace("lowres", "blur"), "Model/hash" => info.Replace("Model hash: abc", "Model hash: bad"), "Sampler" => info.Replace("Euler a", "Euler"), _ => info.Replace("Karras", "Normal") };
        var errors = ForgeGenerationApiClient.Compare(new(pos, neg, r), new("sample [abc]", "sample", "abc"), ForgePngGenerationMetadata.Parse("fixture.png", info));
        Assert.Equal(new[] { field }, errors);
    }
    [Fact]
    public async Task MismatchPreservesActualImageAndDoesNotRetry()
    {
        using var d = new LibraryFixture(); var server = new FakeApi(d) { Info = Issue226LibraryFoundationTests.Info.Replace("Seed: 42", "Seed: 43") };
        var result = await new ForgeGenerationApiClient(new(server)).GenerateAsync("http://localhost:7860", new("1girl, <lora:detail:0.75>", "lowres", Recipe), d.Images);
        Assert.False(result.Success); Assert.Contains("Seed", result.Status); Assert.True(File.Exists(result.ImagePath)); Assert.Equal(1, server.Posts);
    }
    [Theory]
    [InlineData("restore")]
    [InlineData("duplicate")]
    [InlineData("http")]
    [InlineData("schema")]
    public async Task IncompatibleAndUncertainOutcomesFailClosed(string mode)
    {
        using var d = new LibraryFixture(); var server = new FakeApi(d) { Mode = mode };
        var result = await new ForgeGenerationApiClient(new(server)).GenerateAsync("http://localhost:7860", new("1girl, <lora:detail:0.75>", "lowres", Recipe), d.Images);
        Assert.False(result.Success); Assert.Equal(mode == "schema" ? 0 : 1, server.Posts);
    }
    [Theory]
    [InlineData("sample", "abc", "abc", true)]
    [InlineData("sample", "abc", "wrong", false)]
    [InlineData("sample", "abc", null, false)]
    [InlineData("sample", null, "abc", false)]
    [InlineData("other_sample", "abc", "abc", false)]
    [InlineData("folder_sample", null, null, true)]
    public void NeoFolderBasenameAliasRequiresExactDeclaredHash(string actualName, string? apiHash, string? pngHash, bool accepted)
    {
        var info = Issue226LibraryFoundationTests.Info.Replace("Model: sample", "Model: " + actualName);
        info = pngHash is null ? info.Replace(", Model hash: abc", "") : info.Replace("Model hash: abc", "Model hash: " + pngHash);
        var metadata = ForgePngGenerationMetadata.Parse("fixture.png", info);
        var errors = ForgeGenerationApiClient.Compare(new("1girl, <lora:detail:0.75>", "lowres", Recipe),
            new("folder\\sample.safetensors [abc]", "folder_sample", apiHash), metadata);
        Assert.Equal(accepted, errors.Count == 0);
        if (!accepted) Assert.Equal(new[] { "Model/hash" }, errors);
    }
    internal sealed class FakeApi(LibraryFixture d, Action<string, string>? writeImage = null) : HttpMessageHandler
    {
        public string Info = Issue226LibraryFoundationTests.Info; public string Mode = ""; public int Posts, Calls, Options; public string? Payload;
        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
        {
            Calls++; var path = request.RequestUri!.AbsolutePath; object body;
            if (path == "/openapi.json")
            {
                var fields = "prompt negative_prompt seed steps sampler_name scheduler cfg_scale width height batch_size n_iter override_settings override_settings_restore_afterwards send_images save_images".Split(' ').Where(f => Mode != "schema" || f != "scheduler").ToDictionary(f => f, _ => new { type = "string" });
                body = new { paths = new Dictionary<string, object> { ["/sdapi/v1/txt2img"] = new { post = new { requestBody = new { content = new Dictionary<string, object> { ["application/json"] = new { schema = new Dictionary<string, string> { ["$ref"] = "#/components/schemas/Request" } } } } } } }, components = new { schemas = new { Request = new { properties = fields } } } };
            }
            else if (path == "/sdapi/v1/sd-models") body = new[] { new { title = "sample [abc]", model_name = "sample", hash = "abc" } };
            else if (path == "/sdapi/v1/samplers") body = new[] { new { name = "Euler a" } };
            else if (path == "/sdapi/v1/schedulers") body = new[] { new { label = "Karras" } };
            else if (path == "/sdapi/v1/options") body = new { sd_model_checkpoint = ++Options == 2 && Mode == "restore" ? "wrong" : "original" };
            else
            {
                Assert.Equal("/sdapi/v1/txt2img", path); Posts++; Payload = await request.Content!.ReadAsStringAsync(ct);
                if (Mode == "http") return new(HttpStatusCode.InternalServerError);
                var temp = Path.Combine(d.Path, "api-fixture.png"); if (writeImage is null) Issue226LibraryFoundationTests.WritePng(temp, Info); else writeImage(temp, Info);
                var encoded = Convert.ToBase64String(File.ReadAllBytes(temp)); body = new { images = Mode == "duplicate" ? new[] { encoded, encoded } : new[] { encoded }, info = "{}" };
            }
            return new(HttpStatusCode.OK) { Content = new StringContent(JsonSerializer.Serialize(body), Encoding.UTF8, "application/json") };
        }
    }
}
