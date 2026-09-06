"""Terminal game loop for DND Lite."""

import getpass
import re

import account
import adventure
import architect
import dm
import session

CLASSES = [
    "Artificer", "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk",
    "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard",
]
_CLASSES_BY_LOWER = {c.lower(): c for c in CLASSES}


class _TagFilter:
    """Suppresses [TAG: ...] sequences from a live token stream, so the
    player never sees a raw tag flash by while the DM's response is still
    streaming in. dm.respond_stream() only strips tags from the final
    assembled text, not from the individual tokens it yields -- this filter
    covers the gap for anything printed live. One instance per DM turn."""

    def __init__(self):
        self._in_tag = False

    def feed(self, token: str) -> str:
        visible = []
        for ch in token:
            if self._in_tag:
                if ch == "]":
                    self._in_tag = False
                continue
            if ch == "[":
                self._in_tag = True
                continue
            visible.append(ch)
        return "".join(visible)


def _print_streamed_response(dungeon_master: dm.DungeonMaster, s: dict, player_input: str) -> list:
    """Streams a DM turn to the terminal with tags live-filtered out, and
    returns the parsed events from the completed turn."""
    tag_filter = _TagFilter()
    events = []
    for chunk in dungeon_master.respond_stream(s, player_input):
        if "token" in chunk:
            print(tag_filter.feed(chunk["token"]), end="", flush=True)
        elif chunk.get("done"):
            events = chunk["events"]
    print("\n")
    return events


def _prompt(text: str) -> str:
    return input(text).strip()


def _confirm(text: str) -> bool:
    return _prompt(f"{text} [y/N]: ").strip().lower() in ("y", "yes")


def _choose_from_list(options: list, label: str, describe=None) -> str:
    print(f"\nChoose a {label.lower()}:")
    for i, option in enumerate(options, start=1):
        extra = f" -- {describe(option)}" if describe else ""
        print(f"  {i}) {option}{extra}")
    while True:
        choice = _prompt(f"{label} [1-{len(options)}]: ")
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("Please enter a valid number.")


def _prompt_classes() -> list:
    while True:
        raw = _prompt("Class(es) (e.g. 'Fighter' or 'Fighter/Rogue' for multiclass): ")
        parts = [c.strip() for c in re.split(r"[/,]", raw) if c.strip()]
        if not parts:
            print("Please enter at least one class.")
            continue
        resolved = []
        bad = None
        for part in parts:
            canonical = _CLASSES_BY_LOWER.get(part.lower())
            if canonical is None:
                bad = part
                break
            resolved.append(canonical)
        if bad is not None:
            print(f"'{bad}' isn't one of the 13 D&D 5e classes ({', '.join(CLASSES)}). Try again.")
            continue
        return resolved


def _prompt_level() -> int:
    while True:
        raw = _prompt("Starting level (1-20): ")
        if raw.isdigit() and 1 <= int(raw) <= 20:
            return int(raw)
        print("Please enter a number from 1 to 20.")


def _create_account_flow(name: str) -> dict:
    while True:
        password = getpass.getpass("Choose a password: ")
        if not password:
            print("Password cannot be empty.")
            continue
        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            print("Passwords didn't match.")
            continue
        break

    acct = account.create_account(name, password)

    if _confirm("Save a default character for this account, so you skip character setup on every adventure?"):
        character_name = _prompt("Character name: ")
        while not character_name:
            character_name = _prompt("Character name: ")
        classes = _prompt_classes()
        level = _prompt_level()
        blurb = _prompt("Describe your character in a sentence or two: ")
        account.set_default_character(acct, character_name, classes, level, blurb)

    account.save_account(acct)
    print(f"Account '{name}' created.")
    return acct


def _login_or_create_account() -> dict:
    print("DND Lite")
    print("========")
    existing = account.list_accounts()
    if existing:
        print("Existing accounts:", ", ".join(existing))

    while True:
        name = _prompt("Account name: ")
        if not name:
            continue

        try:
            acct = account.load_account(name)
        except FileNotFoundError:
            if _confirm(f"No account named '{name}' -- create one?"):
                return _create_account_flow(name)
            continue

        while True:
            password = getpass.getpass("Password: ")
            if account.verify_login(acct, password):
                return acct
            print("Incorrect password.")
            if not _confirm("Try again?"):
                break


def _startup_menu(acct: dict) -> str:
    entry = account.current_adventure_entry(acct)
    if entry is not None:
        title = entry.get("title", "your adventure")
        started = entry.get("started_at", "an earlier session")
        print(f'\n1) Resume "{title}" (started {started})')
        print("2) Start a new adventure")
        print("3) Quit")
        choice = _prompt("> ")
        if choice == "1":
            return "resume"
        if choice == "2":
            if _confirm(f'This will discard your unfinished adventure "{title}". Continue?'):
                return "new"
            return "quit"
        return "quit"

    print("\n1) New adventure")
    print("2) Quit")
    return "new" if _prompt("> ") == "1" else "quit"


