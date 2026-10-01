using System.Buffers.Binary;
using System.Text;

namespace DanbooruTagTool.Core;

public sealed class PngGenerationMetadataReader : IGenerationMetadataReader
{
    public bool CanRead(string extension) => extension.Equals(".png", StringComparison.OrdinalIgnoreCase);
    public MetadataReadResult Read(string path)
    {
        int? width = null, height = null;
        try
        {
            using (var s = File.OpenRead(path))
            {
                Span<byte> header = stackalloc byte[24]; s.ReadExactly(header);
                if (!header[..8].SequenceEqual(new byte[] { 137, 80, 78, 71, 13, 10, 26, 10 }))
                    return new("unreadable", "PNG", Error: "Invalid PNG signature");
                if (header[12..16].SequenceEqual("IHDR"u8))
                {
                    width = checked((int)BinaryPrimitives.ReadUInt32BigEndian(header[16..20]));
                    height = checked((int)BinaryPrimitives.ReadUInt32BigEndian(header[20..24]));
                }
            }
            try { return new("OK", "PNG parameters", ForgePngGenerationMetadata.Read(path), width, height); }
            catch (GenerationMetadataException e)
            { return new(e.Retryable ? "unreadable" : e.Message.Contains("parameters）がありません", StringComparison.Ordinal) ? "metadata_missing" : "metadata_invalid", "PNG", Width: width, Height: height, Error: e.Message, Retryable: e.Retryable); }
            catch (InvalidDataException e) { return new("metadata_invalid", "PNG", Width: width, Height: height, Error: e.Message); }
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException or InvalidDataException or OverflowException)
        { return new("unreadable", "PNG", Error: e.Message, Retryable: e is IOException and not EndOfStreamException or UnauthorizedAccessException); }
    }
}

