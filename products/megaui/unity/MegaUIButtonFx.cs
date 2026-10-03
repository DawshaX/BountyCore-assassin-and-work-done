using UnityEngine;
using UnityEngine.EventSystems;

namespace MegaUI
{
    /// <summary>
    /// Button "juice": scales down on press, pops on release, eases on hover.
    /// Attach next to any Button (uGUI). Motion only — no color overrides,
    /// so it stays compatible with MegaUIThemeSwitcher.
    /// </summary>
    public class MegaUIButtonFx : MonoBehaviour,
        IPointerDownHandler, IPointerUpHandler,
        IPointerEnterHandler, IPointerExitHandler
    {
        [Range(0.7f, 1f)] public float pressedScale = 0.93f;
        [Range(1f, 1.15f)] public float hoverScale = 1.04f;
        public float speed = 14f;

        Vector3 _one;
        Vector3 _target;
        bool _hover, _down;

        void Awake()
        {
            _one = transform.localScale;
            _target = _one;
        }

        public void OnPointerDown(PointerEventData e)
        {
            _down = true;
            _target = _one * pressedScale;
        }

        public void OnPointerUp(PointerEventData e)
        {
            _down = false;
            _target = _one * (_hover ? hoverScale : 1f);
        }

        public void OnPointerEnter(PointerEventData e)
        {
            _hover = true;
            if (!_down) _target = _one * hoverScale;
        }

        public void OnPointerExit(PointerEventData e)
        {
            _hover = false;
            if (!_down) _target = _one;
        }

        void OnDisable()
        {
            _hover = _down = false;
            if (_one != Vector3.zero) transform.localScale = _one;
        }

        void Update()
        {
            transform.localScale = Vector3.Lerp(
                transform.localScale, _target,
                1f - Mathf.Exp(-speed * Time.unscaledDeltaTime));
        }
    }
}
