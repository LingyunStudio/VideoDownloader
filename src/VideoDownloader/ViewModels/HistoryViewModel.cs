using System.Collections.ObjectModel;
using System.Diagnostics;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VideoDownloader.Helpers;
using VideoDownloader.Models;
using VideoDownloader.Services;

namespace VideoDownloader.ViewModels;

public sealed partial class HistoryViewModel : ObservableObject
{
    private readonly HistoryService _history;

    public ObservableCollection<HistoryEntry> FilteredEntries { get; } = [];

    public event Action<string>? RedownloadRequested;

    [ObservableProperty]
    private string _searchQuery = string.Empty;

    [ObservableProperty]
    private bool _hasEntries;

    public HistoryViewModel(HistoryService history)
    {
        _history = history;
        _history.HistoryChanged += Reload;
        Reload();
    }

    partial void OnSearchQueryChanged(string value) => Reload();

    public void Reload()
    {
        var all = _history.GetAll();
        var q = SearchQuery.Trim();

        FilteredEntries.Clear();
        foreach (var item in all)
        {
            if (string.IsNullOrEmpty(q) ||
                item.Title.Contains(q, StringComparison.OrdinalIgnoreCase) ||
                item.Extractor.Contains(q, StringComparison.OrdinalIgnoreCase) ||
                item.Url.Contains(q, StringComparison.OrdinalIgnoreCase))
            {
                FilteredEntries.Add(item);
            }
        }

        HasEntries = FilteredEntries.Count > 0;
    }

    [RelayCommand]
    private void OpenFileLocation(HistoryEntry? entry)
    {
        if (entry is null)
            return;

        try
        {
            if (!string.IsNullOrEmpty(entry.FilePath) && File.Exists(entry.FilePath))
                Process.Start(new ProcessStartInfo("explorer.exe", $"/select,\"{entry.FilePath}\"") { UseShellExecute = true });
            else if (!string.IsNullOrEmpty(entry.OutputDirectory) && Directory.Exists(entry.OutputDirectory))
                Process.Start(new ProcessStartInfo("explorer.exe", entry.OutputDirectory) { UseShellExecute = true });
        }
        catch (Exception ex)
        {
            AppLogger.Error("Failed to open history file location", ex);
        }
    }

    [RelayCommand]
    private void OpenWebPage(HistoryEntry? entry)
    {
        if (entry is null || string.IsNullOrWhiteSpace(entry.Url))
            return;

        try
        {
            Process.Start(new ProcessStartInfo(entry.Url) { UseShellExecute = true });
        }
        catch { }
    }

    [RelayCommand]
    private void Redownload(HistoryEntry? entry)
    {
        if (entry is not null && !string.IsNullOrWhiteSpace(entry.Url))
            RedownloadRequested?.Invoke(entry.Url);
    }

    [RelayCommand]
    private void DeleteEntry(HistoryEntry? entry)
    {
        if (entry is not null)
            _history.Remove(entry.Id);
    }

    [RelayCommand]
    private void ClearAll() => _history.Clear();
}
