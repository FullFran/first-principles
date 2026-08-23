import sys
from pathlib import Path

# Each entry in this repo is standalone: it is read, not installed.
sys.path.insert(0, str(Path(__file__).parent))
