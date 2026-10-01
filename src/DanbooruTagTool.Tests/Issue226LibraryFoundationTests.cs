using System.IO;
using System.Buffers.Binary;
using System.Text;
using System.Security.Cryptography;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Microsoft.Data.Sqlite;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue226LibraryFoundationTests
{
    public const string Info = "1girl, <lora:detail:0.75>\nNegative prompt: lowres\nSteps: 20, Sampler: Euler a, Schedule type: Karras, CFG scale: 5, Seed: 42, Size: 32x24, Model: sample, Model hash: abc, Custom: alpha";
    [Fact]
    public void CreateSchemaRootsAndIncrementalReconciliationPreserveAnnotation()
    {
        using var d = new LibraryFixture(); var store = d.Store(); var root = store.AddRoot(d.Images);
        var path = Path.Combine(d.Images, "sub", "a.png"); Directory.CreateDirectory(Path.GetDirectoryName(path)!); WritePng(path);
        File.WriteAllText(Path.Combine(d.Images, "corrupt.png"), "broken");
        var scanner = new GenerationLibraryScanner(store, new PngGenerationMetadataReader());
        var first = scanner.Scan(root); Assert.True(first.Complete); Assert.Equal(2, first.Added); Assert.Equal(1, first.Errors);
        var row = store.Query(new(Positive: "1girl")).Images.Single(); Assert.Equal("OK", row.MetadataStatus);
        Assert.Equal(32, row.Width); Assert.Equal(24, row.Height); Assert.Equal("alpha", store.Metadata(row.Id)!.Value("Custom"));
        store.SaveAnnotation(row.Id, new(true, 5, "keep 日本語"));
        Assert.Equal(2, scanner.Scan(root).Unchanged);
        WritePng(path, Info.Replace("alpha", "changed")); File.SetLastWriteTimeUtc(path, DateTime.UtcNow.AddSeconds(5));
        Assert.Equal(1, scanner.Scan(root).Refreshed);
        var updated = store.Query(new(FavoriteOnly: true)).Images.Single(); Assert.Equal(row.Id, updated.Id); Assert.Equal("keep 日本語", updated.Annotation.Note);
        File.Delete(path); Assert.Equal(1, scanner.Scan(root).Missing);
        Assert.Equal("missing", store.Query(new(FavoriteOnly: true)).Images.Single().Availability);
        Assert.Equal(5, store.Query(new(FavoriteOnly: true)).Images.Single().Annotation.Rating);
        WritePng(path); Assert.True(scanner.Scan(root).Complete); Assert.Equal("available", store.Query(new(FavoriteOnly: true)).Images.Single().Availability);
        using var c = new SqliteConnection("Data Source=" + store.DatabasePath); c.Open(); using var cmd = c.CreateCommand(); cmd.CommandText = "PRAGMA user_version"; Assert.Equal(1L, cmd.ExecuteScalar());
    }
    [Fact]
    public void MissingRootOrCancelledScanNeverMarksPreviouslySeenFilesMissing()
    {
        using var d = new LibraryFixture(); var store = d.Store(); var root = store.AddRoot(d.Images); WritePng(Path.Combine(d.Images, "a.png"));
        var scan = new GenerationLibraryScanner(store, new PngGenerationMetadataReader()); scan.Scan(root);
        using var cancel = new CancellationTokenSource(); cancel.Cancel(); Assert.Throws<OperationCanceledException>(() => scan.Scan(root, cancel.Token));
        Directory.Move(d.Images, d.Images + "-offline"); Assert.False(scan.Scan(root).Complete);
        Assert.Equal("available", store.Query(new()).Images.Single().Availability);
    }
    [Fact]
    public void NewerSchemaAndFailedMigrationKeepOriginalDatabase()
    {
        using var d = new LibraryFixture(); var store = d.Store();
        using (var c = new SqliteConnection("Data Source=" + store.DatabasePath)) { c.Open(); using var cmd = c.CreateCommand(); cmd.CommandText = "PRAGMA user_version=99"; cmd.ExecuteNonQuery(); }
        SqliteConnection.ClearAllPools();
        var before = SHA256.HashData(File.ReadAllBytes(store.DatabasePath));
        Assert.Throws<InvalidDataException>(() => d.Store()); Assert.Equal(before, SHA256.HashData(File.ReadAllBytes(store.DatabasePath)));
        using (var c = new SqliteConnection("Data Source=" + store.DatabasePath)) { c.Open(); using var cmd = c.CreateCommand(); cmd.CommandText = "PRAGMA user_version=0"; cmd.ExecuteNonQuery(); }
        SqliteConnection.ClearAllPools();
        before = SHA256.HashData(File.ReadAllBytes(store.DatabasePath));
        Assert.Throws<InvalidDataException>(() => d.Store()); Assert.Equal(before, SHA256.HashData(File.ReadAllBytes(store.DatabasePath)));
        Assert.NotEmpty(Directory.GetFiles(d.Path, "*.bak"));
    }
    [Fact]
    public void LibraryOperationsDoNotTouchUserOrCatalogAndBackupRetainsNotes()
    {
        using var d = new LibraryFixture(); var user = System.IO.Path.Combine(d.Path, "user.db"); var catalog = System.IO.Path.Combine(d.Path, "catalog.db");
        File.WriteAllText(user, "protected user"); File.WriteAllText(catalog, "protected catalog");
        var u = SHA256.HashData(File.ReadAllBytes(user)); var ca = SHA256.HashData(File.ReadAllBytes(catalog));
        var store = d.Store(); var root = store.AddRoot(d.Images); WritePng(System.IO.Path.Combine(d.Images, "a.png"));
        new GenerationLibraryScanner(store, new PngGenerationMetadataReader()).Scan(root); var row = store.Query(new()).Images.Single(); store.SaveAnnotation(row.Id, new(true, 3, "backup"));
        store.Backup(System.IO.Path.Combine(d.Path, "backup.db")); Assert.Equal(u, SHA256.HashData(File.ReadAllBytes(user))); Assert.Equal(ca, SHA256.HashData(File.ReadAllBytes(catalog)));
        Assert.Throws<ArgumentException>(() => new GenerationLibraryStore(user)); Assert.Throws<ArgumentException>(() => new GenerationLibraryStore(catalog));
        using var c = new SqliteConnection("Data Source=" + System.IO.Path.Combine(d.Path, "backup.db")); c.Open(); using var cmd = c.CreateCommand(); cmd.CommandText = "SELECT note FROM image_annotation"; Assert.Equal("backup", cmd.ExecuteScalar());
    }
    [Fact]
    public void SqlFilteringAndPagingSupportFieldsAndLiteralLikeCharacters()
    {
        using var d = new LibraryFixture(); var store = d.Store(); var root = store.AddRoot(d.Images);
        WritePng(Path.Combine(d.Images, "a.png")); WritePng(Path.Combine(d.Images, "b.png"), Info.Replace("1girl", "1boy"));
        new GenerationLibraryScanner(store, new PngGenerationMetadataReader()).Scan(root);
        var row = store.Query(new(Positive: "1girl")).Images.Single(); store.SaveAnnotation(row.Id, new(true, 4, "100% 日本語"));
        Assert.Single(store.Query(new(Seed: 42, Sampler: "Euler", Scheduler: "Karras", CfgMin: 4, CfgMax: 6, Width: 32, Height: 24, Lora: "detail", FavoriteOnly: true, RatingMin: 4, Note: "%", RootId: root.Id, HasMetadata: true)).Images);
        Assert.Equal(2, store.Query(new(Limit: 1)).Total); Assert.Single(store.Query(new(Limit: 1, Offset: 1)).Images); Assert.Empty(store.Query(new(Limit: 1, Offset: 2)).Images);
        Assert.Empty(store.Query(new(HasMetadata: false)).Images); Assert.True(store.SupportsFts5());
    }
    [Theory]
    [InlineData(".jpg")]
    [InlineData(".webp")]
    public void ExifUserCommentUsesExistingInfotextParser(string extension)
    {
        using var d = new LibraryFixture(); var path = Path.Combine(d.Images, "image" + extension); WriteExif(path, Info + " 日本語");
        var result = new ExifGenerationMetadataReader().Read(path); Assert.Equal("OK", result.Status); Assert.Equal("42", result.Metadata!.Value("Seed")); Assert.Contains("日本語", result.Metadata.RawInfotext);
        File.WriteAllBytes(path, [1, 2, 3]); Assert.NotEqual("OK", new ExifGenerationMetadataReader().Read(path).Status);
    }
    [Fact]
    public void MetadataDiffPreservesUnknownDuplicatesAndLoraUncertainty()
    {
        var a = ForgePngGenerationMetadata.Parse("a", Info); var b = ForgePngGenerationMetadata.Parse("b", Info.Replace("Seed: 42", "Seed: 43") + ", Extra: two");
        var diff = GenerationMetadataDiff.Compare(a, b); Assert.Contains(diff, x => x.Field == "Positive" && x.State == "same"); Assert.Contains(diff, x => x.Field == "Seed" && x.State == "changed"); Assert.Contains(diff, x => x.Field == "Extra" && x.State == "only right");
        Assert.Single(GenerationLibraryMetadata.Loras(a));
        Assert.Empty(GenerationLibraryMetadata.Loras(ForgePngGenerationMetadata.Parse("x", "<lora:foo:LBW=1>")));
    }
    internal static void WritePng(string path, string? info = Info)
    {
        // Real, tiny PNG fixture with valid pixel payload; standard tEXt metadata.
        var encoder = new System.Windows.Media.Imaging.PngBitmapEncoder();
        encoder.Frames.Add(System.Windows.Media.Imaging.BitmapFrame.Create(System.Windows.Media.Imaging.BitmapSource.Create(32, 24, 96, 96, System.Windows.Media.PixelFormats.Rgb24, null, new byte[32 * 24 * 3], 32 * 3)));
        using var buffer = new MemoryStream(); encoder.Save(buffer); var png = buffer.ToArray();
        using var s = File.Create(path); s.Write(png.AsSpan(0, png.Length - 12));
        if (info is not null)
        {
            var data = Encoding.Latin1.GetBytes("parameters\0" + info); Span<byte> h = stackalloc byte[8]; BinaryPrimitives.WriteInt32BigEndian(h, data.Length); "tEXt"u8.CopyTo(h[4..]); s.Write(h); s.Write(data); s.Write(new byte[4]);
        }
        s.Write(png.AsSpan(png.Length - 12));
    }
    internal static void WriteExif(string path, string info)
    {
        var comment = new byte[] { 85, 78, 73, 67, 79, 68, 69, 0 }.Concat(Encoding.BigEndianUnicode.GetBytes(info)).ToArray();
        var tiff = new byte[44 + comment.Length]; "MM"u8.CopyTo(tiff); BinaryPrimitives.WriteUInt16BigEndian(tiff.AsSpan(2), 42); BinaryPrimitives.WriteUInt32BigEndian(tiff.AsSpan(4), 8);
        BinaryPrimitives.WriteUInt16BigEndian(tiff.AsSpan(8), 1); BinaryPrimitives.WriteUInt16BigEndian(tiff.AsSpan(10), 0x8769); BinaryPrimitives.WriteUInt16BigEndian(tiff.AsSpan(12), 4); BinaryPrimitives.WriteUInt32BigEndian(tiff.AsSpan(14), 1); BinaryPrimitives.WriteUInt32BigEndian(tiff.AsSpan(18), 26);
        BinaryPrimitives.WriteUInt16BigEndian(tiff.AsSpan(26), 1); BinaryPrimitives.WriteUInt16BigEndian(tiff.AsSpan(28), 0x9286); BinaryPrimitives.WriteUInt16BigEndian(tiff.AsSpan(30), 7); BinaryPrimitives.WriteUInt32BigEndian(tiff.AsSpan(32), (uint)comment.Length); BinaryPrimitives.WriteUInt32BigEndian(tiff.AsSpan(36), 44); comment.CopyTo(tiff, 44);
        using var s = File.Create(path);
        if (Path.GetExtension(path) == ".jpg")
        {
            var encoder = new System.Windows.Media.Imaging.JpegBitmapEncoder(); encoder.Frames.Add(System.Windows.Media.Imaging.BitmapFrame.Create(System.Windows.Media.Imaging.BitmapSource.Create(2, 2, 96, 96, System.Windows.Media.PixelFormats.Rgb24, null, new byte[12], 6)));
            using var jpeg = new MemoryStream(); encoder.Save(jpeg); var bytes = jpeg.ToArray();
            s.Write(bytes.AsSpan(0, 2)); s.Write(new byte[] { 255, 225 }); Span<byte> length = stackalloc byte[2]; BinaryPrimitives.WriteUInt16BigEndian(length, (ushort)(tiff.Length + 8)); s.Write(length); s.Write("Exif\0\0"u8); s.Write(tiff); s.Write(bytes.AsSpan(2));
        }
        else
        {
            // 2x2 lossless WebP generated by Pillow 2026-10-01; no external fixture code.
            var webp = Convert.FromBase64String("UklGRhwAAABXRUJQVlA4TA8AAAAvAUAAAAcQ0f/+ByKi/wEA");
            Span<byte> size = stackalloc byte[4]; s.Write("RIFF"u8); BinaryPrimitives.WriteUInt32LittleEndian(size, (uint)(webp.Length - 8 + 8 + tiff.Length + (tiff.Length & 1))); s.Write(size); s.Write(webp.AsSpan(8));
            s.Write("EXIF"u8); BinaryPrimitives.WriteUInt32LittleEndian(size, (uint)tiff.Length); s.Write(size); s.Write(tiff); if ((tiff.Length & 1) != 0) s.WriteByte(0);
        }
    }
}
public sealed class LibraryFixture : IDisposable
{
    public string Path { get; } = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "dtt-library-" + Guid.NewGuid().ToString("N"));
    public string Images => System.IO.Path.Combine(Path, "images");
    public LibraryFixture() => Directory.CreateDirectory(Images);
    public GenerationLibraryStore Store() => new(System.IO.Path.Combine(Path, "generation-library.db"));
    public void Dispose() { SqliteConnection.ClearAllPools(); Directory.Delete(Path, true); }
}
