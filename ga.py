import sys, os, re, json, time, threading, importlib
from datetime import datetime
from pathlib import Path
import tempfile, traceback, subprocess, itertools, collections, difflib
if sys.stdout is None: sys.stdout = open(os.devnull, "w")
if sys.stderr is None: sys.stderr = open(os.devnull, "w")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_loop import BaseHandler, StepOutcome, json_default

def code_run(code, code_type="python", timeout=60, cwd=None, code_cwd=None, stop_signal=[]):
    """Code executor
    python: Run complex .py scripts (file mode)
    powershell/bash: Run single-line instructions (command mode)
    Prioritize python, only use powershell for necessary system operations.
    """
    preview = (code[:60].replace('\n', ' ') + '...') if len(code) > 60 else code.strip()
    yield f"[Action] Running {code_type} in {os.path.basename(cwd)}: {preview}\n"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cwd = cwd or os.path.join(script_dir, 'temp'); tmp_path = None
    if code_type == "python":
        tmp_file = tempfile.NamedTemporaryFile(suffix=".ai.py", delete=False, mode='w', encoding='utf-8', dir=code_cwd)
        cr_header = os.path.join(script_dir, 'assets', 'code_run_header.py')
        if os.path.exists(cr_header): tmp_file.write(open(cr_header, encoding='utf-8').read())
        tmp_file.write(code)
        tmp_path = tmp_file.name
        tmp_file.close()
        cmd = [sys.executable, "-X", "utf8", "-u", tmp_path]   
    elif code_type in ["powershell", "bash"]:
        if os.name == 'nt': cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command", code]
        else: cmd = ["bash", "-c", code]
    else:
        return {"status": "error", "msg": f"Unsupported type: {code_type}"}
    print("code run output:") 
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0 # SW_HIDE
    full_stdout = []

    def stream_reader(proc, logs):
        try:
            for line_bytes in iter(proc.stdout.readline, b''):
                try: line = line_bytes.decode('utf-8')
                except UnicodeDecodeError: line = line_bytes.decode('gbk', errors='ignore')
                logs.append(line)
                try: print(line, end="") 
                except: pass
        except: pass

    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            bufsize=0, cwd=cwd, startupinfo=startupinfo
        )
        start_t = time.time()
        t = threading.Thread(target=stream_reader, args=(process, full_stdout), daemon=True)
        t.start()

        while t.is_alive():
            istimeout = time.time() - start_t > timeout
            if istimeout or len(stop_signal) > 0:
                process.kill()
                print("[Debug] Process killed due to timeout or stop signal.")
                if istimeout: full_stdout.append("\n[Timeout Error] Force terminated due to timeout")
                else: full_stdout.append("\n[Stopped] Force terminated by user")
                break
            time.sleep(1)

        t.join(timeout=1)
        exit_code = process.poll()

        stdout_str = "".join(full_stdout)
        status = "success" if exit_code == 0 else "error"
        status_icon = "✅" if exit_code == 0 else "❌"
        if exit_code is None: status_icon = "⏳" 
        output_snippet = smart_format(stdout_str, max_str_len=600, omit_str='\n\n[omitted long output]\n\n')
        yield f"[Status] {status_icon} Exit Code: {exit_code}\n[Stdout]\n{output_snippet}\n"
        if process.stdout: threading.Thread(target=process.stdout.close, daemon=True).start()
        return {
            "status": status,
            "stdout": smart_format(stdout_str, max_str_len=10000, omit_str='\n\n[omitted long output]\n\n'),
            "exit_code": exit_code
        }
    except Exception as e:
        if 'process' in locals(): process.kill()
        return {"status": "error", "msg": str(e)}
    finally:
        if code_type == "python" and tmp_path and os.path.exists(tmp_path): os.remove(tmp_path)


def ask_user(question: str, candidates: list = None):
    """question: Question directed to user. candidates: Optional list of candidates. Must ensure should_exit is True
    """
    return {"status": "INTERRUPT", "intent": "HUMAN_INTERVENTION",
        "data": {"question": question, "candidates": candidates or []}}

