using DanbooruTagTool.Core;

namespace DanbooruTagTool.Data;

/// <summary>Full reconciliation is authoritative; partial/cancelled enumeration never marks files missing.</summary>
public sealed class GenerationLibraryScanner(GenerationLibraryStore store, params IGenerationMetadataReader[] readers)
{
    public LibraryScanResult Scan(LibraryRoot root, CancellationToken cancellationToken = default)
    {
        if (!root.Enabled) return new(0, 0, 0, 0, 0, false);
        var token = Guid.NewGuid().ToString("N"); var now = DateTime.UtcNow.ToString("O");
        var added = 0; var refreshed = 0; var unchanged = 0; var errors = 0;
        using var c = store.Open(); using var tx = c.BeginTransaction();
        try
        {
            var options = new EnumerationOptions { RecurseSubdirectories = root.Recursive, IgnoreInaccessible = false,
                AttributesToSkip = FileAttributes.ReparsePoint, ReturnSpecialDirectories = false };
            foreach (var path in Directory.EnumerateFiles(root.Path, "*", options))
            {
                cancellationToken.ThrowIfCancellationRequested();
                var extension = Path.GetExtension(path).ToLowerInvariant();
                if (extension is not (".png" or ".jpg" or ".jpeg" or ".webp")) continue;
                var relative = Path.GetRelativePath(root.Path, path);
                long? id = null; long size = -1, ticks = -1;
                using (var cmd = GenerationLibraryStore.Command(c, "SELECT id,file_size,mtime_utc_ticks FROM image_asset WHERE root_id=$r AND relative_path=$p", tx, ("$r", root.Id), ("$p", relative)))
                using (var r = cmd.ExecuteReader()) if (r.Read()) { id = r.GetInt64(0); size = r.GetInt64(1); ticks = r.GetInt64(2); }
                try
                {
                    var f = new FileInfo(path); f.Refresh(); if (!f.Exists) throw new IOException("File disappeared during scan");
                    if (id.HasValue && size == f.Length && ticks == f.LastWriteTimeUtc.Ticks)
                    {
                        GenerationLibraryStore.Execute(c, "UPDATE image_asset SET availability='available',last_seen_utc=$t,scan_token=$token WHERE id=$id", tx, ("$t", now), ("$token", token), ("$id", id)); unchanged++; continue;
                    }
                    var reader = readers.FirstOrDefault(r => r.CanRead(extension));
                    var result = reader?.Read(path) ?? new MetadataReadResult("metadata_missing");
                    if (result.Retryable) throw new IOException(result.Error ?? "Retry metadata read on next scan");
                    var newSize = f.Length; var newTicks = f.LastWriteTimeUtc.Ticks; f.Refresh();
                    if (!f.Exists || f.Length != newSize || f.LastWriteTimeUtc.Ticks != newTicks) throw new IOException("File changed during metadata read; rescan to retry");
                    if (!id.HasValue)
                    {
                        GenerationLibraryStore.Execute(c, "INSERT INTO image_asset(root_id,relative_path,normalized_path,extension,file_size,mtime_utc_ticks,availability,metadata_status,first_seen_utc,last_seen_utc,scan_token) VALUES($r,$p,$full,$ext,$size,$ticks,'available',$status,$t,$t,$token)", tx,
                            ("$r", root.Id), ("$p", relative), ("$full", Path.GetFullPath(path)), ("$ext", extension), ("$size", newSize), ("$ticks", newTicks), ("$status", result.Status), ("$t", now), ("$token", token));
                        id = Convert.ToInt64(GenerationLibraryStore.Scalar(c, "SELECT last_insert_rowid()", tx)); added++;
                    }
                    else refreshed++;
                    GenerationLibraryStore.Execute(c, "UPDATE image_asset SET normalized_path=$full,file_size=$size,mtime_utc_ticks=$ticks,width=$w,height=$h,availability='available',metadata_status=$status,metadata_format=$format,last_seen_utc=$t,scan_token=$token,content_hash=NULL WHERE id=$id", tx,
                        ("$full", Path.GetFullPath(path)), ("$size", newSize), ("$ticks", newTicks), ("$w", result.Width), ("$h", result.Height), ("$status", result.Status), ("$format", result.Format), ("$t", now), ("$token", token), ("$id", id));
                    GenerationLibraryStore.SaveMetadata(c, tx, id.Value, result);
                    if (result.Status is "metadata_invalid" or "unreadable") errors++;
                }
                catch (Exception e) when (e is IOException or UnauthorizedAccessException or GenerationMetadataException or InvalidDataException or OverflowException)
                {
                    errors++;
                    // Keep prior metadata/annotations and retry next scan (mtime/size not advanced).
                    if (id.HasValue) GenerationLibraryStore.Execute(c, "UPDATE image_asset SET metadata_status='unreadable',file_size=-1,mtime_utc_ticks=-1,scan_token=$token WHERE id=$id", tx, ("$token", token), ("$id", id));
                    else GenerationLibraryStore.Execute(c, "INSERT INTO image_asset(root_id,relative_path,normalized_path,extension,file_size,mtime_utc_ticks,availability,metadata_status,first_seen_utc,last_seen_utc,scan_token) VALUES($r,$p,$full,$ext,-1,-1,'available','unreadable',$t,$t,$token)", tx,
                        ("$r", root.Id), ("$p", relative), ("$full", Path.GetFullPath(path)), ("$ext", extension), ("$t", now), ("$token", token));
                }
            }
            cancellationToken.ThrowIfCancellationRequested();
            var missing = GenerationLibraryStore.Execute(c, "UPDATE image_asset SET availability='missing' WHERE root_id=$r AND (scan_token IS NULL OR scan_token<>$token) AND availability<>'missing'", tx, ("$r", root.Id), ("$token", token));
            GenerationLibraryStore.Execute(c, "UPDATE library_root SET last_scan_utc=$t,last_complete_scan_token=$token WHERE id=$r", tx, ("$t", now), ("$token", token), ("$r", root.Id));
            tx.Commit(); return new(added, refreshed, unchanged, missing, errors, true);
        }
        catch (Exception e) when (e is IOException or UnauthorizedAccessException)
        { tx.Rollback(); return new(0, 0, 0, 0, errors + 1, false); }
    }
}
