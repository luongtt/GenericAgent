# Memory Scanner SOP

## 1. Quick Start
Memory footprint scanning tool, supports Hex (CE style) and string matching. Specifically provides LLM mode, facilitating LLM analysis of memory context.

**Python Calling Method:**
```python
import sys
sys.path.append('../memory') # Mount the tool directory directly
from procmem_scanner import scan_memory

# Example: Search specific Hex signature, enable llm_mode to get context
results = scan_memory(pid, "48 8b ?? ?? 00", mode="hex", llm_mode=True)
```

**CLI:**
```powershell
# Basic search
python ../memory/procmem_scanner.py <PID> "pattern" --mode string

# LLM enhanced mode (outputs JSON containing context, recommended)
python ../memory/procmem_scanner.py <PID> "pattern" --llm
```

## 2. Typical Scenario: Locating Structs or Key Data
1. Determine the leading signature or known constants of the target data (e.g., a specific Header or Magic Number).
2. Search this signature in the target process:
   `scan_memory(pid, "4D 5A 90 00", mode="hex", llm_mode=True)`
3. Analyze the `context` field in the returned JSON, view the raw bytes before and after the target address and ASCII previews.

## 3. Notes
- **Permissions**: Administrator privileges are not strictly required, but `PROCESS_QUERY_INFORMATION` and `PROCESS_VM_READ` permissions on the target process are needed.
- **Efficiency**: When searching large blocks of memory, provide a more unique signature to reduce false positives.

## 4. CE-style Diff-scan to Locate Dynamic Fields
Locating memory fields that change with operations in self-drawn UIs like WeChat (e.g., the current session title). Core idea: one full scan + multiple ReadProcessMemory filtering.

**Workflow (3 contacts A/B/C are enough to converge):**
1. Get PID: Weixin.exe has multiple processes, use `win32gui.GetWindowThreadProcessId` to get the one with a window.
2. Current session = A → `scan_memory(pid, "NameA", mode="string")` → Address set S
3. Switch to B → Read all addresses in S → Keep those whose content ≠ "NameA" → Candidate set C
4. Switch to A → Read all addresses in C → Keep those whose content == "NameA" → Candidate set C' (usually 1-3)
5. If C' > 1 → Switch B/C again and repeat → Until unique

**Full code for switching session + reading addresses:**
```python
import sys; sys.path.append('../memory')
import ljqCtrl, pygetwindow as gw, pyperclip, time, ctypes

def switch_chat(name):
    win = gw.getWindowsWithTitle('WeChat')[0]
    if win.isMinimized: win.restore()
    win.activate(); time.sleep(0.3)
    S = 1 / ljqCtrl.dpi_scale
    ljqCtrl.Click(int((win.left+150)*S), int((win.top+40)*S)); time.sleep(0.5)
    pyperclip.copy(name); ljqCtrl.Press('ctrl+v'); time.sleep(1.5)
    ljqCtrl.Click(int((win.left+150)*S), int((win.top+130)*S)); time.sleep(0.8)

def read_addrs(pid, addrs):
    k32 = ctypes.windll.kernel32
    hp = k32.OpenProcess(0x10, False, pid)
    buf = ctypes.create_string_buffer(256)
    rd = ctypes.c_size_t()
    result = {}
    for a in addrs:
        a = int(a, 16) if isinstance(a, str) else a
        k32.ReadProcessMemory(hp, ctypes.c_void_p(a), buf, 256, ctypes.byref(rd))
        result[a] = buf.raw.split(b'\x00')[0].decode('utf-8', errors='ignore').strip()
    k32.CloseHandle(hp)
    return result  # {addr: text}
```

**Pitfalls:**
- Process name is Weixin.exe (not WeChat.exe); address strings should first be `int(addr, 16)`.
- Step 3 filters ≠ A (excluding empty/gibberish), Step 4 filters == A (positive confirmation), alternating is fastest.
- **Searching to switch sessions is fully viable**, most diff-set steps can just use search. Note: the first search result might be an ad, click ≥1.5s after pasting, confirm it's a contact before clicking (or click the 2nd item).
- **Only the final disambiguation step requires clicking the sidebar**: When candidates > 1, click a different person in the sidebar (without going through the search box), use read_addrs to see which address changes accordingly → that is the title bar.
- Use read_addrs to verify the switch was indeed successful before continuing.
- **Steps 3/4 must use read_addrs to read the original address set, strictly NO re-scanning**: Re-scanning will only find static remnants (chat history etc), the dynamic address has changed and won't be in the result, leading to 0 candidates.
- **Use wechat_db_utils.quick_connect to find real people when picking contacts A/B**, to avoid search triggering ad popups (Official Accounts/Mini Programs names will pop ads).
- **scan_memory return format**: Default returns a list of str (each item "Addr:0x...\nHex:..."), not dict. Extract addresses using `[int(r.split('\n')[0].split(':')[1],16) for r in results]`.
- **Sidebar clicking forbids estimating coords**: Session list order changes with messages. Refer to vision_sop + wechat_send_sop flow (Screenshot → ask_vision → Exact coords → Click).