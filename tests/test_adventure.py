import account
import adventure


def _sample_full_adventure(total_beats=3, current_beat=0, adaptations=None):
    return {
        "title": "The Drowned Crown",
        "tone": "Horror",
        "setting": "a flooded coastal ruin",
        "hook": "A fisherman begs for help finding his missing daughter.",
        "antagonist": {
            "name": "Maren Voss",
            "role": "a cult leader",
            "motivation": "convinced she is the only one who can prevent a catastrophe",
            "plan": "drown the coastal town to appease a slumbering sea-spirit",
        },
        "beats": [f"Act {i} content" for i in range(1, total_beats + 1)],
        "climax": "A confrontation with Maren atop the flooded cathedral spire.",
        "resolution_options": ["The spirit is calmed", "The town is evacuated in time"],
        "adaptations": adaptations or [],
        "total_beats": total_beats,
        "current_beat": current_beat,
    }


def test_draft_outline_has_all_fields():
    outline = adventure.draft_outline("Horror")
    for field in (
        "tone",
        "setting_archetype",
        "antagonist_archetype",
        "antagonist_motivation",
        "hook_type",
        "twist_type",
        "climax_type",
    ):
        assert field in outline
        assert isinstance(outline[field], str)
        assert outline[field]


def test_draft_outline_respects_tone_tags():
    # "Heist" settings should never pull something tagged only Horror-exclusive,
    # i.e. every draw should be a valid Heist-tagged (or untagged/fallback) entry.
    heist_settings = {text for text, tags in adventure.SETTINGS if "Heist" in tags}
    for _ in range(20):
        outline = adventure.draft_outline("Heist")
        assert outline["setting_archetype"] in heist_settings


def test_draft_outline_excludes_recent_picks_when_possible():
    a = account.create_account("Sam", "hunter2")
    # Exhaust all but one Horror-tagged antagonist archetype as "recent".
    horror_archetypes = [text for text, tags in adventure.ANTAGONIST_ARCHETYPES if "Horror" in tags]
    for archetype in horror_archetypes[:-1]:
        account.start_new_adventure(a, {"antagonist_archetype": archetype})
        account.complete_current_adventure(a)

    outline = adventure.draft_outline("Horror", a)
    assert outline["antagonist_archetype"] == horror_archetypes[-1]


def test_draft_outline_falls_back_when_all_recent():
    a = account.create_account("Sam", "hunter2")
    horror_archetypes = [text for text, tags in adventure.ANTAGONIST_ARCHETYPES if "Horror" in tags]
    for archetype in horror_archetypes:
        account.start_new_adventure(a, {"antagonist_archetype": archetype})
        account.complete_current_adventure(a)

    # All Horror-tagged options are "recent" -- must fall back rather than error.
    outline = adventure.draft_outline("Horror", a)
    assert outline["antagonist_archetype"] in horror_archetypes


def test_stage_labels():
    assert adventure.stage_labels(1) == ["Act 1"]
    assert adventure.stage_labels(3) == ["Act 1", "Act 2", "Act 3"]
    assert adventure.stage_labels(5) == ["Act 1", "Act 2", "Act 3", "Act 4", "Act 5"]


def test_advance_beat_caps_at_total():
    adv = _sample_full_adventure(total_beats=3, current_beat=0)
    for _ in range(5):
        adventure.advance_beat(adv)
    assert adv["current_beat"] == 3


def test_apply_adaptation_appends():
    adv = _sample_full_adventure()
    adventure.apply_adaptation(adv, "The party spared the cultists, who now owe them a debt.")
    assert adv["adaptations"] == ["The party spared the cultists, who now owe them a debt."]


def test_prompt_block_hides_climax_language_appropriately():
    adv = _sample_full_adventure(current_beat=0)
    block = adventure.adventure_prompt_block(adv)
    assert "Hook" in block
    assert "CURRENT POSITION: the Hook" in block
    assert "never reveal" in block.lower()


def test_prompt_block_shows_current_act():
    adv = _sample_full_adventure(total_beats=3, current_beat=2)
    block = adventure.adventure_prompt_block(adv)
    assert "CURRENT POSITION: Act 2 of 3" in block


def test_prompt_block_includes_adaptations_when_present():
    adv = _sample_full_adventure(adaptations=["The antagonist now suspects the party."])
    block = adventure.adventure_prompt_block(adv)
    assert "LIVE ADAPTATIONS" in block
    assert "The antagonist now suspects the party." in block


def test_prompt_block_omits_adaptations_section_when_empty():
    adv = _sample_full_adventure(adaptations=[])
    block = adventure.adventure_prompt_block(adv)
    assert "LIVE ADAPTATIONS" not in block


def test_level_tier_description_boundaries():
    assert "Tier 1" in adventure.level_tier_description(1)
    assert "Tier 1" in adventure.level_tier_description(4)
    assert "Tier 2" in adventure.level_tier_description(5)
    assert "Tier 2" in adventure.level_tier_description(10)
    assert "Tier 3" in adventure.level_tier_description(11)
    assert "Tier 3" in adventure.level_tier_description(16)
    assert "Tier 4" in adventure.level_tier_description(17)
    assert "Tier 4" in adventure.level_tier_description(20)


def test_presets_shape():
    for name in ("One Shot", "Quest", "Epic"):
        assert name in adventure.PRESETS
        preset = adventure.PRESETS[name]
        assert isinstance(preset["beats"], int)
        assert preset["estimate"]
        assert preset["blurb"]
