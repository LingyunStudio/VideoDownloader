using System.Diagnostics;
using System.IO.Compression;
using System.Text.Json;
using VideoDownloader.Helpers;

namespace VideoDownloader.Services;

public readonly record struct DownloadProgressInfo(long DownloadedBytes, long TotalBytes)
{
    public double Percentage => TotalBytes > 0 ? Math.Clamp(DownloadedBytes * 100.0 / TotalBytes, 0, 100) : 0;
}

public readonly record struct YtDlpVersionCheckResult(
    string CurrentVersion,
    string LatestVersion,
    bool UpdateAvailable,
    string DownloadUrl,
    bool IsZipArchive);

/// <summary>
/// Manages yt-dlp (preferring fast-start unpacked yt-dlp_win.zip) and ffmpeg binaries
/// under %APPDATA%\VideoDownloader\tools\, with automatic download and in-place updates.
/// </summary>
public sealed class ToolManagerService
{
    private const string YtDlpLatestApi = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest";
    private const string Aria2LatestApi = "https://api.github.com/repos/aria2/aria2/releases/latest";
    private const string Aria2FallbackUrl = "https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0-win-64bit-build1.zip";
    private const string FfmpegWinZipUrl = "https://github.com/zackees/ffmpeg_bins/raw/main/v8.0/win32.zip";

    private readonly string _ytDlpDir;
    private readonly string _ffmpegDir;
    private readonly string _aria2Dir;
    private readonly SemaphoreSlim _ytDlpLock = new(1, 1);
    private readonly SemaphoreSlim _ffmpegLock = new(1, 1);
    private readonly SemaphoreSlim _aria2Lock = new(1, 1);

    public ToolManagerService()
    {
        var baseDir = Path.Combine(AppLogger.AppDataDirectory, "tools");
        _ytDlpDir = Path.Combine(baseDir, "yt-dlp");
        _aria2Dir = Path.Combine(baseDir, "aria2");
        _ffmpegDir = Path.Combine(AppLogger.AppDataDirectory, "ffmpeg");
        Directory.CreateDirectory(_ytDlpDir);
        Directory.CreateDirectory(_aria2Dir);
        Directory.CreateDirectory(_ffmpegDir);
    }

    public string YtDlpDirectory => _ytDlpDir;
    public string FfmpegDirectory => _ffmpegDir;
    public string Aria2Directory => _aria2Dir;

    public string? FindYtDlpExecutable()
    {
        // 1. Managed directory in %APPDATA% (fast-start yt-dlp_win.zip or yt-dlp.exe)
        var managed = Path.Combine(_ytDlpDir, "yt-dlp.exe");
        if (File.Exists(managed))
            return managed;

        // 2. Bundled beside app executable
        var bundled = Path.Combine(AppContext.BaseDirectory, "tools", "yt-dlp", "yt-dlp.exe");
        if (File.Exists(bundled))
            return bundled;

        // 3. System PATH
        return FindOnPath("yt-dlp.exe");
    }

    public string? FindFfmpegDirectory()
    {
        if (File.Exists(Path.Combine(_ffmpegDir, "ffmpeg.exe")))
            return _ffmpegDir;

        var bundledDir = Path.Combine(AppContext.BaseDirectory, "tools", "ffmpeg");
        if (File.Exists(Path.Combine(bundledDir, "ffmpeg.exe")))
            return bundledDir;

        var onPath = FindOnPath("ffmpeg.exe");
        return onPath is not null ? Path.GetDirectoryName(onPath) : null;
    }

    public string? FindAria2Executable()
    {
        var managed = Path.Combine(_aria2Dir, "aria2c.exe");
        if (File.Exists(managed))
            return managed;

        var bundled = Path.Combine(AppContext.BaseDirectory, "tools", "aria2", "aria2c.exe");
        if (File.Exists(bundled))
            return bundled;

        return FindOnPath("aria2c.exe");
    }

    public bool IsYtDlpReady => FindYtDlpExecutable() is not null;
    public bool IsFfmpegReady => FindFfmpegDirectory() is not null;
    public bool IsAria2Ready => FindAria2Executable() is not null;

