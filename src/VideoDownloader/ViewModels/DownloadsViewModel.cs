using System.Collections.ObjectModel;
using System.Diagnostics;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VideoDownloader.Helpers;
using VideoDownloader.Models;
using VideoDownloader.Services;

namespace VideoDownloader.ViewModels;

public sealed partial class DownloadsViewModel : ObservableObject
{
    private readonly DownloadQueueService _queue;

    public ObservableCollection<DownloadTaskItem> Tasks => _queue.Tasks;

    [ObservableProperty]
    private int _activeCount;

    [ObservableProperty]
    private int _completedCount;

    [ObservableProperty]
    private int _totalCount;

    [ObservableProperty]
    private string _totalSpeedText = "空闲";

    [ObservableProperty]
    private bool _hasTasks;

    public DownloadsViewModel(DownloadQueueService queue)
    {
        _queue = queue;
        _queue.QueueStatsChanged += RefreshStats;
        RefreshStats();
    }

    private void RefreshStats()
    {
        ActiveCount = _queue.ActiveCount;
        CompletedCount = _queue.Tasks.Count(t => t.Status == DownloadStatus.Completed);
        TotalCount = _queue.Tasks.Count;
        HasTasks = TotalCount > 0;
        var speed = _queue.TotalSpeedBytesPerSec;
        TotalSpeedText = speed > 0 ? FormatHelpers.HumanSpeed(speed) : "空闲";
    }

    [RelayCommand]
    private void CancelTask(DownloadTaskItem? item)
    {
        if (item is not null)
            _queue.Cancel(item);
    }

    [RelayCommand]
    private void RetryTask(DownloadTaskItem? item)
    {
        if (item is not null)
            _queue.Retry(item);
    }

    [RelayCommand]
    private void RemoveTask(DownloadTaskItem? item)
    {
        if (item is not null)
            _queue.Remove(item);
    }

    [RelayCommand]
    private void OpenFileLocation(DownloadTaskItem? item)
    {
        if (item is null)
            return;

        try
        {
            if (!string.IsNullOrEmpty(item.OutputFilePath) && File.Exists(item.OutputFilePath))
            {
                Process.Start(new ProcessStartInfo("explorer.exe", $"/select,\"{item.OutputFilePath}\"") { UseShellExecute = true });
            }
            else if (Directory.Exists(item.Request.OutputDirectory))
            {
                Process.Start(new ProcessStartInfo("explorer.exe", item.Request.OutputDirectory) { UseShellExecute = true });
            }
        }
        catch (Exception ex)
        {
            AppLogger.Error("Failed to open file location", ex);
        }
    }

    [RelayCommand]
    private void ClearFinished() => _queue.ClearFinished();

    [RelayCommand]
    private void CancelAll() => _queue.CancelAll();
}
