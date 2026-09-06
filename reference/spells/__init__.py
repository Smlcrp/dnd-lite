"""Spell reference data, filtered to the player's own caster class(es) and
the spell levels they can actually access at their current level -- never
the full spell compendium. Canonical spell content lives one file per
spell level (cantrips.py, level1.py, ...) since a spell like Fire Bolt
appears on multiple classes' lists and shouldn't be duplicated per class;
class_lists.py is just a name index used for filtering."""

from ..classes import CLASS_MODULES
from . import (
    cantrips, class_lists, level1, level2, level3, level4, level5, level6,
    level7, level8, level9,
)

ALL_SPELLS = {}
ALL_SPELLS.update(cantrips.SPELLS_CANTRIPS)
ALL_SPELLS.update(level1.SPELLS_LEVEL_1)
ALL_SPELLS.update(level2.SPELLS_LEVEL_2)
ALL_SPELLS.update(level3.SPELLS_LEVEL_3)
ALL_SPELLS.update(level4.SPELLS_LEVEL_4)
ALL_SPELLS.update(level5.SPELLS_LEVEL_5)
ALL_SPELLS.update(level6.SPELLS_LEVEL_6)
ALL_SPELLS.update(level7.SPELLS_LEVEL_7)
ALL_SPELLS.update(level8.SPELLS_LEVEL_8)
ALL_SPELLS.update(level9.SPELLS_LEVEL_9)


def get_spells_for_class(class_name: str, level: int) -> dict:
    """Returns {spell_level: [spell dict, ...]}, restricted to spell levels
    this class can actually cast at `level` (per its SPELL_SLOTS table) and
    to spells actually on its list (class_lists.CLASS_SPELL_LISTS). {} for
    non-casters, unauthored classes, or classes with no spell list authored
    yet."""
    module = CLASS_MODULES.get(class_name)
    if module is None or not module.CASTER_TYPE or not module.SPELL_SLOTS:
        return {}

    applicable = [lvl for lvl in module.SPELL_SLOTS if lvl <= level]
    if not applicable:
        return {}
    max_spell_level = max(module.SPELL_SLOTS[max(applicable)].keys())

    class_list = class_lists.CLASS_SPELL_LISTS.get(class_name, {})
    result = {}
    for spell_level, names in class_list.items():
        if spell_level > max_spell_level:
            continue
        spells = [{"name": name, **ALL_SPELLS[name]} for name in names if name in ALL_SPELLS]
        if spells:
            result[spell_level] = spells
    return result


def build_spell_prompt_block(classes: list, level: int) -> str:
    lines = []
    for class_name in classes:
        spells_by_level = get_spells_for_class(class_name, level)
        if not spells_by_level:
            continue
        lines.append(f"{class_name.upper()} SPELLS (known/preparable at this level):")
        for spell_level in sorted(spells_by_level):
            label = "Cantrip" if spell_level == 0 else f"Level {spell_level}"
            for spell in spells_by_level[spell_level]:
                lines.append(f"  [{label}] {spell['name']}: {spell['description']}")

    if not lines:
        return ""
    header = "SPELL REFERENCE (for narration precision only -- never read a stat block aloud):"
    return "\n".join([header] + lines)
