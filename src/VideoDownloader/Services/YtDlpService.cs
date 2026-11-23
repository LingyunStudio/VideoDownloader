using System.Diagnostics;
using System.Globalization;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using VideoDownloader.Helpers;
using VideoDownloader.Models;

namespace VideoDownloader.Services;

public readonly record struct YtDlpDownloadUpdate(
    bool IsPostProcessing,
    long DownloadedBytes,
    long TotalBytes,
    double SpeedBytesPerSec,
    double? EtaSeconds,
    string StatusText,
    string? FinalFilePath,
    string? LogLine = null);

public sealed partial class YtDlpService
{
    [GeneratedRegex(@"\[#[0-9a-fA-F]+\s+([0-9.]+)([KMGTP]?i?B)/([0-9.]+)([KMGTP]?i?B)\((\d+)%\).*?DL:([0-9.]+)([KMGTP]?i?B)(?:\s+ETA:([0-9hms]+))?", RegexOptions.Compiled)]
    private static partial Regex Aria2ProgressRegex();
    private static readonly HashSet<string> SupportedBrowsers = new(StringComparer.OrdinalIgnoreCase)
    {
        "chrome", "firefox", "edge", "brave", "chromium", "opera", "vivaldi", "whale", "safari"
    };

    private readonly ToolManagerService _toolManager;

    public YtDlpService(ToolManagerService toolManager)
    {
        _toolManager = toolManager;
    }

    public static bool UrlContainsVideoAndList(string url)
    {
        if (string.IsNullOrWhiteSpace(url))
            return false;
        return url.Contains("list=", StringComparison.OrdinalIgnoreCase) &&
               (url.Contains("v=", StringComparison.OrdinalIgnoreCase) || url.Contains("youtu.be/", StringComparison.OrdinalIgnoreCase));
    }

    public static bool UrlHasPersonalOrMixList(string url)
    {
        if (string.IsNullOrWhiteSpace(url))
            return false;
        return url.Contains("list=LL", StringComparison.OrdinalIgnoreCase) ||
               url.Contains("list=WL", StringComparison.OrdinalIgnoreCase) ||
               url.Contains("list=RD", StringComparison.OrdinalIgnoreCase);
    }

    public async Task<VideoInfo> ExtractInfoAsync(
        string url,
        PlaylistParseMode playlistMode,
        string cookiesSource,
        string proxyUrl,
        string impersonate,
        bool forceIpv4,
        bool enableJsRuntimes,
        string videoPassword,
        string extraArguments,
        CancellationToken ct = default)
    {
        var ytDlpExe = _toolManager.FindYtDlpExecutable()
                       ?? throw new InvalidOperationException("未找到 yt-dlp 引擎，请等待自动安装完成或在「设置」页安装。");

        var trimmedUrl = url.Trim();
        var psi = CreateBaseStartInfo(ytDlpExe);
        psi.ArgumentList.Add("--dump-single-json");
        psi.ArgumentList.Add("--no-warnings");
        psi.ArgumentList.Add("--no-check-formats");

        // Determine playlist behavior cleanly
        var effectiveMode = playlistMode;
        if (effectiveMode == PlaylistParseMode.Auto && UrlContainsVideoAndList(trimmedUrl) && UrlHasPersonalOrMixList(trimmedUrl))
        {
            // Personal/Mix lists (LL/WL/RD) attached to a watch URL usually fail or explode to thousands of videos;
            // default to single video unless user explicitly requests FullPlaylist.
            effectiveMode = PlaylistParseMode.SingleVideoOnly;
        }

        if (effectiveMode == PlaylistParseMode.SingleVideoOnly)
        {
            psi.ArgumentList.Add("--no-playlist");
        }
        else if (effectiveMode == PlaylistParseMode.FullPlaylist)
        {
            psi.ArgumentList.Add("--yes-playlist");
            psi.ArgumentList.Add("--flat-playlist");
            psi.ArgumentList.Add("--ignore-errors");
        }
        else
        {
            psi.ArgumentList.Add("--flat-playlist");
        }

        if (enableJsRuntimes)
        {
            psi.ArgumentList.Add("--js-runtimes");
            psi.ArgumentList.Add("node");
            psi.ArgumentList.Add("--js-runtimes");
            psi.ArgumentList.Add("deno");
        }

        if (forceIpv4)
            psi.ArgumentList.Add("--force-ipv4");

        ApplyImpersonate(psi, impersonate);
        ApplyCookies(psi, cookiesSource);
        ApplyProxy(psi, proxyUrl);

        if (!string.IsNullOrWhiteSpace(videoPassword))
        {
            psi.ArgumentList.Add("--video-password");
            psi.ArgumentList.Add(videoPassword.Trim());
        }

        AppendExtraArguments(psi, extraArguments);
        psi.ArgumentList.Add(trimmedUrl);

        AppLogger.Info($"ExtractInfo start ({effectiveMode}): {trimmedUrl}");

        using var job = new ProcessJobObject();
        using var proc = new Process { StartInfo = psi };
        proc.Start();
        job.AssignProcess(proc);

        var stdoutTask = proc.StandardOutput.ReadToEndAsync(ct);
        var stderrTask = proc.StandardError.ReadToEndAsync(ct);

        using var reg = ct.Register(() =>
        {
            try { proc.Kill(entireProcessTree: true); } catch { }
        });

        await proc.WaitForExitAsync(ct);
        var stdout = await stdoutTask;
        var stderr = await stderrTask;

        ct.ThrowIfCancellationRequested();

        var cleanedJson = ExtractFirstValidJsonObject(stdout);
        if (cleanedJson is null)
        {
            var errMsg = BuildFriendlyError(stderr, trimmedUrl, cookiesSource);
            throw new InvalidOperationException(errMsg);
        }

        return ParseVideoInfoJson(cleanedJson, trimmedUrl);
    }

