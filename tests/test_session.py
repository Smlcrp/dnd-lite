import session


def _sample_session():
    return session.empty_session("Sam", "Kessa", ["Ranger", "Rogue"], 3, "cautious but kind")


def test_empty_session_shape():
    s = _sample_session()
    assert s["account_name"] == "Sam"
    assert s["character_name"] == "Kessa"
    assert s["classes"] == ["Ranger", "Rogue"]
    assert s["level"] == 3
    assert s["history"] == []
    assert s["flags"] == {}
    assert s["adventure"] is None
    assert s["story_mode"] is False


def test_save_and_load_round_trip():
    s = _sample_session()
    session.add_history(s, "dm", "You arrive at a tavern.")
    session.save_session(s)

    loaded = session.load_active_session("Sam")
    assert loaded is not None
    assert loaded["character_name"] == "Kessa"
    assert loaded["level"] == 3
    assert loaded["history"] == [{"role": "dm", "text": "You arrive at a tavern."}]


def test_no_active_session_returns_none():
    assert session.load_active_session("Nobody") is None
    assert session.has_active_session("Nobody") is False


def test_has_active_session_true_after_save():
    session.save_session(_sample_session())
    assert session.has_active_session("Sam") is True


def test_replace_on_new_adventure_leaves_exactly_one_file():
    session.save_session(_sample_session())
    assert session.has_active_session("Sam") is True

    session.delete_session("Sam")
    assert session.has_active_session("Sam") is False

    s2 = session.empty_session("Sam", "Borin", ["Fighter"], 1, "gruff but loyal")
    session.save_session(s2)

    loaded = session.load_active_session("Sam")
    assert loaded["character_name"] == "Borin"

    files = list(session.SESSIONS_DIR.glob("*.json"))
    assert len(files) == 1


def test_flags():
    s = _sample_session()
    assert session.get_flag(s, "met_wizard") is False
    session.set_flag(s, "met_wizard")
    assert session.get_flag(s, "met_wizard") is True
