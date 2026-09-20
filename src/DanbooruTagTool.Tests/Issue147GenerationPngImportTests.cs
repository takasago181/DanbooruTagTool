using System.Buffers.Binary;
using System.Text;
using DanbooruTagTool.Core;
using Xunit;

namespace DanbooruTagTool.Tests;

public class Issue147GenerationPngImportTests
{
    private const string Infotext =
        "masterpiece, 1girl, blue_hair\n" +
        "Negative prompt: lowres, bad hands\n" +
        "Steps: 25, Sampler: Euler a, Schedule type: Karras, CFG scale: 5, Seed: 123456, Size: 1024x1024, Model: waiNSFWIllustrious_v140, Lora hashes: \"foo: abc, bar: def\", Custom setting: alpha";

    [Fact]
    public void ParseForgeInfotextPreservesPromptNegativeCommonAndUnknownParameters()
    {
        var snapshot = ForgePngGenerationMetadata.Parse("sample.png", Infotext);

        Assert.Equal("masterpiece, 1girl, blue_hair", snapshot.Positive);
        Assert.Equal("lowres, bad hands", snapshot.Negative);
        Assert.Equal("25", snapshot.Value("Steps"));
        Assert.Equal("Euler a", snapshot.Value("Sampler"));
        Assert.Equal("Karras", snapshot.Value("Schedule type"));
        Assert.Equal("5", snapshot.Value("CFG scale"));
        Assert.Equal("123456", snapshot.Value("Seed"));
        Assert.Equal("1024x1024", snapshot.Value("Size"));
        Assert.Equal(1024, snapshot.Width);
        Assert.Equal(1024, snapshot.Height);
        Assert.Equal("foo: abc, bar: def", snapshot.Value("Lora hashes"));
        Assert.Equal("alpha", snapshot.Value("Custom setting"));
    }

    [Fact]
    public void MultilinePositiveAndNegativeArePreserved()
    {
        var text =
            "score_9, score_8_up\n" +
            "1girl, long_hair\n" +
            "Negative prompt: lowres\n" +
            "bad hands, text\n" +
            "Steps: 20, Sampler: Euler a, Seed: 9, Size: 832x1216";

        var snapshot = ForgePngGenerationMetadata.Parse("sample.png", text);

        Assert.Equal("score_9, score_8_up\n1girl, long_hair", snapshot.Positive);
        Assert.Equal("lowres\nbad hands, text", snapshot.Negative);
        Assert.Equal(832, snapshot.Width);
        Assert.Equal(1216, snapshot.Height);
    }

    [Fact]
    public void ReadsStandardPngTextParametersWithoutDecodingImagePixels()
    {
        using var directory = new TempDirectory();
        var path = Path.Combine(directory.Path, "forge.png");
        WritePng(path, ("tEXt", TextChunk("parameters", Infotext)));

        var snapshot = ForgePngGenerationMetadata.Read(path);

        Assert.Equal(path, snapshot.SourcePath);
        Assert.Equal("123456", snapshot.Value("Seed"));
        Assert.Equal("masterpiece, 1girl, blue_hair", snapshot.Positive);
    }

    [Fact]
    public void ReadsUtf8InternationalTextParameters()
    {
        using var directory = new TempDirectory();
        var path = Path.Combine(directory.Path, "forge-unicode.png");
        var text = "1girl, café\nNegative prompt: 悪い手\nSteps: 20, Sampler: Euler a, Seed: 1, Size: 512x512";
        WritePng(path, ("iTXt", InternationalTextChunk("parameters", text)));

        var snapshot = ForgePngGenerationMetadata.Read(path);

        Assert.Equal("1girl, café", snapshot.Positive);
        Assert.Equal("悪い手", snapshot.Negative);
        Assert.Equal("1", snapshot.Value("Seed"));
    }

    [Fact]
    public void MissingOrMalformedPngMetadataFailsClearly()
    {
        using var directory = new TempDirectory();
        var noParameters = Path.Combine(directory.Path, "plain.png");
        WritePng(noParameters, ("tEXt", TextChunk("comment", "hello")));

        var missing = Assert.Throws<GenerationMetadataException>(() => ForgePngGenerationMetadata.Read(noParameters));
        Assert.Contains("parameters", missing.Message);

        var malformed = Path.Combine(directory.Path, "broken.png");
        File.WriteAllText(malformed, "not a png");
        var invalid = Assert.Throws<GenerationMetadataException>(() => ForgePngGenerationMetadata.Read(malformed));
        Assert.Contains("PNG", invalid.Message);
    }

    [Fact]
    public void ImportReviewDoesNotMutatePromptUntilRestoreAndRestoreIsUndoable()
    {
        using var directory = new TempDirectory();
        var path = Path.Combine(directory.Path, "forge.png");
        WritePng(path, ("tEXt", TextChunk("parameters", Infotext)));
        var clipboard = new MemoryClipboard();
        var vm = Fixtures.Vm(clipboard: clipboard);
        vm.Workspace.Replace("smile");

        Assert.True(vm.ImportGenerationPng(path));
        Assert.Equal("smile", vm.English);
        Assert.Equal("123456", vm.GenerationImport.Snapshot!.Value("Seed"));
        Assert.Contains(vm.GenerationImport.AdditionalRows, row => row.Name == "Lora hashes");

        vm.GenerationImport.CopyNegative.Execute(null);
        Assert.Equal("lowres, bad hands", clipboard.Value);

        vm.GenerationImport.RestorePositive.Execute(null);
        Assert.Equal("masterpiece, 1girl, blue_hair", vm.English);

        vm.Undo.Execute(null);
        Assert.Equal("smile", vm.English);
    }

    private static byte[] TextChunk(string keyword, string text)
    {
        var key = Encoding.Latin1.GetBytes(keyword);
        var value = Encoding.Latin1.GetBytes(text);
        return [.. key, 0, .. value];
    }

    private static byte[] InternationalTextChunk(string keyword, string text)
    {
        var key = Encoding.Latin1.GetBytes(keyword);
        var value = Encoding.UTF8.GetBytes(text);
        return [.. key, 0, 0, 0, 0, 0, .. value];
    }

    private static void WritePng(string path, params (string Type, byte[] Data)[] chunks)
    {
        using var stream = File.Create(path);
        stream.Write([137, 80, 78, 71, 13, 10, 26, 10]);
        foreach (var chunk in chunks) WriteChunk(stream, chunk.Type, chunk.Data);
        WriteChunk(stream, "IEND", []);
    }

    private static void WriteChunk(Stream stream, string type, byte[] data)
    {
        Span<byte> length = stackalloc byte[4];
        BinaryPrimitives.WriteUInt32BigEndian(length, (uint)data.Length);
        stream.Write(length);
        stream.Write(Encoding.ASCII.GetBytes(type));
        stream.Write(data);
        stream.Write([0, 0, 0, 0]); // Reader intentionally does not decode pixels or validate CRC.
    }
}
