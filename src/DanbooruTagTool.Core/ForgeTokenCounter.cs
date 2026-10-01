using System.Net.Http;
using System.Text;
using System.Text.Json;

namespace DanbooruTagTool.Core;

public sealed record ForgeTokenCount(bool Available, string Status, string Model = "", string ModelHash = "", string Engine = "", string Tokenizer = "", int? Count = null, int? Capacity = null, int? ChunkLength = null, int? Chunks = null);
public interface IForgeTokenCounter { Task<ForgeTokenCount> CountAsync(string url, string text, bool negative, int steps, CancellationToken ct = default); }
public sealed class ForgeTokenCounter(HttpClient? client = null) : IForgeTokenCounter
{
    private readonly HttpClient http = client ?? new(new HttpClientHandler { UseProxy = false, AllowAutoRedirect = false });
    public async Task<ForgeTokenCount> CountAsync(string url, string text, bool negative, int steps, CancellationToken ct = default)
    {
        if (!Uri.TryCreate(url, UriKind.Absolute, out var uri) || uri.Scheme != "http" || !uri.IsLoopback || uri.UserInfo.Length > 0 || uri.AbsolutePath != "/" || uri.Query.Length > 0 || uri.Fragment.Length > 0 || text.Length > 128 * 1024 || steps is < 1 or > 150) return new(false, "Loopback URL / Prompt / Stepsを確認してください。");
        using var timeout = CancellationTokenSource.CreateLinkedTokenSource(ct); timeout.CancelAfter(TimeSpan.FromSeconds(10));
        try
        {
            var payload = JsonSerializer.Serialize(new { protocolVersion = 1, text, negative, steps });
            using var request = new HttpRequestMessage(HttpMethod.Post, new Uri(uri, "dtt-bridge/token-count")) { Content = new StringContent(payload, Encoding.UTF8, "application/json") };
            using var response = await http.SendAsync(request, HttpCompletionOption.ResponseHeadersRead, timeout.Token);
            if (!response.IsSuccessStatusCode) return new(false, "Forge token counterを取得できません。対応拡張/読み込み済みモデルを確認してください。推定値は表示しません。");
            if (response.Content.Headers.ContentLength > 512 * 1024) return new(false, "Counter responseが上限超過です。");
            using var stream = await response.Content.ReadAsStreamAsync(timeout.Token); using var buffer = new MemoryStream(); var chunk = new byte[4096];
            while (true) { var read = await stream.ReadAsync(chunk, timeout.Token); if (read == 0) break; if (buffer.Length + read > 512 * 1024) return new(false, "Counter responseが上限超過です。"); buffer.Write(chunk, 0, read); }
            using var json = JsonDocument.Parse(buffer.ToArray()); var root = json.RootElement;
            if (root.GetProperty("protocolVersion").GetInt32() != 1 || root.GetProperty("source").GetString() != "Forge.ui.update_token_counter" || root.GetProperty("text").GetString() != text || root.GetProperty("negative").GetBoolean() != negative || root.GetProperty("steps").GetInt32() != steps) return new(false, "Counter source / request mismatch。値を採用しません。");
            var count = root.GetProperty("count").GetInt32(); var capacity = root.GetProperty("capacity").GetInt32();
            var model = root.GetProperty("model").GetString()!; var engine = root.GetProperty("engine").GetString()!; var tokenizer = root.GetProperty("tokenizer").GetString()!;
            if (string.IsNullOrWhiteSpace(model) || string.IsNullOrWhiteSpace(engine) || engine == "FakeInitialModel" || string.IsNullOrWhiteSpace(tokenizer) || count < 0 || capacity < count || capacity <= 0) return new(false, "Counter model/contractが不正です。");
            int? size = root.GetProperty("chunkLength").ValueKind == JsonValueKind.Null ? null : root.GetProperty("chunkLength").GetInt32();
            int? chunks = root.GetProperty("chunks").ValueKind == JsonValueKind.Null ? null : root.GetProperty("chunks").GetInt32();
            if ((size.HasValue && (size <= 0 || chunks <= 0 || chunks is null || (long)size * chunks != capacity)) || (!size.HasValue && chunks.HasValue)) return new(false, "Chunk contract mismatch。");
            return new(true, "Forge UI counter / stylesなし / schedules最大値 / 指定Stepsで照合", model, root.GetProperty("modelHash").GetString() ?? "", engine, tokenizer, count, capacity, size, chunks);
        }
        catch (Exception e) when (e is HttpRequestException or OperationCanceledException or JsonException or InvalidOperationException or KeyNotFoundException or FormatException or IOException) { return new(false, "Counter unavailable。Promptを保持しています。推定値は表示しません。"); }
    }
}
