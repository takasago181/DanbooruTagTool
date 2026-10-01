using System.Globalization;
using DanbooruTagTool.Core;
using Microsoft.Data.Sqlite;

namespace DanbooruTagTool.Data;

/// <summary>User-owned image index. Never opens catalog.db or user.db.</summary>
public sealed class GenerationLibraryStore
{
    public const int SchemaVersion = 1;
    public string DatabasePath { get; }
    private readonly string connectionString;
    public GenerationLibraryStore(string path)
    {
        if (!Path.GetFileName(path).Equals("generation-library.db", StringComparison.OrdinalIgnoreCase))
            throw new ArgumentException("Library output must be named generation-library.db.");
        DatabasePath = Path.GetFullPath(path);
        Directory.CreateDirectory(Path.GetDirectoryName(DatabasePath)!);
        connectionString = new SqliteConnectionStringBuilder { DataSource = DatabasePath, Pooling = false }.ToString();
        using var c = Open();
        var version = Convert.ToInt32(Scalar(c, "PRAGMA user_version"));
        if (version > SchemaVersion) throw new InvalidDataException($"Library schema {version} requires a newer DTT. Keep {DatabasePath}; do not delete it.");
        if (version == SchemaVersion) return;
        // A consistent SQLite backup includes committed WAL data, unlike a raw file copy.
        if (new FileInfo(DatabasePath).Length > 0)
        {
            using var backup = new SqliteConnection(new SqliteConnectionStringBuilder { DataSource = DatabasePath + ".before-migration-" + Guid.NewGuid().ToString("N") + ".bak", Pooling = false }.ToString());
            backup.Open(); c.BackupDatabase(backup);
        }
        using var tx = c.BeginTransaction();
        try
        {
            Execute(c, Schema, tx); tx.Commit();
        }
        catch (Exception e) when (e is SqliteException or IOException)
        {
            throw new InvalidDataException($"Library migration failed. Original DB retained at {DatabasePath}. Restore a backup or use a matching runtime: {e.Message}", e);
        }
    }
    internal SqliteConnection Open()
    {
        var c = new SqliteConnection(connectionString); c.Open();
        Execute(c, "PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000;"); return c;
    }
    internal static SqliteCommand Command(SqliteConnection c, string sql, SqliteTransaction? tx = null, params (string, object?)[] values)
    {
        var cmd = c.CreateCommand(); cmd.CommandText = sql; cmd.Transaction = tx;
        foreach (var (key, value) in values) cmd.Parameters.AddWithValue(key, value ?? DBNull.Value);
        return cmd;
    }
    internal static int Execute(SqliteConnection c, string sql, SqliteTransaction? tx = null, params (string, object?)[] values)
    { using var cmd = Command(c, sql, tx, values); return cmd.ExecuteNonQuery(); }
    internal static object? Scalar(SqliteConnection c, string sql, SqliteTransaction? tx = null, params (string, object?)[] values)
    { using var cmd = Command(c, sql, tx, values); return cmd.ExecuteScalar(); }
    public LibraryRoot AddRoot(string path, bool recursive = true)
    {
        path = Path.TrimEndingDirectorySeparator(Path.GetFullPath(path));
        using var c = Open();
        Execute(c, "INSERT INTO library_root(path,enabled,recursive,created_utc) VALUES($p,1,$r,$t) ON CONFLICT(path) DO UPDATE SET enabled=1,recursive=excluded.recursive", null,
            ("$p", path), ("$r", recursive), ("$t", DateTime.UtcNow.ToString("O")));
        return Roots().Single(r => r.Path.Equals(path, StringComparison.OrdinalIgnoreCase));
    }
    public IReadOnlyList<LibraryRoot> Roots()
    {
        using var c = Open(); using var cmd = Command(c, "SELECT id,path,enabled,recursive FROM library_root ORDER BY path");
        using var r = cmd.ExecuteReader(); var roots = new List<LibraryRoot>();
        while (r.Read()) roots.Add(new(r.GetInt64(0), r.GetString(1), r.GetBoolean(2), r.GetBoolean(3))); return roots;
    }
    public void SetRootEnabled(long id, bool enabled)
    { using var c = Open(); Execute(c, "UPDATE library_root SET enabled=$e WHERE id=$id", null, ("$e", enabled), ("$id", id)); }
    public void SaveAnnotation(long imageId, ImageAnnotation annotation)
    {
        if (annotation.Rating is < 0 or > 5) throw new ArgumentOutOfRangeException(nameof(annotation));
        using var c = Open();
        Execute(c, "INSERT INTO image_annotation(image_id,favorite,rating,note,updated_utc) VALUES($id,$f,$r,$n,$t) ON CONFLICT(image_id) DO UPDATE SET favorite=excluded.favorite,rating=excluded.rating,note=excluded.note,updated_utc=excluded.updated_utc", null,
            ("$id", imageId), ("$f", annotation.Favorite), ("$r", annotation.Rating), ("$n", annotation.Note), ("$t", DateTime.UtcNow.ToString("O")));
    }
    public GenerationMetadataSnapshot? Metadata(long id)
    {
        using var c = Open();
        using var cmd = Command(c, "SELECT a.normalized_path,m.raw_infotext,m.positive,m.negative FROM generation_metadata m JOIN image_asset a ON a.id=m.image_id WHERE image_id=$id", null, ("$id", id));
        using var r = cmd.ExecuteReader(); if (!r.Read()) return null;
        var path = r.GetString(0); var raw = r.GetString(1); var positive = r.GetString(2); var negative = r.GetString(3); r.Close();
        using var pc = Command(c, "SELECT name,value FROM generation_parameter WHERE image_id=$id ORDER BY ordinal", null, ("$id", id));
        using var pr = pc.ExecuteReader(); var parameters = new List<GenerationParameter>();
        while (pr.Read()) parameters.Add(new(pr.GetString(0), pr.GetString(1)));
        return new(path, raw, positive, negative, parameters);
    }
    public LibraryPage Query(LibraryQuery query)
    {
        using var c = Open(); var where = new List<string>(); var values = new List<(string, object?)>();
        void Filter(string sql, string key, object? value) { if (value is null) return; where.Add(sql); values.Add((key, value)); }
        void Contains(string column, string key, string text)
        { if (text.Length > 0) Filter(column + " LIKE " + key + " ESCAPE '\\'", key, "%" + Escape(text) + "%"); }
        Contains("m.positive", "$pos", query.Positive); Contains("m.negative", "$neg", query.Negative);
        Contains("m.model", "$model", query.Model); Contains("m.sampler", "$sampler", query.Sampler);
        Contains("m.scheduler", "$scheduler", query.Scheduler); Contains("n.note", "$note", query.Note);
        if (query.Text.Length > 0) Filter("(m.positive LIKE $q ESCAPE '\\' OR m.negative LIKE $q ESCAPE '\\' OR m.model LIKE $q ESCAPE '\\' OR n.note LIKE $q ESCAPE '\\' OR a.relative_path LIKE $q ESCAPE '\\' OR EXISTS(SELECT 1 FROM generation_lora l WHERE l.image_id=a.id AND l.name LIKE $q ESCAPE '\\'))", "$q", "%" + Escape(query.Text) + "%");
        if (query.Lora.Length > 0) Filter("EXISTS(SELECT 1 FROM generation_lora l WHERE l.image_id=a.id AND l.name LIKE $lora ESCAPE '\\')", "$lora", "%" + Escape(query.Lora) + "%");
        Filter("a.root_id=$root", "$root", query.RootId); Filter("m.seed=$seed", "$seed", query.Seed);
        Filter("m.cfg >= $cfgMin", "$cfgMin", query.CfgMin is { } min ? (double)min : null);
        Filter("m.cfg <= $cfgMax", "$cfgMax", query.CfgMax is { } max ? (double)max : null);
        Filter("COALESCE(m.width,a.width)=$width", "$width", query.Width); Filter("COALESCE(m.height,a.height)=$height", "$height", query.Height);
        Filter("n.rating >= $rating", "$rating", query.RatingMin);
        if (query.FavoriteOnly) where.Add("n.favorite=1");
        if (query.HasMetadata is { } has) where.Add(has ? "a.metadata_status='OK'" : "a.metadata_status<>'OK'");
        var from = " FROM image_asset a LEFT JOIN generation_metadata m ON m.image_id=a.id LEFT JOIN image_annotation n ON n.image_id=a.id";
        var condition = where.Count == 0 ? "" : " WHERE " + string.Join(" AND ", where);
        var total = Convert.ToInt64(Scalar(c, "SELECT COUNT(*)" + from + condition, null, values.ToArray()));
        var order = query.Sort switch
        {
            LibrarySort.Oldest => "a.mtime_utc_ticks ASC,a.id ASC", LibrarySort.Filename => "a.relative_path COLLATE NOCASE,a.id",
            LibrarySort.Favorite => "COALESCE(n.favorite,0) DESC,a.mtime_utc_ticks DESC,a.id DESC",
            LibrarySort.Rating => "COALESCE(n.rating,-1) DESC,a.mtime_utc_ticks DESC,a.id DESC", _ => "a.mtime_utc_ticks DESC,a.id DESC"
        };
        values.Add(("$limit", Math.Clamp(query.Limit, 1, 200))); values.Add(("$offset", Math.Max(0, query.Offset)));
        using var cmd = Command(c, "SELECT a.id,a.root_id,a.relative_path,a.normalized_path,a.extension,a.file_size,a.mtime_utc_ticks,a.width,a.height,a.availability,a.metadata_status,a.metadata_format,COALESCE(n.favorite,0),n.rating,COALESCE(n.note,'')" + from + condition + " ORDER BY " + order + " LIMIT $limit OFFSET $offset", null, values.ToArray());
        using var r = cmd.ExecuteReader(); var images = new List<LibraryImage>();
        while (r.Read()) images.Add(new(r.GetInt64(0), r.GetInt64(1), r.GetString(2), r.GetString(3), r.GetString(4), r.GetInt64(5), r.GetInt64(6),
            r.IsDBNull(7) ? null : r.GetInt32(7), r.IsDBNull(8) ? null : r.GetInt32(8), r.GetString(9), r.GetString(10),
            r.IsDBNull(11) ? null : r.GetString(11), new(r.GetBoolean(12), r.IsDBNull(13) ? null : r.GetInt32(13), r.GetString(14))));
        return new(images, total);
    }
    private static string Escape(string s) => s.Replace("\\", "\\\\").Replace("%", "\\%").Replace("_", "\\_");
    public void Backup(string destination)
    {
        if (File.Exists(destination)) throw new IOException("Choose a new backup filename; existing files are preserved.");
        if (!Path.GetExtension(destination).Equals(".db", StringComparison.OrdinalIgnoreCase)) throw new ArgumentException("Backup filename must end in .db");
        using var c = Open(); using var b = new SqliteConnection(new SqliteConnectionStringBuilder { DataSource = destination, Pooling = false }.ToString()); b.Open(); c.BackupDatabase(b);
    }
    public bool SupportsFts5()
    {
        using var c = Open();
        try { Execute(c, "CREATE VIRTUAL TABLE temp.library_fts_probe USING fts5(text); DROP TABLE temp.library_fts_probe;"); return true; }
        catch (SqliteException) { return false; }
    }
    internal static void SaveMetadata(SqliteConnection c, SqliteTransaction tx, long id, MetadataReadResult result)
    {
        Execute(c, "DELETE FROM generation_metadata WHERE image_id=$id; DELETE FROM generation_parameter WHERE image_id=$id; DELETE FROM generation_lora WHERE image_id=$id;", tx, ("$id", id));
        if (result.Metadata is not { } m) return;
        var recipe = GenerationRecipe.FromMetadata(m);
        Execute(c, "INSERT INTO generation_metadata VALUES($id,$p,$n,$model,$hash,$seed,$steps,$sampler,$scheduler,$cfg,$width,$height,$raw,1)", tx,
            ("$id", id), ("$p", m.Positive), ("$n", m.Negative), ("$model", recipe.Model), ("$hash", m.Value("Model hash")), ("$seed", recipe.Seed),
            ("$steps", recipe.Steps), ("$sampler", recipe.Sampler), ("$scheduler", recipe.Scheduler), ("$cfg", recipe.Cfg is { } cfg ? (double)cfg : null),
            ("$width", recipe.Width), ("$height", recipe.Height), ("$raw", m.RawInfotext));
        for (var i = 0; i < m.Parameters.Count; i++)
            Execute(c, "INSERT INTO generation_parameter VALUES($id,$o,$n,$v)", tx, ("$id", id), ("$o", i), ("$n", m.Parameters[i].Name), ("$v", m.Parameters[i].Value));
        var loras = GenerationLibraryMetadata.Loras(m);
        for (var i = 0; i < loras.Count; i++)
            Execute(c, "INSERT INTO generation_lora VALUES($id,$o,$n,$w,$raw)", tx, ("$id", id), ("$o", i), ("$n", loras[i].Name), ("$w", (double)loras[i].Weight), ("$raw", loras[i].RawToken));
    }
    private const string Schema = """
        CREATE TABLE library_root(id INTEGER PRIMARY KEY,path TEXT COLLATE NOCASE UNIQUE NOT NULL,enabled INTEGER NOT NULL,recursive INTEGER NOT NULL,created_utc TEXT NOT NULL,last_scan_utc TEXT,last_complete_scan_token TEXT);
        CREATE TABLE image_asset(id INTEGER PRIMARY KEY,root_id INTEGER NOT NULL REFERENCES library_root(id),relative_path TEXT COLLATE NOCASE NOT NULL,normalized_path TEXT NOT NULL,extension TEXT NOT NULL,file_size INTEGER NOT NULL,mtime_utc_ticks INTEGER NOT NULL,width INTEGER,height INTEGER,media_type TEXT NOT NULL DEFAULT 'image',availability TEXT NOT NULL,metadata_status TEXT NOT NULL,metadata_format TEXT,first_seen_utc TEXT NOT NULL,last_seen_utc TEXT NOT NULL,content_hash TEXT,scan_token TEXT,UNIQUE(root_id,relative_path));
        CREATE INDEX image_path ON image_asset(normalized_path);
        CREATE INDEX image_available ON image_asset(availability);
        CREATE INDEX image_date ON image_asset(mtime_utc_ticks DESC,id DESC);
        CREATE INDEX image_name ON image_asset(relative_path COLLATE NOCASE,id);
        CREATE INDEX image_stat ON image_asset(root_id,file_size,mtime_utc_ticks);
        CREATE TABLE generation_metadata(image_id INTEGER PRIMARY KEY REFERENCES image_asset(id),positive TEXT NOT NULL,negative TEXT NOT NULL,model TEXT,model_hash TEXT,seed INTEGER,steps INTEGER,sampler TEXT,scheduler TEXT,cfg REAL,width INTEGER,height INTEGER,raw_infotext TEXT NOT NULL,parser_version INTEGER NOT NULL);
        CREATE INDEX metadata_seed ON generation_metadata(seed);
        CREATE INDEX metadata_model ON generation_metadata(model);
        CREATE INDEX metadata_cfg ON generation_metadata(cfg);
        CREATE TABLE generation_parameter(image_id INTEGER NOT NULL REFERENCES image_asset(id),ordinal INTEGER NOT NULL,name TEXT NOT NULL,value TEXT NOT NULL,PRIMARY KEY(image_id,ordinal));
        CREATE TABLE generation_lora(image_id INTEGER NOT NULL REFERENCES image_asset(id),ordinal INTEGER NOT NULL,name TEXT NOT NULL,weight REAL,raw_token TEXT NOT NULL,PRIMARY KEY(image_id,ordinal));
        CREATE INDEX lora_name ON generation_lora(name,image_id);
        CREATE TABLE image_annotation(image_id INTEGER PRIMARY KEY REFERENCES image_asset(id),favorite INTEGER NOT NULL DEFAULT 0,rating INTEGER CHECK(rating BETWEEN 0 AND 5),note TEXT NOT NULL DEFAULT '',updated_utc TEXT NOT NULL);
        CREATE INDEX annotation_favorite ON image_annotation(favorite,image_id);
        CREATE INDEX annotation_rating ON image_annotation(rating,image_id);
        PRAGMA user_version=1;
        """;
}
