# ADW Bootstrap Setup Script (PowerShell)
# Run this from your project root to install ADW

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Get-Location

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  ADW - AI Developer Workflow" -ForegroundColor Cyan
Write-Host "  Bootstrap Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..."

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host "WARNING: Claude Code CLI not found. Install from https://docs.anthropic.com/en/docs/claude-code" -ForegroundColor Yellow
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "WARNING: uv not found. Install from https://github.com/astral-sh/uv" -ForegroundColor Yellow
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "WARNING: GitHub CLI not found. Install from https://cli.github.com/" -ForegroundColor Yellow
}

try {
    git rev-parse --is-inside-work-tree 2>$null | Out-Null
} catch {
    Write-Host "ERROR: Not inside a git repository. Initialize git first." -ForegroundColor Red
    exit 1
}

Write-Host "Prerequisites check complete."
Write-Host ""

# Copy .claude folder
Write-Host "Installing ADW to .claude/..."

$ClaudeDir = Join-Path $ProjectRoot ".claude"
if (Test-Path $ClaudeDir) {
    Write-Host "WARNING: .claude directory already exists." -ForegroundColor Yellow
    $confirm = Read-Host "Overwrite? (y/N)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "Aborting."
        exit 1
    }
    # Backup existing
    $backupName = ".claude.backup." + (Get-Date -Format "yyyyMMddHHmmss")
    Rename-Item $ClaudeDir $backupName
    Write-Host "Existing .claude backed up to $backupName"
}

Copy-Item -Recurse (Join-Path $ScriptDir ".claude") $ClaudeDir
Write-Host "ADW installed to .claude/"

# Update .gitignore
Write-Host ""
Write-Host "Updating .gitignore..."

$GitignorePath = Join-Path $ProjectRoot ".gitignore"
if (Test-Path $GitignorePath) {
    $content = Get-Content $GitignorePath -Raw
    if ($content -notmatch ".claude/workflows/") {
        Add-Content $GitignorePath "`n# ADW artifacts (workflow state is local)`n.claude/workflows/"
        Write-Host "Added .claude/workflows/ to .gitignore"
    } else {
        Write-Host ".gitignore already configured"
    }
} else {
    Set-Content $GitignorePath "# ADW artifacts (workflow state is local)`n.claude/workflows/"
    Write-Host "Created .gitignore"
}

# Check for pyproject.toml
Write-Host ""
$PyprojectPath = Join-Path $ProjectRoot "pyproject.toml"
if (-not (Test-Path $PyprojectPath)) {
    Write-Host "Creating minimal pyproject.toml for uv..."
    @"
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
"@ | Set-Content $PyprojectPath
    Write-Host "Created pyproject.toml (edit name as needed)"
} else {
    Write-Host "pyproject.toml already exists"
}

# Create settings template
Write-Host ""
$SettingsPath = Join-Path $ClaudeDir "settings.local.json"
if (-not (Test-Path $SettingsPath)) {
    Write-Host "Creating .claude/settings.local.json template..."
    @"
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
      "Bash(npm:*)",
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
"@ | Set-Content $SettingsPath
    Write-Host "Created settings.local.json"
} else {
    Write-Host "settings.local.json already exists"
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Configure Linear MCP (optional) - see README.md"
Write-Host "  2. Run: claude"
Write-Host "  3. Try: /prime to onboard"
Write-Host "  4. Try: /run `"Your feature description`""
Write-Host ""
Write-Host "CLI usage:"
Write-Host "  uv run .claude/adw/cli.py run `"Add feature X`""
Write-Host "  uv run .claude/adw/cli.py project `"Build app Y`""
Write-Host ""
