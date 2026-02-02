# Review

Review implementation against the spec file.

## Variables

- `workflow_id`: $1 - Workflow ID for organizing artifacts
- `spec_path`: $2 - Path to the spec file
- `issue_id`: $3 - (Optional) Linear issue ID for commenting (e.g., "ACA-123")

## Instructions

1. **Check Context**
   - Run `git branch` to see current branch
   - Run `git diff origin/main --stat` to see all changes

2. **Read the Spec**
   - Read the spec file at `spec_path`
   - Understand what was supposed to be built
   - Extract Linear issue ID if present in spec

3. **Compare Implementation**
   - Review the code changes against requirements
   - Check if all Implementation Steps were completed
   - Verify all listed files were modified appropriately

4. **Classify Issues**
   For each issue found, classify as:
   - `blocker`: Must fix before release - breaks functionality
   - `tech_debt`: Should fix later - not ideal but works
   - `skippable`: Minor - informational only

5. **Take Screenshots (if UI changes)**
   - Navigate to the application
   - Capture 1-5 screenshots of key functionality
   - Save to `.claude/workflows/{workflow_id}/screenshots/`

6. **Post Linear Comment (if issue_id provided)**
   Post a comment using `mcp__linear__create_comment`:

   ```markdown
   ## 📋 Review Complete

   **Status:** ✅ Approved / ⚠️ Changes Needed

   ### Acceptance Criteria
   - [x] {criteria 1}
   - [x] {criteria 2}
   - [ ] {criteria 3 - if not met}

   ### Findings
   {List any issues found, or "All requirements met. Implementation matches spec."}

   ### Issues
   | # | Severity | Description |
   |---|----------|-------------|
   | 1 | blocker/tech_debt/skippable | {description} |
   ```

## Output

Return ONLY valid JSON:

```json
{
  "success": true,
  "review_summary": "The feature was implemented correctly. All requirements from the spec are met. The API endpoint works as expected and the frontend displays the data properly.",
  "review_issues": [
    {
      "review_issue_number": 1,
      "issue_description": "Missing error handling for empty response",
      "issue_resolution": "Add try-catch block in fetchData function",
      "issue_severity": "tech_debt"
    }
  ],
  "screenshots": [
    "/absolute/path/to/screenshot1.png",
    "/absolute/path/to/screenshot2.png"
  ],
  "linear_comment_posted": true
}
```

## Success Criteria

- `success: true` if NO blockers found
- `success: false` if ANY blockers found
- Can have tech_debt/skippable issues and still pass

## Rules

- Be thorough but practical
- Focus on functionality, not style preferences
- Only flag real issues, not nitpicks
- Post Linear comment before returning JSON
- Output ONLY the JSON, no other text