import simphtml
driver = None
def first_init_driver():
    global driver
    from TMWebDriver import TMWebDriver
    driver = TMWebDriver()
    for i in range(20):
        time.sleep(1)
        sess = driver.get_all_sessions()
        if len(sess) > 0: break
    if len(sess) == 0: return 
    if len(sess) == 1: 
        #driver.newtab()
        time.sleep(3)

def web_scan(tabs_only=False, switch_tab_id=None, text_only=False):
    """
    Get the simplified HTML content and tabs list of the current page. Note: The simplified process filters out sidebars, floating elements, and other non-main content.
    tabs_only: Only return the tabs list, do not get HTML content (to save tokens).
    switch_tab_id: Optional parameter, if provided, switches to this tab before scanning.
    You should use execute_js more often and full HTML observation less.
    """
    global driver
    try:
        if driver is None: first_init_driver()
        if len(driver.get_all_sessions()) == 0:
            return {"status": "error", "msg": "No browser tabs available, check L3 memory to analyze reason."}
        tabs = []
        for sess in driver.get_all_sessions(): 
            sess.pop('connected_at', None)
            sess.pop('type', None)
            sess['url'] = sess.get('url', '')[:50] + ("..." if len(sess.get('url', '')) > 50 else "")
            tabs.append(sess)
        if switch_tab_id: driver.default_session_id = switch_tab_id
        result = {
            "status": "success",
            "metadata": {
                "tabs_count": len(tabs), "tabs": tabs,
                "active_tab": driver.default_session_id
            }
        }
        if not tabs_only: 
            importlib.reload(simphtml); result["content"] = simphtml.get_html(driver, cutlist=True, maxchars=35000, text_only=text_only)
            if text_only: result['content'] = smart_format(result['content'], max_str_len=10000, omit_str='\n\n[omitted long content]\n\n')
        return result
    except Exception as e:
        return {"status": "error", "msg": format_error(e)}
    
def format_error(e):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = traceback.extract_tb(exc_traceback)
    if tb:
        f = tb[-1]
        fname = os.path.basename(f.filename)
        return f"{exc_type.__name__}: {str(e)} @ {fname}:{f.lineno}, {f.name} -> `{f.line}`"
    return f"{exc_type.__name__}: {str(e)}"

def log_memory_access(path):
    if 'memory' not in path: return
    script_dir = os.path.dirname(os.path.abspath(__file__))
    stats_file = os.path.join(script_dir, 'memory/file_access_stats.json')
    try:
        with open(stats_file, 'r', encoding='utf-8') as f: stats = json.load(f)
    except: stats = {}
    fname = os.path.basename(path)
    stats[fname] = {'count': stats.get(fname, {}).get('count', 0) + 1, 'last': datetime.now().strftime('%Y-%m-%d')}
    with open(stats_file, 'w', encoding='utf-8') as f: json.dump(stats, f, indent=2, ensure_ascii=False)

def web_execute_js(script, switch_tab_id=None, no_monitor=False):
    """
    Execute JS script to control browser and capture results and page changes.
    script: The JavaScript code string to execute.
    return {
        "status": "failed" if error_msg else "success",
        "js_return": result,
        "error": error_msg,
        "transients": transients, 
        "environment": {
            "newTabs": [],
            "reloaded": reloaded
        },
        "diff": diff_summary,
    }
    """
    global driver
    try:
        if driver is None: first_init_driver()
        if len(driver.get_all_sessions()) == 0: return {"status": "error", "msg": "No browser tabs available, check L3 memory to analyze reason."}
        if switch_tab_id: driver.default_session_id = switch_tab_id
        result = simphtml.execute_js_rich(script, driver, no_monitor=no_monitor)
        return result
    except Exception as e:
        return {"status": "error", "msg": format_error(e)}