    public async Task<string> GetInstalledYtDlpVersionAsync(CancellationToken ct = default)
    {
        var exe = FindYtDlpExecutable();
        if (exe is null)
            return "未安装";

        try
        {
            using var proc = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = exe,
                    Arguments = "--version",
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true
                }
            };
            proc.Start();
            var output = await proc.StandardOutput.ReadToEndAsync(ct);
            await proc.WaitForExitAsync(ct);
            var ver = output.Trim();
            return string.IsNullOrWhiteSpace(ver) ? "未知" : ver;
        }
        catch (Exception ex)
        {
            AppLogger.Warn($"Failed to query yt-dlp version: {ex.Message}");
            return "未知";
        }
    }

    public async Task<YtDlpVersionCheckResult> CheckYtDlpUpdateAsync(CancellationToken ct = default)
    {
        var current = await GetInstalledYtDlpVersionAsync(ct);

        using var req = new HttpRequestMessage(HttpMethod.Get, YtDlpLatestApi);
        req.Headers.Accept.ParseAdd("application/vnd.github+json");
        using var resp = await HttpClientProvider.Shared.SendAsync(req, ct);
        resp.EnsureSuccessStatusCode();

        await using var stream = await resp.Content.ReadAsStreamAsync(ct);
        using var doc = await JsonDocument.ParseAsync(stream, cancellationToken: ct);
        var root = doc.RootElement;

        var tag = root.TryGetProperty("tag_name", out var tagEl) ? tagEl.GetString()?.Trim() ?? "" : "";
        string zipUrl = "";
        string exeUrl = "";

        if (root.TryGetProperty("assets", out var assets) && assets.ValueKind == JsonValueKind.Array)
        {
            foreach (var asset in assets.EnumerateArray())
            {
                var name = asset.TryGetProperty("name", out var nEl) ? nEl.GetString() : null;
                var url = asset.TryGetProperty("browser_download_url", out var uEl) ? uEl.GetString() : null;
                if (string.IsNullOrEmpty(name) || string.IsNullOrEmpty(url))
                    continue;

                if (name.Equals("yt-dlp_win.zip", StringComparison.OrdinalIgnoreCase))
                    zipUrl = url;
                else if (name.Equals("yt-dlp.exe", StringComparison.OrdinalIgnoreCase))
                    exeUrl = url;
            }
        }

        // Prefer unpacked yt-dlp_win.zip for instant startup (<0.2s vs ~1.2s for onefile exe)
        bool useZip = !string.IsNullOrEmpty(zipUrl);
        var dlUrl = useZip ? zipUrl : exeUrl;
        bool updateAvailable = !IsYtDlpReady || FormatHelpers.IsNewerVersion(tag, current);

        return new YtDlpVersionCheckResult(current, tag, updateAvailable, dlUrl, useZip);
    }

    public async Task<string> EnsureYtDlpAsync(IProgress<DownloadProgressInfo>? progress = null, CancellationToken ct = default)
    {
        var existing = FindYtDlpExecutable();
        if (existing is not null)
            return existing;

        await InstallOrUpdateYtDlpAsync(progress, ct);
        return FindYtDlpExecutable() ?? throw new InvalidOperationException("yt-dlp 安装完成但未找到可执行文件。");
    }

    public async Task<string> InstallOrUpdateYtDlpAsync(IProgress<DownloadProgressInfo>? progress = null, CancellationToken ct = default)
    {
        await _ytDlpLock.WaitAsync(ct);
        try
        {
            var check = await CheckYtDlpUpdateAsync(ct);
            if (string.IsNullOrEmpty(check.DownloadUrl))
                throw new InvalidOperationException("无法从 GitHub 获取 yt-dlp 下载地址，请检查网络。");

            var tempDir = Path.Combine(Path.GetTempPath(), $"vdl_ytdlp_{Guid.NewGuid():N}");
            Directory.CreateDirectory(tempDir);

            try
            {
                if (check.IsZipArchive)
                {
                    var zipPath = Path.Combine(tempDir, "yt-dlp_win.zip");
                    await DownloadFileAsync(check.DownloadUrl, zipPath, progress, ct);

                    var extractDir = Path.Combine(tempDir, "extracted");
                    ZipFile.ExtractToDirectory(zipPath, extractDir, overwriteFiles: true);

                    // Find folder containing yt-dlp.exe
                    var exeFile = Directory.EnumerateFiles(extractDir, "yt-dlp.exe", SearchOption.AllDirectories).FirstOrDefault()
                                  ?? throw new InvalidOperationException("压缩包内未找到 yt-dlp.exe。");
                    var sourceRoot = Path.GetDirectoryName(exeFile)!;

                    // Swap directory safely
                    var stagingDir = Path.Combine(AppLogger.AppDataDirectory, "tools", $"yt-dlp_new_{Guid.NewGuid():N}");
                    CopyDirectory(sourceRoot, stagingDir);

                    var backupDir = Path.Combine(AppLogger.AppDataDirectory, "tools", $"yt-dlp_old_{Guid.NewGuid():N}");
                    if (Directory.Exists(_ytDlpDir))
                    {
                        try { Directory.Move(_ytDlpDir, backupDir); }
                        catch
                        {
                            // Fallback: overwrite in place
                            CopyDirectory(stagingDir, _ytDlpDir);
                            TryDeleteDirectory(stagingDir);
                            return check.LatestVersion;
                        }
                    }

                    Directory.Move(stagingDir, _ytDlpDir);
                    TryDeleteDirectory(backupDir);
                }
                else
                {
                    var tempExe = Path.Combine(tempDir, "yt-dlp.exe");
                    await DownloadFileAsync(check.DownloadUrl, tempExe, progress, ct);
                    Directory.CreateDirectory(_ytDlpDir);
                    File.Copy(tempExe, Path.Combine(_ytDlpDir, "yt-dlp.exe"), overwrite: true);
                }

                AppLogger.Info($"yt-dlp installed/updated to {check.LatestVersion}");
                return check.LatestVersion;
            }
            finally
            {
                TryDeleteDirectory(tempDir);
            }
        }
        finally
        {
            _ytDlpLock.Release();
        }
    }

    public async Task<string> EnsureFfmpegAsync(IProgress<DownloadProgressInfo>? progress = null, CancellationToken ct = default)
    {
        var existing = FindFfmpegDirectory();
        if (existing is not null)
            return existing;

        await InstallFfmpegAsync(progress, ct);
        return FindFfmpegDirectory() ?? throw new InvalidOperationException("ffmpeg 安装完成但未找到可执行文件。");
    }

    public async Task InstallFfmpegAsync(IProgress<DownloadProgressInfo>? progress = null, CancellationToken ct = default)
    {
        await _ffmpegLock.WaitAsync(ct);
        try
        {
            var tempDir = Path.Combine(Path.GetTempPath(), $"vdl_ff_{Guid.NewGuid():N}");
            Directory.CreateDirectory(tempDir);

            try
            {
                var zipPath = Path.Combine(tempDir, "ffmpeg.zip");
                await DownloadFileAsync(FfmpegWinZipUrl, zipPath, progress, ct);

                var extractDir = Path.Combine(tempDir, "extracted");
                ZipFile.ExtractToDirectory(zipPath, extractDir, overwriteFiles: true);

                var ffmpegExe = Directory.EnumerateFiles(extractDir, "ffmpeg.exe", SearchOption.AllDirectories).FirstOrDefault()
                                ?? throw new InvalidOperationException("解压后未找到 ffmpeg.exe。");
                var ffprobeExe = Directory.EnumerateFiles(extractDir, "ffprobe.exe", SearchOption.AllDirectories).FirstOrDefault();

                Directory.CreateDirectory(_ffmpegDir);
                File.Copy(ffmpegExe, Path.Combine(_ffmpegDir, "ffmpeg.exe"), overwrite: true);
                if (ffprobeExe is not null)
                    File.Copy(ffprobeExe, Path.Combine(_ffmpegDir, "ffprobe.exe"), overwrite: true);

                AppLogger.Info($"ffmpeg installed to {_ffmpegDir}");
            }
            finally
            {
                TryDeleteDirectory(tempDir);
            }
        }
        finally
        {
            _ffmpegLock.Release();
        }
    }

    public async Task<string> EnsureAria2Async(IProgress<DownloadProgressInfo>? progress = null, CancellationToken ct = default)
    {
        var existing = FindAria2Executable();
        if (existing is not null)
            return existing;

        await InstallAria2Async(progress, ct);
        return FindAria2Executable() ?? throw new InvalidOperationException("aria2c 安装完成但未找到可执行文件。");
    }

    public async Task InstallAria2Async(IProgress<DownloadProgressInfo>? progress = null, CancellationToken ct = default)
    {
        await _aria2Lock.WaitAsync(ct);
        try
        {
            var url = await ResolveAria2DownloadUrlAsync(ct);
            var tempDir = Path.Combine(Path.GetTempPath(), $"vdl_aria2_{Guid.NewGuid():N}");
            Directory.CreateDirectory(tempDir);

            try
            {
                var zipPath = Path.Combine(tempDir, "aria2.zip");
                await DownloadFileAsync(url, zipPath, progress, ct);

                var extractDir = Path.Combine(tempDir, "extracted");
                ZipFile.ExtractToDirectory(zipPath, extractDir, overwriteFiles: true);

                var aria2Exe = Directory.EnumerateFiles(extractDir, "aria2c.exe", SearchOption.AllDirectories).FirstOrDefault()
                               ?? throw new InvalidOperationException("解压后未找到 aria2c.exe。");

                Directory.CreateDirectory(_aria2Dir);
                File.Copy(aria2Exe, Path.Combine(_aria2Dir, "aria2c.exe"), overwrite: true);
                AppLogger.Info($"aria2c installed to {_aria2Dir}");
            }
            finally
            {
                TryDeleteDirectory(tempDir);
            }
        }
        finally
        {
            _aria2Lock.Release();
        }
    }

    private static async Task<string> ResolveAria2DownloadUrlAsync(CancellationToken ct)
    {
        try
        {
            using var req = new HttpRequestMessage(HttpMethod.Get, Aria2LatestApi);
            req.Headers.Accept.ParseAdd("application/vnd.github+json");
            using var resp = await HttpClientProvider.Shared.SendAsync(req, ct);
            if (resp.IsSuccessStatusCode)
            {
                await using var stream = await resp.Content.ReadAsStreamAsync(ct);
                using var doc = await JsonDocument.ParseAsync(stream, cancellationToken: ct);
                if (doc.RootElement.TryGetProperty("assets", out var assets) && assets.ValueKind == JsonValueKind.Array)
                {
                    foreach (var asset in assets.EnumerateArray())
                    {
                        var name = asset.TryGetProperty("name", out var nEl) ? nEl.GetString() : null;
                        var dl = asset.TryGetProperty("browser_download_url", out var uEl) ? uEl.GetString() : null;
                        if (name is not null && dl is not null &&
                            name.Contains("win-64bit", StringComparison.OrdinalIgnoreCase) &&
                            name.EndsWith(".zip", StringComparison.OrdinalIgnoreCase))
                        {
                            return dl;
                        }
                    }
                }
            }
        }
        catch { }

        return Aria2FallbackUrl;
    }

    private static async Task DownloadFileAsync(
        string url,
        string destinationPath,
        IProgress<DownloadProgressInfo>? progress,
        CancellationToken ct)
    {
        using var resp = await HttpClientProvider.Shared.GetAsync(url, HttpCompletionOption.ResponseHeadersRead, ct);
        resp.EnsureSuccessStatusCode();

        long total = resp.Content.Headers.ContentLength ?? 0;
        await using var input = await resp.Content.ReadAsStreamAsync(ct);
        await using var output = new FileStream(destinationPath, FileMode.Create, FileAccess.Write, FileShare.None, 81920, useAsync: true);

        var buffer = new byte[81920];
        long downloaded = 0;
        long lastReportTick = Environment.TickCount64;

        int read;
        while ((read = await input.ReadAsync(buffer, ct)) > 0)
        {
            await output.WriteAsync(buffer.AsMemory(0, read), ct);
            downloaded += read;

            long now = Environment.TickCount64;
            if (now - lastReportTick >= 80)
            {
                progress?.Report(new DownloadProgressInfo(downloaded, total));
                lastReportTick = now;
            }
        }

        progress?.Report(new DownloadProgressInfo(downloaded, total));
    }

    private static string? FindOnPath(string fileName)
    {
        var pathEnv = Environment.GetEnvironmentVariable("PATH");
        if (string.IsNullOrEmpty(pathEnv))
            return null;

        foreach (var dir in pathEnv.Split(Path.PathSeparator, StringSplitOptions.RemoveEmptyEntries))
        {
            try
            {
                var candidate = Path.Combine(dir.Trim(), fileName);
                if (File.Exists(candidate))
                    return candidate;
            }
            catch { }
        }
        return null;
    }

    private static void CopyDirectory(string sourceDir, string targetDir)
    {
        Directory.CreateDirectory(targetDir);
        foreach (var file in Directory.EnumerateFiles(sourceDir))
            File.Copy(file, Path.Combine(targetDir, Path.GetFileName(file)), overwrite: true);
        foreach (var subDir in Directory.EnumerateDirectories(sourceDir))
            CopyDirectory(subDir, Path.Combine(targetDir, Path.GetFileName(subDir)));
    }

    private static void TryDeleteDirectory(string path)
    {
        try
        {
            if (Directory.Exists(path))
                Directory.Delete(path, recursive: true);
        }
        catch { }
    }
}
