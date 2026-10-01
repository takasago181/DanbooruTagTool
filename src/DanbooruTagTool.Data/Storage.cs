using System.Text.Json;
using System.Text.Json.Serialization;
using DanbooruTagTool.Core;
using Microsoft.Data.Sqlite;

namespace DanbooruTagTool.Data;

public sealed record PortablePaths(string Root)
{
    public string Catalog => Path.Combine(Root, "Data", "catalog.db");
    public string User => Path.Combine(Root, "UserData", "user.db");
    public string GenerationLibrary => Path.Combine(Root, "UserData", "generation-library.db");
    public string GenerationThumbnails => Path.Combine(Root, "UserData", "Cache", "GenerationThumbnails");
}
public sealed record UiState(int Workspace = 0, string Browse = "tags", string Query = "",
    string? SelectedEntry = null, double BrowseScroll = 0, double NavWidth = 300, double PromptWidth = 400,
    double EditRatio = 0.75, double Width = 1280, double Height = 820, double Left = 80, double Top = 60,
    bool EnglishChips = false, PromptOutputProfile OutputProfile = PromptOutputProfile.Canonical,
    string ForgeUrl = ForgeBridgeProtocol.DefaultUrl, string ForgeExtensionPath = "",
    string BrowseScope = "", string? BrowsePrimaryRoute = null, string? BrowseLocalSubroute = null,
    string[]? BrowseBodySites = null, string[]? BrowseThemes = null, bool BrowseDeepOnly = false,
    string ContentIntent = "ALL");
public sealed record GenerationPreset(Guid Id, string Name, string Description, string Positive, string Negative, GenerationRecipe? Recipe = null)
{
    [JsonIgnore] public bool HasRecipe => Recipe?.HasAny == true;
    [JsonIgnore] public string RecipeSummary => Recipe?.Summary ?? "";
}
public sealed record UserState(WorkspaceSnapshot Prompt, UiState Ui, GenerationPreset[]? Presets = null, WorkspaceSnapshot? Negative = null);
public interface IUserStateStore { UserState? Load(); void Save(UserState state); }

