using System.Globalization;
using System.Text.Json;

namespace DanbooruTagTool.Core;

// Backend fingerprints and full-file SHA256 are deliberately distinct identities.
public sealed record GenerationLoraIdentity(string Name, string BackendHash, string? FileSha256 = null, decimal? Weight = null);
public static class GenerationLoraProvenance
{
    public const string ReceiptKey = "DTT LoRA provenance v1";
    public const string HashesKey = "Lora hashes";
    public const int MaxLoras = 32;
    public static bool IsIdentity(string name) => name.Equals(HashesKey, StringComparison.OrdinalIgnoreCase) || name.Equals(ReceiptKey, StringComparison.OrdinalIgnoreCase);
    public static bool IsValid(GenerationParameter p)
    {
        try { _ = Expected([p]); return true; }
        catch (InvalidDataException) { return false; }
    }
    public static IReadOnlyList<GenerationLoraIdentity> Expected(IReadOnlyList<GenerationParameter>? parameters)
    {
        var fields = (parameters ?? []).Where(p => IsIdentity(p.Name)).ToArray();
        if (fields.GroupBy(p => p.Name, StringComparer.OrdinalIgnoreCase).Any(g => g.Count() > 1)) throw new InvalidDataException("重複LoRA identityを確認してください。");
        var hashes = new Dictionary<string, GenerationLoraIdentity>(StringComparer.Ordinal);
        var source = fields.SingleOrDefault(p => p.Name.Equals(HashesKey, StringComparison.OrdinalIgnoreCase));
        if (source is not null)
        {
            foreach (var part in source.Value.Split(','))
            {
                var split = part.Split(':');
                if (split.Length != 2 || !Name(split[0].Trim()) || !Hex(split[1].Trim(), 12)) throw new InvalidDataException("Lora hashesは名前と12桁backend hashが必要です。");
                var identity = new GenerationLoraIdentity(split[0].Trim(), split[1].Trim().ToLowerInvariant());
                if (!hashes.TryAdd(identity.Name, identity)) throw new InvalidDataException("重複LoRA hash名を確認してください。");
            }
        }
        var receipt = fields.SingleOrDefault(p => p.Name.Equals(ReceiptKey, StringComparison.OrdinalIgnoreCase));
        if (receipt is not null)
        {
            if (receipt.Value.Length > 128 * 1024) throw new InvalidDataException("LoRA provenance上限超過。");
            GenerationLoraIdentity[] identities;
            try { identities = JsonSerializer.Deserialize<GenerationLoraIdentity[]>(receipt.Value) ?? throw new InvalidDataException("空LoRA provenance。"); }
            catch (JsonException e) { throw new InvalidDataException("不正LoRA provenance。", e); }
            if (identities.Length is 0 or > MaxLoras || identities.Any(i => i is null) || identities.Select(i => i.Name).Distinct(StringComparer.Ordinal).Count() != identities.Length) throw new InvalidDataException("LoRA provenance件数/重複を確認してください。");
            if (identities.Any(i => !Name(i.Name) || !Hex(i.BackendHash, 12) || !Hex(i.FileSha256, 64) || i.Weight is null or < -2 or > 2)) throw new InvalidDataException("LoRA provenanceのidentity/weightを確認してください。");
            if (source is not null && (identities.Length != hashes.Count || identities.Any(i => !hashes.ContainsKey(i.Name)))) throw new InvalidDataException("PNG LoRA hash名とprovenance名が矛盾しています。");
            foreach (var i in identities)
            {
                if (hashes.TryGetValue(i.Name, out var old) && !old.BackendHash.Equals(i.BackendHash, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("PNG LoRA hashとローカルprovenanceが矛盾しています。");
                hashes[i.Name] = i;
            }
        }
        if (hashes.Count > MaxLoras) throw new InvalidDataException("LoRAは最大32件です。");
        return hashes.Values.ToArray();
    }
    internal static bool Hex(string? s, int length) => s?.Length == length && s.All(Uri.IsHexDigit);
    internal static bool Name(string? s) => !string.IsNullOrWhiteSpace(s) && s.Length <= 256 && s.IndexOfAny(['<', '>', ':', ',', '\r', '\n']) < 0;
    public static string Summary(IReadOnlyList<GenerationParameter>? parameters)
    {
        try
        {
            var identities = Expected(parameters);
            return identities.Count == 0 ? "LoRA identity記録なし（名前だけでは実体を証明できません）。" : string.Join("\n", identities.Select(i => $"LoRA {i.Name} · backend {i.BackendHash}" + (i.FileSha256 is null ? " · file SHA256未記録" : $" · file SHA256 {i.FileSha256}") + (i.Weight.HasValue ? $" · weight {i.Weight.Value.ToString(CultureInfo.InvariantCulture)}（元実行値）" : "")));
        }
        catch (InvalidDataException e) { return e.Message; }
    }
}
