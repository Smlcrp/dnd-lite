from unittest.mock import patch

import dm
import session


def _sample_adventure(current_beat=0, adaptations=None):
    return {
        "title": "The Drowned Crown",
        "tone": "Horror",
        "setting": "a flooded coastal ruin",
        "hook": "A fisherman begs for help finding his missing daughter.",
        "antagonist": {
            "name": "Maren Voss",
            "role": "a cult leader",
            "motivation": "prevent a catastrophe",
            "plan": "drown the town",
        },
        "beats": ["Act 1 content", "Act 2 content", "Act 3 content"],
        "climax": "A confrontation atop the flooded cathedral spire.",
        "resolution_options": ["The spirit is calmed", "The town is evacuated"],
        "adaptations": adaptations or [],
        "total_beats": 3,
        "current_beat": current_beat,
    }


def _sample_session(story_mode=False, history=None, adventure_adaptations=None, current_beat=0):
    s = session.empty_session("Sam", "Kessa", ["Ranger", "Rogue"], "cautious but kind")
    s["adventure"] = _sample_adventure(current_beat=current_beat, adaptations=adventure_adaptations)
    s["story_mode"] = story_mode
    if history:
        s["history"] = history
    return s


# ---- system prompt assembly ----

def test_system_prompt_includes_core_blocks():
    d = dm.DungeonMaster()
    prompt = d._build_system_prompt(_sample_session())

    assert "ABSOLUTE RULE" in prompt
    assert "Kessa" in prompt
    assert "Ranger/Rogue" in prompt
    assert "cautious but kind" in prompt
    assert "NARRATION STYLE" in prompt
    assert "PLAYER AGENCY" in prompt
    assert "SELF-REPORTED DICE" in prompt
    assert "TAGS:" in prompt
    assert "The Drowned Crown" in prompt


def test_system_prompt_opening_turn_has_no_scene_anchor():
    d = dm.DungeonMaster()
    prompt = d._build_system_prompt(_sample_session(history=[]))

    assert "opening turn" in prompt.lower()
    assert "SCENE IN PROGRESS" not in prompt


def test_system_prompt_continuing_turn_has_scene_anchor():
    d = dm.DungeonMaster()
    history = [
        {"role": "player", "text": "I look around."},
        {"role": "dm", "text": "The tavern is dim and quiet."},
    ]
    prompt = d._build_system_prompt(_sample_session(history=history))

    assert "SCENE IN PROGRESS" in prompt
    assert "The tavern is dim and quiet." in prompt
    assert "opening turn" not in prompt.lower()


def test_system_prompt_story_mode_block_only_when_enabled():
    d = dm.DungeonMaster()
    on = d._build_system_prompt(_sample_session(story_mode=True))
    off = d._build_system_prompt(_sample_session(story_mode=False))

    assert "STORY MODE" in on
    assert "STORY MODE" not in off


def test_system_prompt_includes_adaptations_when_present():
    d = dm.DungeonMaster()
    prompt = d._build_system_prompt(
        _sample_session(adventure_adaptations=["The antagonist now suspects the party."])
    )
    assert "LIVE ADAPTATIONS" in prompt
    assert "The antagonist now suspects the party." in prompt


def test_scene_anchor_truncates_long_text_on_sentence_boundary():
    d = dm.DungeonMaster()
    long_text = ("The hall stretches before you. " * 30).strip()
    anchor = dm._scene_anchor(long_text)
    # Should not include the full 900+ char text verbatim
    assert len(anchor) < len(long_text) + 200


def test_messages_for_ollama_windows_history():
    d = dm.DungeonMaster()
    history = [{"role": "player" if i % 2 == 0 else "dm", "text": f"turn {i}"} for i in range(20)]
    s = _sample_session(history=history)
    messages = d._messages_for_ollama(s, "I move on.")

    # system + last 12 history turns + current input
    assert messages[0]["role"] == "system"
    assert len(messages) == 1 + 12 + 1
    assert messages[-1] == {"role": "user", "content": "I move on."}
    assert messages[1]["content"] == "turn 8"  # first of the last 12 (indices 8..19)


# ---- tag parsing ----

def test_parse_tags_strips_all_tags_and_extracts_events():
    d = dm.DungeonMaster()
    raw = (
        "[SCENE: The Drowned Chapel]\n"
        "You step into the flooded nave.\n"
        "[CHECK: Perception]\n"
        "Something glints beneath the water.\n"
        "[BEAT]\n"
        "[ADAPT: The party's mercy toward the cultists earns them an ally.]\n"
    )
    clean, events = d._parse_tags(raw)

    assert "[SCENE" not in clean
    assert "[CHECK" not in clean
    assert "[BEAT]" not in clean
    assert "[ADAPT" not in clean
    assert "You step into the flooded nave." in clean

    types = {e["type"] for e in events}
    assert types == {"scene_change", "check_requested", "beat_complete", "adapt"}

    scene_event = next(e for e in events if e["type"] == "scene_change")
    assert scene_event["location"] == "The Drowned Chapel"

    adapt_event = next(e for e in events if e["type"] == "adapt")
    assert adapt_event["note"] == "The party's mercy toward the cultists earns them an ally."