/// <summary>Bounded JPEG APP1 / WebP EXIF envelope and TIFF UserComment reader; no pixel decode.</summary>
public sealed class ExifGenerationMetadataReader : IGenerationMetadataReader
{
    private const int MaxExif = 2 * 1024 * 1024;
    public bool CanRead(string extension) => extension.ToLowerInvariant() is ".jpg" or ".jpeg" or ".webp";
    public MetadataReadResult Read(string path)
    {
        var format = Path.GetExtension(path).Equals(".webp", StringComparison.OrdinalIgnoreCase) ? "WebP" : "JPEG";
        try
        {
            using var s = File.OpenRead(path);
            var exif = format == "JPEG" ? JpegExif(s) : WebpExif(s);
            if (exif is null) return new("metadata_missing", format);
            var text = UserComment(exif);
            if (string.IsNullOrWhiteSpace(text)) return new("metadata_missing", format);
            var metadata = ForgePngGenerationMetadata.Parse(path, text);
            return new("OK", format + " EXIF UserComment", metadata, metadata.Width, metadata.Height);
        }
        catch (Exception e) when (e is InvalidDataException or GenerationMetadataException or ArgumentException or OverflowException)
        { return new("metadata_invalid", format, Error: e.Message); }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException)
        { return new("unreadable", format, Error: e.Message, Retryable: e is not EndOfStreamException); }
    }
    private static byte[]? JpegExif(Stream s)
    {
        if (s.ReadByte() != 0xff || s.ReadByte() != 0xd8) throw new InvalidDataException("Invalid JPEG signature");
        Span<byte> length = stackalloc byte[2];
        while (s.Position < s.Length)
        {
            if (s.ReadByte() != 0xff) throw new InvalidDataException("Invalid JPEG marker");
            int marker; do { marker = s.ReadByte(); } while (marker == 0xff);
            if (marker is 0xda or 0xd9) return null;
            if (marker is 0x01 or >= 0xd0 and <= 0xd8) continue;
            s.ReadExactly(length); var count = BinaryPrimitives.ReadUInt16BigEndian(length) - 2;
            if (count < 0 || count > s.Length - s.Position) throw new InvalidDataException("Truncated JPEG segment");
            if (marker == 0xe1)
            {
                var data = new byte[count]; s.ReadExactly(data);
                if (data.AsSpan().StartsWith("Exif\0\0"u8)) return data;
            }
            else s.Seek(count, SeekOrigin.Current);
        }
        throw new InvalidDataException("Truncated JPEG");
    }
    private static byte[]? WebpExif(Stream s)
    {
        Span<byte> header = stackalloc byte[12]; s.ReadExactly(header);
        if (!header[..4].SequenceEqual("RIFF"u8) || !header[8..].SequenceEqual("WEBP"u8)) throw new InvalidDataException("Invalid WebP signature");
        var end = BinaryPrimitives.ReadUInt32LittleEndian(header[4..8]) + 8L;
        if (end > s.Length) throw new InvalidDataException("Truncated WebP");
        Span<byte> chunk = stackalloc byte[8];
        while (s.Position + 8 <= end)
        {
            s.ReadExactly(chunk); var count = BinaryPrimitives.ReadUInt32LittleEndian(chunk[4..]);
            var padded = count + (long)(count & 1);
            if (padded > end - s.Position) throw new InvalidDataException("Truncated WebP chunk");
            if (chunk[..4].SequenceEqual("EXIF"u8))
            {
                if (count > MaxExif) throw new InvalidDataException("EXIF exceeds 2 MiB");
                var data = new byte[(int)count]; s.ReadExactly(data); return data;
            }
            s.Seek(padded, SeekOrigin.Current);
        }
        return null;
    }
    private static string? UserComment(byte[] envelope)
    {
        var data = envelope.AsSpan().StartsWith("Exif\0\0"u8) ? envelope[6..] : envelope;
        if (data.Length < 8) throw new InvalidDataException("Truncated TIFF");
        var little = data.AsSpan(0, 2).SequenceEqual("II"u8);
        if (!little && !data.AsSpan(0, 2).SequenceEqual("MM"u8)) throw new InvalidDataException("Invalid TIFF byte order");
        void Bound(int offset, int count) { if (offset < 0 || count < 0 || offset > data.Length - count) throw new InvalidDataException("Invalid EXIF offset"); }
        ushort U16(int offset) { Bound(offset, 2); return little ? BinaryPrimitives.ReadUInt16LittleEndian(data.AsSpan(offset, 2)) : BinaryPrimitives.ReadUInt16BigEndian(data.AsSpan(offset, 2)); }
        uint U32(int offset) { Bound(offset, 4); return little ? BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(offset, 4)) : BinaryPrimitives.ReadUInt32BigEndian(data.AsSpan(offset, 4)); }
        if (U16(2) != 42) throw new InvalidDataException("Invalid TIFF magic");
        var visited = new HashSet<int>();
        byte[]? ReadIfd(int offset, int depth)
        {
            if (depth > 2 || !visited.Add(offset)) throw new InvalidDataException("Invalid EXIF IFD cycle");
            var count = U16(offset); if (count > 4096) throw new InvalidDataException("Too many EXIF entries");
            Bound(offset + 2, count * 12);
            for (var i = 0; i < count; i++)
            {
                var p = offset + 2 + i * 12; var tag = U16(p); var type = U16(p + 2); var size = U32(p + 4);
                if (tag == 0x8769 && type == 4 && size == 1)
                { var nested = ReadIfd(checked((int)U32(p + 8)), depth + 1); if (nested is not null) return nested; }
                if (tag == 0x9286 && type is 7 or 2 or 1)
                {
                    if (size > MaxExif) throw new InvalidDataException("UserComment too large");
                    var start = size <= 4 ? p + 8 : checked((int)U32(p + 8)); Bound(start, (int)size); return data.AsSpan(start, (int)size).ToArray();
                }
            }
            return null;
        }
        var comment = ReadIfd(checked((int)U32(4)), 0);
        if (comment is null || comment.Length < 8) return null;
        var body = comment.AsSpan(8);
        if (comment.AsSpan(0, 8).SequenceEqual("ASCII\0\0\0"u8)) return Encoding.UTF8.GetString(body).TrimEnd('\0');
        if (!comment.AsSpan(0, 8).SequenceEqual("UNICODE\0"u8)) throw new InvalidDataException("Unsupported UserComment encoding");
        if ((body.Length & 1) != 0) throw new InvalidDataException("Odd-length Unicode UserComment");
        // piexif writes UTF-16 big endian independently of TIFF's endian flag. Honor an explicit BOM.
        var encoding = Encoding.BigEndianUnicode;
        if (body.StartsWith(new byte[] { 0xff, 0xfe })) { encoding = Encoding.Unicode; body = body[2..]; }
        else if (body.StartsWith(new byte[] { 0xfe, 0xff })) body = body[2..];
        return encoding.GetString(body).TrimEnd('\0');
    }
}
