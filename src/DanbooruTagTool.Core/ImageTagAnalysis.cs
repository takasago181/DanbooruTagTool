using System.Net.Http;
using System.Net.Http.Json;
using System.Security.Cryptography;
using System.Text.Json;
namespace DanbooruTagTool.Core;
public sealed record TaggerProfile(string ApiModel, string ModelName, string ModelSource, string Revision, string ModelPath, string ModelSha256, string TagsPath, string TagsSha256, string ManifestPath, string Implementation, string ImplementationCommit, string License, int Version = 1);
public sealed record PredictedTag(string Tag, double Confidence);
public sealed record TagAnalysis(int Version, long LibraryImageId, string ImagePath, string ImageSha256, DateTime AnalyzedUtc, string ServiceUrl, TaggerProfile Model, IReadOnlyList<PredictedTag> Tags);
public sealed record TagComparison(string Tag, double? Confidence, string Observation);
public static class ImageTagDiagnostics
{
    private static string Normalize(string s) => s.Trim().Replace(' ', '_');
    public static IReadOnlyList<TagComparison> Compare(TagAnalysis analysis, PromptWorkspace prompt, double threshold, string filter = "")
    {
        if (!double.IsFinite(threshold) || threshold is < 0 or > 1) throw new ArgumentException("thresholdは0〜1です。");
        var current = prompt.Items.Where(i => i.Kind is PromptItemKind.Normal or PromptItemKind.Raw or PromptItemKind.Weighted)
            .Select(i => Normalize(i.Canonical ?? i.StructuredName ?? i.Surface)).ToHashSet(StringComparer.OrdinalIgnoreCase);
        var predicted = analysis.Tags.Where(t => t.Confidence >= threshold).ToArray(); var names = predicted.Select(t => Normalize(t.Tag)).ToHashSet(StringComparer.OrdinalIgnoreCase);
        return predicted.Select(t => new TagComparison(t.Tag,t.Confidence,current.Contains(Normalize(t.Tag)) ? "Promptに存在" : "観察のみ / 追加候補"))
            .Concat(current.Where(t => !names.Contains(t)).Select(t => new TagComparison(t,null,"Promptのみ / 閾値以上の観察なし（誤りとは限りません）")))
            .Where(t => t.Tag.Contains(filter,StringComparison.OrdinalIgnoreCase)).OrderByDescending(t => t.Confidence ?? -1).ThenBy(t => t.Tag,StringComparer.Ordinal).ToArray();
    }
}
public sealed class LocalTaggerClient(HttpClient? client = null)
{
    private readonly HttpClient http = client ?? new(new HttpClientHandler { AllowAutoRedirect = false }) { Timeout = TimeSpan.FromMinutes(3) };
    public static async Task<string> HashAsync(string path,CancellationToken ct = default)
    { await using var stream = File.OpenRead(path); return Convert.ToHexString(await SHA256.HashDataAsync(stream,ct)); }
    public async Task<TagAnalysis> AnalyzeAsync(string serviceUrl, long imageId, string path, TaggerProfile profile, CancellationToken ct = default)
    {
        if (!Uri.TryCreate(serviceUrl,UriKind.Absolute,out var url) || !url.IsLoopback || url.Scheme != "http" || url.UserInfo.Length > 0 || url.AbsolutePath != "/" || url.Query.Length > 0 || url.Fragment.Length > 0)
            throw new ArgumentException("解析先はloopback HTTP rootのみです。");
        if (new FileInfo(path).Length > 32*1024*1024) throw new ArgumentException("画像は32MB以内です。");
        await VerifyAsync(profile,ct);
        var bytes = await File.ReadAllBytesAsync(path,ct); var imageHash = Convert.ToHexString(SHA256.HashData(bytes));
        using var response = await http.PostAsJsonAsync(new Uri(url,"tagger/v1/interrogate"), new { image = Convert.ToBase64String(bytes), model = profile.ApiModel, threshold = 0, queue = "", name_in_queue = "" }, ct);
        response.EnsureSuccessStatusCode(); using var json = JsonDocument.Parse(await response.Content.ReadAsStringAsync(ct));
        var tags = json.RootElement.GetProperty("caption").GetProperty("tag").EnumerateObject().Select(p => new PredictedTag(p.Name,p.Value.GetDouble())).ToArray();
        if (tags.Length > 100000 || tags.Any(t => string.IsNullOrWhiteSpace(t.Tag) || t.Tag.Length > 200 || !double.IsFinite(t.Confidence) || t.Confidence is < 0 or > 1)) throw new InvalidDataException("不正tagger応答。");
        await VerifyAsync(profile,ct);
        if (imageHash != await HashAsync(path,ct)) throw new IOException("解析中に元画像が変更されました。");
        return new(1,imageId,path,imageHash,DateTime.UtcNow,serviceUrl,profile,tags.OrderByDescending(t => t.Confidence).ThenBy(t => t.Tag,StringComparer.Ordinal).ToArray());
    }
    private static async Task VerifyAsync(TaggerProfile profile,CancellationToken ct)
    {
        if (profile.Version != 1 || profile.Revision.Length == 0 || profile.ImplementationCommit.Length != 40 || profile.License.Length == 0 ||
            !string.Equals(profile.ModelSha256,await HashAsync(profile.ModelPath,ct),StringComparison.OrdinalIgnoreCase) ||
            !string.Equals(profile.TagsSha256,await HashAsync(profile.TagsPath,ct),StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("model/labels provenanceが変わりました。明示Setupをやり直してください。");
        using var manifest = JsonDocument.Parse(await File.ReadAllTextAsync(profile.ManifestPath,ct));
        if (!manifest.RootElement.EnumerateArray().Any(e => e.GetProperty("name").GetString() == profile.ModelName &&
            e.GetProperty("model_path").GetString() == profile.ModelPath && e.GetProperty("tags_path").GetString() == profile.TagsPath)) throw new InvalidDataException("tagger model manifestが設定と一致しません。");
    }
}
