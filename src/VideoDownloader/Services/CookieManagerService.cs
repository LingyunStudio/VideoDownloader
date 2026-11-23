using System.Text;
using VideoDownloader.Helpers;

namespace VideoDownloader.Services;

public sealed record CookieSourceChoice(string Key, string DisplayName, string Description);

public readonly record struct CookieFileInspection(
    bool Exists,
    int TotalCookies,
    bool HasYouTubeAuth,
    bool HasBilibiliAuth,
    DateTime? LastUpdated)
{
    public string StatusSummary
    {
        get
        {
            if (!Exists || TotalCookies == 0)
                return "尚未提取 Cookies，点击右侧「网页登录」一次登录即可长期使用";

            var sites = new List<string>(3);
            if (HasYouTubeAuth) sites.Add("YouTube ✓");
            if (HasBilibiliAuth) sites.Add("Bilibili ✓");
            var siteText = sites.Count > 0 ? $"（{string.Join(" · ", sites)}）" : string.Empty;
            return $"已就绪 · {TotalCookies} 条记录{siteText}";
        }
    }
}

/// <summary>
/// Manages all cookie sources:
/// 1) Built-in WebView2 login (exports standard Netscape cookies.txt via CoreWebView2CookieManager,
///    completely bypassing Chrome/Edge App-Bound Encryption and SQLite database locks).
/// 2) Auto-detected local browser profiles (Firefox profiles, Edge, Chrome, Brave).
/// 3) User-imported Netscape cookies.txt files.
/// </summary>
public sealed class CookieManagerService
{
    public const string BuiltinSourceKey = "builtin";
    public const string NoneSourceKey = "none";

    private readonly string _cookiesDir;
    private readonly string _webViewProfileDir;

    public CookieManagerService()
    {
        _cookiesDir = Path.Combine(AppLogger.AppDataDirectory, "cookies");
        _webViewProfileDir = Path.Combine(AppLogger.AppDataDirectory, "webview2_profile");
        Directory.CreateDirectory(_cookiesDir);
        Directory.CreateDirectory(_webViewProfileDir);
    }

    public string BuiltinCookieFilePath => Path.Combine(_cookiesDir, "builtin_cookies.txt");
    public string WebView2ProfileDirectory => _webViewProfileDir;

    /// <summary>
    /// Resolves a UI cookie source key ("builtin", "none", "firefox", "firefox:profile", or file path)
    /// into the actual value passed to YtDlpService.
    /// </summary>
    public string ResolveForYtDlp(string? sourceKey)
    {
        if (string.IsNullOrWhiteSpace(sourceKey))
            return string.Empty;

        var trimmed = sourceKey.Trim();
        if (trimmed.Equals(NoneSourceKey, StringComparison.OrdinalIgnoreCase))
            return string.Empty;

        if (trimmed.Equals(BuiltinSourceKey, StringComparison.OrdinalIgnoreCase))
            return File.Exists(BuiltinCookieFilePath) ? BuiltinCookieFilePath : string.Empty;

        return trimmed;
    }

    public CookieFileInspection InspectBuiltinCookies() => InspectCookieFile(BuiltinCookieFilePath);

    public CookieFileInspection InspectCookieFile(string? path)
    {
        if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
            return new CookieFileInspection(false, 0, false, false, null);

        int count = 0;
        bool hasYt = false;
        bool hasBili = false;

        try
        {
            foreach (var line in File.ReadLines(path))
            {
                if (string.IsNullOrWhiteSpace(line) || line.StartsWith('#'))
                    continue;

                var cols = line.Split('\t');
                if (cols.Length < 7)
                    continue;

                count++;
                var domain = cols[0];
                var name = cols[5];

                if ((domain.Contains("youtube.com", StringComparison.OrdinalIgnoreCase) ||
                     domain.Contains("google.com", StringComparison.OrdinalIgnoreCase)) &&
                    (name.Equals("SAPISID", StringComparison.Ordinal) ||
                     name.Equals("__Secure-3PAPISID", StringComparison.Ordinal) ||
                     name.Equals("LOGIN_INFO", StringComparison.Ordinal)))
                {
                    hasYt = true;
                }

                if (domain.Contains("bilibili.com", StringComparison.OrdinalIgnoreCase) &&
                    name.Equals("SESSDATA", StringComparison.OrdinalIgnoreCase))
                {
                    hasBili = true;
                }
            }

            return new CookieFileInspection(true, count, hasYt, hasBili, File.GetLastWriteTime(path));
        }
        catch (Exception ex)
        {
            AppLogger.Warn($"Failed to inspect cookie file {path}: {ex.Message}");
            return new CookieFileInspection(false, 0, false, false, null);
        }
    }

