using System.Buffers.Binary;
using System.IO.Compression;
using System.Text;
using System.Text.Json;

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

public sealed class GenerationMetadataException(string message) : Exception(message);

public static class ForgePngGenerationMetadata
{
    private static readonly byte[] Signature = [137, 80, 78, 71, 13, 10, 26, 10];
    private const int MaxTextChunkBytes = 2 * 1024 * 1024;
    private const int MaxDecodedTextBytes = 2 * 1024 * 1024;
    private const int MaxInfotextChars = 1_000_000;

    public static GenerationMetadataSnapshot Read(string path)
    {
        if (string.IsNullOrWhiteSpace(path)) throw new GenerationMetadataException("PNGファイルを指定してください");
        if (!Path.GetExtension(path).Equals(".png", StringComparison.OrdinalIgnoreCase))
            throw new GenerationMetadataException("生成情報の読込はPNGファイルに対応しています");
        if (!File.Exists(path)) throw new GenerationMetadataException("PNGファイルが見つかりません");

        string? infotext;
        try
        {
            using var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
            infotext = ReadParametersText(stream);
        }
        catch (GenerationMetadataException) { throw; }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
        {
            throw new GenerationMetadataException("PNGファイルを読み込めません: " + ex.Message);
        }

        if (string.IsNullOrWhiteSpace(infotext))
            throw new GenerationMetadataException("このPNGにはForge生成情報（parameters）がありません");
        if (infotext.Length > MaxInfotextChars)
            throw new GenerationMetadataException("PNGの生成情報が大きすぎます");

        return Parse(path, infotext);
    }

    public static GenerationMetadataSnapshot Parse(string sourcePath, string infotext)
    {
        if (string.IsNullOrWhiteSpace(infotext))
            throw new GenerationMetadataException("生成情報が空です");
        if (infotext.Length > MaxInfotextChars)
            throw new GenerationMetadataException("PNGの生成情報が大きすぎます");

        var normalized = infotext.Replace("\r\n", "\n", StringComparison.Ordinal).Replace('\r', '\n').Trim();
        var allLines = normalized.Split('\n');
        var parameterLine = "";
        var promptLines = allLines.AsEnumerable();

        if (allLines.Length > 0)
        {
            var candidate = allLines[^1].Trim();
            var candidateParameters = ParseParameterLine(candidate);
            if (candidateParameters.Count >= 3)
            {
                parameterLine = candidate;
                promptLines = allLines.Take(allLines.Length - 1);
            }
        }

        var positive = new List<string>();
        var negative = new List<string>();
        var inNegative = false;
        foreach (var rawLine in promptLines)
        {
            var line = rawLine.Trim();
            if (line.StartsWith("Negative prompt:", StringComparison.Ordinal))
            {
                inNegative = true;
                line = line["Negative prompt:".Length..].Trim();
            }

            if (inNegative) negative.Add(line);
            else positive.Add(line);
        }

        var positiveText = string.Join("\n", positive).Trim();
        var negativeText = string.Join("\n", negative).Trim();
        var parameters = ParseParameterLine(parameterLine);

        if (positiveText.Length == 0 && parameters.Count == 0)
            throw new GenerationMetadataException("Forge形式の生成情報を解析できません");

        return new(sourcePath, infotext, positiveText, negativeText, parameters);
    }

    private static string? ReadParametersText(Stream stream)
    {
        Span<byte> signature = stackalloc byte[8];
        ReadExactly(stream, signature);
        if (!signature.SequenceEqual(Signature))
            throw new GenerationMetadataException("PNGファイルの形式が正しくありません");

        Span<byte> header = stackalloc byte[8];
        Span<byte> crc = stackalloc byte[4];
        while (true)
        {
            if (!TryReadExactly(stream, header))
                throw new GenerationMetadataException("PNGファイルが途中で終わっています");

            var lengthValue = BinaryPrimitives.ReadUInt32BigEndian(header[..4]);
            if (lengthValue > int.MaxValue)
                throw new GenerationMetadataException("PNGチャンクが大きすぎます");
            var length = (int)lengthValue;
            var type = Encoding.ASCII.GetString(header[4..8]);

            string? value = null;
            if (type is "tEXt" or "zTXt" or "iTXt")
            {
                if (length > MaxTextChunkBytes)
                    throw new GenerationMetadataException("PNGのテキストメタデータが大きすぎます");
                var data = new byte[length];
                ReadExactly(stream, data);
                value = type switch
                {
                    "tEXt" => ReadText(data),
                    "zTXt" => ReadCompressedText(data),
                    "iTXt" => ReadInternationalText(data),
                    _ => null
                };
            }
            else
            {
                if (stream.CanSeek)
                {
                    if (stream.Length - stream.Position < length + 4L)
                        throw new GenerationMetadataException("PNGファイルが途中で終わっています");
                    stream.Seek(length, SeekOrigin.Current);
                }
                else
                {
                    SkipExactly(stream, length);
                }
            }

            ReadExactly(stream, crc);

            if (value is not null) return value;
            if (type == "IEND") return null;
        }
    }

