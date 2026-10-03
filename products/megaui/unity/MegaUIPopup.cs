using System.Collections;
using UnityEngine;

namespace MegaUI
{
    /// <summary>
    /// Modal / popup controller: scale + fade in on Show, reverse on Hide.
    /// Works on any GameObject carrying a CanvasGroup (dialogs, toasts, menus).
    /// </summary>
    public class MegaUIPopup : MonoBehaviour
    {
        [Tooltip("Optional; added automatically if missing")]
        public CanvasGroup group;
        [Tooltip("Hidden scale (pop-in starts here)")]
        public float fromScale = 0.85f;
        public float inDuration = 0.22f;
        public float outDuration = 0.16f;
        [Tooltip("Disable raycast blocking while hidden")]
        public bool blockRaycast = true;

        Coroutine _routine;
        Vector3 _one;

        void Awake()
        {
            if (group == null) group = GetComponent<CanvasGroup>();
            if (group == null) group = gameObject.AddComponent<CanvasGroup>();
            _one = transform.localScale;
        }

        public void Show()
        {
            gameObject.SetActive(true);
            Restart(Present(), 1f);
        }

        public void Hide()
        {
            Restart(Absent(), 0f);
        }

        public void Toggle()
        {
            if (group.alpha > 0.5f) Hide(); else Show();
        }

        IEnumerator Present()
        {
            float t = 0f;
            while (t < inDuration)
            {
                t += Time.unscaledDeltaTime;
                float k = Mathf.Clamp01(t / inDuration);
                k = 1f - (1f - k) * (1f - k); // ease-out
                group.alpha = k;
                transform.localScale = Vector3.LerpUnclamped(
                    _one * fromScale, _one, k);
                if (blockRaycast) group.blocksRaycasts = k > 0.9f;
                yield return null;
            }
            group.alpha = 1f;
            transform.localScale = _one;
            if (blockRaycast) group.blocksRaycasts = true;
        }

        IEnumerator Absent()
        {
            float t = 0f;
            while (t < outDuration)
            {
                t += Time.unscaledDeltaTime;
                float k = Mathf.Clamp01(t / outDuration);
                group.alpha = 1f - k;
                transform.localScale = Vector3.LerpUnclamped(
                    _one, _one * fromScale, k);
                if (blockRaycast) group.blocksRaycasts = false;
                yield return null;
            }
            group.alpha = 0f;
            gameObject.SetActive(false);
        }

        void Restart(IEnumerator flow, float alpha)
        {
            if (_routine != null) StopCoroutine(_routine);
            if (group == null) group = gameObject.AddComponent<CanvasGroup>();
            group.alpha = alpha;
            _routine = StartCoroutine(flow);
        }
    }
}