    public string BuildCommandPreview(DownloadRequest request)
    {
        var args = BuildDownloadArgumentList(request, forPreview: true);
        var sb = new StringBuilder("yt-dlp");
        foreach (var arg in args)
        {
            sb.Append(' ');
            if (arg.Contains(' ') || arg.Contains('&') || arg.Contains('"') || arg.Contains('%'))
                sb.Append('"').Append(arg.Replace("\"", "\\\"")).Append('"');
            else
                sb.Append(arg);
        }
        return sb.ToString();
    }

    public async Task<string> DownloadAsync(
        DownloadRequest request,
        Action<YtDlpDownloadUpdate> onUpdate,
        CancellationToken ct = default)
    {
        var ytDlpExe = _toolManager.FindYtDlpExecutable()
                       ?? throw new InvalidOperationException("未找到 yt-dlp 引擎。");

        Directory.CreateDirectory(request.OutputDirectory);

        var psi = CreateBaseStartInfo(ytDlpExe);
        var aria2Exe = _toolManager.FindAria2Executable();
        if (!string.IsNullOrEmpty(aria2Exe))
        {
            var aria2Dir = Path.GetDirectoryName(aria2Exe);
            if (!string.IsNullOrEmpty(aria2Dir))
            {
                var currentPath = Environment.GetEnvironmentVariable("PATH") ?? string.Empty;
                psi.Environment["PATH"] = aria2Dir + Path.PathSeparator + currentPath;
            }
        }
        foreach (var arg in BuildDownloadArgumentList(request, forPreview: false))
            psi.ArgumentList.Add(arg);

        AppLogger.Info($"Download start: {request.Url} | fmt={request.FormatSpec}");

        using var job = new ProcessJobObject();
        using var proc = new Process { StartInfo = psi };
        proc.Start();
        job.AssignProcess(proc);

        using var reg = ct.Register(() =>
        {
            try { proc.Kill(entireProcessTree: true); } catch { }
        });

        string finalFilePath = string.Empty;
        var errLines = new List<string>(32);

        var stderrTask = Task.Run(async () =>
        {
            while (await proc.StandardError.ReadLineAsync(ct) is { } line)
            {
                if (!string.IsNullOrWhiteSpace(line))
                {
                    if (errLines.Count < 40)
                        errLines.Add(line);
                    onUpdate(new YtDlpDownloadUpdate(false, 0, 0, 0, null, string.Empty, null, line));
                }
            }
        }, ct);

        long lastUiTick = 0;

        while (await proc.StandardOutput.ReadLineAsync(ct) is { } line)
        {
            if (line.StartsWith("VDL_DL|", StringComparison.Ordinal))
            {
                long now = Environment.TickCount64;
                var parts = line.Split('|');
                if (parts.Length >= 7)
                {
                    var status = parts[1];
                    if (status == "finished")
                    {
                        onUpdate(new YtDlpDownloadUpdate(true, 0, 0, 0, null, "正在合并与后期处理…", null));
                        lastUiTick = now;
                        continue;
                    }

                    // Throttle UI updates to ~10 FPS to keep CPU & GC minimal
                    if (now - lastUiTick < 100)
                        continue;
                    lastUiTick = now;

                    long dl = ParseLong(parts[2]);
                    long total = ParseLong(parts[3]);
                    if (total <= 0)
                        total = ParseLong(parts[4]);
                    double speed = ParseDouble(parts[5]);
                    double? eta = ParseNullableDouble(parts[6]);

                    onUpdate(new YtDlpDownloadUpdate(false, dl, total, speed, eta, "下载中…", null));
                }
            }
            else if (line.StartsWith("VDL_PP|", StringComparison.Ordinal))
            {
                onUpdate(new YtDlpDownloadUpdate(true, 0, 0, 0, null, "正在合并音视频 / 处理字幕与元数据…", null));
            }
            else if (line.StartsWith("VDL_FILE|", StringComparison.Ordinal))
            {
                var path = line["VDL_FILE|".Length..].Trim();
                if (!string.IsNullOrEmpty(path))
                {
                    finalFilePath = path;
                    onUpdate(new YtDlpDownloadUpdate(false, 0, 0, 0, null, "已完成", finalFilePath, $"输出文件: {path}"));
                }
            }
            else if (TryParseAria2Progress(line, out long aDl, out long aTotal, out double aSpeed, out double? aEta))
            {
                long now = Environment.TickCount64;
                if (now - lastUiTick >= 100)
                {
                    lastUiTick = now;
                    onUpdate(new YtDlpDownloadUpdate(false, aDl, aTotal, aSpeed, aEta, "aria2c 多线程极速下载中…", null));
                }
            }
            else if (!string.IsNullOrWhiteSpace(line))
            {
                onUpdate(new YtDlpDownloadUpdate(false, 0, 0, 0, null, string.Empty, null, line));
            }
        }

        await proc.WaitForExitAsync(ct);
        try { await stderrTask; } catch (OperationCanceledException) { }

        ct.ThrowIfCancellationRequested();

        if (proc.ExitCode != 0)
        {
            var errMsg = BuildFriendlyError(string.Join('\n', errLines), request.Url, request.CookiesSource);
            throw new InvalidOperationException(string.IsNullOrEmpty(errMsg) ? $"yt-dlp 退出异常（代码 {proc.ExitCode}）" : errMsg);
        }

        return finalFilePath;
    }

