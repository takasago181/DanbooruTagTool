using System.Buffers.Binary;
using System.Net;
using System.Text;
using System.Text.Json;

namespace DanbooruTagTool.Core;

public sealed record ForgeApiModel(string Title, string Name, string? Hash);
public sealed record ForgeApiCapabilities(IReadOnlyList<ForgeApiModel> Models, IReadOnlyList<string> Samplers, IReadOnlyList<string> Schedulers);
public sealed record ForgeApiRequest(string Positive, string Negative, GenerationRecipe Recipe);
public sealed record ForgeApiResult(bool Success, string Status, string? ImagePath = null, GenerationMetadataSnapshot? Metadata = null);
public interface IForgeGenerationApiClient
{
    Task<ForgeApiCapabilities> ProbeAsync(string baseUrl, CancellationToken cancellationToken = default);
    Task<ForgeApiResult> GenerateAsync(string baseUrl, ForgeApiRequest request, string outputDirectory, CancellationToken cancellationToken = default);
}

/// <summary>A1111-compatible HTTP adapter. Never edits Forge options, retries a POST, or uses Gradio.</summary>
public sealed class ForgeGenerationApiClient : IForgeGenerationApiClient
{
    private readonly HttpClient http;
    private readonly SemaphoreSlim generation = new(1, 1);
    public ForgeGenerationApiClient(HttpClient? client = null) => http = client ?? new(new HttpClientHandler { UseProxy = false, AllowAutoRedirect = false }) { Timeout = Timeout.InfiniteTimeSpan };
    private static Uri Base(string value)
    {
        if (!Uri.TryCreate(value, UriKind.Absolute, out var uri) || uri.Scheme != "http" ||
            !(uri.Host.Equals("localhost", StringComparison.OrdinalIgnoreCase) || IPAddress.TryParse(uri.Host, out var ip) && IPAddress.IsLoopback(ip)) ||
            uri.UserInfo.Length != 0 || uri.Query.Length != 0 || uri.Fragment.Length != 0 || uri.AbsolutePath != "/")
            throw new ArgumentException("Forge API URLはhttp://localhost またはloopback IPのルートURLを指定してください。");
        return uri;
    }
    private async Task<JsonDocument> Read(HttpResponseMessage response, int limit, CancellationToken ct)
    {
        if (!response.IsSuccessStatusCode) throw new HttpRequestException($"Forge API HTTP {(int)response.StatusCode}。--apiとAPI互換性を確認してください。");
        if (response.Content.Headers.ContentLength > limit) throw new InvalidDataException("Forge API応答が上限を超えました。");
        using var s = await response.Content.ReadAsStreamAsync(ct); using var buffer = new MemoryStream();
        var bytes = new byte[8192]; int n;
        while ((n = await s.ReadAsync(bytes, ct)) != 0) { if (buffer.Length + n > limit) throw new InvalidDataException("Forge API応答が上限を超えました。"); buffer.Write(bytes, 0, n); }
        return JsonDocument.Parse(buffer.ToArray());
    }
    private async Task<JsonDocument> Get(Uri uri, string path, CancellationToken ct)
    { using var response = await http.GetAsync(new Uri(uri, path), HttpCompletionOption.ResponseHeadersRead, ct); return await Read(response, 4 * 1024 * 1024, ct); }
    public async Task<ForgeApiCapabilities> ProbeAsync(string baseUrl, CancellationToken cancellationToken = default)
    {
        var uri = Base(baseUrl); using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken); timeout.CancelAfter(TimeSpan.FromSeconds(10));
        using var schema = await Get(uri, "openapi.json", timeout.Token);
        var paths = schema.RootElement.GetProperty("paths");
        var operation = paths.GetProperty("/sdapi/v1/txt2img").GetProperty("post");
        var body = operation.GetProperty("requestBody").GetProperty("content").GetProperty("application/json").GetProperty("schema");
        var reference = body.GetProperty("$ref").GetString()!;
        var props = schema.RootElement.GetProperty("components").GetProperty("schemas").GetProperty(reference.Split('/')[^1]).GetProperty("properties");
        foreach (var field in new[] { "prompt", "negative_prompt", "seed", "steps", "sampler_name", "scheduler", "cfg_scale", "width", "height", "batch_size", "n_iter", "override_settings", "override_settings_restore_afterwards", "send_images", "save_images" })
            if (!props.TryGetProperty(field, out _)) throw new InvalidDataException("Forge API未対応field: " + field);
        using var models = await Get(uri, "sdapi/v1/sd-models", timeout.Token);
        using var samplers = await Get(uri, "sdapi/v1/samplers", timeout.Token);
        using var schedulers = await Get(uri, "sdapi/v1/schedulers", timeout.Token);
        return new(models.RootElement.EnumerateArray().Select(m => new ForgeApiModel(m.GetProperty("title").GetString()!, m.GetProperty("model_name").GetString()!, m.TryGetProperty("hash", out var h) ? h.GetString() : null)).ToArray(),
            samplers.RootElement.EnumerateArray().Select(m => m.GetProperty("name").GetString()!).ToArray(),
            schedulers.RootElement.EnumerateArray().Select(m => m.GetProperty("label").GetString()!).ToArray());
    }
    private static ForgeApiModel? Validate(ForgeApiRequest request, ForgeApiCapabilities caps)
    {
        var r = request.Recipe;
        if (Encoding.UTF8.GetByteCount(request.Positive) + Encoding.UTF8.GetByteCount(request.Negative) > ForgeBridgeProtocol.MaxPayloadBytes) throw new ArgumentException("Promptが大きすぎます。");
        if (r.Seed is < 0 || r.Steps is < 1 or > 150 || r.Cfg is < 0 or > 30 || r.Width is < 64 or > 2048 || r.Height is < 64 or > 2048 || r.Width % 8 != 0 && r.Width.HasValue || r.Height % 8 != 0 && r.Height.HasValue) throw new ArgumentException("Recipe数値を確認してください（fixed Seed>=0 / Steps 1..150 / CFG 0..30 / Size 64..2048, 8の倍数）。");
        if (r.Sampler is not null && !caps.Samplers.Contains(r.Sampler, StringComparer.Ordinal)) throw new ArgumentException("未対応Sampler: " + r.Sampler);
        if (r.Scheduler is not null && !caps.Schedulers.Contains(r.Scheduler, StringComparer.Ordinal)) throw new ArgumentException("未対応Scheduler: " + r.Scheduler);
        if (r.Model is null) return null;
        var matches = caps.Models.Where(m => m.Title == r.Model || m.Name == r.Model || m.Title.Split(" [")[0] == r.Model).ToArray();
        if (matches.Length != 1) throw new ArgumentException("未対応または曖昧なModel: " + r.Model);
        return matches[0];
    }
    public async Task<ForgeApiResult> GenerateAsync(string baseUrl, ForgeApiRequest request, string outputDirectory, CancellationToken cancellationToken = default)
    {
        if (!await generation.WaitAsync(0, cancellationToken)) return new(false, "Recipe生成が進行中です。重複要求は送信していません。");
        string? saved = null; var posted = false;
        try
        {
            using var timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken); timeout.CancelAfter(TimeSpan.FromMinutes(10));
            var uri = Base(baseUrl); var caps = await ProbeAsync(baseUrl, cancellationToken); var model = Validate(request, caps); var r = request.Recipe;
            using var before = await Get(uri, "sdapi/v1/options", timeout.Token);
            var checkpoint = before.RootElement.GetProperty("sd_model_checkpoint").GetString();
            var payload = new Dictionary<string, object?> { ["prompt"] = request.Positive, ["negative_prompt"] = request.Negative, ["batch_size"] = 1, ["n_iter"] = 1, ["send_images"] = true, ["save_images"] = false, ["override_settings_restore_afterwards"] = true };
            void Add(string name, object? value) { if (value is not null) payload[name] = value; }
            Add("seed", r.Seed); Add("steps", r.Steps); Add("sampler_name", r.Sampler); Add("scheduler", r.Scheduler); Add("cfg_scale", r.Cfg); Add("width", r.Width); Add("height", r.Height);
            if (model is not null) payload["override_settings"] = new Dictionary<string, object> { ["sd_model_checkpoint"] = model.Title };
            using var content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json");
            posted = true;
            using var message = new HttpRequestMessage(HttpMethod.Post, new Uri(uri, "sdapi/v1/txt2img")) { Content = content };
            using var response = await http.SendAsync(message, HttpCompletionOption.ResponseHeadersRead, timeout.Token);
            using var result = await Read(response, 64 * 1024 * 1024, timeout.Token);
            var images = result.RootElement.GetProperty("images");
            if (images.GetArrayLength() != 1) throw new InvalidDataException("1要求1画像を確認できません。再送信しないでForgeを確認してください。");
            var bytes = Convert.FromBase64String(images[0].GetString()!);
            if (bytes.Length < 24 || !bytes.AsSpan(0, 8).SequenceEqual(new byte[] { 137, 80, 78, 71, 13, 10, 26, 10 })) throw new InvalidDataException("ForgeがPNGを返しませんでした。");
            Directory.CreateDirectory(outputDirectory); saved = Path.Combine(outputDirectory, "forge-" + Guid.NewGuid().ToString("N") + ".png");
            await using (var file = new FileStream(saved, FileMode.CreateNew, FileAccess.Write)) await file.WriteAsync(bytes, cancellationToken);
            var metadata = ForgePngGenerationMetadata.Read(saved);
            var mismatches = Compare(request, model, metadata).ToList();
            if (metadata.Width != BinaryPrimitives.ReadInt32BigEndian(bytes.AsSpan(16, 4)) || metadata.Height != BinaryPrimitives.ReadInt32BigEndian(bytes.AsSpan(20, 4))) mismatches.Add("PNG dimensions");
            using var after = await Get(uri, "sdapi/v1/options", timeout.Token);
            if (checkpoint != after.RootElement.GetProperty("sd_model_checkpoint").GetString()) mismatches.Add("Model restore");
            if (mismatches.Count > 0) return new(false, "Recipe照合失敗: " + string.Join(", ", mismatches) + "。出力を保持しました。再送信せず確認してください。", saved, metadata);
            return new(true, "RecipeをAPIで生成し、指定fieldを実画像metadataで照合しました。", saved, metadata);
        }
        catch (Exception e) when (e is HttpRequestException or JsonException or InvalidDataException or GenerationMetadataException or ArgumentException or IOException or UnauthorizedAccessException or OperationCanceledException or InvalidOperationException or KeyNotFoundException or FormatException)
        { return new(false, "Recipe API: " + e.Message + (posted ? " 生成結果が不明な場合はForgeを確認してください。自動再試行はしません。" : " 生成要求は送信していません。"), saved); }
        finally { generation.Release(); }
    }
    public static IReadOnlyList<string> Compare(ForgeApiRequest request, ForgeApiModel? model, GenerationMetadataSnapshot actual)
    {
        var errors = new List<string>(); var a = GenerationRecipe.FromMetadata(actual); var r = request.Recipe;
        static string Normalize(string s) => s.Replace("\r\n", "\n").Replace('\r', '\n').Trim();
        if (Normalize(request.Positive) != actual.Positive) errors.Add("Positive"); if (Normalize(request.Negative) != actual.Negative) errors.Add("Negative");
        void Field<T>(string name, T? expected, T? received) where T : struct { if (expected.HasValue && !EqualityComparer<T?>.Default.Equals(expected, received)) errors.Add(name); }
        Field("Seed", r.Seed, a.Seed); Field("Steps", r.Steps, a.Steps); Field("CFG", r.Cfg, a.Cfg); Field("Width", r.Width, a.Width); Field("Height", r.Height, a.Height);
        if (r.Sampler is not null && r.Sampler != a.Sampler) errors.Add("Sampler");
        if (r.Scheduler is not null && r.Scheduler != a.Scheduler) errors.Add("Scheduler");
        if (model is not null)
        {
            var hashMatches = !string.IsNullOrEmpty(model.Hash) && actual.Value("Model hash") == model.Hash;
            // Neo may prefix API model_name with the containing folder, while PNG
            // infotext uses the checkpoint basename. Accept only that exact title
            // basename, authenticated by the API-declared hash; never strip an
            // arbitrary prefix from received metadata or accept a hashless alias.
            var checkpoint = model.Title.Split(" [")[0].Replace('\\', '/').Split('/')[^1];
            var titleBasename = Path.GetFileNameWithoutExtension(checkpoint);
            var nameMatches = a.Model == model.Name || hashMatches && a.Model == titleBasename;
            if (!nameMatches || model.Hash is not null && !hashMatches) errors.Add("Model/hash");
        }
        return errors;
    }
}
