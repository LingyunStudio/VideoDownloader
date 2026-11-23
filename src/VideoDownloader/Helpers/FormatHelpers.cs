using System.Globalization;

namespace VideoDownloader.Helpers;

public static class FormatHelpers
{
    private static readonly string[] SizeUnits = ["B", "KB", "MB", "GB", "TB", "PB"];

    public static string HumanSize(long bytes) =>
        bytes <= 0 ? "—" : HumanSize((double)bytes);

    public static string HumanSize(long? bytes) =>
        bytes is null or <= 0 ? "—" : HumanSize((double)bytes.Value);

    public static string HumanSize(double bytes)
    {
        if (bytes <= 0 || double.IsNaN(bytes) || double.IsInfinity(bytes))
            return "—";

        int unit = 0;
        double val = bytes;
        while (val >= 1024.0 && unit < SizeUnits.Length - 1)
        {
            val /= 1024.0;
            unit++;
        }
        return unit == 0
            ? $"{val:0} {SizeUnits[unit]}"
            : $"{val:0.0} {SizeUnits[unit]}";
    }

    public static string HumanSpeed(double bytesPerSec)
    {
        if (bytesPerSec <= 0 || double.IsNaN(bytesPerSec) || double.IsInfinity(bytesPerSec))
            return string.Empty;
        return $"{HumanSize(bytesPerSec)}/s";
    }

    public static string HumanDuration(double? seconds)
    {
        if (seconds is null or <= 0 || double.IsNaN(seconds.Value))
            return "—";

        var total = (long)Math.Round(seconds.Value);
        var h = total / 3600;
        var m = (total % 3600) / 60;
        var s = total % 60;
        return h > 0 ? $"{h}:{m:D2}:{s:D2}" : $"{m}:{s:D2}";
    }

    public static string HumanCount(long? count)
    {
        if (count is null or < 0)
            return "—";
        long c = count.Value;
        if (c >= 100_000_000)
            return $"{c / 100_000_000.0:0.0}亿";
        if (c >= 10_000)
            return $"{c / 10_000.0:0.0}万";
        return c.ToString("N0", CultureInfo.InvariantCulture);
    }

    public static string FormatUploadDate(string? yyyymmdd)
    {
        if (string.IsNullOrWhiteSpace(yyyymmdd) || yyyymmdd.Length != 8)
            return string.Empty;
        return $"{yyyymmdd[..4]}-{yyyymmdd[4..6]}-{yyyymmdd[6..8]}";
    }

    public static string CodecLabel(string? codec)
    {
        if (string.IsNullOrWhiteSpace(codec) || codec.Equals("none", StringComparison.OrdinalIgnoreCase))
            return "—";

        var c = codec.Trim().ToLowerInvariant();
        if (c.StartsWith("avc1") || c.StartsWith("avc3") || c.StartsWith("h264"))
            return "H.264";
        if (c.StartsWith("hev1") || c.StartsWith("hvc1") || c.StartsWith("h265") || c.StartsWith("hevc"))
            return "H.265";
        if (c.StartsWith("av01") || c.StartsWith("av1"))
            return "AV1";
        if (c.StartsWith("vp09") || c.StartsWith("vp9"))
            return "VP9";
        if (c.StartsWith("vp8"))
            return "VP8";
        if (c.StartsWith("mp4a"))
            return "AAC";
        if (c.StartsWith("opus"))
            return "Opus";
        if (c.StartsWith("vorbis"))
            return "Vorbis";
        if (c.StartsWith("flac"))
            return "FLAC";
        if (c.StartsWith("ac-3") || c.StartsWith("ac3"))
            return "AC-3";
        if (c.StartsWith("ec-3"))
            return "E-AC-3";

        return c.Length > 8 ? c[..8].ToUpperInvariant() : c.ToUpperInvariant();
    }

    public static int CompareVersions(string? a, string? b)
    {
        var pa = ParseVersionParts(a);
        var pb = ParseVersionParts(b);
        int len = Math.Max(pa.Length, pb.Length);
        for (int i = 0; i < len; i++)
        {
            int va = i < pa.Length ? pa[i] : 0;
            int vb = i < pb.Length ? pb[i] : 0;
            if (va != vb)
                return va.CompareTo(vb);
        }
        return 0;
    }

    public static bool IsNewerVersion(string? latest, string? current)
    {
        if (string.IsNullOrWhiteSpace(latest))
            return false;
        return CompareVersions(latest, current) > 0;
    }

    private static int[] ParseVersionParts(string? s)
    {
        if (string.IsNullOrWhiteSpace(s))
            return [0];
        var cleaned = s.Trim().TrimStart('v', 'V');
        var tokens = cleaned.Split(['.', '-', '+', ' '], StringSplitOptions.RemoveEmptyEntries);
        var result = new int[tokens.Length];
        for (int i = 0; i < tokens.Length; i++)
        {
            int num = 0;
            foreach (char ch in tokens[i])
            {
                if (ch is >= '0' and <= '9')
                    num = num * 10 + (ch - '0');
                else
                    break;
            }
            result[i] = num;
        }
        return result;
    }
}
