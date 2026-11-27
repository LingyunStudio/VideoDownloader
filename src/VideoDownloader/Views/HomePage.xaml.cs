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
    private bool? _isWideLayout;

    public HomePage()
    {
        InitializeComponent();
        ViewModel.PropertyChanged += OnViewModelPropertyChanged;
        SizeChanged += OnPageSizeChanged;
    }

    private void OnPageSizeChanged(object sender, SizeChangedEventArgs e)
    {
        UpdateResponsiveLayout(e.NewSize.Width);
    }

    private void UpdateResponsiveLayout(double width)
    {
        bool wide = width >= 1160;
        if (_isWideLayout == wide)
            return;
        _isWideLayout = wide;

        if (wide)
        {
            PageRootGrid.Padding = new Thickness(36, 18, 36, 36);
            WorkspaceGrid.ColumnSpacing = 20;
            PrimaryColumn.Width = new GridLength(1.45, GridUnitType.Star);
            SecondaryColumn.Width = new GridLength(1, GridUnitType.Star);
            SecondaryColumn.MinWidth = 420;
            SecondaryColumn.MaxWidth = 580;

            Grid.SetRow(AdvancedOptionsExpander, 0);
            Grid.SetColumn(AdvancedOptionsExpander, 1);
            AdvancedOptionsExpander.IsExpanded = true;

            ThumbnailContainer.Width = 304;
            ThumbnailContainer.Height = 171;
            SaveDirTextBlock.MaxWidth = 560;

            PlaylistEntriesListView.MaxHeight = 460;
            VideoFormatsListView.MaxHeight = 460;
            AudioFormatsListView.MaxHeight = 460;
            CombinedFormatsListView.MaxHeight = 460;
        }
        else
        {
            PageRootGrid.Padding = new Thickness(28, 16, 28, 36);
            WorkspaceGrid.ColumnSpacing = 0;
            PrimaryColumn.Width = new GridLength(1, GridUnitType.Star);
            SecondaryColumn.MinWidth = 0;
            SecondaryColumn.MaxWidth = double.PositiveInfinity;
            SecondaryColumn.Width = new GridLength(0);

            Grid.SetRow(AdvancedOptionsExpander, 1);
            Grid.SetColumn(AdvancedOptionsExpander, 0);

            ThumbnailContainer.Width = 264;
            ThumbnailContainer.Height = 148;
            SaveDirTextBlock.MaxWidth = 300;

            PlaylistEntriesListView.MaxHeight = 300;
            VideoFormatsListView.MaxHeight = 340;
            AudioFormatsListView.MaxHeight = 340;
            CombinedFormatsListView.MaxHeight = 340;
        }
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
