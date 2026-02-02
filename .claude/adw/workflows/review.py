"""
Review workflow - Reviews implementation against spec.

This workflow:
1. Loads workflow state
2. Checks out the correct branch
3. Executes the /review command
4. Parses review results
5. Optionally fixes blocker issues
"""

import sys
import json
from pathlib import Path

# Add parent (adw) directory to path for imports
adw_dir = Path(__file__).parent.parent
if str(adw_dir) not in sys.path:
    sys.path.insert(0, str(adw_dir))

from state import WorkflowState
from logger import create_logger, log_section, log_step, log_success, log_error
from git_ops import checkout_branch, commit_changes, push_branch
from agent import execute_command, check_claude_installed


MAX_FIX_ATTEMPTS = 3


def run_review(state: WorkflowState, fix_blockers: bool = True) -> int:
    """Run the review workflow.

    Args:
        state: Existing workflow state
        fix_blockers: Whether to attempt fixing blocker issues

    Returns:
        Exit code (0 for success)
    """
    logger = create_logger(state.workflow_id, "review")
    log_section(logger, f"REVIEW WORKFLOW - {state.workflow_id}")

    state.update(phase="review")
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

    # Review loop with fix attempts
    attempt = 0
    review_passed = False
    review_results = {}

    while attempt < MAX_FIX_ATTEMPTS and not review_passed:
        attempt += 1

        # Step 2: Execute /review command
        log_step(logger, 2, f"Running review (attempt {attempt}/{MAX_FIX_ATTEMPTS})")

        response = execute_command(
            command="review",
            args=[state.workflow_id, state.spec_file, f"reviewer_{attempt}"],
            workflow_id=state.workflow_id,
            agent_name=f"reviewer_{attempt}",
            logger=logger,
            model="opus",  # Use opus for review
        )

        if not response.success:
            log_error(logger, f"Review execution failed: {response.error}")
            state.update(error=f"Review execution failed: {response.error}")
            state.save(logger)
            return 1

        # Parse review results
        try:
            review_results = json.loads(response.output)
        except json.JSONDecodeError:
            logger.warning("Could not parse review results as JSON")
            review_results = {
                "success": False,
                "review_summary": response.output,
                "review_issues": [],
            }

        review_passed = review_results.get("success", False)
        issues = review_results.get("review_issues", [])

        # Log results
        logger.info(f"Review result: {'PASSED' if review_passed else 'ISSUES FOUND'}")
        logger.info(f"Summary: {review_results.get('review_summary', 'N/A')}")

        if issues:
            blockers = [i for i in issues if i.get("issue_severity") == "blocker"]
            tech_debt = [i for i in issues if i.get("issue_severity") == "tech_debt"]
            skippable = [i for i in issues if i.get("issue_severity") == "skippable"]

            if blockers:
                logger.error(f"Blockers: {len(blockers)}")
                for issue in blockers:
                    logger.error(f"  - {issue.get('issue_description', 'Unknown')}")

            if tech_debt:
                logger.warning(f"Tech debt: {len(tech_debt)}")

            if skippable:
                logger.info(f"Skippable: {len(skippable)}")

        if review_passed:
            break

        # Attempt to fix blockers if enabled
        if fix_blockers and attempt < MAX_FIX_ATTEMPTS and blockers:
            logger.info(f"\nAttempting to fix {len(blockers)} blocker(s)...")

            for issue in blockers:
                fix_response = execute_command(
                    command="patch",
                    args=[
                        state.workflow_id,
                        issue.get("issue_description", ""),
                        state.spec_file,
                        f"fixer_{attempt}",
                    ],
                    workflow_id=state.workflow_id,
                    agent_name=f"review_fixer_{attempt}",
                    logger=logger,
                    model="opus",
                )

                if fix_response.success:
                    logger.info(f"Fix attempted for: {issue.get('issue_description', '')[:50]}")
                else:
                    logger.warning(f"Could not fix issue")

            # Commit fixes
            commit_msg = f"fix({state.issue_id}): address review blockers\n\nWorkflow: {state.workflow_id}"
            commit_changes(commit_msg, logger)

    # Store results
    state.update(review_results={
        "passed": review_passed,
        "attempts": attempt,
        "issues_count": len(review_results.get("review_issues", [])),
        "summary": review_results.get("review_summary", ""),
        "screenshots": review_results.get("screenshots", []),
    })

    # Push any changes
    push_branch(state.branch_name, logger)

    # Mark phase complete
    state.mark_phase_complete("review")
    state.save(logger)

    if review_passed:
        log_success(logger, "Review passed")
        logger.info(f"\nNext: uv run .claude/adw/cli.py document {state.workflow_id}")
        return 0
    else:
        blockers = [i for i in issues if i.get("issue_severity") == "blocker"]
        if blockers:
            log_error(logger, f"Review failed with {len(blockers)} blocker(s)")
            return 1
        else:
            log_success(logger, "Review completed (non-blocking issues only)")
            return 0
