import sys
from pathlib import Path

# Ensure the project root and `book_lib` package are importable regardless of CWD
ROOT = Path(__file__).resolve().parent
BOOK_LIB = ROOT / "book_lib"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(BOOK_LIB) not in sys.path:
    sys.path.insert(0, str(BOOK_LIB))