public sealed class UserStateStore : IUserStateStore
{
    public const int SchemaVersion = 2;
    private readonly string connectionString;
    public UserStateStore(string path)
    {
        if (Path.GetFileName(path).Equals("catalog.db", StringComparison.OrdinalIgnoreCase)) throw new ArgumentException("User state must be separate from catalog.");
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path))!);
        connectionString = new SqliteConnectionStringBuilder { DataSource = path, Pooling = false }.ToString();
        using var c = Open(); using var cmd = c.CreateCommand();
        cmd.CommandText = "PRAGMA user_version"; var schema = Convert.ToInt32(cmd.ExecuteScalar());
        cmd.CommandText = "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='user_state'"; var hasState = Convert.ToInt32(cmd.ExecuteScalar()) != 0;
        var payloadVersion = 0; if (hasState) { cmd.CommandText = "SELECT COALESCE(MAX(version),0) FROM user_state"; payloadVersion = Convert.ToInt32(cmd.ExecuteScalar()); }
        if (schema > SchemaVersion || payloadVersion > SchemaVersion) throw new InvalidDataException("Newer UserData schema/payload. Keep user.db and use a matching DTT.");
        if (schema == SchemaVersion && payloadVersion is 0 or SchemaVersion) return;
        if (new FileInfo(path).Length > 0)
        {
            using var backup = new SqliteConnection(new SqliteConnectionStringBuilder { DataSource = Path.GetFullPath(path) + ".before-migration-" + Guid.NewGuid().ToString("N") + ".bak", Pooling = false }.ToString()); backup.Open(); c.BackupDatabase(backup);
        }
        using var tx = c.BeginTransaction(); cmd.Transaction = tx;
        cmd.CommandText = "CREATE TABLE IF NOT EXISTS user_state(id INTEGER PRIMARY KEY CHECK(id=1), version INTEGER NOT NULL, payload TEXT NOT NULL); UPDATE user_state SET version=2; PRAGMA user_version=2;"; cmd.ExecuteNonQuery(); tx.Commit();
    }
    private SqliteConnection Open() { var c = new SqliteConnection(connectionString); c.Open(); return c; }
    public UserState? Load()
    {
        using var c = Open(); using var cmd = c.CreateCommand(); cmd.CommandText = "SELECT version FROM user_state WHERE id=1";
        if (cmd.ExecuteScalar() is long version && version != SchemaVersion) throw new InvalidDataException("Unsupported UserData payload. No reset performed.");
        cmd.CommandText = "SELECT payload FROM user_state WHERE id=1 AND version=2";
        return cmd.ExecuteScalar() is string json ? JsonSerializer.Deserialize<UserState>(json) : null;
    }
    public void Save(UserState state)
    {
        using var c = Open(); using var tx = c.BeginTransaction(); using var cmd = c.CreateCommand(); cmd.Transaction = tx;
        cmd.CommandText = "SELECT MAX(version) FROM user_state"; if (cmd.ExecuteScalar() is long newer && newer > SchemaVersion) throw new InvalidDataException("Newer UserData payload; save refused.");
        cmd.CommandText = "PRAGMA user_version"; if (Convert.ToInt32(cmd.ExecuteScalar()) != SchemaVersion) throw new InvalidDataException("Unsupported UserData schema; save refused.");
        cmd.CommandText = "INSERT INTO user_state VALUES(1,2,$json) ON CONFLICT(id) DO UPDATE SET version=2,payload=excluded.payload";
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
public sealed class GeneralBrowseProvider : IGeneralBrowseProvider
{
    private readonly IReadOnlyDictionary<string, BrowsePath[]> acceptedMappings;
    private readonly IReadOnlyDictionary<string, IReadOnlyList<CatalogEntry>> byPath;
    private readonly IReadOnlyList<BrowsePath> paths;

    public GeneralBrowseProvider(ICatalog catalog, IReadOnlyDictionary<string, BrowsePath[]> acceptedMappings)
    {
        this.acceptedMappings = acceptedMappings;
        var query = RuntimeCatalogIndex.Create(catalog);
        var rows = query.BrowseCategory("General", canBrowseOnly: false)
            .Where(entry => entry.CanBrowse && entry.Canonical is not null && acceptedMappings.ContainsKey(entry.Canonical))
            .ToArray();
        var indexed = new Dictionary<string, List<CatalogEntry>>(StringComparer.Ordinal) { [""] = [] };
        foreach (var entry in rows)
        {
            indexed[""].Add(entry);
            var seen = new HashSet<string>(StringComparer.Ordinal);
            foreach (var path in acceptedMappings[entry.Canonical!])
            {
                foreach (var key in new[] { path.Key, path.GenreId + ">" })
                {
                    if (!seen.Add(key)) continue;
                    if (!indexed.TryGetValue(key, out var target)) indexed[key] = target = [];
                    target.Add(entry);
                }
            }
        }
        byPath = new System.Collections.ObjectModel.ReadOnlyDictionary<string, IReadOnlyList<CatalogEntry>>(
            indexed.ToDictionary(pair => pair.Key, pair => (IReadOnlyList<CatalogEntry>)Array.AsReadOnly(pair.Value.ToArray()), StringComparer.Ordinal));
        paths = Array.AsReadOnly(acceptedMappings.Values.SelectMany(value => value).Distinct().ToArray());
    }

    public static IGeneralBrowseProvider FromCatalog(ICatalog catalog)
    {
        var query = RuntimeCatalogIndex.Create(catalog);
        var mappings = query.BrowseCategory("General", canBrowseOnly: false)
            .Where(e => e.Canonical != null && e.BrowseClassification == BrowseClassificationStatus.Proposed && e.Paths.Length > 0)
            .ToDictionary(e => e.Canonical!, e => e.Paths, StringComparer.Ordinal);
        return mappings.Count == 0 ? new PendingGeneralBrowseProvider() : new GeneralBrowseProvider(catalog, mappings);
    }

    public bool IsPending => false;
    public string Status => "";
    public IReadOnlyList<BrowsePath> Paths => paths;
    public IReadOnlyList<CatalogEntry> Browse(string path) =>
        byPath.GetValueOrDefault(path) is { } entries
            ? entries.OrderByDescending(entry => entry.Usage).ToArray()
            : [];
}
