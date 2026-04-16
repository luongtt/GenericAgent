# Autonomous Operation SOP

⚠️ **Path Warning**: `autonomous_reports` is under `temp/`. Access it using `./autonomous_reports/`, **NOT** `../memory/autonomous_reports/` or `../autonomous_reports/`! TODO is under cwd.
Reports are stored in `./autonomous_reports/`, filename `RXX_Short_Description.md` (XX auto-increments inferred from history.txt).

You are authorized to conduct autonomous operations, provided no side-effects are caused to the environment.

## Initialization (Step 1)
- `update_working_checkpoint`: `Autonomous Action | Re-read SOP during wrap-up | from autonomous_operation_sop.helper import *; set_todo()/complete_task(tasktitle, historyline, report_path)`

Step 2:
```python
from autonomous_operation_sop.helper import *
print(get_history(40))  # Understand history to avoid repetition
print(get_todo())       # Check pending to-dos
```

## Task Selection
- If there are incomplete items → pick **one** and proceed to execution. Do others next time.
- If no TODOs → read `autonomous_operation_sop/task_planning.md` to plan, execute next time.
- Do not execute the same sub-task twice consecutively.
- Value Formula: **"AI training data unable to cover" × "Long-term benefit for future collaboration"**

## Execution
- After selecting a task, `update_working_checkpoint`, append the selected TODO item and execution warnings to the checkpoint.
- Call `code_run` to prepare an ending callback. The script is `handler._done_hooks.append("Re-read autonomous task SOP, check if your wrap-up work is correct, and correct it if not")`, `_inline_eval=True` (secret parameter).
- ≤ 30 turns. Take small, fast steps. Probe and experiment simultaneously.
- Use temporary scripts to verify hypotheses; forbidden from concluding through read-only probes. Only write reports after complete verification.
- Even if it fails, record the experimental process and results. Failure reports are equally valuable.
- The user is offline. If you encounter a problem requiring a decision, write it in the report pending review instead of getting stuck.

**Wrap-up (Three mandatory steps)**:
0. Re-read this SOP.
1. Write a report in `cwd` (any filename). If memory update suggestions exist, append them to the end of the report.
2. `from/import helper; complete_task(tasktitle, historyline, report_path)` → Auto numbers + moves the report to `autonomous_reports/` + prepends `history` (historyline format: `Type | Subject | Conclusion`, strictly single line).
3. `set_todo()` to get the TODO path → Mark completed items as `[x]`.

## Permission Boundaries
- No approval required: Read-only probes, write operations/script experiments within `cwd`.
- Pending review in report required: Modifying `global_mem` / SOPs under `memory`, installing software, external API calls, deleting non-temp files.
- Absolutely Forbidden: Reading secret keys, modifying core codebases, irreversible dangerous operations.

## Pending User Review
- Upon the user's return, they will review the reports to decide whether to approve, modify, or reject proposals.