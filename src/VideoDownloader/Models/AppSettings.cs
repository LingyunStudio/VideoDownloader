using VideoDownloader.Helpers;

namespace VideoDownloader.Models;

public sealed class HistoryEntry
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..10];
    public string Title { get; set; } = string.Empty;
    public string Url { get; set; } = string.Empty;
    public string ThumbnailUrl { get; set; } = string.Empty;
    public string Extractor { get; set; } = string.Empty;
    public string FormatSummary { get; set; } = string.Empty;
    public string FilePath { get; set; } = string.Empty;
    public string OutputDirectory { get; set; } = string.Empty;
    public long FileSizeBytes { get; set; }
    public DateTime CompletedAt { get; set; } = DateTime.Now;

    public string FileSizeText => FormatHelpers.HumanSize(FileSizeBytes > 0 ? FileSizeBytes : null);
    public string CompletedAtText => CompletedAt.ToString("yyyy-MM-dd HH:mm");
    public string DisplaySource => string.IsNullOrWhiteSpace(Extractor) ? "网页视频" : Extractor;
}

public sealed class AppSettings
{
    public string Theme { get; set; } = "Default";          // Default / Light / Dark
    public string Backdrop { get; set; } = "Mica";          // Mica / MicaAlt / Acrylic
    public string OutputDirectory { get; set; } = GetDefaultDownloadsDir();
    public string OutputTemplate { get; set; } = "%(title).100B [%(id)s].%(ext)s";
    public string CookiesSource { get; set; } = "builtin";  // Built-in WebView2 login (falls back to anonymous if not extracted yet)
    public string DefaultContainer { get; set; } = "auto";
    public string ProxyUrl { get; set; } = string.Empty;
    public int MaxConcurrentDownloads { get; set; } = 3;
    public int ConcurrentFragments { get; set; } = 8;       // -N for DASH/HLS speed boost
    public bool UseAria2Acceleration { get; set; } = true;  // 16-thread HTTP/HTTPS chunked download via aria2c
    public int Aria2Connections { get; set; } = 16;         // -x / -s for aria2c
    public string RateLimit { get; set; } = string.Empty;
    public string Impersonate { get; set; } = "none";       // none / chrome / edge / safari
    public bool ForceIpv4 { get; set; } = false;
    public bool EnableJsRuntimes { get; set; } = true;
    public bool UseDownloadArchive { get; set; } = false;
    public bool NoMtime { get; set; } = false;
    public bool AutoEmbedMetadata { get; set; } = true;
    public bool AutoEmbedChapters { get; set; } = true;
    public bool AutoEmbedThumbnail { get; set; } = false;
    public bool AutoDownloadSubtitles { get; set; } = false;
    public string DefaultSubtitleLangs { get; set; } = "zh-Hans,zh-CN,zh,en.*";
    public string SponsorBlockMode { get; set; } = "off";   // off / remove / mark
    public string DefaultExtraArguments { get; set; } = string.Empty;

    public static string GetDefaultDownloadsDir()
    {
        var userProfile = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
        var downloads = Path.Combine(userProfile, "Downloads");
        return Directory.Exists(downloads) ? downloads : userProfile;
    }
}
