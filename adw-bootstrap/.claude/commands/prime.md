# Prime

Onboard to the codebase for a new session. Run this command when starting fresh to understand the project context.

## Instructions

1. List all tracked files to understand project structure
2. Read core documentation
3. Check for active projects in Linear (single source of truth)
4. Summarize your understanding

## Run

```bash
git ls-files
```

## Read

Read these files in order:

1. **README.md** - Project overview and setup
2. **.claude/commands/conditional_docs.md** - Documentation routing guide
3. **.claude/current-work.md** - Current work in progress (active issue, status, recent changes)

## Check Active Projects

Query Linear for active projects:
- Use `mcp__linear__list_projects` with state "In Progress" to find active projects
- For each relevant project, use `mcp__linear__get_project` to read the description

If projects exist, the description contains:
- What features are planned
- Feature dependencies and acceptance criteria
- Check associated issues in Linear for completion status (use Linear's project progress)

Also check for PRD.md in the root (product requirements):
```bash
ls -la PRD.md 2>/dev/null || echo "No PRD file"
```

## Output

After reading, provide a concise summary:

1. **Project Purpose**: What does this project do?
2. **Tech Stack**: What technologies are used?
3. **Key Directories**: Where is the main code?
4. **How to Run**: Commands to start the application
5. **Current Project Status**: Features completed vs pending (from Linear)
6. **Current Work**: What's actively being worked on (from .claude/current-work.md)

Keep the summary brief but include the project status table if a Linear project exists.
