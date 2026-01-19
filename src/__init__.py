"""
Centralized path setup for the src package.

This module automatically adds the project root to sys.path when imported,
ensuring all submodules can properly import from the src package.
"""

import sys
from pathlib import Path

# Add project root to sys.path to allow imports from 'src'
# This ensures that all agents can find the 'src.utils' package
PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
