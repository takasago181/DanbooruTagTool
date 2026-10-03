using System.Buffers.Binary;
using System.Text;
using System.Text.Json;

namespace DanbooruTagTool.Core;

/// <summary>Bounded, unsigned DTT local-file observations in a separate PNG iTXt.
/// Forge's original parameters chunk, raw infotext and image chunks are not rewritten.</summary>
public static class GenerationLoraPngReceipt
{
    private static readonly byte[] Prefix = Encoding.ASCII.GetBytes(GenerationLoraProvenance.ReceiptKey + "\0\0\0\0\0");
    private const int MaxBytes = 128 * 1024;
    public static string? Read(string path)
    {
        using var stream = File.OpenRead(path);
        return Read(stream);
    }
    private static string? Read(Stream stream)
    {
        Span<byte> header = stackalloc byte[8]; stream.ReadExactly(header);
        if (!header.SequenceEqual(new byte[] {137,80,78,71,13,10,26,10})) throw new InvalidDataException("PNG signature。");
        string? receipt = null;
        Span<byte> crc = stackalloc byte[4];
        while (true)
        {
            if (stream.Length - stream.Position < header.Length) return receipt;
            stream.ReadExactly(header); var length = BinaryPrimitives.ReadUInt32BigEndian(header[..4]);
            if (length > int.MaxValue || stream.Length - stream.Position < length + 4L) throw new InvalidDataException("PNG receipt envelopeが不正です。");
            byte[]? crcData = null;
            if (header[4..].SequenceEqual("iTXt"u8) && length >= Prefix.Length)
            {
                var prefix = new byte[Prefix.Length]; stream.ReadExactly(prefix);
                if (prefix.AsSpan(0, Prefix.Length - 4).SequenceEqual(Prefix.AsSpan(0, Prefix.Length - 4)) && !prefix.AsSpan().SequenceEqual(Prefix)) throw new InvalidDataException("未対応LoRA receipt encoding。");
                if (prefix.AsSpan().SequenceEqual(Prefix))
                {
                    if (length > MaxBytes || receipt is not null) throw new InvalidDataException("LoRA receipt重複/上限超過。");
                    var body = new byte[(int)length - prefix.Length]; stream.ReadExactly(body);
                    receipt = new UTF8Encoding(false, true).GetString(body);
                    crcData = "iTXt"u8.ToArray().Concat(prefix).Concat(body).ToArray();
                    if (!GenerationLoraProvenance.IsValid(new(GenerationLoraProvenance.ReceiptKey, receipt))) throw new InvalidDataException("不正LoRA receipt。");
                }
                else stream.Seek(length - prefix.Length, SeekOrigin.Current);
            }
            else stream.Seek(length, SeekOrigin.Current);
            stream.ReadExactly(crc);
            if (crcData is not null && BinaryPrimitives.ReadUInt32BigEndian(crc) != Crc(crcData)) throw new InvalidDataException("LoRA receipt CRC不一致。");
            if (header[4..].SequenceEqual("IEND"u8)) return receipt;
        }
    }
    public static byte[] Attach(byte[] png, IReadOnlyList<GenerationLoraIdentity> identities)
    {
        if (identities.Count == 0) return png;
        using var stream = new MemoryStream(png, false);
        if (Read(stream) is not null) throw new InvalidDataException("Forge結果に予期しないDTT receiptがあります。");
        if (!png.AsSpan(png.Length - 12, 8).SequenceEqual(new byte[] {0,0,0,0,73,69,78,68})) throw new InvalidDataException("PNG IENDを確認できません。");
        var json = JsonSerializer.Serialize(identities);
        if (!GenerationLoraProvenance.IsValid(new(GenerationLoraProvenance.ReceiptKey, json))) throw new InvalidDataException("不正な観測identity。");
        var data = Prefix.Concat(Encoding.UTF8.GetBytes(json)).ToArray();
        if (data.Length > MaxBytes) throw new InvalidDataException("LoRA receipt上限超過。");
        using var output = new MemoryStream(); output.Write(png.AsSpan(0, png.Length - 12));
        Span<byte> number = stackalloc byte[4]; BinaryPrimitives.WriteInt32BigEndian(number, data.Length); output.Write(number);
        var typeData = "iTXt"u8.ToArray().Concat(data).ToArray(); output.Write(typeData); BinaryPrimitives.WriteUInt32BigEndian(number, Crc(typeData)); output.Write(number);
        output.Write(png.AsSpan(png.Length - 12)); return output.ToArray();
    }
    // Same PNG CRC32 algorithm already used by DTT's fixture writer.
    private static uint Crc(byte[] bytes)
    {
        uint crc = 0xffffffff;
        foreach (var b in bytes) { crc ^= b; for (var j = 0; j < 8; j++) crc = (crc >> 1) ^ ((crc & 1) == 0 ? 0u : 0xedb88320u); }
        return ~crc;
    }
}
