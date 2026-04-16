# GitHub Contribution SOP
**Trigger**: When needing to submit a PR to an open-source project (fix bug / add feature / modify doc) | **Prohibited**: When only reading code or no changes need to be submitted
**Core Principles**: One PR does one thing, only push if tests pass, respect project conventions

## Pre-requisites (Execute once for each new project)
1. **Read project guidelines** (Mandatory, cannot skip)
   ```
   file_read('CONTRIBUTING.md')  # Contribution guide
   file_read('.github/PULL_REQUEST_TEMPLATE.md')  # PR template
   file_read('.github/ISSUE_TEMPLATE/')  # Issue templates
   ```
   If absent, read the Contributing section of README. If neither exist, follow the default flow of this SOP.

2. **Understand project structure and testing methods**
   ```
   # Find test command
   file_read('package.json')  # Node: scripts.test
   file_read('Makefile')      # or Makefile
   file_read('pyproject.toml') # Python: [tool.pytest] etc.
   ```
   Note down the test command for later use. A PR that cannot run tests = an unverified PR.

3. **Fork + Clone**
   ```
   code_run('bash', 'gh repo fork OWNER/REPO --clone && cd REPO && git remote -v')
   ```

## Workflow (For each PR)

### Step 1: Confirm goal
- Read related Issue (if any)
- Write clearly in one sentence: what to change, why change it
- Check: is someone else already doing it? (Check Issue assignee, recent PRs)

### Step 2: Create branch
```
code_run('bash', 'git checkout -b fix/issue-description && git status')
```
Branch naming: `fix/xxx` (fix bug), `feat/xxx` (new feature), `docs/xxx` (documentation)

### Step 3: Implement changes
- **Minimize changes**: Only change what is needed, do not casually refactor unrelated code
- **Follow project style**: Keep indentation, naming, and comment styles consistent with existing code
- **Commit once for every logical point modified**:
  ```
  code_run('bash', 'git add -A && git commit -m "fix: concise description"')
  ```
- Commit message format: Follow project conventions (Conventional Commits / Project customs)
  - If no convention exists, use: `type: short description`
  - type: fix / feat / docs / refactor / test / chore

### Step 4: Testing (Cannot be skipped)
```
code_run('bash', 'project test command')  # npm test / pytest / go test ./...
```
**Checklist**:
- [ ] All existing tests passed?
- [ ] New feature has corresponding tests? (If the project has a testing culture)
- [ ] lint/type check passed? (If the project has it)

**⛔ If tests fail, do not push code. Fix until they pass.**

### Step 5: Push + Submit PR
```
code_run('bash', 'git push origin HEAD')
```
PR Content:
- **Title**: `type: concise description` or following project template
- **Body** must contain:
  - What was changed (What)
  - Why it was changed (Why) — To link an Issue use `Fixes #123`
  - How it was tested (Testing)
- **Do not write**: Over-explanation, unrelated background, bragging

### Step 6: CI Checks
Wait for CI after submitting PR:
- ✅ All passed → Wait for review
- ❌ Has failures → Read logs, fix your own issues
  - If CI failure is an upstream issue (unrelated to your changes) → Explain it in the PR
  ```
  code_run('bash', 'gh run view --log-failed')
  ```

### Step 7: Respond to Review
- **Change what the reviewer asks to change**, do not argue over style preferences
- **Disagreements on technical decisions**: Politely state reasons, but ultimately respect the maintainer
- **After changing**: Append commits + push, do not force push (unless maintainer requests squash)
- **Reviewer asks to add tests** → Add them, this is not optional

## Common Mistakes (Pitfalls)

| Error | Correct Action |
|------|----------|
| One PR changes multiple things | Split into multiple PRs, each independent |
| Submitted PR but didn't follow up | Check review status daily |
| Pushed without running tests | Step 4 is a hard requirement |
| Changed code style is messy | Keep consistent with existing code |
| Commit message says "update" | Write specifically what was changed |
| Force push overwrites review history | Append commits |
| PR description is blank | Write What/Why/Testing |

## Follow-up State Machine

```
PR Submitted → Wait for CI
  CI ✅ → Wait for Review
    Review Passed → Wait for Merge ✅
    Review demands changes → Change + Test → Go back to waiting for CI
  CI ❌ → Fix → Go back to waiting for CI
```

Commands used for each follow-up round:
```
code_run('bash', 'gh pr status')
code_run('bash', 'gh pr checks PR_NUMBER')
code_run('bash', 'gh pr view PR_NUMBER --comments')
```
