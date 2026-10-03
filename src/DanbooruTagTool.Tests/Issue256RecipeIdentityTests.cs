using System.IO;
using System.Text.Json;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Microsoft.Data.Sqlite;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue256RecipeIdentityTests
{
    [Theory]
    [InlineData("abc", "", true)]
    [InlineData("ABC", "", true)]
    [InlineData("def", "", false)]
    [InlineData("ab", "", false)]
    [InlineData("abc", "folder_hashless", false)]
    [InlineData("abc", "duplicate_basename", true)]
    [InlineData("def", "duplicate_basename", false)]
    public async Task ImportedHashConstrainsNameBeforePostAndActualPngAfterPost(string hash, string mode, bool success)
    {
        using var d = new LibraryFixture();
        var server = new Issue228ForgeApiTests.FakeApi(d) { Mode = mode };
        var recipe = new GenerationRecipe("sample", 42, 20, "Euler a", "Karras", 5, ModelHash: hash);
        var result = await new ForgeGenerationApiClient(new(server)).GenerateAsync("http://localhost:7860",
            new("1girl, <lora:detail:0.75>", "lowres", recipe), d.Images);
        Assert.Equal(success, result.Success);
        // 'def' resolves the second duplicate but its returned fixture is actually 'abc'.
        Assert.Equal(success || hash == "def" && mode == "duplicate_basename" ? 1 : 0, server.Posts);
        if (server.Posts == 1 && !success) Assert.True(File.Exists(result.ImagePath));
        if (mode == "duplicate_basename" && success)
            Assert.Contains("one/sample.safetensors", server.Payload!);
    }

    [Fact]
    public async Task HashWithoutNameIsNotAnImplicitModelSwitch()
    {
        using var d = new LibraryFixture(); var server = new Issue228ForgeApiTests.FakeApi(d);
        var result = await new ForgeGenerationApiClient(new(server)).GenerateAsync("http://localhost:7860",
            new("1girl", "", new(ModelHash: "abc")), d.Images);
        Assert.False(result.Success); Assert.Equal(0, server.Posts);
    }

    [Fact]
    public void RequestedHashMustMatchEvenWithoutResolvedCapability()
    {
        var snapshot = GenerationInfotextParser.Parse("fixture.png", Issue226LibraryFoundationTests.Info);
        Assert.Equal("abc", GenerationRecipe.FromMetadata(snapshot).ModelHash);
        Assert.Contains("Requested Model hash", ForgeGenerationApiClient.Compare(
            new(snapshot.Positive, snapshot.Negative, new(Model: "sample", ModelHash: "def")), null, snapshot));
        Assert.Null(GenerationRecipe.FromMetadata(snapshot with { Parameters = [] }).ModelHash);
    }

    [Fact]
    public async Task LibraryToCreateToSavedPresetAndRestartKeepsHashAndExplicitEdits()
    {
        using var d = new LibraryFixture(); var path = Path.Combine(d.Images, "source.png");
        Issue226LibraryFoundationTests.WritePng(path);
        var store = new UserStateStore(Path.Combine(d.Path, "UserData", "user.db"));
        var main = new MainViewModel(Fixtures.Catalog(), store, new MemoryClipboard(), paths: new(d.Path));
        var library = main.GenerationLibrary!;
        await library.AddRootAsync(d.Images); await library.ScanAsync(); library.Selected = library.Images.Single();
        main.Workspace.Replace("old positive"); main.NegativeWorkspace.Replace("old negative");
        library.LoadInCreate.Execute(null);
        Assert.Equal("abc", main.Create.ModelHash); Assert.Contains("Hash: abc", main.Create.ConditionsSummary);
        main.Create.Width = "512"; main.Create.Height = "768";
        main.Create.SaveName = "restored"; main.Create.Save.Execute(null);
        Assert.Equal("abc", Assert.Single(store.Load()!.Presets!).Recipe!.ModelHash);
        main.Create.Model = "different";
        Assert.Equal("abc", main.Create.ModelHash); // Never silently remove the identity constraint.
        main.Create.ModelHash = "";
        Assert.True(main.Create.TryRecipe(out var changed, out _)); Assert.Null(changed!.ModelHash);
        main.Create.ModelHash = "not-a-hash";
        Assert.False(main.Create.TryRecipe(out _, out _)); Assert.False(main.Create.CanGenerate);
        main.Create.ModelHash = "abc"; main.Create.Model = "";
        Assert.False(main.Create.TryRecipe(out _, out _));
        main.Workspace.Undo(); main.NegativeWorkspace.Undo();
        Assert.Equal("old positive", main.English); Assert.Equal("old negative", main.Negative.English);
        var restarted = new MainViewModel(Fixtures.Catalog(), store, new MemoryClipboard());
        restarted.PresetEditor.SelectedPreset = Assert.Single(restarted.Presets);
        Assert.Equal("abc", restarted.PresetEditor.PresetModelHash);
        restarted.PresetEditor.SavePreset.Execute(null);
        Assert.Equal("abc", Assert.Single(store.Load()!.Presets!).Recipe!.ModelHash);
    }

    [Fact]
    public void VersionTwoMigrationPreservesExactJsonAndBackupThenSavesHashDurably()
    {
        using var d = new TempDirectory(); var path = Path.Combine(d.Path, "user.db");
        var p = Fixtures.Workspace(); p.Replace(" raw\\,comma ,blue_hair"); p.Replace("kept");
        var n = Fixtures.Workspace(); n.Replace("(blue_hair:0.7) AND raw");
        var state = new UserState(p.Snapshot(), new UiState(Workspace: 3),
            [new(Guid.NewGuid(), "old", "note", "positive", "negative", new("sample", 42, 20, "Euler", "Karras", 5, 512, 768))], n.Snapshot());
        var json = JsonSerializer.Serialize(state).Replace(",\"ModelHash\":null", "");
        using (var c = new SqliteConnection("Data Source=" + path + ";Pooling=False"))
        {
            c.Open(); using var cmd = c.CreateCommand();
            cmd.CommandText = "CREATE TABLE user_state(id INTEGER PRIMARY KEY,version INTEGER,payload TEXT); INSERT INTO user_state VALUES(1,2,$p); PRAGMA user_version=2;";
            cmd.Parameters.AddWithValue("$p", json); cmd.ExecuteNonQuery();
        }
        var store = new UserStateStore(path); var backup = Assert.Single(Directory.GetFiles(d.Path, "*.bak"));
        foreach (var file in new[] { backup, path })
        {
            using var c = new SqliteConnection("Data Source=" + file + ";Pooling=False"); c.Open(); using var cmd = c.CreateCommand();
            cmd.CommandText = "SELECT payload FROM user_state"; Assert.Equal(json, cmd.ExecuteScalar());
            cmd.CommandText = "PRAGMA user_version"; Assert.Equal(file == backup ? 2L : UserStateStore.SchemaVersion, cmd.ExecuteScalar());
        }
        var loaded = store.Load()!;
        Assert.Equal(JsonSerializer.Serialize(state), JsonSerializer.Serialize(loaded));
        var preset = loaded.Presets!.Single();
        store.Save(loaded with { Presets = [preset with { Recipe = preset.Recipe! with { ModelHash = "abc" } }] });
        Assert.Equal("abc", new UserStateStore(path).Load()!.Presets!.Single().Recipe!.ModelHash);
        Assert.Single(Directory.GetFiles(d.Path, "*.bak"));
        // The Foundation client checks version>2 before any migration/save.
        using var oldCheck = new SqliteConnection("Data Source=" + path + ";Pooling=False"); oldCheck.Open();
        using var check = oldCheck.CreateCommand(); check.CommandText = "SELECT version FROM user_state";
        Assert.True((long)check.ExecuteScalar()! > 2);
    }

    [Theory]
    [InlineData(2)] [InlineData(3)]
    public void FailedMigrationRollsBackAndRetainsOriginalBackup(int previousVersion)
    {
        using var d = new TempDirectory(); var path = Path.Combine(d.Path, "user.db");
        using (var c = new SqliteConnection("Data Source=" + path + ";Pooling=False"))
        {
            c.Open(); using var cmd = c.CreateCommand(); cmd.CommandText = $"CREATE TABLE user_state(id INTEGER PRIMARY KEY,version INTEGER,payload TEXT); INSERT INTO user_state VALUES(1,{previousVersion},'{{}}'); PRAGMA user_version={previousVersion}; CREATE TRIGGER prevent_update BEFORE UPDATE ON user_state BEGIN SELECT RAISE(ABORT,'fixture'); END;"; cmd.ExecuteNonQuery();
        }
        var bytes = File.ReadAllBytes(path);
        Assert.Throws<SqliteException>(() => new UserStateStore(path));
        Assert.Equal(bytes, File.ReadAllBytes(path)); Assert.Single(Directory.GetFiles(d.Path, "*.bak"));
    }
}
