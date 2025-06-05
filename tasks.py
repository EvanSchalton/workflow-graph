from invoke import task, Context

@task
def run(c: Context, port=8080):
    """Run the FastAPI server on a specified port (default: 8080)."""
    c.run(f"uvicorn api.jira.main:app --reload --port {port}", pty=True)

@task
def test(c: Context, path: str = "", verbose: bool = False, log: bool = False, keyword: str | None = None):
    """Run the test suite using pytest. Optionally specify a path to test specific files/directories."""
    command = f"pytest {path}".strip()
    
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
