using CommunityToolkit.Mvvm.ComponentModel;
using VideoDownloader.Helpers;

namespace VideoDownloader.Models;

public enum FormatGroup
{
    VideoOnly,
    AudioOnly,
    Combined
}

public sealed partial class FormatOption : ObservableObject
{
    public string FormatId { get; init; } = string.Empty;
    public string Ext { get; init; } = string.Empty;
    public int? Width { get; init; }
    public int? Height { get; init; }
    public double? Fps { get; init; }
    public string VCodec { get; init; } = string.Empty;
    public string ACodec { get; init; } = string.Empty;
    public double? Tbr { get; init; }
    public long? FileSize { get; init; }
    public long? FileSizeApprox { get; init; }
    public string Note { get; init; } = string.Empty;
    public bool HasVideo { get; init; }
    public bool HasAudio { get; init; }
    public bool IsRecommended { get; set; }

    [ObservableProperty]
    private bool _isSelected;

    public FormatGroup Group =>
        HasVideo && HasAudio ? FormatGroup.Combined :
        HasVideo ? FormatGroup.VideoOnly :
        FormatGroup.AudioOnly;

    public long EffectiveSize => FileSize ?? FileSizeApprox ?? 0;

    public string ResolutionText
    {
        get
        {
            if (Height is > 0 && Width is > 0)
                return $"{Width}×{Height}";
            if (Height is > 0)
                return $"{Height}p";
            if (Width is > 0)
                return $"{Width}×?";
            return HasAudio ? "纯音频" : "—";
        }
    }

    public string ShortQualityBadge =>
        Height is > 0 ? $"{Height}p" :
        HasAudio ? $"{(Tbr is > 0 ? $"{Math.Round(Tbr.Value)}k" : "音频")}" : "—";

    public string FpsText => Fps is > 0 ? $"{Math.Round(Fps.Value)}fps" : string.Empty;

    public string CodecDisplay
    {
        get
        {
            if (HasVideo && HasAudio)
                return $"{FormatHelpers.CodecLabel(VCodec)} + {FormatHelpers.CodecLabel(ACodec)}";
            if (HasVideo)
                return FormatHelpers.CodecLabel(VCodec);
            if (HasAudio)
                return FormatHelpers.CodecLabel(ACodec);
            return "—";
        }
    }

    public string BitrateText => Tbr is > 0 ? $"{Math.Round(Tbr.Value)} kbps" : "—";

    public string SizeText => FormatHelpers.HumanSize(EffectiveSize > 0 ? EffectiveSize : null);

    public string RecommendedMark => IsRecommended ? "★ 推荐" : string.Empty;

    public string ExtUpper => string.IsNullOrEmpty(Ext) ? "—" : Ext.ToUpperInvariant();

    public string SummaryLine
    {
        get
        {
            var parts = new List<string>(5);
            if (!string.IsNullOrEmpty(Ext))
                parts.Add(ExtUpper);
            if (!string.IsNullOrEmpty(FpsText))
                parts.Add(FpsText);
            if (Tbr is > 0)
                parts.Add(BitrateText);
            if (!string.IsNullOrWhiteSpace(Note))
                parts.Add(Note);
            return string.Join(" · ", parts);
        }
    }
}
