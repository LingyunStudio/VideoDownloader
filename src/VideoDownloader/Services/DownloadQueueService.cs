using System.Collections.Concurrent;
using System.Collections.ObjectModel;
using Microsoft.UI.Dispatching;
using VideoDownloader.Helpers;
using VideoDownloader.Models;

namespace VideoDownloader.Services;

public sealed class DownloadQueueService
{
    private readonly YtDlpService _ytDlp;
    private readonly HistoryService _history;
    private readonly SettingsService _settings;
    private readonly ConcurrentDictionary<string, CancellationTokenSource> _activeTokens = new();
    private readonly SemaphoreSlim _concurrencyGate;
    private DispatcherQueue? _dispatcher;

    public ObservableCollection<DownloadTaskItem> Tasks { get; } = [];

    public event Action? QueueStatsChanged;

    public DownloadQueueService(
        YtDlpService ytDlp,
        HistoryService history,
        SettingsService settings)
    {
        _ytDlp = ytDlp;
        _history = history;
        _settings = settings;
        _concurrencyGate = new SemaphoreSlim(Math.Clamp(_settings.Current.MaxConcurrentDownloads, 1, 10));
    }

    public void AttachDispatcher(DispatcherQueue dispatcher)
    {
        _dispatcher = dispatcher;
    }

    public int ActiveCount => Tasks.Count(t => t.IsActive);

    public double TotalSpeedBytesPerSec =>
        Tasks.Where(t => t.Status == DownloadStatus.Downloading).Sum(t => t.SpeedBytesPerSec);

    public DownloadTaskItem Enqueue(DownloadRequest request)
    {
        var item = new DownloadTaskItem(request)
        {
            CommandPreview = _ytDlp.BuildCommandPreview(request)
        };
        RunOnUi(() =>
        {
            Tasks.Insert(0, item);
            QueueStatsChanged?.Invoke();
        });
        _ = RunTaskAsync(item);
        return item;
    }

    public void Retry(DownloadTaskItem item)
    {
        if (!item.CanRetry)
            return;

        RunOnUi(() =>
        {
            item.ResetForRetry();
            QueueStatsChanged?.Invoke();
        });
        _ = RunTaskAsync(item);
    }

    public void Cancel(DownloadTaskItem item)
    {
        if (_activeTokens.TryGetValue(item.Id, out var cts))
        {
            try { cts.Cancel(); } catch { }
        }
        else if (item.Status == DownloadStatus.Queued)
        {
            RunOnUi(() =>
            {
                item.Status = DownloadStatus.Cancelled;
                item.StatusMessage = "已取消";
                item.NotifyMetricsChanged();
                QueueStatsChanged?.Invoke();
            });
        }
    }

    public void CancelAll()
    {
        foreach (var item in Tasks.Where(t => t.CanCancel).ToList())
            Cancel(item);
    }

    public void Remove(DownloadTaskItem item)
    {
        if (item.IsActive)
            return;

        RunOnUi(() =>
        {
            Tasks.Remove(item);
            QueueStatsChanged?.Invoke();
        });
    }

    public void ClearFinished()
    {
        RunOnUi(() =>
        {
            for (int i = Tasks.Count - 1; i >= 0; i--)
            {
                if (!Tasks[i].IsActive)
                    Tasks.RemoveAt(i);
            }
            QueueStatsChanged?.Invoke();
        });
    }

