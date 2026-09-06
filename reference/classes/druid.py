"""Druid combat-relevant features and spell-slot progression by level (SRD
core class). Wild Shape's exact CR/form limits loosen at 4/8 but are
narrative texture here, not a mechanical table this app enforces."""

from ._shared import FULL_CASTER_SPELL_SLOTS

FEATURES = {
    1: ["Spellcasting (Wisdom-based)", "Druidic (secret druidic language)"],
    2: ["Wild Shape (2/rest: transform into a beast form for a time)", "Druid Circle feature (subclass-specific)"],
    4: ["Wild Shape (higher-CR/more capable forms allowed)"],
    6: ["Druid Circle feature"],
    8: ["Wild Shape (higher-CR/more capable forms allowed again)"],
    10: ["Druid Circle feature"],
    14: ["Druid Circle feature"],
    18: ["Timeless Body (ages very slowly)", "Beast Spells (can cast most spells while Wild Shaped)"],
    20: ["Archdruid (unlimited Wild Shape uses)"],
}

RESOURCE_POOLS = {
    2: {"wild_shape_uses_per_rest": 2},
    20: {"wild_shape_uses_per_rest": "unlimited"},
}

CASTER_TYPE = "full"
SPELL_SLOTS = FULL_CASTER_SPELL_SLOTS
WEAPON_PROFICIENCIES = ["Simple"]