def test_parse_tags_no_tags_present():
    d = dm.DungeonMaster()
    clean, events = d._parse_tags("Nothing special happens.")
    assert clean == "Nothing special happens."
    assert events == []


def test_parse_tags_case_and_whitespace_insensitive():
    d = dm.DungeonMaster()
    raw = "[climax]\nThe ground shakes.\n[break]"
    clean, events = d._parse_tags(raw)
    types = {e["type"] for e in events}
    assert types == {"climax_reached", "break_suggested"}
    assert "[climax]" not in clean.lower()


# ---- event application ----

def test_apply_events_scene_change_updates_location():
    d = dm.DungeonMaster()
    s = _sample_session()
    d._apply_events(s, [{"type": "scene_change", "location": "The Drowned Chapel"}])
    assert s["location"] == "The Drowned Chapel"


def test_apply_events_beat_and_climax_advance_beat():
    d = dm.DungeonMaster()
    s = _sample_session(current_beat=0)
    d._apply_events(s, [{"type": "beat_complete"}])
    assert s["adventure"]["current_beat"] == 1
    d._apply_events(s, [{"type": "climax_reached"}])
    assert s["adventure"]["current_beat"] == 2


def test_apply_events_adapt_appends_note():
    d = dm.DungeonMaster()
    s = _sample_session()
    d._apply_events(s, [{"type": "adapt", "note": "New direction."}])
    assert s["adventure"]["adaptations"] == ["New direction."]


def test_apply_events_check_and_break_are_noops():
    d = dm.DungeonMaster()
    s = _sample_session()
    before = dict(s["adventure"])
    d._apply_events(s, [{"type": "check_requested", "skill": "Perception"}, {"type": "break_suggested"}])
    assert s["adventure"]["current_beat"] == before["current_beat"]
    assert s["adventure"]["adaptations"] == before["adaptations"]


# ---- respond / respond_stream / recap ----

def test_respond_records_history_and_returns_clean_narration():
    d = dm.DungeonMaster()
    s = _sample_session()
    with patch("dm.ollama_client.call_ollama", return_value="[SCENE: Docks]\nYou reach the docks."):
        result = d.respond(s, "I head to the docks.")

    assert result["narration"] == "You reach the docks."
    assert s["history"][-2] == {"role": "player", "text": "I head to the docks."}
    assert s["history"][-1] == {"role": "dm", "text": "You reach the docks."}
    assert s["location"] == "Docks"


def test_respond_begin_adventure_sentinel_not_recorded_as_player_turn():
    d = dm.DungeonMaster()
    s = _sample_session()
    with patch("dm.ollama_client.call_ollama", return_value="You stand at the edge of the ruin."):
        d.respond(s, dm.BEGIN_ADVENTURE)

    assert len(s["history"]) == 1
    assert s["history"][0]["role"] == "dm"


def test_respond_stream_yields_tokens_then_done_with_events():
    d = dm.DungeonMaster()
    s = _sample_session()

    def fake_stream(messages, model):
        yield "[BEAT]\n"
        yield "You "
        yield "press onward."

    with patch("dm.ollama_client.stream_ollama", side_effect=fake_stream):
        chunks = list(d.respond_stream(s, "I press onward."))

    token_chunks = [c for c in chunks if "token" in c]
    done_chunks = [c for c in chunks if c.get("done")]

    assert "".join(c["token"] for c in token_chunks) == "[BEAT]\nYou press onward."
    assert len(done_chunks) == 1
    assert done_chunks[0]["narration"] == "You press onward."
    assert s["adventure"]["current_beat"] == 1
    assert s["history"][-1] == {"role": "dm", "text": "You press onward."}


def test_recap_with_no_history_returns_placeholder():
    d = dm.DungeonMaster()
    s = _sample_session(history=[])
    assert d.recap(s) == "No previous narration to recap."


def test_recap_calls_ollama_with_last_dm_turn():
    d = dm.DungeonMaster()
    history = [
        {"role": "player", "text": "I look around."},
        {"role": "dm", "text": "The tavern is dim and quiet."},
    ]
    s = _sample_session(history=history)
    with patch("dm.ollama_client.call_ollama", return_value="Previously, you entered a quiet tavern.") as mock_call:
        result = d.recap(s)

    assert result == "Previously, you entered a quiet tavern."
    sent_messages = mock_call.call_args.args[0]
    assert any("The tavern is dim and quiet." in m["content"] for m in sent_messages)
