using System.Text.Json;
using VideoDownloader.Helpers;
using VideoDownloader.Models;

namespace VideoDownloader.Services;

public sealed class SettingsService
{
    private readonly string _settingsPath;
    private readonly object _lock = new();

    public AppSettings Current { get; private set; }

    public SettingsService()
    {
        _settingsPath = Path.Combine(AppLogger.AppDataDirectory, "settings.json");
        Current = Load();
    }

    private AppSettings Load()
    {
        try
        {
            if (File.Exists(_settingsPath))
            {
                var json = File.ReadAllText(_settingsPath);
                var loaded = JsonSerializer.Deserialize(json, AppJsonContext.Default.AppSettings);
                if (loaded is not null)
                {
                    if (string.IsNullOrWhiteSpace(loaded.OutputDirectory) || !Directory.Exists(loaded.OutputDirectory))
                        loaded.OutputDirectory = AppSettings.GetDefaultDownloadsDir();
                    if (loaded.MaxConcurrentDownloads < 1 || loaded.MaxConcurrentDownloads > 10)
                        loaded.MaxConcurrentDownloads = 3;
                    return loaded;
                }
            }
        }
        catch (Exception ex)
        {
            AppLogger.Error("Failed to load settings.json, falling back to defaults.", ex);
        }

        return new AppSettings();
    }

    public void Save()
    {
        try
        {
            lock (_lock)
            {
                var dir = Path.GetDirectoryName(_settingsPath);
                if (!string.IsNullOrEmpty(dir))
                    Directory.CreateDirectory(dir);
                var json = JsonSerializer.Serialize(Current, AppJsonContext.Default.AppSettings);
                File.WriteAllText(_settingsPath, json);
            }
        }
        catch (Exception ex)
        {
            AppLogger.Error("Failed to save settings.json.", ex);
        }
    }
}
