"""
Workflow state management for ADW.

Provides persistent JSON-based state that can be read by any session.
Each workflow has its own isolated state file.
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Any
import logging


def generate_workflow_id() -> str:
    """Generate an 8-character workflow ID."""
    return uuid.uuid4().hex[:8]


@dataclass
class WorkflowState:
    """Persistent state for a workflow."""

    workflow_id: str
    issue_id: Optional[str] = None
    issue_title: Optional[str] = None
    issue_description: Optional[str] = None
    issue_type: Optional[str] = None  # feature | bug | chore
    branch_name: Optional[str] = None
    phase: str = "init"  # init | plan | develop | test | review | document | complete
    spec_file: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    phases_completed: List[str] = field(default_factory=list)
    test_results: Optional[dict] = None
    review_results: Optional[dict] = None
    pr_url: Optional[str] = None
    merged: bool = False
    error: Optional[str] = None

    @classmethod
    def create(cls, issue_id: Optional[str] = None) -> "WorkflowState":
        """Create a new workflow state.

        Args:
            issue_id: Optional Linear issue ID

        Returns:
            New WorkflowState instance
        """
        return cls(
            workflow_id=generate_workflow_id(),
            issue_id=issue_id,
        )

    @classmethod
    def load(cls, workflow_id: str, logger: Optional[logging.Logger] = None) -> Optional["WorkflowState"]:
        """Load workflow state from file.

        Args:
            workflow_id: Workflow ID to load
            logger: Optional logger for debug output

        Returns:
            WorkflowState if found, None otherwise
        """
        state_file = get_state_path(workflow_id)

        if not state_file.exists():
            if logger:
                logger.debug(f"No state file found at {state_file}")
            return None

        try:
            with open(state_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if logger:
                logger.debug(f"Loaded state from {state_file}")

            return cls(**data)

        except (json.JSONDecodeError, TypeError) as e:
            if logger:
                logger.error(f"Failed to load state: {e}")
            return None

    def save(self, logger: Optional[logging.Logger] = None) -> Path:
        """Save workflow state to file.

        Args:
            logger: Optional logger for debug output

        Returns:
            Path to saved state file
        """
        self.updated_at = datetime.now().isoformat()
        state_file = get_state_path(self.workflow_id)
        state_file.parent.mkdir(parents=True, exist_ok=True)

        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)

        if logger:
            logger.debug(f"Saved state to {state_file}")

        return state_file

    def update(self, **kwargs: Any) -> "WorkflowState":
        """Update state fields.

        Args:
            **kwargs: Fields to update

        Returns:
            Self for chaining
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        return self

    def mark_phase_complete(self, phase: str) -> "WorkflowState":
        """Mark a phase as completed.

        Args:
            phase: Phase name to mark complete

        Returns:
            Self for chaining
        """
        if phase not in self.phases_completed:
            self.phases_completed.append(phase)

        return self

    def to_dict(self) -> dict:
        """Convert state to dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert state to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


def get_state_path(workflow_id: str) -> Path:
    """Get the path to a workflow's state file.

    Args:
        workflow_id: Workflow ID

    Returns:
        Path to state.json
    """
    return Path(".claude/workflows") / workflow_id / "state.json"


def get_workflow_dir(workflow_id: str) -> Path:
    """Get the directory for a workflow's artifacts.

    Args:
        workflow_id: Workflow ID

    Returns:
        Path to workflow directory
    """
    return Path(".claude/workflows") / workflow_id


def list_workflows() -> List[WorkflowState]:
    """List all workflows with their states.

    Returns:
        List of WorkflowState objects
    """
    workflows_dir = Path(".claude/workflows")

    if not workflows_dir.exists():
        return []

    workflows = []
    for workflow_dir in workflows_dir.iterdir():
        if workflow_dir.is_dir():
            state = WorkflowState.load(workflow_dir.name)
            if state:
                workflows.append(state)

    # Sort by updated_at descending (most recent first)
    workflows.sort(key=lambda w: w.updated_at, reverse=True)

    return workflows


def find_workflow_by_issue(issue_id: str) -> Optional[WorkflowState]:
    """Find a workflow by its Linear issue ID.

    Args:
        issue_id: Linear issue ID (e.g., "LIN-123")

    Returns:
        WorkflowState if found, None otherwise
    """
    for workflow in list_workflows():
        if workflow.issue_id == issue_id:
            return workflow

    return None
