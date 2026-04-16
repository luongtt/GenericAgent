<div align="center">
<img src="assets/images/bar.jpg" width="880"/>
</div>

---

## 🌟 Overview

**GenericAgent** is a minimal, self-evolving autonomous agent framework. Its core is just **~3K lines of code**. Through **9 atomic tools + a ~100-line Agent Loop**, it grants any LLM system-level control over a local computer — covering browser, terminal, filesystem, keyboard/mouse input, screen vision, and mobile devices (ADB).

Its design philosophy: **don't preload skills — evolve them.**

Every time GenericAgent solves a new task, it automatically crystallizes the execution path into an skill for direct reuse later. The longer you use it, the more skills accumulate — forming a skill tree that belongs entirely to you, grown from 3K lines of seed code.

> **🤖 Self-Bootstrap Proof** — Everything in this repository, from installing Git and running `git init` to every commit message, was completed autonomously by GenericAgent. The author never opened a terminal once.

## 📋 Core Features
- **Self-Evolving**: Automatically crystallizes each task into an skill. Capabilities grow with every use, forming your personal skill tree.
- **Minimal Architecture**: ~3K lines of core code. Agent Loop is ~100 lines. No complex dependencies, zero deployment overhead.
- **Strong Execution**: Injects into a real browser (preserving login sessions). 9 atomic tools take direct control of the system.
- **High Compatibility**: Supports Claude / Gemini / Kimi / MiniMax and other major models. Cross-platform.


## 🧬 Self-Evolution Mechanism

This is what fundamentally distinguishes GenericAgent from every other agent framework.

```
[New Task] --> [Autonomous Exploration] (install deps, write scripts, debug & verify) -->
[Crystallize Execution Path into skill] --> [Write to Memory Layer] --> [Direct Recall on Next Similar Task]
```

| What you say | What the agent does the first time | Every time after |
|---|---|---|
| *"Read my WeChat messages"* | Install deps → reverse DB → write read script → save skill | **one-line invoke** |
| *"Monitor stocks and alert me"* | Install mootdx → build selection flow → configure cron → save skill | **one-line start** |
| *"Send this file via Gmail"* | Configure OAuth → write send script → save skill | **ready to use** |

After a few weeks, your agent instance will have a skill tree no one else in the world has — all grown from 3K lines of seed code.


##### 🎯 Demo Showcase

| 🧋 Food Delivery Order | 📈 Quantitative Stock Screening |
|:---:|:---:|
| <img src="assets/demo/order_tea.gif" width="100%" alt="Order Tea"> | <img src="assets/demo/selectstock.gif" width="100%" alt="Stock Selection"> |
| *"Order me a milk tea"* — Navigates the delivery app, selects items, and completes checkout automatically. | *"Find GEM stocks with EXPMA golden cross, turnover > 5%"* — Screens stocks with quantitative conditions. |
| 🌐 Autonomous Web Exploration | 💰 Expense Tracking | 💬 Batch Messaging |
| <img src="assets/demo/autonomous_explore.png" width="100%" alt="Web Exploration"> | <img src="assets/demo/alipay_expense.png" width="100%" alt="Alipay Expense"> | <img src="assets/demo/wechat_batch.png" width="100%" alt="WeChat Batch"> |
| Autonomously browses and periodically summarizes web content. | *"Find expenses over ¥2K in the last 3 months"* — Drives Alipay via ADB. | Sends bulk WeChat messages, fully driving the WeChat client. |

## 📅 Latest News

