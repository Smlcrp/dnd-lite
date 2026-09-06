import account
import adventure
import cli


def _inputs(monkeypatch, values):
    it = iter(values)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(it))


def _passwords(monkeypatch, values):
    it = iter(values)
    monkeypatch.setattr(cli.getpass, "getpass", lambda prompt="": next(it))


# ---- tag filter ----

def test_tag_filter_hides_tag_within_single_token():
    f = cli._TagFilter()
    assert f.feed("Before [SCENE: Docks] after") == "Before  after"


def test_tag_filter_hides_tag_split_across_multiple_tokens():
    f = cli._TagFilter()
    out = []
    for chunk in ["Before ", "[SCE", "NE: Doc", "ks] after"]:
        out.append(f.feed(chunk))
    assert "".join(out) == "Before  after"


def test_tag_filter_handles_multiple_tags():
    f = cli._TagFilter()
    out = f.feed("[BEAT]\nYou press onward.\n[CHECK: Perception]\nSomething glints.")
    assert out == "\nYou press onward.\n\nSomething glints."


def test_tag_filter_no_tags_passthrough():
    f = cli._TagFilter()
    assert f.feed("Nothing special happens.") == "Nothing special happens."


# ---- class / level input validation ----

def test_prompt_classes_accepts_valid_single_class(monkeypatch):
    _inputs(monkeypatch, ["Fighter"])
    assert cli._prompt_classes() == ["Fighter"]


def test_prompt_classes_accepts_multiclass_case_insensitive(monkeypatch):
    _inputs(monkeypatch, ["fighter/rogue"])
    assert cli._prompt_classes() == ["Fighter", "Rogue"]


def test_prompt_classes_rejects_invalid_then_accepts(monkeypatch):
    _inputs(monkeypatch, ["Wizardish", "Wizard"])
    assert cli._prompt_classes() == ["Wizard"]


def test_prompt_level_accepts_valid(monkeypatch):
    _inputs(monkeypatch, ["3"])
    assert cli._prompt_level() == 3


def test_prompt_level_rejects_out_of_range_and_non_numeric_then_accepts(monkeypatch):
    _inputs(monkeypatch, ["0", "21", "abc", "5"])
    assert cli._prompt_level() == 5


# ---- login / account creation ----

def test_login_existing_account_correct_password(monkeypatch):
    account.save_account(account.create_account("Sam", "hunter2"))
    _inputs(monkeypatch, ["Sam"])
    _passwords(monkeypatch, ["hunter2"])

    acct = cli._login_or_create_account()
    assert acct["account_name"] == "Sam"


def test_login_wrong_password_then_correct(monkeypatch):
    account.save_account(account.create_account("Sam", "hunter2"))
    _inputs(monkeypatch, ["Sam", "y"])  # account name, then "Try again?" -> yes
    _passwords(monkeypatch, ["wrong", "hunter2"])

    acct = cli._login_or_create_account()
    assert acct["account_name"] == "Sam"


def test_login_creates_new_account_no_default_character(monkeypatch):
    _inputs(monkeypatch, ["Newbie", "y", "n"])  # name, confirm-create, no default character
    _passwords(monkeypatch, ["mypassword", "mypassword"])

    acct = cli._login_or_create_account()
    assert acct["account_name"] == "Newbie"
    assert account.verify_login(acct, "mypassword") is True
    assert acct["default_character"] is None


def test_create_account_password_mismatch_then_match(monkeypatch):
    _inputs(monkeypatch, ["Newbie", "y", "n"])
    _passwords(monkeypatch, ["first", "second", "match", "match"])

    acct = cli._login_or_create_account()
    assert account.verify_login(acct, "match") is True


def test_create_account_with_default_character(monkeypatch):
    _inputs(monkeypatch, ["test", "y", "y", "Adventurer", "Fighter", "3", ""])
    _passwords(monkeypatch, ["test", "test"])

    acct = cli._login_or_create_account()
    assert account.get_default_character(acct) == {
        "name": "Adventurer",
        "classes": ["Fighter"],
        "level": 3,
        "blurb": "",
    }


# ---- new-adventure character collection ----

def test_collect_new_adventure_details_uses_default_character(monkeypatch, capsys):
    a = account.create_account("test", "test")
    account.set_default_character(a, "Adventurer", ["Fighter"], 3, "")

    _inputs(monkeypatch, ["1", "1"])  # tone choice, length choice only

    character_name, classes, level, blurb, tone, preset = cli._collect_new_adventure_details(a)

    assert character_name == "Adventurer"
    assert classes == ["Fighter"]
    assert level == 3
    assert blurb == ""
    assert tone == adventure.TONES[0]
    assert preset == list(adventure.PRESETS.keys())[0]
    assert "Using your saved character" in capsys.readouterr().out


def test_collect_new_adventure_details_without_default_character_asks_level(monkeypatch):
    a = account.create_account("Sam", "hunter2")
    _inputs(monkeypatch, ["Kessa", "Ranger", "4", "cautious but kind", "1", "1"])

    character_name, classes, level, blurb, tone, preset = cli._collect_new_adventure_details(a)

    assert character_name == "Kessa"
    assert classes == ["Ranger"]
    assert level == 4
    assert blurb == "cautious but kind"


# ---- main() orchestration ----

def test_main_handles_ollama_failure_gracefully(monkeypatch, capsys):
    """A cold-start timeout or dropped Ollama server during adventure setup
    should print a friendly message, not crash with a raw traceback -- and
    must never fall through into the main game loop."""
    monkeypatch.setattr(cli, "_login_or_create_account", lambda: account.create_account("Sam", "hunter2"))
    monkeypatch.setattr(cli, "_startup_menu", lambda acct: "new")

    def boom(acct, dungeon_master):
        raise RuntimeError("Could not reach Ollama at http://localhost:11434/api/chat: timed out")

    monkeypatch.setattr(cli, "_start_new_adventure", boom)
    monkeypatch.setattr(
        cli,
        "_main_loop",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("main loop must not run after a setup failure")),
    )

    cli.main()  # must not raise

    out = capsys.readouterr().out
    assert "DM error" in out
    assert "ollama serve" in out


def test_main_passes_explicit_model_override_to_dungeon_master(monkeypatch):
    monkeypatch.setattr(cli, "_login_or_create_account", lambda: account.create_account("Sam", "hunter2"))
    monkeypatch.setattr(cli, "_startup_menu", lambda acct: "quit")

    captured = {}

    class FakeDungeonMaster:
        def __init__(self, model):
            captured["model"] = model

    monkeypatch.setattr(cli.dm, "DungeonMaster", FakeDungeonMaster)

    cli.main(model="qwen2.5:7b")

    assert captured["model"] == "qwen2.5:7b"


def test_main_uses_dungeon_master_default_when_no_model_given(monkeypatch):
    """With no --model override, DungeonMaster() must be constructed with no
    argument at all -- not model=None -- so it falls back to its own default
    (ollama_client.DEFAULT_MODEL) rather than a broken None model string."""
    monkeypatch.setattr(cli, "_login_or_create_account", lambda: account.create_account("Sam", "hunter2"))
    monkeypatch.setattr(cli, "_startup_menu", lambda acct: "quit")

    captured = {"args": "not called"}

    class FakeDungeonMaster:
        def __init__(self, *args):
            captured["args"] = args

    monkeypatch.setattr(cli.dm, "DungeonMaster", FakeDungeonMaster)

    cli.main()

    assert captured["args"] == ()
