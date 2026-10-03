using System.Security.Cryptography;
using System.Text.Json;
namespace DanbooruTagTool.Data;

public sealed record TemplateDocument(int Version = 1, string Source = "{red|blue|black} hair", int Cap = 64, string ExternalRoot = "");
public sealed record WildcardSnapshot(IReadOnlyDictionary<string,string[]> Values, IReadOnlyDictionary<string,string> Hashes);
public sealed class TemplateStore(string root)
{
    private string DirectoryPath => Path.Combine(root, "UserData", "Templates");
    private string FilePath => Path.Combine(DirectoryPath, "workspace.json");
    public TemplateDocument Load()
    {
        if (!File.Exists(FilePath)) return new();
        var document = JsonSerializer.Deserialize<TemplateDocument>(File.ReadAllText(FilePath)) ?? throw new InvalidDataException("空template設定。");
        if (document.Version != 1) throw new InvalidDataException("未対応template設定version。上書きしません。");
        return document;
    }
    public void Save(TemplateDocument document)
    {
        if (document.Version != 1 || document.Source.Length > 16000 || document.Cap is < 1 or > 256) throw new ArgumentException("template設定の上限を確認してください。");
        _ = Load(); Directory.CreateDirectory(DirectoryPath); var temp = FilePath + "." + Guid.NewGuid() + ".tmp";
        try { File.WriteAllText(temp, JsonSerializer.Serialize(document)); if (File.Exists(FilePath)) File.Replace(temp, FilePath, FilePath + ".bak"); else File.Move(temp, FilePath); }
        finally { if (File.Exists(temp)) File.Delete(temp); }
    }
    public WildcardSnapshot ReadWildcards(string externalRoot)
    {
        var values = new Dictionary<string,string[]>(StringComparer.Ordinal); var hashes = new Dictionary<string,string>();
        var local = Path.Combine(DirectoryPath, "Wildcards");
        foreach (var directory in new[] {local, externalRoot}.Where(d => !string.IsNullOrWhiteSpace(d)))
        {
            if (!Directory.Exists(directory)) { if (directory != local) throw new DirectoryNotFoundException(directory); continue; }
            // Deliberately flat, no globbing/path traversal/reparse recursion. External root is explicit.
            foreach (var path in Directory.EnumerateFiles(directory, "*.txt", SearchOption.TopDirectoryOnly).Take(257))
            {
                if (values.Count >= 256 || new FileInfo(path).Length > 256000) throw new ArgumentException("wildcardファイル数/サイズ上限超過。");
                var bytes = File.ReadAllBytes(path); var lines = System.Text.Encoding.UTF8.GetString(bytes).TrimStart('\uFEFF').Replace("\r\n", "\n").Split('\n').Where(l => !string.IsNullOrWhiteSpace(l) && !l.TrimStart().StartsWith('#')).ToArray();
                var name = Path.GetFileNameWithoutExtension(path); if (!values.TryAdd(name, lines)) throw new ArgumentException("重複wildcard名: " + name);
                hashes.Add(name, Convert.ToHexString(SHA256.HashData(bytes)));
            }
        }
        return new(values, hashes);
    }
}
