using System.Net;
using System.Net.Http;
using System.IO;
using System.Text;
using DanbooruTagTool.App;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public sealed class Issue80Tests
{
    [Fact]
    public async Task CommonSendUsesExactVisiblePositiveAndLeavesNegativeUnchanged()
    {
        var bridge = new RecordingBridge();
        var vm = new MainViewModel(Fixtures.Catalog(), new MemoryStore(), new MemoryClipboard(), forgeBridge: bridge);
        vm.Workspace.Replace("long_hair, raw, (blue_hair:1.2)");
        vm.OutputProfile = PromptOutputProfile.GenerationFriendly;
        var before = vm.Workspace.Items.Select(item => (item.Id, item.Surface)).ToArray();

        await vm.SendToForgeAsync();

        Assert.Equal(vm.English, bridge.Request.Positive);
        Assert.Equal("long hair, raw, (blue hair:1.2)", bridge.Request.Positive);
        Assert.Equal(ForgeNegativeMode.Unchanged, bridge.Request.NegativeMode);
        Assert.Null(bridge.Request.Negative);
        Assert.Equal(before, vm.Workspace.Items.Select(item => (item.Id, item.Surface)).ToArray());
        Assert.Equal("Forgeへ送信しました", vm.Status);
    }

    [Fact]
    public async Task PresetSendUsesCurrentVisiblePositiveAndExactNegativeIncludingEmptyReplace()
    {
        var bridge = new RecordingBridge();
        var vm = new MainViewModel(Fixtures.Catalog(), new MemoryStore(), new MemoryClipboard(), forgeBridge: bridge);
        vm.Workspace.Replace("long_hair");
        var preset = new GenerationPreset(Guid.NewGuid(), "Set", "", "blue_hair", "  lowres\r\n(custom:1.2)  ");

        await vm.SendToForgeAsync(preset);

        Assert.Equal("long_hair", bridge.Request.Positive);
        Assert.Equal(ForgeNegativeMode.Replace, bridge.Request.NegativeMode);
        Assert.Equal(preset.Negative, bridge.Request.Negative);
        await vm.SendToForgeAsync(preset with { Negative = "" });
        Assert.Equal(ForgeNegativeMode.Replace, bridge.Request.NegativeMode);
        Assert.Equal("", bridge.Request.Negative);
    }

    [Fact]
    public void ForgeUrlDefaultsAndPersistsThroughExistingUiState()
    {
        var store = new MemoryStore();
        var vm = new MainViewModel(Fixtures.Catalog(), store, new MemoryClipboard());
        Assert.Equal(ForgeBridgeProtocol.DefaultUrl, vm.ForgeUrl);

        vm.ForgeUrl = "http://localhost:7860";
        vm.SaveForgeSettings.Execute(null);

        var restored = new MainViewModel(Fixtures.Catalog(), store, new MemoryClipboard());
        Assert.Equal("http://localhost:7860", restored.ForgeUrl);
        Assert.Equal(PromptOutputProfile.Canonical, restored.OutputProfile);
    }

    [Fact]
    public async Task ClientPerformsHealthThenPromptAndUsesVersionedPayload()
    {
        var handler = new RecordingHandler((request, index) => index == 0
            ? Json(HttpStatusCode.OK, "{\"protocolVersion\":1,\"ok\":true}")
            : Json(HttpStatusCode.OK, "{\"protocolVersion\":1,\"accepted\":true,\"requestId\":\"PLACEHOLDER\"}"));
        var client = new ForgeBridgeClient(new HttpClient(handler));
        var result = await client.SendAsync(ForgeBridgeProtocol.DefaultUrl, new("blue hair", ForgeNegativeMode.Replace, "bad anatomy"));

        Assert.False(result.Success); // response intentionally has the wrong request id
        Assert.Equal("health", handler.Requests[0].RequestUri!.AbsolutePath.Split('/').Last());
        Assert.Equal("prompt", handler.Requests[1].RequestUri!.AbsolutePath.Split('/').Last());
        var body = handler.Bodies[1];
        Assert.Contains("\"protocolVersion\":1", body);
        Assert.Contains("\"negativeMode\":\"replace\"", body);
        Assert.Contains("\"negative\":\"bad anatomy\"", body);
    }

    [Fact]
    public async Task ClientRejectsProtocolMismatchOversizedAndNonLoopbackBeforeSending()
    {
        var mismatchHandler = new RecordingHandler((_, _) => Json(HttpStatusCode.OK, "{\"protocolVersion\":99}"));
        var mismatch = await new ForgeBridgeClient(new HttpClient(mismatchHandler)).SendAsync(ForgeBridgeProtocol.DefaultUrl, new("x", ForgeNegativeMode.Unchanged));
        Assert.False(mismatch.Success);
        Assert.Equal("protocol", mismatch.ErrorCode);
        Assert.Single(mismatchHandler.Requests);

        var oversized = await new ForgeBridgeClient(new HttpClient(new RecordingHandler((_, _) => throw new InvalidOperationException())))
            .SendAsync(ForgeBridgeProtocol.DefaultUrl, new(new string('x', ForgeBridgeProtocol.MaxPayloadBytes + 1), ForgeNegativeMode.Unchanged));
        Assert.False(oversized.Success);
        Assert.Equal("oversized", oversized.ErrorCode);

        var remote = await new ForgeBridgeClient(new HttpClient(new RecordingHandler((_, _) => throw new InvalidOperationException())))
            .SendAsync("http://192.0.2.1:7860", new("x", ForgeNegativeMode.Unchanged));
        Assert.False(remote.Success);
        Assert.Equal("url", remote.ErrorCode);
    }

    [Fact]
    public async Task FailedBridgeReturnsActionableStatusWithoutChangingPrompt()
    {
        var bridge = new RecordingBridge { Result = new(false, "Forgeが起動していません", "unavailable") };
        var vm = new MainViewModel(Fixtures.Catalog(), new MemoryStore(), new MemoryClipboard(), forgeBridge: bridge);
        vm.Workspace.Replace("long_hair, raw");
        var before = vm.English;

        await vm.SendToForgeAsync();

        Assert.Equal("Forgeが起動していません", vm.Status);
        Assert.Equal(before, vm.English);
    }

    [Fact]
    public async Task HealthFailureIsReturnedWithoutBlockingOrMutatingPrompt()
    {
        var client = new ForgeBridgeClient(new HttpClient(new RecordingHandler((_, _) => throw new HttpRequestException())));
        var result = await client.SendAsync(ForgeBridgeProtocol.DefaultUrl, new("x", ForgeNegativeMode.Unchanged));

        Assert.False(result.Success);
        Assert.Equal("unavailable", result.ErrorCode);
    }

    [Fact]
    public async Task ClientTimeoutReturnsWithoutWaitingForLongHandler()
    {
        var client = new ForgeBridgeClient(new HttpClient(new DelayedHandler()));
        var started = DateTime.UtcNow;

        var result = await client.SendAsync(ForgeBridgeProtocol.DefaultUrl, new("x", ForgeNegativeMode.Unchanged));

        Assert.False(result.Success);
        Assert.Equal("timeout", result.ErrorCode);
        Assert.InRange((DateTime.UtcNow - started).TotalSeconds, 1.5, 5);
    }

    [Fact]
    public void CompanionAssetsContainLocalProtocolAndNeverGenerationHooks()
    {
        var root = Path.Combine(AppContext.BaseDirectory, "ForgeBridge");
        var python = File.ReadAllText(Path.Combine(root, "scripts", "dtt_bridge.py"));
        var javascript = File.ReadAllText(Path.Combine(root, "javascript", "dtt_bridge.js"));

        Assert.Contains("/dtt-bridge/health", python);
        Assert.Contains("/dtt-bridge/prompt", python);
        Assert.Contains("/dtt-bridge/pending", python);
        Assert.Contains("#txt2img_prompt", javascript);
        Assert.Contains("#txt2img_neg_prompt", javascript);
        Assert.Contains("dispatchEvent(new Event(\"input\"", javascript);
        Assert.DoesNotContain("/sdapi/v1/txt2img", python);
        Assert.DoesNotContain("generate", javascript, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void InstallerCopiesOnlyCompanionFilesIntoSelectedExtensionsFolder()
    {
        using var directory = new TempDirectory();
        var extensions = Path.Combine(directory.Path, "extensions");
        Directory.CreateDirectory(extensions);

        Assert.True(ForgeBridgeInstaller.TryInstall(directory.Path, out var message), message);
        Assert.Contains("再起動", message);
        Assert.True(File.Exists(Path.Combine(extensions, "dtt_bridge", "scripts", "dtt_bridge.py")));
        Assert.True(File.Exists(Path.Combine(extensions, "dtt_bridge", "javascript", "dtt_bridge.js")));
        Assert.False(File.Exists(Path.Combine(directory.Path, "webui-user.bat")));
    }

    private static HttpResponseMessage Json(HttpStatusCode status, string body) => new(status) { Content = new StringContent(body, Encoding.UTF8, "application/json") };

    private sealed class RecordingBridge : IForgeBridgeClient
    {
        public ForgeBridgeSendRequest Request { get; private set; } = new("", ForgeNegativeMode.Unchanged);
        public ForgeBridgeResult Result { get; set; } = new(true, "Forgeへ送信しました");
        public Task<ForgeBridgeResult> SendAsync(string baseUrl, ForgeBridgeSendRequest request, CancellationToken cancellationToken = default)
        { Request = request; return Task.FromResult(Result); }
    }

    private sealed class RecordingHandler(Func<HttpRequestMessage, int, HttpResponseMessage> responder) : HttpMessageHandler
    {
        public List<HttpRequestMessage> Requests { get; } = [];
        public List<string> Bodies { get; } = [];
        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        { Requests.Add(request); Bodies.Add(request.Content == null ? "" : await request.Content.ReadAsStringAsync(cancellationToken)); return responder(request, Requests.Count - 1); }
    }

    private sealed class DelayedHandler : HttpMessageHandler
    {
        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        { await Task.Delay(TimeSpan.FromSeconds(10), cancellationToken); return Json(HttpStatusCode.OK, "{}"); }
    }
}
