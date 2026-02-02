"""
Plan workflow - Creates implementation plans from issues.

This workflow:
1. Creates a new workflow state
2. Creates a feature branch
3. Executes the /plan command to generate a spec
4. Saves the spec file path to state
"""

import sys
from pathlib import Path

# Add parent (adw) directory to path for imports
adw_dir = Path(__file__).parent.parent
if str(adw_dir) not in sys.path:
    sys.path.insert(0, str(adw_dir))

from state import WorkflowState
from logger import create_logger, log_section, log_step, log_success, log_error
from git_ops import create_branch, generate_branch_name, commit_changes, push_branch
from agent import execute_command, check_claude_installed
from linear import LinearIssue


def run_plan(issue: LinearIssue) -> int:
    """Run the plan workflow.

    Args:
        issue: Linear issue or manual issue to plan

    Returns:
        Exit code (0 for success)
    """
    # Create new workflow state
    state = WorkflowState.create(issue_id=issue.identifier)
    state.update(
        issue_title=issue.title,
        issue_description=issue.description,
        issue_type=issue.issue_type,
        phase="plan",
    )

    logger = create_logger(state.workflow_id, "plan")
    log_section(logger, f"PLAN WORKFLOW - {state.workflow_id}")

    logger.info(f"Issue: {issue.identifier} - {issue.title}")
    logger.info(f"Type: {issue.issue_type}")

    # Check Claude is available
    if not check_claude_installed(logger):
        log_error(logger, "Claude Code CLI not available")
        state.update(error="Claude Code CLI not available")
        state.save(logger)
        return 1

    # Step 1: Create branch
    log_step(logger, 1, "Creating feature branch")

    branch_name = generate_branch_name(
        issue_type=issue.issue_type,
        issue_id=issue.identifier,
        workflow_id=state.workflow_id,
        title=issue.title,
    )

    success, error = create_branch(branch_name, logger)
    if not success:
        log_error(logger, f"Failed to create branch: {error}")
        state.update(error=f"Branch creation failed: {error}")
        state.save(logger)
        return 1

    state.update(branch_name=branch_name)
    state.save(logger)
    logger.info(f"Created branch: {branch_name}")

    # Step 2: Execute /plan command
    log_step(logger, 2, "Generating implementation plan")

    # Prepare issue JSON for the command
    issue_json = f'{{"identifier": "{issue.identifier}", "title": "{issue.title}", "description": "{issue.description or ""}", "type": "{issue.issue_type}"}}'

    response = execute_command(
        command="plan",
        args=[issue.identifier, state.workflow_id, issue_json],
        workflow_id=state.workflow_id,
        agent_name="planner",
        logger=logger,
        model="sonnet",
    )

    if not response.success:
        log_error(logger, f"Plan generation failed: {response.error}")
        state.update(error=f"Plan generation failed: {response.error}")
        state.save(logger)
        return 1

    # Extract spec file path from response
    spec_file = response.output.strip()

    # Validate spec file exists
    if not spec_file or not Path(spec_file).exists():
        # Try to find it in the workflow directory
        workflow_spec = Path(f".claude/workflows/{state.workflow_id}/spec.md")
        if workflow_spec.exists():
            spec_file = str(workflow_spec)
        else:
            log_error(logger, "Spec file not created")
            state.update(error="Spec file not created")
            state.save(logger)
            return 1

    state.update(spec_file=spec_file)
    state.save(logger)
    logger.info(f"Spec file created: {spec_file}")

    # Step 3: Commit the plan
    log_step(logger, 3, "Committing plan")

    commit_msg = f"plan({issue.identifier}): create implementation spec\n\nWorkflow: {state.workflow_id}\nSpec: {spec_file}"
    success, result = commit_changes(commit_msg, logger)

    if not success and "No changes" not in result:
        log_error(logger, f"Failed to commit: {result}")
        state.update(error=f"Commit failed: {result}")
        state.save(logger)
        return 1

    # Step 4: Push branch
    log_step(logger, 4, "Pushing branch")

    success, error = push_branch(branch_name, logger)
    if not success:
        logger.warning(f"Failed to push (continuing): {error}")

    # Mark phase complete
    state.mark_phase_complete("plan")
    state.save(logger)

    log_success(logger, f"Plan workflow completed")
    logger.info(f"Workflow ID: {state.workflow_id}")
    logger.info(f"Branch: {branch_name}")
    logger.info(f"Spec: {spec_file}")
    logger.info(f"\nNext: uv run .claude/adw/cli.py develop {state.workflow_id}")

    return 0
