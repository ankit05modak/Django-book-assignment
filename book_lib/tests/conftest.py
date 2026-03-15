import os
import sys

# Ensure project app packages are importable (book_lib is sibling to tests/)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BOOK_LIB = os.path.join(ROOT, "book_lib")
if BOOK_LIB not in sys.path:
    sys.path.insert(0, BOOK_LIB)

# DJANGO_SETTINGS_MODULE is set by pytest.ini; pytest-django will configure Django.
