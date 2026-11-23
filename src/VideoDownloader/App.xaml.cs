using Microsoft.UI.Xaml;
using VideoDownloader.Helpers;
using VideoDownloader.Services;
using VideoDownloader.ViewModels;

namespace VideoDownloader;

public partial class App : Application
{
    public static App CurrentApp => (App)Current;

    public SettingsService SettingsService { get; }
    public HistoryService HistoryService { get; }
    public ToolManagerService ToolManagerService { get; }
    public CookieManagerService CookieManagerService { get; }
    public AppUpdaterService AppUpdaterService { get; }
    public YtDlpService YtDlpService { get; }
    public DownloadQueueService DownloadQueueService { get; }

    public MainViewModel MainViewModel { get; }
    public HomeViewModel HomeViewModel { get; }
    public DownloadsViewModel DownloadsViewModel { get; }
    public HistoryViewModel HistoryViewModel { get; }
    public SettingsViewModel SettingsViewModel { get; }

    public MainWindow? MainWindow { get; private set; }

    public App()
    {
        InitializeComponent();

        UnhandledException += OnUnhandledException;
        AppDomain.CurrentDomain.UnhandledException += (_, e) =>
        {
            if (e.ExceptionObject is Exception ex)
                AppLogger.Crash(ex, "AppDomain");
        };
        TaskScheduler.UnobservedTaskException += (_, e) =>
        {
            AppLogger.Crash(e.Exception, "UnobservedTask");
            e.SetObserved();
        };

        // Lightweight manual DI (zero reflection overhead, fast startup)
        SettingsService = new SettingsService();
        HistoryService = new HistoryService();
        ToolManagerService = new ToolManagerService();
        CookieManagerService = new CookieManagerService();
        AppUpdaterService = new AppUpdaterService();
        YtDlpService = new YtDlpService(ToolManagerService);
        DownloadQueueService = new DownloadQueueService(YtDlpService, HistoryService, SettingsService);

        MainViewModel = new MainViewModel(DownloadQueueService, ToolManagerService);
        HomeViewModel = new HomeViewModel(YtDlpService, DownloadQueueService, SettingsService, ToolManagerService, CookieManagerService);
        DownloadsViewModel = new DownloadsViewModel(DownloadQueueService);
        HistoryViewModel = new HistoryViewModel(HistoryService);
        SettingsViewModel = new SettingsViewModel(SettingsService, ToolManagerService, AppUpdaterService);
    }

    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        AppLogger.Info($"App launched v{AppUpdaterService.CurrentVersion}");
        MainWindow = new MainWindow();
        MainWindow.Activate();
    }

    private static void OnUnhandledException(object sender, Microsoft.UI.Xaml.UnhandledExceptionEventArgs e)
    {
        AppLogger.Crash(e.Exception, "WinUI");
    }
}
