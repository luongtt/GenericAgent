# Plan Mode SOP

**Trigger**: ≥3 steps with dependencies / multi-file coordination / conditional branching / requiring parallelism | **Forbidden**: Do 1-2 step simple tasks directly
Before starting the task, you must create a working directory `./plan_XXX/` (XXX = English short name of the task)
Use `code_run({'inline_eval':True, 'script':'handler.enter_plan_mode("./plan_XXX/plan.md")'})` alone to enter plan mode.

---

## I. Exploration State (Pre-planning, MUST execute)

⛔ **Hard Rules (Read before doing)**:

- **Main agent is forbidden from performing environmental probes directly** (Must delegate to subagent, no exceptions)
- Main agent only does: create directory, read SOP index, start subagent, read conclusions
- Subagent only does read-only probing, forbidden from modifying any files or executing operations with side effects
- **If exploration subagent fails to start: troubleshoot cause → retry, max 2 times. Main agent is forbidden from falling back to probing itself**

**Goal**: Before writing any plan, figure out 3 things:
① Environment status (what exists, what's missing) ② Available SOPs ③ Key uncertainties

**Why use a subagent**: Main agent's context is the scarcest resource. Long probe outputs will crowd out space for planning and execution.

### Step 1: Create Directory (Mandatory) + Match SOP + Set Plan Flag (Main agent does directly)

1. Create working directory `mkdir plan_XXX/`
2. Read `sop_index.md` to match available domain SOPs
3. Update checkpoint: `[Task] XXX | [Requirement] One sentence | [Constraints] Key limits | [Matched SOP] ... | [Progress] Exploration State`

### Step 2: Start Exploration Subagent (Supervise mode)

Start the exploration subagent according to `subagent.md`, **add `--verbose`** to enable supervise mode. Key input inputs:

- **Task**: Probe environment info, write to `plan_XXX/exploration_findings.md`
- **Probe Items** (Choose based on task type, do not do all):
  - Code type → Key file structure, dependencies, entry points
  - Browser type → Target page current state, interactive elements
  - Automation type → Environment check (which/pip/path/permissions)
  - Data type → Sample data (Top 5 rows + Bottom 5 rows + Total count)
- **Output Format**: `## Environment Status` / `## Key Findings` / `## Risks/Uncertainties`
- **Constraints**: Read-only probing, file modification forbidden, ≤10 tool calls
- **Complexity Assessment**: Note data scale during probing (file count, line count, page count), write to findings for delegation judgment during planning

### Step 3: Supervise Wait + Read Conclusions

Main agent actively observes `output.txt` progress (`--verbose` output contains raw tool results), instead of blindly sleeping and polling:

1. **Observe**: Read `output.txt`, review the subagent's probing direction and raw data
2. **Correct** (as needed):
   - Off-direction → Write `_intervene` to append corrective instructions
   - Missing key context → Write `_keyinfo` to inject info
   - Enough info obtained → Write `_stop` to terminate early, saving turns
3. **Collect**: Wait for `[ROUND END]`, read `exploration_findings.md`

**Output**: `exploration_findings.md` (Structured finding report). Main agent relies on this to enter the planning state, writing it into the "Exploration Findings" section at the top of `plan.md`. First-hand cognition gained by the main agent during supervision can also be directly used for planning.

---

## II. Planning State (Includes Review Gate)

### Step 4: Read Domain SOP → Write plan.md

First read SOPs matched during the exploration state, then write the plan skeleton. "⚠ To be confirmed" is allowed, postponing due to "not investigated clearly" is forbidden.

**[D] Delegation Marking Rule**: When writing each step, assess the workload based on exploration findings. Mark `[D]` if matching any of the following:

- Need to read a large amount of code/files (estimated >3 files or >100 lines)
- Need to browse websites and extract info
- Need to execute repetitive operations >3 times
- Need to run tests/builds and analyze output

Instances NOT to mark `[D]`: Read/update plan.md, minor single-file modifications, `ask_user`, simple one-off commands.

**plan.md Format**:

```markdown
<!-- EXECUTION PROTOCOL (Read every turn, this is your execution guide)
1. file_read(plan.md), find the first [ ] item
2. If the step is marked with an SOP → file_read the 🔑 Quick Reference section of that SOP
3. Execute the step + Mini-verify output
4. file_patch to mark [ ] → [✓]+brief result, then return to step 1 to continue to the next [ ]
5. After all steps (including verify steps) are marked → Termination check: file_read(plan.md) explicitly confirm 0 [ ] remain
⚠ Forbidden to execute from memory | Forbidden to skip verify steps | Forbidden to end without termination check | Forbidden to stop to output plain text reports
💡 Brick-moving work (reading lots of code/files/pages/repetitive operations) prioritize delegation to subagents, keeping main agent context clean
-->
# Task Title
Requirement: One sentence | Constraints: Key limits

## Exploration Findings
- Finding 1: XXX (Source: file_read/web_scan/code_run)
- Finding 2: YYY
- Uncertainties: ZZZ

## Execution Plan
1. [ ] Step 1 summary
   SOP: xxx_sop.md
2. [D] Step 2 summary (Delegate to subagent)
   SOP: yyy_sop.md
   Dependency: 1
3. [P] Step 3 summary (Parallel, read subagent.md execute Map mode)
   SOP: yyy_sop.md
4. [?] Step 4 (Conditional branch)
   SOP: (None) ← High risk
   Condition: If X succeeds→4.1, else→4.2

---

## Verification Checkpoint
N+1. [ ] **[VERIFY] Start independent verification subagent**
     SOP: verify_sop.md
     Action: Prepare verify_context.json → Start verification subagent → Read VERDICT → Handle per result
     ⚠ Cannot be skipped, cannot be marked [✓] without starting the subagent

---
```

### Step 5: Self-Check Checklist (Main agent checks item by item)

- □ Are all exploration findings reflected in the plan? (No key constraints missed)
- □ Is the marked SOP reasonable for each step? (Can the SOP really solve the step?)
- □ Are step dependencies correct? (Any implicit dependencies unwritten?)
- □ Do high-risk steps (SOP:None/Irreversible) have a clear execution thought process?
- □ Is step granularity appropriate? ("Process all files" is forbidden, must expand into specific items)
- □ **Are complex/tedious steps marked [D]?** (Reading lots of code/pages/repetitive ops MUST be delegated)
- □ **Is the "Verification Checkpoint" section included, with a [VERIFY] step? (MUST exist, it's mandatory)**

### Step 6: User Confirmation

`ask_user` to confirm the plan before transitioning into the execution state. **⛔ Do not execute unconfirmed plans.**

### Step 7: Transition to Execution State

Update checkpoint: `[Execution] plan.md | Current: Step 1 | ⚡If marked [P], must read subagent.md to execute Map mode`

---

## III. Execution State Loop

> **Core Principle: Execute continuously, without pausing to report.** Immediately `file_read(plan.md)` after finishing a step to find the next `[ ]`, until all are done.

### Per-Turn Flow

1. **Read plan** — `file_read(plan.md)` locate the first `[ ]` item
2. **Read SOP** — If the step marks an SOP → `file_read` that SOP first
3. **Check flags** — `[D]` flag → must delegate to subagent, main agent only receives summary; `[P]` flag → `file_read subagent_sop.md` to execute Map mode; `[?]` condition → assess condition to pick branch, unmarked ones mark `[SKIP]`
4. **Execute** — Steps with no special marks are executed by the main agent itself
5. **Mini-Verification** — Quickly verify output exists and makes sense (`file_read` non-empty, `exit code`, etc.)
6. **Mark Complete** — `file_patch` mark `[ ]` → `[✓ Brief result]` (Progress written to `plan.md`)
7. **Continue** — Immediately return to step 1, `file_read(plan.md)` to execute the next `[ ]`

### Termination Check (After the last step is marked, indispensable)

`file_read(plan.md)` full text scan, confirm all steps (including `[VERIFY]`) are `[✓]`/`[✗]`, with 0 `[ ]` remaining.
Output: `🏁 Termination Check: All [Total] steps completed, 0 [ ] remain → Task finished`
If omissions found → continue execution, forbidden to falsely claim completion.

### ⚠ Execution State Bans

- **Forbidden to execute from memory**: You must `file_read(plan.md)` before each new step. Do not assume "I remember the next step is..."
- **Forbidden to skip verification steps**: The `[VERIFY]` step is mandatory and cannot be skipped using the excuse "All task work is completed."
- **Forbidden to end without a termination check**: After marking the last step, a full text `file_read` scan is required to confirm 0 `[ ]` remain, and output a 🏁 termination confirmation line.
- **Forbidden to stop to output plain text reports**: Do not output progress summaries after a step; immediately `file_read(plan.md)` and continue.

### 💡 Dynamic Delegation Principle

During execution, even if a step is not marked `[D]`, proactively delegate to a subagent if the following occurs:

- You need to read a lot of code/files to understand the context (>3 files or estimated >100 lines)
- Intensive trial-and-error debugging is required
- You need to browse webpages to extract information

How to: Start a subagent to perform the specific operation and ask it to return a concise summary. The main agent continues decision-making based on the summary. Keeping the main agent's context clean is the highest priority.

---

## IV. Verification State (Subagent Independent Verification)

> Enter after all steps are `[✓]`. A mandatory start of an independent subagent to do adversarial verification to prevent context pollution.

### Trigger Conditions

- All execution steps marked as `[✓]`
- **All plan mode tasks must be verified by a subagent** (Main agent has confirmation bias and is easily fooled by superficial successes)

### Step 8: Prepare Verification Context

Create `verify_context.json` under `./plan_XXX/`, including:

- `task_description`: Original task description (User's exact words)
- `plan_file`: Absolute path of `plan.md`
- `task_type`: code|data|browser|file|system
- `deliverables`: List of deliverables (type/path/expected)
- `required_checks`: List of mandatory checks (check/tool)

**What to pass**: Task description, plan path, deliverables list, required checks. **Do NOT pass**: Execution process, debugging logs.

### Step 9: Start Verification Subagent

Start verification subagent per `subagent.md` standard process. Key inputs:

- **Role**: You are an independent verifier. Your job is adversarial verification (prove deliverables are unusable).
- **Step 1 is mandatory**: `file_read verify_sop.md` to completely read the verification SOP
- **Execute the chosen verification strategy** based on `task_type` according to Section 3 of `verify_sop.md`.
- **Each check must have tool operation evidence** (actual execution, not a narrative).
- **Task Description**: (Fill in original request)
- **Deliverables List**: (Fill in deliverables list)
- **Output**: Output in `result.md` per layout in Section 6 of `verify_sop.md`, with the last line being `VERDICT: PASS / FAIL / PARTIAL`
- **Constraints**: Finish within 3 turns, at least 1 actual tool call per turn.

Simultaneously pass the path to `verify_context.json` so the subagent can read the detailed context itself.

### Step 10: Collect Verification Results

Poll `output.txt` to wait for `[ROUND END]`, then read `result.md`:

1. **Find the VERDICT line**: Read the last few lines of `result.md` to extract `VERDICT: PASS/FAIL/PARTIAL`
2. **Check validity**: If all PASS items lack tool call output (only narrative), the verification is deemed invalid and treated as FAIL.
3. **Handle per result**:
   - **PASS** → Proceed to task completion wrap-up
   - **FAIL** → Enter the repair loop
   - **PARTIAL** → Main agent deems acceptable to complete, else repair
   - **No VERDICT line** → Extract key info from `output.txt`, main agent judges PASS/FAIL independently.

**Task Completion Wrap-up** (Executed after Verification PASS):

1. Mark the `[VERIFY]` step in `plan.md` as `[✓]`
2. Update checkpoint: `[Completed] XXX Task | [Output] ... | [Experience] ...`
3. Confirm task completion to the user

**Critical**: Only after verification is PASS can you mark `[VERIFY]` as `[✓]` and claim task completion. If verification is FAIL, enter the repair loop.

**Fallback**: If the subagent fails to produce `result.md` (turns exhausted), extract VERDICT key info from `output.txt`.

### Repair Loop (After FAIL)

FAIL → Extract specific failure items → Return to execution state to fix (do not re-plan) → Repair complete → Restart verification subagent → Max 2 rounds of FAIL-Retry, beyond this involve `ask_user`.

When repairing:

1. Append FAIL items as new steps to `plan.md` (marked as `[FIX]`)
2. Only repair failing items; do not redo already PASS parts.
3. Prepare a new `verify_context.json` (containing only failing items) once repaired.

### Special Scenario Handling

Browsers / Keyboard/Mouse / Cron jobs, etc.: Main agent executes operations and exports evidence (screenshots/recordings/logs) → Subagent verifies evidence files. **Main agent is forbidden from judging PASS/FAIL itself.**

---

## V. Failure Handling

1. **Record**: `step_X: [FAILED] Reason (retry: N/3)` in checkpoint
2. **Retry**: Network timeout → auto retry 3 times (2s/4s/8s) | Config error → ask user | Other → mark `[✗]` and skip
3. **Subagent Failure**: Check `stderr.log` → If clear error, main agent corrects and restarts | If unknown error, retry 1 time | Max 2 restarts total
4. **Dependency Propagation**: When a step fails, mark its subsequent dependencies as `[SKIP]`.
5. **Plan is Wrong**: Revert to planning state to fix `plan.md`, go through review gate again.

## Hard Constraints

- Every item must have independent completion criteria.
- "Process all files" is forbidden. Expand into specific items.
- Only do one item at a time. If the plan is flawed, return to the planning state to fix it.
- Take an extra verification step before executing an irreversible operation.
