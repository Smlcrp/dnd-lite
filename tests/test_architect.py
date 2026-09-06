from unittest.mock import patch

import architect


def _draft():
    return {
        "tone": "Horror",
        "setting_archetype": "a flooded coastal ruin",
        "antagonist_archetype": "a cult leader promising false salvation",
        "antagonist_motivation": "convinced they are the only one who can prevent a catastrophe",
        "hook_type": "a stranger begs the party for help in a crowded public place",
        "twist_type": "someone the party trusted is working against them",
        "climax_type": "a direct confrontation with the antagonist at their seat of power",
    }


def _valid_json_response(n_beats=3):
    return (
        '{"title": "The Drowned Crown", "tone": "Horror", '
        '"setting": "a flooded coastal ruin", '
        '"hook": "A fisherman begs for help.", '
        '"antagonist": {"name": "Maren Voss", "role": "cult leader", '
        '"motivation": "prevent a catastrophe", "plan": "drown the town"}, '
        f'"beats": {[f"Act {i}" for i in range(1, n_beats + 1)]!r}, '
        '"climax": "confrontation at the spire", '
        '"resolution_options": ["spirit calmed", "town evacuated"]}'
    ).replace("'", '"')


def test_build_adventure_parses_valid_json_on_first_try():
    with patch("architect.ollama_client.call_ollama", return_value=_valid_json_response(3)) as mock_call:
        result = architect.build_adventure(_draft(), "Kessa", ["Ranger"], 3, "cautious but kind", "Quest")

    assert mock_call.call_count == 1
    assert result["title"] == "The Drowned Crown"
    assert result["antagonist"]["name"] == "Maren Voss"
    assert len(result["beats"]) == 3
    assert result["total_beats"] == 3
    assert result["current_beat"] == 0
    assert result["adaptations"] == []


def test_build_adventure_strips_markdown_fences():
    fenced = "```json\n" + _valid_json_response(1) + "\n```"
    with patch("architect.ollama_client.call_ollama", return_value=fenced):
        result = architect.build_adventure(_draft(), "Borin", ["Fighter"], 3, "gruff", "One Shot")

    assert result["title"] == "The Drowned Crown"
    assert result["total_beats"] == 1


def test_build_adventure_retries_once_on_invalid_json_then_succeeds():
    responses = ["not json at all", _valid_json_response(3)]

    with patch("architect.ollama_client.call_ollama", side_effect=responses) as mock_call:
        result = architect.build_adventure(_draft(), "Kessa", ["Ranger"], 3, "cautious", "Quest")

    assert mock_call.call_count == 2
    assert result["title"] == "The Drowned Crown"


def test_build_adventure_falls_back_after_two_failures():
    with patch("architect.ollama_client.call_ollama", side_effect=["garbage one", "garbage two"]) as mock_call:
        result = architect.build_adventure(_draft(), "Kessa", ["Ranger"], 3, "cautious", "Quest")

    assert mock_call.call_count == 2
    # Fallback path -- deterministic, always produces a usable, valid shape.
    assert result["setting"] == "a flooded coastal ruin"
    assert len(result["beats"]) == 3
    assert result["total_beats"] == 3
    assert result["current_beat"] == 0
    assert "name" in result["antagonist"]
    assert len(result["resolution_options"]) >= 1


def test_beats_padded_when_model_returns_too_few():
    short_beats_json = _valid_json_response(1)  # only 1 beat, but preset needs 3
    with patch("architect.ollama_client.call_ollama", return_value=short_beats_json):
        result = architect.build_adventure(_draft(), "Kessa", ["Ranger"], 3, "cautious", "Quest")

    assert len(result["beats"]) == 3


def test_beats_truncated_when_model_returns_too_many():
    long_beats_json = _valid_json_response(5)  # 5 beats, but preset needs 1
    with patch("architect.ollama_client.call_ollama", return_value=long_beats_json):
        result = architect.build_adventure(_draft(), "Kessa", ["Ranger"], 3, "cautious", "One Shot")

    assert len(result["beats"]) == 1


def test_parse_adventure_json_rejects_missing_antagonist_fields():
    bad = '{"title": "T", "tone": "Horror", "setting": "S", "hook": "H", ' \
          '"antagonist": {"name": "N"}, "beats": ["b1"], "climax": "C", ' \
          '"resolution_options": ["R"]}'
    assert architect._parse_adventure_json(bad, 1) is None


def test_parse_adventure_json_rejects_non_dict():
    assert architect._parse_adventure_json("[1, 2, 3]", 1) is None


def test_build_adventure_passes_explicit_model_through():
    with patch("architect.ollama_client.call_ollama", return_value=_valid_json_response(3)) as mock_call:
        architect.build_adventure(
            _draft(), "Kessa", ["Ranger"], 3, "cautious", "Quest", model="llama3.2:1b"
        )
    assert mock_call.call_args.args[1] == "llama3.2:1b"


def test_build_adventure_defaults_to_ollama_client_default_model():
    with patch("architect.ollama_client.call_ollama", return_value=_valid_json_response(3)) as mock_call:
        architect.build_adventure(_draft(), "Kessa", ["Ranger"], 3, "cautious", "Quest")
    assert mock_call.call_args.args[1] == architect.ollama_client.DEFAULT_MODEL


def test_build_messages_includes_level_and_encounter_scaling_guidance():
    messages = architect._build_messages(_draft(), "Kessa", ["Ranger"], 12, "cautious", n_beats=3)
    system_content = messages[0]["content"]
    user_content = messages[1]["content"]

    assert "ENCOUNTER SCALING" in system_content
    assert "Tier 3" in system_content  # level 12 -> "Masters of the Realm" (11-16)
    assert "level 12" in user_content


def test_build_messages_reflects_correct_tier_per_level():
    tier1 = architect._build_messages(_draft(), "Kessa", ["Ranger"], 1, "cautious", n_beats=1)
    tier2 = architect._build_messages(_draft(), "Kessa", ["Ranger"], 7, "cautious", n_beats=1)
    tier3 = architect._build_messages(_draft(), "Kessa", ["Ranger"], 12, "cautious", n_beats=1)
    tier4 = architect._build_messages(_draft(), "Kessa", ["Ranger"], 19, "cautious", n_beats=1)

    assert "Tier 1" in tier1[0]["content"]
    assert "Tier 2" in tier2[0]["content"]
    assert "Tier 3" in tier3[0]["content"]
    assert "Tier 4" in tier4[0]["content"]
    assert "level 1 " in tier1[1]["content"]
    assert "level 19 " in tier4[1]["content"]
