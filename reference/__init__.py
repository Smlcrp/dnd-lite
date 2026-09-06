"""Hand-built D&D 5e reference data for the DM's narration precision --
never a rules engine. Every function here returns static lookup text,
filtered to just the player's own class(es)/level/current adventure before
injection -- never the full dataset (that would recreate the exact
context-bloat problem a vector-DB/RAG approach was rejected for). No
arithmetic is ever performed here; nothing computes a derived stat.

Content here is original wording or paraphrased from the D&D 5e SRD (open
under Wizards' OGL/ORC) -- never copied verbatim from the Player's
Handbook, Monster Manual, or DMG.
"""

from . import classes, monsters, spells
from .conditions import conditions_block
from .death_and_dying import DEATH_AND_DYING_BLOCK
from .weapons import weapon_reference_block


def class_features_block(classes_list: list, level: int) -> str:
    return classes.build_class_features_prompt_block(classes_list, level)


def spell_block(classes_list: list, level: int) -> str:
    return spells.build_spell_prompt_block(classes_list, level)


def monster_block(level: int, adventure_dict: dict = None) -> str:
    return monsters.build_monster_prompt_block(level, adventure_dict)


def general_reference_block(classes_list: list) -> str:
    """Weapons (filtered to this class list's actual proficiencies) plus
    conditions and death & dying, which stay small and bounded enough
    (SRD-table-sized) to always include in full."""
    proficiencies = classes.get_weapon_proficiencies(classes_list)
    blocks = [b for b in (weapon_reference_block(proficiencies), conditions_block(), DEATH_AND_DYING_BLOCK) if b]
    return "\n\n".join(blocks)