    private List<string> BuildDownloadArgumentList(DownloadRequest request, bool forPreview)
    {
        var args = new List<string>(32);
        var ffmpegDir = _toolManager.FindFfmpegDirectory();

        var outTemplate = Path.Combine(request.OutputDirectory,
            string.IsNullOrWhiteSpace(request.OutputTemplate)
                ? "%(title).100B [%(id)s].%(ext)s"
                : request.OutputTemplate);

        if (!forPreview)
        {
            args.Add("--newline");
            args.Add("--no-warnings");
            args.Add("--retries");
            args.Add("5");
            args.Add("--fragment-retries");
            args.Add("5");
            args.Add("--progress");
            args.Add("--progress-template");
            args.Add("download:VDL_DL|%(progress.status)s|%(progress.downloaded_bytes)s|%(progress.total_bytes)s|%(progress.total_bytes_estimate)s|%(progress.speed)s|%(progress.eta)s");
            args.Add("--progress-template");
            args.Add("postprocess:VDL_PP|%(progress.status)s|%(progress.postprocessor)s");
            args.Add("--print");
            args.Add("after_move:VDL_FILE|%(filepath)s");
        }

        args.Add("-o");
        args.Add(outTemplate);

        // Playlist handling
        if (request.PlaylistMode == PlaylistParseMode.SingleVideoOnly ||
            (request.PlaylistMode == PlaylistParseMode.Auto && UrlContainsVideoAndList(request.Url) && UrlHasPersonalOrMixList(request.Url)))
        {
            args.Add("--no-playlist");
        }
        else if (request.PlaylistMode == PlaylistParseMode.FullPlaylist)
        {
            args.Add("--yes-playlist");
            args.Add("--ignore-errors");
        }

        if (!string.IsNullOrWhiteSpace(request.PlaylistItems))
        {
            args.Add("-I");
            args.Add(request.PlaylistItems.Trim());
        }

        if (request.PlaylistReverse)
            args.Add("--playlist-reverse");

        if (request.UseArchive)
        {
            var archivePath = string.IsNullOrWhiteSpace(request.ArchiveFilePath)
                ? Path.Combine(AppLogger.AppDataDirectory, "download_archive.txt")
                : request.ArchiveFilePath;
            args.Add("--download-archive");
            args.Add(archivePath);
        }

        if (request.NoMtime)
            args.Add("--no-mtime");

        if (!string.IsNullOrEmpty(ffmpegDir) && !forPreview)
        {
            args.Add("--ffmpeg-location");
            args.Add(ffmpegDir);
        }

        if (request.EnableJsRuntimes)
        {
            args.Add("--js-runtimes");
            args.Add("node");
            args.Add("--js-runtimes");
            args.Add("deno");
        }

        if (request.ConcurrentFragments > 1)
        {
            args.Add("-N");
            args.Add(Math.Clamp(request.ConcurrentFragments, 1, 16).ToString(CultureInfo.InvariantCulture));
        }

        // Auto-recover when YouTube throttles a connection below 100 KB/s
        args.Add("--throttled-rate");
        args.Add("100K");

        // Multi-thread HTTP/HTTPS acceleration via aria2c (leaves HLS/DASH to native -N, skips clip/live)
        bool canUseAria2 = request.UseAria2Acceleration
                           && string.IsNullOrWhiteSpace(request.SectionRange)
                           && !request.LiveFromStart
                           && (forPreview || _toolManager.IsAria2Ready);

        if (canUseAria2)
        {
            int conn = Math.Clamp(request.Aria2Connections, 1, 16);
            var ariaArgs = $"-x {conn} -s {conn} -k 1M --file-allocation=none --console-log-level=warn --summary-interval=1 --auto-file-renaming=false";
            if (!string.IsNullOrWhiteSpace(request.RateLimit))
                ariaArgs += $" --max-download-limit={request.RateLimit.Trim()}";

            args.Add("--downloader");
            args.Add("http,https:aria2c");
            args.Add("--downloader-args");
            args.Add($"aria2c:{ariaArgs}");
        }
        else
        {
            // 10 MB Range chunks help bypass YouTube single-stream throttling on native downloader
            args.Add("--http-chunk-size");
            args.Add("10M");
        }

        if (!string.IsNullOrWhiteSpace(request.RateLimit))
        {
            args.Add("-r");
            args.Add(request.RateLimit.Trim());
        }

        if (request.ForceIpv4)
            args.Add("-4");

        // Format / Audio / Container
        if (request.AudioOnly)
        {
            args.Add("-f");
            args.Add(string.IsNullOrWhiteSpace(request.FormatSpec) ? "ba/b" : request.FormatSpec);
            args.Add("-x");
            if (!string.IsNullOrWhiteSpace(request.AudioFormat) && !request.AudioFormat.Equals("best", StringComparison.OrdinalIgnoreCase))
            {
                args.Add("--audio-format");
                args.Add(request.AudioFormat);
                args.Add("--audio-quality");
                args.Add("0");
            }
        }
        else
        {
            if (!string.IsNullOrWhiteSpace(request.FormatSpec))
            {
                args.Add("-f");
                args.Add(request.FormatSpec);
            }

            if (!string.IsNullOrWhiteSpace(request.FormatSort))
            {
                args.Add("-S");
                args.Add(request.FormatSort.Trim());
            }

            if (!string.IsNullOrWhiteSpace(request.Container) &&
                !request.Container.Equals("auto", StringComparison.OrdinalIgnoreCase))
            {
                args.Add("--merge-output-format");
                args.Add(request.Container);
                if (request.RemuxVideo)
                {
                    args.Add("--remux-video");
                    args.Add(request.Container);
                }
            }
        }

        // Subtitles
        if (request.DownloadSubtitles || request.DownloadAutoSubtitles)
        {
            if (request.DownloadSubtitles)
                args.Add("--write-subs");
            if (request.DownloadAutoSubtitles)
                args.Add("--write-auto-subs");

            if (!string.IsNullOrWhiteSpace(request.SubtitleLangs))
            {
                args.Add("--sub-langs");
                args.Add(request.SubtitleLangs.Trim());
            }

            if (!string.IsNullOrWhiteSpace(request.ConvertSubtitles) &&
                !request.ConvertSubtitles.Equals("none", StringComparison.OrdinalIgnoreCase))
            {
                args.Add("--convert-subs");
                args.Add(request.ConvertSubtitles.Trim());
            }

            if (request.EmbedSubtitles)
                args.Add("--embed-subs");
        }

        // Thumbnail, Metadata & Chapters
        if (request.EmbedThumbnail)
            args.Add("--embed-thumbnail");
        if (request.WriteThumbnail)
            args.Add("--write-thumbnail");
        if (request.EmbedMetadata)
            args.Add("--add-metadata");
        if (request.EmbedChapters)
            args.Add("--embed-chapters");
        if (request.SplitChapters)
            args.Add("--split-chapters");

        // SponsorBlock
        if (request.SponsorBlockMode.Equals("remove", StringComparison.OrdinalIgnoreCase))
        {
            args.Add("--sponsorblock-remove");
            args.Add(string.IsNullOrWhiteSpace(request.SponsorBlockCategories) ? "default" : request.SponsorBlockCategories);
        }
        else if (request.SponsorBlockMode.Equals("mark", StringComparison.OrdinalIgnoreCase))
        {
            args.Add("--sponsorblock-mark");
            args.Add(string.IsNullOrWhiteSpace(request.SponsorBlockCategories) ? "default" : request.SponsorBlockCategories);
        }

        // Clip & Live
        if (!string.IsNullOrWhiteSpace(request.SectionRange))
        {
            args.Add("--download-sections");
            args.Add("*" + request.SectionRange.Trim().TrimStart('*'));
            if (request.ForceKeyframesAtCuts)
                args.Add("--force-keyframes-at-cuts");
        }

        if (request.LiveFromStart)
            args.Add("--live-from-start");

        // Auth, Impersonate, Proxy, Extra
        if (!string.IsNullOrWhiteSpace(request.Impersonate) &&
            !request.Impersonate.Equals("none", StringComparison.OrdinalIgnoreCase))
        {
            args.Add("--impersonate");
            args.Add(request.Impersonate.Trim());
        }

        AppendCookiesArgs(args, request.CookiesSource);

        if (!string.IsNullOrWhiteSpace(request.ProxyUrl))
        {
            args.Add("--proxy");
            args.Add(request.ProxyUrl.Trim());
        }

        if (!string.IsNullOrWhiteSpace(request.VideoPassword))
        {
            args.Add("--video-password");
            args.Add(request.VideoPassword.Trim());
        }

        foreach (var token in SplitCommandLineArguments(request.ExtraArguments))
            args.Add(token);

        args.Add(request.Url.Trim());
        return args;
    }

