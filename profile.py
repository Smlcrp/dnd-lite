"""Persistent player profiles: play history across many adventures.

Separate from session.py's single active-session slot — a profile
accumulates a history entry per adventure (in_progress/completed/abandoned)
so repeat-avoidance (adventure.draft_outline) has something to look at even
across abandoned or long-finished adventures.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

PROFILES_DIR = Path(__file__).parent / "profiles"


def slugify(name: str) -> str:
    slug = re.sub(r"[^\w\-]", "_", name.strip())
    return slug or "profile"


def _profile_path(profile_name: str) -> Path:
    return PROFILES_DIR / f"{slugify(profile_name)}.json"


def create_profile(profile_name: str) -> dict:
    return {
        "profile_name": profile_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "adventures": [],
    }


def load_profile(profile_name: str) -> dict:
    path = _profile_path(profile_name)
    if not path.exists():
        raise FileNotFoundError(f"No profile named {profile_name!r}")
    return json.loads(path.read_text())


def save_profile(profile: dict) -> None:
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    _profile_path(profile["profile_name"]).write_text(json.dumps(profile, indent=2))


def list_profiles() -> list:
    if not PROFILES_DIR.exists():
        return []
    return sorted(p.stem for p in PROFILES_DIR.glob("*.json"))


def start_new_adventure(profile: dict, entry: dict) -> None:
    """Append a new in_progress adventure entry, abandoning any pending one."""
    adventures = profile["adventures"]
    if adventures and adventures[-1]["status"] == "in_progress":
        adventures[-1]["status"] = "abandoned"
    new_entry = dict(entry)
    new_entry.setdefault("started_at", datetime.now(timezone.utc).isoformat())
    new_entry["status"] = "in_progress"
    adventures.append(new_entry)
    save_profile(profile)


def complete_current_adventure(profile: dict) -> None:
    entry = current_adventure_entry(profile)
    if entry is not None:
        entry["status"] = "completed"
        save_profile(profile)


def current_adventure_entry(profile: dict) -> dict | None:
    adventures = profile["adventures"]
    if adventures and adventures[-1]["status"] == "in_progress":
        return adventures[-1]
    return None


def recent_picks(profile: dict, field: str, n: int = 5) -> list:
    """Most recent values of `field` across this profile's adventure history,
    newest first, for excluding from the next random draw."""
    picks = [a[field] for a in reversed(profile["adventures"]) if field in a]
    return picks[:n]
