# TMWebDriver SOP

- Forbidden to import directly, use `web_scan`/`web_execute_js` tools. This file records features and pitfalls.
- Low-level: `../TMWebDriver.py` takes over user's browser via Chrome extension (not Tampermonkey) (keeps Login State/Cookies)
- Not Selenium/Playwright; retains user browser logged-in state.
- ⚠ Ext update won't reload content scripts in old tabs → page refresh required.

## General Features
- ⚠ When using `await` in `web_execute_js`, you must **explicitly `return`** to get a value (due to underlying async wrapper, no return gives null).
- ✅ `web_scan` automatically penetrates same-origin iframes; cross-origin iframes require CDP or postMessage (see section below).

## Restrictions (isTrusted)
- JS event `isTrusted=false`: sensitive ops (like file upload/certain buttons) may be blocked; **CDP Bridge** is preferred for these scenarios.
- ⚠ JS button clicking doesn't open a new tab → may be blocked by browser popup blockers, try clicking via CDP instead.
- File upload: JS cannot populate `<input type=file>`. Preferred: CDP batch (getDocument → querySelector → DOM.setFileInputFiles). Backup: `ljqCtrl` physical click.
- When generating physical coordinates: `physX = (screenX + rect centerX) * dpr`, `physY = (screenY + chromeH + rect centerY) * dpr`; where `chromeH = outerHeight - innerHeight`.

## Navigation
- `web_scan` strictly reads current page and doesn't navigate. Change websites using `web_execute_js` + `location.href='url'`.

## Google Image Search
- Class names are obfuscated; hard-coding is forbidden. Click results via `[role=button]` div.
- `web_scan` filters out sidebars. After popup, use JS: Text `document.body.innerText`, traverse `img` for largest image `naturalWidth` for src.
- "Visit" link: Traverse `a` to find href where `textContent.includes('Visit')` or similar depending on the local language.
- Thumbnails: Extract `img[src^="data:image"]` directly. Large image src might be truncated so `return img.src` in JS.

## Chrome PDF Download
Scenario: PDF link previews in browser instead of downloading
```js
fetch('PDF_URL').then(r=>r.blob()).then(b=>{
  const a=document.createElement('a');
  a.href=URL.createObjectURL(b);
  a.download='filename.pdf';
  a.click();
});
```
Note: Must be same-origin or CORS permitted. For cross-origin, navigate to target domain before execution.

## Chrome Background Tab Throttling
- `setTimeout` in background tabs is throttled by Chrome intensive throttling to ≥1min/time. Avoid relying on `setTimeout` polling in extension scripts.

## CDP Bridge (tmwd_cdp_bridge extension) ⭐Preferred
Extension path: `assets/tmwd_cdp_bridge/` (needs to be installed, contains debugger permissions)
⚠ TID convention: Automatically generated to `assets/tmwd_cdp_bridge/config.js` on first run (gitignored), referenced via manifest.
Calls: `web_execute_js` passes JSON string directly to `script` (Tool layer auto detects object format, routing via WS→background.js cmd).
```js
// Pass JSON string directly as script param, no DOM ops needed
web_execute_js script='{"cmd": "cookies"}'
web_execute_js script='{"cmd": "tabs"}'
web_execute_js script='{"cmd": "cdp", "tabId": N, "method": "...", "params": {...}}'
web_execute_js script='{"cmd": "batch", "commands": [...]}'
// Return value is pure JSON result
```
Comm Mode: ⭐JSON string direct passing (Preferred) | TID DOM Mode (TID elem + MutationObserver, historically relied upon by web_scan/execute_js)
Single cmds: `{cmd:'tabs'}`, `{cmd:'cookies'}`, `{cmd:'cdp', tabId:N, method:'...', params:{...}}`, `{cmd:'management', method:'list|reload|disable|enable', extId:'...'}`
- management: list returns all extension info; reload/disable/enable requires extId.
- ⭐ batch mix: `{cmd:'batch', commands:[{cmd:'cookies'},{cmd:'tabs'},{cmd:'cdp',...},...]}`
  - Returns `{ok:true, results:[...]}`, allowing multi-commands in one request, lazy attaching CDP for session reuse.
  - Subcommands auto inherit the tabId of the outer batch (e.g. `cookies` cmd can accurately get current page URL).
  - `$N.path` references the Nth result field (0-indexed), e.g., `"nodeId":"$2.root.nodeId"`.
  - ⚠ If a preceding batch command fails, subsequent `$N` references silently turn `undefined`. Check the `ok` status of each item in the results array.
  - Typical file upload: `getDocument(depth:1)` → `querySelector(input[type=file])` → `setFileInputFiles`
  - Ideas:
    - Retain nodeId consistency inside a single chain. Do not mix `querySelector` path with `performSearch` path.
    - Front-end frameworks might not detect the upload. Manually dispatch `input`/`change` events via JS if necessary.
    - Verify `input.accept` before uploading; distinguish multi-inputs using accept attributes or parent semantics.
    - To await elements, lightweight polling via `DOM.performSearch('input[type=file]')` is preferred.
    - Core logic of short-lived inputs is **minimizing discovery until setFileInputFiles window**. Try in the same batch, fallback to DOM event listeners. Monkey patching is an absolute last resort.
  - ⚠ tabId: Default CDP is sender.tab.id (currently injected page). Cross-tabs need explicit tabId or nested batch using `tabs` to check.
- ⭐ Cross-tab background access: Operating on background tabs is possible by specifying `tabId`.

