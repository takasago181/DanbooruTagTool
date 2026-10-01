using System.Buffers.Binary;
using System.Globalization;
using System.Text.Json;

namespace DanbooruTagTool.Core;

public sealed record LoraTrigger(string Text, string Source, bool Enabled = true);
public sealed record LoraFacts(string BaseModel, string BaseModelSource, LoraTrigger[] Triggers, string? Preview = null, string? SourceUrl = null);
public sealed record LoraRecipe(string Sha256, decimal Weight, string[] Triggers, string Positive = "", string Negative = "", string Note = "");
public sealed record LoraUserMetadata(string Category = "Other", bool Favorite = false, string Note = "", decimal PreferredWeight = 1,
    string[]? Links = null, string? BaseModel = null, LoraTrigger[]? Triggers = null, string? Preview = null, LoraRecipe? Recipe = null);
public sealed record LoraAsset(long Id, string Path, string Sha256, long Size, long MtimeTicks, bool Available, LoraFacts Facts, LoraUserMetadata User, long UsageCount, string? LastUsed, int HashCopies)
{
    public string Name => System.IO.Path.GetFileNameWithoutExtension(Path);
    public string BaseModel => User.BaseModel ?? Facts.BaseModel;
    public string BaseModelSource => User.BaseModel is null ? Facts.BaseModelSource : "user";
    public LoraTrigger[] Triggers => User.Triggers ?? Facts.Triggers;
    public string? Preview => User.Preview ?? Facts.Preview;
    public string Summary => $"{Name} · {User.Category} · {BaseModel} · {(Available ? "available" : "missing")} · {HashCopies} path(s) · used {UsageCount}";
    public string Token(decimal weight)
    {
        if (weight is < -2 or > 2 || Name.IndexOfAny(['<', '>', ':', '\r', '\n']) >= 0) throw new ArgumentException("LoRA名/weightを確認してください（-2..2）。");
        return $"<lora:{Name}:{weight.ToString(CultureInfo.InvariantCulture)}>";
    }
}
public sealed record LoraScanResult(int Added, int Refreshed, int Unchanged, int Hashed, int Missing, bool Complete, string Error = "");

/// <summary>Reads only bounded embedded metadata and adjacent local files. Never opens URLs.</summary>
public static class LoraLocalMetadata
{
    public const int MaxMetadataBytes = 4 * 1024 * 1024;
    public static string[] Sidecars(string path) => [System.IO.Path.ChangeExtension(path, ".civitai.info"), System.IO.Path.ChangeExtension(path, ".metadata.json"), System.IO.Path.ChangeExtension(path, ".json")];
    public static string[] Previews(string path)
    {
        var stem = System.IO.Path.Combine(System.IO.Path.GetDirectoryName(path)!, System.IO.Path.GetFileNameWithoutExtension(path));
        return [stem + ".preview.png", stem + ".preview.jpg", stem + ".preview.webp", stem + ".png", stem + ".jpg", stem + ".webp"];
    }
    public static string Fingerprint(string path) => string.Join('|', Sidecars(path).Concat(Previews(path)).Where(File.Exists).Select(p => { var f = new FileInfo(p); return $"{p}:{f.Length}:{f.LastWriteTimeUtc.Ticks}"; }));
    private static bool SafeLocal(string path) => File.Exists(path) && (File.GetAttributes(path) & FileAttributes.ReparsePoint) == 0;
    public static LoraFacts Read(string path)
    {
        using var file = File.OpenRead(path); Span<byte> header = stackalloc byte[8]; file.ReadExactly(header); var length = BinaryPrimitives.ReadUInt64LittleEndian(header);
        if (length is < 2 or > MaxMetadataBytes || length > (ulong)Math.Max(0, file.Length - 8)) throw new InvalidDataException("safetensors metadata headerが不正/上限超過です。");
        var data = new byte[(int)length]; file.ReadExactly(data); using var document = JsonDocument.Parse(data);
        var baseModel = "unknown"; var source = "unknown"; var triggers = new List<LoraTrigger>(); string? sourceUrl = null;
        if (document.RootElement.TryGetProperty("__metadata__", out var meta))
        {
            foreach (var key in new[] { "modelspec.architecture", "ss_base_model_version", "ss_sd_model_name" })
                if (meta.TryGetProperty(key, out var value) && value.ValueKind == JsonValueKind.String && !string.IsNullOrWhiteSpace(value.GetString())) { baseModel = value.GetString()!; source = "embedded:" + key; break; }
            if (meta.TryGetProperty("modelspec.trigger_phrase", out var trigger) && trigger.ValueKind == JsonValueKind.String)
                triggers.AddRange(trigger.GetString()!.Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries).Select(t => new LoraTrigger(t, "embedded:modelspec.trigger_phrase")));
        }
        foreach (var sidecar in Sidecars(path).Where(SafeLocal))
        {
            if (new FileInfo(sidecar).Length > MaxMetadataBytes) throw new InvalidDataException("LoRA sidecarが上限を超えました。");
            using var json = JsonDocument.Parse(File.ReadAllBytes(sidecar)); var root = json.RootElement;
            if (source == "unknown" && root.TryGetProperty("baseModel", out var b) && b.ValueKind == JsonValueKind.String) { baseModel = b.GetString() ?? "unknown"; source = "sidecar:" + System.IO.Path.GetFileName(sidecar); }
            if (triggers.Count == 0 && root.TryGetProperty("trainedWords", out var words) && words.ValueKind == JsonValueKind.Array)
                triggers.AddRange(words.EnumerateArray().Where(w => w.ValueKind == JsonValueKind.String).Select(w => new LoraTrigger(w.GetString()!, "sidecar:" + System.IO.Path.GetFileName(sidecar))));
            if (sourceUrl is null && root.TryGetProperty("id", out var id) && id.TryGetInt64(out var version)) sourceUrl = "https://civitai.com/models?modelVersionId=" + version.ToString(CultureInfo.InvariantCulture);
        }
        return new(baseModel, source, triggers.ToArray(), Previews(path).FirstOrDefault(SafeLocal), sourceUrl);
    }
}
