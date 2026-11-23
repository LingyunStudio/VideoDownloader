using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media.Imaging;
using VideoDownloader.Helpers;
using VideoDownloader.ViewModels;

namespace VideoDownloader.Views;

public sealed partial class SettingsPage : Page
{
    public SettingsViewModel ViewModel => App.CurrentApp.SettingsViewModel;

    public SettingsPage()
    {
        InitializeComponent();
        LoadBrandLogo();
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