## Entire CDP Click Lifecycle (Unverified, BBS#23)
- Generic click entails **a 3-event sequence**: mouseMoved → mousePressed → mouseReleased (50-100ms interval).
  - Omitting `mouseMoved` might invalidate hover-dependent elements like MUI Tooltips / Ant Design Dropdowns.
  - ⚠ Autofill release is an exception: Requires only `mousePressed` (see Autofill section below).
- Coordinate patching (When page has transform:scale/zoom):
  ```js
  var scale = window.visualViewport ? window.visualViewport.scale : 1;
  var zoom = parseFloat(getComputedStyle(document.documentElement).zoom) || 1;
  var realX = x * zoom; var realY = y * zoom;
  ```
- Clicking elements within an iframe via CDP require relative syntheses: `finalX = iframeRect.x + elRect.x`.
  - Cross-origin iframes cannot acquire contentDocument.
  - ⚠ `Target.getTargets`/`Target.attachToTarget` returns "Not allowed" in CDP bridge (restricted by chrome.debugger perms).
  - ⭐ **Verified Scheme**: `Page.getFrameTree` to find iframe frameId → `Page.createIsolatedWorld({frameId})` to acquire contextId → `Runtime.evaluate({expression, contextId})` executes JS in iframe.
  - Batch chained reference approach: Use `$0.frameTree.childFrames` traversals finding matching frame URLs, then mapping `$1.executionContextId` to evaluate.
  - postMessage relays only operate if content scripts are already injected into the iframe (3rd party payment iframes are often unaided).

## CDP Text Input (Unverified, BBS#23)
- `insertText` is fast but drops key events. Controlled inputs dictate patching `input` event dispatch mappings.
- Rely on `dispatchKeyEvent` sequences for rigorous full keyboard mocking.

## CDP DOM Layer Penetration over Closed Shadow DOM (Unverified, BBS#24/#25)
- `DOM.getDocument({depth:-1, pierce:true})` penetrates all Shadow demarcations (including closed).
- `DOM.querySelector({nodeId, selector})` locates → `DOM.getBoxModel({nodeId})` pulls coordinates
- getBoxModel yields 8 content points `[x1,y1,...x4,y4]`, utilize the **four point average** to approximate centroids: `centerX=sum(x)/4`, `centerY=sum(y)/4`.
  - ⚠ Simplistic diagonal average logic fails when elements sustain transform:rotate/skew manipulations producing arbitrary shapes.
- querySelector **cannot interpret complex combinators vaulting across Shadow boundaries**, step separately: initially locate host and then inspect components inside its shadow.
- ⚠ `nodeId`s invalidate after DOM augmentations → Prioritize semantic `backendNodeId`s or invoke `getDocument` refreshes.

## Autofill Capture & Login
Detection: `web_scan` yields inputs adorned with `data-autofilled="true"`, wherein value shows a dummy obfuscated placeholder (not the true string, blocked by Chrome security limits requiring manual physical click simulation interactions to unseal).
- ⚠ **Prerequisite Criterion: CDP `Page.bringToFront` MUST forcibly foreground tab**, since Chrome releases protected autofill credentials merely in foregrounded tabs, ignoring actions to background environments.
- ⭐ **One-Click Seal Breach & Auth Launch**: `bringToFront` → `mousePressed` clicking any particular field (no `Released` reqs needed, a single prod unlocks the entire page) → Sleep 500ms → Synthetic DOM inject `input`/`change` event cascades → Proc Login trigger.

## Captcha/Visual Page Snapshot Methods
- ⭐ Top Preference CDP Screenshots: Use `Page.captureScreenshot` (format: 'png') to extract base64 encodings directly. Works across un-foreground context boundaries providing high-res frames.
- Captcha canvas/img blocks: Read JS instances optimally using pristine `canvas.toDataURL()` buffers.

## simphtml & TMWebDriver Tuning Guidelines
- `simphtml` diagnostics warrant injecting scripts into standard browser engines via `code_run` operations (since pure Python modules fake DOM structures feebly).
- Routine setups: `d=TMWebDriver()`, `d.set_session('url_pattern')`, `d.execute_js(code)` → Emits `{'data': value}`.
- `simphtml`: Execution routines leveraging `str(simphtml.optimize_html_for_tokens(html))` (where return types mandate conversion via `str()` casting due to BS4 tag constructs).
- ⚠ **DOMRect Overlap Discrepancies**: Occasional contextual execution traces omit `rect.x/y` attributes yielding NaN returns over bounds comparisons (exclusively emitting left/top). Patch fixes via implementation parsing logic routines: e.g. `rect.x ?? rect.left`.

## Connection Troubleshooting Overviews
Address `web_scan` linkage failures procedurally:
① Extensions lacking? → Query extensions panel (chrome://extensions) examining if TMWebDriver persists.
  Missing → Pursue integrations outlined inside `web_setup_sop`; Situated → Validate enabled parameters.
② Browsers inactive? → Correlate active process threads verifying binaries (tasklist/ps) execution cycles, launching fresh if uninitialized traversing standard site scopes (⚠ Ignore initial internal system views viz. about:blank implementations loading no resources).
③ WS Background termination? → Verifying `socket.connect_ex(('127.0.0.1',18766))` failure conditions yielding nonzero traces denoting dead endpoints → Spawning ad-hoc resets manually initiating via CLI: `from TMWebDriver import TMWebDriver; TMWebDriver()` to seed master logic instances.
