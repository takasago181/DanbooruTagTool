using System.Buffers.Binary;
using System.IO.Compression;
using System.Text;

namespace DanbooruTagTool.Core;

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
            throw new GenerationMetadataException("PNGファイルを読み込めません: " + ex.Message, retryable: true);
        }

        if (string.IsNullOrWhiteSpace(infotext))
            throw new GenerationMetadataException("このPNGにはForge生成情報（parameters）がありません");
        if (infotext.Length > MaxInfotextChars)
            throw new GenerationMetadataException("PNGの生成情報が大きすぎます");

        var snapshot = Parse(path, infotext);
        try
        {
            var receipt = GenerationLoraPngReceipt.Read(path);
            if (receipt is not null) snapshot = snapshot with { Parameters = snapshot.Parameters.Concat([new GenerationParameter(GenerationLoraProvenance.ReceiptKey, receipt)]).ToArray() };
            var regional = GenerationLoraPngReceipt.Read(path, RegionComposer.Key);
            if (regional is not null)
            {
                var field = new GenerationParameter(RegionComposer.Key, regional);
                var observed = RegionComposer.Read([field])!;
                RegionComposer.Verify(observed.Config, snapshot);
                snapshot = snapshot with { Parameters = snapshot.Parameters.Concat([field]).ToArray() };
            }
            var derivation = GenerationLoraPngReceipt.Read(path, GenerationRecipeDerivation.Key);
            if (derivation is not null)
            {
                var field = new GenerationParameter(GenerationRecipeDerivation.Key, derivation);
                var edge = GenerationRecipeDerivation.Read([field])!;
                if (ForgeGenerationApiClient.Compare(new(edge.Requested.Positive, edge.Requested.Negative, edge.Requested.Recipe), null, snapshot).Count > 0)
                    throw new InvalidDataException("Recipe派生記録と実画像metadataが矛盾しています。");
                snapshot = snapshot with { Parameters = snapshot.Parameters.Concat([field]).ToArray() };
            }
            return snapshot;
        }
        catch (Exception e) when (e is IOException or InvalidDataException or DecoderFallbackException)
        { throw new GenerationMetadataException("DTT provenanceを読み込めません: " + e.Message); }
    }

    // Compatibility entry point for existing PNG import/API callers.
    public static GenerationMetadataSnapshot Parse(string sourcePath, string infotext) =>
        GenerationInfotextParser.Parse(sourcePath, infotext);

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
