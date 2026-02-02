"""
Project workflow - Interactive project planning.

This workflow:
1. Starts an interactive planning session
2. Helps break down project into features
3. Creates Linear issues for each feature
4. Optionally runs the full pipeline for each
"""

import sys
import json
from pathlib import Path
from typing import Optional, List

# Add parent (adw) directory to path for imports
adw_dir = Path(__file__).parent.parent
if str(adw_dir) not in sys.path:
    sys.path.insert(0, str(adw_dir))

from state import WorkflowState, generate_workflow_id
from logger import create_logger
from linear import LinearIssue, create_issue_placeholder
from agent import execute_command


def run_project(description: str, auto_run: bool = False) -> int:
    """Run interactive project planning.

    Args:
        description: Initial project description
        auto_run: Whether to automatically run pipeline after creating issues

    Returns:
        Exit code (0 for success)
    """
    workflow_id = generate_workflow_id()
    logger = create_logger(workflow_id, "project")

    print("\n" + "=" * 60)
    print("  ADW PROJECT PLANNING MODE")
    print("=" * 60)
    print(f"\nWorkflow ID: {workflow_id}")
    print(f"Project: {description[:50]}...")
    print("\nThis is an interactive session. Claude will help you:")
    print("  1. Break down your project into features")
    print("  2. Define acceptance criteria for each")
    print("  3. Create Linear issues")
    print("  4. Optionally run the full pipeline")
    print("\n" + "=" * 60 + "\n")

    logger.info(f"Starting project planning: {description}")

    # Execute the /project command interactively
    # This will be a conversation with the user
    result = execute_command(
        command="project",
        args=[description],
        workflow_id=workflow_id,
        agent_name="project",
        logger=logger,
    )

    if not result.success:
        logger.error(f"Project planning failed: {result.error}")
        return 1

    # Parse output for created issues
    output = result.output
    logger.info(f"Project planning completed")

    # Look for created issues in output
    issues = parse_created_issues(output)

    if issues and auto_run:
        logger.info(f"Auto-running pipeline for {len(issues)} issues")
        return run_pipeline_for_issues(issues, logger)

    return 0


def parse_created_issues(output: str) -> List[str]:
    """Parse created issue IDs from project output.

    Args:
        output: Output from project command

    Returns:
        List of Linear issue IDs
    """
    issues = []

    # Look for ISSUES: line
    for line in output.split("\n"):
        if line.startswith("ISSUES:"):
            # Parse comma-separated issue IDs
            ids_part = line.replace("ISSUES:", "").strip()
            issues = [id.strip() for id in ids_part.split(",") if id.strip()]
            break

    return issues


def run_pipeline_for_issues(issues: List[str], logger) -> int:
    """Run full pipeline for each issue in order.

    Args:
        issues: List of Linear issue IDs
        logger: Logger instance

    Returns:
        Exit code (0 if all succeed)
    """
    from workflows.full import run_full

    print("\n" + "=" * 60)
    print(f"  RUNNING PIPELINE FOR {len(issues)} ISSUES")
    print("=" * 60 + "\n")

    failed = []

    for i, issue_id in enumerate(issues, 1):
        print(f"\n[{i}/{len(issues)}] Processing {issue_id}")
        print("-" * 40)

        issue = create_issue_placeholder(issue_id, logger)
        result = run_full(issue, auto_push=True)

        if result != 0:
            logger.error(f"Pipeline failed for {issue_id}")
            failed.append(issue_id)
            # Continue with next issue instead of stopping
            print(f"WARNING: {issue_id} failed, continuing with next...")
        else:
            logger.info(f"Pipeline completed for {issue_id}")

    # Summary
    print("\n" + "=" * 60)
    print("  PIPELINE SUMMARY")
    print("=" * 60)
    print(f"\nTotal issues: {len(issues)}")
    print(f"Succeeded: {len(issues) - len(failed)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print(f"\nFailed issues: {', '.join(failed)}")
        return 1

    return 0
