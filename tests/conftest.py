import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest


@pytest.fixture(autouse=True)
def isolate_storage(tmp_path, monkeypatch):
    """Point session/account storage at a per-test tmp dir so tests never
    touch the real sessions/ or accounts/ directories."""
    import session
    import account

    monkeypatch.setattr(session, "SESSIONS_DIR", tmp_path / "sessions")
    monkeypatch.setattr(account, "ACCOUNTS_DIR", tmp_path / "accounts")
    yield
