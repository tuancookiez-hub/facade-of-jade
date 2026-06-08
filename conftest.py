"""Test configuration for Facade of Jade.

Ensures the repository root is on sys.path so plain `pytest` works without
requiring callers to set PYTHONPATH=.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
