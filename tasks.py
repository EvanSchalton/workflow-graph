from invoke import task, Context

@task
def run(c: Context, port=8080):
    """Run the FastAPI server on a specified port (default: 8080)."""
    c.run(f"uvicorn app.jira.main:app --reload --port {port}", pty=True)

@task
def test(c: Context, verbose: bool = False):
    """Run the test suite using pytest."""
    command = "pytest"

    if verbose:
        command += " -vv"

    c.run(command, pty=True)

@task
def check(c: Context):
    """Run mypy to check for type errors."""
    c.run("poetry run mypy . --explicit-package-bases")
