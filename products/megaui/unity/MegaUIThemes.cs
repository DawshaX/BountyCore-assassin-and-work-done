using UnityEngine;

namespace MegaUI
{
    /// <summary>The four MegaUI themes. Colors match design-tokens.json exactly.</summary>
    public enum MegaTheme { DarkFantasy, Scifi, Royal, Pixel }

    /// <summary>One theme's full palette (from tokens/design-tokens.json).</summary>
    [System.Serializable]
    public struct MegaPalette
    {
        public Color bg, panel, panel2, ink, muted, accent, accent2, stroke, danger, good, mana;

        public static MegaPalette Get(MegaTheme theme)
        {
            switch (theme)
            {
                case MegaTheme.Scifi:
                    return new MegaPalette
                    {
                        bg = C("#070B14"), panel = C("#0D1526"), panel2 = C("#12203A"),
                        ink = C("#E6F4FF"), muted = C("#6E8BA8"), accent = C("#38E8FF"),
                        accent2 = C("#FF4FD8"), stroke = C("#1E3A5F"), danger = C("#FF4464"),
                        good = C("#3DFFB5"), mana = C("#7A5CFF")
                    };
                case MegaTheme.Royal:
                    return new MegaPalette
                    {
                        bg = C("#F4EFE4"), panel = C("#FFFFFF"), panel2 = C("#F7F3EA"),
                        ink = C("#1C2333"), muted = C("#6B7386"), accent = C("#1F3A6E"),
                        accent2 = C("#C9A227"), stroke = C("#D8D0BE"), danger = C("#B23A3A"),
                        good = C("#2F7D4F"), mana = C("#3F6FD8")
                    };
                case MegaTheme.Pixel:
                    return new MegaPalette
                    {
                        bg = C("#1A1C2C"), panel = C("#2E2E48"), panel2 = C("#3D3D5C"),
                        ink = C("#F4F4F4"), muted = C("#9B9BB5"), accent = C("#FFCD75"),
                        accent2 = C("#41A6F6"), stroke = C("#0D0D1A"), danger = C("#EF7D57"),
                        good = C("#4BC95F"), mana = C("#41A6F6")
                    };
                default: // DarkFantasy
                    return new MegaPalette
                    {
                        bg = C("#14100C"), panel = C("#1E1813"), panel2 = C("#271F17"),
                        ink = C("#F0E6D2"), muted = C("#A8987C"), accent = C("#D4A94E"),
                        accent2 = C("#F2CC7A"), stroke = C("#7A5C2C"), danger = C("#C0392B"),
                        good = C("#4E9A51"), mana = C("#4F7BD8")
                    };
            }
        }

        static Color C(string hex)
        {
            ColorUtility.TryParseHtmlString(hex, out var c);
            return c;
        }
    }
}
