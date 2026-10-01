using System.Buffers.Binary;
using System.IO;
using System.Text;
using System.Text.Json;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Microsoft.Data.Sqlite;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue229LoraLibraryTests
{
    [Fact] public void ThousandModelWarmScanAndQueryRemainBounded()
    {
        using var f = new LoraFixture(); for (var i = 0; i < 1000; i++) f.File($"folder/model{i:0000}.safetensors", new() { ["index"] = i.ToString() });
        var cold = f.Store.Scan(f.Models); Assert.True(cold.Complete); Assert.Equal(1000, cold.Hashed);
        var warm = f.Store.Scan(f.Models); Assert.True(warm.Complete); Assert.Equal(0, warm.Hashed); Assert.Equal(1000, warm.Unchanged);
        Assert.Equal(100, f.Store.Query().Length); Assert.Equal(100, f.Store.Query(offset: 900).Length); Assert.Empty(f.Store.Query(offset: 1000));
        Assert.Single(f.Store.Query("model0999"));
    }
    [Fact] public void OfflineRecursiveScanSkipsHashAndRefreshesSidecars()
    {
        using var f = new LoraFixture(); var path = f.File("nested/a.safetensors");
        var first = f.Store.Scan(f.Models); Assert.True(first.Complete); Assert.Equal(1, first.Hashed);
        var repeat = f.Store.Scan(f.Models); Assert.Equal(0, repeat.Hashed); Assert.Equal(1, repeat.Unchanged);
        System.IO.File.WriteAllText(Path.ChangeExtension(path, ".civitai.info"), "{\"baseModel\":\"SDXL\",\"trainedWords\":[\"trigger\"]}");
        var refresh = f.Store.Scan(f.Models); Assert.Equal(0, refresh.Hashed); Assert.Equal(1, refresh.Refreshed);
        Assert.Equal("SDXL", f.Store.Query().Single().BaseModel); Assert.Equal("trigger", f.Store.Query().Single().Triggers.Single().Text);
        Assert.Equal(1, f.Store.Scan(f.Models, forceHash: true).Hashed);
        Assert.False(System.IO.File.Exists(Path.Combine(f.Root, "UserData", "user.db")));
        Assert.False(Directory.Exists(Path.Combine(f.Root, "Data")));
    }
    [Fact] public void EmbeddedThenSidecarThenExplicitUserPrecedenceAndDisabledTriggers()
    {
        using var f = new LoraFixture(); var path = f.File("a.safetensors", new() { ["modelspec.architecture"] = "embedded-model", ["modelspec.trigger_phrase"] = "first, second" });
        System.IO.File.WriteAllText(Path.ChangeExtension(path, ".json"), "{\"baseModel\":\"lower\",\"trainedWords\":[\"lower\"],\"id\":42}");
        f.Store.Scan(f.Models); var asset = f.Store.Query().Single(); Assert.Equal("embedded-model", asset.BaseModel); Assert.Equal(2, asset.Triggers.Length);
        f.Store.Save(asset.Sha256, new("Character", true, "note", .7m, ["blue_hair"], "user-model", [new("user-trigger", "user", false)]));
        f.Store.Scan(f.Models); var reopened = new LoraLibraryStore(f.Store.DatabasePath).Query(favoriteOnly: true).Single();
        Assert.Equal("user-model", reopened.BaseModel); Assert.Equal("user", reopened.BaseModelSource); Assert.False(reopened.Triggers.Single().Enabled);
        Assert.Equal("note", reopened.User.Note); Assert.Contains("42", reopened.Facts.SourceUrl!);
    }
    [Fact] public void IdenticalCopiesAndRenameShareShaUserMetadataButDistinctNamesDoNot()
    {
        using var f = new LoraFixture(); var a = f.File("one.safetensors"); System.IO.File.Copy(a, Path.Combine(f.Models, "two.safetensors"));
        f.Store.Scan(f.Models); var assets = f.Store.Query(); Assert.Equal(2, assets.Length); Assert.Single(assets.Select(x => x.Sha256).Distinct()); Assert.All(assets, x => Assert.Equal(2, x.HashCopies));
        f.Store.Save(assets[0].Sha256, new(Note: "retained")); System.IO.File.Move(a, Path.Combine(f.Models, "renamed.safetensors"));
        f.Store.Scan(f.Models); Assert.Equal(3, f.Store.Query().Length); Assert.All(f.Store.Query(), x => Assert.Equal("retained", x.User.Note));
        Assert.False(f.Store.Query().Single(x => x.Name == "one").Available);
    }
    [Fact] public void SameNameDifferentHashIsKeptSeparateAndRejectsAmbiguousInsertion()
    {
        using var f = new LoraFixture(); f.File("a/same.safetensors"); f.File("b/same.safetensors", new() { ["different"] = "yes" }); f.Store.Scan(f.Models);
        var assets = f.Store.Query(); Assert.Equal(2, assets.Select(x => x.Sha256).Distinct().Count()); Assert.All(assets, x => Assert.False(f.Store.CanInsert(x)));
        f.Store.Save(assets[0].Sha256, new(Note: "first-only")); Assert.Equal(1, f.Store.Query().Count(x => x.User.Note.Length > 0));
    }
    [Fact] public void ChangedFileKeepsOldIdentityAndUserNotes()
    {
        using var f = new LoraFixture(); var path = f.File("a.safetensors"); f.Store.Scan(f.Models); var original = f.Store.Query().Single();
        f.Store.Save(original.Sha256, new(Note: "old")); f.File("a.safetensors", new() { ["replacement"] = "different-content" });
        Assert.False(f.Store.CanInsert(original)); f.Store.Scan(f.Models); var rows = f.Store.Query(); Assert.Equal(2, rows.Length);
        Assert.Equal("old", rows.Single(x => !x.Available).User.Note); Assert.Equal("", rows.Single(x => x.Available).User.Note);
    }
    [Fact] public void MissingFilesRetainMetadataAndUnavailableRootDoesNotFalselyMarkMissing()
    {
        using var f = new LoraFixture(); var path = f.File("a.safetensors"); f.Store.Scan(f.Models);
        Directory.Move(f.Models, f.Models + "-offline"); Assert.False(f.Store.Scan(f.Models).Complete); Assert.True(f.Store.Query().Single().Available);
        Directory.Move(f.Models + "-offline", f.Models); System.IO.File.Delete(path); Assert.Equal(1, f.Store.Scan(f.Models).Missing); Assert.False(f.Store.Query().Single().Available);
    }
    [Fact] public void MalformedMetadataAndCancellationRollbackWholeRoot()
    {
        using var f = new LoraFixture(); f.File("a.safetensors"); f.Store.Scan(f.Models); var before = f.Store.Query().Single();
        System.IO.File.WriteAllText(Path.Combine(f.Models, "bad.safetensors"), "bad"); var bad = f.Store.Scan(f.Models); Assert.False(bad.Complete); Assert.Equal(before, f.Store.Query().Single());
        System.IO.File.Delete(Path.Combine(f.Models, "bad.safetensors")); using var cancel = new CancellationTokenSource(); cancel.Cancel();
        Assert.False(f.Store.Scan(f.Models, cancel.Token).Complete); Assert.Equal(before, f.Store.Query().Single());
    }
    [Fact] public void BoundedMetadataAndUnsafeTokenRejected()
    {
        using var f = new LoraFixture(); var path = Path.Combine(f.Models, "bad.safetensors"); Span<byte> head = stackalloc byte[8]; BinaryPrimitives.WriteUInt64LittleEndian(head, ulong.MaxValue); System.IO.File.WriteAllBytes(path, head.ToArray());
        Assert.Throws<InvalidDataException>(() => LoraLocalMetadata.Read(path));
        f.File("good.safetensors"); System.IO.File.Delete(path); f.Store.Scan(f.Models); Assert.Throws<ArgumentException>(() => f.Store.Query().Single().Token(3));
        Assert.Throws<ArgumentException>(() => new LoraLibraryStore(Path.Combine(f.Root, "catalog.db")));
    }
    [Fact] public void SchemaRefusalAndMigrationBackupPreserveExistingBytes()
    {
        using var f = new LoraFixture(); var path = Path.Combine(f.Root, "future", "lora-library.db"); Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        using (var c = new SqliteConnection("Data Source=" + path + ";Pooling=False")) { c.Open(); using var cmd = c.CreateCommand(); cmd.CommandText = "CREATE TABLE personal(note TEXT);INSERT INTO personal VALUES('keep');PRAGMA user_version=99;"; cmd.ExecuteNonQuery(); }
        var bytes = System.IO.File.ReadAllBytes(path); Assert.Throws<InvalidDataException>(() => new LoraLibraryStore(path)); Assert.Equal(bytes, System.IO.File.ReadAllBytes(path));
        using (var c = new SqliteConnection("Data Source=" + path + ";Pooling=False")) { c.Open(); using var cmd = c.CreateCommand(); cmd.CommandText = "PRAGMA user_version=0"; cmd.ExecuteNonQuery(); }
        var store = new LoraLibraryStore(path); Assert.Single(Directory.GetFiles(Path.GetDirectoryName(path)!, "*.bak"));
        using var read = new SqliteConnection("Data Source=" + path + ";Pooling=False"); read.Open(); using var query = read.CreateCommand(); query.CommandText = "SELECT note FROM personal"; Assert.Equal("keep", query.ExecuteScalar());
    }
    [Fact] public void UsageAndFavoritesAreExplicitAndBackupsAreConsistent()
    {
        using var f = new LoraFixture(); f.File("a.safetensors"); f.Store.Scan(f.Models); var a = f.Store.Query().Single(); Assert.Equal(0, a.UsageCount);
        f.Store.Save(a.Sha256, new(Favorite: true, Note: "find me")); f.Store.RecordUse(a.Sha256); f.Store.RecordUse(a.Sha256);
        var actual = f.Store.Query("find me", true).Single(); Assert.Equal(2, actual.UsageCount); Assert.NotNull(actual.LastUsed);
        var backup = Path.Combine(f.Root, "backup", "lora-library.db"); Directory.CreateDirectory(Path.GetDirectoryName(backup)!); f.Store.Backup(backup);
        Assert.Equal(actual, new LoraLibraryStore(backup).Query().Single()); Assert.Throws<IOException>(() => f.Store.Backup(backup));
    }
    [Fact] public async Task WorkflowDraftsSaveRecipeInsertionAndUndoUseExistingWorkspace()
    {
        using var f = new LoraFixture(); f.File("a.safetensors"); f.File("b.safetensors", new() { ["x"] = "other" }); f.Store.Scan(f.Models);
        var workspace = Fixtures.Workspace(); workspace.Replace(" blue_hair ,unknown\\,raw"); var original = workspace.English; GenerationPreset? preset = null;
        var vm = new LoraLibraryViewModel(new(f.Root), workspace, new(Fixtures.Catalog()), new MemoryClipboard(), () => true, p => preset = p);
        await vm.InitializeAsync(); vm.Selected = vm.Assets[0]; var first = vm.Selected;
        vm.Note = "draft survives"; vm.Weight = "invalid"; vm.Selected = vm.Assets[1]; vm.Selected = first; Assert.Equal("invalid", vm.Weight); Assert.Equal("draft survives", vm.Note);
        vm.Weight = "0.7"; vm.AddTrigger(); vm.Triggers[0].Text = "blue_hair"; vm.PositiveAdditions = "unknown_trigger"; vm.NegativeAdditions = "lowres"; vm.Save();
        Assert.Equal("draft survives", vm.Selected!.User.Note); vm.Insert(false); Assert.Contains("<lora:a:0.7>", workspace.English); Assert.DoesNotContain("unknown_trigger", workspace.English);
        workspace.Undo(); Assert.Equal(original, workspace.English); vm.Insert(true); Assert.Contains("unknown_trigger", workspace.English); Assert.Equal(1, workspace.Items.Count(x => x.Canonical == "blue_hair"));
        workspace.Undo(); Assert.Equal(original, workspace.English); vm.CreatePreset(); Assert.Equal("lowres", preset!.Negative); Assert.Contains("<lora:a:0.7>", preset.Positive);
        Assert.Equal(2, f.Store.Query().Single(x => x.Name == "a").UsageCount);
    }
}

internal sealed class LoraFixture : IDisposable
{
    public string Root { get; } = Path.Combine(Path.GetTempPath(), "dtt-lora-" + Guid.NewGuid().ToString("N"));
    public string Models => Path.Combine(Root, "models");
    public LoraLibraryStore Store { get; }
    public LoraFixture() { Directory.CreateDirectory(Models); Store = new(Path.Combine(Root, "UserData", "lora-library.db")); Store.AddRoot(Models); }
    public string File(string relative, Dictionary<string, string>? metadata = null)
    {
        var path = Path.Combine(Models, relative); Directory.CreateDirectory(Path.GetDirectoryName(path)!); var json = Encoding.UTF8.GetBytes(JsonSerializer.Serialize(new { __metadata__ = metadata ?? new Dictionary<string, string>() }));
        using var stream = System.IO.File.Create(path); Span<byte> size = stackalloc byte[8]; BinaryPrimitives.WriteUInt64LittleEndian(size, (ulong)json.Length); stream.Write(size); stream.Write(json); return path;
    }
    public void Dispose() { SqliteConnection.ClearAllPools(); Directory.Delete(Root, true); }
}
