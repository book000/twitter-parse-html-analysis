"""Tests for the command-line entry point."""

import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "extract_tweets.py"


def test_cli_help_runs_without_pythonpath(tmp_path):
    """The CLI must import `src` without PYTHONPATH and from any directory."""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "--input" in result.stdout
