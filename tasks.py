from invoke import task, Context
import sys
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
def test(c: Context, path: str = "", verbose: bool = False, log: bool = False, keyword: str | None = None, coverage: bool = True):
    """
    Run the test suite using pytest with coverage reporting.
    Parameters:
    path: optional, specific path to test files or directories.
    verbose: optional, if True, run pytest in verbose mode.
    log: optional, if True, redirect output to a log file (test.log).
    keyword: optional, run tests matching the specified keyword expression.
    coverage: optional, if True (default), run with coverage reporting.
    """
    # Use python -m pytest to ensure proper module resolution
    command = f"python -m pytest {path}".strip()
    
    if coverage:
        command += " --cov=api --cov-branch --cov-report=term-missing --cov-report=html  --cov-report=xml"
    
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
def coverage(c: Context, path: str = "", html: bool = True, xml: bool = True):
    """
    Run test coverage analysis and generate reports.
    Parameters:
    path: optional, specific path to test files or directories.
    html: optional, if True (default), generate HTML coverage report.
    """
    command = f"python -m pytest {path} --cov=api --cov-branch --cov-report=term-missing".strip()
    
    if html:
        command += " --cov-report=html"
    if xml:
        command += " --cov-report=xml"
    
    c.run(command, pty=True)
    
    if html:
        print("\nHTML coverage report generated in htmlcov/index.html")

@task
def mypy(c: Context, path: str = ".", log: bool = False):
    """
    Run mypy to check for type errors.
    Parameters:
    path: optional, specific path to check (default: current directory).
    log: optional, if True, redirect output to a log file.
    """
    command = f"poetry run mypy {path} --explicit-package-bases"
    if log:
        log_file = "mypy.log"
        if path and path != ".":
            path_safe = path.replace("/", "_").replace(".", "_")
            log_file = f"mypy_{path_safe}.log"
        command += f" > {log_file}"
    c.run(command)

@task
def ruff_check(c: Context, path: str = ".", log: bool = False):
    """
    Run ruff to check for code quality issues.
    Parameters:
    path: optional, specific path to check (default: current directory).
    log: optional, if True, redirect output to a log file.
    """
    command = f"poetry run ruff check {path}"
    if log:
        log_file = "ruff_check.log"
        if path and path != ".":
            path_safe = path.replace("/", "_").replace(".", "_")
            log_file = f"ruff_check_{path_safe}.log"
        command += f" > {log_file}"
    c.run(command)

@task
def ruff_fix(c: Context, path: str = ".", log: bool = False):
    """
    Run ruff to automatically fix code quality issues.
    Parameters:
    path: optional, specific path to fix (default: current directory).
    log: optional, if True, redirect output to a log file.
    """
    command = f"poetry run ruff check {path} --fix"
    if log:
        log_file = "ruff_fix.log"
        if path and path != ".":
            path_safe = path.replace("/", "_").replace(".", "_")
            log_file = f"ruff_fix_{path_safe}.log"
        command += f" > {log_file}"
    c.run(command)

@task
def check(c: Context, path: str = ".", log: bool = False):
    """
    Run all code quality checks (mypy and ruff).
    Parameters:
    path: optional, specific path to check (default: current directory).
    log: optional, if True, redirect output to a log file.
    """
    print(f"Running mypy type checking on {path}...")
    mypy(c, path, log)
    print(f"Running ruff code quality checks on {path}...")
    ruff_check(c, path, log)
    print("All quality checks completed.")