    private static ProcessStartInfo CreateBaseStartInfo(string exePath)
    {
        var psi = new ProcessStartInfo
        {
            FileName = exePath,
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8
        };
        psi.Environment["PYTHONUTF8"] = "1";
        psi.Environment["PYTHONIOENCODING"] = "utf-8";
        return psi;
    }

    private static void ApplyImpersonate(ProcessStartInfo psi, string impersonate)
    {
        if (!string.IsNullOrWhiteSpace(impersonate) &&
            !impersonate.Equals("none", StringComparison.OrdinalIgnoreCase))
        {
            psi.ArgumentList.Add("--impersonate");
            psi.ArgumentList.Add(impersonate.Trim());
        }
    }

    private static void ApplyCookies(ProcessStartInfo psi, string cookiesSource)
    {
        var list = new List<string>(2);
        AppendCookiesArgs(list, cookiesSource);
        foreach (var item in list)
            psi.ArgumentList.Add(item);
    }

    private static void AppendCookiesArgs(List<string> args, string cookiesSource)
    {
        if (string.IsNullOrWhiteSpace(cookiesSource))
            return;

        var src = cookiesSource.Trim();
        if (src.Equals("none", StringComparison.OrdinalIgnoreCase) || src == "不使用")
            return;

        // Support browser[:profile][::container] syntax (e.g. "chrome:Profile 1", "firefox", "edge:Default")
        var browserPart = src.Split([':', '+'], 2)[0];
        if (SupportedBrowsers.Contains(browserPart))
        {
            args.Add("--cookies-from-browser");
            args.Add(src);
        }
        else if (File.Exists(src))
        {
            args.Add("--cookies");
            args.Add(src);
        }
    }

