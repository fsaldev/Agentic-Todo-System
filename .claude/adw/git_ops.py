"""
Git operations for ADW workflows.

Provides branch management, commits, and push operations.
"""

import subprocess
import re
from typing import Tuple, Optional
import logging


def run_git(
    args: list[str],
    logger: Optional[logging.Logger] = None,
    capture_output: bool = True,
) -> Tuple[bool, str]:
    """Run a git command.

    Args:
        args: Git command arguments (without 'git' prefix)
        logger: Optional logger for debug output
        capture_output: Whether to capture stdout/stderr

    Returns:
        Tuple of (success, output/error message)
    """
    cmd = ["git"] + args

    if logger:
        logger.debug(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            output = result.stdout.strip() if result.stdout else ""
            if logger:
                logger.debug(f"Git output: {output[:200]}...")
            return True, output
        else:
            error = result.stderr.strip() if result.stderr else f"Exit code: {result.returncode}"
            if logger:
                logger.error(f"Git error: {error}")
            return False, error

    except Exception as e:
        error = str(e)
        if logger:
            logger.error(f"Git exception: {error}")
        return False, error


def get_current_branch(logger: Optional[logging.Logger] = None) -> Optional[str]:
    """Get the current git branch name.

    Returns:
        Branch name or None if not in a git repo
    """
    success, output = run_git(["branch", "--show-current"], logger)
    return output if success else None


def create_branch(
    branch_name: str,
    logger: Optional[logging.Logger] = None,
) -> Tuple[bool, str]:
    """Create and checkout a new branch from main.

    Args:
        branch_name: Name for the new branch
        logger: Optional logger

    Returns:
        Tuple of (success, message)
    """
    # First, ensure we're on main and up to date
    success, error = run_git(["checkout", "main"], logger)
    if not success:
        # Try master if main doesn't exist
        success, error = run_git(["checkout", "master"], logger)
        if not success:
            return False, f"Failed to checkout main/master: {error}"

    # Pull latest
    success, error = run_git(["pull"], logger)
    if not success:
        if logger:
            logger.warning(f"Failed to pull (continuing anyway): {error}")

    # Create and checkout new branch
    success, error = run_git(["checkout", "-b", branch_name], logger)
    if not success:
        return False, f"Failed to create branch: {error}"

    if logger:
        logger.info(f"Created and checked out branch: {branch_name}")

    return True, branch_name


def checkout_branch(
    branch_name: str,
    logger: Optional[logging.Logger] = None,
) -> Tuple[bool, str]:
    """Checkout an existing branch.

    Args:
        branch_name: Branch to checkout
        logger: Optional logger

    Returns:
        Tuple of (success, message)
    """
    success, error = run_git(["checkout", branch_name], logger)
    if not success:
        return False, f"Failed to checkout branch: {error}"

    if logger:
        logger.info(f"Checked out branch: {branch_name}")

    return True, branch_name


def commit_changes(
    message: str,
    logger: Optional[logging.Logger] = None,
) -> Tuple[bool, str]:
    """Stage all changes and commit.

    Args:
        message: Commit message
        logger: Optional logger

    Returns:
        Tuple of (success, commit hash or error)
    """
    # Stage all changes
    success, error = run_git(["add", "-A"], logger)
    if not success:
        return False, f"Failed to stage changes: {error}"

    # Check if there are changes to commit
    success, output = run_git(["status", "--porcelain"], logger)
    if success and not output:
        if logger:
            logger.info("No changes to commit")
        return True, "No changes to commit"

    # Commit
    success, error = run_git(["commit", "-m", message], logger)
    if not success:
        return False, f"Failed to commit: {error}"

    # Get commit hash
    success, commit_hash = run_git(["rev-parse", "--short", "HEAD"], logger)

    if logger:
        logger.info(f"Committed: {commit_hash} - {message[:50]}...")

    return True, commit_hash


def push_branch(
    branch_name: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
    set_upstream: bool = True,
) -> Tuple[bool, str]:
    """Push branch to remote.

    Args:
        branch_name: Branch to push (defaults to current branch)
        logger: Optional logger
        set_upstream: Whether to set upstream tracking

    Returns:
        Tuple of (success, message)
    """
    if branch_name is None:
        branch_name = get_current_branch(logger)
        if not branch_name:
            return False, "Could not determine current branch"

    args = ["push"]
    if set_upstream:
        args.extend(["-u", "origin", branch_name])
    else:
        args.extend(["origin", branch_name])

    success, error = run_git(args, logger)
    if not success:
        return False, f"Failed to push: {error}"

    if logger:
        logger.info(f"Pushed branch: {branch_name}")

    return True, f"Pushed {branch_name}"


def get_diff_stat(
    base: str = "origin/main",
    logger: Optional[logging.Logger] = None,
) -> str:
    """Get diff statistics against a base branch.

    Args:
        base: Base branch/ref to compare against
        logger: Optional logger

    Returns:
        Diff stat output
    """
    success, output = run_git(["diff", base, "--stat"], logger)
    return output if success else ""


def get_changed_files(
    base: str = "origin/main",
    logger: Optional[logging.Logger] = None,
) -> list[str]:
    """Get list of changed files against a base branch.

    Args:
        base: Base branch/ref to compare against
        logger: Optional logger

    Returns:
        List of changed file paths
    """
    success, output = run_git(["diff", base, "--name-only"], logger)
    if not success:
        return []

    return [f.strip() for f in output.split("\n") if f.strip()]


def generate_branch_name(
    issue_type: str,
    issue_id: str,
    workflow_id: str,
    title: str,
) -> str:
    """Generate a semantic branch name.

    Args:
        issue_type: Type of issue (feature, bug, chore)
        issue_id: Linear issue ID
        workflow_id: ADW workflow ID
        title: Issue title

    Returns:
        Branch name in format: {type}-{issue_id}-{workflow_id}-{slug}
    """
    # Map issue type to branch prefix
    type_map = {
        "feature": "feat",
        "bug": "fix",
        "chore": "chore",
    }
    prefix = type_map.get(issue_type, "feat")

    # Create slug from title
    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", title.lower())
    slug = re.sub(r"\s+", "-", slug)
    slug = slug[:30].strip("-")  # Limit length

    # Clean issue_id (remove any prefix like "LIN-")
    issue_num = re.sub(r"[^0-9]", "", issue_id) or issue_id

    return f"{prefix}-{issue_num}-{workflow_id}-{slug}"


def create_pr(
    title: str,
    body: str,
    base: str = "main",
    logger: Optional[logging.Logger] = None,
) -> Tuple[bool, str]:
    """Create a pull request using GitHub CLI.

    Args:
        title: PR title
        body: PR body/description
        base: Base branch to merge into (default: main)
        logger: Optional logger

    Returns:
        Tuple of (success, PR URL or error message)
    """
    try:
        result = subprocess.run(
            ["gh", "pr", "create", "--title", title, "--body", body, "--base", base],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            pr_url = result.stdout.strip()
            if logger:
                logger.info(f"Created PR: {pr_url}")
            return True, pr_url
        else:
            error = result.stderr.strip() if result.stderr else f"Exit code: {result.returncode}"
            if logger:
                logger.error(f"Failed to create PR: {error}")
            return False, error

    except FileNotFoundError:
        error = "GitHub CLI (gh) not installed. Install from https://cli.github.com/"
        if logger:
            logger.error(error)
        return False, error
    except Exception as e:
        error = str(e)
        if logger:
            logger.error(f"PR creation error: {error}")
        return False, error


def generate_pr_body(
    issue_id: str,
    issue_title: str,
    summary: str,
    changes: list[str],
    linear_url: Optional[str] = None,
) -> str:
    """Generate a standardized PR body.

    Args:
        issue_id: Linear issue ID
        issue_title: Issue title
        summary: Brief summary of changes
        changes: List of changed files
        linear_url: Optional Linear issue URL

    Returns:
        Formatted PR body markdown
    """
    body_lines = [
        "## Summary",
        "",
        summary,
        "",
        "## Changes",
        "",
    ]

    for change in changes[:10]:  # Limit to 10 files
        body_lines.append(f"- `{change}`")

    if len(changes) > 10:
        body_lines.append(f"- ... and {len(changes) - 10} more files")

    body_lines.extend([
        "",
        "## Test plan",
        "",
        "- [ ] Verify changes work as expected",
        "- [ ] Run tests if applicable",
        "",
    ])

    if linear_url:
        body_lines.extend([
            f"**Linear:** [{issue_id}]({linear_url})",
            "",
        ])

    body_lines.append("🤖 Generated with [Claude Code](https://claude.ai/code)")

    return "\n".join(body_lines)


def review_pr(
    pr_url: Optional[str] = None,
    approve: bool = True,
    body: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
) -> Tuple[bool, str]:
    """Review a pull request using GitHub CLI.

    Args:
        pr_url: PR URL or number (defaults to current branch's PR)
        approve: Whether to approve (True) or just comment (False)
        body: Review comment body
        logger: Optional logger

    Returns:
        Tuple of (success, message)
    """
    try:
        args = ["gh", "pr", "review"]

        if pr_url:
            args.append(pr_url)

        if approve:
            args.append("--approve")

        if body:
            args.extend(["--body", body])
        elif approve:
            args.extend(["--body", "Auto-approved by ADW pipeline"])

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            if logger:
                logger.info(f"PR reviewed successfully")
            return True, "PR approved"
        else:
            error = result.stderr.strip() if result.stderr else f"Exit code: {result.returncode}"
            if logger:
                logger.error(f"Failed to review PR: {error}")
            return False, error

    except FileNotFoundError:
        error = "GitHub CLI (gh) not installed"
        if logger:
            logger.error(error)
        return False, error
    except Exception as e:
        error = str(e)
        if logger:
            logger.error(f"PR review error: {error}")
        return False, error


def merge_pr(
    pr_url: Optional[str] = None,
    method: str = "squash",
    delete_branch: bool = True,
    logger: Optional[logging.Logger] = None,
) -> Tuple[bool, str]:
    """Merge a pull request using GitHub CLI.

    Args:
        pr_url: PR URL or number (defaults to current branch's PR)
        method: Merge method - "squash", "merge", or "rebase"
        delete_branch: Whether to delete the branch after merge
        logger: Optional logger

    Returns:
        Tuple of (success, message)
    """
    try:
        args = ["gh", "pr", "merge"]

        if pr_url:
            args.append(pr_url)

        # Add merge method
        if method == "squash":
            args.append("--squash")
        elif method == "rebase":
            args.append("--rebase")
        else:
            args.append("--merge")

        if delete_branch:
            args.append("--delete-branch")

        # Auto-confirm
        args.append("--auto")

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            output = result.stdout.strip() if result.stdout else "PR merged successfully"
            if logger:
                logger.info(f"PR merged: {output}")
            return True, output
        else:
            error = result.stderr.strip() if result.stderr else f"Exit code: {result.returncode}"
            # Check if it's just waiting for checks
            if "auto-merge" in error.lower() or "enabled" in error.lower():
                if logger:
                    logger.info("Auto-merge enabled, waiting for checks")
                return True, "Auto-merge enabled"
            if logger:
                logger.error(f"Failed to merge PR: {error}")
            return False, error

    except FileNotFoundError:
        error = "GitHub CLI (gh) not installed"
        if logger:
            logger.error(error)
        return False, error
    except Exception as e:
        error = str(e)
        if logger:
            logger.error(f"PR merge error: {error}")
        return False, error
