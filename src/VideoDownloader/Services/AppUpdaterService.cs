using System.Diagnostics;
using System.Text.Json;
using VideoDownloader.Helpers;

namespace VideoDownloader.Services;

public readonly record struct AppUpdateCheckResult(
    string CurrentVersion,
    string LatestVersion,
    bool UpdateAvailable,
    string InstallerUrl,
    string ReleaseNotesUrl);

public sealed class AppUpdaterService
{
    public const string CurrentVersion = "3.0.1";
    private const string LatestReleaseApi = "https://api.github.com/repos/LingyunStudio/VideoDownloader/releases/latest";
    private const string InstallerAssetName = "VideoDownloader_Setup.exe";

    public async Task<AppUpdateCheckResult> CheckForUpdateAsync(CancellationToken ct = default)
    {
        using var req = new HttpRequestMessage(HttpMethod.Get, LatestReleaseApi);
        req.Headers.Accept.ParseAdd("application/vnd.github+json");
        using var resp = await HttpClientProvider.Shared.SendAsync(req, ct);
        resp.EnsureSuccessStatusCode();

        await using var stream = await resp.Content.ReadAsStreamAsync(ct);
        using var doc = await JsonDocument.ParseAsync(stream, cancellationToken: ct);
        var root = doc.RootElement;

        var tag = root.TryGetProperty("tag_name", out var tagEl) ? tagEl.GetString()?.Trim() ?? "" : "";
        var latest = tag.TrimStart('v', 'V');
        var htmlUrl = root.TryGetProperty("html_url", out var htmlEl) ? htmlEl.GetString() ?? "" : "";
        string installerUrl = "";

        if (root.TryGetProperty("assets", out var assets) && assets.ValueKind == JsonValueKind.Array)
        {
            foreach (var asset in assets.EnumerateArray())
            {
                var name = asset.TryGetProperty("name", out var nEl) ? nEl.GetString() : null;
                if (name is not null && name.Equals(InstallerAssetName, StringComparison.OrdinalIgnoreCase))
                {
                    installerUrl = asset.TryGetProperty("browser_download_url", out var uEl) ? uEl.GetString() ?? "" : "";
                    break;
                }
            }
        }

        bool needsUpdate = FormatHelpers.IsNewerVersion(latest, CurrentVersion);
        return new AppUpdateCheckResult(CurrentVersion, latest, needsUpdate, installerUrl, htmlUrl);
    }

    public async Task<string> DownloadInstallerAsync(
        string url,
        IProgress<DownloadProgressInfo>? progress = null,
        CancellationToken ct = default)
    {
        var dir = Path.Combine(AppLogger.AppDataDirectory, "updates", "app");
        Directory.CreateDirectory(dir);
        var dest = Path.Combine(dir, InstallerAssetName);

        using var resp = await HttpClientProvider.Shared.GetAsync(url, HttpCompletionOption.ResponseHeadersRead, ct);
        resp.EnsureSuccessStatusCode();

        long total = resp.Content.Headers.ContentLength ?? 0;
        await using var input = await resp.Content.ReadAsStreamAsync(ct);
        await using var output = new FileStream(dest, FileMode.Create, FileAccess.Write, FileShare.None, 81920, useAsync: true);

        var buffer = new byte[81920];
        long downloaded = 0;
        long lastTick = Environment.TickCount64;
        int read;
        while ((read = await input.ReadAsync(buffer, ct)) > 0)
        {
            await output.WriteAsync(buffer.AsMemory(0, read), ct);
            downloaded += read;
            long now = Environment.TickCount64;
            if (now - lastTick >= 80)
            {
                progress?.Report(new DownloadProgressInfo(downloaded, total));
                lastTick = now;
            }
        }

        progress?.Report(new DownloadProgressInfo(downloaded, total));
        return dest;
    }

    public void LaunchSilentInstallAndExit(string installerPath)
    {
        var psi = new ProcessStartInfo
        {
            FileName = installerPath,
            Arguments = "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART",
            UseShellExecute = true,
            Verb = "runas"
        };
        Process.Start(psi);
        Environment.Exit(0);
    }
}
