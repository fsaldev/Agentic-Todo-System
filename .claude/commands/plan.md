# Plan

Create an implementation plan from an issue or task description.

## Variables

- `issue_id`: $1 - Linear issue ID (e.g., "ABC-123") or "MANUAL-0" for text input
- `workflow_id`: $2 - Unique workflow identifier
- `issue_json`: $3 - JSON with issue details (may be placeholder for Linear issues)

## Instructions

### 1. Fetch Issue Details

**If `issue_id` looks like a Linear issue (e.g., "ABC-123"):**
- Use the Linear MCP tools to fetch the issue details
- Call `linear_getIssue` or equivalent with the issue ID
- Extract: title, description, labels, priority, state

**If `issue_id` is "MANUAL-0":**
- Use the title/description from `issue_json` directly

### 2. Classify the Issue

Based on the issue content and labels, determine the type:
- **bug**: Fix something broken
- **feature**: Add new functionality
- **chore**: Maintenance, refactoring, dependencies

### 3. Research the Codebase

- Read `.claude/commands/conditional_docs.md` to find relevant docs
- Explore files related to the task
- Understand existing patterns and architecture

### 4. Create the Plan

- Create spec file at: `.claude/workflows/{workflow_id}/spec.md`
- Use the Plan Format below
- Be specific and actionable

### 5. Include Validation

- Add test commands to verify the implementation
- Include regression test commands

## Plan Format

```markdown
# {Issue Type}: {Title}

## Metadata
- workflow_id: `{workflow_id}`
- issue_id: `{issue_id}`
- type: {feature|bug|chore}
- linear_url: {URL from Linear if available}

## Summary
{2-3 sentence description of what needs to be done}

## Requirements
{List of specific requirements from the issue}

## Implementation Steps

### Step 1: {Action}
- {Detail}
- {Detail}

### Step 2: {Action}
- {Detail}
- {Detail}

{Continue as needed}

## Files to Modify
- `path/to/file.py` - {reason}
- `path/to/other.ts` - {reason}

## Validation Commands
Run these commands to verify the implementation:

```bash
# Backend tests
cd app/server && uv run pytest -v

# Frontend checks
cd app/client && bun tsc --noEmit
cd app/client && bun run build
```

## Notes
{Any additional context or considerations}
```

## Output

Return ONLY the path to the created spec file:
```
.claude/workflows/{workflow_id}/spec.md
```
