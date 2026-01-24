import sys
from pathlib import Path

# Add project root to sys.path
# This file is in src/agents/path_setup.py, so root is 2 levels up
def resolve_agent_reference(f: str) -> Path:
    PROJECT_ROOT = Path(f).resolve().parents[2]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
