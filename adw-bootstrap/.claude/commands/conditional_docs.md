# Conditional Documentation Guide

This guide helps you read only the documentation relevant to your current task.
**Read this file first** when starting any new session or task.

## Instructions

1. Identify your current task/context
2. Find matching conditions below
3. Read ONLY the documentation that matches your task
4. Skip irrelevant documentation to preserve context

## Documentation Routes

### Project Understanding
- **README.md**
  - When: First time understanding the project
  - When: Need to run server/client
  - When: Understanding project structure

- **PRD.md**
  - When: Understanding product requirements
  - When: Need full context on what's being built
  - When: Checking acceptance criteria

- **Linear Projects** (via `mcp__linear__list_projects` / `mcp__linear__get_project`)
  - When: Checking current project status
  - When: Need to see which features are done vs pending
  - When: Looking up Linear issue IDs for features

### Workflow State
- **.claude/workflows/{workflow_id}/state.json**
  - When: Resuming an existing workflow
  - When: Need to know current phase, branch, or spec file
  - When: Checking what phases have been completed

### Implementation Plans
- **.claude/workflows/{workflow_id}/spec.md**
  - When: Implementing a plan (develop phase)
  - When: Reviewing implementation against requirements
  - When: Need to understand what was planned
  - Note: Linear issue details remain the source of truth for requirements

### Backend Development
- **app/server/README.md** (if exists)
  - When: Working on Python backend code
  - When: Adding API endpoints
  - When: Modifying database operations

- **app/client/src/style.css**
  - When: Making style/CSS changes to the client

### Frontend Development
- **app/client/README.md** (if exists)
  - When: Working on TypeScript/React frontend
  - When: Modifying UI components
  - When: Adding client-side features

### Testing
- **.claude/commands/test.md**
  - When: Running the test suite
  - When: Understanding test structure
  - When: Fixing failed tests

### ADW System
- **.claude/adw/** files
  - When: Modifying the ADW workflow system
  - When: Adding new workflow phases
  - When: Debugging workflow issues

- **adws/README.md**
  - When: Working with the original ADW reference implementation

## Quick Reference

| Task | Read First |
|------|------------|
| New to project | README.md |
| Project status | Linear Projects (MCP tools) |
| Product requirements | PRD.md |
| Resume workflow | .claude/workflows/{id}/state.json |
| Implement feature | Linear issue details → spec.md |
| Fix test | .claude/commands/test.md |
| Backend work | app/server/ |
| Frontend work | app/client/ |

## Notes

- Linear is the single source of truth for project and issue status
- Use `mcp__linear__get_issue` for detailed implementation requirements
- Check issue descriptions for acceptance criteria before implementing
- Workflow state.json tracks local progress; spec.md captures the plan
- Always check state.json when resuming work to know current phase
- Each workflow is independent - don't mix contexts
