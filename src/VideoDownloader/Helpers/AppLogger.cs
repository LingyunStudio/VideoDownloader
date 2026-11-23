namespace VideoDownloader.Helpers;

public static class AppLogger
{
    private static readonly object Sync = new();
    private static readonly string DataDir;
    private static readonly string TracePath;
    private static readonly string CrashPath;

    static AppLogger()
    {
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
        DataDir = Path.Combine(appData, "VideoDownloader");
        Directory.CreateDirectory(DataDir);
        TracePath = Path.Combine(DataDir, "trace.log");
        CrashPath = Path.Combine(DataDir, "crash.log");

        // Keep trace log compact (< 1 MB)
        try
        {
            var fi = new FileInfo(TracePath);
            if (fi.Exists && fi.Length > 1_048_576)
                fi.Delete();
        }
        catch { }
    }

    public static string AppDataDirectory => DataDir;

    public static void Info(string message)
    {
        WriteLine(TracePath, "INFO", message);
    }

    public static void Warn(string message)
    {
        WriteLine(TracePath, "WARN", message);
    }

    public static void Error(string message, Exception? ex = null)
    {
        var text = ex is null ? message : $"{message} | {ex.GetType().Name}: {ex.Message}\n{ex.StackTrace}";
        WriteLine(TracePath, "ERROR", text);
    }

    public static void Crash(Exception ex, string context = "Unhandled")
    {
        var text = $"[{context}] {ex.GetType().FullName}: {ex.Message}\n{ex.StackTrace}";
        WriteLine(CrashPath, "CRASH", text);
        WriteLine(TracePath, "CRASH", text);
    }

    private static void WriteLine(string path, string level, string message)
    {
        try
        {
            lock (Sync)
            {
                File.AppendAllText(path, $"{DateTime.Now:yyyy-MM-dd HH:mm:ss.fff} [{level}] {message}{Environment.NewLine}");
            }
        }
        catch
        {
            // Never throw from logger
        }
    }
}
