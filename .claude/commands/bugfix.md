# Bugfix

Fix a bug and automatically document it in Linear.

## Variables

- `bug_description`: $1 - Description of the bug to fix

## Instructions

### 1. Understand the Bug

- Ask clarifying questions if the bug description is unclear
- Reproduce or locate the bug in the codebase
- Identify the root cause

### 2. Plan the Fix

Before coding, briefly outline:
- What's causing the bug
- What changes are needed to fix it
- Any potential side effects

### 3. Implement the Fix

- Make the necessary code changes
- Follow existing code patterns
- Keep changes minimal and focused

### 4. Validate

- Test that the bug is fixed
- Ensure no regressions were introduced
- Run relevant tests if available

### 5. Commit

Commit with a `fix:` prefix message:
```bash
git add <files>
git commit -m "fix: <concise description of what was fixed>"
```

### 6. Create Linear Bug Issue

**IMPORTANT**: Always create a Linear bug issue for documentation.

Use `mcp__linear__create_issue` with:
- **title**: Clear description of the bug
- **team**: "Acadexis"
- **project**: Current project (e.g., "Job Posting")
- **state**: "Done"
- **labels**: ["Bug"]
- **description**: Use this format:

```markdown
## Bug

{Description of what was broken and how it manifested}

## Root Cause

{Technical explanation of why the bug occurred}

## Fix

{What changes were made to fix it}

## Files Changed

{List of files modified}

## Commits

{Commit hash(es) and message(s)}
```

### 7. Push Changes

```bash
git push
```

### 8. Report

Provide a summary:

```
## Bug Fix Summary

### Bug
{What was broken}

### Root Cause
{Why it was broken}

### Fix
{What was changed}

### Linear Issue
{Issue ID}: {URL}

### Commits
{List of commits}
```

## Guidelines

- Keep fixes focused - don't refactor unrelated code
- Document the root cause clearly for future reference
- Always create the Linear issue - this is non-negotiable
- If multiple bugs are fixed, create separate Linear issues for each

## Example

```
/bugfix "Email regeneration shows 'failed to fetch' error and navigates to /emails/0"
```