def expand_file_refs(text, base_dir=None):
    """Expand {{file:path:start_line:end_line}} references in text into actual file contents.
    Can be mixed with normal text. Raises ValueError if expansion fails.
    base_dir: Relative base directory, defaults to process cwd."""
    pattern = r'\{\{file:(.+?):(\d+):(\d+)\}\}'
    def replacer(match):
        path, start, end = match.group(1), int(match.group(2)), int(match.group(3))
        path = os.path.abspath(os.path.join(base_dir or '.', path))
        if not os.path.isfile(path): raise ValueError(f"Reference file not found: {path}")
        with open(path, 'r', encoding='utf-8') as f: lines = f.readlines()
        if start < 1 or end > len(lines) or start > end: raise ValueError(f"Line number out of bounds: {path} total {len(lines)} lines, requested {start}-{end}")
        return ''.join(lines[start-1:end])
    return re.sub(pattern, replacer, text)
    
def file_patch(path: str, old_content: str, new_content: str):
    """Find the exact old_content block in the file and replace it with new_content.
    """
    path = str(Path(path).resolve())
    try:
        if not os.path.exists(path): return {"status": "error", "msg": "File not found"}
        with open(path, 'r', encoding='utf-8') as f: full_text = f.read()
        if not old_content: return {"status": "error", "msg": "old_content is empty, please check arguments"}
        count = full_text.count(old_content)
        if count == 0: return {"status": "error", "msg": "Old text block not found. Recommendation: first use file_read to confirm current content, then patch in small chunks. If multiple failures occur, ask user, do not overwrite or replace on your own."}
        if count > 1: return {"status": "error", "msg": f"Found {count} matches, location not unique. Provide a longer and more specific old text block to guarantee uniqueness. Recommendation: include context lines to boost distinctiveness, or apply changes sequentially."}
        updated_text = full_text.replace(old_content, new_content)
        with open(path, 'w', encoding='utf-8') as f: f.write(updated_text)
        return {"status": "success", "msg": "File partially modified"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

_read_dirs = set()
def _scan_files(base, depth=2):
    try:
        for e in os.scandir(base):
            if e.is_file(): yield (e.name, e.path)
            elif depth > 0 and e.is_dir(follow_symlinks=False): yield from _scan_files(e.path, depth - 1)
    except (PermissionError, OSError): pass
def file_read(path, start=1, keyword=None, count=200, show_linenos=True):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            stream = ((i, l.rstrip('\r\n')) for i, l in enumerate(f, 1))
            stream = itertools.dropwhile(lambda x: x[0] < start, stream)
            if keyword:
                before = collections.deque(maxlen=count//3)
                for i, l in stream:
                    if keyword.lower() in l.lower():
                        res = list(before) + [(i, l)] + list(itertools.islice(stream, count - len(before) - 1))
                        break
                    before.append((i, l))
                else: return f"Keyword '{keyword}' not found after line {start}. Falling back to content from line {start}:\n\n" \
                               + file_read(path, start, None, count, show_linenos)
            else: res = list(itertools.islice(stream, count))
            realcnt = len(res); L_MAX = min(max(100, 256000//realcnt), 8000); TAG = " ... [TRUNCATED]"
            remaining = sum(1 for _ in itertools.islice(stream, 5000))
            total_lines = (res[0][0] - 1 if res else start - 1) + realcnt + remaining
            total_tag = "[FILE] Total " + (f"{total_lines}+" if remaining >= 5000 else str(total_lines)) + ' lines\n'
            res = [(i, l if len(l) <= L_MAX else l[:L_MAX] + TAG) for i, l in res]
            result = "\n".join(f"{i}|{l}" if show_linenos else l for i, l in res)
            if show_linenos: result = total_tag + result
            _read_dirs.add(os.path.dirname(os.path.abspath(path)))
            return result
    except FileNotFoundError:
        msg = f"Error: File not found: {path}"
        try:
            tgt = os.path.basename(path); scan = os.path.dirname(os.path.dirname(os.path.abspath(path)))
            roots = [scan] + [d for d in _read_dirs if not d.startswith(scan)]
            cands = list(itertools.islice((c for base in roots for c in _scan_files(base)), 2000))
            top = sorted([(difflib.SequenceMatcher(None, tgt.lower(), c[0].lower()).ratio(), c) for c in cands[:2000]], key=lambda x: -x[0])[:5]
            top = [(s, c) for s, c in top if s > 0.3]
            if top: msg += "\n\nDid you mean:\n" + "\n".join(f"  {c[1]}  ({s:.0%})" for s, c in top)
        except Exception: pass
        return msg
    except Exception as e: return f"Error: {str(e)}"

def smart_format(data, max_str_len=100, omit_str=' ... '):
    if not isinstance(data, str): data = str(data)
    if len(data) < max_str_len + len(omit_str)*2: return data
    return f"{data[:max_str_len//2]}{omit_str}{data[-max_str_len//2:]}"

def consume_file(dr, file):
    if dr and os.path.exists(os.path.join(dr, file)): 
        with open(os.path.join(dr, file), encoding='utf-8', errors='replace') as f: content = f.read()
        os.remove(os.path.join(dr, file))
        return content

class GenericAgentHandler(BaseHandler):
    '''Generic Agent tool library, contains implementations for multiple tools. Tool methods automatically have a do_ prefix. The actual tool name does not.'''
    def __init__(self, parent, last_history=None, cwd='./temp'):
        self.parent = parent
        self.working = {}
        self.cwd = cwd;  self.current_turn = 0
        self.history_info = last_history if last_history else []
        self.code_stop_signal = []

    def _get_abs_path(self, path):
        if not path: return ""
        return os.path.abspath(os.path.join(self.cwd, path))   

    def _extract_code_block(self, response, code_type):
        matches = re.findall(rf"```{code_type}\n(.*?)\n```", response.content, re.DOTALL)
        return matches[-1].strip() if matches else None

    def do_code_run(self, args, response):
        '''Execute code snippet, there is a length limit, avoid putting large amounts of data in code, if needed use file_read.'''
        code_type = args.get("type", "python")
        code = args.get("code") or args.get("script")
        if not code:
            code = self._extract_code_block(response, code_type)
            if not code: return StepOutcome("[Error] Code missing. Use ```{code_type} block or 'script' arg.", next_prompt="\n")
        timeout = args.get("timeout", 60)
        raw_path = os.path.join(self.cwd, args.get("cwd", './'))
        cwd = os.path.normpath(os.path.abspath(raw_path))
        code_cwd = os.path.normpath(self.cwd)
        if code_type == 'python' and args.get("inline_eval"):
            ns = {'handler': self, 'parent': self.parent}
            old_cwd = os.getcwd()
            try:
                os.chdir(cwd)
                try: result = repr(eval(code, ns))
                except SyntaxError: exec(code, ns); result = ns.get('_r', 'OK')
                except Exception as e: result = f'Error: {e}'
            finally: os.chdir(old_cwd)
        else: result = yield from code_run(code, code_type, timeout, cwd, code_cwd=code_cwd, stop_signal=self.code_stop_signal)
        next_prompt = self._get_anchor_prompt(skip=args.get('_index', 0) > 0)
        return StepOutcome(result, next_prompt=next_prompt)
    
    def do_ask_user(self, args, response):
        question = args.get("question", "Please provide input:")
        candidates = args.get("candidates", [])
        result = ask_user(question, candidates)
        yield f"Waiting for your answer ...\n"
        return StepOutcome(result, next_prompt="", should_exit=True)
    
    def do_web_scan(self, args, response):
        '''Get current page content and tabs list. Can also be used to switch tabs.
        Note: HTML is simplified, sidebars/floating elements may be filtered. Use execute_js if you need to see filtered content.
        tabs_only=true returns only tabs list, without HTML (saves tokens).
        '''
        tabs_only = args.get("tabs_only", False)
        switch_tab_id = args.get("switch_tab_id", None)
        text_only = args.get("text_only", False)
        result = web_scan(tabs_only=tabs_only, switch_tab_id=switch_tab_id, text_only=text_only)
        content = result.pop("content", None)
        yield f'[Info] {str(result)}\n'
        if content: result = json.dumps(result, ensure_ascii=False, default=json_default) + f"\n```html\n{content}\n```"
        next_prompt = "\n"
        return StepOutcome(result, next_prompt=next_prompt)
    
    def do_web_execute_js(self, args, response):
        '''Primary tool for web scenarios, execute any JS to achieve *full* control of the browser. Supports saving result to file for later analysis.'''
        script = args.get("script", "") or self._extract_code_block(response, "javascript")
        if not script: return StepOutcome("[Error] Script missing. Use ```javascript block or 'script' arg.", next_prompt="\n")
        abs_path = self._get_abs_path(script.strip())
        if os.path.isfile(abs_path):
            with open(abs_path, 'r', encoding='utf-8') as f: script = f.read()
        save_to_file = args.get("save_to_file", "")
        switch_tab_id = args.get("switch_tab_id") or args.get("tab_id")
        no_monitor = args.get("no_monitor", False)
        result = web_execute_js(script, switch_tab_id=switch_tab_id, no_monitor=no_monitor)
        if save_to_file and "js_return" in result:
            content = str(result["js_return"] or '')
            abs_path = self._get_abs_path(save_to_file)
            result["js_return"] = smart_format(content, max_str_len=170)
            try:
                with open(abs_path, 'w', encoding='utf-8') as f: f.write(str(content))
                result["js_return"] += f"\n\n[Successfully saved full content to {abs_path}]"
            except:
                result['js_return'] += f"\n\n[Failed to save, cannot write to file {abs_path}]"
        show = smart_format(json.dumps(result, ensure_ascii=False, indent=2, default=json_default), max_str_len=300)
        try: print("Web Execute JS Result:", show)
        except: pass
        yield f"JS execution result:\n{show}\n"
        next_prompt = self._get_anchor_prompt(skip=args.get('_index', 0) > 0)
        result = json.dumps(result, ensure_ascii=False, default=json_default)
        return StepOutcome(smart_format(result, max_str_len=8000), next_prompt=next_prompt)
    
    def do_file_patch(self, args, response):
        path = self._get_abs_path(args.get("path", ""))
        yield f"[Action] Patching file: {path}\n"
        old_content = args.get("old_content", "")
        new_content = args.get("new_content", "")
        try: new_content = expand_file_refs(new_content, base_dir=self.cwd)
        except ValueError as e:
            yield f"[Status] ❌ Reference expansion failed: {e}\n"
            return StepOutcome({"status": "error", "msg": str(e)}, next_prompt="\n")
        result = file_patch(path, old_content, new_content)
        yield f"\n{str(result)}\n"
        next_prompt = self._get_anchor_prompt(skip=args.get('_index', 0) > 0)
        return StepOutcome(result, next_prompt=next_prompt)
    
    def do_file_write(self, args, response):
        '''Used to process large amounts of data in a file, for precise edits use file_patch.
        Place content to write within <file_content> tags, or inside a code block.
        '''
        path = self._get_abs_path(args.get("path", ""))
        mode = args.get("mode", "overwrite")  # overwrite/append/prepend
        action_str = {"prepend": "Prepending to", "append": "Appending to"}.get(mode, "Overwriting")
        yield f"[Action] {action_str} file: {os.path.basename(path)}\n"

        def extract_robust_content(text):
            tag = re.search(r"<file_content[^>]*>(.*)</file_content>", text, re.DOTALL)
            if tag: return tag.group(1).strip()
            s, e = text.find("```"), text.rfind("```")
            if -1 < s < e: return text[text.find("\n", s)+1 : e].strip()
            return None
        
        blocks = extract_robust_content(response.content)
        if not blocks:
            yield f"[Status] ❌ Failed: Did not find <file_content> code block in response\n"
            return StepOutcome({"status": "error", "msg": "No content found. Put content inside <file_content>...</file_content> tags in your reply body and call file_write."}, next_prompt="\n")
        try:
            new_content = expand_file_refs(blocks, base_dir=self.cwd)
            if mode == "prepend":
                old = open(path, 'r', encoding="utf-8").read() if os.path.exists(path) else ""
                open(path, 'w', encoding="utf-8").write(new_content + old)
            else:
                with open(path, 'a' if mode == "append" else 'w', encoding="utf-8") as f: f.write(new_content)
            yield f"[Status] ✅ {mode.capitalize()} successful ({len(new_content)} bytes)\n"
            next_prompt = self._get_anchor_prompt(skip=args.get('_index', 0) > 0)
            return StepOutcome({"status": "success", 'writed_bytes': len(new_content)}, next_prompt=next_prompt)
        except Exception as e:
            yield f"[Status] ❌ Write exception: {str(e)}\n"
            return StepOutcome({"status": "error", "msg": str(e)}, next_prompt="\n")
        
    def do_file_read(self, args, response):
        '''Read file content. Reads starting from `start` line. If keyword provided, returns context around the first matched keyword (case-insensitive)'''
        path = self._get_abs_path(args.get("path", ""))
        yield f"\n[Action] Reading file: {path}\n"
        start = args.get("start", 1)
        count = args.get("count", 200)
        keyword = args.get("keyword")
        show_linenos = args.get("show_linenos", True)
        result = file_read(path, start=start, keyword=keyword,
                           count=count, show_linenos=show_linenos)
        if show_linenos and not result.startswith("Error:"): result = 'Since show_linenos is set, the following format is: (Line number|) Content.\\n' + result 
        if ' ... [TRUNCATED]' in result: result += '\\n\\n(Certain lines truncated, you can use code_run to read full content)'
        result = smart_format(result, max_str_len=20000, omit_str='\n\n[omitted long content]\n\n')
        next_prompt = self._get_anchor_prompt(skip=args.get('_index', 0) > 0)
        log_memory_access(path)
        if 'memory' in path or 'sop' in path: 
            next_prompt += "\\n[SYSTEM TIPS] Reading memory or SOP file, if you decide to follow the SOP, please extract the key points (especially the later ones) to update working memory."
        return StepOutcome(result, next_prompt=next_prompt)
    
    def _in_plan_mode(self): return self.working.get('in_plan_mode')
    def _exit_plan_mode(self): self.working.pop('in_plan_mode', None)
    def enter_plan_mode(self, plan_path): 
        self.working['in_plan_mode'] = plan_path; self.max_turns = 80
        print(f"[Info] Entered plan mode with plan file: {plan_path}"); return plan_path
    def _check_plan_completion(self):
        if not os.path.isfile(p:=self._in_plan_mode() or ''): return None
        try: return len(re.findall(r'\[ \]', open(p, encoding='utf-8', errors='replace').read()))
        except: return None
    
    def do_update_working_checkpoint(self, args, response):
        '''Used to set important points to temporarily commit to memory for the remainder of the task.'''
        key_info = args.get("key_info", "")
        related_sop = args.get("related_sop", "")
        if "key_info" in args: self.working['key_info'] = key_info
        if "related_sop" in args: self.working['related_sop'] = related_sop
        self.working['passed_sessions'] = 0
        yield f"[Info] Updated key_info and related_sop.\n"
        next_prompt = self._get_anchor_prompt(skip=args.get('_index', 0) > 0)
        #next_prompt += '\\n[SYSTEM TIPS] This function is usually called at the beginning or middle of a task. If the task is successfully fully completed, you should be using start_long_term_update to settle long-term memory.\\n'
        return StepOutcome({"result": "working key_info updated"}, next_prompt=next_prompt)

    def do_no_tool(self, args, response):
        '''This is a special tool autonomously called by the engine, do not include it in TOOLS_SCHEMA.
        Triggered automatically by the engine when the model fails to explicitly call any tools in a turn.
        Secondary confirmation is only triggered when the reply mostly contains <thinking>/<summary> and a large block of code.'''
        content = getattr(response, 'content', '') or ""
        if not response or not content.strip():
            yield "[Warn] LLM returned an empty response. Retrying...\n"
            return StepOutcome({}, next_prompt="[System] Blank response, regenerate and tooluse")
        if 'incomplete response received !!!]' in content[-100:]:
            return StepOutcome({}, next_prompt="[System] Incomplete response. Regenerate and tooluse.")
        if 'max_tokens !!!]' in content[-100:]:
            return StepOutcome({}, next_prompt="[System] max_tokens limit reached. Use multi small steps to do it.")
        
        if self._in_plan_mode() and any(kw in content for kw in ['task complete', 'all complete', 'completed all', '🏁']):
            if 'VERDICT' not in content and '[VERIFY]' not in content and 'verify subagent' not in content:
                yield "[Warn] Plan mode completion declaration intercepted.\n"
                return StepOutcome({}, next_prompt="⛔ [Verification Intercept] Detected you claimed completion in plan mode, but did not execute the [VERIFY] validation step. Please launch the verify subagent per plan_sop Section IV first, you can only claim completion after obtaining a VERDICT.")
            
        # 2. Detect the scenario of "containing a large block of code but no tools are called"
        # Key feature: exactly 1 large code block + directly followed by the end (only whitespace after it)
        code_block_pattern = r"```[a-zA-Z0-9_]*\n[\s\S]{50,}?```"
        blocks = re.findall(code_block_pattern, content)
        if len(blocks) == 1:
            m = re.search(code_block_pattern, content)
            after_block = content[m.end():]
            if not after_block.strip():
                residual = content.replace(m.group(0), "")
                residual = re.sub(r"<thinking>[\s\S]*?</thinking>", "", residual, flags=re.IGNORECASE)
                residual = re.sub(r"<summary>[\s\S]*?</summary>", "", residual, flags=re.IGNORECASE)
                clean_residual = re.sub(r"\s+", "", residual)
                if len(clean_residual) <= 30:
                    yield "[Info] Detected large code block without tool call and no extra natural language. Requesting clarification.\n"
                    next_prompt = (
                        "[System] Detected that your previous response mainly consisted of a large code block, and no tools were called.\n"
                        "If this code needs to be executed, written to a file, or further analyzed, please reorganise your response to explicitly call the corresponding tool"
                        " (e.g. code_run, file_write, file_patch, etc.);\n"
                        "If you are simply demonstrating or explaining the code snippet to the user, please supplement with a natural language explanation in your response,"
                        " and clarify whether additional concrete actions are still needed."
                    )
                    return StepOutcome({}, next_prompt=next_prompt)
                
        if self._in_plan_mode():
            remaining = self._check_plan_completion()
            if remaining == 0:
                self._exit_plan_mode(); yield "[Info] Plan complete: 0 [ ] remaining targets in plan.md, exiting plan mode.\n"
        
        yield "[Info] Final response to user.\n"
        return StepOutcome(response, next_prompt=None)
    
    def do_start_long_term_update(self, args, response):
        '''Tool to be called when the Agent feels there is important information to remember after completing the current task.'''
        prompt = '''### [Summarize and refine experience] Since you feel there is important information to remember from the current task, please extract environmentally factual, user preference, and vital procedural data [which has been practically verified and will be effective long-term] from the last task, in order to update the memory.
This tool flags the beginning of the checkout process. If a memory update process is already ongoing or there's nothing worth recalling, ignore this call.
**Extract factually verified action information**:
- **Environmental realities** (paths/credentials/configs) → Use `file_patch` to update L2, synchronize to L1
- **Complex task experience** (key pitfalls/prerequisites/important steps) → Put in L3 refined SOP (only record the crucial lessons learned via multiple tedious trial and errors)
**Prohibited**: temporary variables, specific reasoning procedures, unverified info, common sense, or details you can easily reconstruct.
**Procedure**: strictly follow the L0 Memory Update SOP provided. Use `file_read` first to check what's already there → assess type → minimize modifications → skip if there's no new content, ensuring minimal localised alterations to the memory bank.\n
''' + get_global_memory()
        yield "[Info] Start distilling good memory for long-term storage.\n"
        path = './memory/memory_management_sop.md'
        if os.path.exists(path): result = file_read(path, show_linenos=False)
        else: result = "Memory Management SOP not found. Do not update memory."
        return StepOutcome(result, next_prompt=prompt)

    def _get_anchor_prompt(self, skip=False):
        if skip: return "\n"
        h_str = "\n".join(self.history_info[-20:])
        prompt = f"\n### [WORKING MEMORY]\n<history>\n{h_str}\n</history>"
        prompt += f"\nCurrent turn: {self.current_turn}\n"
        if self.working.get('key_info'): prompt += f"\n<key_info>{self.working.get('key_info')}</key_info>"
        if self.working.get('related_sop'): prompt += f"\nIf there are unclear parts please re-read {self.working.get('related_sop')}"
        if getattr(self.parent, 'verbose', False):
            try: print(prompt)
            except: pass
        return prompt

    def turn_end_callback(self, response, tool_calls, tool_results, turn, next_prompt, exit_reason):
        _c = re.sub(r'```.*?```|<thinking>.*?</thinking>', '', response.content, flags=re.DOTALL)
        rsumm = re.search(r"<summary>(.*?)</summary>", _c, re.DOTALL)
        if rsumm: summary = rsumm.group(1).strip()
        else:
            tc = tool_calls[0]; tool_name, args = tc['tool_name'], tc['args']   # at least one because no_tool
            clean_args = {k: v for k, v in args.items() if not k.startswith('_')}
            summary = f"Called tool {tool_name}, args: {clean_args}"
            if tool_name == 'no_tool': summary = "Directly answered user question"
            next_prompt += "\n[DANGER] Missing <summary> from last round, automatically supplemented based on physical actions. Remember the <summary> protocol in your next reply." 
        summary = smart_format(summary, max_str_len=100)
        self.history_info.append(f'[Agent] {summary}')
        if turn % 35 == 0 and 'plan' not in str(self.working.get('related_sop')):
            next_prompt += f"\n\n[DANGER] Execution has continued for {turn} rounds. You must summarize the situation and ask_user, continued retries are prohibited."
        elif turn % 7 == 0:
            next_prompt += f"\n\n[DANGER] Execution has continued for {turn} rounds. Invalid retries are prohibited. If there is no valid progress, you must switch strategies: 1. Probe physical boundaries 2. Request user assistance. If necessary, you may use update_working_checkpoint to save critical context."
        elif turn % 10 == 0: next_prompt += get_global_memory()

        if (_plan := self._in_plan_mode()) and turn >= 10 and turn % 5 == 0:
            next_prompt = f"[Plan Hint] You are in plan mode. You must file_read({_plan}) to confirm current step, quote it at the start of your reply: 📌 Current step: ...\n\n" + next_prompt
        if _plan and turn >= 70: next_prompt += f"\n\n[DANGER] Plan mode has run for {turn} rounds, reached limit. You must use ask_user to report progress and confirm whether to proceed."

        injkeyinfo = consume_file(self.parent.task_dir, '_keyinfo')
        injprompt = consume_file(self.parent.task_dir, '_intervene')
        if injkeyinfo: self.working['key_info'] = self.working.get('key_info', '') + f"\n[MASTER] {injkeyinfo}"
        if injprompt: next_prompt += f"\n\n[MASTER] {injprompt}\n"
        for hook in getattr(self.parent, '_turn_end_hooks', {}).values(): hook(locals())  # current readonly
        return next_prompt

def get_global_memory():
    prompt = "\n"
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, 'memory/global_mem_insight.txt'), 'r', encoding='utf-8', errors='replace') as f: insight = f.read()
        with open(os.path.join(script_dir, 'assets/insight_fixed_structure.txt'), 'r', encoding='utf-8') as f: structure = f.read()
        prompt += f'cwd = {os.path.join(script_dir, "temp")} (Referenced via ./)\n'
        prompt += f"\n[Memory] (../memory)\n"
        prompt += structure + '\n../memory/global_mem_insight.txt:\n'
        prompt += insight + "\n"
    except FileNotFoundError: pass
    return prompt
