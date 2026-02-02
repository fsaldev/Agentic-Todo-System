# Test

Run the application test suite and return structured results.

## Variables

- `issue_id`: $1 - (Optional) Linear issue ID for commenting (e.g., "ACA-123")

## Instructions

1. Execute each test in sequence
2. Collect all results
3. Post results to Linear (if issue_id provided)
4. Return JSON results

## Test Sequence

Run tests appropriate for the project type. Detect and run:

### For Node.js Projects
```bash
npm test
```
Or if no test script, verify the app starts:
```bash
npm start & sleep 3 && curl -s http://localhost:3000/ && kill %1
```

### For Python Projects
```bash
cd app/server && uv run python -m py_compile *.py **/*.py
cd app/server && uv run ruff check .
cd app/server && uv run pytest -v --tb=short
```

### For TypeScript/React Projects
```bash
cd app/client && bun tsc --noEmit
cd app/client && bun run build
```

## Post Linear Comment (if issue_id provided)

After running tests, post a comment using `mcp__linear__create_comment`:

```markdown
## 🧪 Test Results

| Test | Status |
|------|--------|
| {test_name} | ✅ Pass |
| {test_name} | ❌ Fail |

### Summary
- **Passed:** {n}
- **Failed:** {n}

{If failures, include brief error summary}
```

## Output

Return ONLY valid JSON array:

```json
[
  {
    "test_name": "server_start",
    "passed": true,
    "execution_command": "npm start",
    "test_purpose": "Verify server starts correctly"
  },
  {
    "test_name": "health_check",
    "passed": true,
    "execution_command": "curl http://localhost:3000/",
    "test_purpose": "Verify health endpoint responds"
  }
]
```

## Rules

- Execute ALL tests even if some fail
- Sort results with failures first
- Include exact command in `execution_command`
- Truncate errors to 500 chars max
- Post Linear comment before returning JSON
- Output ONLY the JSON array, no other text
