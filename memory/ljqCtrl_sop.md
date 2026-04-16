# ljqCtrl Usage and Coordinate Conversion SOP

> **Must call update working ckp**: `ljqCtrl must exclusively use physical coordinates | PyAutoGUI is forbidden | Restore/Activate window horizontally via gw before acting`

## 0. API Quick Reference (Signatures)
- `ljqCtrl.dpi_scale`: float (Scale factor = logical width / physical width)
- `ljqCtrl.SetCursorPos(z)`: Move mouse cursor to logical coordinate `z=(x, y)`
- `ljqCtrl.Click(x, y=None)`: Simulate a click. Supports `Click((x, y))` or `Click(x, y)`
- `ljqCtrl.Press(cmd, staytime=0)`: Simulate a keyboard press. E.g. `Press('ctrl+c')`
- `ljqCtrl.FindBlock(fn, wrect=None, threshold=0.8)`: Find image on screen. Returns `((center_x, center_y), is_found)`
- `ljqCtrl.MouseDClick(staytime=0.05)`: Mouse double click.

## 1. Environment Loading
`../memory` must be appended to the path before the tool module can be imported:
```python
import sys, os, pygetwindow as gw
sys.path.append("../memory")
import ljqCtrl
```

## 2. Core: High-DPI Physical Coordinate Conversion
`ljqCtrl`'s `Click/MoveTo` interfaces accept **physical pixel coordinates**.
When using utilities like `pygetwindow` to acquire window dimensions/positions (logical coordinates), they MUST be divided by the scaling coefficient.

- **Conversion Equation**: `Physical Coordinate = Logical Coordinate / ljqCtrl.dpi_scale`
- **Note**: 3840 (4K) operates merely as a dev machine example; actual physical borders rely deeply upon system environments. Scripts must continually infer dynamic values via `dpi_scale`.

## 3. Window Operation & Click Flow
1. **Activate Window**: Derive targeted window sequences parsing via `gw.getWindowsWithTitle('Title')`, triggering `restore()` and `activate()`.
2. **Coordinate Calculations**:
```python
win = gw.getWindowsWithTitle('WeChat')[0]
# Compute specific points relative to inside window tracking local bounds as logical coordinates (lx, ly)
# Transpose onto physical coords and proceed to click:
px, py = lx / ljqCtrl.dpi_scale, ly / ljqCtrl.dpi_scale
ljqCtrl.Click(px, py)
```

## 4. Pitfall Guidelines
- **⚠️ Always use physical coordinates**: Coords supplied to `ljqCtrl.Click`/`SetCursorPos` MUST be physical points (= screenshot pixel coords). Logical bounds fetched by pygetwindow implicitly mandate initial processing step sequences mapping scaling bounds integrating via `/ dpi_scale`. Inserting logical coords directly is STRICTLY PROHIBITED.
- **Physical Verification**: Prior to orchestrating simulated ops, guarantee targeted windows operate fully inside active foreground matrices via programmatic invocations utilizing `activate()`.
- **Offsets**: Apply analogous `/ dpi_scale` calculations towards strictly all relative offset derivations (e.g. "slide right 10 pixels").
- **Coordinate Alignment**: Physical Coordinate = Screenshot Coordinate; ljqCtrl handles DPI conversions internally; repetitive manual coordinate computations are forbidden.
- **⚠️ Window Coordinate Conversion Trap**: Dimensions output directly tracing via `win32gui.GetWindowRect(hwnd)` envelop bounding edges including titlebars alongside borders padding out framing constructs overlaying raw client regions mapped within screenshots natively tracking pure render extents without Chrome trims. When clicking elements within a screenshot area, invoke transformations via `win32gui.ClientToScreen(hwnd, (0, 0))` yielding client-origins mapped explicitly over targeted screens alongside appending screenshot local displacements natively. Directly appending internal image coords matching upper-left bounds rendered by standard `GetWindowRect` endpoints constitutes PROHIBITED behavior risking massive coordinate detours miscalibrations.
- **⚠️ Win32 DPI Coordinate Trap**: Overlying code ignoring instances launching routines failing to explicitly set `SetProcessDPIAware()` inherently renders bounds queried using `GetWindowRect/ClientToScreen/GetClientRect` strictly across **logical coordinate** scaling dimensions; consequently forcing uniform mappings invoking implementations evaluating formulas enforcing `Location / ljqCtrl.dpi_scale`. Equivalent solution logic entails upfront explicit definitions launching `SetProcessDPIAware()`, proceeding utilizing unadulterated "raw" physical matrices globally discarding blended usage routines mapping physical/logical conversions intermixing scopes improperly. Prohibited.
- **Text Input Processing**: Explicit integrations driving keyboard events omit automated input mapping macros typically encompassing TypeText/SendKeys. Entering text contents demands sequences: execute clicking sequence highlighting targets natively (maybe Triple-Clicks enabling overwrites) mapping `pyperclip.copy('Text Content'); ljqCtrl.Press('ctrl+v')` bindings inserting clipboard buffer data precisely.