"""
Develop workflow - Implements plans.

This workflow:
1. Loads workflow state
2. Checks out the correct branch
3. Executes the /develop command with the spec file
4. Commits the implementation
"""

import sys
from pathlib import Path

# Add parent (adw) directory to path for imports
adw_dir = Path(__file__).parent.parent
if str(adw_dir) not in sys.path:
    sys.path.insert(0, str(adw_dir))

from state import WorkflowState
from logger import create_logger, log_section, log_step, log_success, log_error
from git_ops import checkout_branch, commit_changes, push_branch, get_diff_stat
from agent import execute_command, check_claude_installed


def run_develop(state: WorkflowState) -> int:
    """Run the develop workflow.

    Args:
        state: Existing workflow state

    Returns:
        Exit code (0 for success)
    """
    logger = create_logger(state.workflow_id, "develop")
    log_section(logger, f"DEVELOP WORKFLOW - {state.workflow_id}")

    state.update(phase="develop")
    state.save(logger)

    logger.info(f"Issue: {state.issue_id} - {state.issue_title}")
    logger.info(f"Spec: {state.spec_file}")

    # Validate state
    if not state.spec_file:
        log_error(logger, "No spec file in state. Run plan first.")
        return 1

    if not Path(state.spec_file).exists():
        log_error(logger, f"Spec file not found: {state.spec_file}")
        return 1

    # Check Claude is available
    if not check_claude_installed(logger):
        log_error(logger, "Claude Code CLI not available")
        return 1

    # Step 1: Checkout branch
    log_step(logger, 1, "Checking out branch")

    if state.branch_name:
        success, error = checkout_branch(state.branch_name, logger)
        if not success:
            log_error(logger, f"Failed to checkout branch: {error}")
            return 1
    else:
        logger.warning("No branch in state, using current branch")

    # Step 2: Execute /develop command
    log_step(logger, 2, "Implementing plan")

    response = execute_command(
        command="develop",
        args=[state.spec_file],
        workflow_id=state.workflow_id,
        agent_name="developer",
        logger=logger,
        model="opus",  # Use opus for implementation
    )

    if not response.success:
        log_error(logger, f"Implementation failed: {response.error}")
        state.update(error=f"Implementation failed: {response.error}")
        state.save(logger)
        return 1

    logger.info("Implementation completed")
    logger.debug(f"Output: {response.output[:500]}...")

    # Step 3: Show diff stats
    log_step(logger, 3, "Reviewing changes")

    diff_stat = get_diff_stat(logger=logger)
    if diff_stat:
        logger.info(f"Changes:\n{diff_stat}")
    else:
        logger.warning("No changes detected")

    # Step 4: Commit changes
    log_step(logger, 4, "Committing implementation")

    issue_prefix = state.issue_type or "feat"
    if issue_prefix == "bug":
        issue_prefix = "fix"
    elif issue_prefix == "feature":
        issue_prefix = "feat"

    commit_msg = f"{issue_prefix}({state.issue_id}): implement {state.issue_title[:50]}\n\nWorkflow: {state.workflow_id}"
    success, result = commit_changes(commit_msg, logger)

    if not success and "No changes" not in result:
        log_error(logger, f"Failed to commit: {result}")
        state.update(error=f"Commit failed: {result}")
        state.save(logger)
        return 1

    # Step 5: Push
    log_step(logger, 5, "Pushing changes")

    success, error = push_branch(state.branch_name, logger)
    if not success:
        logger.warning(f"Failed to push (continuing): {error}")

    # Mark phase complete
    state.mark_phase_complete("develop")
    state.save(logger)

    log_success(logger, "Develop workflow completed")
    logger.info(f"\nNext: uv run .claude/adw/cli.py test {state.workflow_id}")

    return 0
