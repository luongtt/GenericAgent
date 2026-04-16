# Vision API SOP

## ⚠️ Prerequisite Rules (Strictly Follow)

1. **Enumerate Windows First**: Before calling vision, you must use `pygetwindow` to enumerate window titles to confirm the target window exists and is activated to the foreground. Do not take screenshots if the window does not exist.
2. **🚫 NO Fullscreen Screenshots**: You must first use `win32gui.GetWindowRect` to fetch the target window coordinates, then use `ImageGrab.grab(bbox=...)` to screenshot the window region. If you can screenshot a sub-region (like a title bar), don't do the whole window. If you screenshot a window, NEVER do full screen. Fullscreen screenshots are disallowed in ALL scenarios.
3. **Avoid Vision If Possible**: If the window title or local OCR (`ocr_utils.py`) can obtain the required info, do not call the Vision API. It saves tokens and is more reliable. Vision is the last resort.

## Quick Usage

### Function Signature
```python
ask_vision(
    image_input,
    prompt: str | None = None,
    timeout: int = 60,
    max_pixels: int = 1_440_000,
) -> str
```

### Example
```python
from vision_api import ask_vision
result = ask_vision("image.png", prompt="Describe the content of the image")  # Path or PIL Image both work
```
Returns `str`: Model's response on success, `Error: ...` on failure.

## Core Parameters
- `image_input`: File path (str/Path) or PIL Image object
- `prompt`: Prompt string (Default: Describe the content of this image in detail)
- `max_pixels`: Max pixel count (Default 1,440,000, autoscales if exceeded)
- `timeout`: Timeout in seconds (Default 60)

## Troubleshooting
| Issue | Solution |
|------|--------|
| Import Fails | Check if `../../mykey.py` exists (only existence check, no content reading) |
| Timeout | Increase `timeout` or decrease `max_pixels` |
| Format Error | Ensure a PIL-supported format is used (PNG/JPG/GIF etc.) |

## Key Risks & Pitfalls (L3 Caveats)
- **No Retry Mechanism**: `vision_api.py` does not internally implement API error retries (e.g. 503, timeout). When using it in an automated flow, **you must manually implement retry logic in the upper-layer code** (exponential backoff recommended), otherwise occasional network issues will crash the task immediately.
- **API Config**: Currently using `claude_config141` (ncode.vkm2.com, verified). Backup available: `native_claude_config2/84/5535`. If it expires, manually change `cfg = mk.claude_configXXX` inside `vision_api.py`.

---
Updated: 2025-07-18 | Fix oai_config import + unify string return type
Updated: 2026-02-18 | Default backend changed to Claude native API | SOP simplification (removed fluff/merged examples)
Updated: 2026-07 | Fix config (old claude_config8 didn't exist) → switched to claude_config141
