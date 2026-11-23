using Microsoft.UI;
using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using Windows.Storage.Pickers;
using WinRT.Interop;

namespace VideoDownloader.Helpers;

public static class WindowHelper
{
    public static nint GetWindowHandle(Window window) => WindowNative.GetWindowHandle(window);

    public static AppWindow GetAppWindow(Window window)
    {
        var hwnd = GetWindowHandle(window);
        var windowId = Win32Interop.GetWindowIdFromWindow(hwnd);
        return AppWindow.GetFromWindowId(windowId);
    }

    public static async Task<string?> PickFolderAsync(Window window)
    {
        var picker = new FolderPicker
        {
            SuggestedStartLocation = PickerLocationId.Downloads
        };
        picker.FileTypeFilter.Add("*");
        InitializeWithWindow.Initialize(picker, GetWindowHandle(window));
        var folder = await picker.PickSingleFolderAsync();
        return folder?.Path;
    }

    public static async Task<string?> PickCookieFileAsync(Window window)
    {
        var picker = new FileOpenPicker
        {
            SuggestedStartLocation = PickerLocationId.Desktop,
            ViewMode = PickerViewMode.List
        };
        picker.FileTypeFilter.Add(".txt");
        InitializeWithWindow.Initialize(picker, GetWindowHandle(window));
        var file = await picker.PickSingleFileAsync();
        return file?.Path;
    }

    public static string GetAssetPath(params string[] relativeParts)
    {
        var baseDir = AppContext.BaseDirectory;
        return Path.Combine([baseDir, .. relativeParts]);
    }
}
