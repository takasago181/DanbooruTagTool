using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace DanbooruTagTool.Core;

public sealed record ForgeApiLora(string Name, string Alias, string Path, string? EmbeddedHash);
internal sealed class ForgeLoraSelection : IDisposable
{
    private readonly List<FileStream> locks = [];
    public List<GenerationLoraIdentity> Identities { get; } = [];
    public static IReadOnlyList<GenerationLora> Tokens(ForgeApiRequest request)
    {
        // Neo activates extra networks only from Positive. Unsupported dialects
        // must not be silently indexed as the simple numeric form.
        if (Regex.IsMatch(request.Negative, @"<(?:lora|lyco):", RegexOptions.IgnoreCase)) throw new InvalidDataException("Negative側LoRAはこのAPI経路のprovenance対象外です。");
        var tokens = GenerationLibraryMetadata.Loras(request.Positive);
        if (Regex.Matches(request.Positive, @"<lora:", RegexOptions.IgnoreCase).Count != tokens.Count || Regex.IsMatch(request.Positive, @"<lyco:", RegexOptions.IgnoreCase)) throw new InvalidDataException("LoRAは単純な<lora:name:weight>形式で指定してください。");
        if (tokens.Count > GenerationLoraProvenance.MaxLoras || tokens.Select(t => t.Name).Distinct(StringComparer.Ordinal).Count() != tokens.Count) throw new InvalidDataException("LoRAの重複/件数を確認してください。");
        if (tokens.Any(t => !GenerationLoraProvenance.Name(t.Name) || t.Weight is < -2 or > 2 || !t.RawToken.StartsWith("<lora:", StringComparison.Ordinal))) throw new InvalidDataException("LoRA名/weightを確認してください（-2..2）。");
        return tokens;
    }
    public static async Task<ForgeLoraSelection> ResolveAsync(IReadOnlyList<GenerationLora> tokens, IReadOnlyList<GenerationLoraIdentity> expected, IReadOnlyList<ForgeApiLora> inventory, CancellationToken ct)
    {
        var selection = new ForgeLoraSelection();
        try
        {
            if (expected.Any(e => !tokens.Any(t => t.Name == e.Name))) throw new InvalidDataException("元LoRA identityが現在Promptにありません。Createで元LoRA制約を明示解除して派生生成してください。");
            foreach (var token in tokens)
            {
                // Reject collisions even if a hash could select a candidate: Forge
                // resolves the unchanged token by its own name/alias table.
                var matches = inventory.Where(l => l.Name == token.Name || l.Alias == token.Name).ToArray();
                if (matches.Length != 1) throw new InvalidDataException("missing / ambiguous Forge LoRA: " + token.Name);
                var lora = matches[0];
                if (!System.IO.Path.IsPathFullyQualified(lora.Path) || lora.Path.StartsWith(@"\\", StringComparison.Ordinal) || !System.IO.Path.GetExtension(lora.Path).Equals(".safetensors", StringComparison.OrdinalIgnoreCase) || (File.GetAttributes(lora.Path) & FileAttributes.ReparsePoint) != 0) throw new InvalidDataException("LoRA実体は非linkローカルsafetensorsが必要です。");
                var stream = new FileStream(lora.Path, FileMode.Open, FileAccess.Read, FileShare.Read, 1024 * 1024, FileOptions.Asynchronous | FileOptions.SequentialScan);
                selection.locks.Add(stream); var size = stream.Length; var mtime = File.GetLastWriteTimeUtc(lora.Path);
                var sha = Convert.ToHexString(await SHA256.HashDataAsync(stream, ct)).ToLowerInvariant();
                stream.Position = 0; var header = new byte[8]; await stream.ReadExactlyAsync(header, ct); var length = BinaryPrimitives.ReadUInt64LittleEndian(header);
                if (length is < 2 or > LoraLocalMetadata.MaxMetadataBytes || length > (ulong)Math.Max(0, size - 8)) throw new InvalidDataException("LoRA safetensors header不正。");
                var bytes = new byte[(int)length]; await stream.ReadExactlyAsync(bytes, ct); using var json = JsonDocument.Parse(bytes);
                var embedded = json.RootElement.TryGetProperty("__metadata__", out var metadata) && metadata.TryGetProperty("sshs_model_hash", out var h) ? h.GetString() : null;
                if (!string.Equals(lora.EmbeddedHash, embedded, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Forge LoRA metadataがlocal実体と違います。既存Forge inventoryをrefreshして確認してください。");
                var backend = sha;
                if (!string.IsNullOrEmpty(embedded))
                {
                    // Forge prefers Kohya's embedded tensor hash. Authenticate it
                    // independently rather than confuse it with full-file SHA256.
                    var tensorSha = Convert.ToHexString(await SHA256.HashDataAsync(stream, ct));
                    if (!GenerationLoraProvenance.Hex(embedded, 64) || !embedded.Equals(tensorSha, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("LoRA embedded tensor hashが実体と一致しません。");
                    backend = embedded.ToLowerInvariant();
                }
                if (stream.Length != size || File.GetLastWriteTimeUtc(lora.Path) != mtime) throw new IOException("LoRA changed while hashing。");
                var identity = new GenerationLoraIdentity(token.Name, backend[..12], sha, token.Weight);
                var pin = expected.SingleOrDefault(e => e.Name == token.Name);
                if (pin is not null && (!pin.BackendHash.Equals(identity.BackendHash, StringComparison.OrdinalIgnoreCase) || pin.FileSha256 is not null && !pin.FileSha256.Equals(sha, StringComparison.OrdinalIgnoreCase))) throw new InvalidDataException("changed / hash mismatch LoRA: " + token.Name);
                selection.Identities.Add(identity);
            }
            return selection;
        }
        catch { selection.Dispose(); throw; }
    }
    public IReadOnlyList<string> Compare(GenerationMetadataSnapshot actual)
    {
        var errors = new List<string>();
        var fields = actual.Parameters.Where(p => p.Name.Equals(GenerationLoraProvenance.HashesKey, StringComparison.OrdinalIgnoreCase)).ToArray();
        try
        {
            var received = GenerationLoraProvenance.Expected(fields);
            if (received.Count != Identities.Count || Identities.Any(i => !received.Any(a => a.Name == i.Name && a.BackendHash.Equals(i.BackendHash, StringComparison.OrdinalIgnoreCase)))) errors.Add("LoRA hash/identity");
        }
        catch (InvalidDataException) { errors.Add("LoRA hash/identity"); }
        return errors;
    }
    public void Dispose() { foreach (var stream in locks) stream.Dispose(); }
}
