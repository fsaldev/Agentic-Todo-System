"""
Test workflow - Runs test suite.

This workflow:
1. Loads workflow state
2. Checks out the correct branch
3. Executes the /test command
4. Parses and stores test results
5. Optionally attempts to fix failing tests
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


def run_test(state: WorkflowState, fix_failures: bool = True) -> int:
    """Run the test workflow.

    Args:
        state: Existing workflow state
        fix_failures: Whether to attempt fixing failed tests

    Returns:
        Exit code (0 for success)
    """
    logger = create_logger(state.workflow_id, "test")
    log_section(logger, f"TEST WORKFLOW - {state.workflow_id}")

    state.update(phase="test")
    state.save(logger)

    logger.info(f"Issue: {state.issue_id} - {state.issue_title}")

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

    # Test loop with fix attempts
    attempt = 0
    all_passed = False
    test_results = []

    while attempt < MAX_FIX_ATTEMPTS and not all_passed:
        attempt += 1

        # Step 2: Execute /test command
        log_step(logger, 2, f"Running tests (attempt {attempt}/{MAX_FIX_ATTEMPTS})")

        response = execute_command(
            command="test",
            args=[],
            workflow_id=state.workflow_id,
            agent_name=f"tester_{attempt}",
            logger=logger,
            model="sonnet",
        )

        if not response.success:
            log_error(logger, f"Test execution failed: {response.error}")
            state.update(error=f"Test execution failed: {response.error}")
            state.save(logger)
            return 1

        # Parse test results
        try:
            test_results = json.loads(response.output)
        except json.JSONDecodeError:
            logger.warning("Could not parse test results as JSON")
            test_results = [{"test_name": "unknown", "passed": False, "error": response.output}]

        # Count results
        passed = sum(1 for t in test_results if t.get("passed", False))
        failed = len(test_results) - passed

        logger.info(f"Test results: {passed} passed, {failed} failed")

        if failed == 0:
            all_passed = True
            break

        # Log failed tests
        for test in test_results:
            if not test.get("passed", False):
                logger.error(f"FAILED: {test.get('test_name', 'unknown')}")
                if test.get("error"):
                    logger.error(f"  Error: {test['error'][:200]}")

        # Attempt to fix if enabled and not last attempt
        if fix_failures and attempt < MAX_FIX_ATTEMPTS:
            logger.info(f"\nAttempting to fix {failed} failed test(s)...")

            for test in test_results:
                if not test.get("passed", False):
                    fix_response = execute_command(
                        command="resolve_failed_test",
                        args=[json.dumps(test)],
                        workflow_id=state.workflow_id,
                        agent_name=f"fixer_{attempt}",
                        logger=logger,
                        model="sonnet",
                    )

                    if fix_response.success:
                        logger.info(f"Fix attempted for: {test.get('test_name')}")
                    else:
                        logger.warning(f"Could not fix: {test.get('test_name')}")

    # Store results
    state.update(test_results={
        "passed": all_passed,
        "total": len(test_results),
        "failed": sum(1 for t in test_results if not t.get("passed", False)),
        "attempts": attempt,
        "details": test_results,
    })

    # Commit any fixes
    if attempt > 1:
        log_step(logger, 3, "Committing test fixes")
        commit_msg = f"test({state.issue_id}): fix failing tests\n\nWorkflow: {state.workflow_id}"
        commit_changes(commit_msg, logger)
        push_branch(state.branch_name, logger)

    # Mark phase complete
    state.mark_phase_complete("test")
    state.save(logger)

    if all_passed:
        log_success(logger, "All tests passed")
        logger.info(f"\nNext: uv run .claude/adw/cli.py review {state.workflow_id}")
        return 0
    else:
        log_error(logger, f"Tests failed after {attempt} attempts")
        return 1
