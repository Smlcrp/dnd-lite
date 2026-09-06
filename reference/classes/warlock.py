"""Warlock combat-relevant features and Pact Magic slot progression by
level (SRD core class). Pact Magic is structurally different from other
casters -- few slots, all the same (highest available) level, and they
recharge on a SHORT rest rather than a long rest. SPELL_SLOTS still uses
the same {level: {spell_level: count}} shape (just with one spell_level
key per row) so the existing retrieval code needs no special-casing."""

FEATURES = {
    1: ["Otherworldly Patron feature (subclass-specific)", "Pact Magic (few slots, all the same level, recharge on a SHORT rest)"],
    2: ["Eldritch Invocations (choose magical customizations, e.g. Agonizing Blast)"],
    3: ["Pact Boon (a subclass-like choice: Pact of the Blade/Chain/Tome)"],
    6: ["Otherworldly Patron feature"],
    10: ["Otherworldly Patron feature"],
    11: ["Mystic Arcanum (a 6th-level spell, castable once per long rest without a slot)"],
    13: ["Mystic Arcanum (a 7th-level spell)"],
    14: ["Otherworldly Patron feature"],
    15: ["Mystic Arcanum (an 8th-level spell)"],
    17: ["Mystic Arcanum (a 9th-level spell)"],
    20: ["Eldritch Master (regain all Pact Magic slots once per long rest by pleading with your patron)"],
}

RESOURCE_POOLS = {}

CASTER_TYPE = "pact"
SPELL_SLOTS = {
    1: {1: 1},
    2: {1: 2},
    3: {2: 2},
    4: {2: 2},
    5: {3: 2},
    6: {3: 2},
    7: {4: 2},
    8: {4: 2},
    9: {5: 2},
    10: {5: 2},
    11: {5: 3},
    12: {5: 3},
    13: {5: 3},
    14: {5: 3},
    15: {5: 3},
    16: {5: 3},
    17: {5: 4},
    18: {5: 4},
    19: {5: 4},
    20: {5: 4},
}
WEAPON_PROFICIENCIES = ["Simple"]
