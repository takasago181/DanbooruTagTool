using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

/// <summary>Library file adapters; concrete parsers and future library dependencies belong in Data.</summary>
public static class GenerationMetadataReaders
{
    public static IGenerationMetadataReader[] CreateDefault() =>
        [new PngGenerationMetadataReader(), new ExifGenerationMetadataReader()];
    public static GenerationMetadataSnapshot ReadSnapshot(string path)
    {
        var reader = CreateDefault().FirstOrDefault(r => r.CanRead(Path.GetExtension(path)));
        return reader?.Read(path).Metadata ?? throw new InvalidDataException("派生元metadataを再確認できません。");
    }
}