- **2026-04-11:** Introduced **L4 session archive memory** and scheduler cron integration
- **2026-03-23:** Support personal WeChat as a bot frontend
- **2026-03-10:** [Released million-scale Skill Library](https://mp.weixin.qq.com/s/q2gQ7YvWoiAcwxzaiwpuiQ?scene=1&click_id=7)
- **2026-03-08:** [Released "Dintal Claw" — a GenericAgent-powered government affairs bot](https://mp.weixin.qq.com/s/eiEhwo-j6S-WpLxgBnNxBg)
- **2026-03-01:** [GenericAgent featured by Jiqizhixin (机器之心)](https://mp.weixin.qq.com/s/uVWpTTF5I1yzAENV_qm7yg)
- **2026-01-16:** GenericAgent V1.0 public release

---

## 🚀 Quick Start

#### Method 1: Standard Installation

```bash
# 1. Clone the repo
git clone https://github.com/lsdefine/GenericAgent.git
cd GenericAgent

# 2. Install minimal dependencies
pip install streamlit pywebview

# 3. Configure API Key
cp mykey_template.py mykey.py
# Edit mykey.py and fill in your LLM API Key

# 4. Launch
python launch.pyw
```

Full guide: [GETTING_STARTED.md](GETTING_STARTED.md)

---

## 🤖 Bot Interface (Optional)

### Telegram Bot

```python
# mykey.py
tg_bot_token = 'YOUR_BOT_TOKEN'
tg_allowed_users = [YOUR_USER_ID]
```

```bash
python frontends/tgapp.py
```

### Alternative App Frontends

Besides the default Streamlit web UI, you can also try other frontend styles:

```bash
python frontends/qtapp.py                # Qt-based desktop app
streamlit run frontends/stapp2.py        # Alternative Streamlit UI
```


## 📊 Comparison with Similar Tools

| Feature | GenericAgent | OpenClaw | Claude Code |
|------|:---:|:---:|:---:|
| **Codebase** | ~3K lines | ~530,000 lines | Open-sourced (large) |
| **Deployment** | `pip install` + API Key | Multi-service orchestration | CLI + subscription |
| **Browser Control** | Real browser (session preserved) | Sandbox / headless browser | Via MCP plugin |
| **OS Control** | Mouse/kbd, vision, ADB | Multi-agent delegation | File + terminal |
| **Self-Evolution** | Autonomous skill growth | Plugin ecosystem | Stateless between sessions |
| **Out of the Box** | A few core files + starter skills | Hundreds of modules | Rich CLI toolset |


## 🧠 How It Works

GenericAgent accomplishes complex tasks through **Layered Memory × Minimal Toolset × Autonomous Execution Loop**, continuously accumulating experience during execution.

1️⃣ **Layered Memory System**
> _Memory crystallizes throughout task execution, letting the agent build stable, efficient working patterns over time._

- **L0 — Meta Rules**: Core behavioral rules and system constraints of the agent
- **L1 — Insight Index**: Minimal memory index for fast routing and recall
- **L2 — Global Facts**: Stable knowledge accumulated over long-term operation
- **L3 — Task Skills / SOPs**: Reusable workflows for completing specific task types
- **L4 — Session Archive**: Archived task records distilled from finished sessions for long-horizon recall

2️⃣ **Autonomous Execution Loop**

> _Perceive environment state → Task reasoning → Execute tools → Write experience to memory → Loop_

The entire core loop is just **~100 lines of code** (`agent_loop.py`).

3️⃣ **Minimal Toolset**
> _GenericAgent provides only **9 atomic tools**, forming the foundational capabilities for interacting with the outside world._

| Tool | Function |
|------|------|
| `code_run` | Execute arbitrary code |
| `file_read` | Read files |
| `file_write` | Write files |
| `file_patch` | Patch / modify files |
| `web_scan` | Perceive web content |
| `web_execute_js` | Control browser behavior |
| `ask_user` | Human-in-the-loop confirmation |

> Additionally, 2 **memory management tools** (`update_working_checkpoint`, `start_long_term_update`) allow the agent to persist context and accumulate experience across sessions.

4️⃣ **Capability Extension Mechanism**
> _Capable of dynamically creating new tools._

Via `code_run`, GenericAgent can dynamically install Python packages, write new scripts, call external APIs, or control hardware at runtime — crystallizing temporary abilities into permanent tools.

<div align="center">
  <img src="assets/images/workflow.jpg" alt="GenericAgent Workflow" width="400"/>
  <br><em>GenericAgent Workflow Diagram</em>
</div>


## ⭐ Support

If this project helped you, please consider leaving a **Star!** 🙏

You're also welcome to join our **GenericAgent Community Group** for discussion, feedback, and co-building 👏

<div align="center">
  <table>
    <tr>
      <td align="center"><strong>WeChat Group 4</strong><br><img src="assets/images/wechat_group4.jpg" alt="WeChat Group 4 QR Code" width="250"/></td>
      <td align="center"><strong>WeChat Group 3</strong><br><img src="assets/images/wechat_group2.JPG" alt="WeChat Group 3 QR Code" width="250"/></td>
      <td align="center"><strong>Feishu Group</strong><br><img src="assets/images/feishu_group.jpg" alt="Feishu Group QR Code" width="250"/></td>
    </tr>
  </table>
</div>

## 🚩 Friendly Links

Thanks for the support from the LinuxDo community!

[![LinuxDo](https://img.shields.io/badge/Community-LinuxDo-blue?style=for-the-badge)](https://linux.do/)

## 📄 License

MIT License — see [LICENSE](LICENSE)

## 📈 Star History

<a href="https://star-history.com/#lsdefine/GenericAgent&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=lsdefine/GenericAgent&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=lsdefine/GenericAgent&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=lsdefine/GenericAgent&type=Date" />
 </picture>
</a>
