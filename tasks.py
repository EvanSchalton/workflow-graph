from invoke import task, Context

@task
def run(c: Context, port=8080):
    """Run the FastAPI server on a specified port (default: 8080)."""
    c.run(f"uvicorn api.jira.main:app --reload --port {port}", pty=True)

@task
def test(c: Context, verbose: bool = False, log: bool = False, keyword: str | None = None):
    """Run the test suite using pytest."""
    command = "pytest"
    
    if keyword:
        command += f" -k {keyword}"

    if verbose:
        command += " -vv"

    if log:
        command += " > test.log"

    c.run(command, pty=True)

@task
def check(c: Context, log: bool = False):
    """Run mypy to check for type errors."""
    command = "poetry run mypy . --explicit-package-bases"
    if log:
        command += " > mypy.log"
    c.run(command)
