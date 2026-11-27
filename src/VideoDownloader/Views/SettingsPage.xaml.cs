using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media.Imaging;
using VideoDownloader.Helpers;
using VideoDownloader.ViewModels;

namespace VideoDownloader.Views;

public sealed partial class SettingsPage : Page
{
    public SettingsViewModel ViewModel => App.CurrentApp.SettingsViewModel;
    private bool? _isWideLayout;

    public SettingsPage()
    {
        InitializeComponent();
        LoadBrandLogo();
        SizeChanged += OnPageSizeChanged;
    }

    private void OnPageSizeChanged(object sender, SizeChangedEventArgs e)
    {
        bool wide = e.NewSize.Width >= 1120;
        if (_isWideLayout == wide)
            return;
        _isWideLayout = wide;

        if (wide)
        {
            SettingsRootGrid.Padding = new Thickness(36, 18, 36, 40);
            SettingsColumnsGrid.ColumnSpacing = 20;
            LeftColumnDef.Width = new GridLength(1, GridUnitType.Star);
            RightColumnDef.Width = new GridLength(1.15, GridUnitType.Star);
            Grid.SetRow(RightSettingsColumn, 0);
            Grid.SetColumn(RightSettingsColumn, 1);
        }
        else
        {
            SettingsRootGrid.Padding = new Thickness(28, 16, 28, 40);
            SettingsColumnsGrid.ColumnSpacing = 0;
            LeftColumnDef.Width = new GridLength(1, GridUnitType.Star);
            RightColumnDef.Width = new GridLength(0);
            Grid.SetRow(RightSettingsColumn, 1);
            Grid.SetColumn(RightSettingsColumn, 0);
        }
    }

    private void LoadBrandLogo()
    {
        var pngPath = WindowHelper.GetAssetPath("Assets", "Icons", "dlp.png");
        if (File.Exists(pngPath))
        {
            AboutLogoImage.Source = new BitmapImage(new Uri(pngPath)) { DecodePixelWidth = 128 };
            return;
        }

        var icoPath = WindowHelper.GetAssetPath("Assets", "Icons", "1.ico");
        if (File.Exists(icoPath))
            AboutLogoImage.Source = new BitmapImage(new Uri(icoPath)) { DecodePixelWidth = 128 };
    }

    private async void BrowseDir_Click(object sender, RoutedEventArgs e)
    {
        if (App.CurrentApp.MainWindow is null)
            return;

        var path = await WindowHelper.PickFolderAsync(App.CurrentApp.MainWindow);
        if (!string.IsNullOrEmpty(path))
            ViewModel.OutputDirectory = path;
    }
}
