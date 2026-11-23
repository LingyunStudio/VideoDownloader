using VideoDownloader.Helpers;

namespace VideoDownloader.Models;

public sealed class PlaylistEntryItem
{
    public int Index { get; init; }
    public string Id { get; init; } = string.Empty;
    public string Title { get; init; } = string.Empty;
    public string Url { get; init; } = string.Empty;
    public double Duration { get; init; }
    public string Uploader { get; init; } = string.Empty;

    public string IndexText => $"#{Index}";
    public string DurationText => FormatHelpers.HumanDuration(Duration);
}

public sealed class VideoInfo
{
    public string Title { get; init; } = string.Empty;
    public string Uploader { get; init; } = string.Empty;
    public double Duration { get; init; }
    public string Thumbnail { get; init; } = string.Empty;
    public string WebpageUrl { get; init; } = string.Empty;
    public string Extractor { get; init; } = string.Empty;
    public string VideoId { get; init; } = string.Empty;
    public long? ViewCount { get; init; }
    public long? LikeCount { get; init; }
    public string UploadDate { get; init; } = string.Empty;
    public string Description { get; init; } = string.Empty;
    public bool IsLive { get; init; }
    public bool IsPlaylist { get; init; }
    public int PlaylistCount { get; init; }
    public List<PlaylistEntryItem> PlaylistEntries { get; init; } = [];
    public string BestFormatId { get; init; } = string.Empty;
    public List<FormatOption> Formats { get; init; } = [];
    public List<string> AvailableSubtitleLangs { get; init; } = [];
    public int ChapterCount { get; init; }

    public string DurationText => IsLive ? "直播中" : FormatHelpers.HumanDuration(Duration);
    public string ViewCountText => FormatHelpers.HumanCount(ViewCount);
    public string LikeCountText => FormatHelpers.HumanCount(LikeCount);
    public string UploadDateText => FormatHelpers.FormatUploadDate(UploadDate);
    public string SubtitleSummaryText => AvailableSubtitleLangs.Count > 0
        ? $"可用字幕：{string.Join(", ", AvailableSubtitleLangs.Take(8))}{(AvailableSubtitleLangs.Count > 8 ? $" 等 {AvailableSubtitleLangs.Count} 种" : "")}"
        : string.Empty;
}
