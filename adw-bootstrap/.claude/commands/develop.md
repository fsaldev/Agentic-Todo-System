# Develop

Implement a plan from a spec file.

## Variables

- `spec_path`: $1 - Path to the spec file
- `issue_id`: $2 - (Optional) Linear issue ID for commenting (e.g., "ACA-123")

## Instructions

1. **Read the Spec**
   - Read the spec file at `spec_path`
   - Understand all requirements and steps
   - Extract the Linear issue ID if present in the spec

2. **Post Start Comment (if Linear issue)**
   If `issue_id` is provided or found in spec, post a comment using `mcp__linear__create_comment`:
   ```markdown
   ## 🚀 Development Started

   **Branch:** `{current_branch}`

   ### Approach
   {brief summary of implementation approach from spec}
   ```

3. **Read Context**
   - Read `.claude/commands/conditional_docs.md`
   - Read any additional docs relevant to the task

4. **Implement**
   - Follow the Implementation Steps in order
   - Make changes to the files listed
   - Follow existing code patterns

5. **Validate**
   - Run the Validation Commands from the spec
   - Fix any issues that arise
   - Ensure all tests pass

6. **Post Completion Comment (if Linear issue)**
   Post a comment using `mcp__linear__create_comment`:
   ```markdown
   ## ✅ Development Complete

   ### Files Changed
   {list files from git diff --stat}

   ### Summary
   {what was implemented}
   ```

7. **Report**
   - Summarize what was implemented
   - Show `git diff --stat`

## Guidelines

- Follow existing code style and patterns
- Don't over-engineer - implement exactly what's specified
- If something is unclear, check the spec again
- Commit frequently with clear messages

## Output

Provide a summary:

```
## Implementation Summary

### Changes Made
- {Brief description of change 1}
- {Brief description of change 2}

### Files Modified
{output of git diff --stat}

### Validation
- [ ] Backend tests: PASS/FAIL
- [ ] Frontend build: PASS/FAIL

### Notes
{Any issues encountered or decisions made}

### Linear
{issue_id}: 2 comments posted
```
