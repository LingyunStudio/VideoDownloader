using System.Text.Json;
using VideoDownloader.Helpers;
using VideoDownloader.Models;

namespace VideoDownloader.Services;

public sealed class HistoryService
{
    private const int MaxEntries = 500;
    private readonly string _historyPath;
    private readonly object _lock = new();
    private List<HistoryEntry> _entries;

    public event Action? HistoryChanged;

    public HistoryService()
    {
        _historyPath = Path.Combine(AppLogger.AppDataDirectory, "history.json");
        _entries = Load();
    }

    public IReadOnlyList<HistoryEntry> GetAll()
    {
        lock (_lock)
        {
            return [.. _entries];
        }
    }

    public void Add(HistoryEntry entry)
    {
        lock (_lock)
        {
            _entries.Insert(0, entry);
            if (_entries.Count > MaxEntries)
                _entries.RemoveRange(MaxEntries, _entries.Count - MaxEntries);
            SaveLocked();
        }
        HistoryChanged?.Invoke();
    }

    public void Remove(string id)
    {
        lock (_lock)
        {
            _entries.RemoveAll(e => e.Id == id);
            SaveLocked();
        }
        HistoryChanged?.Invoke();
    }

    public void Clear()
    {
        lock (_lock)
        {
            _entries.Clear();
            SaveLocked();
        }
        HistoryChanged?.Invoke();
    }

    private List<HistoryEntry> Load()
    {
        try
        {
            if (File.Exists(_historyPath))
            {
                var json = File.ReadAllText(_historyPath);
                var list = JsonSerializer.Deserialize(json, AppJsonContext.Default.ListHistoryEntry);
                if (list is not null)
                    return list;
            }
        }
        catch (Exception ex)
        {
            AppLogger.Error("Failed to load history.json.", ex);
        }
        return [];
    }

    private void SaveLocked()
    {
        try
        {
            var json = JsonSerializer.Serialize(_entries, AppJsonContext.Default.ListHistoryEntry);
            File.WriteAllText(_historyPath, json);
        }
        catch (Exception ex)
        {
            AppLogger.Error("Failed to save history.json.", ex);
        }
    }
}
