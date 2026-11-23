namespace VideoDownloader.Models;

public enum PlaylistParseMode
{
    Auto,
    SingleVideoOnly,
    FullPlaylist
}

public sealed class DownloadRequest
{
    // Source & Identity
    public string Url { get; init; } = string.Empty;
    public string Title { get; init; } = string.Empty;
    public string ThumbnailUrl { get; init; } = string.Empty;
    public string Extractor { get; init; } = string.Empty;

    // Output & File
    public string OutputDirectory { get; init; } = string.Empty;
    public string OutputTemplate { get; init; } = "%(title).100B [%(id)s].%(ext)s";
    public bool UseArchive { get; init; }
    public string ArchiveFilePath { get; init; } = string.Empty;
    public bool NoMtime { get; init; }

    // Format & Post-processing
    public string FormatSpec { get; init; } = "bv*+ba/b";
    public string FormatSort { get; init; } = string.Empty;       // e.g. "vcodec:h264,acodec:aac"
    public string FormatSummary { get; init; } = "最佳画质";
    public string Container { get; init; } = "auto";              // auto / mp4 / mkv / webm / mov
    public bool RemuxVideo { get; init; }
    public bool AudioOnly { get; init; }
    public string AudioFormat { get; init; } = "mp3";

    // Playlist
    public PlaylistParseMode PlaylistMode { get; init; } = PlaylistParseMode.Auto;
    public string PlaylistItems { get; init; } = string.Empty;    // e.g. "1-10,15"
    public bool PlaylistReverse { get; init; }

    // Subtitles, Chapters & Metadata
    public bool DownloadSubtitles { get; init; }
    public bool DownloadAutoSubtitles { get; init; }
    public string SubtitleLangs { get; init; } = "zh-Hans,zh-CN,zh,en.*";
    public bool EmbedSubtitles { get; init; } = true;
    public string ConvertSubtitles { get; init; } = "none";       // none / srt / ass / vtt / lrc
    public bool EmbedThumbnail { get; init; }
    public bool WriteThumbnail { get; init; }
    public bool EmbedMetadata { get; init; } = true;
    public bool EmbedChapters { get; init; } = true;
    public bool SplitChapters { get; init; }

    // SponsorBlock (YouTube)
    public string SponsorBlockMode { get; init; } = "off";        // off / remove / mark
    public string SponsorBlockCategories { get; init; } = "default";

    // Clip & Live
    public string SectionRange { get; init; } = string.Empty;
    public bool ForceKeyframesAtCuts { get; init; }
    public bool LiveFromStart { get; init; }

    // Network, Performance & Auth
    public int ConcurrentFragments { get; init; } = 8;
    public bool UseAria2Acceleration { get; init; } = true;
    public int Aria2Connections { get; init; } = 16;
    public string RateLimit { get; init; } = string.Empty;        // e.g. "5M", "500K"
    public string CookiesSource { get; init; } = string.Empty;
    public string ProxyUrl { get; init; } = string.Empty;
    public string Impersonate { get; init; } = string.Empty;      // "", "chrome", "edge", "safari"
    public bool ForceIpv4 { get; init; }
    public bool EnableJsRuntimes { get; init; } = true;
    public string VideoPassword { get; init; } = string.Empty;

    // Power-user custom CLI arguments
    public string ExtraArguments { get; init; } = string.Empty;
}
