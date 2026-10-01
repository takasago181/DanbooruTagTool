using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Media.Imaging;
using DanbooruTagTool.Core;

namespace DanbooruTagTool.App;

/// <summary>Disposable/reconstructible pixel cache; no DB or annotation writes.</summary>
public sealed class GenerationThumbnailCache(string directory)
{
    public const int SchemaVersion = 1;
    public const int Edge = 256;
    private readonly SemaphoreSlim workers = new(2);
    public string Key(LibraryImage image) => Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(
        $"{SchemaVersion}|{Edge}|{image.Id}|{image.NormalizedPath}|{image.FileSize}|{image.MtimeUtcTicks}")));
    public async Task<BitmapSource?> GetAsync(LibraryImage image, CancellationToken cancellationToken = default)
    {
        if (image.Availability != "available") return null;
        await workers.WaitAsync(cancellationToken);
        try
        {
            return await Task.Run(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var path = Path.Combine(directory, Key(image) + ".png");
                if (File.Exists(path))
                {
                    try { return Load(path); }
                    catch (Exception e) when (Recoverable(e)) { File.Delete(path); }
                }
                Directory.CreateDirectory(directory);
                using var source = new FileStream(image.NormalizedPath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
                var frame = BitmapFrame.Create(source, BitmapCreateOptions.DelayCreation, BitmapCacheOption.None);
                var width = frame.PixelWidth; var height = frame.PixelHeight;
                source.Position = 0;
                var bitmap = new BitmapImage(); bitmap.BeginInit(); bitmap.CacheOption = BitmapCacheOption.OnLoad;
                bitmap.StreamSource = source;
                if (width >= height) bitmap.DecodePixelWidth = Math.Min(Edge, width);
                else bitmap.DecodePixelHeight = Math.Min(Edge, height);
                bitmap.EndInit(); bitmap.Freeze();
                cancellationToken.ThrowIfCancellationRequested();
                var current = new FileInfo(image.NormalizedPath);
                if (!current.Exists || current.Length != image.FileSize || current.LastWriteTimeUtc.Ticks != image.MtimeUtcTicks) return null;
                var temp = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
                try
                {
                    using (var output = File.Create(temp))
                    {
                        var encoder = new PngBitmapEncoder(); encoder.Frames.Add(BitmapFrame.Create(bitmap)); encoder.Save(output);
                    }
                    File.Move(temp, path, overwrite: true);
                }
                finally { if (File.Exists(temp)) File.Delete(temp); }
                return (BitmapSource)bitmap;
            }, cancellationToken);
        }
        catch (Exception e) when (Recoverable(e)) { return null; }
        finally { workers.Release(); }
    }
    private static BitmapSource Load(string path)
    {
        using var s = File.OpenRead(path); var image = new BitmapImage(); image.BeginInit(); image.CacheOption = BitmapCacheOption.OnLoad;
        image.StreamSource = s; image.DecodePixelWidth = Edge; image.EndInit(); image.Freeze(); return image;
    }
    private static bool Recoverable(Exception e) => e is IOException or UnauthorizedAccessException or NotSupportedException or ArgumentException or FileFormatException or InvalidOperationException or OverflowException;
}
