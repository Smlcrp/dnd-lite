import pytest

import account


def _entry(**overrides):
    base = {
        "character_name": "Kessa",
        "classes": ["Ranger"],
        "level": 3,
        "blurb": "cautious but kind",
        "tone": "Horror",
        "setting_archetype": "flooded ruin",
        "antagonist_archetype": "cult leader",
        "hook_type": "stranger begs for help",
        "twist_type": "betrayal",
        "climax_type": "showdown",
    }
    base.update(overrides)
    return base


def test_create_and_save_and_load_round_trip():
    a = account.create_account("Sam", "hunter2")
    account.save_account(a)

    loaded = account.load_account("Sam")
    assert loaded["account_name"] == "Sam"
    assert loaded["adventures"] == []
    assert loaded["default_character"] is None


def test_load_missing_account_raises():
    with pytest.raises(FileNotFoundError):
        account.load_account("Nobody")


def test_list_accounts():
    account.save_account(account.create_account("Sam", "hunter2"))
    account.save_account(account.create_account("Alex", "swordfish"))
    assert account.list_accounts() == ["Alex", "Sam"]


def test_verify_login_correct_and_incorrect_password():
    a = account.create_account("Sam", "hunter2")
    assert account.verify_login(a, "hunter2") is True
    assert account.verify_login(a, "wrong") is False


def test_password_not_stored_in_plaintext():
    a = account.create_account("Sam", "hunter2")
    assert a["password_hash"] != "hunter2"
    assert "hunter2" not in str(a)


def test_set_and_get_default_character():
    a = account.create_account("test", "test")
    assert account.get_default_character(a) is None

    account.set_default_character(a, "Adventurer", ["Fighter"], 3, "")
    default = account.get_default_character(a)
    assert default == {
        "name": "Adventurer",
        "classes": ["Fighter"],
        "level": 3,
        "blurb": "",
    }


def test_start_new_adventure_appends_in_progress():
    a = account.create_account("Sam", "hunter2")
    account.start_new_adventure(a, _entry())
    assert len(a["adventures"]) == 1
    assert a["adventures"][0]["status"] == "in_progress"


def test_start_new_adventure_abandons_previous():
    a = account.create_account("Sam", "hunter2")
    account.start_new_adventure(a, _entry(character_name="Kessa"))
    account.start_new_adventure(a, _entry(character_name="Borin"))
    assert a["adventures"][0]["status"] == "abandoned"
    assert a["adventures"][1]["status"] == "in_progress"
    assert a["adventures"][1]["character_name"] == "Borin"


def test_complete_current_adventure():
    a = account.create_account("Sam", "hunter2")
    account.start_new_adventure(a, _entry())
    account.complete_current_adventure(a)
    assert a["adventures"][0]["status"] == "completed"


def test_complete_current_adventure_noop_when_none_pending():
    a = account.create_account("Sam", "hunter2")
    account.complete_current_adventure(a)  # should not raise
    assert a["adventures"] == []


def test_current_adventure_entry():
    a = account.create_account("Sam", "hunter2")
    assert account.current_adventure_entry(a) is None

    account.start_new_adventure(a, _entry())
    entry = account.current_adventure_entry(a)
    assert entry is not None
    assert entry["status"] == "in_progress"

    account.complete_current_adventure(a)
    assert account.current_adventure_entry(a) is None


def test_recent_picks_newest_first_and_capped_at_n():
    a = account.create_account("Sam", "hunter2")
    account.start_new_adventure(a, _entry(antagonist_archetype="cult leader"))
    account.complete_current_adventure(a)
    account.start_new_adventure(a, _entry(antagonist_archetype="fallen noble"))
    account.complete_current_adventure(a)
    account.start_new_adventure(a, _entry(antagonist_archetype="rival mercenary"))

    picks = account.recent_picks(a, "antagonist_archetype", n=2)
    assert picks == ["rival mercenary", "fallen noble"]


def test_recent_picks_missing_field_skipped():
    a = account.create_account("Sam", "hunter2")
    a["adventures"].append({"status": "completed"})  # no antagonist_archetype key
    assert account.recent_picks(a, "antagonist_archetype") == []
