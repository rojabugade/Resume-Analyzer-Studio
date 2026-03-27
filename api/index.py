from __future__ import annotations

import sys
from pathlib import Path

# Ensure src-layout packages are importable in Vercel serverless runtime.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ai_agent_system.main import app