    private static void ApplyProxy(ProcessStartInfo psi, string proxyUrl)
    {
        if (!string.IsNullOrWhiteSpace(proxyUrl))
        {
            psi.ArgumentList.Add("--proxy");
            psi.ArgumentList.Add(proxyUrl.Trim());
        }
    }

    private static void AppendExtraArguments(ProcessStartInfo psi, string extraArgs)
    {
        foreach (var token in SplitCommandLineArguments(extraArgs))
            psi.ArgumentList.Add(token);
    }

    public static List<string> SplitCommandLineArguments(string? commandLine)
    {
        var result = new List<string>();
        if (string.IsNullOrWhiteSpace(commandLine))
            return result;

        var current = new StringBuilder();
        bool inQuotes = false;
        char quoteChar = '\0';

        foreach (char ch in commandLine)
        {
            if (inQuotes)
            {
                if (ch == quoteChar)
                {
                    inQuotes = false;
                }
                else
                {
                    current.Append(ch);
                }
            }
            else if (ch is '"' or '\'')
            {
                inQuotes = true;
                quoteChar = ch;
            }
            else if (char.IsWhiteSpace(ch))
            {
                if (current.Length > 0)
                {
                    result.Add(current.ToString());
                    current.Clear();
                }
            }
            else
            {
                current.Append(ch);
            }
        }

        if (current.Length > 0)
            result.Add(current.ToString());

        return result;
    }

