# Makes the app directory a Python package.
"""Application package initialization.

Set this before PyTorch, NumPy, or Transformers import their native libraries.
On Windows, those packages can otherwise load duplicate Intel OpenMP runtimes
and abort the Uvicorn worker during startup.
"""

import os

if os.name == "nt":
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
