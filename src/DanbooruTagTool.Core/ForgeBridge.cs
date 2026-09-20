using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.Json;

namespace DanbooruTagTool.Core;

public static class ForgeBridgeProtocol
{
    public const int Version = 1;
    public const int MaxPayloadBytes = 256 * 1024;
    public const string DefaultUrl = "http://127.0.0.1:7860";
    public const string GenerateCapability = "generate";
}

public enum ForgeNegativeMode { Unchanged, Replace }
public enum ForgeBridgeAction { SendOnly, SendAndGenerate }

public sealed record ForgeBridgeSendRequest(
    string Positive,
    ForgeNegativeMode NegativeMode,
    string? Negative = null,
    ForgeBridgeAction Action = ForgeBridgeAction.SendOnly);

public sealed record ForgeBridgeResult(bool Success, string Status, string ErrorCode = "");

public interface IForgeBridgeClient
{
    Task<ForgeBridgeResult> SendAsync(string baseUrl, ForgeBridgeSendRequest request, CancellationToken cancellationToken = default);
}

public sealed class ForgeBridgeClient(HttpClient? httpClient = null) : IForgeBridgeClient
{
    private readonly HttpClient http = httpClient ?? CreateDefaultClient();

    private static HttpClient CreateDefaultClient() => new(new HttpClientHandler { UseProxy = false });

    public async Task<ForgeBridgeResult> SendAsync(string baseUrl, ForgeBridgeSendRequest request, CancellationToken cancellationToken = default)
    {
        if (!TryGetLoopbackBase(baseUrl, out var baseUri))
            return Failure("url", "Forge URLを確認してください");
        if (request.Positive.Length > ForgeBridgeProtocol.MaxPayloadBytes || request.Negative is { Length: > ForgeBridgeProtocol.MaxPayloadBytes })
            return Failure("oversized", "Forgeへ送る内容が大きすぎます");

        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeout.CancelAfter(request.Action == ForgeBridgeAction.SendAndGenerate ? TimeSpan.FromSeconds(5) : TimeSpan.FromSeconds(2));
        try
        {
            using var health = await http.GetAsync(Endpoint(baseUri, "health"), timeout.Token);
            if (!health.IsSuccessStatusCode)
                return health.StatusCode == HttpStatusCode.NotFound ? Failure("missing", "Forge連携拡張が見つかりません") : Failure("unavailable", "Forgeが起動していません");
            var healthJson = await ReadSmallBody(health, timeout.Token);
            if (!HasProtocolVersion(healthJson))
                return Failure("protocol", "Forge連携拡張のバージョンが合いません");
            if (request.Action == ForgeBridgeAction.SendAndGenerate && !HasCapability(healthJson, ForgeBridgeProtocol.GenerateCapability))
                return Failure("upgrade", "Forge連携拡張を更新してください（Forgeで生成には最新版が必要です）");

            var requestId = Guid.NewGuid().ToString("N");
            var payload = new Dictionary<string, object?>
            {
                ["protocolVersion"] = ForgeBridgeProtocol.Version,
                ["requestId"] = requestId,
                ["positive"] = request.Positive,
                ["negativeMode"] = request.NegativeMode == ForgeNegativeMode.Replace ? "replace" : "unchanged"
            };
            if (request.NegativeMode == ForgeNegativeMode.Replace) payload["negative"] = request.Negative ?? "";
            // Keep the legacy send-only payload shape intact so older bridge installs continue to work.
            if (request.Action == ForgeBridgeAction.SendAndGenerate) payload["action"] = "send_and_generate";

            var json = JsonSerializer.Serialize(payload);
            if (Encoding.UTF8.GetByteCount(json) > ForgeBridgeProtocol.MaxPayloadBytes)
                return Failure("oversized", "Forgeへ送る内容が大きすぎます");

            using var content = new StringContent(json, Encoding.UTF8, "application/json");
            using var response = await http.PostAsync(Endpoint(baseUri, "prompt"), content, timeout.Token);
            if (!response.IsSuccessStatusCode)
                return response.StatusCode == HttpStatusCode.NotFound ? Failure("missing", "Forge連携拡張が見つかりません") : Failure("rejected", "Forge連携拡張がpayloadを拒否しました");
            var responseJson = await ReadSmallBody(response, timeout.Token);
            if (!TryAccepted(responseJson, requestId))
                return Failure("protocol", "Forge連携拡張の応答を確認できません");

            if (request.Action == ForgeBridgeAction.SendOnly)
                return new(true, "Forgeへ送信しました");

            return await WaitForGenerateResultAsync(baseUri, requestId, timeout.Token);
        }
        catch (TaskCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            return request.Action == ForgeBridgeAction.SendAndGenerate
                ? Failure("timeout", "Forge側の生成開始を確認できませんでした")
                : Failure("timeout", "Forgeへの接続がタイムアウトしました");
        }
        catch (HttpRequestException)
        {
            return Failure("unavailable", "Forgeが起動していません");
        }
        catch (Exception ex) when (ex is JsonException or InvalidOperationException)
        {
            return Failure("protocol", "Forge連携拡張の応答を確認できません");
        }
    }

