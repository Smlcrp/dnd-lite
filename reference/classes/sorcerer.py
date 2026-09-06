"""Sorcerer combat-relevant features and spell-slot progression by level
(SRD core class). Sorcery points equal sorcerer level from level 2 on -- a
simple formula, described qualitatively rather than enumerated."""

from ._shared import FULL_CASTER_SPELL_SLOTS

FEATURES = {
    1: ["Spellcasting (Charisma-based)", "Sorcerous Origin feature (subclass-specific)"],
    2: ["Font of Magic (sorcery points = sorcerer level; convert points to/from spell slots)"],
    3: ["Metamagic (choose 2 options, e.g. Quickened/Twinned/Empowered Spell)"],
    6: ["Sorcerous Origin feature"],
    10: ["Metamagic (a 3rd option)"],
    14: ["Sorcerous Origin feature"],
    17: ["Metamagic (a 4th option)"],
    18: ["Sorcerous Origin feature"],
    20: ["Sorcerous Restoration (regain 4 sorcery points on a short rest)"],
}

RESOURCE_POOLS = {}

CASTER_TYPE = "full"
SPELL_SLOTS = FULL_CASTER_SPELL_SLOTS
WEAPON_PROFICIENCIES = ["Simple"]
