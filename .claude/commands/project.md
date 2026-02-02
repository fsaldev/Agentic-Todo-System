# Project Planning

Interactive project planning session to break down a project into features and create Linear issues.

## Variables

- `project_description`: $1 - Initial project description or goal

## Instructions

### 1. Understand the Project

Start by understanding what the user wants to build:
- Ask clarifying questions about the project scope
- Understand the target users and use cases
- Identify technical constraints or preferences

### 2. Iterative Feature Discovery

Work with the user to identify features:
- Suggest potential features based on the project description
- Ask which features are must-have vs nice-to-have
- Help prioritize features (MVP first, then enhancements)
- Break down large features into smaller, implementable pieces

### 3. Define Each Feature

For each agreed-upon feature, define:
- **Title**: Clear, concise feature name
- **Description**: What it does and why
- **Acceptance Criteria**: How to know it's done
- **Dependencies**: Other features it depends on
- **Priority**: 1 (Urgent), 2 (High), 3 (Medium), 4 (Low)
- **Labels**: feature, bug, chore, enhancement

### 4. Select or Create Linear Project

Before creating issues, associate them with a Linear project:

1. **List existing projects**: Use `mcp__linear__list_projects` to show available projects
2. **Ask user to choose**:
   - Select an existing project from the list
   - Create a new project for this work
3. **If creating new project**:
   - Use `mcp__linear__create_project` with:
     - `name`: Project name
     - `team`: The team name
     - `summary`: Brief description (max 255 chars)
     - `description`: **Full project spec** (see format below) - this is the source of truth
     - `state`: "In Progress" for active projects
4. **Store the project ID** for use when creating issues
5. **After creating issues**: Use `mcp__linear__update_project` to update the description with the Linear issue IDs

Present the options clearly:
```
I found these existing Linear projects:
1. Project A - Description...
2. Project B - Description...

Would you like to:
- Use an existing project (enter number)
- Create a new project for "{Project Name}"
```

### 5. Create Linear Issues

After user confirms the plan and selects/creates a project, create Linear issues:
- Use `mcp__linear__create_issue` MCP tool for each feature
- **IMPORTANT**: Include `project` parameter with the selected/created project ID or name
- Set appropriate priority and labels
- Link dependencies where supported
- Return list of created issue IDs

### 6. Offer Next Steps

Ask the user how to proceed:
- **Run All**: Execute full pipeline for all issues in order
- **Run One**: Start with a specific issue
- **Manual**: Just create issues, user will run manually later

## Project Spec Format

This format is stored in the Linear project's `description` field:

```markdown
# Project: {Project Name}

## Overview
{2-3 paragraph description of the project}

## Target Users
{Who will use this}

## Technical Stack
{Languages, frameworks, etc.}

## Features

### MVP (Must Have)

#### Feature 1: {Title}
- **Issue ID**: {Will be filled after Linear creation}
- **Priority**: {1-4}
- **Description**: {What and why}
- **Acceptance Criteria**:
  - [ ] Criterion 1
  - [ ] Criterion 2
- **Dependencies**: None

#### Feature 2: {Title}
...

### Phase 2 (Nice to Have)

#### Feature 3: {Title}
...

## Dependency Graph

```
Feature 1 (no deps)
    └── Feature 2 (depends on 1)
        └── Feature 4 (depends on 2)
Feature 3 (no deps)
```

## Created Issues

| Feature | Linear ID | Status |
|---------|-----------|--------|
| Feature 1 | LIN-123 | Created |
| Feature 2 | LIN-124 | Created |
```

## Conversation Style

- Be collaborative and conversational
- Ask one or two questions at a time, not a long list
- Summarize understanding before moving to next step
- Offer suggestions but let user have final say
- Keep responses concise but helpful

## Output

After creating issues, return:
```
LINEAR_PROJECT: {project-name} (https://linear.app/...)
ISSUES: LIN-123, LIN-124, LIN-125
READY_TO_RUN: true|false
```
