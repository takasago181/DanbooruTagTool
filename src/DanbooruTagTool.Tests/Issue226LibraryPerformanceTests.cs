using System.Diagnostics;
using System.IO;
using System.Text.Json;
using DanbooruTagTool.Core;
using Microsoft.Data.Sqlite;
using DanbooruTagTool.Data;
using Xunit;
using Xunit.Abstractions;

namespace DanbooruTagTool.Tests;

public class Issue226LibraryPerformanceTests(ITestOutputHelper output)
{
    [Fact]
    public void FiveThousandImagesAndTwentyThousandRowsExerciseIncrementalAndSqlPages()
    {
        using var d = new LibraryFixture(); var store = d.Store(); var root = store.AddRoot(d.Images);
        var template = Path.Combine(d.Images, "0.png"); Issue226LibraryFoundationTests.WritePng(template);
        var bytes = File.ReadAllBytes(template);
        for (var i = 1; i < 5000; i++) File.WriteAllBytes(Path.Combine(d.Images, $"{i}.png"), bytes);
        var scanner = new GenerationLibraryScanner(store, new PngGenerationMetadataReader());
        var timer = Stopwatch.StartNew(); var cold = scanner.Scan(root); var coldMs = timer.Elapsed.TotalMilliseconds; Assert.Equal(5000, cold.Added); Assert.Equal(0, cold.Errors);
        timer.Restart(); var warm = scanner.Scan(root); var warmMs = timer.Elapsed.TotalMilliseconds; Assert.Equal(5000, warm.Unchanged);
        for (var i = 0; i < 10; i++) File.SetLastWriteTimeUtc(Path.Combine(d.Images, $"{i}.png"), DateTime.UtcNow.AddMinutes(1));
        timer.Restart(); var changed = scanner.Scan(root); var changedMs = timer.Elapsed.TotalMilliseconds; Assert.Equal(10, changed.Refreshed);
        for (var i = 10; i < 20; i++) File.Delete(Path.Combine(d.Images, $"{i}.png"));
        timer.Restart(); var missing = scanner.Scan(root); var missingMs = timer.Elapsed.TotalMilliseconds; Assert.Equal(10, missing.Missing);
        using (var c = new SqliteConnection(new SqliteConnectionStringBuilder { DataSource = store.DatabasePath, Pooling = false }.ToString()))
        {
            c.Open(); using var cmd = c.CreateCommand();
            cmd.CommandText = """
                BEGIN;
                WITH RECURSIVE n(x) AS (SELECT 5001 UNION ALL SELECT x+1 FROM n WHERE x<20000)
                INSERT INTO image_asset(id,root_id,relative_path,normalized_path,extension,file_size,mtime_utc_ticks,availability,metadata_status,first_seen_utc,last_seen_utc)
                SELECT x,1,'synthetic-'||x||'.png','synthetic-'||x||'.png','.png',100,x,'available','OK','2026-10-01','2026-10-01' FROM n;
                INSERT INTO generation_metadata(image_id,positive,negative,model,seed,raw_infotext,parser_version) SELECT id,'1girl, smile','lowres','sample',42,'fixture',1 FROM image_asset WHERE id>5000;
                INSERT INTO image_annotation(image_id,favorite,rating,note,updated_utc) SELECT id,1,5,'performance','2026-10-01' FROM image_asset WHERE id%100=0;
                COMMIT;
                """; cmd.ExecuteNonQuery();
        }
        timer.Restart(); var search = store.Query(new(Text: "1girl", Limit: 60)); var queryMs = timer.Elapsed.TotalMilliseconds; Assert.Equal(20000, search.Total); Assert.Equal(60, search.Images.Count);
        timer.Restart(); var favorites = store.Query(new(FavoriteOnly: true, Limit: 60)); var favoriteMs = timer.Elapsed.TotalMilliseconds; Assert.Equal(200, favorites.Total);
        timer.Restart(); var last = store.Query(new(Offset: 19980, Limit: 60)); var lastPageMs = timer.Elapsed.TotalMilliseconds; Assert.Equal(20, last.Images.Count);
        // #254: observe the existing query shape without changing schema or user DBs.
        using var inspect = new SqliteConnection(new SqliteConnectionStringBuilder { DataSource = store.DatabasePath, Mode = SqliteOpenMode.ReadOnly, Pooling = false }.ToString()); inspect.Open();
        var plans = new Dictionary<string, List<string>>();
        var from = " FROM image_asset a LEFT JOIN generation_metadata m ON m.image_id=a.id LEFT JOIN image_annotation n ON n.image_id=a.id";
        foreach (var (name, condition) in new[] { ("Text", " WHERE (m.positive LIKE '%1girl%' OR m.negative LIKE '%1girl%' OR m.model LIKE '%1girl%' OR n.note LIKE '%1girl%' OR a.relative_path LIKE '%1girl%' OR EXISTS(SELECT 1 FROM generation_lora l WHERE l.image_id=a.id AND l.name LIKE '%1girl%'))"), ("Favorite", " WHERE n.favorite=1"), ("LastPage", "") }) {
            using var plan = inspect.CreateCommand(); plan.CommandText = "EXPLAIN QUERY PLAN SELECT a.id" + from + condition + " ORDER BY a.mtime_utc_ticks DESC,a.id DESC LIMIT 60 OFFSET " + (name == "LastPage" ? "19980" : "0");
            using var rows = plan.ExecuteReader(); var details = new List<string>(); while (rows.Read()) details.Add(rows.GetString(3)); plans[name] = details;
        }
        using var pragma = inspect.CreateCommand(); pragma.CommandText = "PRAGMA page_count"; var pages = Convert.ToInt64(pragma.ExecuteScalar()); pragma.CommandText = "PRAGMA freelist_count"; var freePages = Convert.ToInt64(pragma.ExecuteScalar());
        var result = new { Images = 5000, Rows = 20000, ColdMs = coldMs, WarmMs = warmMs, Changed10Ms = changedMs, Missing10Ms = missingMs, CommonQueryMs = queryMs, FavoriteQueryMs = favoriteMs, LastPageMs = lastPageMs, Fts5Available = store.SupportsFts5(), Runtime = System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription, DbBytes = new FileInfo(store.DatabasePath).Length, Pages = pages, FreePages = freePages, QueryPlans = plans };
        var json = JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true }); output.WriteLine(json);
        if (Environment.GetEnvironmentVariable("DTT_LIBRARY_PERF_OUTPUT") is { Length: > 0 } destination) File.WriteAllText(destination, json);
    }
}
