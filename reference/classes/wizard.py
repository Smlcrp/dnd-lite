"""Wizard combat-relevant features and spell-slot progression by level (SRD
core class). SPELL_SLOTS is structural only (how many slots of what level) --
the actual spell list/effects live in reference/spells/, authored
incrementally (cantrips + level 1 only so far)."""

from ._shared import FULL_CASTER_SPELL_SLOTS

FEATURES = {
    1: [
        "Spellcasting (Intelligence-based)",
        "Arcane Recovery (once per day on a short rest: recover expended "
        "spell slots totaling up to half wizard level, rounded up, none "
        "6th level or higher)",
    ],
    2: ["Arcane Tradition feature (subclass-specific)"],
    6: ["Arcane Tradition feature"],
    10: ["Arcane Tradition feature"],
    14: ["Arcane Tradition feature"],
    18: ["Spell Mastery (cast a chosen 1st- and 2nd-level spell at will without expending a slot)"],
    20: ["Signature Spells (cast two chosen 3rd-level spells once each per short rest without expending a slot)"],
}

RESOURCE_POOLS = {}

CASTER_TYPE = "full"
# Real SRD Wizard proficiency is a specific subset of simple weapons
# (dagger, dart, sling, quarterstaff, light crossbow), not every simple
# weapon -- simplified to the whole "Simple" group here, consistent with
# this module's prompt-scaffolding-not-simulation level of detail.
WEAPON_PROFICIENCIES = ["Simple"]

SPELL_SLOTS = FULL_CASTER_SPELL_SLOTS