    private static string? ReadText(byte[] data)
    {
        var zero = Array.IndexOf(data, (byte)0);
        if (zero <= 0) return null;
        var keyword = Encoding.Latin1.GetString(data, 0, zero);
        if (!keyword.Equals("parameters", StringComparison.OrdinalIgnoreCase)) return null;
        return Encoding.Latin1.GetString(data, zero + 1, data.Length - zero - 1);
    }

    private static string? ReadCompressedText(byte[] data)
    {
        var zero = Array.IndexOf(data, (byte)0);
        if (zero <= 0 || zero + 2 > data.Length) return null;
        var keyword = Encoding.Latin1.GetString(data, 0, zero);
        if (!keyword.Equals("parameters", StringComparison.OrdinalIgnoreCase)) return null;
        if (data[zero + 1] != 0) throw new GenerationMetadataException("未対応のPNG圧縮テキストです");
        return DecodeZlib(data.AsSpan(zero + 2), Encoding.Latin1);
    }

    private static string? ReadInternationalText(byte[] data)
    {
        var keywordEnd = Array.IndexOf(data, (byte)0);
        if (keywordEnd <= 0 || keywordEnd + 3 > data.Length) return null;
        var keyword = Encoding.Latin1.GetString(data, 0, keywordEnd);
        if (!keyword.Equals("parameters", StringComparison.OrdinalIgnoreCase)) return null;

        var compressionFlag = data[keywordEnd + 1];
        var compressionMethod = data[keywordEnd + 2];
        var cursor = keywordEnd + 3;
        var languageEnd = Array.IndexOf(data, (byte)0, cursor);
        if (languageEnd < 0) return null;
        cursor = languageEnd + 1;
        var translatedEnd = Array.IndexOf(data, (byte)0, cursor);
        if (translatedEnd < 0) return null;
        cursor = translatedEnd + 1;

        if (compressionFlag == 0)
            return Encoding.UTF8.GetString(data, cursor, data.Length - cursor);
        if (compressionFlag == 1 && compressionMethod == 0)
            return DecodeZlib(data.AsSpan(cursor), Encoding.UTF8);
        throw new GenerationMetadataException("未対応のPNG国際化テキストです");
    }

    private static string DecodeZlib(ReadOnlySpan<byte> compressed, Encoding encoding)
    {
        using var input = new MemoryStream(compressed.ToArray(), writable: false);
        using var zlib = new ZLibStream(input, CompressionMode.Decompress);
        using var output = new MemoryStream();
        var buffer = new byte[8192];
        while (true)
        {
            var read = zlib.Read(buffer, 0, buffer.Length);
            if (read == 0) break;
            if (output.Length + read > MaxDecodedTextBytes)
                throw new GenerationMetadataException("PNGの展開後メタデータが大きすぎます");
            output.Write(buffer, 0, read);
        }
        return encoding.GetString(output.ToArray());
    }

    private static IReadOnlyList<GenerationParameter> ParseParameterLine(string line)
    {
        if (string.IsNullOrWhiteSpace(line)) return [];
        var parts = new List<string>();
        var start = 0;
        var quoted = false;
        var escaped = false;

        for (var i = 0; i < line.Length; i++)
        {
            var c = line[i];
            if (escaped) { escaped = false; continue; }
            if (quoted && c == '\\') { escaped = true; continue; }
            if (c == '"') { quoted = !quoted; continue; }
            if (c == ',' && !quoted)
            {
                parts.Add(line[start..i]);
                start = i + 1;
            }
        }
        parts.Add(line[start..]);

        var result = new List<GenerationParameter>();
        foreach (var part in parts)
        {
            var colon = part.IndexOf(':');
            if (colon <= 0) continue;
            var name = part[..colon].Trim();
            var value = part[(colon + 1)..].Trim();
            if (name.Length == 0) continue;
            if (value.Length >= 2 && value[0] == '"' && value[^1] == '"')
            {
                try { value = JsonSerializer.Deserialize<string>(value) ?? value; }
                catch (JsonException) { value = value[1..^1]; }
            }
            result.Add(new(name, value));
        }
        return result;
    }

    private static void ReadExactly(Stream stream, Span<byte> buffer)
    {
        if (!TryReadExactly(stream, buffer))
            throw new GenerationMetadataException("PNGファイルが途中で終わっています");
    }

    private static void ReadExactly(Stream stream, byte[] buffer) => ReadExactly(stream, buffer.AsSpan());

    private static bool TryReadExactly(Stream stream, Span<byte> buffer)
    {
        var total = 0;
        while (total < buffer.Length)
        {
            var read = stream.Read(buffer[total..]);
            if (read == 0) return false;
            total += read;
        }
        return true;
    }

    private static void SkipExactly(Stream stream, int count)
    {
        var buffer = new byte[Math.Min(8192, Math.Max(1, count))];
        var remaining = count;
        while (remaining > 0)
        {
            var read = stream.Read(buffer, 0, Math.Min(buffer.Length, remaining));
            if (read == 0) throw new GenerationMetadataException("PNGファイルが途中で終わっています");
            remaining -= read;
        }
    }
}