    private async Task RunTaskAsync(DownloadTaskItem item)
    {
        var cts = new CancellationTokenSource();
        _activeTokens[item.Id] = cts;

        try
        {
            await _concurrencyGate.WaitAsync(cts.Token);
            try
            {
                RunOnUi(() =>
                {
                    item.Status = DownloadStatus.Downloading;
                    item.StatusMessage = "正在连接…";
                    item.NotifyMetricsChanged();
                    QueueStatsChanged?.Invoke();
                });

                var logBuffer = new Queue<string>(64);
                var finalPath = await _ytDlp.DownloadAsync(item.Request, update =>
                {
                    if (!string.IsNullOrEmpty(update.LogLine))
                    {
                        lock (logBuffer)
                        {
                            if (logBuffer.Count >= 60)
                                logBuffer.Dequeue();
                            logBuffer.Enqueue(update.LogLine);
                        }
                    }

                    if (string.IsNullOrEmpty(update.StatusText) && string.IsNullOrEmpty(update.FinalFilePath) && !update.IsPostProcessing && update.DownloadedBytes == 0)
                        return;

                    RunOnUi(() =>
                    {
                        if (!string.IsNullOrEmpty(update.FinalFilePath))
                            item.OutputFilePath = update.FinalFilePath;

                        if (update.IsPostProcessing)
                        {
                            item.Status = DownloadStatus.PostProcessing;
                            item.StatusMessage = update.StatusText;
                            item.SpeedBytesPerSec = 0;
                            item.EtaSeconds = null;
                        }
                        else
                        {
                            item.Status = DownloadStatus.Downloading;
                            if (update.DownloadedBytes > 0)
                                item.DownloadedBytes = update.DownloadedBytes;
                            if (update.TotalBytes > 0)
                            {
                                item.TotalBytes = update.TotalBytes;
                                item.HasKnownTotal = true;
                                item.ProgressPercent = Math.Clamp(update.DownloadedBytes * 100.0 / update.TotalBytes, 0, 100);
                            }
                            else
                            {
                                item.HasKnownTotal = false;
                            }
                            item.SpeedBytesPerSec = update.SpeedBytesPerSec;
                            item.EtaSeconds = update.EtaSeconds;
                            item.StatusMessage = update.StatusText;
                        }

                        item.NotifyMetricsChanged();
                        QueueStatsChanged?.Invoke();
                    });
                }, cts.Token);

                string logSnapshot;
                lock (logBuffer)
                    logSnapshot = string.Join(Environment.NewLine, logBuffer);
                RunOnUi(() => item.LogSummary = logSnapshot);

                long fileSize = item.TotalBytes;
                if (!string.IsNullOrEmpty(finalPath) && File.Exists(finalPath))
                {
                    try { fileSize = new FileInfo(finalPath).Length; } catch { }
                }

                RunOnUi(() =>
                {
                    item.Status = DownloadStatus.Completed;
                    item.ProgressPercent = 100;
                    item.HasKnownTotal = true;
                    item.SpeedBytesPerSec = 0;
                    item.EtaSeconds = null;
                    if (fileSize > 0)
                        item.TotalBytes = fileSize;
                    if (!string.IsNullOrEmpty(finalPath))
                        item.OutputFilePath = finalPath;
                    item.StatusMessage = "下载完成";
                    item.NotifyMetricsChanged();
                    QueueStatsChanged?.Invoke();
                });

                _history.Add(new HistoryEntry
                {
                    Title = item.Title,
                    Url = item.Request.Url,
                    ThumbnailUrl = item.Request.ThumbnailUrl,
                    Extractor = item.Request.Extractor,
                    FormatSummary = item.Request.FormatSummary,
                    FilePath = finalPath,
                    OutputDirectory = item.Request.OutputDirectory,
                    FileSizeBytes = fileSize,
                    CompletedAt = DateTime.Now
                });
            }
            finally
            {
                _concurrencyGate.Release();
            }
        }
        catch (OperationCanceledException)
        {
            RunOnUi(() =>
            {
                item.Status = DownloadStatus.Cancelled;
                item.SpeedBytesPerSec = 0;
                item.EtaSeconds = null;
                item.StatusMessage = "已取消";
                item.NotifyMetricsChanged();
                QueueStatsChanged?.Invoke();
            });
        }
        catch (Exception ex)
        {
            AppLogger.Error($"Download failed for {item.Request.Url}", ex);
            RunOnUi(() =>
            {
                item.Status = DownloadStatus.Failed;
                item.SpeedBytesPerSec = 0;
                item.EtaSeconds = null;
                item.ErrorMessage = ex.Message;
                item.StatusMessage = $"失败：{ex.Message}";
                item.NotifyMetricsChanged();
                QueueStatsChanged?.Invoke();
            });
        }
        finally
        {
            _activeTokens.TryRemove(item.Id, out _);
            cts.Dispose();
        }
    }

    private void RunOnUi(Action action)
    {
        if (_dispatcher is null || _dispatcher.HasThreadAccess)
            action();
        else
            _dispatcher.TryEnqueue(() => action());
    }
}
