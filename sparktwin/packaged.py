"""Allow PyInstaller one-folder / one-file distribution by setting resolved asset root."""
from pathlib import Path
import sys

def root():
    return Path(getattr(sys,"_MEIPASS",Path(__file__).resolve().parent.parent))
