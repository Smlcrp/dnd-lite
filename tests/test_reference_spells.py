from reference import spells


def test_get_spells_for_class_returns_empty_for_non_caster():
    assert spells.get_spells_for_class("Fighter", 10) == {}


def test_get_spells_for_class_returns_empty_for_unauthored_class():
    # "Cavalier" isn't one of the 13 D&D classes this app supports.
    assert spells.get_spells_for_class("Cavalier", 10) == {}


def test_get_spells_for_class_returns_empty_when_no_spell_list_authored_yet(monkeypatch):
    # Structural degradation guard: a caster with SPELL_SLOTS but no
    # CLASS_SPELL_LISTS entry yet (a future rollout state) must not crash.
    monkeypatch.setitem(spells.class_lists.CLASS_SPELL_LISTS, "Wizard", {})
    assert spells.get_spells_for_class("Wizard", 10) == {}


def test_get_spells_for_class_never_exceeds_accessible_spell_level():
    # A level-1 Wizard only has 1st-level slots -- must not see 2nd level+.
    result = spells.get_spells_for_class("Wizard", 1)
    assert set(result.keys()) <= {0, 1}


def test_get_spells_for_class_includes_cantrips_and_level_1_at_level_3():
    result = spells.get_spells_for_class("Wizard", 3)
    assert 0 in result
    assert 1 in result
    names = {s["name"] for s in result[1]}
    assert "Magic Missile" in names


def test_half_casters_get_no_spells_at_level_1():
    # Paladin/Ranger's SPELL_SLOTS table starts at level 2 (a real 5e rule) --
    # a level-1 half-caster shouldn't see any spell reference yet.
    assert spells.get_spells_for_class("Paladin", 1) == {}
    assert spells.get_spells_for_class("Ranger", 1) == {}


def test_build_spell_prompt_block_empty_for_no_caster_classes():
    assert spells.build_spell_prompt_block(["Fighter"], 10) == ""


def test_build_spell_prompt_block_only_includes_listed_classes():
    block = spells.build_spell_prompt_block(["Wizard"], 5)
    assert "WIZARD SPELLS" in block
    assert "Magic Missile" in block
