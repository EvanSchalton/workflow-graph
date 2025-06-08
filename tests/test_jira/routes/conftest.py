import pytest
import sys
from pathlib import Path

# Import the fixtures we need from the parent conftest
# NOTE: We don't use pytest_plugins as it's not supported in non-top-level conftest files
# The fixtures from test_jira/conftest.py will be automatically available
