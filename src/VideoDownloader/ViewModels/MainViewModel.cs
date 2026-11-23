using CommunityToolkit.Mvvm.ComponentModel;
using Microsoft.UI.Dispatching;
using Microsoft.UI.Xaml;
using VideoDownloader.Helpers;
using VideoDownloader.Services;

namespace VideoDownloader.ViewModels;

public sealed partial class MainViewModel : ObservableObject
{
    private readonly DownloadQueueService _queue;
    private readonly ToolManagerService _tools;
    private DispatcherQueue? _dispatcher;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(ActiveBadgeVisibility))]
    private int _activeDownloadCount;

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(ToolSetupBannerVisibility))]
    private bool _isToolSetupBannerVisible;

    public Visibility ActiveBadgeVisibility => ActiveDownloadCount > 0 ? Visibility.Visible : Visibility.Collapsed;
    public Visibility ToolSetupBannerVisibility => IsToolSetupBannerVisible ? Visibility.Visible : Visibility.Collapsed;

    [ObservableProperty]
    private string _toolSetupMessage = string.Empty;

    [ObservableProperty]
    private double _toolSetupProgress;

    [ObservableProperty]
    private bool _isToolSetupIndeterminate = true;

    public MainViewModel(DownloadQueueService queue, ToolManagerService tools)
    {
        _queue = queue;
        _tools = tools;
        _queue.QueueStatsChanged += OnQueueStatsChanged;
    }

    public void AttachDispatcher(DispatcherQueue dispatcher)
    {
        _dispatcher = dispatcher;
        _queue.AttachDispatcher(dispatcher);
    }

    private void OnQueueStatsChanged()
    {
        if (_dispatcher is null || _dispatcher.HasThreadAccess)
            ActiveDownloadCount = _queue.ActiveCount;
        else
            _dispatcher.TryEnqueue(() => ActiveDownloadCount = _queue.ActiveCount);
    }

    /// <summary>
    /// Ensures yt-dlp and ffmpeg are available on first launch without blocking the UI thread.
    /// </summary>
    public async Task EnsureToolsReadyOnStartupAsync()
    {
        bool needYtDlp = !_tools.IsYtDlpReady;
        bool needFfmpeg = !_tools.IsFfmpegReady;
        bool needAria2 = !_tools.IsAria2Ready;

        if (!needYtDlp && !needFfmpeg && !needAria2)
            return;

        IsToolSetupBannerVisible = true;
        try
        {
            if (needYtDlp)
            {
                ToolSetupMessage = "首次运行：正在下载高速版 yt-dlp 引擎…";
                IsToolSetupIndeterminate = false;
                var progress = new Progress<DownloadProgressInfo>(p =>
                {
                    ToolSetupProgress = p.Percentage;
                    ToolSetupMessage = p.TotalBytes > 0
                        ? $"正在下载 yt-dlp 引擎（{FormatHelpers.HumanSize(p.DownloadedBytes)} / {FormatHelpers.HumanSize(p.TotalBytes)}）…"
                        : "正在下载 yt-dlp 引擎…";
                });
                await _tools.EnsureYtDlpAsync(progress);
            }

            if (needFfmpeg)
            {
                ToolSetupMessage = "首次运行：正在下载 ffmpeg 音视频合并组件…";
                ToolSetupProgress = 0;
                IsToolSetupIndeterminate = false;
                var progress = new Progress<DownloadProgressInfo>(p =>
                {
                    ToolSetupProgress = p.Percentage;
                    ToolSetupMessage = p.TotalBytes > 0
                        ? $"正在下载 ffmpeg 组件（{FormatHelpers.HumanSize(p.DownloadedBytes)} / {FormatHelpers.HumanSize(p.TotalBytes)}）…"
                        : "正在下载 ffmpeg 组件…";
                });
                await _tools.EnsureFfmpegAsync(progress);
            }

            if (needAria2)
            {
                ToolSetupMessage = "正在下载 aria2c 多线程加速引擎（约 2.5 MB）…";
                ToolSetupProgress = 0;
                IsToolSetupIndeterminate = false;
                var progress = new Progress<DownloadProgressInfo>(p =>
                {
                    ToolSetupProgress = p.Percentage;
                    ToolSetupMessage = p.TotalBytes > 0
                        ? $"正在下载 aria2c 加速引擎（{FormatHelpers.HumanSize(p.DownloadedBytes)} / {FormatHelpers.HumanSize(p.TotalBytes)}）…"
                        : "正在下载 aria2c 加速引擎…";
                });
                await _tools.EnsureAria2Async(progress);
            }

            ToolSetupMessage = "引擎组件已就绪！";
            ToolSetupProgress = 100;
            await Task.Delay(1200);
            IsToolSetupBannerVisible = false;
        }
        catch (Exception ex)
        {
            AppLogger.Error("Startup tool setup failed.", ex);
            IsToolSetupIndeterminate = false;
            ToolSetupMessage = $"自动下载组件失败（可在设置页重试）：{ex.Message}";
        }
    }
}
