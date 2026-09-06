"""Terminal game loop for DND Lite."""

import re

import adventure
import architect
import dm
import profile
import session


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


def _pick_profile() -> dict:
    print("DND Lite")
    print("========")
    existing = profile.list_profiles()
    if existing:
        print("Existing profiles:", ", ".join(existing))
    name = _prompt("Enter your profile name (new or existing): ")
    while not name:
        name = _prompt("Please enter a name: ")
    try:
        return profile.load_profile(name)
    except FileNotFoundError:
        p = profile.create_profile(name)
        profile.save_profile(p)
        print(f"Created new profile '{name}'.")
        return p


def _startup_menu(prof: dict) -> str:
    entry = profile.current_adventure_entry(prof)
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


def _collect_new_adventure_details() -> tuple:
    character_name = _prompt("\nCharacter name: ")
    while not character_name:
        character_name = _prompt("Character name: ")

    classes_raw = _prompt("Class(es) (e.g. 'Ranger' or 'Ranger/Rogue' for multiclass): ")
    classes = [c.strip() for c in re.split(r"[/,]", classes_raw) if c.strip()] or ["Adventurer"]

    blurb = _prompt("Describe your character in a sentence or two: ")

    tone = _choose_from_list(adventure.TONES, "Tone")
    preset = _choose_from_list(
        list(adventure.PRESETS.keys()),
        "Length",
        describe=lambda name: f"{adventure.PRESETS[name]['estimate']} -- {adventure.PRESETS[name]['blurb']}",
    )

    return character_name, classes, blurb, tone, preset


def _start_new_adventure(prof: dict, dungeon_master: dm.DungeonMaster) -> dict:
    character_name, classes, blurb, tone, preset = _collect_new_adventure_details()

    draft = adventure.draft_outline(tone, prof)
    print("\nThe DM is preparing your adventure...")
    full_adventure = architect.build_adventure(
        draft, character_name, classes, blurb, preset, model=dungeon_master.model
    )

    session.delete_session(prof["profile_name"])

    entry = {
        "title": full_adventure["title"],
        "character_name": character_name,
        "classes": classes,
        "blurb": blurb,
        "tone": tone,
        "setting_archetype": draft["setting_archetype"],
        "antagonist_archetype": draft["antagonist_archetype"],
        "hook_type": draft["hook_type"],
        "twist_type": draft["twist_type"],
        "climax_type": draft["climax_type"],
    }
    profile.start_new_adventure(prof, entry)

    s = session.empty_session(prof["profile_name"], character_name, classes, blurb)
    s["adventure"] = full_adventure
    session.save_session(s)

    print("The DM is warming up...")
    dungeon_master.warmup()

    print()
    _print_streamed_response(dungeon_master, s, dm.BEGIN_ADVENTURE)
    session.save_session(s)
    return s


def _resume_adventure(prof: dict, dungeon_master: dm.DungeonMaster) -> dict:
    s = session.load_active_session(prof["profile_name"])
    print("\nPreviously...")
    print(dungeon_master.recap(s))
    print()
    return s


def _maybe_complete_adventure(prof: dict, s: dict, event_types: set) -> None:
    if "climax_reached" in event_types:
        session.set_flag(s, "climax_reached")
    if session.get_flag(s, "climax_reached") and "break_suggested" in event_types:
        profile.complete_current_adventure(prof)


def _main_loop(prof: dict, s: dict, dungeon_master: dm.DungeonMaster) -> None:
    print("Type your actions. Commands: 'save', 'quit'.\n")
    while True:
        try:
            player_input = _prompt("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nSaving and exiting...")
            if session.get_flag(s, "climax_reached"):
                profile.complete_current_adventure(prof)
            session.save_session(s)
            break

        if not player_input:
            continue

        lower = player_input.lower()
        if lower in ("quit", "exit"):
            if session.get_flag(s, "climax_reached"):
                profile.complete_current_adventure(prof)
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
        _maybe_complete_adventure(prof, s, event_types)
        session.save_session(s)

        if "break_suggested" in event_types:
            print("(This feels like a good stopping point -- type 'save' or 'quit' when ready.)\n")


def main(model: str = None) -> None:
    prof = _pick_profile()
    dungeon_master = dm.DungeonMaster(model) if model else dm.DungeonMaster()
    if model:
        print(f"(using model: {model})")

    action = _startup_menu(prof)
    if action == "quit":
        print("Goodbye.")
        return

    try:
        if action == "new":
            s = _start_new_adventure(prof, dungeon_master)
        else:
            s = _resume_adventure(prof, dungeon_master)
    except RuntimeError as e:
        print(f"\n[DM error: {e}]")
        print("Make sure 'ollama serve' is running (and the model is pulled), then try again.")
        return

    _main_loop(prof, s, dungeon_master)


if __name__ == "__main__":
    main()
