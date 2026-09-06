import pytest

import profile


def _entry(**overrides):
    base = {
        "character_name": "Kessa",
        "classes": ["Ranger"],
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
    p = profile.create_profile("Sam")
    profile.save_profile(p)

    loaded = profile.load_profile("Sam")
    assert loaded["profile_name"] == "Sam"
    assert loaded["adventures"] == []


def test_load_missing_profile_raises():
    with pytest.raises(FileNotFoundError):
        profile.load_profile("Nobody")


def test_list_profiles():
    profile.save_profile(profile.create_profile("Sam"))
    profile.save_profile(profile.create_profile("Alex"))
    assert profile.list_profiles() == ["Alex", "Sam"]


def test_start_new_adventure_appends_in_progress():
    p = profile.create_profile("Sam")
    profile.start_new_adventure(p, _entry())
    assert len(p["adventures"]) == 1
    assert p["adventures"][0]["status"] == "in_progress"


def test_start_new_adventure_abandons_previous():
    p = profile.create_profile("Sam")
    profile.start_new_adventure(p, _entry(character_name="Kessa"))
    profile.start_new_adventure(p, _entry(character_name="Borin"))
    assert p["adventures"][0]["status"] == "abandoned"
    assert p["adventures"][1]["status"] == "in_progress"
    assert p["adventures"][1]["character_name"] == "Borin"


def test_complete_current_adventure():
    p = profile.create_profile("Sam")
    profile.start_new_adventure(p, _entry())
    profile.complete_current_adventure(p)
    assert p["adventures"][0]["status"] == "completed"


def test_complete_current_adventure_noop_when_none_pending():
    p = profile.create_profile("Sam")
    profile.complete_current_adventure(p)  # should not raise
    assert p["adventures"] == []


def test_current_adventure_entry():
    p = profile.create_profile("Sam")
    assert profile.current_adventure_entry(p) is None

    profile.start_new_adventure(p, _entry())
    entry = profile.current_adventure_entry(p)
    assert entry is not None
    assert entry["status"] == "in_progress"

    profile.complete_current_adventure(p)
    assert profile.current_adventure_entry(p) is None


def test_recent_picks_newest_first_and_capped_at_n():
    p = profile.create_profile("Sam")
    profile.start_new_adventure(p, _entry(antagonist_archetype="cult leader"))
    profile.complete_current_adventure(p)
    profile.start_new_adventure(p, _entry(antagonist_archetype="fallen noble"))
    profile.complete_current_adventure(p)
    profile.start_new_adventure(p, _entry(antagonist_archetype="rival mercenary"))

    picks = profile.recent_picks(p, "antagonist_archetype", n=2)
    assert picks == ["rival mercenary", "fallen noble"]


def test_recent_picks_missing_field_skipped():
    p = profile.create_profile("Sam")
    p["adventures"].append({"status": "completed"})  # no antagonist_archetype key
    assert profile.recent_picks(p, "antagonist_archetype") == []
