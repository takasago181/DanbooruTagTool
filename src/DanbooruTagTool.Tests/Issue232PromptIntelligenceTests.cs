using System.IO;
using System.Net;
using System.Net.Http;
using System.Text.Json;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Microsoft.Data.Sqlite;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue232PromptIntelligenceTests
{
    [Theory]
    [InlineData(" blue_hair BREAK red_hair AND (smile:1.2),<lora:detail:0.75>, unknown\\,raw ")]
    [InlineData("BREAK\nAND,blue_hair,, BREAK ")]
    [InlineData("[blue_hair:red_hair:0.5], ((smile)), {x|y}, (BREAK:1.2), \\AND, candy")]
    [InlineData("blue_hair,(broken,tail")]
    [InlineData("a),blue_hair")]
    public void SyntaxAndUnknownRoundTripByteForByteWithOutputAndUndo(string text)
    {
        var parser = new PromptParser(Fixtures.Catalog()); var parsed = parser.Parse(text); Assert.Equal(text, PromptParser.Serialize(parsed));
        var w = Fixtures.Workspace(); w.Replace(text); w.DirectEdit("other"); w.Undo(); Assert.Equal(text, w.English); w.Redo(); Assert.Equal("other", w.English);
        var snapshot = JsonSerializer.Deserialize<WorkspaceSnapshot>(JsonSerializer.Serialize(w.Snapshot()))!; w.Restore(snapshot); Assert.Equal("other", w.English);
    }
    [Fact] public void InlineControlsRecognizeCanonicalAliasesAndPreserveLosslessSeparators()
    {
        var w = Fixtures.Workspace(); w.Replace("azure_locks BREAK (blue_hair:1.2) AND red_hair");
        Assert.Equal(new[] { "BREAK", "AND" }, w.Items.Where(i => i.Kind == PromptItemKind.Control).Select(i => i.StructuredName));
        Assert.Equal("blue_hair BREAK (blue_hair:1.2) AND red_hair", PromptOutputFormatter.SerializeCanonical(w.Items));
        Assert.Equal(2, w.Items.Count(i => i.Canonical == "blue_hair"));
        w.AppendPreset(new PromptParser(Fixtures.Catalog()).Parse("smile AND unknown")); Assert.Contains(",smile AND unknown", w.English);
    }
    [Fact] public void WarningsResolveAliasesAndWeightAcrossSidesWithoutMutation()
    {
        var p = Fixtures.Workspace(); var n = Fixtures.Workspace(); p.Replace("azure_locks BREAK (blue_hair:1.2), unknown"); n.Replace("blue_hair,blue hair");
        var ps = p.Snapshot(); var ns = n.Snapshot(); var warnings = PromptDiagnostics.Warnings(p, n);
        Assert.Single(warnings, w => w.Code == "conflict"); Assert.Equal(2, warnings.Count(w => w.Code == "duplicate")); Assert.Single(warnings, w => w.Code == "raw");
        Assert.Equal(ps.Items, p.Items); Assert.Equal(ns.Items, n.Items); Assert.Equal("BREAK", PromptDiagnostics.Boundaries(p, "Positive").Single().Kind);
    }
    [Fact] public void NegativeDirectEditingHistoryAndRecoveryAreIndependentAndPersisted()
    {
        var store = new MemoryStore(); var clip = new MemoryClipboard(); var main = Fixtures.Vm(store, clip); main.Workspace.Replace("smile"); main.NegativeWorkspace.Replace(" blue_hair ,raw");
        main.Negative.StartDirect.Execute(null); Assert.False(main.CanEditPrompt); Assert.False(main.Import.CanExecute(null)); main.Negative.DirectText = "azure_locks BREAK <lora:a:0.5>"; main.Negative.ApplyDirect.Execute(null);
        Assert.Equal("smile", main.English); main.Negative.Undo.Execute(null); Assert.Equal(" blue_hair ,raw", main.Negative.English); main.Negative.Redo.Execute(null);
        var restored = Fixtures.Vm(store, clip); Assert.Equal(main.Negative.English, restored.Negative.English); Assert.Equal("smile", restored.English);
        restored.Negative.New.Execute(null); restored.Negative.Recover.Execute(null); Assert.Equal(main.Negative.English, restored.Negative.English);
    }
    [Fact] public async Task PresetPngLibraryAndForgeHaveExplicitNegativeActions()
    {
        using var d = new LibraryFixture(); var bridge = new RecordingBridge(); var main = new MainViewModel(Fixtures.Catalog(), new MemoryStore(), new MemoryClipboard(), forgeBridge: bridge, paths: new(d.Path));
        main.Workspace.Replace("smile"); main.NegativeWorkspace.Replace("original_negative"); var preset = new GenerationPreset(Guid.NewGuid(), "saved", "", "blue_hair", "lowres");
        main.ApplyPreset.Execute(preset); Assert.Equal("original_negative", main.Negative.English); main.PresetEditor.ApplyPresetNegative.Execute(preset); Assert.Equal("lowres", main.Negative.English); main.Negative.Undo.Execute(null);
        main.PresetEditor.CapturePresetNegative.Execute(null); Assert.Equal("original_negative", main.PresetNegative);
        var path = Path.Combine(d.Images, "a.png"); Issue226LibraryFoundationTests.WritePng(path); Assert.True(main.ImportGenerationPng(path)); Assert.Equal("original_negative", main.Negative.English);
        main.GenerationImport.RestoreNegative.Execute(null); Assert.Equal("lowres", main.Negative.English); main.Negative.Undo.Execute(null);
        var library = main.GenerationLibrary!; await library.AddRootAsync(d.Images); await library.ScanAsync(); library.Selected = library.Images.Single(); library.RestoreNegative.Execute(null);
        Assert.Equal("lowres", main.Negative.English); await main.Forge.SendWorkspacePair.ExecuteAsync(null); Assert.Equal("lowres", bridge.Request!.Negative); Assert.Equal(ForgeNegativeMode.Replace, bridge.Request.NegativeMode);
        main.NegativeWorkspace.Replace(""); await main.Forge.SendWorkspacePair.ExecuteAsync(null); Assert.Equal("", bridge.Request!.Negative); Assert.Equal(ForgeNegativeMode.Replace, bridge.Request.NegativeMode);
    }
    [Fact] public void VersionOneMigrationBacksUpExactPayloadAndPreservesAllPersonalState()
    {
        using var d = new TempDirectory(); var path = Path.Combine(d.Path, "user.db"); var p = Fixtures.Workspace(); p.Replace(" raw\\,comma ,blue_hair"); p.Replace("kept");
        var state = new UserState(p.Snapshot(), new UiState(Workspace: 3), [new(Guid.NewGuid(), "preset", "note", "positive", "negative")]); var json = JsonSerializer.Serialize(state);
        using (var c = new SqliteConnection("Data Source=" + path + ";Pooling=False")) { c.Open(); using var cmd = c.CreateCommand(); cmd.CommandText = "CREATE TABLE user_state(id INTEGER PRIMARY KEY,version INTEGER,payload TEXT);INSERT INTO user_state VALUES(1,1,$p);"; cmd.Parameters.AddWithValue("$p", json); cmd.ExecuteNonQuery(); }
        var store = new UserStateStore(path); var backup = Assert.Single(Directory.GetFiles(d.Path, "*.bak"));
        using (var c = new SqliteConnection("Data Source=" + backup + ";Pooling=False")) { c.Open(); using var cmd = c.CreateCommand(); cmd.CommandText = "SELECT payload FROM user_state"; Assert.Equal(json, cmd.ExecuteScalar()); cmd.CommandText = "SELECT version FROM user_state"; Assert.Equal(1L, cmd.ExecuteScalar()); }
        Assert.Equal(json, JsonSerializer.Serialize(store.Load())); Assert.Null(store.Load()!.Negative);
        var negative = Fixtures.Workspace(); negative.Replace("(blue_hair:0.7) AND raw"); store.Save(state with { Negative = negative.Snapshot() }); Assert.Equal(negative.English, PromptParser.Serialize(store.Load()!.Negative!.Items));
        new UserStateStore(path); Assert.Single(Directory.GetFiles(d.Path, "*.bak"));
    }
    [Theory] [InlineData(true)] [InlineData(false)]
    public void FutureSchemaOrPayloadRefusedWithoutWrites(bool schema)
    {
        using var d = new TempDirectory(); var path = Path.Combine(d.Path, "user.db"); _ = new UserStateStore(path);
        using (var c = new SqliteConnection("Data Source=" + path + ";Pooling=False")) { c.Open(); using var cmd = c.CreateCommand(); cmd.CommandText = schema ? "PRAGMA user_version=99" : "INSERT INTO user_state VALUES(1,99,'{\"kept\":true}')"; cmd.ExecuteNonQuery(); }
        var bytes = File.ReadAllBytes(path); Assert.Throws<InvalidDataException>(() => new UserStateStore(path)); Assert.Equal(bytes, File.ReadAllBytes(path));
    }
    [Fact] public void LegacyJsonMissingSeparatorPreservesCommaSurface()
    {
        var json = "{\"Prompt\":{\"Items\":[{\"Id\":\"00000000-0000-0000-0000-000000000001\",\"Surface\":\"a\",\"Kind\":4},{\"Id\":\"00000000-0000-0000-0000-000000000002\",\"Surface\":\" b\",\"Kind\":4}]},\"Ui\":{}}";
        var state = JsonSerializer.Deserialize<UserState>(json)!; Assert.Equal("a, b", PromptParser.Serialize(state.Prompt.Items));
    }
    [Fact] public void FutureSchemaWrittenAfterOpenRefusesLoadAndSaveWithoutWrites()
    {
        using var d = new TempDirectory(); var path = Path.Combine(d.Path, "user.db"); var store = new UserStateStore(path); var state = new UserState(Fixtures.Workspace().Snapshot(), new()); store.Save(state);
        using (var c = new SqliteConnection("Data Source=" + path + ";Pooling=False")) { c.Open(); using var cmd = c.CreateCommand(); cmd.CommandText = "PRAGMA user_version=99"; cmd.ExecuteNonQuery(); }
        var bytes = File.ReadAllBytes(path); Assert.Throws<InvalidDataException>(() => store.Load()); Assert.Throws<InvalidDataException>(() => store.Save(state)); Assert.Equal(bytes, File.ReadAllBytes(path));
    }
    [Theory] [InlineData("http://example.com")] [InlineData("https://localhost")]
    [InlineData("http://127.0.0.1:7860/path")] [InlineData("http://u:p@localhost")]
    public async Task TokenCounterRejectsUnsafeUrlWithoutRequest(string url)
    {
        var handler = new CounterHandler(); Assert.False((await new ForgeTokenCounter(new(handler)).CountAsync(url, "a", false, 20)).Available); Assert.Equal(0, handler.Calls);
    }
    [Theory] [InlineData("good")] [InlineData("noChunk")] [InlineData("side")] [InlineData("source")] [InlineData("text")] [InlineData("fakeModel")] [InlineData("badChunk")] [InlineData("http")]
    public async Task TokenCountRequiresSourceModelRequestAndChunkContract(string scenario)
    {
        var handler = new CounterHandler(scenario); var result = await new ForgeTokenCounter(new(handler)).CountAsync("http://127.0.0.1:7860", "blue_hair BREAK smile", false, 20);
        Assert.Equal(scenario is "good" or "noChunk", result.Available);
        if (scenario == "good") { Assert.Equal(80, result.Count); Assert.Equal(2, result.Chunks); Assert.Equal("real-model", result.Model); }
        if (scenario == "noChunk") Assert.Null(result.Chunks);
    }
    [Fact] public async Task CounterInFlightEditsNeverPublishStaleCounts()
    {
        var p = Fixtures.Workspace(); var n = Fixtures.Workspace(); var counter = new DelayedCounter(); var vm = new PromptIntelligenceViewModel(p, n, () => "http://localhost", counter);
        var pending = vm.CountAsync(); p.Replace("changed"); vm.Refresh(); counter.Ready.SetResult(); await pending; Assert.Contains("採用せず", vm.TokenStatus);
    }
    private sealed class RecordingBridge : IForgeBridgeClient { public ForgeBridgeSendRequest? Request; public Task<ForgeBridgeResult> SendAsync(string u, ForgeBridgeSendRequest r, CancellationToken ct = default) { Request = r; return Task.FromResult(new ForgeBridgeResult(true, "ok")); } }
    private sealed class DelayedCounter : IForgeTokenCounter { public TaskCompletionSource Ready = new(); public async Task<ForgeTokenCount> CountAsync(string u, string t, bool n, int s, CancellationToken ct = default) { await Ready.Task; return new(true, "source", "model", Engine: "engine", Tokenizer: "tokenizer", Count: 1, Capacity: 75); } }
    private sealed class CounterHandler(string scenario = "good") : HttpMessageHandler
    {
        public int Calls;
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage r, CancellationToken ct)
        {
            Calls++; var response = new { protocolVersion = 1, source = scenario == "source" ? "heuristic" : "Forge.ui.update_token_counter", text = scenario == "text" ? "wrong" : "blue_hair BREAK smile", negative = scenario == "side", steps = 20, model = "real-model", modelHash = "abc", engine = scenario == "fakeModel" ? "FakeInitialModel" : "StableDiffusionXL", tokenizer = "CLIPTokenizer", count = 80, capacity = 150, chunkLength = scenario == "noChunk" ? (int?)null : 75, chunks = scenario == "noChunk" ? (int?)null : scenario == "badChunk" ? 3 : 2 };
            return Task.FromResult(new HttpResponseMessage(scenario == "http" ? HttpStatusCode.NotFound : HttpStatusCode.OK) { Content = new StringContent(JsonSerializer.Serialize(response)) });
        }
    }
}
