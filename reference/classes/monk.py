"""Monk combat-relevant features by level (SRD core class). Ki points equal
monk level from level 2 on -- a simple formula, described qualitatively
rather than enumerated as a RESOURCE_POOLS entry per level."""

FEATURES = {
    1: ["Martial Arts (unarmed strikes/monk weapons deal 1d4 and can use Dexterity)", "Unarmored Defense (AC benefit while unarmored -- not tracked here)"],
    2: ["Ki (points = monk level; fuels Flurry of Blows, Patient Defense, Step of the Wind)", "Unarmored Movement (+speed while unarmored)"],
    3: ["Monastic Tradition feature (subclass-specific)", "Deflect Missiles (reduce/redirect a ranged weapon attack's damage)"],
    4: ["Slow Fall (reduce falling damage)"],
    5: ["Extra Attack (attack twice whenever you take the Attack action)", "Stunning Strike (spend a ki point to force a Constitution save or be stunned)", "Martial Arts die improves to 1d6"],
    6: ["Ki-Empowered Strikes (unarmed strikes count as magical)", "Monastic Tradition feature"],
    7: ["Evasion (no damage on a successful Dexterity save vs. an area effect)", "Stillness of Mind (end your own charmed/frightened condition as an action)"],
    9: ["Unarmored Movement improves (can move along vertical surfaces/liquid briefly)"],
    10: ["Purity of Body (immune to disease and poison)"],
    11: ["Monastic Tradition feature", "Martial Arts die improves to 1d8"],
    13: ["Tongue of the Sun and Moon (understand all spoken languages)"],
    14: ["Diamond Soul (proficiency in all saving throws)"],
    15: ["Timeless Body (no longer needs food/water, ages very slowly)"],
    17: ["Monastic Tradition feature", "Martial Arts die improves to 1d10"],
    18: ["Empty Body (become invisible briefly, or manifest astral projection)"],
    20: ["Perfect Self (regain ki points on rolling initiative with none left)"],
}

RESOURCE_POOLS = {}

CASTER_TYPE = None
SPELL_SLOTS = None
WEAPON_PROFICIENCIES = ["Simple"]