    private async Task<ForgeBridgeResult> WaitForGenerateResultAsync(Uri baseUri, string requestId, CancellationToken cancellationToken)
    {
        while (true)
        {
            using var response = await http.GetAsync(Endpoint(baseUri, "result/" + requestId), cancellationToken);
            if (!response.IsSuccessStatusCode)
                return Failure("protocol", "Forge側の生成結果を確認できません");

            var json = await ReadSmallBody(response, cancellationToken);
            if (!TryGenerateResult(json, out var completed, out var success, out var error))
                return Failure("protocol", "Forge側の生成結果を確認できません");
            if (completed)
                return success ? new(true, "Forgeで生成を開始しました") : Failure(error, GenerateFailureMessage(error));

            await Task.Delay(100, cancellationToken);
        }
    }

    private static string GenerateFailureMessage(string error) => error switch
    {
        "positive_missing" => "ForgeのPositive Prompt欄を見つけられません",
        "negative_missing" => "ForgeのNegative Prompt欄を見つけられません",
        "generate_missing" => "ForgeのGenerateボタンを見つけられません。Forgeまたは連携拡張を確認してください",
        "generate_failed" => "Forge側でGenerate操作に失敗しました",
        _ => "Forge側で生成を開始できませんでした"
    };

    private static ForgeBridgeResult Failure(string code, string status) => new(false, status, code);

    private static Uri Endpoint(Uri baseUri, string endpoint) => new(baseUri.ToString().TrimEnd('/') + "/dtt-bridge/" + endpoint);

    private static bool TryGetLoopbackBase(string value, out Uri uri)
    {
        if (Uri.TryCreate(value?.Trim(), UriKind.Absolute, out uri!) && uri.Scheme == Uri.UriSchemeHttp &&
            (uri.Host.Equals("localhost", StringComparison.OrdinalIgnoreCase) ||
             (IPAddress.TryParse(uri.Host, out var address) && IPAddress.IsLoopback(address)))) return true;
        uri = null!;
        return false;
    }

    private static async Task<string> ReadSmallBody(HttpResponseMessage response, CancellationToken cancellationToken)
    {
        var bytes = await response.Content.ReadAsByteArrayAsync(cancellationToken);
        if (bytes.Length > 16 * 1024) throw new JsonException("Bridge response too large");
        return Encoding.UTF8.GetString(bytes);
    }

    private static bool HasProtocolVersion(string json)
    {
        using var document = JsonDocument.Parse(json);
        return HasProtocolVersion(document.RootElement);
    }

    private static bool HasCapability(string json, string capability)
    {
        using var document = JsonDocument.Parse(json);
        var root = document.RootElement;
        if (!HasProtocolVersion(root) || !root.TryGetProperty("capabilities", out var capabilities) || capabilities.ValueKind != JsonValueKind.Array)
            return false;
        return capabilities.EnumerateArray().Any(item => item.ValueKind == JsonValueKind.String && item.GetString() == capability);
    }

    private static bool TryAccepted(string json, string requestId)
    {
        using var document = JsonDocument.Parse(json);
        var root = document.RootElement;
        return HasProtocolVersion(root) &&
            root.TryGetProperty("accepted", out var accepted) && accepted.ValueKind == JsonValueKind.True &&
            root.TryGetProperty("requestId", out var responseId) && responseId.GetString() == requestId;
    }

    private static bool TryGenerateResult(string json, out bool completed, out bool success, out string error)
    {
        completed = false;
        success = false;
        error = "";
        using var document = JsonDocument.Parse(json);
        var root = document.RootElement;
        if (!HasProtocolVersion(root)) return false;
        if (!root.TryGetProperty("result", out var result)) return false;
        if (result.ValueKind == JsonValueKind.Null) return true;
        if (result.ValueKind != JsonValueKind.Object ||
            !result.TryGetProperty("success", out var successElement) ||
            successElement.ValueKind is not (JsonValueKind.True or JsonValueKind.False))
            return false;

        completed = true;
        success = successElement.GetBoolean();
        if (result.TryGetProperty("error", out var errorElement) && errorElement.ValueKind == JsonValueKind.String)
            error = errorElement.GetString() ?? "";
        return true;
    }

    private static bool HasProtocolVersion(JsonElement root) => root.ValueKind == JsonValueKind.Object &&
        root.TryGetProperty("protocolVersion", out var version) && version.ValueKind == JsonValueKind.Number &&
        version.TryGetInt32(out var number) && number == ForgeBridgeProtocol.Version;
}
