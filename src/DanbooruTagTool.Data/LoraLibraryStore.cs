using System.Security.Cryptography;
using System.Text.Encodings.Web;
using System.Text.Json;
using DanbooruTagTool.Core;
using Microsoft.Data.Sqlite;

namespace DanbooruTagTool.Data;

/// <summary>SHA-keyed personal identity, separate path inventory. No catalog/user.db access.</summary>
public sealed class LoraLibraryStore
{
    public const int SchemaVersion = 1;
    public string DatabasePath { get; }
    private static readonly JsonSerializerOptions Json = new() { Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping };
    private string Connection => new SqliteConnectionStringBuilder { DataSource = DatabasePath, Pooling = false }.ToString();
    public LoraLibraryStore(string path)
    {
        if (!Path.GetFileName(path).Equals("lora-library.db", StringComparison.OrdinalIgnoreCase)) throw new ArgumentException("LoRA DB must be lora-library.db.");
        DatabasePath = Path.GetFullPath(path); Directory.CreateDirectory(Path.GetDirectoryName(DatabasePath)!); using var c = Open();
        var version = Convert.ToInt32(Scalar(c, "PRAGMA user_version")); if (version > SchemaVersion) throw new InvalidDataException("Newer LoRA schema. Keep the DB and use a matching DTT.");
        if (version == SchemaVersion) return;
        if (new FileInfo(DatabasePath).Length > 0) Backup(DatabasePath + ".before-migration-" + Guid.NewGuid().ToString("N") + ".bak");
        using var tx = c.BeginTransaction();
        Exec(c, "CREATE TABLE lora_root(id INTEGER PRIMARY KEY,path TEXT NOT NULL UNIQUE); CREATE TABLE lora_file(id INTEGER PRIMARY KEY,root INTEGER NOT NULL REFERENCES lora_root(id),path TEXT NOT NULL,sha TEXT NOT NULL,size INTEGER NOT NULL,mtime INTEGER NOT NULL,sidecars TEXT NOT NULL,facts TEXT NOT NULL,available INTEGER NOT NULL,seen TEXT NOT NULL,UNIQUE(root,path,sha)); CREATE INDEX lora_hash ON lora_file(sha); CREATE TABLE lora_user(sha TEXT PRIMARY KEY,metadata TEXT NOT NULL,usage INTEGER NOT NULL DEFAULT 0,last_used TEXT); PRAGMA user_version=1;", tx);
        tx.Commit();
    }
    private SqliteConnection Open() { var c = new SqliteConnection(Connection); c.Open(); Exec(c, "PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000;"); return c; }
    private static SqliteCommand Command(SqliteConnection c, string sql, SqliteTransaction? tx, params (string, object?)[] values)
    { var cmd = c.CreateCommand(); cmd.CommandText = sql; cmd.Transaction = tx; foreach (var (k, v) in values) cmd.Parameters.AddWithValue(k, v ?? DBNull.Value); return cmd; }
    private static object? Scalar(SqliteConnection c, string sql, params (string, object?)[] values) { using var cmd = Command(c, sql, null, values); return cmd.ExecuteScalar(); }
    private static int Exec(SqliteConnection c, string sql, SqliteTransaction? tx = null, params (string, object?)[] values) { using var cmd = Command(c, sql, tx, values); return cmd.ExecuteNonQuery(); }
    public void Backup(string destination)
    {
        if (File.Exists(destination)) throw new IOException("Backup destination must be new.");
        using var c = Open(); using var backup = new SqliteConnection(new SqliteConnectionStringBuilder { DataSource = destination, Pooling = false }.ToString()); backup.Open(); c.BackupDatabase(backup);
    }
    public string[] Roots() { using var c = Open(); using var cmd = Command(c, "SELECT path FROM lora_root ORDER BY path", null); using var r = cmd.ExecuteReader(); var paths = new List<string>(); while (r.Read()) paths.Add(r.GetString(0)); return paths.ToArray(); }
    public void AddRoot(string path)
    {
        path = Path.TrimEndingDirectorySeparator(Path.GetFullPath(path)); if (!Directory.Exists(path) || (File.GetAttributes(path) & FileAttributes.ReparsePoint) != 0) throw new IOException("Select an available non-link local LoRA folder.");
        using var c = Open(); Exec(c, "INSERT OR IGNORE INTO lora_root(path) VALUES($p)", null, ("$p", path));
    }
    public LoraScanResult Scan(string rootPath, CancellationToken ct = default, bool forceHash = false)
    {
        var added = 0; var refreshed = 0; var unchanged = 0; var hashed = 0; using var c = Open();
        var root = Scalar(c, "SELECT id FROM lora_root WHERE path=$p", ("$p", rootPath)) ?? throw new ArgumentException("Register root first.");
        using var tx = c.BeginTransaction(); var token = Guid.NewGuid().ToString("N");
        try
        {
            if ((File.GetAttributes(rootPath) & FileAttributes.ReparsePoint) != 0) throw new IOException("Root became a link.");
            var options = new EnumerationOptions { RecurseSubdirectories = true, IgnoreInaccessible = false, AttributesToSkip = FileAttributes.ReparsePoint };
            foreach (var path in Directory.EnumerateFiles(rootPath, "*", options).Where(p => Path.GetExtension(p).Equals(".safetensors", StringComparison.OrdinalIgnoreCase)))
            {
                ct.ThrowIfCancellationRequested(); var file = new FileInfo(path); var size = file.Length; var mtime = file.LastWriteTimeUtc.Ticks; var relative = Path.GetRelativePath(rootPath, path);
                string? sha = null; var same = false; var sidecars = LoraLocalMetadata.Fingerprint(path); string? facts = null;
                using (var cmd = Command(c, "SELECT sha,size,mtime,sidecars,facts FROM lora_file WHERE root=$r AND path=$p ORDER BY available DESC,mtime DESC LIMIT 1", tx, ("$r", root), ("$p", relative)))
                using (var row = cmd.ExecuteReader()) if (row.Read() && row.GetInt64(1) == size && row.GetInt64(2) == mtime) { sha = row.GetString(0); same = row.GetString(3) == sidecars; if (same) facts = row.GetString(4); }
                if (sha is null || forceHash) { using var stream = File.OpenRead(path); sha = Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant(); hashed++; ct.ThrowIfCancellationRequested(); }
                facts ??= JsonSerializer.Serialize(LoraLocalMetadata.Read(path), Json);
                file.Refresh(); if (file.Length != size || file.LastWriteTimeUtc.Ticks != mtime) throw new IOException("LoRA changed during scan. Retry after writes finish.");
                var exists = false; using (var check = Command(c, "SELECT 1 FROM lora_file WHERE root=$r AND path=$p AND sha=$h", tx, ("$r", root), ("$p", relative), ("$h", sha))) exists = check.ExecuteScalar() is not null;
                Exec(c, "INSERT INTO lora_file(root,path,sha,size,mtime,sidecars,facts,available,seen) VALUES($r,$p,$h,$s,$m,$f,$j,1,$t) ON CONFLICT(root,path,sha) DO UPDATE SET size=$s,mtime=$m,sidecars=$f,facts=$j,available=1,seen=$t", tx, ("$r", root), ("$p", relative), ("$h", sha), ("$s", size), ("$m", mtime), ("$f", sidecars), ("$j", facts), ("$t", token));
                if (!exists) added++; else if (same) unchanged++; else refreshed++;
            }
            var missing = Exec(c, "UPDATE lora_file SET available=0 WHERE root=$r AND seen<>$t AND available=1", tx, ("$r", root), ("$t", token)); tx.Commit(); return new(added, refreshed, unchanged, hashed, missing, true);
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or JsonException or OperationCanceledException or InvalidOperationException)
        { tx.Rollback(); return new(0, 0, 0, hashed, 0, false, e.Message); }
    }
    public LoraAsset[] Query(string search = "", bool favoriteOnly = false, int offset = 0)
    {
        using var c = Open(); using var cmd = Command(c, "SELECT f.id,r.path,f.path,f.sha,f.size,f.mtime,f.available,f.facts,u.metadata,COALESCE(u.usage,0),u.last_used,(SELECT COUNT(*) FROM lora_file copies WHERE copies.sha=f.sha AND copies.available=1) FROM lora_file f JOIN lora_root r ON f.root=r.id LEFT JOIN lora_user u ON f.sha=u.sha WHERE ($fav=0 OR json_extract(u.metadata,'$.Favorite')=1) AND ($q='' OR instr(lower(f.path || ' ' || f.facts || ' ' || COALESCE(u.metadata,'')),lower($q))>0) ORDER BY f.available DESC,f.path,f.id LIMIT 100 OFFSET $o", null, ("$q", search.Trim()), ("$fav", favoriteOnly), ("$o", Math.Max(0, offset)));
        using var row = cmd.ExecuteReader(); var results = new List<LoraAsset>();
        while (row.Read()) results.Add(new(row.GetInt64(0), Path.Combine(row.GetString(1), row.GetString(2)), row.GetString(3), row.GetInt64(4), row.GetInt64(5), row.GetBoolean(6), JsonSerializer.Deserialize<LoraFacts>(row.GetString(7))!, row.IsDBNull(8) ? new() : JsonSerializer.Deserialize<LoraUserMetadata>(row.GetString(8))!, row.GetInt64(9), row.IsDBNull(10) ? null : row.GetString(10), row.GetInt32(11)));
        return results.ToArray();
    }
    public void Save(string sha, LoraUserMetadata value)
    {
        if (sha.Length != 64 || !sha.All(Uri.IsHexDigit) || value.PreferredWeight is < -2 or > 2 || value.Category is not ("Character" or "Style" or "Concept" or "Other")) throw new ArgumentException("LoRA user metadataを確認してください。");
        using var c = Open(); Exec(c, "INSERT INTO lora_user(sha,metadata) VALUES($h,$j) ON CONFLICT(sha) DO UPDATE SET metadata=$j", null, ("$h", sha), ("$j", JsonSerializer.Serialize(value, Json)));
    }
    public bool CanInsert(LoraAsset asset)
    {
        var file = new FileInfo(asset.Path); if (!asset.Available || !file.Exists || (file.Attributes & FileAttributes.ReparsePoint) != 0 || file.Length != asset.Size || file.LastWriteTimeUtc.Ticks != asset.MtimeTicks) return false;
        using var c = Open(); using var cmd = Command(c, "SELECT DISTINCT f.sha,f.path FROM lora_file f WHERE available=1", null); using var r = cmd.ExecuteReader();
        while (r.Read()) if (Path.GetFileNameWithoutExtension(r.GetString(1)).Equals(asset.Name, StringComparison.OrdinalIgnoreCase) && r.GetString(0) != asset.Sha256) return false;
        return true;
    }
    public void RecordUse(string sha)
    {
        using var c = Open(); Exec(c, "INSERT INTO lora_user(sha,metadata,usage,last_used) VALUES($h,$j,1,$t) ON CONFLICT(sha) DO UPDATE SET usage=usage+1,last_used=$t", null, ("$h", sha), ("$j", JsonSerializer.Serialize(new LoraUserMetadata(), Json)), ("$t", DateTime.UtcNow.ToString("O")));
    }
}
