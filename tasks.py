from invoke import task, Context
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path if it's not already there
workspace_dir = Path(__file__).parent
if str(workspace_dir) not in sys.path:
    sys.path.insert(0, str(workspace_dir))

@task
def run(c: Context, port=8080):
    """Run the FastAPI server on a specified port (default: 8080)."""
    c.run(f"uvicorn api.jira.main:app --reload --port {port}", pty=True)

@task
def test(c: Context, path: str = "", verbose: bool = False, log: bool = False, keyword: str | None = None):
    """
    Run the test suite using pytest.
    Parameters:
    path: optional, specific path to test files or directories.
    verbose: optional, if True, run pytest in verbose mode.
    log: optional, if True, redirect output to a log file (test.log).
    keyword: optional, run tests matching the specified keyword expression.
    """
    # Use python -m pytest to ensure proper module resolution
    command = f"python -m pytest {path}".strip()
    
    if keyword:
        command += f" -k {keyword}"

    if verbose:
        command += " -vv"

    if log:
        log_file = "test.log"
        if path:
            # Create a more specific log filename based on the path
            path_safe = path.replace("/", "_").replace(".", "_")
            log_file = f"test_{path_safe}.log"
        command += f" > {log_file}"

    c.run(command, pty=True)

@task
def check(c: Context, log: bool = False):
    """Run mypy to check for type errors."""
    command = "poetry run mypy . --explicit-package-bases"
    if log:
        command += " > mypy.log"
    c.run(command)
