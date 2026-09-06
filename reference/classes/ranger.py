"""Ranger combat-relevant features and spell-slot progression by level (SRD
core class, half caster). Favored Enemy/Natural Explorer are exploration/
utility flavor with no fixed-use resource, so they have no RESOURCE_POOLS
entry."""

from ._shared import HALF_CASTER_SPELL_SLOTS

FEATURES = {
    1: ["Favored Enemy (bonus tracking/knowledge vs. a chosen creature type)", "Natural Explorer (bonus in a chosen favored terrain)"],
    2: ["Fighting Style (a chosen combat specialty)", "Spellcasting (Wisdom-based)"],
    3: ["Ranger Archetype feature (subclass-specific)", "Primeval Awareness (sense nearby creature types of a chosen kind)"],
    5: ["Extra Attack (attack twice whenever you take the Attack action)"],
    6: ["Favored Enemy improves (a second chosen type)", "Natural Explorer improves (a second favored terrain)"],
    7: ["Ranger Archetype feature"],
    8: ["Land's Stride (move through difficult terrain from plants unimpeded)"],
    10: ["Hide in Plain Sight (camouflage bonus while stationary)"],
    11: ["Ranger Archetype feature"],
    14: ["Vanish (can always Hide as a bonus action; can't be tracked non-magically)"],
    15: ["Ranger Archetype feature"],
    18: ["Feral Senses (fight blinded/invisible foes without disadvantage)"],
    20: ["Foe Slayer (add a bonus to one attack or damage roll per turn against a favored enemy)"],
}

RESOURCE_POOLS = {}

CASTER_TYPE = "half"
SPELL_SLOTS = HALF_CASTER_SPELL_SLOTS
WEAPON_PROFICIENCIES = ["Simple", "Martial"]
