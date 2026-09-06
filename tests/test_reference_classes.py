from reference import classes

# "Cavalier" is not one of the 13 D&D classes this app supports (cli.CLASSES)
# -- used here purely to exercise the "no authored module" code path, since
# all 13 real classes now have one.


def test_get_class_block_returns_none_for_unauthored_class():
    assert classes.get_class_block("Cavalier", 5) is None


def test_get_class_block_respects_headroom_cap():
    block = classes.get_class_block("Fighter", 3, headroom=2)
    assert "through level 5" in block
    assert "Level 5" in block  # within cap
    assert "Level 7" not in block  # beyond cap


def test_get_class_block_includes_resource_pool_at_level():
    block = classes.get_class_block("Fighter", 10)
    assert "action_surge_uses_per_rest: 1" in block


def test_get_class_block_includes_spell_slots_for_caster():
    block = classes.get_class_block("Wizard", 5)
    assert "Spell slots at level 5" in block
    assert "3rd: 2" in block


def test_get_class_block_omits_spell_slots_for_non_caster():
    block = classes.get_class_block("Fighter", 5)
    assert "Spell slots" not in block


def test_build_class_features_prompt_block_only_includes_listed_classes():
    block = classes.build_class_features_prompt_block(["Fighter"], 5)
    assert "FIGHTER" in block
    assert "WIZARD" not in block


def test_build_class_features_prompt_block_skips_unauthored_classes_gracefully():
    block = classes.build_class_features_prompt_block(["Fighter", "Cavalier"], 5)
    assert "FIGHTER" in block
    assert "CAVALIER" not in block


def test_get_weapon_proficiencies_union_across_classes():
    assert classes.get_weapon_proficiencies(["Wizard"]) == {"Simple"}
    assert classes.get_weapon_proficiencies(["Fighter"]) == {"Simple", "Martial"}
    assert classes.get_weapon_proficiencies(["Wizard", "Fighter"]) == {"Simple", "Martial"}


def test_get_weapon_proficiencies_defaults_simple_for_unauthored_class():
    assert classes.get_weapon_proficiencies(["Cavalier"]) == {"Simple"}
