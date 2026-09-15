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
}

public enum ForgeNegativeMode { Unchanged, Replace }

public sealed record ForgeBridgeSendRequest(string Positive, ForgeNegativeMode NegativeMode, string? Negative = null);
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
        timeout.CancelAfter(TimeSpan.FromSeconds(2));
        try
        {
            using var health = await http.GetAsync(Endpoint(baseUri, "health"), timeout.Token);
            if (!health.IsSuccessStatusCode)
                return health.StatusCode == HttpStatusCode.NotFound ? Failure("missing", "Forge連携拡張が見つかりません") : Failure("unavailable", "Forgeが起動していません");
            var healthJson = await ReadSmallBody(health, timeout.Token);
            if (!HasProtocolVersion(healthJson))
                return Failure("protocol", "Forge連携拡張のバージョンが合いません");

            var requestId = Guid.NewGuid().ToString("N");
            var payload = new Dictionary<string, object?>
            {
                ["protocolVersion"] = ForgeBridgeProtocol.Version,
                ["requestId"] = requestId,
                ["positive"] = request.Positive,
                ["negativeMode"] = request.NegativeMode == ForgeNegativeMode.Replace ? "replace" : "unchanged"
            };
            if (request.NegativeMode == ForgeNegativeMode.Replace) payload["negative"] = request.Negative ?? "";
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
            return new(true, "Forgeへ送信しました");
        }
        catch (TaskCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            return Failure("timeout", "Forgeへの接続がタイムアウトしました");
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

    private static bool TryAccepted(string json, string requestId)
    {
        using var document = JsonDocument.Parse(json);
        var root = document.RootElement;
        return HasProtocolVersion(root) &&
            root.TryGetProperty("accepted", out var accepted) && accepted.ValueKind == JsonValueKind.True &&
            root.TryGetProperty("requestId", out var responseId) && responseId.GetString() == requestId;
    }

    private static bool HasProtocolVersion(JsonElement root) => root.ValueKind == JsonValueKind.Object &&
        root.TryGetProperty("protocolVersion", out var version) && version.ValueKind == JsonValueKind.Number &&
        version.TryGetInt32(out var number) && number == ForgeBridgeProtocol.Version;
}
