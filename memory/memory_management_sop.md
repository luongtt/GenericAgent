## 0. Core Axioms (Highest Priority)
1.  **Action-Verified Only**
    *   **Definition**: Any information written to L1/L2/L3 must originate from **successful tool execution results** (e.g., successful `shell` execution, confirmed `file_read` content, passed code execution).
    *   **Prohibited**: It is strictly forbidden to write the model's "inherent knowledge", "inferred guesses", "unexecuted plans", or "unverified assumptions" as facts.
    *   **Slogan**: **No Execution, No Memory.**
2.  **Sanctity of Verified Data**
    *   **Definition**: Valid configurations, pitfalls, and critical paths that have been verified by action **must not be discarded** during refactoring (Refactoring/GC).
    *   **Operation**: You can compress text, you can move hierarchies (from L2 to L3), but you must never lose the accuracy and traceability of information.
    *   Please be extremely careful when modifying memory. Try not to use overwrite or code run. Only small patches are allowed. If it's hard to change, it's better not to change it.
3.  **No Volatile State**
    *   **Definition**: It is strictly forbidden to store data that changes frequently over time or across sessions.
    *   **Examples**: Current timestamps, temporary Session IDs, running PIDs, specific absolute paths, connected device information.
4.  **Minimum Sufficient Pointer**
    *   The upper layer only keeps the shortest identifier that can locate the lower layer. One extra word is redundant.
---
## Memory Hierarchy Architecture
```
L1: global_mem_insight.txt (Minimalist Index Layer - Strictly controlled ≤30 lines)
    ↓ Pointer
L2: global_mem.txt (Fact Base Layer - Short now but will expand)
    ↓ Detailed Reference
L3: ../memory/ (Record Base Layer - Contains various files like .md/.py)
L4: ../memory/L4_raw_sessions/ (Historical Session Layer - Auto-collected by scheduler reflection, can locate past context)
```
---
## Responsibilities and Principles of Each Layer
### L1: Global Memory Index (global_mem_insight.txt)
**Responsibility**: Provide minimalist navigation index for L2 and L3 to ensure critical capabilities can be discovered.
**Characteristics**:
- Size limit: ≤ 30 lines (hard constraint), < 1k tokens (expected). Strictly forbidden to fill in details (unless extremely high frequency task)
- Content: Two layers of "Scenario Keywords → Memory Location" mapping + RULES (Red line rules + High frequency mistakes)
  - First layer: High frequency scenario key→value (directly give sop/py/L2 section name), self-contained names are just one word, do not repeatedly translate.
  - Second layer: Low frequency scenarios only list keywords, read L2 or ls L3 to locate when needed.
  - Core: Scenario trigger words are extremely important (without indexing, you won't know this capability exists), but writing How-to details is strictly prohibited.
  - RULES: Compressed version of pitfalls, including:
    - Red line rules (Fatal): Violations will cause process termination or system crash (e.g., `Forbid unconditional kill python (will kill itself)`).
    - Red line rules (Hidden): Violations do not report errors but produce wrong results (e.g., `Search uses google, not baidu`).
    - High frequency mistakes: Key constraints that are easy to forget (e.g., `es(PATH)` to prevent path searching).
- Updating: When L2/L3 has additions/deletions, judge the frequency and assign it to the corresponding layer. Be extremely careful when modifying. Overwrite or code run operations are strictly prohibited. Use only small patches; if modifying becomes difficult, do not change it at all.
**Prohibited**: Strictly forbidden to write passwords or API Keys. Inline non-sensitive trigger parameters (like proxy port) are allowed. Do not write "How to" or detailed explanations. Strictly forbidden to contain specific task technical details (specific task details should be in L3). Even more strictly forbidden to write operation logs!
---
### L2: Global Fact Base (global_mem.txt)
**Responsibility**: Store global environmental facts (paths, credentials, configs, constants, etc.).
**Characteristics**:
- Trend: Expands as the environment scales (acceptable)
- Content: Fact entries organized by `## [SECTION]`
- Synchronization: Update corresponding TOPIC navigation lines in L1 when changes occur; it can only act as navigation.
**Prohibited**: Forbidden to store volatile states. Forbidden to store guesses. Strictly forbidden to store general common sense that the large model can deduce.
---
### L3: Task-level Essential Record Base (../memory/)
Responsibility: Supplement a small amount of detailed information that cannot be accommodated in L1/L2 but is crucial for future reuse of **specific tasks**. Content must be **as brief as possible** while meeting reuse requirements.
Principles:
- Only record: Key points that remain important across sessions and are hard to quickly reconstruct via minimal file_read/web_scan/simple scripts.
- Priority: Hidden prerequisites unique to the task, typical pitfalls, and information that, if forgotten, leads to high-cost retries.
- Do not record: Ordinary operational steps, path or state info that can be regained within a few probing steps.
Format:
- SOP (*_sop.md): Preserve a minimalist "critical prerequisites + typical pitfalls" checklist for a single task or small category of tasks, avoiding lengthy tutorials.
- Tool Scripts (*.py): Only encapsulate high-reuse, relatively complex processing flows that you don't want to deduce from scratch every time.
---
## L1 ↔ L2/L3 Synchronization Rules
| Operation | L1 Synchronization |
|---------|--------|
| New Scenario in L2/L3 | Judge frequency: High frequency → Add key→value to 1st layer; Low frequency → Add keyword to 2nd layer |
| Delete Scenario in L2/L3 | Delete corresponding keyword/mapping line |
| Modify Value in L2/L3 | If scenario location is unaffected, do not touch L1 |
| Found Common Pitfall Pattern | Compress into one sentence and add to RULES |

> **Synchronization Red Line**: L1 strictly contains keywords/names; transferring details is prohibited. Evaluate token count and index utility in L1 on an ongoing basis.

---
## Fast Decision Tree for Info Classification
```
"Which layer should this info go to?"

Is it an "Environment-specific fact"? (IP, irregular path, credential, ID, API key, etc., things LLM zero-shot cannot generate accurately)
  ├─ YES → L2 (global_mem.txt)
  │        Then → Assign to L1 1st layer (key→value) or 2nd layer (keywords only) by frequency
  │
  └─ NO
       ↓
       Is it a "General operation rule"? (Global pitfalls, troubleshooting methods, general rules not specific to a single task)
       ├─ YES → L1 [RULES] (Limited to 1 compressed sentence rule)
       │
       └─ NO
            ↓
            Is it "Specific task technique"? (Requires intense troubleshooting to succeed, and task might be reused later, e.g., WeChat parsing params, specific game coordinates, temp tool config)
            ├─ YES → L3 (../memory/ Special SOP or script)
            │
            └─ NO → Deemed "Common sense" or "Redundant info": Storage strictly forbidden, discard directly
```