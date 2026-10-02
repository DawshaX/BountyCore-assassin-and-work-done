using UnityEngine;
using UnityEngine.UI;

namespace MegaUI
{
    /// <summary>
    /// Smooth status-bar driver (HP / mana / XP / cooldowns).
    /// Assign an Image set to Filled type, then call SetValue(0..1).
    /// Optional segment count snaps the fill to hard chunks — matches the
    /// segmented bars in the PNG/SVG kit.
    /// </summary>
    [RequireComponent(typeof(Image))]
    public class MegaUIBar : MonoBehaviour
    {
        [Tooltip("Filled-type image that grows with the value")]
        public Image fillImage;
        [Tooltip("0 = empty, 1 = full")]
        [Range(0f, 1f)] public float value = 1f;
        [Tooltip("Lerp speed; higher = snappier")]
        public float speed = 8f;
        [Tooltip(">0 snaps fill into that many hard segments (segmented style)")]
        public int segments = 0;
        [Tooltip("Optional label showing e.g. '82%'")]
        public Text label;

        float _shown;

        void Awake()
        {
            if (fillImage == null) fillImage = GetComponent<Image>();
            _shown = value;
            Apply(_shown);
        }

        public void SetValue(float v) => value = Mathf.Clamp01(v);

        public void SetValue(float v, bool instant)
        {
            SetValue(v);
            if (instant) { _shown = value; Apply(_shown); }
        }

        void Update()
        {
            if (Mathf.Abs(_shown - value) > 0.0005f)
            {
                _shown = Mathf.Lerp(_shown, value,
                    1f - Mathf.Exp(-speed * Time.unscaledDeltaTime));
                Apply(_shown);
            }
        }

        void Apply(float v)
        {
            if (fillImage == null) return;
            float shown = v;
            if (segments > 1)
            {
                float seg = Mathf.Ceil(v * segments) / segments;
                shown = Mathf.Clamp01(seg);
            }
            fillImage.fillAmount = shown;
            if (label != null) label.text = Mathf.RoundToInt(v * 100f) + "%";
        }
    }
}
