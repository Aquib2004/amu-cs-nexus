# Path bootstrap: make the monorepo root importable from the backend.
#
# The backend imports the `ai` package, which lives at the repository root
# (amu-cs-nexus/ai), not inside backend/. When running the API normally
# (e.g. `uvicorn app.main:app` from backend/), Python does not have that
# directory on sys.path, so `import ai.retrieval` fails. Adding it here
# (once, guarded) ensures the app boots outside pytest. Tests also add it
# via backend/tests/conftest.py; the guard keeps this a no-op for them.

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]  # backend/app -> amu-cs-nexus/


def ensure_repo_root() -> None:
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))


ensure_repo_root()