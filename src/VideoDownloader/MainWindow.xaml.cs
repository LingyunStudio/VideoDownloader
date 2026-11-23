using Microsoft.UI.Composition.SystemBackdrops;
using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Media.Imaging;
using VideoDownloader.Helpers;
using VideoDownloader.ViewModels;
using VideoDownloader.Views;
using Windows.Graphics;

namespace VideoDownloader;

public sealed partial class MainWindow : Window
{
    public MainViewModel ViewModel => App.CurrentApp.MainViewModel;

    // Cached page instances for instant zero-allocation navigation & state preservation
    private HomePage? _homePage;
    private DownloadsPage? _downloadsPage;
    private HistoryPage? _historyPage;
    private SettingsPage? _settingsPage;

    public MainWindow()
    {
        InitializeComponent();

        ViewModel.AttachDispatcher(DispatcherQueue);

        ConfigureWindowChrome();
        ApplyTheme(App.CurrentApp.SettingsService.Current.Theme);
        ApplyBackdrop(App.CurrentApp.SettingsService.Current.Backdrop);

        // Wire cross-page events
        App.CurrentApp.HomeViewModel.NavigateToDownloadsRequested += () => NavigateTo("downloads");
        App.CurrentApp.HistoryViewModel.RedownloadRequested += url =>
        {
            App.CurrentApp.HomeViewModel.UrlInput = url;
            NavigateTo("home");
            _ = App.CurrentApp.HomeViewModel.ParseAsync();
        };
        App.CurrentApp.SettingsViewModel.ThemeChanged += ApplyTheme;
        App.CurrentApp.SettingsViewModel.BackdropChanged += ApplyBackdrop;

        NavView.SelectedItem = NavHome;
        NavigateTo("home");

        _ = ViewModel.EnsureToolsReadyOnStartupAsync();
    }

    private void ConfigureWindowChrome()
    {
        ExtendsContentIntoTitleBar = true;
        SetTitleBar(AppTitleBar);

        var appWindow = WindowHelper.GetAppWindow(this);
        appWindow.Title = "VideoDownloader";

        // Load user's custom 1.ico for taskbar, Alt+Tab, and title bar
        var icoPath = WindowHelper.GetAssetPath("Assets", "Icons", "1.ico");
        if (File.Exists(icoPath))
        {
            appWindow.SetIcon(icoPath);
            TitleBarIcon.Source = new BitmapImage(new Uri(icoPath));
        }
        else
        {
            var pngPath = WindowHelper.GetAssetPath("Assets", "Icons", "dlp.png");
            if (File.Exists(pngPath))
                TitleBarIcon.Source = new BitmapImage(new Uri(pngPath));
        }

        // Comfortable modern default size centered on screen
        appWindow.Resize(new SizeInt32(1180, 780));
        var displayArea = DisplayArea.GetFromWindowId(appWindow.Id, DisplayAreaFallback.Primary);
        if (displayArea is not null)
        {
            var workArea = displayArea.WorkArea;
            int x = workArea.X + (workArea.Width - 1180) / 2;
            int y = workArea.Y + (workArea.Height - 780) / 2;
            appWindow.Move(new PointInt32(Math.Max(workArea.X, x), Math.Max(workArea.Y, y)));
        }

        if (appWindow.Presenter is OverlappedPresenter presenter)
        {
            presenter.IsResizable = true;
            presenter.IsMaximizable = true;
            presenter.IsMinimizable = true;
        }
    }

    public void ApplyTheme(string themeName)
    {
        RootGrid.RequestedTheme = themeName switch
        {
            "Light" => ElementTheme.Light,
            "Dark" => ElementTheme.Dark,
            _ => ElementTheme.Default
        };
    }

    public void ApplyBackdrop(string backdropName)
    {
        try
        {
            SystemBackdrop = backdropName switch
            {
                "MicaAlt" when MicaController.IsSupported() => new MicaBackdrop { Kind = MicaKind.BaseAlt },
                "Acrylic" when DesktopAcrylicController.IsSupported() => new DesktopAcrylicBackdrop(),
                _ when MicaController.IsSupported() => new MicaBackdrop { Kind = MicaKind.Base },
                _ when DesktopAcrylicController.IsSupported() => new DesktopAcrylicBackdrop(),
                _ => null
            };
        }
        catch (Exception ex)
        {
            AppLogger.Warn($"Failed to set backdrop '{backdropName}': {ex.Message}");
        }
    }

    public void NavigateTo(string tag)
    {
        NavigationViewItem? targetItem = tag switch
        {
            "downloads" => NavDownloads,
            "history" => NavHistory,
            "settings" => NavSettings,
            _ => NavHome
        };

        if (!ReferenceEquals(NavView.SelectedItem, targetItem))
            NavView.SelectedItem = targetItem;

        Page page = tag switch
        {
            "downloads" => _downloadsPage ??= new DownloadsPage(),
            "history" => _historyPage ??= new HistoryPage(),
            "settings" => _settingsPage ??= new SettingsPage(),
            _ => _homePage ??= new HomePage()
        };

        ContentFrame.Content = page;

        if (page is SettingsPage sp)
            _ = sp.ViewModel.RefreshEngineStatusAsync();
        else if (page is HistoryPage hp)
            hp.ViewModel.Reload();
    }

    private void NavView_SelectionChanged(NavigationView sender, NavigationViewSelectionChangedEventArgs args)
    {
        if (args.SelectedItem is NavigationViewItem item && item.Tag is string tag)
        {
            NavigateTo(tag);
        }
    }
}
