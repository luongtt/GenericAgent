# Subagent Invocation SOP

## File IO Protocol

- Directory: `temp/{task_name}/` (when cwd is temp/, it's `./{task_name}/`)
- Startup: `python agentmain.py --task {name} [--input "short text"] [--bg] [--llm_no N]` (cwd = code root)
- `--input` auto creates dir + clears old output + writes input.txt; For long text, manually write input.txt first then start (without --input).
- `--bg` background (print PID exit), you can sleep then poll in the same code_run; without --bg, do not combine startup + polling.
- input: Target + constraints are enough, subagent has equal intelligence. **Do not write steps/over-describe**, for large amounts of data provide paths.
- Communication: output.txt (append, `[ROUND END]` = turn completed) → write reply.txt to continue → will exit if not written within 10min. After a reply, output goes to output1/2/3.txt (same format).
- Intervention files: `_stop` (exits when current turn ends) | `_keyinfo` (injects to working memory) | `_intervene` (appends instructions)
- **When idle, the main agent should read output to observe progress, and use intervention files to correct course if necessary. Mindless long-sleep polling is forbidden.**
- Add `--verbose` when starting in supervisor mode, the output will contain tool execution results, allowing the main agent to directly review raw data rather than just trusting summaries.

## Scenario 1: Test Mode - Behavior Validation
**Purpose**: Observe genuine agent behavior, fix RULES/L2/L3/SOP
**Process**: Create test_path/write input.txt → start subagent → poll output.txt (2s intervals) → validate → clear repeats
**Testing Principle**: Only give target, do not hint at location/induce approach, observe autonomous choices.
**Correction Loop**: Discover issue → Design test → Locate root cause (RULES/L2/L3/SOP) → Patch correction → Verify
**Technical Keys**: Insight priority > SOP; subagent cwd = temp/
**Two types of tests**:
- Test SOP quality: input specifies SOP name (e.g., "Use ezgmail_sop to view latest 3 unread emails"), eliminates navigation interference, failure means SOP issue.
- Test Navigation ability: input only writes target, verifies subagent can independently find the right SOP from insight. Inlining SOP content is prohibited.

## Scenario 2: Map Mode - Parallel Processing
**Purpose**: Distribute N independent isomorphic subtasks to their respective subagents for processing.
**Core Advantage**: Independent context. Avoids long context from processing Document A polluting the quality of processing Document B.
**Constraints**:
- File system sharing is a plus: different agents process different input files, producing different output files.
- Shared resource conflicts: Keyboard/mouse cannot be shared; browser temporarily cannot be used in parallel to avoid interacting with the same tab simultaneously.
- Tasks that don't fit map mode → Main agent executes sequentially, don't use subagents.
**Standard Flow (map-reduce)**:
1. Main agent prep phase: Crawl/dump data, save as multiple independent input files.
2. Distribution: Start a subagent for each file (main agent can also process one itself).
3. Collection: Wait for all subagents to complete, main agent reads output files to aggregate results.

## Subagent Internal plan_mode Usage
**Principle**: The subagent itself is a complete agent, when receiving multi-step tasks it should internally create a plan to manage execution.
**Trigger conditions**: Task contains 3+ sub-steps, sub-steps have dependencies, checkpoints needed to resume.
**Implementation**:
1. **When main agent creates subagent**: Specify in input.txt that the task has multiple steps and recommend using plan_mode.
2. **Subagent internal execution**: Upon detecting a multi-step task, create `./subagent_plan.md` and use plan_mode to execute.
3. **Main agent monitoring**: Only focus on final results (output*.txt), no need to care how the subagent executes internally.
4. **File passing mechanism**: When creating the subagent, the main agent generates `context.json` in the task_dir containing **absolute paths** to all files.
   **⚠ The first step after the subagent starts MUST be reading context.json**
   **⚠ All file operations MUST use the absolute paths from context.json**
**Format Example**:
```json
{
  "task": "Task description",
  "work_dir": "/absolute/path/to/plan_dir/",
  "input_files": {
    "paper_info": "/absolute/path/to/paper_info.txt"
  },
  "output_files": {
    "pdf": "/absolute/path/to/paper.pdf",
    "report": "/absolute/path/to/paper_report.md"
  },
  "dependencies": ["paper_info.txt must exist"]
}
```