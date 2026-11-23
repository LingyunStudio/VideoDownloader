using System.ComponentModel;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media.Imaging;
using VideoDownloader.Helpers;
using VideoDownloader.Models;
using VideoDownloader.ViewModels;
using Windows.ApplicationModel.DataTransfer;
using Windows.System;

namespace VideoDownloader.Views;

public sealed partial class HomePage : Page
{
    public HomeViewModel ViewModel => App.CurrentApp.HomeViewModel;
    private CookieLoginWindow? _cookieLoginWindow;

    public HomePage()
    {
        InitializeComponent();
        ViewModel.PropertyChanged += OnViewModelPropertyChanged;
    }

    private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName == nameof(HomeViewModel.CurrentVideo))
        {
            UpdateThumbnail();
        }
    }

    private void UpdateThumbnail()
    {
        var url = ViewModel.CurrentVideo?.Thumbnail;
        if (string.IsNullOrWhiteSpace(url))
        {
            ThumbnailImage.Source = null;
            return;
        }

        try
        {
            var bmp = new BitmapImage
            {
                DecodePixelWidth = 320,
                CreateOptions = BitmapCreateOptions.IgnoreImageCache
            };
            bmp.UriSource = new Uri(url);
            ThumbnailImage.Source = bmp;
        }
        catch
        {
            ThumbnailImage.Source = null;
        }
    }

    private async void PasteClipboard_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            var pkg = Clipboard.GetContent();
            if (pkg.Contains(StandardDataFormats.Text))
            {
                var text = await pkg.GetTextAsync();
                if (!string.IsNullOrWhiteSpace(text))
                {
                    ViewModel.UrlInput = text.Trim();
                }
            }
        }
        catch { }
    }

    private void UrlTextBox_KeyDown(object sender, KeyRoutedEventArgs e)
    {
        if (e.Key == VirtualKey.Enter &&
            !Microsoft.UI.Input.InputKeyboardSource.GetKeyStateForCurrentThread(VirtualKey.Shift)
                .HasFlag(Windows.UI.Core.CoreVirtualKeyStates.Down))
        {
            if (ViewModel.ParseCommand.CanExecute(null))
            {
                e.Handled = true;
                ViewModel.ParseCommand.Execute(null);
            }
        }
    }

    private async void BrowseOutputDir_Click(object sender, RoutedEventArgs e)
    {
        if (App.CurrentApp.MainWindow is null)
            return;

        var path = await WindowHelper.PickFolderAsync(App.CurrentApp.MainWindow);
        if (!string.IsNullOrEmpty(path))
            ViewModel.OutputDirectory = path;
    }

    private async void BrowseCookieFile_Click(object sender, RoutedEventArgs e)
    {
        if (App.CurrentApp.MainWindow is null)
            return;

        var path = await WindowHelper.PickCookieFileAsync(App.CurrentApp.MainWindow);
        if (!string.IsNullOrEmpty(path))
            ViewModel.ImportExternalCookieFile(path);
    }

    private void OpenCookieLogin_Click(object sender, RoutedEventArgs e)
    {
        if (_cookieLoginWindow is not null)
        {
            _cookieLoginWindow.Activate();
            return;
        }

        var suggestedUrl = ViewModel.GetSuggestedLoginUrl();
        var win = new CookieLoginWindow(App.CurrentApp.CookieManagerService, suggestedUrl);
        win.CookiesExtracted += inspection =>
        {
            DispatcherQueue.TryEnqueue(() => ViewModel.OnBuiltinCookiesExtracted(inspection));
        };
        win.Closed += (_, _) => _cookieLoginWindow = null;
        _cookieLoginWindow = win;
        win.Activate();
    }

    private void FormatList_ItemClick(object sender, ItemClickEventArgs e)
    {
        if (e.ClickedItem is FormatOption option)
        {
            ViewModel.SelectFormat(option);
        }
    }

    private void CopyCommand_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            var dp = new DataPackage();
            dp.SetText(ViewModel.CommandPreview);
            Clipboard.SetContent(dp);
        }
        catch { }
    }
}
