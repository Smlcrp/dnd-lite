import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest


@pytest.fixture(autouse=True)
def isolate_storage(tmp_path, monkeypatch):
    """Point session/profile storage at a per-test tmp dir so tests never
    touch the real sessions/ or profiles/ directories."""
    import session
    import profile

    monkeypatch.setattr(session, "SESSIONS_DIR", tmp_path / "sessions")
    monkeypatch.setattr(profile, "PROFILES_DIR", tmp_path / "profiles")
    yield
