# Web Toolchain Initialization Execution SOP

⚠ **Currently, only installing the `assets/tmwd_cdp_bridge` Chrome extension is required. The Tampermonkey solution will be removed in the future.**

If `web_scan` and `web_execute_js` have been tested and are available, there is no need to execute this SOP.
Only for scenarios during initial installation where `code_run` is available but web tools are not yet configured.

## Goal
Establish Web interactive capabilities (`web_scan` / `web_execute_js`) when only possessing system-level permissions (`code_run`).

## Prerequisite: Detect Browser
```python
import shutil, subprocess
browser = "chrome" if shutil.which("chrome") else "msedge"  # Edge is built-in and must exist. Chrome is optional.
```

## Phase 1: Install Tampermonkey (Manual)
**Status**: Automation not yet implemented; requires manual user interaction.
1. Use `start` to open the extension store page (auto-adapts to browser):
   - Chrome: `start "" "https://chromewebstore.google.com/detail/tampermonkey-beta/gcalenpjmijncebpfijmoaglllgpjagf"`
   - Edge: `start "" "https://microsoftedge.microsoft.com/addons/detail/tampermonkey/iikmkjmpaadaobahmlepeloendndfphd"`
2. Prompt the user to click "Install" and confirm.

## Phase 1.5: Enable "Allow access to file URLs"
**Prerequisite**: TM is installed, but Chrome might not enable this permission by default.
Need to open TM's extension details page and manually toggle the relevant switch.

### Auto-open Details Page
1. Read TM Extension ID from the file system:
   ```python
   import os, json, glob
   ext_dir = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Extensions')
   for eid in os.listdir(ext_dir):
       for ver in glob.glob(os.path.join(ext_dir, eid, '*')):
           mf = os.path.join(ver, 'manifest.json')
           if os.path.isfile(mf):
               with open(mf, encoding='utf-8') as f:
                   m = json.load(f)
               if 'tampermonkey' in m.get('name','').lower() or 'tampermonkey' in m.get('description','').lower():
                   tm_id = eid; break
   ```
2. Navigate to `chrome://extensions/?id={tm_id}`:
   - ⚠️ `chrome://` protocols cannot be opened via command-line arguments or JS (`window.open`).
   - ✅ Use `ljqCtrl` (needs to open a Chrome window and bring to top first) or Clipboard + Address Bar approach:
     ```python
     # Clipboard approach: Write URL → Ctrl+L → Ctrl+V → Enter
     import win32clipboard
     win32clipboard.OpenClipboard(); win32clipboard.EmptyClipboard()
     win32clipboard.SetClipboardText(f'chrome://extensions/?id={tm_id}')
     win32clipboard.CloseClipboard()
     # Then use ljqCtrl or SendKeys to send Ctrl+L, Ctrl+V, Enter
     ```
3. Prompt the user to enable the "Allow access to file URLs" switch on the details page.

## Phase 1.6: Configure Tampermonkey CSP Settings
**Purpose**: Remove website CSP headers so `web_execute_js` can uniformly inject and execute on all pages.
**Path**: TM Control Panel → Settings → Configuration mode select "Advanced" → Modify Content Security Policy (CSP) headers → Select "Remove entirely" → **Click Save button**
- ⚠️ Advanced settings do not auto-save; you must manually click the "Save" button at the bottom of the page, otherwise the config won't take effect.

## Phase 2: Install ljq_web_driver.user.js
**Script Path**: `../assets/ljq_web_driver.user.js`

### Option A (Automated, Preferred)
Local HTTP server + TM intermediate page, opened with the `start` command:
1. Python starts `http.server` to host the script (Content-Type: text/javascript)
   - ⚠️ MUST use `Popen(..., stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)` to discard output.
   - ❌ Disable `stdout=PIPE` or `stderr=PIPE`; it will cause the server to block and return empty responses after the buffer gets full.
   - On Windows, add `creationflags=subprocess.CREATE_NO_WINDOW` to avoid popups.
2. `start "" "https://www.tampermonkey.net/script_installation.php#url=http://127.0.0.1:{port}/ljq_web_driver.user.js"`
   - ⚠️ The above steps MUST be executed non-blockingly using `Popen`. `subprocess.run` is forbidden (it waits for the process to finish).
   - The server needs to keep running until the user completes installation. Use `Popen` to launch and return immediately to continue execution.
3. TM instantly pops up installation confirmation. The user clicks "Install".

### Option B (Manual fallback)
If Option A fails, use the clipboard:
1. Read script content → `pyperclip.copy()`
2. Notify the user to [Create a new script → Select All → Paste → Save] inside TM.

## Phase 3: Verification
Call `web_scan` or inject a JS heartbeat check to confirm the script is active.

## Pitfalls (Chromium 'untrusted' interception)
- ❌ Direct navigation to `localhost/.user.js` → Chromium triggers an 'untrusted' intercept block + "Save As", delaying ~1 minute.
- ✅ MUST use the `start` command (system level) to open the TM intermediate page URL → Installation popup triggers instantly without interception.
- This issue persists in both Chrome and Edge (a common Chromium engine flaw).