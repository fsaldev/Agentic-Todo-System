"""
Linear integration for ADW.

Uses Linear MCP server for fetching issues. Claude Code calls MCP tools
directly during workflow execution.

This module provides utilities for issue ID handling and manual issue creation.
"""

import re
from dataclasses import dataclass
from typing import Optional, List
import logging


@dataclass
class LinearIssue:
    """Represents a Linear issue."""
    id: str
    identifier: str  # e.g., "LIN-123"
    title: str
    description: Optional[str]
    state: str  # e.g., "In Progress", "Todo"
    priority: int  # 0-4, 0 is no priority, 1 is urgent
    labels: List[str]
    url: str

    @property
    def issue_type(self) -> str:
        """Determine issue type from labels.

        Returns:
            'bug', 'feature', or 'chore'
        """
        labels_lower = [l.lower() for l in self.labels]

        if any("bug" in l for l in labels_lower):
            return "bug"
        elif any("feature" in l or "enhancement" in l for l in labels_lower):
            return "feature"
        elif any("chore" in l or "maintenance" in l for l in labels_lower):
            return "chore"
        else:
            # Default to feature if no matching label
            return "feature"


def is_linear_issue_id(text: str) -> bool:
    """Check if text looks like a Linear issue ID.

    Args:
        text: Text to check

    Returns:
        True if it looks like a Linear issue ID (e.g., "LIN-123", "ABC-45")
    """
    return bool(re.match(r"^[A-Z]+-\d+$", text.upper()))


def parse_issue_id(text: str) -> str:
    """Parse and normalize a Linear issue ID.

    Args:
        text: Issue ID text (e.g., "lin-123", "LIN-123", "123")

    Returns:
        Normalized issue ID (uppercase)
    """
    text = text.strip().upper()
    return text


def create_issue_from_text(
    text: str,
    logger: Optional[logging.Logger] = None,
) -> LinearIssue:
    """Create a pseudo-issue from plain text (for manual input).

    Args:
        text: Issue description text
        logger: Optional logger

    Returns:
        LinearIssue with text as title/description
    """
    # Try to extract a title from the first line
    lines = text.strip().split("\n")
    title = lines[0][:100] if lines else "Manual task"
    description = "\n".join(lines[1:]).strip() if len(lines) > 1 else text

    if logger:
        logger.info(f"Created manual issue: {title[:50]}...")

    return LinearIssue(
        id="manual",
        identifier="MANUAL-0",
        title=title,
        description=description,
        state="Todo",
        priority=2,
        labels=[],
        url="",
    )


def create_issue_placeholder(
    issue_id: str,
    logger: Optional[logging.Logger] = None,
) -> LinearIssue:
    """Create a placeholder issue for Linear MCP workflow.

    The actual issue details will be fetched by Claude via MCP
    during the /plan command execution.

    Args:
        issue_id: Linear issue ID (e.g., "LIN-123")
        logger: Optional logger

    Returns:
        LinearIssue placeholder with ID set
    """
    if logger:
        logger.info(f"Created placeholder for Linear issue: {issue_id}")
        logger.info("Issue details will be fetched via Linear MCP during planning")

    return LinearIssue(
        id=issue_id,
        identifier=issue_id.upper(),
        title=f"[Fetched via MCP: {issue_id}]",
        description=None,
        state="Unknown",
        priority=0,
        labels=[],
        url="",
    )
