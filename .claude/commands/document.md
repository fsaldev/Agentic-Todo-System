# Document

Generate documentation for a completed feature.

## Variables

- `workflow_id`: $1 - Workflow ID to document

## Instructions

1. **Load Context**
   - Read `.claude/workflows/{workflow_id}/state.json`
   - Read the spec file from state
   - Run `git diff origin/main --stat` to see changes

2. **Analyze Changes**
   - Understand what was built
   - Identify key files and components
   - Note any configuration changes

3. **Generate Documentation**
   - Create doc at: `docs/features/{workflow_id}-{name}.md`
   - Use the Documentation Format below
   - Be concise and practical

4. **Update Conditional Docs**
   - Add entry to `.claude/commands/conditional_docs.md`
   - Specify when this doc should be read

## Documentation Format

```markdown
# {Feature Title}

**Workflow ID:** {workflow_id}
**Date:** {current date}
**Issue:** {issue_id}

## Overview

{2-3 sentences describing what was built and why}

## What Was Built

- {Component/feature 1}
- {Component/feature 2}

## How to Use

1. {Step 1}
2. {Step 2}

## Technical Details

### Files Changed
- `path/to/file`: {what changed}

### Key Implementation Notes
- {Important detail 1}
- {Important detail 2}

## Configuration

{Any env vars or config needed}

## Testing

```bash
# How to test this feature
{command}
```
```

## Output

Return ONLY the path to the created documentation file:
```
docs/features/{workflow_id}-{name}.md
```
