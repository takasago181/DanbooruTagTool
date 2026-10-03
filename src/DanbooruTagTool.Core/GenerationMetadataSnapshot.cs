namespace DanbooruTagTool.Core;

public sealed record GenerationParameter(string Name, string Value);

public sealed record GenerationMetadataSnapshot(
    string SourcePath,
    string RawInfotext,
    string Positive,
    string Negative,
    IReadOnlyList<GenerationParameter> Parameters)
{
    public string? Value(string name) =>
        Parameters.LastOrDefault(item => item.Name.Equals(name, StringComparison.OrdinalIgnoreCase))?.Value;

    public int? Width => ParseSize()?.Width;
    public int? Height => ParseSize()?.Height;

    private (int Width, int Height)? ParseSize()
    {
        var size = Value("Size");
        if (string.IsNullOrWhiteSpace(size)) return null;
        var x = size.IndexOf('x');
        if (x < 0) x = size.IndexOf('X');
        if (x <= 0 || x >= size.Length - 1) return null;
        return int.TryParse(size[..x], out var width) && int.TryParse(size[(x + 1)..], out var height)
            ? (width, height)
            : null;
    }
}

public sealed class GenerationMetadataException(string message, bool retryable = false) : Exception(message)
{
    public bool Retryable { get; } = retryable;
}
