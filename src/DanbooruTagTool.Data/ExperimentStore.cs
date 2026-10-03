using System.Text.Json;
using DanbooruTagTool.Core;
using Microsoft.Data.Sqlite;

namespace DanbooruTagTool.Data;

/// <summary>Additive user-owned DB. Plans are immutable; each explicit rerun retains separate attempts and evaluations.</summary>
public sealed class ExperimentStore
{
    public const int SchemaVersion = 1;
    private readonly string connection;
    public ExperimentStore(string path)
    {
        if (Path.GetFileName(path) != "experiment-lab.db") throw new ArgumentException("Experiment DB must be experiment-lab.db.");
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path))!);
        connection = new SqliteConnectionStringBuilder { DataSource = path, Pooling = false }.ToString();
        using var c = Open(); var version = Convert.ToInt32(GenerationLibraryStore.Scalar(c, "PRAGMA user_version"));
        if (version > SchemaVersion) throw new InvalidDataException("Newer Experiment schema. Keep DB and use matching DTT.");
        if (version == SchemaVersion) return;
        if (Convert.ToInt32(GenerationLibraryStore.Scalar(c, "SELECT COUNT(*) FROM sqlite_master WHERE type='table'")) != 0)
            throw new InvalidDataException("Unknown Experiment schema; no overwrite/migration performed.");
        using var tx = c.BeginTransaction(); GenerationLibraryStore.Execute(c, """
            CREATE TABLE experiment(id TEXT PRIMARY KEY,name TEXT NOT NULL,plan TEXT NOT NULL,created_utc TEXT NOT NULL);
            CREATE TABLE run(id TEXT PRIMARY KEY,experiment_id TEXT NOT NULL REFERENCES experiment(id),ordinal INTEGER NOT NULL,capabilities TEXT,UNIQUE(experiment_id,ordinal));
            CREATE TABLE attempt(id TEXT PRIMARY KEY,run_id TEXT NOT NULL REFERENCES run(id),trial_id TEXT NOT NULL,status TEXT NOT NULL,
                started_utc TEXT,completed_utc TEXT,receipt TEXT,image_id INTEGER,evaluation TEXT,UNIQUE(run_id,trial_id));
            CREATE TABLE observation(experiment_id TEXT PRIMARY KEY REFERENCES experiment(id),payload TEXT NOT NULL);
            PRAGMA user_version=1;
            """, tx); tx.Commit();
    }
    private SqliteConnection Open()
    { var c = new SqliteConnection(connection); c.Open(); GenerationLibraryStore.Execute(c, "PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000;"); return c; }
    public void Save(ExperimentPlan p)
    {
        ExperimentPlanner.Validate(p); var json = ExperimentPlanner.Json(p);
        if (System.Text.Encoding.UTF8.GetByteCount(json) > 16 * 1024 * 1024) throw new InvalidDataException("Experiment size limit.");
        using var c = Open(); GenerationLibraryStore.Execute(c, "INSERT INTO experiment VALUES($id,$n,$p,$t)", null,
            ("$id", p.Id.ToString()), ("$n", p.Setup.Name), ("$p", json), ("$t", p.CreatedUtc.ToString("O")));
    }
    public IReadOnlyList<(Guid Id, string Name)> List()
    {
        using var c = Open(); using var cmd = GenerationLibraryStore.Command(c, "SELECT id,name FROM experiment ORDER BY created_utc DESC");
        using var r = cmd.ExecuteReader(); var rows = new List<(Guid, string)>(); while (r.Read()) rows.Add((Guid.Parse(r.GetString(0)), r.GetString(1))); return rows;
    }
    public ExperimentPlan Load(Guid id)
    {
        using var c = Open(); var json = GenerationLibraryStore.Scalar(c, "SELECT plan FROM experiment WHERE id=$id", null, ("$id", id.ToString())) as string ?? throw new InvalidDataException("Experiment missing.");
        var p = JsonSerializer.Deserialize<ExperimentPlan>(json) ?? throw new InvalidDataException("Invalid Experiment.");
        if (p.Id != id) throw new InvalidDataException("Experiment id mismatch."); ExperimentPlanner.Validate(p); return p;
    }
    public Guid CreateRun(Guid id)
    {
        var p = Load(id); using var c = Open(); using var tx = c.BeginTransaction(); var run = Guid.NewGuid();
        var n = Convert.ToInt32(GenerationLibraryStore.Scalar(c, "SELECT COALESCE(MAX(ordinal),0)+1 FROM run WHERE experiment_id=$id", tx, ("$id", id.ToString())));
        GenerationLibraryStore.Execute(c, "INSERT INTO run(id,experiment_id,ordinal) VALUES($r,$e,$n)", tx, ("$r", run.ToString()), ("$e", id.ToString()), ("$n", n));
        foreach (var t in p.Trials) GenerationLibraryStore.Execute(c, "INSERT INTO attempt(id,run_id,trial_id,status) VALUES($a,$r,$t,'Pending')", tx,
            ("$a", Guid.NewGuid().ToString()), ("$r", run.ToString()), ("$t", t.Id.ToString()));
        tx.Commit(); return run;
    }
    public void Capabilities(Guid run, string provenance)
    { using var c = Open(); GenerationLibraryStore.Execute(c, "UPDATE run SET capabilities=$p WHERE id=$r AND capabilities IS NULL", null, ("$r", run.ToString()), ("$p", provenance)); }
    public bool Claim(Guid attempt)
    { using var c = Open(); return GenerationLibraryStore.Execute(c, "UPDATE attempt SET status='Running',started_utc=$s WHERE id=$a AND status='Pending'", null, ("$a", attempt.ToString()), ("$s", DateTime.UtcNow.ToString("O"))) == 1; }
    public void MarkUnknown(Guid attempt)
    { using var c = Open(); GenerationLibraryStore.Execute(c, "UPDATE attempt SET status='Unknown',completed_utc=$t WHERE id=$a AND status='Running'", null, ("$a", attempt.ToString()), ("$t", DateTime.UtcNow.ToString("O"))); }
    public void SaveObservation(Guid id, ExperimentObservation value)
    {
        if (value.Direction.Length > 4000 || value.Exceptions.Length > 4000) throw new ArgumentException("観察・例外は各4000文字まで。");
        using var c = Open(); GenerationLibraryStore.Execute(c, "INSERT INTO observation VALUES($id,$p) ON CONFLICT(experiment_id) DO UPDATE SET payload=excluded.payload", null, ("$id", id.ToString()), ("$p", ExperimentPlanner.Json(value)));
    }
    public ExperimentObservation Observation(Guid id)
    { using var c = Open(); var json = GenerationLibraryStore.Scalar(c, "SELECT payload FROM observation WHERE experiment_id=$id", null, ("$id", id.ToString())) as string; return json is null ? new() : JsonSerializer.Deserialize<ExperimentObservation>(json)!; }
    public string Evidence(Guid id)
    {
        var plan = Load(id); using var c = Open(); using var cmd = GenerationLibraryStore.Command(c, "SELECT ordinal,capabilities FROM run WHERE experiment_id=$id ORDER BY ordinal", null, ("$id", id.ToString()));
        using var r = cmd.ExecuteReader(); var capabilities = new List<object>(); while (r.Read()) capabilities.Add(new { Run = r.GetInt32(0), Provenance = r.IsDBNull(1) ? null : r.GetString(1) });
        return ExperimentPlanner.Json(new { Plan = plan, Attempts = Attempts(id), Observation = Observation(id), RendererCapabilities = capabilities, AutoPromoteToKnowledge = false });
    }
    public void Complete(Guid attempt, ForgeApiResult receipt, long? imageId)
    {
        using var c = Open(); var n = GenerationLibraryStore.Execute(c, "UPDATE attempt SET status=$s,completed_utc=$t,receipt=$r,image_id=$i WHERE id=$a AND status='Running'", null,
            ("$a", attempt.ToString()), ("$s", receipt.Success && imageId is not null && receipt.Metadata is not null ? "Succeeded" : "Failed"),
            ("$t", DateTime.UtcNow.ToString("O")), ("$r", ExperimentPlanner.Json(receipt)), ("$i", imageId));
        if (n != 1) throw new InvalidDataException("Attempt not running; no result overwrite.");
    }
    public IReadOnlyList<ExperimentAttempt> Attempts(Guid experiment)
    {
        using var c = Open(); using var cmd = GenerationLibraryStore.Command(c, """
            SELECT a.id,a.run_id,a.trial_id,r.ordinal,a.status,a.started_utc,a.completed_utc,a.receipt,a.image_id,a.evaluation
            FROM attempt a JOIN run r ON a.run_id=r.id WHERE r.experiment_id=$e ORDER BY r.ordinal,a.rowid
            """, null, ("$e", experiment.ToString()));
        using var r = cmd.ExecuteReader(); var rows = new List<ExperimentAttempt>();
        DateTime? Time(int i) => r.IsDBNull(i) ? null : DateTime.Parse(r.GetString(i), null, System.Globalization.DateTimeStyles.RoundtripKind);
        while (r.Read()) rows.Add(new(Guid.Parse(r.GetString(0)), Guid.Parse(r.GetString(1)), Guid.Parse(r.GetString(2)), r.GetInt32(3), r.GetString(4), Time(5), Time(6),
            r.IsDBNull(7) ? null : JsonSerializer.Deserialize<ForgeApiResult>(r.GetString(7)), r.IsDBNull(8) ? null : r.GetInt64(8),
            r.IsDBNull(9) ? new() : JsonSerializer.Deserialize<TrialEvaluation>(r.GetString(9))));
        return rows;
    }
    public void Evaluate(Guid experiment, Guid attemptId, TrialEvaluation evaluation)
    {
        if (evaluation.Rating is < 0 or > 5 || evaluation.Note.Length > 4000) throw new ArgumentException("rating0〜5 /note4000文字まで。");
        var p = Load(experiment); var attempts = Attempts(experiment); var selected = attempts.Single(a => a.Id == attemptId);
        if (evaluation.Winner && selected.Status != "Succeeded") throw new ArgumentException("成功画像のみwinnerに指定できます。");
        var t = p.Trials.Single(t => t.Id == selected.TrialId); using var c = Open(); using var tx = c.BeginTransaction();
        // One human-selected winner per run/seed/repetition group; never infer image quality.
        if (evaluation.Winner)
            foreach (var a in attempts.Where(a => a.RunId == selected.RunId && a.Id != selected.Id && a.Evaluation?.Winner == true))
            {
                var other = p.Trials.Single(t => t.Id == a.TrialId);
                if (other.Seed == t.Seed && other.Repetition == t.Repetition)
                    GenerationLibraryStore.Execute(c, "UPDATE attempt SET evaluation=$v WHERE id=$a", tx, ("$a", a.Id.ToString()), ("$v", ExperimentPlanner.Json(a.Evaluation! with { Winner = false })));
            }
        GenerationLibraryStore.Execute(c, "UPDATE attempt SET evaluation=$v WHERE id=$a", tx, ("$a", attemptId.ToString()), ("$v", ExperimentPlanner.Json(evaluation))); tx.Commit();
    }
}