    /// <summary>
    /// Writes cookies extracted from CoreWebView2CookieManager into standard Netscape HTTP Cookie File format.
    /// </summary>
    public CookieFileInspection SaveNetscapeCookies(
        IEnumerable<(string Domain, string Path, bool IsSecure, double ExpiresUnixSeconds, string Name, string Value, bool IsSession)> cookies)
    {
        var sb = new StringBuilder(16384);
        sb.AppendLine("# Netscape HTTP Cookie File");
        sb.AppendLine("# Generated by VideoDownloader built-in WebView2 login");
        sb.AppendLine();

        foreach (var c in cookies)
        {
            if (string.IsNullOrWhiteSpace(c.Domain) || string.IsNullOrWhiteSpace(c.Name))
                continue;

            var domain = c.Domain.Trim();
            var includeSubdomains = domain.StartsWith('.') ? "TRUE" : "FALSE";
            var path = string.IsNullOrEmpty(c.Path) ? "/" : c.Path;
            var secure = c.IsSecure ? "TRUE" : "FALSE";

            long expiry = 0;
            if (!c.IsSession && !double.IsNaN(c.ExpiresUnixSeconds) && !double.IsInfinity(c.ExpiresUnixSeconds) && c.ExpiresUnixSeconds > 0)
            {
                expiry = (long)Math.Floor(c.ExpiresUnixSeconds);
            }

            // Sanitize newlines/tabs in cookie values to keep Netscape format strictly valid
            var val = c.Value.Replace("\r", "").Replace("\n", "").Replace("\t", " ");
            sb.Append(domain).Append('\t')
              .Append(includeSubdomains).Append('\t')
              .Append(path).Append('\t')
              .Append(secure).Append('\t')
              .Append(expiry).Append('\t')
              .Append(c.Name).Append('\t')
              .Append(val).Append('\n');
        }

        Directory.CreateDirectory(_cookiesDir);
        File.WriteAllText(BuiltinCookieFilePath, sb.ToString(), new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));

        var result = InspectBuiltinCookies();
        AppLogger.Info($"Saved built-in WebView2 cookies: {result.TotalCookies} entries (YT={result.HasYouTubeAuth}, Bili={result.HasBilibiliAuth})");
        return result;
    }

    public void ClearBuiltinCookies()
    {
        try
        {
            if (File.Exists(BuiltinCookieFilePath))
                File.Delete(BuiltinCookieFilePath);
        }
        catch (Exception ex)
        {
            AppLogger.Warn($"Failed to delete builtin cookies: {ex.Message}");
        }
    }

    /// <summary>
    /// Builds the recommended list of cookie sources by auto-detecting local installed browsers & Firefox profiles.
    /// </summary>
    public List<CookieSourceChoice> DiscoverAvailableSources()
    {
        var list = new List<CookieSourceChoice>
        {
            new(BuiltinSourceKey, "内置网页登录（推荐）", "使用应用内置浏览器登录提取，绕过 Chrome/Edge 加密与锁库"),
            new(NoneSourceKey, "不使用 Cookies", "仅适用于无需登录的公开视频")
        };

        // Detect Firefox profiles (most reliable external browser on Windows because it does not use App-Bound Encryption)
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
        var ffProfilesDir = Path.Combine(appData, "Mozilla", "Firefox", "Profiles");
        if (Directory.Exists(ffProfilesDir))
        {
            var profileDirs = Directory.EnumerateDirectories(ffProfilesDir)
                .Where(d => File.Exists(Path.Combine(d, "cookies.sqlite")))
                .Select(Path.GetFileName)
                .Where(n => !string.IsNullOrEmpty(n))
                .ToList();

            if (profileDirs.Count > 0)
            {
                list.Add(new CookieSourceChoice("firefox", "Firefox（默认配置文件）", "直接读取本机 Firefox Cookies"));
                if (profileDirs.Count > 1)
                {
                    foreach (var prof in profileDirs)
                        list.Add(new CookieSourceChoice($"firefox:{prof}", $"Firefox · {prof}", "指定 Firefox 配置文件"));
                }
            }
        }

        // Detect Chromium-based browsers (note: newer Windows Chrome/Edge use App-Bound Encryption & file locks)
        var localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        if (Directory.Exists(Path.Combine(localAppData, "Microsoft", "Edge", "User Data")))
            list.Add(new CookieSourceChoice("edge", "Edge（可能受系统加密限制）", "若读取失败请改用「内置网页登录」"));

        if (Directory.Exists(Path.Combine(localAppData, "Google", "Chrome", "User Data")))
            list.Add(new CookieSourceChoice("chrome", "Chrome（可能受加密/锁库限制）", "若读取失败请改用「内置网页登录」"));

        if (Directory.Exists(Path.Combine(localAppData, "BraveSoftware", "Brave-Browser", "User Data")))
            list.Add(new CookieSourceChoice("brave", "Brave 浏览器", "尝试读取本机 Brave Cookies"));

        return list;
    }
}
