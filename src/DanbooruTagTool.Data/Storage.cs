using System.Text.Json;
using DanbooruTagTool.Core;
using Microsoft.Data.Sqlite;

namespace DanbooruTagTool.Data;

public sealed record PortablePaths(string Root)
{
    public string Catalog => Path.Combine(Root, "Data", "catalog.db");
    public string User => Path.Combine(Root, "UserData", "user.db");
}
public sealed record UiState(int Workspace = 0, string Browse = "special", string Query = "",
    string? SelectedEntry = null, double BrowseScroll = 0, double NavWidth = 300, double PromptWidth = 400,
    double EditRatio = 0.75, double Width = 1280, double Height = 820, double Left = 80, double Top = 60,
    bool EnglishChips = false, PromptOutputProfile OutputProfile = PromptOutputProfile.Canonical,
    string ForgeUrl = ForgeBridgeProtocol.DefaultUrl, string ForgeExtensionPath = "");
public sealed record GenerationPreset(Guid Id, string Name, string Description, string Positive, string Negative);
public sealed record UserState(WorkspaceSnapshot Prompt, UiState Ui, GenerationPreset[]? Presets = null);
public interface IUserStateStore { UserState? Load(); void Save(UserState state); }

public sealed class UserStateStore : IUserStateStore
{
    private readonly string connectionString;
    public UserStateStore(string path)
    {
        if (Path.GetFileName(path).Equals("catalog.db", StringComparison.OrdinalIgnoreCase)) throw new ArgumentException("User state must be separate from catalog.");
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path))!);
        connectionString = new SqliteConnectionStringBuilder { DataSource = path, Pooling = false }.ToString();
        using var c = Open(); using var cmd = c.CreateCommand();
        cmd.CommandText = "CREATE TABLE IF NOT EXISTS user_state(id INTEGER PRIMARY KEY CHECK(id=1), version INTEGER NOT NULL, payload TEXT NOT NULL);"; cmd.ExecuteNonQuery();
    }
    private SqliteConnection Open() { var c = new SqliteConnection(connectionString); c.Open(); return c; }
    public UserState? Load()
    {
        using var c = Open(); using var cmd = c.CreateCommand(); cmd.CommandText = "SELECT payload FROM user_state WHERE id=1 AND version=1";
        return cmd.ExecuteScalar() is string json ? JsonSerializer.Deserialize<UserState>(json) : null;
    }
    public void Save(UserState state)
    {
        using var c = Open(); using var tx = c.BeginTransaction(); using var cmd = c.CreateCommand(); cmd.Transaction = tx;
        cmd.CommandText = "INSERT INTO user_state VALUES(1,1,$json) ON CONFLICT(id) DO UPDATE SET version=1,payload=excluded.payload";
        cmd.Parameters.AddWithValue("$json", JsonSerializer.Serialize(state)); cmd.ExecuteNonQuery(); tx.Commit();
    }
}

public static class CatalogDatabase
{
    public static ICatalog Open(string path)
    {
        if (!File.Exists(path)) throw new FileNotFoundException("Data/catalog.db がありません。明示的なcatalog buildが必要です。", path);
        using var c = new SqliteConnection(new SqliteConnectionStringBuilder { DataSource = path, Mode = SqliteOpenMode.ReadOnly, Pooling = false }.ToString()); c.Open();
        using var version = c.CreateCommand(); version.CommandText = "PRAGMA user_version";
        if (Convert.ToInt32(version.ExecuteScalar()) != 1) throw new InvalidDataException("Unsupported catalog schema");
        using var cmd = c.CreateCommand(); cmd.CommandText = "SELECT payload FROM entries ORDER BY ordinal";
        using var reader = cmd.ExecuteReader(); var entries = new List<CatalogEntry>();
        while (reader.Read()) entries.Add(JsonSerializer.Deserialize<CatalogEntry>(reader.GetString(0)) ?? throw new InvalidDataException("Null catalog entry"));
        return new Catalog(entries);
    }
    // Explicit build only. Refuse overwrites, especially user.db and protected source assets.
    public static void Build(string path, IReadOnlyList<CatalogEntry> entries, string provenance)
    {
        if (Path.GetFileName(path) != "catalog.db") throw new ArgumentException("Output must be named catalog.db");
        if (File.Exists(path)) throw new IOException("Catalog already exists; choose a new output directory.");
        if (entries.Select(e => e.Id).Distinct().Count() != entries.Count) throw new InvalidDataException("Duplicate catalog ID");
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path))!);
        using var c = new SqliteConnection(new SqliteConnectionStringBuilder { DataSource = path, Pooling = false }.ToString()); c.Open();
        using var tx = c.BeginTransaction(); using var cmd = c.CreateCommand(); cmd.Transaction = tx;
        cmd.CommandText = "PRAGMA user_version=1; CREATE TABLE entries(id TEXT PRIMARY KEY,canonical TEXT,ordinal INTEGER NOT NULL,payload TEXT NOT NULL); CREATE INDEX canonical_lookup ON entries(canonical); CREATE TABLE metadata(provenance TEXT NOT NULL);"; cmd.ExecuteNonQuery();
        cmd.CommandText = "INSERT INTO metadata VALUES($p)"; cmd.Parameters.AddWithValue("$p", provenance); cmd.ExecuteNonQuery(); cmd.Parameters.Clear();
        cmd.CommandText = "INSERT INTO entries VALUES($id,$canonical,$ordinal,$json)";
        cmd.Parameters.Add("$id", SqliteType.Text); cmd.Parameters.Add("$canonical", SqliteType.Text); cmd.Parameters.Add("$ordinal", SqliteType.Integer); cmd.Parameters.Add("$json", SqliteType.Text);
        for (int i = 0; i < entries.Count; i++)
        {
            var e = entries[i]; cmd.Parameters["$id"].Value = e.Id; cmd.Parameters["$canonical"].Value = (object?)e.Canonical ?? DBNull.Value;
            cmd.Parameters["$ordinal"].Value = i; cmd.Parameters["$json"].Value = JsonSerializer.Serialize(e); cmd.ExecuteNonQuery();
        }
        tx.Commit();
    }
}

// Future accepted #64 sidecar adapter: no production loader is activated in Phase B.
public sealed class GeneralBrowseProvider(ICatalog catalog, IReadOnlyDictionary<string, BrowsePath[]> acceptedMappings) : IGeneralBrowseProvider
{
    public static IGeneralBrowseProvider FromCatalog(ICatalog catalog)
    {
        var mappings = catalog.Entries
            .Where(e => !e.IsSpecial && e.Canonical != null && e.BrowseClassification == BrowseClassificationStatus.Proposed && e.Paths.Length > 0)
            .ToDictionary(e => e.Canonical!, e => e.Paths, StringComparer.Ordinal);
        return mappings.Count == 0 ? new PendingGeneralBrowseProvider() : new GeneralBrowseProvider(catalog, mappings);
    }

    public bool IsPending => false;
    public string Status => "";
    public IReadOnlyList<BrowsePath> Paths => acceptedMappings.Values.SelectMany(p => p).Distinct().ToArray();
    public IReadOnlyList<CatalogEntry> Browse(string path) => catalog.Entries.Where(e => !e.IsSpecial && e.CanBrowse && e.Canonical != null
        && acceptedMappings.TryGetValue(e.Canonical, out var paths) && paths.Any(p => path.Length == 0 || p.Key == path || (path.EndsWith('>') && p.GenreId + ">" == path))).OrderByDescending(e => e.Usage).ToArray();
}
