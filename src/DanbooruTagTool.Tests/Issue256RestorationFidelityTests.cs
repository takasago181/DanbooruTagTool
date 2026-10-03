using System.IO;
using System.Net.Http;
using System.Text.Json;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Microsoft.Data.Sqlite;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue256RestorationFidelityTests
{
    private const string Info = "blue_hair\nNegative prompt: lowres\nSteps: 20, Sampler: Euler a, Schedule type: Karras, CFG scale: 5, Seed: 42, Size: 512x768, Model: sample, Model hash: abc";
    private static GenerationRecipe Import(string extra = "") => GenerationRecipe.FromMetadata(GenerationInfotextParser.Parse("source.png", Info + extra));

    [Theory]
    [InlineData("RNG", "CPU")]
    [InlineData("Clip skip", "2")]
    [InlineData("Hires upscale", "2")]
    [InlineData("VAE hash", "abc")]
    [InlineData("ControlNet 0", "enabled")]
    [InlineData("ADetailer model", "face")]
    [InlineData("Lora hashes", "detail: abc")]
    [InlineData("Future extension", "unknown")]
    public async Task UnrepresentedConditionsArePreservedAndRejectBeforeAnyNetwork(string name, string value)
    {
        var recipe = Import($", {name}: \"{value}\"");
        Assert.Equal(new GenerationParameter(name, value), Assert.Single(recipe.UnappliedParameters));
        Assert.True(recipe.RequiresDerivativeConsent);
        using var d = new LibraryFixture(); var server = new Issue228ForgeApiTests.FakeApi(d);
        var result = await new ForgeGenerationApiClient(new HttpClient(server)).GenerateAsync("http://localhost:7860", new("blue_hair", "lowres", recipe), d.Images);
        Assert.False(result.Success); Assert.Null(result.ImagePath); Assert.Equal(0, server.Calls);
    }

    [Fact]
    public void InformationalFieldsDoNotBlockAndOrderedDuplicateAliasesDo()
    {
        Assert.False(Import(", Version: neo, User: local, Time taken: 1s").RequiresDerivativeConsent);
        var r = Import(", Scheduler: Normal, Custom: \"a,b: c\", Custom: second");
        Assert.Equal(new[] { "Schedule type", "Scheduler", "Custom", "Custom" }, r.UnappliedParameters.Select(p => p.Name));
        Assert.Equal("a,b: c", r.UnappliedParameters[2].Value);
        Assert.True(GenerationRecipe.FromMetadata(GenerationInfotextParser.Parse("bad.png", Info.Replace("Steps: 20", "Steps: bad"))).RequiresDerivativeConsent);
        Assert.False(new GenerationRecipe("sample", 42, 20, "Euler a", "Karras", 5, 512, 768).RequiresDerivativeConsent);
    }

    [Theory]
    [InlineData(false)] [InlineData(true)]
    public async Task ExplicitDerivativeHasOnePostNoUnknownOverridesAndStillVerifiesTypedFields(bool mismatch)
    {
        using var d = new LibraryFixture(); var server = new Issue228ForgeApiTests.FakeApi(d, (path, info) =>
            typeof(DanbooruTagTool.App.GenerationLibraryValidation).GetMethod("WriteFixture", System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic)!.Invoke(null, [path, info]))
        { Info = Info + ", RNG: CPU" };
        var recipe = Import(", RNG: CPU");
        if (mismatch) server.Info = server.Info.Replace("Seed: 42", "Seed: 43");
        var result = await new ForgeGenerationApiClient(new HttpClient(server)).GenerateAsync("http://localhost:7860", new("blue_hair", "lowres", recipe, AllowDerivative: true), d.Images);
        Assert.Equal(!mismatch, result.Success); Assert.Equal(1, server.Posts); Assert.True(File.Exists(result.ImagePath));
        Assert.DoesNotContain("RNG", server.Payload!); Assert.DoesNotContain("SourceParameters", server.Payload!);
        if (!mismatch) Assert.Contains("派生生成", result.Status); else Assert.Contains("Seed", result.Status);
        Assert.Equal("CPU", result.Metadata!.Value("RNG"));
    }

    [Fact]
    public async Task LibraryCreatePresetRestartKeepsEvidenceButNeverPersistsConsent()
    {
        using var d = new LibraryFixture(); var path = Path.Combine(d.Images, "source.png");
        typeof(DanbooruTagTool.App.GenerationLibraryValidation).GetMethod("WriteFixture", System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic)!.Invoke(null, [path, Info + ", RNG: CPU, Future: \"a,b\""]);
        var store = new UserStateStore(Path.Combine(d.Path, "UserData", "user.db"));
        var main = new MainViewModel(Fixtures.Catalog(), store, new MemoryClipboard(), paths: new(d.Path));
        var library = main.GenerationLibrary!; await library.AddRootAsync(d.Images); await library.ScanAsync(); library.Selected = library.Images.Single();
        library.LoadInCreate.Execute(null);
        Assert.True(main.Create.RequiresDerivativeConsent); Assert.False(main.Create.CanGenerate);
        Assert.Contains("RNG: CPU", main.Create.RestorationWarning); Assert.False(main.Create.Changed);
        main.Create.AllowDerivative = true; Assert.True(main.Create.CanGenerate);
        main.Create.Seed = "43"; main.Create.SaveName = "derivative"; main.Create.Save.Execute(null);
        var saved = Assert.Single(store.Load()!.Presets!);
        Assert.Equal(43, saved.Recipe!.Seed); Assert.Equal("a,b", saved.Recipe.UnappliedParameters.Last().Value);
        var restarted = new MainViewModel(Fixtures.Catalog(), new UserStateStore(Path.Combine(d.Path, "UserData", "user.db")), new MemoryClipboard(), paths: new(d.Path));
        restarted.Create.Load(restarted.Presets.Single(), "reopened");
        Assert.False(restarted.Create.AllowDerivative); Assert.False(restarted.Create.CanGenerate);
        restarted.PresetEditor.SelectedPreset = restarted.Presets.Single(); restarted.PresetEditor.PresetSeed = "44"; restarted.PresetEditor.SavePreset.Execute(null);
        Assert.Equal(JsonSerializer.Serialize(saved.Recipe.SourceParameters), JsonSerializer.Serialize(store.Load()!.Presets!.Single().Recipe!.SourceParameters));
        main.Create.Load(saved, "reload"); Assert.False(main.Create.AllowDerivative);
        // Direct Library/Preset execution cannot bypass Create's explicit consent.
        await main.Forge.GenerateRecipeAsync(saved); Assert.Contains("生成要求は送信していません", main.Forge.RecipeStatus);
    }

    [Fact]
    public void SchemaThreeMigrationBacksUpExactPayloadAndRefusesFutureVersions()
    {
        using var d = new TempDirectory(); var path = Path.Combine(d.Path, "user.db");
        var state = new UserState(Fixtures.Workspace().Snapshot(), new UiState(), [new(Guid.NewGuid(), "fixture", "", "blue_hair", "lowres", Import(", RNG: CPU"))]);
        var oldState = state with { Presets = [state.Presets![0] with { Recipe = state.Presets[0].Recipe! with { SourceParameters = null } }] };
        var oldJson = JsonSerializer.Serialize(oldState).Replace(",\"SourceParameters\":null", "");
        using (var c = new SqliteConnection("Data Source=" + path + ";Pooling=False"))
        {
            c.Open(); using var cmd = c.CreateCommand(); cmd.CommandText = "CREATE TABLE user_state(id INTEGER PRIMARY KEY,version INTEGER,payload TEXT); INSERT INTO user_state VALUES(1,3,$p); PRAGMA user_version=3;"; cmd.Parameters.AddWithValue("$p", oldJson); cmd.ExecuteNonQuery();
        }
        var store = new UserStateStore(path); var backup = Assert.Single(Directory.GetFiles(d.Path, "*.bak"));
        foreach (var file in new[] { backup, path })
        {
            using var c = new SqliteConnection("Data Source=" + file + ";Pooling=False"); c.Open(); using var cmd = c.CreateCommand();
            cmd.CommandText = "SELECT payload FROM user_state"; Assert.Equal(oldJson, cmd.ExecuteScalar());
            cmd.CommandText = "PRAGMA user_version"; Assert.Equal(file == backup ? 3L : 4L, cmd.ExecuteScalar());
        }
        store.Save(state); Assert.Equal("CPU", new UserStateStore(path).Load()!.Presets!.Single().Recipe!.UnappliedParameters.Single().Value);
        using (var c = new SqliteConnection("Data Source=" + path + ";Pooling=False"))
        { c.Open(); using var cmd = c.CreateCommand(); cmd.CommandText = "PRAGMA user_version=5;"; cmd.ExecuteNonQuery(); }
        var bytes = File.ReadAllBytes(path); Assert.Throws<InvalidDataException>(() => new UserStateStore(path)); Assert.Equal(bytes, File.ReadAllBytes(path));
    }
}
