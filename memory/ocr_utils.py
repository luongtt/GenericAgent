"""
# Local OCR tool
# - OCR engine: rapidocr-onnxruntime (~1s/time, high accuracy for Chinese and English, includes bbox)
# - Issue (rapid): result[i][2] conf is str not float
# - Issue (rapid): Returns None instead of empty list when no text is found
# - Issue: enhance enlargement+high contrast processing is harmful to clear text, disabled by default
# - Issue (Remote Desktop): ImageGrab/mss screenshots are fully black after RDP disconnection, use ocr_window(hwnd) instead
"""
import re
from PIL import ImageGrab, Image, ImageEnhance

_LANG = 'zh-Hans-CN'
_rapid_engine = None

def _get_rapid():
    global _rapid_engine
    if _rapid_engine is None:
        from rapidocr_onnxruntime import RapidOCR
        _rapid_engine = RapidOCR()
    return _rapid_engine

def _preprocess(img, scale=3, contrast=3.0):
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = img.resize((img.width * scale, img.height * scale))
    return img

def _strip_cjk_spaces(t):
    return re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', t)

def _ocr_rapid(img):
    import numpy as np
    engine = _get_rapid()
    arr = np.array(img)
    result, elapse = engine(arr)
    if not result:
        return {'text': '', 'lines': [], 'details': []}
    lines = [r[1] for r in result]
    details = [{'bbox': r[0], 'text': r[1], 'conf': float(r[2])} for r in result]
    text = _strip_cjk_spaces('\n'.join(lines))
    return {'text': text, 'lines': [_strip_cjk_spaces(l) for l in lines], 'details': details}

def ocr_image(image_input, lang=_LANG, enhance=False, engine=None):
    """
    Perform OCR on a PIL Image
    :param image_input: PIL Image object or file path (str)
    :param lang: Reserved parameter, currently unused
    :param enhance: Pre-process
    :param engine: Reserved parameter, currently only supports rapid/None
    :return: dict {'text': full text, 'lines': [line text], 'details': [bbox+conf]}
    """
    if isinstance(image_input, str):
        image_input = Image.open(image_input)
    if enhance:
        image_input = _preprocess(image_input)
    if engine not in (None, 'rapid'):
        raise ValueError("Only rapid OCR is supported")
    return _ocr_rapid(image_input)

def ocr_screen(bbox=None, lang=_LANG, enhance=False, engine=None):
    """
    Capture screen area and perform OCR
    :param bbox: (x1, y1, x2, y2) pixel coordinates, None=full screen
    :return: dict {'text': full text, 'lines': [line text], 'details': [bbox+conf](rapid only)}
    """
    img = ImageGrab.grab(bbox=bbox)
    return ocr_image(img, lang, enhance, engine)

def ocr_window(hwnd, lang=_LANG, enhance=False, engine=None):
    """
    Capture window and perform OCR (Uses PrintWindow API, supports remote desktop disconnect scenarios)
    :param hwnd: Window handle (int)
    :return: dict {'text': full text, 'lines': [line text], 'details': [bbox+conf](rapid only)}
    """
    import win32gui, win32ui
    from ctypes import windll
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    w, h = r - l, b - t
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    return ocr_image(img, lang, enhance, engine)

if __name__ == "__main__":
    r = ocr_screen((0, 0, 400, 100))
    print(f"Recognition result: {r['text']}")
    for line in r['lines']:
        print(f"  Line: {line}")
    if 'details' in r:
        for d in r['details']:
            print(f"  [{d['conf']:.3f}] {d['text']}")