using System.Net;

namespace VideoDownloader.Services;

public static class HttpClientProvider
{
    public const string UserAgent = "VideoDownloader/3.0";

    private static readonly Lazy<HttpClient> SharedInstance = new(() =>
    {
        var handler = new SocketsHttpHandler
        {
            PooledConnectionLifetime = TimeSpan.FromMinutes(5),
            PooledConnectionIdleTimeout = TimeSpan.FromMinutes(2),
            AutomaticDecompression = DecompressionMethods.GZip | DecompressionMethods.Deflate | DecompressionMethods.Brotli,
            MaxConnectionsPerServer = 8
        };

        var client = new HttpClient(handler)
        {
            Timeout = TimeSpan.FromMinutes(10)
        };
        client.DefaultRequestHeaders.UserAgent.ParseAdd(UserAgent);
        return client;
    });

    public static HttpClient Shared => SharedInstance.Value;
}
