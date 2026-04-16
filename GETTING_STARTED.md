# 🚀 Beginner's Quick Start Guide

> It doesn't matter if you have zero programming experience, just follow along. Works for both Mac and Windows.
>
> If you already have a Python environment, skip directly to [Step 2](#2-configure-api-key).

---

## 1. Install Python

### Mac

Open "Terminal" (search "Terminal" in Launchpad), paste this command and press Enter:

```bash
brew install python
```

If it says `brew: command not found`, it means Homebrew isn't installed. Paste this first:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation finishes, run `brew install python` again.

### Windows

1. Open [python.org/downloads](https://www.python.org/downloads/), click the big yellow button to download
2. Run the installer, **strictly ensure "Add Python to PATH" at the bottom is checked**
3. Click "Install Now"

### Verify

Enter in Terminal / Command Prompt:

```bash
python3 --version
```

If you see `Python 3.x.x`, you're good to go. On Windows, you can also try `python --version`.

> ⚠️ **Version Warning**: Recommended **Python 3.11 or 3.12**. Avoid 3.14 (incompatible with pywebview and other dependencies).

---

## 2. Configure API Key

### Download Project

1. Open the [GitHub Repository page](https://github.com/lsdefine/GenericAgent)
2. Click the green **Code** button → **Download ZIP**
3. Extract to your preferred location

### Create Config File

Go into the project folder, duplicate `mykey_template.py`, and rename it to `mykey.py`.

Open `mykey.py` with any text editor and fill in your API information. **Just pick one setup**, you can delete the unused ones or leave them alone.

### Config Examples

**Most common usage:**

```python
# Variable name contains 'oai' → Uses OpenAI compatible format (/chat/completions)
oai_config = {
    'apikey': 'sk-YourKey',
    'apibase': 'http://YourAPIAddress:Port',
    'model': 'ModelName',
}
```

```python
# Variable name contains 'claude' (without 'native') → Uses Claude compatible format (/messages)
claude_config = {
    'apikey': 'sk-YourKey',
    'apibase': 'http://YourAPIAddress:Port',
    'model': 'claude-sonnet-4-20250514',
}
```

```python
# MiniMax uses OpenAI compatible format, just include 'oai' in the variable name
# Temperature is auto-corrected to (0, 1], supports full M2.7 / M2.5 series, 204K context
oai_minimax_config = {
    'apikey': 'eyJh...',
    'apibase': 'https://api.minimax.io/v1',
    'model': 'MiniMax-M2.7',
}
```

**Using native Tool Call format (suitable for weaker models):**

```python
# Variable name contains both 'native' and 'claude' → Claude standard tool call format
native_claude_config = {
    'apikey': 'sk-ant-YourKey',
    'apibase': 'https://api.anthropic.com',
    'model': 'claude-sonnet-4-20250514',
}
```

> 💡 Also supports `native_oai_config` (OpenAI standard tool calling), `sider_cookie` (Sider), etc., check the comments in `mykey_template.py` for details.

### Crucial Rules

**Variable naming dictates the interface format** (Not the model name):

| Variable Contains | Session Triggered | Best For |
|-----------|---------------|---------|
| `oai` | OpenAI Compatible | Most API services, OpenAI official |
| `claude` (no `native`) | Claude Compatible | Claude API services |
| `native` + `claude` | Claude Native Tool Call | Recommended for weaker models, stricter tool calling |
| `native` + `oai` | OpenAI Native Tool Call | Recommended for weaker models, stricter tool calling |

> Ex: Using a Claude model, but your API provider uses an OpenAI-compatible endpoint → Name the variable `oai_xxx`.
> Ex: Using MiniMax model → Name it `oai_minimax_config`, since MiniMax uses OpenAI APIs.

**`apibase` filling rules** (endpoints append auto-magically):

| What you write | System behavior |
|-----------|---------|
| `http://host:2001` | Auto-appends `/v1/chat/completions` |
| `http://host:2001/v1` | Auto-appends `/chat/completions` |
| `http://host:2001/v1/chat/completions` | Used exactly as-is, no appending |

---

## 3. First Launch

Open terminal in the project folder and run:

```bash
cd your/extraction/path
python3 agentmain.py
```

This is the **command-line mode**, ready to use. You'll see a prompt, just type and send tasks.

Try your first task:

```
Create a hello.txt on my desktop containing the text Hello World
```

> 💡 On Windows, if `python3` is not recognized, use `python agentmain.py`.

---

## 4. Let the Agent Install Dependencies

Once the Agent is up, a single sentence is all it takes to handle dependencies:

```
Please review your code and install all python dependencies you might need
```

The Agent will read its own code, identify the required packages, and install them for you.

> ⚠️ If network issues block the Agent from calling its API, you may need to install one package manually first:
> ```bash
> pip install requests
> ```

### Upgrading to the GUI 

Once dependencies are installed, you can use the graphical mode:

```bash
python3 launch.pyw
```

A floating overlay widget will appear on your desktop. Type your tasks directly there.

### Optional: Stuff you can ask the Agent to do

```
Please set up git connections for me so I can easily update your code later
```

The Agent will set it up automatically. If you don't have Git, it'll download a portable version.

```
Please create a desktop shortcut for launch.pyw
```

Now you can just double-click the icon to launch, no more terminals needed.

---

## 5. Unlocking Capabilities

With the environment running, you can progressively unlock more powers. Each point just needs **one sentence told to the Agent**:

### Basic Powers

| Capability | What to tell the Agent | Description |
|------|-----------|------|
| **PowerShell Scripting** | `Unlock my current user's PowerShell ps1 execution permissions` | Windows blocks .ps1 execution by default |
| **Global File Search** | `Install and configure Everything CLI into my PATH` | Millisecond-level full drive searches |

### Browser Automation

| Capability | What to tell the Agent | Description |
|------|-----------|------|
| **Web Tools Unlock** | `Execute web setup sop, unlock web tools` | Injects browser extension, allowing browser manipulation |

Once unlocked, the Agent acts inside your **real browser, preserving your login states**:

```
Open Amazon, search for iPhone 16, sort by price
Go to YouTube, check my recently watched history
```

### Advanced Powers

| Capability | What to tell the Agent | Description |
|------|-----------|------|
| **OCR** | `Use rapidocr to configure your OCR capability and save it to your memory` | Let the Agent "see" text on screen |
| **Screen Vision** | `Look at your llmcore, write a capability to invoke vision and save it to your memory` | Let the Agent "see" on-screen content |
| **Mobile Control** | `Configure ADB environment, prepare to connect Android device` | Control Android phones via USB/WiFi |

### Chat Platform Integrations (Optional)

Once integrated, you can message the Agent on your PC from your phone anytime, anywhere.

Tell the Agent: `Check your code and help me configure the Bot integration for platform XX`

Supported platforms: **Personal WeChat Bot** / QQ / Feishu / WeCom / DingTalk / Telegram

> The Agent will automatically read its code and guide you through the setup.

### Advanced Modes

The following modes are fully **Self-Documenting**—no need to look up manuals, just ask the Agent directly:

| Mode | What to tell the Agent |
|------|------------|
| **Reflect** | `Read your code, tell me how to enable your reflect mode` |
| **Scheduled Tasks** | `Read your code, tell me how to enable your scheduled task mode` |
| **Plan** | `Read your code, tell me how to enable your plan mode` |
| **SubAgent** | `Read your code, tell me how to enable your subagent mode` |
| **Autonomous Probing** | `Read your code, tell me how to enable your autonomous exploration mode` |

> 💡 This is GenericAgent's core design philosophy: **Code IS the documentation**. The Agent can understand its own source code, so you can ask it directly for any functionality.

---

## 💡 Gets Stronger the More You Use It

GenericAgent does not have pre-programmed skills, instead **it evolves through usage**. Every time a new task is completed, it automatically solidifies the execution path into a Skill, to be invoked directly on similar tasks.

You don't need to manage these Skills, the Agent does it. The longer you use it, the more skills it accumulates, ultimately growing a tailored, exclusive skill tree.

> 💡 If you feel the Agent forgot something important, tell it directly: `Save this into your memory`, and it'll memorize it.

**You can also directly reuse Skills from other Claws:**

- To let the Agent search: `Help me find a skill that does XXX` → After completion → `Add it to your memory`
- Directly specify a source: `Access directory/URL XXX, follow this skill to do XXX`

**Staying Updated:**

Tell the Agent: `git update your code, then look at the commits to see what's new`

> The Agent will automatically git pull and interpret the commit logs to summarize its new abilities.

> Please refer to [README.md](README.md) for more details.