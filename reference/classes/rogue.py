"""Rogue combat-relevant features by level (SRD core class). Sneak Attack
is a once-per-turn bonus damage die that scales with level -- folded into
FEATURES as a die-size note rather than RESOURCE_POOLS, since it isn't a
limited-use resource."""

FEATURES = {
    1: ["Expertise (double proficiency bonus on two skills)", "Sneak Attack (1d6 extra damage once per turn, with advantage or an ally adjacent to the target)", "Thieves' Cant (secret rogue code/language)"],
    2: ["Cunning Action (Dash, Disengage, or Hide as a bonus action)"],
    3: ["Roguish Archetype feature (subclass-specific)", "Sneak Attack improves to 2d6"],
    5: ["Uncanny Dodge (halve damage from one attack that hits you, as a reaction)", "Sneak Attack improves to 3d6"],
    6: ["Expertise (two more skills)"],
    7: ["Evasion (no damage on a successful Dexterity save vs. an area effect)", "Sneak Attack improves to 4d6"],
    9: ["Roguish Archetype feature", "Sneak Attack improves to 5d6"],
    11: ["Reliable Talent (treat a d20 roll below 10 as a 10 on proficient checks)", "Sneak Attack improves to 6d6"],
    13: ["Roguish Archetype feature", "Sneak Attack improves to 7d6"],
    14: ["Blindsense (aware of nearby unseen creatures within 10 feet)"],
    15: ["Slippery Mind (proficiency in Wisdom saving throws)", "Sneak Attack improves to 8d6"],
    17: ["Roguish Archetype feature", "Sneak Attack improves to 9d6"],
    18: ["Elusive (no attack roll has advantage against you while not incapacitated)"],
    19: ["Sneak Attack improves to 10d6"],
    20: ["Stroke of Luck (turn a failed attack/check into a success once per rest)"],
}

RESOURCE_POOLS = {}

CASTER_TYPE = None
SPELL_SLOTS = None
WEAPON_PROFICIENCIES = ["Simple"]
