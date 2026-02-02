"""
Claude Code CLI integration for ADW.

Provides functions to execute Claude Code with prompts and templates.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass
import logging


# Path to Claude Code CLI (configurable via environment)
CLAUDE_PATH = os.getenv("CLAUDE_CODE_PATH", "claude")


@dataclass
class AgentResponse:
    """Response from a Claude Code execution."""
    success: bool
    output: str
    session_id: Optional[str] = None
    error: Optional[str] = None


def check_claude_installed(logger: Optional[logging.Logger] = None) -> bool:
    """Check if Claude Code CLI is installed and accessible.

    Returns:
        True if Claude Code is available
    """
    try:
        result = subprocess.run(
            [CLAUDE_PATH, "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            if logger:
                logger.debug(f"Claude Code version: {result.stdout.strip()}")
            return True
        return False
    except FileNotFoundError:
        if logger:
            logger.error(f"Claude Code CLI not found at: {CLAUDE_PATH}")
        return False


def execute_prompt(
    prompt: str,
    workflow_id: str,
    agent_name: str,
    logger: Optional[logging.Logger] = None,
    output_dir: Optional[Path] = None,
    model: str = "sonnet",
) -> AgentResponse:
    """Execute a prompt with Claude Code CLI.

    Args:
        prompt: The prompt to execute
        workflow_id: Workflow ID for organizing output
        agent_name: Name of the agent for logging
        logger: Optional logger
        output_dir: Directory for output files
        model: Model to use (sonnet, opus, haiku)

    Returns:
        AgentResponse with results
    """
    if output_dir is None:
        output_dir = Path(".claude/workflows") / workflow_id / agent_name

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "output.jsonl"

    if logger:
        logger.info(f"Executing prompt with Claude Code ({model})")
        logger.debug(f"Prompt: {prompt[:200]}...")

    cmd = [
        CLAUDE_PATH,
        "--print",
        "--output-format", "json",
        "--model", model,
        "-p", prompt,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            cwd=os.getcwd(),
        )

        # Save raw output
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.stdout)

        if result.returncode == 0:
            # Parse output to extract result
            output = parse_claude_output(result.stdout)
            if logger:
                logger.info(f"Claude Code execution completed successfully")
                logger.debug(f"Output: {output[:500]}...")

            return AgentResponse(
                success=True,
                output=output,
            )
        else:
            error = result.stderr.strip() if result.stderr else f"Exit code: {result.returncode}"
            if logger:
                logger.error(f"Claude Code execution failed: {error}")

            return AgentResponse(
                success=False,
                output="",
                error=error,
            )

    except Exception as e:
        if logger:
            logger.error(f"Exception running Claude Code: {e}")

        return AgentResponse(
            success=False,
            output="",
            error=str(e),
        )


def execute_command(
    command: str,
    args: list[str],
    workflow_id: str,
    agent_name: str,
    logger: Optional[logging.Logger] = None,
    model: str = "sonnet",
) -> AgentResponse:
    """Execute a slash command with Claude Code CLI.

    Args:
        command: Command name (without slash)
        args: Arguments for the command
        workflow_id: Workflow ID
        agent_name: Agent name for logging
        logger: Optional logger
        model: Model to use

    Returns:
        AgentResponse with results
    """
    # Build the prompt to execute the command
    args_str = " ".join(args) if args else ""
    prompt = f"/{command} {args_str}".strip()

    if logger:
        logger.info(f"Executing command: {prompt}")

    return execute_prompt(
        prompt=prompt,
        workflow_id=workflow_id,
        agent_name=agent_name,
        logger=logger,
        model=model,
    )


def parse_claude_output(raw_output: str) -> str:
    """Parse Claude Code JSONL output to extract the result.

    Args:
        raw_output: Raw JSONL output from Claude Code

    Returns:
        Extracted text content
    """
    lines = raw_output.strip().split("\n")
    result_parts = []

    for line in lines:
        if not line.strip():
            continue

        try:
            data = json.loads(line)

            # Handle different message types
            if data.get("type") == "result":
                if "result" in data:
                    result_parts.append(data["result"])
            elif data.get("type") == "assistant":
                if "message" in data:
                    # Extract text from content blocks
                    content = data["message"].get("content", [])
                    for block in content:
                        if block.get("type") == "text":
                            result_parts.append(block.get("text", ""))
            elif "content" in data:
                # Direct content
                result_parts.append(str(data["content"]))

        except json.JSONDecodeError:
            # Not JSON, might be plain text
            result_parts.append(line)

    return "\n".join(result_parts).strip()


def get_safe_env() -> dict:
    """Get a safe environment for subprocess execution.

    Returns:
        Filtered environment variables
    """
    safe_vars = [
        "PATH",
        "HOME",
        "USER",
        "SHELL",
        "TERM",
        "LANG",
        "LC_ALL",
        "ANTHROPIC_API_KEY",
        "CLAUDE_CODE_PATH",
        "LINEAR_API_KEY",
        "PYTHONPATH",
    ]

    env = {}
    for var in safe_vars:
        value = os.getenv(var)
        if value:
            env[var] = value

    return env
