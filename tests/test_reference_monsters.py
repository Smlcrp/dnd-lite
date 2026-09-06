import adventure
from reference import monsters


def test_tier_bucketing_matches_level_tier_description_boundaries():
    assert adventure._tier_number(1) == 1
    assert adventure._tier_number(4) == 1
    assert adventure._tier_number(5) == 2
    assert adventure._tier_number(10) == 2
    assert adventure._tier_number(11) == 3
    assert adventure._tier_number(16) == 3
    assert adventure._tier_number(17) == 4
    assert adventure._tier_number(20) == 4


def test_get_monster_archetypes_returns_tier_1_list_for_low_level():
    entries = monsters.get_monster_archetypes(3, None)
    assert len(entries) > 0
    assert all("name" in m for m in entries)


def test_get_monster_archetypes_returns_tier_2_list_for_mid_level():
    # Tier 2-4 were authored in Phase 2 -- must return real entries, not
    # empty (previously Phase 1's example of graceful degradation).
    entries = monsters.get_monster_archetypes(7, None)
    assert len(entries) > 0
    assert all("name" in m for m in entries)


def test_get_monster_archetypes_returns_empty_for_out_of_range_tier(monkeypatch):
    # Structural degradation guard: an unpopulated tier bucket (e.g. if a
    # future tier were added without content yet) must not crash.
    monkeypatch.setitem(monsters.MONSTER_ARCHETYPES, 1, [])
    assert monsters.get_monster_archetypes(3, None) == []


def test_get_monster_archetypes_narrows_by_antagonist_key_when_matched():
    entries = monsters.get_monster_archetypes(3, "cult_leader")
    assert len(entries) > 0
    assert all("cult_leader" in m["antagonist_archetype_keys"] for m in entries)


def test_get_monster_archetypes_falls_back_to_full_tier_when_no_match():
    full_tier = monsters.get_monster_archetypes(3, None)
    no_match = monsters.get_monster_archetypes(3, "nonexistent_key")
    assert no_match == full_tier


def test_build_monster_prompt_block_non_empty_for_tier_2():
    assert monsters.build_monster_prompt_block(7, None) != ""


def test_all_antagonist_archetype_keys_covered_in_every_tier():
    """Regression guard for Phase 4's coverage cross-check: a campaign can
    keep the same antagonist across all 4 tiers, so every key must have at
    least one tagged monster in every tier."""
    all_keys = {key for key, text, tags in adventure.ANTAGONIST_ARCHETYPES}
    for tier, entries in monsters.MONSTER_ARCHETYPES.items():
        covered = set()
        for entry in entries:
            covered.update(entry["antagonist_archetype_keys"])
        assert all_keys <= covered, f"tier {tier} missing keys: {all_keys - covered}"


def test_build_monster_prompt_block_reads_key_from_adventure_dict():
    block = monsters.build_monster_prompt_block(3, {"antagonist_archetype_key": "cult_leader"})
    assert "Cultist" in block
    assert "Bandit Captain" not in block
