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
    public const string RecipeCapability = "recipe_settings";
}

public enum ForgeNegativeMode { Unchanged, Replace }
public enum ForgeBridgeAction { SendOnly, SendAndGenerate, ApplyRecipe }

public sealed record ForgeBridgeSendRequest(
    string Positive,
    ForgeNegativeMode NegativeMode,
    string? Negative = null,
    ForgeBridgeAction Action = ForgeBridgeAction.SendOnly,
    GenerationRecipe? Recipe = null);

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

        if (request.Action == ForgeBridgeAction.ApplyRecipe && request.Recipe?.HasAny != true)
            return Failure("recipe_empty", "このプリセットには生成条件がありません");

        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeout.CancelAfter(request.Recipe?.HasAny == true ? TimeSpan.FromSeconds(30) :
            request.Action == ForgeBridgeAction.SendAndGenerate ? TimeSpan.FromSeconds(5) : TimeSpan.FromSeconds(2));
        try
        {
            using var health = await http.GetAsync(Endpoint(baseUri, "health"), timeout.Token);
            if (!health.IsSuccessStatusCode)
                return health.StatusCode == HttpStatusCode.NotFound ? Failure("missing", "Forge連携拡張が見つかりません") : Failure("unavailable", "Forgeが起動していません");
            var healthJson = await ReadSmallBody(health, timeout.Token);
            if (!HasProtocolVersion(healthJson))
                return Failure("protocol", "Forge連携拡張のバージョンが合いません");
            if (request.Action == ForgeBridgeAction.SendAndGenerate && !HasCapability(healthJson, ForgeBridgeProtocol.GenerateCapability))
                return Failure("upgrade", "Forge連携拡張を更新してください（Forge設定→拡張を配置→Forge再起動）");
            if ((request.Action == ForgeBridgeAction.ApplyRecipe || request.Recipe?.HasAny == true) &&
                !HasCapability(healthJson, ForgeBridgeProtocol.RecipeCapability))
                return Failure("upgrade", "Forge連携拡張を更新してください（生成レシピ対応版が必要です）");

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
            else if (request.Action == ForgeBridgeAction.ApplyRecipe) payload["action"] = "apply_recipe";
            if (request.Recipe?.HasAny == true) payload["settings"] = RecipePayload(request.Recipe);

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

            return await WaitForActionResultAsync(baseUri, requestId, request, timeout.Token);
        }
        catch (TaskCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            return request.Action switch
            {
                ForgeBridgeAction.SendAndGenerate => Failure("timeout", "Forge側の生成開始を確認できませんでした。Forgeを再起動して連携拡張を確認してください"),
                ForgeBridgeAction.ApplyRecipe => Failure("timeout", "Forge側のレシピ適用を確認できませんでした"),
                _ => Failure("timeout", "Forgeへの接続がタイムアウトしました")
            };
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

    private async Task<ForgeBridgeResult> WaitForActionResultAsync(Uri baseUri, string requestId, ForgeBridgeSendRequest request, CancellationToken cancellationToken)
    {
        while (true)
        {
            using var response = await http.GetAsync(Endpoint(baseUri, "result/" + requestId), cancellationToken);
            if (!response.IsSuccessStatusCode)
                return Failure("protocol", "Forge側の処理結果を確認できません");

            var json = await ReadSmallBody(response, cancellationToken);
            if (!TryGenerateResult(json, out var completed, out var success, out var error))
                return Failure("protocol", "Forge側の処理結果を確認できません");
            if (completed)
            {
                if (!success) return Failure(error, ActionFailureMessage(error));
                if (request.Action == ForgeBridgeAction.ApplyRecipe) return new(true, "Forgeへレシピを適用しました");
                return new(true, request.Recipe?.HasAny == true ? "Forgeへレシピ生成操作を送信しました" : "Forgeへ生成操作を送信しました");
            }

            await Task.Delay(100, cancellationToken);
        }
    }

    private static string ActionFailureMessage(string error) => error switch
    {
        "positive_missing" => "ForgeのPositive Prompt欄を見つけられません",
        "negative_missing" => "ForgeのNegative Prompt欄を見つけられません",
        "generate_missing" => "ForgeのGenerateボタンを見つけられません。Forgeまたは連携拡張を確認してください",
        "generate_failed" => "Forge側でGenerate操作に失敗しました",
        "model_not_found" => "レシピのModelをForgeで見つけられません",
        "model_apply_failed" => "ForgeでModelを適用できませんでした",
        "seed_missing" => "ForgeのSeed欄を見つけられません",
        "steps_missing" => "ForgeのSteps欄を見つけられません",
        "sampler_missing" => "ForgeのSampler欄または選択肢を見つけられません",
        "scheduler_missing" => "ForgeのScheduler欄または選択肢を見つけられません",
        "cfg_missing" => "ForgeのCFG欄を見つけられません",
        "width_missing" => "ForgeのWidth欄を見つけられません",
        "height_missing" => "ForgeのHeight欄を見つけられません",
        "recipe_failed" => "Forge側で生成レシピを適用できませんでした",
        _ => "Forge側の処理を完了できませんでした"
    };

    private static Dictionary<string, object> RecipePayload(GenerationRecipe recipe)
    {
        var result = new Dictionary<string, object>();
        if (!string.IsNullOrWhiteSpace(recipe.Model)) result["model"] = recipe.Model!;
        if (recipe.Seed is { } seed) result["seed"] = seed;
        if (recipe.Steps is { } steps) result["steps"] = steps;
        if (!string.IsNullOrWhiteSpace(recipe.Sampler)) result["sampler"] = recipe.Sampler!;
        if (!string.IsNullOrWhiteSpace(recipe.Scheduler)) result["scheduler"] = recipe.Scheduler!;
        if (recipe.Cfg is { } cfg) result["cfg"] = cfg;
        if (recipe.Width is { } width) result["width"] = width;
        if (recipe.Height is { } height) result["height"] = height;
        return result;
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