    private static string? ExtractFirstValidJsonObject(string? stdout)
    {
        if (string.IsNullOrWhiteSpace(stdout))
            return null;

        var trimmed = stdout.Trim();
        if (trimmed.Equals("null", StringComparison.OrdinalIgnoreCase))
            return null;

        if (trimmed.StartsWith('{'))
            return trimmed;

        // Multi-line fallback: find first JSON object line
        foreach (var line in trimmed.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
        {
            if (line.StartsWith('{') && line.EndsWith('}'))
                return line;
        }

        return null;
    }

    private static string BuildFriendlyError(string stderr, string url, string cookiesSource)
    {
        var rawErr = ExtractReadableError(stderr);

        if (stderr.Contains("Sign in to confirm", StringComparison.OrdinalIgnoreCase) ||
            stderr.Contains("confirm you're not a bot", StringComparison.OrdinalIgnoreCase) ||
            stderr.Contains("confirm you’re not a bot", StringComparison.OrdinalIgnoreCase))
        {
            return "YouTube 触发了人机验证（需要登录态）。推荐点击右侧「网页登录」在内置浏览器登录 YouTube 后一键提取 Cookies（可完全绕过 Chrome/Edge 加密限制）。";
        }

        if (stderr.Contains("Could not copy Chrome cookie database", StringComparison.OrdinalIgnoreCase) ||
            stderr.Contains("Failed to decrypt with DPAPI", StringComparison.OrdinalIgnoreCase))
        {
            return "Windows 新版 Chrome/Edge 启用了数据库锁定与 App-Bound 加密，外部程序无法直接解密其 Cookies。请点击「网页登录」使用内置浏览器一键提取，或导入 cookies.txt。";
        }

        if (stderr.Contains("could not find", StringComparison.OrdinalIgnoreCase) &&
            stderr.Contains("cookies", StringComparison.OrdinalIgnoreCase))
        {
            return $"未找到指定浏览器（{cookiesSource}）的 Cookies 数据库。建议切回「内置网页登录」或「不使用 Cookies」。";
        }

        if (stderr.Contains("Private video", StringComparison.OrdinalIgnoreCase) ||
            stderr.Contains("This playlist type is unviewable", StringComparison.OrdinalIgnoreCase) ||
            (url.Contains("list=LL", StringComparison.OrdinalIgnoreCase) && string.IsNullOrEmpty(rawErr)))
        {
            return "该视频或播放列表（如 list=LL 赞过的视频）为私有内容。请点击「网页登录」登录对应账号提取 Cookies，或切换为「仅当前视频」。";
        }

        if (stderr.Contains("Unsupported URL", StringComparison.OrdinalIgnoreCase))
        {
            return $"不支持该链接格式：{rawErr}";
        }

        return string.IsNullOrEmpty(rawErr) ? "未能提取到任何视频信息，请检查链接、网络代理或 Cookies 设置。" : rawErr;
    }

    private static VideoInfo ParseVideoInfoJson(string json, string fallbackUrl)
    {
        using var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;
        if (root.ValueKind != JsonValueKind.Object)
            throw new InvalidOperationException("yt-dlp 返回了无效的 JSON 结构。");

        var title = GetString(root, "title") ?? GetString(root, "id") ?? "(未知标题)";
        var uploader = GetString(root, "uploader") ?? GetString(root, "channel") ?? string.Empty;
        var duration = GetDouble(root, "duration") ?? 0;
        var thumbnail = GetString(root, "thumbnail") ?? string.Empty;
        var webpageUrl = GetString(root, "webpage_url") ?? GetString(root, "original_url") ?? fallbackUrl;
        var extractor = GetString(root, "extractor_key") ?? GetString(root, "extractor") ?? string.Empty;
        var videoId = GetString(root, "id") ?? string.Empty;
        var viewCount = GetLong(root, "view_count");
        var likeCount = GetLong(root, "like_count");
        var uploadDate = GetString(root, "upload_date") ?? string.Empty;
        var description = GetString(root, "description") ?? string.Empty;
        var bestFormatId = GetString(root, "format_id") ?? string.Empty;
        var isLive = root.TryGetProperty("is_live", out var liveEl) && liveEl.ValueKind == JsonValueKind.True;

        int chapterCount = 0;
        if (root.TryGetProperty("chapters", out var chaptersEl) && chaptersEl.ValueKind == JsonValueKind.Array)
            chapterCount = chaptersEl.GetArrayLength();

        var subLangs = new List<string>();
        CollectSubtitleLangs(root, "subtitles", subLangs);
        CollectSubtitleLangs(root, "automatic_captions", subLangs);

        // Check playlist
        if (root.TryGetProperty("entries", out var entriesEl) && entriesEl.ValueKind == JsonValueKind.Array)
        {
            var playlistItems = new List<PlaylistEntryItem>();
            int idx = 1;
            foreach (var entry in entriesEl.EnumerateArray())
            {
                if (entry.ValueKind != JsonValueKind.Object)
                    continue;

                var eId = GetString(entry, "id") ?? string.Empty;
                var eTitle = GetString(entry, "title") ?? eId;
                var eUrl = GetString(entry, "webpage_url") ?? GetString(entry, "url") ?? string.Empty;
                var eDur = GetDouble(entry, "duration") ?? 0;
                var eUp = GetString(entry, "uploader") ?? GetString(entry, "channel") ?? string.Empty;

                if (string.IsNullOrEmpty(thumbnail))
                {
                    thumbnail = GetString(entry, "thumbnail") ?? string.Empty;
                    if (string.IsNullOrEmpty(thumbnail) &&
                        entry.TryGetProperty("thumbnails", out var thumbs) &&
                        thumbs.ValueKind == JsonValueKind.Array &&
                        thumbs.GetArrayLength() > 0)
                    {
                        thumbnail = GetString(thumbs[thumbs.GetArrayLength() - 1], "url") ?? string.Empty;
                    }
                }

                playlistItems.Add(new PlaylistEntryItem
                {
                    Index = idx++,
                    Id = eId,
                    Title = eTitle,
                    Url = eUrl,
                    Duration = eDur,
                    Uploader = eUp
                });
            }

            return new VideoInfo
            {
                Title = title,
                Uploader = uploader,
                Duration = duration,
                Thumbnail = thumbnail,
                WebpageUrl = webpageUrl,
                Extractor = extractor,
                VideoId = videoId,
                ViewCount = viewCount,
                LikeCount = likeCount,
                UploadDate = uploadDate,
                Description = description,
                IsPlaylist = true,
                PlaylistCount = playlistItems.Count,
                PlaylistEntries = playlistItems,
                BestFormatId = bestFormatId
            };
        }

        var formats = new List<FormatOption>();
        if (root.TryGetProperty("formats", out var fmtsEl) && fmtsEl.ValueKind == JsonValueKind.Array)
        {
            foreach (var f in fmtsEl.EnumerateArray())
            {
                if (f.ValueKind != JsonValueKind.Object)
                    continue;

                var vcodec = GetString(f, "vcodec") ?? string.Empty;
                var acodec = GetString(f, "acodec") ?? string.Empty;
                bool hasVideo = !string.IsNullOrEmpty(vcodec) && !vcodec.Equals("none", StringComparison.OrdinalIgnoreCase);
                bool hasAudio = !string.IsNullOrEmpty(acodec) && !acodec.Equals("none", StringComparison.OrdinalIgnoreCase);

                if (!hasVideo && !hasAudio)
                    continue;

                var ext = GetString(f, "ext") ?? string.Empty;
                if (ext.Equals("mhtml", StringComparison.OrdinalIgnoreCase))
                    continue;

                formats.Add(new FormatOption
                {
                    FormatId = GetString(f, "format_id") ?? string.Empty,
                    Ext = ext,
                    Width = GetInt(f, "width"),
                    Height = GetInt(f, "height"),
                    Fps = GetDouble(f, "fps"),
                    VCodec = vcodec,
                    ACodec = acodec,
                    Tbr = GetDouble(f, "tbr") ?? GetDouble(f, "abr") ?? GetDouble(f, "vbr"),
                    FileSize = GetLong(f, "filesize"),
                    FileSizeApprox = GetLong(f, "filesize_approx"),
                    Note = GetString(f, "format_note") ?? string.Empty,
                    HasVideo = hasVideo,
                    HasAudio = hasAudio
                });
            }
        }

        MarkRecommendedFormats(formats, bestFormatId);

        return new VideoInfo
        {
            Title = title,
            Uploader = uploader,
            Duration = duration,
            Thumbnail = thumbnail,
            WebpageUrl = webpageUrl,
            Extractor = extractor,
            VideoId = videoId,
            ViewCount = viewCount,
            LikeCount = likeCount,
            UploadDate = uploadDate,
            Description = description,
            IsLive = isLive,
            IsPlaylist = false,
            BestFormatId = bestFormatId,
            Formats = formats,
            AvailableSubtitleLangs = subLangs,
            ChapterCount = chapterCount
        };
    }

    private static void CollectSubtitleLangs(JsonElement root, string prop, List<string> target)
    {
        if (!root.TryGetProperty(prop, out var el) || el.ValueKind != JsonValueKind.Object)
            return;

        foreach (var item in el.EnumerateObject())
        {
            if (!target.Contains(item.Name, StringComparer.OrdinalIgnoreCase))
                target.Add(item.Name);
        }
    }

    private static void MarkRecommendedFormats(List<FormatOption> formats, string bestFormatId)
    {
        var bestIds = new HashSet<string>(
            bestFormatId.Split('+', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries),
            StringComparer.OrdinalIgnoreCase);

        foreach (var f in formats)
        {
            if (bestIds.Contains(f.FormatId))
                f.IsRecommended = true;
        }

        var bestVideo = formats.Where(f => f.Group == FormatGroup.VideoOnly)
            .OrderByDescending(f => f.Height ?? 0)
            .ThenByDescending(f => f.Tbr ?? 0)
            .FirstOrDefault();
        if (bestVideo is not null && !formats.Any(f => f.Group == FormatGroup.VideoOnly && f.IsRecommended))
            bestVideo.IsRecommended = true;

        var bestAudio = formats.Where(f => f.Group == FormatGroup.AudioOnly)
            .OrderByDescending(f => f.Tbr ?? 0)
            .FirstOrDefault();
        if (bestAudio is not null && !formats.Any(f => f.Group == FormatGroup.AudioOnly && f.IsRecommended))
            bestAudio.IsRecommended = true;

        var bestCombined = formats.Where(f => f.Group == FormatGroup.Combined)
            .OrderByDescending(f => f.Height ?? 0)
            .ThenByDescending(f => f.Tbr ?? 0)
            .FirstOrDefault();
        if (bestCombined is not null && !formats.Any(f => f.Group == FormatGroup.Combined && f.IsRecommended))
            bestCombined.IsRecommended = true;
    }

    private static string ExtractReadableError(string stderr)
    {
        if (string.IsNullOrWhiteSpace(stderr))
            return string.Empty;

        var lines = stderr.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        var errLine = lines.LastOrDefault(l => l.StartsWith("ERROR:", StringComparison.OrdinalIgnoreCase))
                      ?? lines.LastOrDefault()
                      ?? string.Empty;
        return errLine.Replace("ERROR:", "", StringComparison.OrdinalIgnoreCase).Trim();
    }

    private static string? GetString(JsonElement el, string prop)
    {
        if (el.ValueKind != JsonValueKind.Object || !el.TryGetProperty(prop, out var v))
            return null;
        return v.ValueKind switch
        {
            JsonValueKind.String => v.GetString(),
            JsonValueKind.Number => v.GetRawText(),
            _ => null
        };
    }

    private static int? GetInt(JsonElement el, string prop)
    {
        if (el.ValueKind != JsonValueKind.Object || !el.TryGetProperty(prop, out var v) || v.ValueKind != JsonValueKind.Number)
            return null;
        return v.TryGetInt32(out var i) ? i : (int?)Math.Round(v.GetDouble());
    }

    private static long? GetLong(JsonElement el, string prop)
    {
        if (el.ValueKind != JsonValueKind.Object || !el.TryGetProperty(prop, out var v) || v.ValueKind != JsonValueKind.Number)
            return null;
        return v.TryGetInt64(out var l) ? l : (long?)Math.Round(v.GetDouble());
    }

    private static double? GetDouble(JsonElement el, string prop)
    {
        if (el.ValueKind != JsonValueKind.Object || !el.TryGetProperty(prop, out var v) || v.ValueKind != JsonValueKind.Number)
            return null;
        return v.TryGetDouble(out var d) ? d : null;
    }

    private static long ParseLong(string s)
    {
        if (long.TryParse(s, NumberStyles.Integer, CultureInfo.InvariantCulture, out var val))
            return val;
        if (double.TryParse(s, NumberStyles.Float, CultureInfo.InvariantCulture, out var d) && !double.IsNaN(d))
            return (long)d;
        return 0;
    }

    private static double ParseDouble(string s) =>
        double.TryParse(s, NumberStyles.Float, CultureInfo.InvariantCulture, out var d) && !double.IsNaN(d) ? d : 0;

    private static double? ParseNullableDouble(string s) =>
        double.TryParse(s, NumberStyles.Float, CultureInfo.InvariantCulture, out var d) && !double.IsNaN(d) ? d : null;

    private static bool TryParseAria2Progress(string line, out long downloaded, out long total, out double speed, out double? eta)
    {
        downloaded = 0;
        total = 0;
        speed = 0;
        eta = null;

        if (!line.Contains("[#", StringComparison.Ordinal) || !line.Contains("DL:", StringComparison.Ordinal))
            return false;

        var m = Aria2ProgressRegex().Match(line);
        if (!m.Success)
            return false;

        downloaded = (long)ParseHumanBytes(m.Groups[1].Value, m.Groups[2].Value);
        total = (long)ParseHumanBytes(m.Groups[3].Value, m.Groups[4].Value);
        speed = ParseHumanBytes(m.Groups[6].Value, m.Groups[7].Value);

        if (m.Groups[8].Success)
            eta = ParseAria2EtaSeconds(m.Groups[8].Value);

        return true;
    }

    private static double ParseHumanBytes(string numberText, string unit)
    {
        if (!double.TryParse(numberText, NumberStyles.Float, CultureInfo.InvariantCulture, out double val))
            return 0;

        return unit.ToUpperInvariant() switch
        {
            "KIB" or "KB" => val * 1024.0,
            "MIB" or "MB" => val * 1024.0 * 1024.0,
            "GIB" or "GB" => val * 1024.0 * 1024.0 * 1024.0,
            "TIB" or "TB" => val * 1024.0 * 1024.0 * 1024.0 * 1024.0,
            _ => val
        };
    }

    private static double? ParseAria2EtaSeconds(string text)
    {
        double totalSec = 0;
        double current = 0;
        foreach (char ch in text)
        {
            if (ch is >= '0' and <= '9')
            {
                current = current * 10 + (ch - '0');
            }
            else if (ch == 'h') { totalSec += current * 3600; current = 0; }
            else if (ch == 'm') { totalSec += current * 60; current = 0; }
            else if (ch == 's') { totalSec += current; current = 0; }
        }
        return totalSec > 0 ? totalSec : null;
    }
}
