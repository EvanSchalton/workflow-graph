#!/usr/bin/env python3

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")

try:
    from api.jira.routes.dependencies.get_session import get_session
    print("✓ get_session imported successfully")
except Exception as e:
    print(f"✗ get_session import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from api.jira.models import Board, StatusColumn, Ticket, TicketComment, Webhook
    print("✓ models imported successfully")
except Exception as e:
    print(f"✗ models import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from api.jira.routes import boards
    print("✓ boards route imported successfully")
except Exception as e:
    print(f"✗ boards route import failed: {e}")
    import traceback
    traceback.print_exc()

print("Import test complete")
