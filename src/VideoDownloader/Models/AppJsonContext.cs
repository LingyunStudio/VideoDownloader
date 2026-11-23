using System.Text.Json.Serialization;

namespace VideoDownloader.Models;

[JsonSourceGenerationOptions(
    WriteIndented = true,
    PropertyNameCaseInsensitive = true,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull)]
[JsonSerializable(typeof(AppSettings))]
[JsonSerializable(typeof(List<HistoryEntry>))]
internal sealed partial class AppJsonContext : JsonSerializerContext
{
}
