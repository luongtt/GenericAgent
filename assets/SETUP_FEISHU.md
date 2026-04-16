# Feishu Agent Setup Guide

> Turn your personal computer into the brain of a Feishu (Lark) bot, allowing you to control your PC anytime, anywhere via Feishu conversations.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Solution Choice](#solution-choice)
3. [Enterprise User Setup](#enterprise-user-setup)
4. [Personal User Setup](#personal-user-setup)
5. [Project Configuration](#project-configuration)
6. [Run and Test](#run-and-test)
7. [FAQ](#faq)

---

## Prerequisites

### Required Environment

- Python 3.8+
- Complete source code of this project
- LLM API Key (Claude/OpenAI etc., configured in `llmcore/mykeys`)

### Install Dependencies

```bash
pip install lark-oapi
```

---

## Solution Choice

| Your Situation | Recommended Solution | Est. Time |
| --- | --- | --- |
| Company already uses Feishu | [Enterprise User Setup](#enterprise-user-setup) | 5-10 mins |
| Personal user/Testing | [Personal User Setup](#personal-user-setup) | 10-15 mins |

---

## Enterprise User Setup

> Applicable if: Your company uses Feishu, and you have permission to create applications or contact admins for approval

### Step 1: Create Application

1. Visit [Feishu Open Platform](https://open.feishu.cn/)
2. Log in to your enterprise Feishu account
3. Click "Create App" → "Custom App" (企业自建应用) in the top right corner
4. Fill in the app info:
   - App Name: `My Agent Assistant` (customizable)
   - App Description: `Personal AI Assistant`
   - App Icon: Optional

### Step 2: Add Bot Capabilities

1. Enter the app details page
2. Select "Add Features" (添加应用能力) on the left menu
3. Find "Bot" (机器人) and click "Add"
4. Configure bot information (can be kept default)

### Step 3: Configure Permissions

1. Left menu "Permissions" (权限管理) → "API Permissions" (API 权限)
2. Search and enable the following permissions:
   - `im:message` - Read and send messages in private and group chats
   - `im:message:send_as_bot` - Send messages as the app
   - `contact:user.id:readonly` - Read user ID

### Step 4: Get Credentials

1. Left menu "Credentials & Basic Info" (凭证与基础信息)
2. Note down the following information:
   - **App ID**: `cli_xxxxxxxx`
   - **App Secret**: `xxxxxxxxxxxxxxxx`

### Step 5: Publish Application

1. Left menu "Version Management & Release" (版本管理与发布)
2. Click "Create Version"
3. Fill in version information and submit for review
4. **Contact enterprise admin for approval** (or approve directly if you are an admin)

### Step 6: Get Your Open ID

1. After the app is approved, search for your bot in Feishu
2. Send any message to the bot
3. Run the following code to get your Open ID:

```python
# Run temporarily to get open_id
import lark_oapi as lark
from lark_oapi.api.im.v1 import *

client = lark.Client.builder().app_id("YOUR_APP_ID").app_secret("YOUR_APP_SECRET").build()

# Listen to messages and print the sender's open_id
def handle(data):
    print(f"Your Open ID: {data.event.sender.sender_id.open_id}")

# ... Or check the runtime log output from frontends/fsapp.py
```

---

## Personal User Setup

> Applicable if: You don't have an enterprise Feishu account and want to test it personally

### Step 1: Create a Test Enterprise

1. Visit [Feishu Open Platform](https://open.feishu.cn/)
2. Register/Log in with a personal phone number
3. Click your avatar in the top right → "Create Test Enterprise"
4. Fill in the enterprise name (e.g., `My Test Workspace`)
5. Once created, you are the **Admin** of this test enterprise

### Step 2: Create Application

> Same as the Enterprise User steps

1. Click "Create App" → "Custom App"
2. Fill in the app info

### Step 3: Add Bot Capabilities

1. Enter the app details page
2. "Add Features" → "Bot" → "Add"

### Step 4: Configure Permissions

1. "Permissions" → "API Permissions"
2. Enable permissions:
   - `im:message`
   - `im:message:send_as_bot`
   - `contact:user.id:readonly`

### Step 5: Get Credentials

1. "Credentials & Basic Info"
2. Copy **App ID** and **App Secret**

### Step 6: Publish Application (Test enterprise can self-approve)

1. "Version Management & Release" → "Create Version"
2. After submission, enter the [Feishu Admin Console](https://feishu.cn/admin)
3. "Workplace" → "App Review" → Approve your app

### Step 7: Use in Feishu Client

1. Download the [Feishu Client](https://www.feishu.cn/download)
2. Log in to your test enterprise account
3. Search for the bot name you created
4. Start chatting!

---

## Project Configuration

### Configure Feishu Credentials

Edit `mykey.py` in the project root directory and add:

```python
# Feishu app credentials
fs_app_id = "cli_xxxxxxxxxxxxxxxx"      # Replace with your App ID
fs_app_secret = "xxxxxxxxxxxxxxxx"       # Replace with your App Secret

# List of allowed User Open IDs (optional, leave empty to allow everyone)
fs_allowed_users = [
    "ou_xxxxxxxxxxxxxxxxxxxxxxxx",       # Your Open ID
]
```

### Confirm LLM Configuration

Ensure your LLM API keys are configured in `llmcore/mykeys`:

```python
# Example: Claude API
claude_config = {
    'apikey': 'sk-ant-xxxxx',
    'apibase': 'https://api.anthropic.com',
    'model': 'claude-sonnet-4-20250514'
}
```

---

## Run and Test

### Start Service

```bash
cd /path/to/pc-agent-loop
python frontends/fsapp.py
```

### Expected Output

```
==================================================
Feishu Agent Started (WebSocket Mode)
App ID: cli_xxxxxxxxxxxxxxxx
Waiting for messages...
==================================================
```

### Test Conversation

1. Open Feishu client
2. Find your bot
3. Send: `Hello`
4. Wait for reply (The first time might take a few seconds)

---

## Available Commands

When talking to the bot, you can use the following special commands:

| Command | Description |
| ---- | ---- |
| `/new` | Start a new conversation, clear current context |
| `/stop` | Abort the currently executing task |
| `/restore <keyword>` | Restore previous conversation context (searches history using keyword) |

### Command Examples

```
/new                    # Clear conversation, start over
/stop                   # Stop running tasks
/restore yesterday's task # Restore historical chat containing "yesterday's task" keyword
```

### Message Display Notes

- ⏳ Indicates task is currently executing
- Messages update in real-time, no need to wait for completion
- Extremely long replies will automatically be split into segments

---

## FAQ

### Q: Prompt "App not published" or "No permission"

**A:** Ensure the app is published and approved by an admin. Test enterprise users need to manually approve it in the admin console.

### Q: No reply after sending a message

**A:** Check:
1. Is `frontends/fsapp.py` running?
2. Are there execution errors in the terminal?
3. Is your LLM API key configured correctly?

### Q: Prompt "invalid app_id"

**A:** Check if `fs_app_id` in `mykey.py` is copied correctly (including the `cli_` prefix).

### Q: How do I get my Open ID?

**A:** After running `frontends/fsapp.py`, send a message to the bot and check the terminal logs for your `open_id`.

### Q: Can multiple people use it simultaneously?

**A:** No. One app can only establish one persistent connection to one PC. Each person needs to create their own application.

---

## Architecture Overview

```
Your Feishu ←→ Feishu Cloud ←→ Long Connection ←→ frontends/fsapp.py ←→ Agent ←→ Your PC
                                    ↑
                             Runs on your PC
```

- Messages are forwarded through Feishu Cloud to `frontends/fsapp.py` running on your PC
- After the Agent processes the request, it replies via the Feishu API
- **Your PC must keep running** `frontends/fsapp.py` to respond to messages.

---

## Next Steps

- Customize Agent behavior: Edit `assets/sys_prompt.txt`
- Add new tools: Edit `assets/tools_schema.json`
- View logs: Observe terminal output during runtime

---

*Document Version: v1.1 | Update Date: 2026-03-07*

**v1.1 Changes:**
- Added "Available Commands" section (/new, /stop, /restore)
- Added Message Display Notes (⏳ In-progress marker, real-time updates etc.)
