using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue145ForgeGenerateTests
{
    [Fact]
    public async Task LegacyBridgeStillAcceptsSendOnlyWithoutActionField()
    {
        string? posted = null;
        var client = Client(async (request, cancellationToken) =>
        {
            if (request.Method == HttpMethod.Get && request.RequestUri!.AbsolutePath.EndsWith("/health", StringComparison.Ordinal))
                return Json("""{"protocolVersion":1,"ok":true,"ready":true}""");

            if (request.Method == HttpMethod.Post && request.RequestUri!.AbsolutePath.EndsWith("/prompt", StringComparison.Ordinal))
            {
                posted = await request.Content!.ReadAsStringAsync(cancellationToken);
                using var document = JsonDocument.Parse(posted);
                var requestId = document.RootElement.GetProperty("requestId").GetString();
                return Json($$"""{"protocolVersion":1,"accepted":true,"requestId":"{{requestId}}"}""");
            }

            throw new InvalidOperationException(request.RequestUri!.ToString());
        });

        var result = await client.SendAsync(
            "http://127.0.0.1:7860",
            new ForgeBridgeSendRequest("blue_hair", ForgeNegativeMode.Unchanged));

        Assert.True(result.Success);
        Assert.Equal("Forgeへ送信しました", result.Status);
        using var payload = JsonDocument.Parse(posted!);
        Assert.False(payload.RootElement.TryGetProperty("action", out _));
    }

    [Fact]
    public async Task GenerateRequiresUpdatedBridgeCapability()
    {
        var client = Client((request, _) =>
        {
            Assert.EndsWith("/health", request.RequestUri!.AbsolutePath, StringComparison.Ordinal);
            return Task.FromResult(Json("""{"protocolVersion":1,"ok":true,"ready":true}"""));
        });

        var result = await client.SendAsync(
            "http://localhost:7860",
            new ForgeBridgeSendRequest("blue_hair", ForgeNegativeMode.Unchanged, Action: ForgeBridgeAction.SendAndGenerate));

        Assert.False(result.Success);
        Assert.Equal("upgrade", result.ErrorCode);
        Assert.Contains("更新", result.Status);
    }

    [Fact]
    public async Task GenerateSendsExplicitActionAndWaitsForBrowserAck()
    {
        string? posted = null;
        string? requestId = null;
        var client = Client(async (request, cancellationToken) =>
        {
            var path = request.RequestUri!.AbsolutePath;
            if (request.Method == HttpMethod.Get && path.EndsWith("/health", StringComparison.Ordinal))
                return Json("""{"protocolVersion":1,"ok":true,"ready":true,"capabilities":["prompt","generate","result_ack"]}""");

            if (request.Method == HttpMethod.Post && path.EndsWith("/prompt", StringComparison.Ordinal))
            {
                posted = await request.Content!.ReadAsStringAsync(cancellationToken);
                using var document = JsonDocument.Parse(posted);
                requestId = document.RootElement.GetProperty("requestId").GetString();
                return Json($$"""{"protocolVersion":1,"accepted":true,"requestId":"{{requestId}}"}""");
            }

            if (request.Method == HttpMethod.Get && path.EndsWith("/result/" + requestId, StringComparison.Ordinal))
                return Json("""{"protocolVersion":1,"result":{"success":true,"error":""}}""");

            throw new InvalidOperationException(request.RequestUri!.ToString());
        });

        var result = await client.SendAsync(
            "http://127.0.0.1:7860",
            new ForgeBridgeSendRequest("blue_hair", ForgeNegativeMode.Unchanged, Action: ForgeBridgeAction.SendAndGenerate));

        Assert.True(result.Success);
        Assert.Equal("Forgeで生成を開始しました", result.Status);
        using var payload = JsonDocument.Parse(posted!);
        Assert.Equal("send_and_generate", payload.RootElement.GetProperty("action").GetString());
        Assert.Equal("unchanged", payload.RootElement.GetProperty("negativeMode").GetString());
    }

    [Fact]
    public async Task GenerateSurfacesMissingForgeGenerateButton()
    {
        string? requestId = null;
        var client = Client(async (request, cancellationToken) =>
        {
            var path = request.RequestUri!.AbsolutePath;
            if (path.EndsWith("/health", StringComparison.Ordinal))
                return Json("""{"protocolVersion":1,"ok":true,"ready":true,"capabilities":["prompt","generate","result_ack"]}""");

            if (request.Method == HttpMethod.Post && path.EndsWith("/prompt", StringComparison.Ordinal))
            {
                var body = await request.Content!.ReadAsStringAsync(cancellationToken);
                using var document = JsonDocument.Parse(body);
                requestId = document.RootElement.GetProperty("requestId").GetString();
                return Json($$"""{"protocolVersion":1,"accepted":true,"requestId":"{{requestId}}"}""");
            }

            if (request.Method == HttpMethod.Get && path.EndsWith("/result/" + requestId, StringComparison.Ordinal))
                return Json("""{"protocolVersion":1,"result":{"success":false,"error":"generate_missing"}}""");

            throw new InvalidOperationException(request.RequestUri!.ToString());
        });

        var result = await client.SendAsync(
            "http://127.0.0.1:7860",
            new ForgeBridgeSendRequest("blue_hair", ForgeNegativeMode.Unchanged, Action: ForgeBridgeAction.SendAndGenerate));

        Assert.False(result.Success);
        Assert.Equal("generate_missing", result.ErrorCode);
        Assert.Contains("Generateボタン", result.Status);
    }

    [Fact]
    public async Task ForgeViewModelGenerateUsesCurrentPromptAndGenerateAction()
    {
        var fake = new RecordingBridge();
        string status = "";
        var vm = new ForgeViewModel(fake, () => { }, () => true, () => "blue_hair, smile", value => status = value, () => { });

        await vm.GenerateAsync(null, CancellationToken.None);

        var request = Assert.IsType<ForgeBridgeSendRequest>(fake.Request);
        Assert.Equal("blue_hair, smile", request.Positive);
        Assert.Equal(ForgeNegativeMode.Unchanged, request.NegativeMode);
        Assert.Equal(ForgeBridgeAction.SendAndGenerate, request.Action);
        Assert.Equal("ok", status);
    }

    private static ForgeBridgeClient Client(Func<HttpRequestMessage, CancellationToken, Task<HttpResponseMessage>> handler) =>
        new(new HttpClient(new StubHandler(handler)));

    private static HttpResponseMessage Json(string json) =>
        new(HttpStatusCode.OK) { Content = new StringContent(json, Encoding.UTF8, "application/json") };

    private sealed class StubHandler(Func<HttpRequestMessage, CancellationToken, Task<HttpResponseMessage>> handler) : HttpMessageHandler
    {
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken) =>
            handler(request, cancellationToken);
    }

    private sealed class RecordingBridge : IForgeBridgeClient
    {
        public ForgeBridgeSendRequest? Request { get; private set; }

        public Task<ForgeBridgeResult> SendAsync(string baseUrl, ForgeBridgeSendRequest request, CancellationToken cancellationToken = default)
        {
            Request = request;
            return Task.FromResult(new ForgeBridgeResult(true, "ok"));
        }
    }
}
