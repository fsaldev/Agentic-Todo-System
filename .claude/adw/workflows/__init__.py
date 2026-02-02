"""
ADW Workflow modules.

Each workflow module handles a specific phase of the development lifecycle.
"""

import sys
from pathlib import Path

# Add parent (adw) directory to path for imports
adw_dir = Path(__file__).parent.parent
if str(adw_dir) not in sys.path:
    sys.path.insert(0, str(adw_dir))

from workflows.plan import run_plan
from workflows.develop import run_develop
from workflows.test import run_test
from workflows.review import run_review
from workflows.full import run_full
from workflows.project import run_project

__all__ = [
    "run_plan",
    "run_develop",
    "run_test",
    "run_review",
    "run_full",
    "run_project",
]
