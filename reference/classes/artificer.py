"""Artificer combat-relevant features and spell-slot progression by level.
Half caster like Paladin/Ranger, but its slot table starts at level 1
rather than level 2, so it keeps its own inline table rather than sharing
_shared.HALF_CASTER_SPELL_SLOTS. Note: Artificer is a newer, less
universally-memorized class than the core PHB casters -- this progression
is a good-faith reconstruction and more likely than the others here to
need a correction pass."""

FEATURES = {
    1: ["Magical Tinkering (imbue a minor magical effect into a tiny object)", "Spellcasting (Intelligence-based)"],
    2: ["Infuse Item (learn a small, growing number of magic item infusions)"],
    3: ["Artificer Specialist feature (subclass-specific, e.g. Battle Smith's Steel Defender)", "The Right Tool for the Job (craft a set of artisan's tools on a short rest)"],
    5: ["Artificer Specialist feature"],
    6: ["Tool Expertise (double proficiency bonus with chosen tool checks)"],
    7: ["Artificer Specialist feature"],
    10: ["Magic Item Adept (attune to one more magic item, craft uncommon items faster)"],
    11: ["Spell-Storing Item (store a spell in an object for another creature to trigger)"],
    14: ["Magic Item Savant (attune to magic items even if they'd normally be restricted)"],
    15: ["Artificer Specialist feature"],
    18: ["Magic Item Master (attune to up to six magic items)"],
    20: ["Soul of Artifice (+1 to all saving throws per attuned magic item)"],
}

RESOURCE_POOLS = {}

CASTER_TYPE = "half"
SPELL_SLOTS = {
    1: {1: 2},
    2: {1: 2},
    3: {1: 3},
    4: {1: 3},
    5: {1: 4, 2: 2},
    6: {1: 4, 2: 2},
    7: {1: 4, 2: 3},
    8: {1: 4, 2: 3},
    9: {1: 4, 2: 3, 3: 2},
    10: {1: 4, 2: 3, 3: 2},
    11: {1: 4, 2: 3, 3: 3},
    12: {1: 4, 2: 3, 3: 3},
    13: {1: 4, 2: 3, 3: 3, 4: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 2},
    16: {1: 4, 2: 3, 3: 3, 4: 2},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
}
WEAPON_PROFICIENCIES = ["Simple"]
