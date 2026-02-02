#!/bin/bash
# ADW Bootstrap Setup Script
# Run this from your project root to install ADW

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(pwd)"

echo "=================================="
echo "  ADW - AI Developer Workflow"
echo "  Bootstrap Setup"
echo "=================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v claude &> /dev/null; then
    echo "WARNING: Claude Code CLI not found. Install from https://docs.anthropic.com/en/docs/claude-code"
fi

if ! command -v uv &> /dev/null; then
    echo "WARNING: uv not found. Install from https://github.com/astral-sh/uv"
fi

if ! command -v gh &> /dev/null; then
    echo "WARNING: GitHub CLI not found. Install from https://cli.github.com/"
fi

if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo "ERROR: Not inside a git repository. Initialize git first."
    exit 1
fi

echo "Prerequisites check complete."
echo ""

# Copy .claude folder
echo "Installing ADW to .claude/..."

if [ -d "$PROJECT_ROOT/.claude" ]; then
    echo "WARNING: .claude directory already exists."
    read -p "Overwrite? (y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Aborting."
        exit 1
    fi
    # Backup existing
    mv "$PROJECT_ROOT/.claude" "$PROJECT_ROOT/.claude.backup.$(date +%s)"
    echo "Existing .claude backed up."
fi

cp -r "$SCRIPT_DIR/.claude" "$PROJECT_ROOT/.claude"
echo "ADW installed to .claude/"

# Update .gitignore
echo ""
echo "Updating .gitignore..."

if [ -f "$PROJECT_ROOT/.gitignore" ]; then
    if ! grep -q ".claude/workflows/" "$PROJECT_ROOT/.gitignore"; then
        echo "" >> "$PROJECT_ROOT/.gitignore"
        echo "# ADW artifacts (workflow state is local)" >> "$PROJECT_ROOT/.gitignore"
        echo ".claude/workflows/" >> "$PROJECT_ROOT/.gitignore"
        echo "Added .claude/workflows/ to .gitignore"
    else
        echo ".gitignore already configured"
    fi
else
    echo "# ADW artifacts (workflow state is local)" > "$PROJECT_ROOT/.gitignore"
    echo ".claude/workflows/" >> "$PROJECT_ROOT/.gitignore"
    echo "Created .gitignore"
fi

# Check for pyproject.toml
echo ""
if [ ! -f "$PROJECT_ROOT/pyproject.toml" ]; then
    echo "Creating minimal pyproject.toml for uv..."
    cat > "$PROJECT_ROOT/pyproject.toml" << 'EOF'
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
EOF
    echo "Created pyproject.toml (edit name as needed)"
else
    echo "pyproject.toml already exists"
fi

# Create settings template
echo ""
if [ ! -f "$PROJECT_ROOT/.claude/settings.local.json" ]; then
    echo "Creating .claude/settings.local.json template..."
    cat > "$PROJECT_ROOT/.claude/settings.local.json" << 'EOF'
{
  "permissions": {
    "allow": [
      "Bash(git status:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git push:*)",
      "Bash(git checkout:*)",
      "Bash(git branch:*)",
      "Bash(git log:*)",
      "Bash(git diff:*)",
      "Bash(gh pr create:*)",
      "Bash(gh pr merge:*)",
      "Bash(gh pr review:*)",
      "Bash(uv run:*)",
      "mcp__linear__list_projects",
      "mcp__linear__get_project",
      "mcp__linear__create_project",
      "mcp__linear__update_project",
      "mcp__linear__list_issues",
      "mcp__linear__get_issue",
      "mcp__linear__create_issue",
      "mcp__linear__update_issue",
      "Edit",
      "Write"
    ]
  }
}
EOF
    echo "Created settings.local.json"
else
    echo "settings.local.json already exists"
fi

echo ""
echo "=================================="
echo "  Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Configure Linear MCP (optional) - see README.md"
echo "  2. Run: claude"
echo "  3. Try: /prime to onboard"
echo "  4. Try: /run \"Your feature description\""
echo ""
echo "CLI usage:"
echo "  uv run .claude/adw/cli.py run \"Add feature X\""
echo "  uv run .claude/adw/cli.py project \"Build app Y\""
echo ""
