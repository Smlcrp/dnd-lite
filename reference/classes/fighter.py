"""Fighter combat-relevant features by level (SRD core class, subclass
features summarized generically since this app doesn't track a chosen
subclass). Ability Score Improvement levels are omitted -- ability scores
aren't tracked by this app; they live on the player's own sheet."""

FEATURES = {
    1: [
        "Fighting Style (a chosen combat specialty, e.g. Archery, Defense, "
        "Dueling, Great Weapon Fighting)",
        "Second Wind (bonus action, once per rest: regain 1d10 + fighter level HP)",
    ],
    2: ["Action Surge (once per rest: take one additional action on your turn)"],
    3: ["Martial Archetype feature (subclass-specific combat option)"],
    5: ["Extra Attack (attack twice whenever you take the Attack action)"],
    7: ["Martial Archetype feature"],
    9: ["Indomitable (once per long rest: reroll a failed saving throw)"],
    10: ["Martial Archetype feature"],
    11: ["Extra Attack (2) -- attack three times whenever you take the Attack action"],
    13: ["Indomitable (two uses per long rest)"],
    15: ["Martial Archetype feature"],
    17: ["Action Surge (two uses per rest)", "Indomitable (three uses per long rest)"],
    18: ["Martial Archetype feature"],
    20: ["Extra Attack (3) -- attack four times whenever you take the Attack action"],
}

RESOURCE_POOLS = {
    2: {"action_surge_uses_per_rest": 1},
    9: {"indomitable_uses_per_long_rest": 1},
    13: {"indomitable_uses_per_long_rest": 2},
    17: {"action_surge_uses_per_rest": 2, "indomitable_uses_per_long_rest": 3},
}

CASTER_TYPE = None
SPELL_SLOTS = None
WEAPON_PROFICIENCIES = ["Simple", "Martial"]
