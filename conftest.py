# Pytest configuration to ensure src is on sys.path
import sys
from pathlib import Path

# Add the src directory (containing the `customerinsight` package) to the import path.
repo_root = Path(__file__).resolve().parent
src_path = repo_root / "src"
if src_path.is_dir() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

