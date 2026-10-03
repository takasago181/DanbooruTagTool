using System.IO;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;
using Xunit;

namespace DanbooruTagTool.Tests;

public class FoundationMetadataBoundaryTests
{
    [Theory]
    [InlineData(".jpg")]
    [InlineData(".webp")]
    public void ImportRetainsRawTextDuplicateUnknownParametersAndRecipeIsOnlyProjection(string extension)
    {
        using var fixture = new LibraryFixture();
        var raw = "日本語, (1girl:1.2), <lora:unknown:LBW=1>\r\nNegative prompt: lowres\r\nSteps: 20, Seed: 42, Size: 32x24, Custom: first, Custom: \"second, 日本語\", Unknown: opaque";
        var path = Path.Combine(fixture.Images, "image" + extension);
        Issue226LibraryFoundationTests.WriteExif(path, raw);
        var sourceHash = System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(path));
        var store = fixture.Store();
        var scan = new GenerationLibraryScanner(store, GenerationMetadataReaders.CreateDefault()).Scan(store.AddRoot(fixture.Images));
        Assert.Equal(0, scan.Errors);
        var imported = store.Metadata(store.Query(new()).Images.Single().Id)!;
        Assert.Equal(raw, imported.RawInfotext);
        Assert.Equal(new[] { "first", "second, 日本語" }, imported.Parameters.Where(p => p.Name == "Custom").Select(p => p.Value));
        Assert.Equal("opaque", imported.Value("Unknown"));
        Assert.Contains("<lora:unknown:LBW=1>", imported.Positive);
        Assert.Equal(42L, GenerationRecipe.FromMetadata(imported).Seed);
        Assert.Equal(raw, imported.RawInfotext);
        Assert.Equal(GenerationInfotextParser.Parse(path, raw).Parameters, imported.Parameters);
        Assert.Equal(sourceHash, System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(path)));
    }

    [Fact]
    public void UnsupportedFileHasNoAdapterAndMalformedSupportedFileRemainsInvalid()
    {
        var readers = GenerationMetadataReaders.CreateDefault();
        Assert.DoesNotContain(readers, reader => reader.CanRead(".json"));
        using var fixture = new LibraryFixture();
        var path = Path.Combine(fixture.Images, "broken.webp");
        File.WriteAllBytes(path, "RIFF\0\0\0\0WEBP"u8.ToArray());
        var result = readers.Single(reader => reader.CanRead(".WEBP")).Read(path);
        Assert.Null(result.Metadata);
        Assert.NotEqual("OK", result.Status);
    }

    [Fact]
    public void WebpEnvelopeLimitAndExifCycleAreStillRejected()
    {
        using var fixture = new LibraryFixture();
        var path = Path.Combine(fixture.Images, "unsafe.webp");
        WriteWebpExif(path, new byte[2 * 1024 * 1024 + 1]);
        var reader = new ExifGenerationMetadataReader();
        var oversized = reader.Read(path);
        Assert.Equal("metadata_invalid", oversized.Status);
        Assert.Contains("2 MiB", oversized.Error!);
        // IFD's EXIF pointer points back to the same IFD.
        byte[] tiff = [73, 73, 42, 0, 8, 0, 0, 0, 1, 0, 105, 135, 4, 0, 1, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0];
        WriteWebpExif(path, tiff);
        var result = reader.Read(path);
        Assert.Equal("metadata_invalid", result.Status);
        Assert.Contains("cycle", result.Error!);
        Assert.Null(result.Metadata);
        Assert.False(result.Retryable);
    }

    [Fact]
    public void PngDecodedTextLimitStillRejectsCompressedExpansion()
    {
        using var fixture = new LibraryFixture();
        var path = Path.Combine(fixture.Images, "unsafe.png");
        using var compressed = new MemoryStream();
        using (var zlib = new System.IO.Compression.ZLibStream(compressed, System.IO.Compression.CompressionLevel.Fastest, leaveOpen: true))
            zlib.Write(new byte[2 * 1024 * 1024 + 1]);
        using (var stream = File.Create(path))
        {
            stream.Write(new byte[] { 137, 80, 78, 71, 13, 10, 26, 10 });
            var text = "parameters\0\0"u8.ToArray().Concat(compressed.ToArray()).ToArray();
            Span<byte> header = stackalloc byte[8];
            System.Buffers.Binary.BinaryPrimitives.WriteInt32BigEndian(header, text.Length);
            "zTXt"u8.CopyTo(header[4..]); stream.Write(header); stream.Write(text); stream.Write(new byte[4]);
        }
        var error = Assert.Throws<GenerationMetadataException>(() => ForgePngGenerationMetadata.Read(path));
        Assert.Contains("展開後", error.Message);
    }

    private static void WriteWebpExif(string path, byte[] exif)
    {
        using var stream = File.Create(path);
        Span<byte> size = stackalloc byte[4];
        stream.Write("RIFF"u8);
        System.Buffers.Binary.BinaryPrimitives.WriteInt32LittleEndian(size, 12 + exif.Length + (exif.Length & 1));
        stream.Write(size); stream.Write("WEBPEXIF"u8);
        System.Buffers.Binary.BinaryPrimitives.WriteInt32LittleEndian(size, exif.Length);
        stream.Write(size); stream.Write(exif);
        if ((exif.Length & 1) != 0) stream.WriteByte(0);
    }
}
