"""Run the InterviewIQ session-memory verification."""

import runpy
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
CLASS_SEVEN_PATH = PROJECT_ROOT / "class-7"
sys.path.insert(0, str(CLASS_SEVEN_PATH))

runpy.run_path(
    str(CLASS_SEVEN_PATH / "memory_check.py"),
    run_name="__main__",
)
