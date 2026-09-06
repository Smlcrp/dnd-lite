"""Barbarian combat-relevant features by level (SRD core class). Ability
Score Improvement levels and the level-20 ability-score-cap capstone are
omitted -- ability scores aren't tracked by this app."""

FEATURES = {
    1: ["Rage (bonus action, 2/long rest: +2 melee damage, resistance to bludgeoning/piercing/slashing, advantage on Strength checks/saves, lasts 1 minute)", "Unarmored Defense (AC benefit while unarmored -- not tracked here, player's sheet is authoritative)"],
    2: ["Reckless Attack (advantage on Strength-based melee attacks this turn, but attacks against you have advantage until your next turn)", "Danger Sense (advantage on Dexterity saves against effects you can see)"],
    3: ["Primal Path feature (subclass-specific)"],
    5: ["Extra Attack (attack twice whenever you take the Attack action)", "Fast Movement (+10 ft. speed while not heavily armored)"],
    6: ["Primal Path feature"],
    7: ["Feral Instinct (advantage on initiative; can act while surprised if raging)"],
    9: ["Brutal Critical (+1 extra weapon damage die on a critical hit)"],
    10: ["Primal Path feature"],
    11: ["Relentless Rage (on dropping to 0 HP while raging, Constitution save to drop to 1 HP instead)"],
    13: ["Brutal Critical (2 extra dice)"],
    14: ["Primal Path feature"],
    15: ["Persistent Rage (rage only ends early if you fall unconscious or choose to end it)"],
    17: ["Brutal Critical (3 extra dice)"],
    18: ["Indomitable Might (Strength check total is at least your Strength score)"],
    20: ["Primal Champion (further ability score cap increase -- not tracked here)"],
}

RESOURCE_POOLS = {
    1: {"rage_uses_per_long_rest": 2, "rage_damage_bonus": 2},
    3: {"rage_uses_per_long_rest": 3},
    6: {"rage_uses_per_long_rest": 4},
    9: {"rage_damage_bonus": 3},
    12: {"rage_uses_per_long_rest": 5},
    16: {"rage_damage_bonus": 4},
    17: {"rage_uses_per_long_rest": 6},
    20: {"rage_uses_per_long_rest": "unlimited"},
}

CASTER_TYPE = None
SPELL_SLOTS = None
WEAPON_PROFICIENCIES = ["Simple", "Martial"]
