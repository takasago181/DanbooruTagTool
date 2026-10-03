using System.IO;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text.Json;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue256LoraProvenanceTests
{
    private const string Positive = "1girl, <lora:detail:0.75>";
    private static GenerationRecipe Recipe = new("sample", 42, 20, "Euler a", "Karras", 5, ModelHash: "abc");
    private static ForgeApiRequest Request(GenerationRecipe? r = null) => new(Positive, "lowres", r ?? Recipe);
    private static Issue228ForgeApiTests.FakeApi Server(LibraryFixture d) { var server = new Issue228ForgeApiTests.FakeApi(d); server.EnsureLora(); return server; }

    [Theory]
    [InlineData("lora_missing", 0)]
    [InlineData("lora_ambiguous", 0)]
    [InlineData("lora_png_mismatch", 1)]
    public async Task MissingAmbiguousAndActualHashMismatchFailWithoutRetry(string mode, int posts)
    {
        using var d = new LibraryFixture(); var server = Server(d); server.Mode = mode;
        var result = await new ForgeGenerationApiClient(new HttpClient(server)).GenerateAsync("http://localhost:7860", Request(), d.Images);
        Assert.False(result.Success); Assert.Equal(posts, server.Posts);
        if (posts == 1) { Assert.True(File.Exists(result.ImagePath)); Assert.Contains("LoRA hash/identity", result.Status); }
    }

    [Theory]
    [InlineData(false)] [InlineData(true)]
    public async Task HistoricalBackendOrFullFileMismatchRejectsBeforePost(bool fullFile)
    {
        using var d = new LibraryFixture(); var server = Server(d);
        GenerationParameter p = fullFile
            ? new(GenerationLoraProvenance.ReceiptKey, JsonSerializer.Serialize(new[] { new GenerationLoraIdentity("detail", server.LoraHash[..12], new string('0', 64), 0.75m) }))
            : new("Lora hashes", "detail: 000000000000");
        var result = await new ForgeGenerationApiClient(new HttpClient(server)).GenerateAsync("http://localhost:7860", Request(Recipe with { SourceParameters = [p] }), d.Images);
        Assert.False(result.Success); Assert.Equal(0, server.Posts); Assert.Contains("hash mismatch", result.Status);
    }

    [Theory]
    [InlineData("1girl, <lora:detail:1:0.5>", "lowres")]
    [InlineData("1girl, <lyco:detail:0.5>", "lowres")]
    [InlineData("1girl, <lora:detail:0.5>, <lora:detail:0.2>", "lowres")]
    [InlineData("1girl", "<lora:detail:0.5>")]
    [InlineData("1girl, <lora:detail:3>", "lowres")]
    public async Task UnsupportedAndDuplicateSyntaxIsNotSilentlyIgnored(string positive, string negative)
    {
        using var d = new LibraryFixture(); var server = Server(d);
        var result = await new ForgeGenerationApiClient(new HttpClient(server)).GenerateAsync("http://localhost:7860", new(positive, negative, Recipe), d.Images);
        Assert.False(result.Success); Assert.Equal(0, server.Posts);
    }

    [Theory]
    [InlineData("[null]")]
    [InlineData("[{}]")]
    [InlineData("[]")]
    [InlineData("not json")]
    public void MalformedReceiptNeverBecomesTrustedEvidence(string json)
    {
        var p = new GenerationParameter(GenerationLoraProvenance.ReceiptKey, json);
        Assert.False(GenerationLoraProvenance.IsValid(p)); Assert.Throws<InvalidDataException>(() => GenerationLoraProvenance.Expected([p]));
        Assert.True((Recipe with { SourceParameters = [p] }).RequiresDerivativeConsent);
    }

    [Fact]
    public async Task SuccessfulOutputPreservesRawInfotextAndFullShaThroughPngLibraryPresetRestartAndRegeneration()
    {
        using var d = new LibraryFixture(); var server = new Issue228ForgeApiTests.FakeApi(d, (path, info) =>
            typeof(DanbooruTagTool.App.GenerationLibraryValidation).GetMethod("WriteFixture", System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic)!.Invoke(null, [path, info]));
        server.EnsureLora(); server.Info = server.Info.Replace("32x24", "512x768").Replace(", Custom: alpha", ""); var api = new ForgeGenerationApiClient(new HttpClient(server));
        var first = await api.GenerateAsync("http://localhost:7860", Request(Recipe with { Width = 512, Height = 768 }), d.Images);
        Assert.True(first.Success, first.Status); var expectedSha = server.LoraHash;
        var identity = Assert.Single(GenerationLoraProvenance.Expected(first.Metadata!.Parameters));
        Assert.Equal(expectedSha, identity.FileSha256); Assert.Equal(expectedSha[..12], identity.BackendHash); Assert.Equal(0.75m, identity.Weight);
        Assert.DoesNotContain("DTT", first.Metadata.RawInfotext);
        var store = d.Store(); var root = store.AddRoot(d.Images); Assert.True(new GenerationLibraryScanner(store, new PngGenerationMetadataReader()).Scan(root).Complete);
        var m = store.Metadata(store.Query(new()).Images.Single().Id)!; Assert.Equal(first.Metadata.RawInfotext, m.RawInfotext);
        var user = new UserStateStore(Path.Combine(d.Path, "UserData", "user.db"));
        var main = new MainViewModel(Fixtures.Catalog(), user, new MemoryClipboard(), paths: new(d.Path));
        main.Create.Load(new(Guid.NewGuid(), "source", "", m.Positive, m.Negative, GenerationRecipe.FromMetadata(m)), "image");
        Assert.Contains(expectedSha, main.Create.LoraProvenance);
        main.Create.Width = "512"; main.Create.Height = "768"; main.Create.SaveName = "copy"; main.Create.Save.Execute(null);
        var saved = new UserStateStore(Path.Combine(d.Path, "UserData", "user.db")).Load()!.Presets!.Single();
        Assert.Equal(expectedSha, GenerationLoraProvenance.Expected(saved.Recipe!.SourceParameters).Single().FileSha256);
        // Same identity permits deliberate weight changes; actual prompt verification remains strict.
        server.Info = server.Info.Replace("0.75", "0.5");
        main.Workspace.Replace(Positive.Replace("0.75", "0.5"));
        Assert.True(main.Create.TryRecipe(out var changed, out _));
        var next = await api.GenerateAsync("http://localhost:7860", new(main.Create.Positive, "lowres", changed!), d.Images);
        Assert.True(next.Success, next.Status); Assert.Equal(2, server.Posts);
        Assert.Equal(expectedSha, GenerationLoraProvenance.Expected(next.Metadata!.Parameters).Single().FileSha256);
        Assert.Equal(0.5m, GenerationLoraProvenance.Expected(next.Metadata.Parameters).Single().Weight);
        main.Create.ReleaseLoraIdentity.Execute(null);
        Assert.Contains("元 Lora hashes", main.Create.RestorationWarning); Assert.False(main.Create.AllowDerivative);
        Assert.Empty(GenerationLoraProvenance.Expected(main.Create.TryRecipe(out var released, out _) ? released!.SourceParameters : null));
        Assert.True(released!.RequiresDerivativeConsent);
    }

    [Fact]
    public void ReceiptCorruptionIsRejectedAndOriginalChunksAreRetained()
    {
        using var d = new LibraryFixture(); var path = Path.Combine(d.Images, "original.png"); Issue226LibraryFoundationTests.WritePng(path);
        var original = File.ReadAllBytes(path); var receipt = new GenerationLoraIdentity("detail", "123456789abc", new string('1', 64), 0.5m);
        var attached = GenerationLoraPngReceipt.Attach(original, [receipt]);
        Assert.Equal(original[..^12], attached[..(original.Length - 12)]);
        Assert.Equal(original[^12..], attached[^12..]);
        File.WriteAllBytes(path, attached); Assert.Equal(Issue226LibraryFoundationTests.Info, ForgePngGenerationMetadata.Read(path).RawInfotext);
        Assert.Throws<InvalidDataException>(() => GenerationLoraPngReceipt.Attach(attached, [receipt]));
        attached[^13] ^= 1; File.WriteAllBytes(path, attached);
        Assert.Throws<GenerationMetadataException>(() => ForgePngGenerationMetadata.Read(path));
    }

    [Fact]
    public async Task RemovedSourceLoraNeedsExplicitConstraintReleaseEvenForDerivatives()
    {
        using var d = new LibraryFixture(); var server = Server(d);
        var recipe = Recipe with { SourceParameters = [new("Lora hashes", "detail: " + server.LoraHash[..12])] };
        var result = await new ForgeGenerationApiClient(new HttpClient(server)).GenerateAsync("http://localhost:7860", new("1girl", "lowres", recipe, true), d.Images);
        Assert.False(result.Success); Assert.Equal(0, server.Posts);
    }

    [Theory]
    [InlineData(false)] [InlineData(true)]
    public async Task SameEmbeddedTensorHashDoesNotHideChangedFileOrStaleApiMetadata(bool staleApi)
    {
        using var d = new LibraryFixture(); var server = Server(d);
        var tensor = new byte[] { 4, 5, 6, 7 }; var hash = Convert.ToHexString(SHA256.HashData(tensor)).ToLowerInvariant();
        void Write(string note)
        {
            var header = System.Text.Encoding.UTF8.GetBytes(JsonSerializer.Serialize(new { __metadata__ = new { sshs_model_hash = hash, note } }));
            using var stream = File.Create(server.LoraPath); var length = new byte[8]; System.Buffers.Binary.BinaryPrimitives.WriteUInt64LittleEndian(length, (ulong)header.Length);
            stream.Write(length); stream.Write(header); stream.Write(tensor);
        }
        Write("original"); server.LoraEmbeddedHash = hash; var originalSha = server.LoraHash;
        Write("changed header, unchanged tensor hash"); if (staleApi) server.LoraEmbeddedHash = new string('0', 64);
        var recipe = Recipe with { SourceParameters = [new(GenerationLoraProvenance.ReceiptKey, JsonSerializer.Serialize(new[] { new GenerationLoraIdentity("detail", hash[..12], originalSha, 0.75m) }))] };
        var result = await new ForgeGenerationApiClient(new HttpClient(server)).GenerateAsync("http://localhost:7860", Request(recipe), d.Images);
        Assert.False(result.Success); Assert.Equal(0, server.Posts);
    }

    [Fact]
    public async Task SelectedLocalFilesStayReadLockedThroughPostAndAreReleasedAfterward()
    {
        using var d = new LibraryFixture(); var server = Server(d); server.Mode = "lora_locked";
        var result = await new ForgeGenerationApiClient(new HttpClient(server)).GenerateAsync("http://localhost:7860", Request(), d.Images);
        Assert.True(result.Success, result.Status); File.WriteAllText(server.LoraPath, "released after POST");
    }
}
