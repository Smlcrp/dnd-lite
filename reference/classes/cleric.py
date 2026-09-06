"""Cleric combat-relevant features and spell-slot progression by level (SRD
core class). Divine Domain feature levels/effects are subclass-specific and
generalized here."""

from ._shared import FULL_CASTER_SPELL_SLOTS

FEATURES = {
    1: ["Spellcasting (Wisdom-based)", "Divine Domain feature (subclass-specific, e.g. a bonus combat spell or proficiency)"],
    2: ["Channel Divinity (1/rest: a domain-specific effect, e.g. Turn Undead)", "Divine Domain feature"],
    5: ["Destroy Undead (Turn Undead also destroys weak undead outright)"],
    6: ["Channel Divinity (2/rest)", "Divine Domain feature"],
    8: ["Divine Domain feature (often a damage boost to certain attacks)"],
    10: ["Divine Intervention (call on your deity for a miraculous effect, chance of success scales with level)"],
    11: ["Destroy Undead threshold improves"],
    14: ["Destroy Undead threshold improves"],
    17: ["Divine Domain feature"],
    18: ["Channel Divinity (3/rest)"],
    20: ["Divine Intervention (guaranteed success)"],
}

RESOURCE_POOLS = {
    2: {"channel_divinity_uses_per_rest": 1},
    6: {"channel_divinity_uses_per_rest": 2},
    18: {"channel_divinity_uses_per_rest": 3},
}

CASTER_TYPE = "full"
SPELL_SLOTS = FULL_CASTER_SPELL_SLOTS
WEAPON_PROFICIENCIES = ["Simple"]
