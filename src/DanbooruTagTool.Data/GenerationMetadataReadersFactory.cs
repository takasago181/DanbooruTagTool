using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

/// <summary>Library file adapters; concrete parsers and future library dependencies belong in Data.</summary>
public static class GenerationMetadataReaders
{
    public static IGenerationMetadataReader[] CreateDefault() =>
        [new PngGenerationMetadataReader(), new ExifGenerationMetadataReader()];
}