def _collect_new_adventure_details(acct: dict) -> tuple:
    default_character = account.get_default_character(acct)
    if default_character is not None:
        character_name = default_character["name"]
        classes = default_character["classes"]
        level = default_character["level"]
        blurb = default_character["blurb"]
        print(
            f"\nUsing your saved character: {character_name} the "
            f"{'/'.join(classes)} (Level {level})"
        )
    else:
        character_name = _prompt("\nCharacter name: ")
        while not character_name:
            character_name = _prompt("Character name: ")
        classes = _prompt_classes()
        level = _prompt_level()
        blurb = _prompt("Describe your character in a sentence or two: ")

    tone = _choose_from_list(adventure.TONES, "Tone")
    preset = _choose_from_list(
        list(adventure.PRESETS.keys()),
        "Length",
        describe=lambda name: f"{adventure.PRESETS[name]['estimate']} -- {adventure.PRESETS[name]['blurb']}",
    )

    return character_name, classes, level, blurb, tone, preset


def _start_new_adventure(acct: dict, dungeon_master: dm.DungeonMaster) -> dict:
    character_name, classes, level, blurb, tone, preset = _collect_new_adventure_details(acct)

    draft = adventure.draft_outline(tone, acct)
    print("\nThe DM is preparing your adventure...")
    full_adventure = architect.build_adventure(
        draft, character_name, classes, blurb, preset, model=dungeon_master.model
    )

    session.delete_session(acct["account_name"])

    entry = {
        "title": full_adventure["title"],
        "character_name": character_name,
        "classes": classes,
        "level": level,
        "blurb": blurb,
        "tone": tone,
        "setting_archetype": draft["setting_archetype"],
        "antagonist_archetype": draft["antagonist_archetype"],
        "hook_type": draft["hook_type"],
        "twist_type": draft["twist_type"],
        "climax_type": draft["climax_type"],
    }
    account.start_new_adventure(acct, entry)

    s = session.empty_session(acct["account_name"], character_name, classes, level, blurb)
    s["adventure"] = full_adventure
    session.save_session(s)

    print("The DM is warming up...")
    dungeon_master.warmup()

    print()
    _print_streamed_response(dungeon_master, s, dm.BEGIN_ADVENTURE)
    session.save_session(s)
    return s


def _resume_adventure(acct: dict, dungeon_master: dm.DungeonMaster) -> dict:
    s = session.load_active_session(acct["account_name"])
    print("\nPreviously...")
    print(dungeon_master.recap(s))
    print()
    return s


def _maybe_complete_adventure(acct: dict, s: dict, event_types: set) -> None:
    if "climax_reached" in event_types:
        session.set_flag(s, "climax_reached")
    if session.get_flag(s, "climax_reached") and "break_suggested" in event_types:
        account.complete_current_adventure(acct)


def _main_loop(acct: dict, s: dict, dungeon_master: dm.DungeonMaster) -> None:
    print("Type your actions. Commands: 'save', 'quit'.\n")
    while True:
        try:
            player_input = _prompt("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nSaving and exiting...")
            if session.get_flag(s, "climax_reached"):
                account.complete_current_adventure(acct)
            session.save_session(s)
            break

        if not player_input:
            continue

        lower = player_input.lower()
        if lower in ("quit", "exit"):
            if session.get_flag(s, "climax_reached"):
                account.complete_current_adventure(acct)
            session.save_session(s)
            print("Saved. See you next time.")
            break
        if lower == "save":
            session.save_session(s)
            print("(saved)")
            continue

        try:
            events = _print_streamed_response(dungeon_master, s, player_input)
        except RuntimeError as e:
            print(f"\n[DM error: {e}]\n")
            continue

        event_types = {e["type"] for e in events}
        _maybe_complete_adventure(acct, s, event_types)
        session.save_session(s)

        if "break_suggested" in event_types:
            print("(This feels like a good stopping point -- type 'save' or 'quit' when ready.)\n")


def main(model: str = None) -> None:
    acct = _login_or_create_account()
    dungeon_master = dm.DungeonMaster(model) if model else dm.DungeonMaster()
    if model:
        print(f"(using model: {model})")

    action = _startup_menu(acct)
    if action == "quit":
        print("Goodbye.")
        return

    try:
        if action == "new":
            s = _start_new_adventure(acct, dungeon_master)
        else:
            s = _resume_adventure(acct, dungeon_master)
    except RuntimeError as e:
        print(f"\n[DM error: {e}]")
        print("Make sure 'ollama serve' is running (and the model is pulled), then try again.")
        return

    _main_loop(acct, s, dungeon_master)


if __name__ == "__main__":
    main()
