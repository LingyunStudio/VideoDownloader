using System.Diagnostics;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VideoDownloader.Helpers;
using VideoDownloader.Services;

namespace VideoDownloader.ViewModels;

public sealed partial class SettingsViewModel : ObservableObject
{
    private readonly SettingsService _settings;
    private readonly ToolManagerService _tools;
    private readonly AppUpdaterService _appUpdater;

    public event Action<string>? ThemeChanged;
    public event Action<string>? BackdropChanged;

    public SettingsViewModel(
        SettingsService settings,
        ToolManagerService tools,
        AppUpdaterService appUpdater)
    {
        _settings = settings;
        _tools = tools;
        _appUpdater = appUpdater;

        _selectedTheme = _settings.Current.Theme;
        _selectedBackdrop = _settings.Current.Backdrop;
        _outputDirectory = _settings.Current.OutputDirectory;
        _outputTemplate = _settings.Current.OutputTemplate;
        _proxyUrl = _settings.Current.ProxyUrl;
        _maxConcurrentDownloads = _settings.Current.MaxConcurrentDownloads;
        _concurrentFragments = _settings.Current.ConcurrentFragments;
        _useAria2Acceleration = _settings.Current.UseAria2Acceleration;
        _aria2Connections = _settings.Current.Aria2Connections;
        _rateLimit = _settings.Current.RateLimit;
        _impersonate = _settings.Current.Impersonate;
        _forceIpv4 = _settings.Current.ForceIpv4;
        _enableJsRuntimes = _settings.Current.EnableJsRuntimes;
        _useDownloadArchive = _settings.Current.UseDownloadArchive;
        _autoEmbedMetadata = _settings.Current.AutoEmbedMetadata;
        _autoEmbedThumbnail = _settings.Current.AutoEmbedThumbnail;
        _autoDownloadSubtitles = _settings.Current.AutoDownloadSubtitles;
        _defaultExtraArguments = _settings.Current.DefaultExtraArguments;
    }

    public string AppVersionText => $"v{AppUpdaterService.CurrentVersion}";

    [ObservableProperty] private string _selectedTheme;
    [ObservableProperty] private string _selectedBackdrop;
    [ObservableProperty] private string _outputDirectory;
    [ObservableProperty] private string _outputTemplate;
    [ObservableProperty] private string _proxyUrl;
    [ObservableProperty] private double _maxConcurrentDownloads;
    [ObservableProperty] private double _concurrentFragments;
    [ObservableProperty] private bool _useAria2Acceleration;
    [ObservableProperty] private double _aria2Connections;
    [ObservableProperty] private string _rateLimit;
    [ObservableProperty] private string _impersonate;
    [ObservableProperty] private bool _forceIpv4;
    [ObservableProperty] private bool _enableJsRuntimes;
    [ObservableProperty] private bool _useDownloadArchive;
    [ObservableProperty] private bool _autoEmbedMetadata;
    [ObservableProperty] private bool _autoEmbedThumbnail;
    [ObservableProperty] private bool _autoDownloadSubtitles;
    [ObservableProperty] private string _defaultExtraArguments;

