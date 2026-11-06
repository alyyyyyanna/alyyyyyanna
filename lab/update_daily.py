"""Refresh today's quote and the activity numbers.

The GitHub workflow runs this once a day. You can run it yourself too.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_profile

if __name__ == "__main__":
    build_profile.refresh_daily()
