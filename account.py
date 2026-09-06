"""Persistent player accounts: credentials + play history across many adventures.

Separate from session.py's single active-session slot — an account
accumulates a history entry per adventure (in_progress/completed/abandoned)
so repeat-avoidance (adventure.draft_outline) has something to look at even
across abandoned or long-finished adventures.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import auth

ACCOUNTS_DIR = Path(__file__).parent / "accounts"


def slugify(name: str) -> str:
    slug = re.sub(r"[^\w\-]", "_", name.strip())
    return slug or "account"


def _account_path(account_name: str) -> Path:
    return ACCOUNTS_DIR / f"{slugify(account_name)}.json"


def create_account(account_name: str, password: str) -> dict:
    salt_hex, hash_hex = auth.hash_password(password)
    return {
        "account_name": account_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "password_salt": salt_hex,
        "password_hash": hash_hex,
        "default_character": None,
        "adventures": [],
    }


def verify_login(account: dict, password: str) -> bool:
    return auth.verify_password(password, account["password_salt"], account["password_hash"])


def set_default_character(account: dict, name: str, classes: list, level: int, blurb: str) -> None:
    account["default_character"] = {
        "name": name,
        "classes": list(classes),
        "level": level,
        "blurb": blurb,
    }


def get_default_character(account: dict) -> dict | None:
    return account.get("default_character")


def load_account(account_name: str) -> dict:
    path = _account_path(account_name)
    if not path.exists():
        raise FileNotFoundError(f"No account named {account_name!r}")
    return json.loads(path.read_text())


def save_account(account: dict) -> None:
    ACCOUNTS_DIR.mkdir(parents=True, exist_ok=True)
    _account_path(account["account_name"]).write_text(json.dumps(account, indent=2))


def list_accounts() -> list:
    if not ACCOUNTS_DIR.exists():
        return []
    return sorted(p.stem for p in ACCOUNTS_DIR.glob("*.json"))


def start_new_adventure(account: dict, entry: dict) -> None:
    """Append a new in_progress adventure entry, abandoning any pending one."""
    adventures = account["adventures"]
    if adventures and adventures[-1]["status"] == "in_progress":
        adventures[-1]["status"] = "abandoned"
    new_entry = dict(entry)
    new_entry.setdefault("started_at", datetime.now(timezone.utc).isoformat())
    new_entry["status"] = "in_progress"
    adventures.append(new_entry)
    save_account(account)


def complete_current_adventure(account: dict) -> None:
    entry = current_adventure_entry(account)
    if entry is not None:
        entry["status"] = "completed"
        save_account(account)


def current_adventure_entry(account: dict) -> dict | None:
    adventures = account["adventures"]
    if adventures and adventures[-1]["status"] == "in_progress":
        return adventures[-1]
    return None


def recent_picks(account: dict, field: str, n: int = 5) -> list:
    """Most recent values of `field` across this account's adventure history,
    newest first, for excluding from the next random draw."""
    picks = [a[field] for a in reversed(account["adventures"]) if field in a]
    return picks[:n]