    // Engine & updater states
    [ObservableProperty] private string _ytDlpVersion = "检测中…";
    [ObservableProperty] private string _ytDlpStatus = string.Empty;
    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CanUpdateYtDlp))]
    private bool _isYtDlpBusy;
    [ObservableProperty] private double _ytDlpProgress;

    [ObservableProperty] private string _ffmpegStatus = "检测中…";
    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CanInstallFfmpeg))]
    private bool _isFfmpegBusy;
    [ObservableProperty] private double _ffmpegProgress;

    [ObservableProperty] private string _aria2Status = "检测中…";
    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(CanInstallAria2))]
    private bool _isAria2Busy;
    [ObservableProperty] private double _aria2Progress;

    public bool CanUpdateYtDlp => !IsYtDlpBusy;
    public bool CanInstallFfmpeg => !IsFfmpegBusy;
    public bool CanInstallAria2 => !IsAria2Busy;

    [ObservableProperty] private string _appUpdateStatus = "点击检查 GitHub 最新版本";
    [ObservableProperty] private bool _isAppUpdateBusy;
    [ObservableProperty] private double _appUpdateProgress;
    [ObservableProperty] private bool _canInstallAppUpdate;
    private string _pendingInstallerUrl = string.Empty;

    partial void OnSelectedThemeChanged(string value)
    {
        _settings.Current.Theme = value;
        _settings.Save();
        ThemeChanged?.Invoke(value);
    }

    partial void OnSelectedBackdropChanged(string value)
    {
        _settings.Current.Backdrop = value;
        _settings.Save();
        BackdropChanged?.Invoke(value);
    }

    partial void OnOutputDirectoryChanged(string value)
    {
        _settings.Current.OutputDirectory = value;
        _settings.Save();
    }

    partial void OnOutputTemplateChanged(string value)
    {
        _settings.Current.OutputTemplate = value;
        _settings.Save();
    }

    partial void OnProxyUrlChanged(string value)
    {
        _settings.Current.ProxyUrl = value;
        _settings.Save();
    }

    partial void OnMaxConcurrentDownloadsChanged(double value)
    {
        if (double.IsNaN(value))
            return;
        _settings.Current.MaxConcurrentDownloads = Math.Clamp((int)Math.Round(value), 1, 10);
        _settings.Save();
    }

    partial void OnConcurrentFragmentsChanged(double value)
    {
        if (double.IsNaN(value))
            return;
        _settings.Current.ConcurrentFragments = Math.Clamp((int)Math.Round(value), 1, 16);
        _settings.Save();
    }

    partial void OnUseAria2AccelerationChanged(bool value)
    {
        _settings.Current.UseAria2Acceleration = value;
        _settings.Save();
    }

    partial void OnAria2ConnectionsChanged(double value)
    {
        if (double.IsNaN(value))
            return;
        _settings.Current.Aria2Connections = Math.Clamp((int)Math.Round(value), 1, 16);
        _settings.Save();
    }

    partial void OnRateLimitChanged(string value)
    {
        _settings.Current.RateLimit = value;
        _settings.Save();
    }

    partial void OnImpersonateChanged(string value)
    {
        _settings.Current.Impersonate = value;
        _settings.Save();
    }

    partial void OnForceIpv4Changed(bool value)
    {
        _settings.Current.ForceIpv4 = value;
        _settings.Save();
    }

    partial void OnUseDownloadArchiveChanged(bool value)
    {
        _settings.Current.UseDownloadArchive = value;
        _settings.Save();
    }

    partial void OnDefaultExtraArgumentsChanged(string value)
    {
        _settings.Current.DefaultExtraArguments = value;
        _settings.Save();
    }

    partial void OnEnableJsRuntimesChanged(bool value)
    {
        _settings.Current.EnableJsRuntimes = value;
        _settings.Save();
    }

    partial void OnAutoEmbedMetadataChanged(bool value)
    {
        _settings.Current.AutoEmbedMetadata = value;
        _settings.Save();
    }

    partial void OnAutoEmbedThumbnailChanged(bool value)
    {
        _settings.Current.AutoEmbedThumbnail = value;
        _settings.Save();
    }

    partial void OnAutoDownloadSubtitlesChanged(bool value)
    {
        _settings.Current.AutoDownloadSubtitles = value;
        _settings.Save();
    }

    public async Task RefreshEngineStatusAsync()
    {
        YtDlpVersion = await _tools.GetInstalledYtDlpVersionAsync();
        var ytExe = _tools.FindYtDlpExecutable();
        YtDlpStatus = ytExe is not null ? $"已就绪（{ytExe}）" : "未安装";

        var ffDir = _tools.FindFfmpegDirectory();
        FfmpegStatus = ffDir is not null ? $"已就绪（{ffDir}）" : "未安装";

        var ariaExe = _tools.FindAria2Executable();
        Aria2Status = ariaExe is not null ? $"已就绪 · 支持 16 线程加速（{ariaExe}）" : "未安装（点击右侧按钮自动下载约 2.5 MB）";
    }

    [RelayCommand]
    private async Task UpdateYtDlpAsync()
    {
        if (IsYtDlpBusy) return;
        IsYtDlpBusy = true;
        YtDlpProgress = 0;
        YtDlpStatus = "正在检查 GitHub 最新版…";

        try
        {
            var check = await _tools.CheckYtDlpUpdateAsync();
            if (!check.UpdateAvailable && _tools.IsYtDlpReady)
            {
                YtDlpStatus = $"已是最新版本（{check.CurrentVersion}）";
                return;
            }

            YtDlpStatus = $"发现新版本 {check.LatestVersion}，正在下载…";
            var progress = new Progress<DownloadProgressInfo>(p =>
            {
                YtDlpProgress = p.Percentage;
                YtDlpStatus = p.TotalBytes > 0
                    ? $"正在下载 {check.LatestVersion}（{FormatHelpers.HumanSize(p.DownloadedBytes)} / {FormatHelpers.HumanSize(p.TotalBytes)}）"
                    : $"正在下载 {check.LatestVersion}…";
            });

            var newVer = await _tools.InstallOrUpdateYtDlpAsync(progress);
            YtDlpVersion = newVer;
            YtDlpProgress = 100;
            YtDlpStatus = $"已更新至 {newVer}（立即生效，无需重启）";
        }
        catch (Exception ex)
        {
            AppLogger.Error("yt-dlp update failed", ex);
            YtDlpStatus = $"更新失败：{ex.Message}";
        }
        finally
        {
            IsYtDlpBusy = false;
        }
    }

    [RelayCommand]
    private async Task InstallFfmpegAsync()
    {
        if (IsFfmpegBusy) return;
        IsFfmpegBusy = true;
        FfmpegProgress = 0;
        FfmpegStatus = "正在下载 ffmpeg 组件…";

        try
        {
            var progress = new Progress<DownloadProgressInfo>(p =>
            {
                FfmpegProgress = p.Percentage;
                FfmpegStatus = p.TotalBytes > 0
                    ? $"正在下载 ffmpeg（{FormatHelpers.HumanSize(p.DownloadedBytes)} / {FormatHelpers.HumanSize(p.TotalBytes)}）"
                    : "正在下载 ffmpeg…";
            });

            await _tools.InstallFfmpegAsync(progress);
            FfmpegProgress = 100;
            FfmpegStatus = $"已就绪（{_tools.FfmpegDirectory}）";
        }
        catch (Exception ex)
        {
            AppLogger.Error("ffmpeg install failed", ex);
            FfmpegStatus = $"下载失败：{ex.Message}";
        }
        finally
        {
            IsFfmpegBusy = false;
        }
    }

    [RelayCommand]
    private async Task InstallAria2Async()
    {
        if (IsAria2Busy) return;
        IsAria2Busy = true;
        Aria2Progress = 0;
        Aria2Status = "正在下载 aria2c 多线程加速引擎…";

        try
        {
            var progress = new Progress<DownloadProgressInfo>(p =>
            {
                Aria2Progress = p.Percentage;
                Aria2Status = p.TotalBytes > 0
                    ? $"正在下载 aria2c（{FormatHelpers.HumanSize(p.DownloadedBytes)} / {FormatHelpers.HumanSize(p.TotalBytes)}）"
                    : "正在下载 aria2c…";
            });

            await _tools.InstallAria2Async(progress);
            Aria2Progress = 100;
            Aria2Status = $"已就绪 · 支持 16 线程加速（{_tools.FindAria2Executable()}）";
        }
        catch (Exception ex)
        {
            AppLogger.Error("aria2c install failed", ex);
            Aria2Status = $"下载失败：{ex.Message}";
        }
        finally
        {
            IsAria2Busy = false;
        }
    }

    [RelayCommand]
    private async Task CheckAppUpdateAsync()
    {
        if (IsAppUpdateBusy) return;
        IsAppUpdateBusy = true;
        CanInstallAppUpdate = false;
        AppUpdateStatus = "正在检查软件更新…";

        try
        {
            var result = await _appUpdater.CheckForUpdateAsync();
            if (!result.UpdateAvailable)
            {
                AppUpdateStatus = $"当前已是最新版本（v{result.CurrentVersion}）";
                return;
            }

            _pendingInstallerUrl = result.InstallerUrl;
            CanInstallAppUpdate = !string.IsNullOrEmpty(_pendingInstallerUrl);
            AppUpdateStatus = CanInstallAppUpdate
                ? $"发现新版本 v{result.LatestVersion}，点击右侧按钮立即更新"
                : $"发现新版本 v{result.LatestVersion}（请前往 GitHub Releases 手动下载）";
        }
        catch (Exception ex)
        {
            AppLogger.Error("App update check failed", ex);
            AppUpdateStatus = $"检查更新失败：{ex.Message}";
        }
        finally
        {
            IsAppUpdateBusy = false;
        }
    }

    [RelayCommand]
    private async Task InstallAppUpdateAsync()
    {
        if (IsAppUpdateBusy || string.IsNullOrEmpty(_pendingInstallerUrl))
            return;

        IsAppUpdateBusy = true;
        AppUpdateProgress = 0;
        AppUpdateStatus = "正在下载新版安装包…";

        try
        {
            var progress = new Progress<DownloadProgressInfo>(p =>
            {
                AppUpdateProgress = p.Percentage;
                AppUpdateStatus = p.TotalBytes > 0
                    ? $"正在下载安装包（{FormatHelpers.HumanSize(p.DownloadedBytes)} / {FormatHelpers.HumanSize(p.TotalBytes)}）"
                    : "正在下载安装包…";
            });

            var installerPath = await _appUpdater.DownloadInstallerAsync(_pendingInstallerUrl, progress);
            AppUpdateStatus = "正在启动静默安装…";
            _appUpdater.LaunchSilentInstallAndExit(installerPath);
        }
        catch (Exception ex)
        {
            AppLogger.Error("App update install failed", ex);
            AppUpdateStatus = $"安装失败：{ex.Message}";
        }
        finally
        {
            IsAppUpdateBusy = false;
        }
    }

    [RelayCommand]
    private void OpenAppDataFolder()
    {
        try
        {
            Process.Start(new ProcessStartInfo("explorer.exe", AppLogger.AppDataDirectory) { UseShellExecute = true });
        }
        catch { }
    }
}
