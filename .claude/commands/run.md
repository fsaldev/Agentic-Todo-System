# Zero-Touch Development

Automatically plan, develop, test, review, and deploy a feature with no manual intervention.

## Variables

- `feature`: $1 - Feature description or Linear issue ID (e.g., "Add dark mode" or "LIN-123")

## Instructions

Execute the complete development pipeline automatically.

### If Linear Issue

If `feature` looks like a Linear issue ID (e.g., "LIN-123", "ACA-42"):
1. Fetch issue details using `mcp__linear__get_issue`
2. Store the issue ID for commenting throughout the pipeline
3. Use issue title and description for planning

### Pipeline Phases

Execute each phase and post Linear comments to document progress:

#### 1. PLAN
- Create implementation specification
- Create feature branch: `feat-{issue-id}-{slug}`
- Generate spec file: `.claude/workflows/{id}/spec.md`
- **Linear Comment**: Post planning summary with spec overview

#### 2. DEVELOP
- Implement the feature following the spec
- **Linear Comment**: Post when starting with approach summary
- **Linear Comment**: Post when complete with files changed

#### 3. TEST
- Run tests with auto-fix (up to 3 retries)
- **Linear Comment**: Post test results (pass/fail counts)

#### 4. REVIEW
- Review implementation against spec
- Fix any blockers found
- **Linear Comment**: Post review summary with any issues found

#### 5. DEPLOY
- Commit changes with conventional commit message
- Push branch to remote
- Create pull request
- Auto-approve the PR
- Auto-merge the PR (squash merge, delete branch)
- **Linear Comment**: Post final summary with branch name, PR link, and merge status

### Linear Comment Templates

Use `mcp__linear__create_comment` with these formats:

**DEVELOP Start:**
```markdown
## 🚀 Development Started

**Branch:** `{branch_name}`

### Approach
{brief summary of implementation approach}
```

**DEVELOP Complete:**
```markdown
## ✅ Development Complete

### Files Changed
{list of files modified}

### Summary
{what was implemented}
```

**TEST Results:**
```markdown
## 🧪 Test Results

| Test | Status |
|------|--------|
| {test_name} | ✅ Pass / ❌ Fail |

{error details if any failures}
```

**REVIEW Summary:**
```markdown
## 📋 Review Complete

**Status:** {Approved / Changes Needed}

### Findings
{list any issues or confirm all requirements met}
```

**DEPLOY Complete:**
```markdown
## 🚢 Deployed & Merged

**Branch:** `{branch_name}`
**Commit:** `{commit_hash}`
**PR:** {github_pr_link}
**Status:** Merged ✅ / Pending review

{merge_status_details}
```

### On Completion

1. Update Linear issue status to "Done" using `mcp__linear__update_issue`
2. Report summary:

```
WORKFLOW_ID: {id}
BRANCH: {branch_name}
STATUS: deployed
REMOTE: pushed
PR: {pr_url}
MERGED: yes/no
LINEAR: {issue_id} → Done (with {n} comments)
```

The feature has been deployed and merged to main.
