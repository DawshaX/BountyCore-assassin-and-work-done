using UnityEngine;
using UnityEngine.UI;

namespace MegaUI
{
    /// <summary>
    /// One-click theme switcher. Assign your scene's Graphics to the four
    /// role arrays in the Inspector, pick a theme, press Apply (or call
    /// Apply at runtime) — every assigned element recolors instantly.
    /// Colors come from MegaPalette = design-tokens.json.
    /// </summary>
    [ExecuteInEditMode]
    public class MegaUIThemeSwitcher : MonoBehaviour
    {
        [Tooltip("Theme to preview / apply")]
        public MegaTheme theme = MegaTheme.DarkFantasy;

        [Header("Role arrays (assign in Inspector)")]
        [Tooltip("Screen background images -> palette.bg")]
        public Graphic[] backgrounds;
        [Tooltip("Panel / card images -> palette.panel (+ panel2 accents)")]
        public Graphic[] panels;
        [Tooltip("Primary buttons, frames, headers -> palette.accent")]
        public Graphic[] accents;
        [Tooltip("Texts and icons -> palette.ink")]
        public Graphic[] texts;

        [ContextMenu("Apply Theme")]
        public void Apply() => Apply(theme);

        public void Apply(MegaTheme t)
        {
            var p = MegaPalette.Get(t);
            Paint(backgrounds, p.bg);
            Paint(panels, p.panel);
            Paint(accents, p.accent);
            Paint(texts, p.ink);
        }

        public static void Paint(Graphic[] list, Color color)
        {
            if (list == null) return;
            for (int i = 0; i < list.Length; i++)
                if (list[i] != null) list[i].color = color;
        }

#if UNITY_EDITOR
        void OnValidate()
        {
            if (Application.isPlaying == false) Apply();
        }
#endif
    }
}
