using System.IO;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text.Json;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue256RecipeDerivationTests
{
    private static GenerationRecipe Recipe => new("sample", 42, 20, "Euler a", "Karras", 5, 512, 768, "abc");
    private static MainViewModel MakeMain(LibraryFixture d) => new(Fixtures.Catalog(), new UserStateStore(Path.Combine(d.Path, "user.db")), new MemoryClipboard(), paths: new(d.Path));
    [Fact]
    public void MachineDiffCoversPromptNegativeLoraAndAllEditableTypedConditions()
    {
        var p = GenerationRecipeDerivation.Snapshot("blue, <lora:a:0.5>", "lowres", Recipe);
        var c = GenerationRecipeDerivation.Snapshot("red, <lora:a:0.7>, <lora:b:0.4>", "watermark",
            Recipe with { Model = "other", ModelHash = "def", Seed = 43, Steps = 8, Sampler = "Euler", Scheduler = "Simple", Cfg = 6, Width = 640, Height = 512 });
        Assert.Equal(new[] { "Positive", "Negative", "Model", "Model hash", "Seed", "Steps", "Sampler", "Scheduler", "CFG", "Width", "Height", "LoRA" }, GenerationRecipeDerivation.Diff(p, c).Select(x => x.Field));
        Assert.Contains("only", GenerationRecipeDerivation.Diff(p, c with { Recipe = c.Recipe with { ModelHash = null } }).Single(x => x.Field == "Model hash").State);
    }
    [Fact]
    public void UnchangedVsEditedVsSavedDirtyStateDoesNotLoseOriginalParent()
    {
        using var d = new LibraryFixture(); var main = MakeMain(d);
        main.Create.Load(new(Guid.NewGuid(), "parent", "", "blue_hair", "lowres", Recipe), "parent");
        Assert.False(main.Create.Changed); Assert.Contains("変更なし", main.Create.DerivationSummary);
        main.Create.Seed = "43"; Assert.True(main.Create.Changed); Assert.Contains("Seed: 42 → 43", main.Create.DerivationSummary);
        main.Create.Seed = "42"; Assert.False(main.Create.Changed);
        main.Create.Seed = "43"; main.Create.SaveName = "derived"; main.Create.Save.Execute(null);
        Assert.False(main.Create.Changed); Assert.Contains("Seed: 42 → 43", main.Create.DerivationSummary);
        var reopened = MakeMain(d); reopened.Create.Load(reopened.Presets.Single(), "reopened");
        Assert.False(reopened.Create.Changed); Assert.Contains("Seed: 42 → 43", reopened.Create.DerivationSummary);
        reopened.Create.Seed = "44"; Assert.Contains("Seed: 42 → 44", reopened.Create.DerivationSummary);
    }
    [Fact]
    public void UnappliedHiresEvidenceNeverClaimsSameExecutionConditions()
    {
        var p = GenerationRecipeDerivation.Snapshot("blue", "lowres", Recipe with { SourceParameters = [new("Hires upscale", "2")] });
        var edge = GenerationRecipeDerivation.Build(p, p, "parent");
        Assert.Equal("not applied", Assert.Single(edge.Changes).State);
        Assert.Contains("Hires upscale", edge.Changes[0].Left); Assert.Contains("not sent", GenerationRecipeDerivation.Summary(edge));
        Assert.True(GenerationRecipeDerivation.With(p.Recipe, edge).RequiresDerivativeConsent);
    }
    [Theory]
    [InlineData("null")][InlineData("{}")][InlineData("[]")][InlineData("bad")]
    public void MalformedParentReceiptsRemainBlockedEvidence(string json)
    {
        var p = new GenerationParameter(GenerationRecipeDerivation.Key, json);
        Assert.False(GenerationRecipeDerivation.IsValid(p)); Assert.Throws<InvalidDataException>(() => GenerationRecipeDerivation.Read([p]));
        Assert.True((Recipe with { SourceParameters = [p] }).RequiresDerivativeConsent);
    }
    [Theory]
    [InlineData(false)][InlineData(true)]
    public void ParentHashAndMachineDiffContradictionsAreRejected(bool changeHash)
    {
        var p = GenerationRecipeDerivation.Snapshot("blue", "lowres", Recipe); var edge = GenerationRecipeDerivation.Build(p, p with { Recipe = p.Recipe with { Seed = 43 } }, "parent");
        edge = changeHash ? edge with { ParentId = new string('0', 64) } : edge with { Changes = [] };
        Assert.Throws<InvalidDataException>(() => GenerationRecipeDerivation.Read([new(GenerationRecipeDerivation.Key, JsonSerializer.Serialize(edge))]));
    }
    [Fact]
    public void ReceiptCannotNestItsParentAndCannotGrowWithoutBound()
    {
        var p = GenerationRecipeDerivation.Snapshot("blue", "lowres", Recipe); var edge = GenerationRecipeDerivation.Build(p, p, "parent");
        Assert.Throws<InvalidDataException>(() => GenerationRecipeDerivation.Build(p with { Recipe = GenerationRecipeDerivation.With(Recipe, edge) }, p, "nested"));
        Assert.Throws<InvalidDataException>(() => GenerationRecipeDerivation.Build(p with { Positive = new string('x', 200000) }, p, "oversized"));
    }
    [Fact]
    public async Task StaleSnapshotIsBlockedBeforeNetworkAndOutputReceiptWaitsForActualMatch()
    {
        using var d = new LibraryFixture(); var server = new Issue228ForgeApiTests.FakeApi(d); var api = new ForgeGenerationApiClient(new HttpClient(server));
        var p = GenerationRecipeDerivation.Snapshot("1girl, <lora:detail:0.75>", "lowres", Recipe);
        var r = GenerationRecipeDerivation.With(Recipe, GenerationRecipeDerivation.Build(p, p, "parent"));
        var stale = await api.GenerateAsync("http://localhost:7860", new("different", "lowres", r), d.Images);
        Assert.False(stale.Success); Assert.Equal(0, server.Calls);
        server.Mode = "mismatch";
        var failed = await api.GenerateAsync("http://localhost:7860", new(p.Positive, p.Negative, r), d.Images);
        Assert.False(failed.Success); Assert.Equal(1, server.Posts); Assert.True(File.Exists(failed.ImagePath));
        Assert.Null(GenerationRecipeDerivation.Read(failed.Metadata!.Parameters));
    }
    [Fact]
    public async Task ActualPngLibraryCreateRestoreKeepsOneParentEdgeAndRebasesNextImage()
    {
        using var d = new LibraryFixture(); var server = new Issue228ForgeApiTests.FakeApi(d, (path, info) =>
            typeof(DanbooruTagTool.App.GenerationLibraryValidation).GetMethod("WriteFixture", System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic)!.Invoke(null, [path, info]));
        server.Info = "red\nNegative prompt: lowres\nSteps: 20, Sampler: Euler a, Schedule type: Karras, CFG scale: 5, Seed: 43, Size: 512x768, Model: sample, Model hash: abc";
        var api = new ForgeGenerationApiClient(new HttpClient(server));
        var parent = GenerationRecipeDerivation.Snapshot("blue", "lowres", Recipe);
        var current = GenerationRecipeDerivation.Snapshot("red", "lowres", Recipe with { Seed = 43 });
        var edge = GenerationRecipeDerivation.Build(parent, current, "parent.png", new string('1', 64));
        var result = await api.GenerateAsync("http://localhost:7860", new(current.Positive, current.Negative, GenerationRecipeDerivation.With(current.Recipe, edge)), d.Images);
        Assert.True(result.Success, result.Status); Assert.DoesNotContain("DTT", result.Metadata!.RawInfotext);
        var store = d.Store(); var root = store.AddRoot(d.Images); Assert.True(new GenerationLibraryScanner(store, new PngGenerationMetadataReader()).Scan(root).Complete);
        var metadata = new GenerationLibraryStore(store.DatabasePath).Metadata(store.Query(new()).Images.Single().Id)!;
        Assert.Equal(JsonSerializer.Serialize(edge), JsonSerializer.Serialize(GenerationRecipeDerivation.Read(metadata.Parameters)));
        var main = MakeMain(d); main.Create.LoadImage(metadata, "child.png"); Assert.False(main.Create.Changed);
        Assert.True(main.Create.TryRecipe(out var restored, out _)); var nextParent = GenerationRecipeDerivation.Read(restored!.SourceParameters)!;
        Assert.Equal("red", nextParent.Parent.Positive); Assert.Equal(43, nextParent.Parent.Recipe.Seed);
        Assert.Equal(Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(result.ImagePath!))).ToLowerInvariant(), nextParent.ParentImageSha256);
        Assert.DoesNotContain(nextParent.Parent.Recipe.SourceParameters!, x => GenerationRecipeDerivation.IsKey(x.Name));
        var bytes = File.ReadAllBytes(result.ImagePath!); bytes[^13] ^= 1; File.WriteAllBytes(result.ImagePath!, bytes);
        Assert.Throws<GenerationMetadataException>(() => ForgePngGenerationMetadata.Read(result.ImagePath!));
        File.WriteAllText(result.ImagePath!, "changed"); main.Create.LoadImage(metadata, "changed");
        Assert.Contains("確認できません", main.Status); Assert.Equal("red", main.Create.Positive);
    }
    [Fact]
    public void EmptyPresetAndClearedWorkingConditionsDoNotCrashDiff()
    {
        using var d = new LibraryFixture(); var main = MakeMain(d);
        main.Create.Load(new(Guid.NewGuid(), "empty", "", "", ""), "empty"); Assert.False(main.Create.Changed);
        main.Create.Model = "sample"; Assert.True(main.Create.Changed);
        main.Create.Load(new(Guid.NewGuid(), "typed", "", "", "", new(Model: "sample")), "typed");
        main.Create.Model = ""; Assert.True(main.Create.TryRecipe(out _, out _)); Assert.True(main.Create.Changed);
    }
}
