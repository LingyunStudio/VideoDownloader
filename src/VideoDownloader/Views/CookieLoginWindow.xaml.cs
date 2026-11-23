using Microsoft.UI.Composition.SystemBackdrops;
using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using Microsoft.Web.WebView2.Core;
using VideoDownloader.Helpers;
using VideoDownloader.Services;
using Windows.Graphics;
using Windows.System;

namespace VideoDownloader.Views;

public sealed partial class CookieLoginWindow : Window
{
    private readonly CookieManagerService _cookieManager;
    private readonly string _initialUrl;
    private bool _webViewReady;

    public event Action<CookieFileInspection>? CookiesExtracted;

    public CookieLoginWindow(CookieManagerService cookieManager, string initialUrl = "https://www.youtube.com/")
    {
        _cookieManager = cookieManager;
        _initialUrl = string.IsNullOrWhiteSpace(initialUrl) ? "https://www.youtube.com/" : initialUrl;

        InitializeComponent();

        ConfigureChrome();
        Closed += OnWindowClosed;
        _ = InitializeWebViewAsync();
    }

    private void ConfigureChrome()
    {
        ExtendsContentIntoTitleBar = true;
        SetTitleBar(LoginTitleBar);

        if (MicaController.IsSupported())
            SystemBackdrop = new MicaBackdrop { Kind = MicaKind.Base };

        var theme = App.CurrentApp.SettingsService.Current.Theme;
        RootGrid.RequestedTheme = theme switch
        {
            "Light" => ElementTheme.Light,
            "Dark" => ElementTheme.Dark,
            _ => ElementTheme.Default
        };

        var appWindow = WindowHelper.GetAppWindow(this);
        appWindow.Title = "网页登录获取 Cookies";

        var icoPath = WindowHelper.GetAssetPath("Assets", "Icons", "1.ico");
        if (File.Exists(icoPath))
            appWindow.SetIcon(icoPath);

        appWindow.Resize(new SizeInt32(1060, 740));
        var display = DisplayArea.GetFromWindowId(appWindow.Id, DisplayAreaFallback.Primary);
        if (display is not null)
        {
            var wa = display.WorkArea;
            appWindow.Move(new PointInt32(
                Math.Max(wa.X, wa.X + (wa.Width - 1060) / 2),
                Math.Max(wa.Y, wa.Y + (wa.Height - 740) / 2)));
        }
    }

    private async Task InitializeWebViewAsync()
    {
        try
        {
            LoadingRing.IsActive = true;
            StatusText.Text = "正在初始化内置浏览器…";

            var envOptions = new CoreWebView2EnvironmentOptions();
            var proxy = App.CurrentApp.SettingsService.Current.ProxyUrl;
            if (!string.IsNullOrWhiteSpace(proxy))
                envOptions.AdditionalBrowserArguments = $"--proxy-server=\"{proxy.Trim()}\"";

            var env = await CoreWebView2Environment.CreateWithOptionsAsync(
                browserExecutableFolder: null,
                userDataFolder: _cookieManager.WebView2ProfileDirectory,
                options: envOptions);

            await BrowserView.EnsureCoreWebView2Async(env);

            var core = BrowserView.CoreWebView2;
            core.Settings.AreDefaultContextMenusEnabled = true;
            core.Settings.AreDevToolsEnabled = false;
            core.Settings.IsStatusBarEnabled = false;

            core.NavigationStarting += (_, args) =>
            {
                DispatcherQueue.TryEnqueue(() =>
                {
                    LoadingRing.IsActive = true;
                    AddressBox.Text = args.Uri;
                });
            };
            core.NavigationCompleted += (_, _) =>
            {
                DispatcherQueue.TryEnqueue(() =>
                {
                    LoadingRing.IsActive = false;
                    if (BrowserView.Source is not null)
                        AddressBox.Text = BrowserView.Source.ToString();
                });
            };

            _webViewReady = true;
            StatusText.Text = "请在下方完成网站登录，登录成功后点击右上角「提取并保存 Cookies」。";
            NavigateTo(_initialUrl);
        }
        catch (Exception ex)
        {
            LoadingRing.IsActive = false;
            AppLogger.Error("WebView2 initialization failed", ex);
            StatusText.Text = $"内置浏览器初始化失败（请确认系统已安装 WebView2 Runtime）：{ex.Message}";
        }
    }

    private void NavigateTo(string url)
    {
        if (!_webViewReady || string.IsNullOrWhiteSpace(url))
            return;

        var u = url.Trim();
        if (!u.StartsWith("http://", StringComparison.OrdinalIgnoreCase) &&
            !u.StartsWith("https://", StringComparison.OrdinalIgnoreCase))
        {
            u = "https://" + u;
        }

        if (Uri.TryCreate(u, UriKind.Absolute, out var uri))
        {
            AddressBox.Text = uri.ToString();
            BrowserView.CoreWebView2.Navigate(uri.ToString());
        }
    }

    private async void ExtractCookies_Click(object sender, RoutedEventArgs e)
    {
        if (!_webViewReady || BrowserView.CoreWebView2 is null)
            return;

        try
        {
            ExtractButton.IsEnabled = false;
            LoadingRing.IsActive = true;
            StatusText.Text = "正在提取全部登录 Cookies（含 HttpOnly 与安全令牌）…";

            // Empty URI fetches all cookies across all domains in this profile (including google.com + youtube.com auth chain)
            var rawCookies = await BrowserView.CoreWebView2.CookieManager.GetCookiesAsync(string.Empty);
            var mapped = rawCookies.Select(c => (
                c.Domain,
                c.Path,
                c.IsSecure,
                c.Expires,
                c.Name,
                c.Value,
                c.IsSession));

            var inspection = _cookieManager.SaveNetscapeCookies(mapped);
            StatusText.Text = $"提取成功！{inspection.StatusSummary}。窗口即将关闭并自动返回应用…";
            CookiesExtracted?.Invoke(inspection);

            await Task.Delay(700);
            Close();
        }
        catch (Exception ex)
        {
            AppLogger.Error("Failed to extract WebView2 cookies", ex);
            StatusText.Text = $"提取 Cookies 失败：{ex.Message}";
        }
        finally
        {
            LoadingRing.IsActive = false;
            ExtractButton.IsEnabled = true;
        }
    }

    private void QuickSite_Click(object sender, RoutedEventArgs e)
    {
        if (sender is FrameworkElement { Tag: string url })
            NavigateTo(url);
    }

    private void Back_Click(object sender, RoutedEventArgs e)
    {
        if (_webViewReady && BrowserView.CoreWebView2.CanGoBack)
            BrowserView.CoreWebView2.GoBack();
    }

    private void Forward_Click(object sender, RoutedEventArgs e)
    {
        if (_webViewReady && BrowserView.CoreWebView2.CanGoForward)
            BrowserView.CoreWebView2.GoForward();
    }

    private void Reload_Click(object sender, RoutedEventArgs e)
    {
        if (_webViewReady)
            BrowserView.CoreWebView2.Reload();
    }

    private void Go_Click(object sender, RoutedEventArgs e) => NavigateTo(AddressBox.Text);

    private void AddressBox_KeyDown(object sender, KeyRoutedEventArgs e)
    {
        if (e.Key == VirtualKey.Enter)
        {
            e.Handled = true;
            NavigateTo(AddressBox.Text);
        }
    }

    private void OnWindowClosed(object sender, WindowEventArgs args)
    {
        // Immediately release WebView2 browser child processes to keep app memory minimal
        try
        {
            BrowserView.Close();
        }
        catch { }
    }
}
