using CommunityToolkit.Mvvm.ComponentModel;
using VideoDownloader.Helpers;

namespace VideoDownloader.Models;

public enum DownloadStatus
{
    Queued,
    Downloading,
    PostProcessing,
    Completed,
    Failed,
    Cancelled
}

public sealed partial class DownloadTaskItem : ObservableObject
{
    public string Id { get; } = Guid.NewGuid().ToString("N")[..8];
    public DownloadRequest Request { get; }
    public DateTime CreatedAt { get; } = DateTime.Now;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(IsActive))]
    [NotifyPropertyChangedFor(nameof(CanCancel))]
    [NotifyPropertyChangedFor(nameof(CanRetry))]
    [NotifyPropertyChangedFor(nameof(CanOpenFile))]
    [NotifyPropertyChangedFor(nameof(CanRemove))]
    [NotifyPropertyChangedFor(nameof(IsIndeterminate))]
    [NotifyPropertyChangedFor(nameof(StatusBadgeText))]
    [NotifyPropertyChangedFor(nameof(IsErrorState))]
    [NotifyPropertyChangedFor(nameof(IsCompletedState))]
    private DownloadStatus _status = DownloadStatus.Queued;

    [ObservableProperty]
    private double _progressPercent;

    [ObservableProperty]
    private bool _hasKnownTotal;

    [ObservableProperty]
    private long _downloadedBytes;

    [ObservableProperty]
    private long _totalBytes;

    [ObservableProperty]
    private double _speedBytesPerSec;

    [ObservableProperty]
    private double? _etaSeconds;

    [ObservableProperty]
    private string _statusMessage = "等待队列调度…";

    [ObservableProperty]
    private string _errorMessage = string.Empty;

    [ObservableProperty]
    private string _outputFilePath = string.Empty;

    [ObservableProperty]
    private string _commandPreview = string.Empty;

    [ObservableProperty]
    private string _logSummary = string.Empty;

    public DownloadTaskItem(DownloadRequest request)
    {
        Request = request;
    }

    public string Title => string.IsNullOrWhiteSpace(Request.Title) ? Request.Url : Request.Title;
    public string ThumbnailUrl => Request.ThumbnailUrl;
    public string FormatBadge => Request.FormatSummary;
    public string SourceBadge => string.IsNullOrWhiteSpace(Request.Extractor) ? "视频" : Request.Extractor;

    public bool IsActive => Status is DownloadStatus.Queued or DownloadStatus.Downloading or DownloadStatus.PostProcessing;
    public bool CanCancel => Status is DownloadStatus.Queued or DownloadStatus.Downloading or DownloadStatus.PostProcessing;
    public bool CanRetry => Status is DownloadStatus.Failed or DownloadStatus.Cancelled;
    public bool CanOpenFile => Status == DownloadStatus.Completed;
    public bool CanRemove => !IsActive;
    public bool IsIndeterminate => Status == DownloadStatus.PostProcessing || (Status == DownloadStatus.Downloading && !HasKnownTotal);
    public bool IsErrorState => Status == DownloadStatus.Failed;
    public bool IsCompletedState => Status == DownloadStatus.Completed;

    public string StatusBadgeText => Status switch
    {
        DownloadStatus.Queued => "排队中",
        DownloadStatus.Downloading => HasKnownTotal ? $"{ProgressPercent:0.0}%" : "下载中",
        DownloadStatus.PostProcessing => "合并处理中",
        DownloadStatus.Completed => "已完成",
        DownloadStatus.Failed => "失败",
        DownloadStatus.Cancelled => "已取消",
        _ => string.Empty
    };

    public string SizeProgressText =>
        Status == DownloadStatus.Completed && TotalBytes > 0 ? FormatHelpers.HumanSize(TotalBytes) :
        TotalBytes > 0 ? $"{FormatHelpers.HumanSize(DownloadedBytes)} / {FormatHelpers.HumanSize(TotalBytes)}" :
        DownloadedBytes > 0 ? $"已下载 {FormatHelpers.HumanSize(DownloadedBytes)}" :
        StatusMessage;

    public string SpeedText => Status == DownloadStatus.Downloading ? FormatHelpers.HumanSpeed(SpeedBytesPerSec) : string.Empty;

    public string EtaText => Status == DownloadStatus.Downloading && EtaSeconds is > 0
        ? $"剩余 {FormatHelpers.HumanDuration(EtaSeconds)}"
        : string.Empty;

    public void NotifyMetricsChanged()
    {
        OnPropertyChanged(nameof(SizeProgressText));
        OnPropertyChanged(nameof(SpeedText));
        OnPropertyChanged(nameof(EtaText));
        OnPropertyChanged(nameof(StatusBadgeText));
        OnPropertyChanged(nameof(IsIndeterminate));
    }

    public void ResetForRetry()
    {
        Status = DownloadStatus.Queued;
        ProgressPercent = 0;
        HasKnownTotal = false;
        DownloadedBytes = 0;
        TotalBytes = 0;
        SpeedBytesPerSec = 0;
        EtaSeconds = null;
        ErrorMessage = string.Empty;
        StatusMessage = "等待重新下载…";
        NotifyMetricsChanged();
    }
}
