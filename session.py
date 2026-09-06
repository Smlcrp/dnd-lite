"""Per-adventure session persistence.

Only one unfinished adventure can exist per profile at a time, so storage is
a single file per profile rather than a list of named saves.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

SESSIONS_DIR = Path(__file__).parent / "sessions"


def _slugify(name: str) -> str:
    slug = re.sub(r"[^\w\-]", "_", name.strip())
    return slug or "profile"


def session_path(profile_name: str) -> Path:
    return SESSIONS_DIR / f"{_slugify(profile_name)}.json"


def empty_session(profile_name: str, character_name: str, classes: list, blurb: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "profile_name": profile_name,
        "character_name": character_name,
        "classes": list(classes),
        "blurb": blurb,
        "location": "",
        "scene": "",
        "history": [],
        "flags": {},
        "adventure": None,
        "story_mode": False,
        "created_at": now,
        "updated_at": now,
    }


def save_session(session: dict) -> None:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    session["updated_at"] = datetime.now(timezone.utc).isoformat()
    session_path(session["profile_name"]).write_text(json.dumps(session, indent=2))


def load_active_session(profile_name: str) -> dict | None:
    path = session_path(profile_name)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def has_active_session(profile_name: str) -> bool:
    return session_path(profile_name).exists()


def delete_session(profile_name: str) -> None:
    path = session_path(profile_name)
    if path.exists():
        path.unlink()


def add_history(session: dict, role: str, text: str) -> None:
    session["history"].append({"role": role, "text": text})


def set_flag(session: dict, key: str, value=True) -> None:
    session["flags"][key] = value


def get_flag(session: dict, key: str, default=False):
    return session["flags"].get(key, default)
