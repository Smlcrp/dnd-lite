"""Bard combat-relevant features and spell-slot progression by level (SRD
core class). Bardic Inspiration uses per rest scale with Charisma modifier
(not tracked by this app -- described qualitatively rather than as a fixed
RESOURCE_POOLS number)."""

from ._shared import FULL_CASTER_SPELL_SLOTS

FEATURES = {
    1: [
        "Spellcasting (Charisma-based)",
        "Bardic Inspiration (bonus action, d6: give an ally a die to add to "
        "one attack/check/save; uses per long rest = Charisma modifier, min 1)",
    ],
    2: ["Jack of All Trades (add half proficiency to checks not already proficient in)", "Song of Rest (extra healing for the group on a short rest)"],
    3: ["Bard College feature (subclass-specific)", "Expertise (double proficiency bonus on two skills)"],
    5: ["Bardic Inspiration die improves to d8", "Font of Inspiration (Bardic Inspiration also regains on a short rest)"],
    6: ["Bard College feature", "Countercharm (advantage for nearby allies against being frightened/charmed)"],
    9: ["Bardic Inspiration die improves to d10"],
    10: ["Magical Secrets (learn spells from any class's list)", "Expertise (two more skills)"],
    14: ["Bard College feature"],
    15: ["Bardic Inspiration die improves to d12"],
    18: ["Magical Secrets (more spells from any class's list)"],
    20: ["Superior Inspiration (regain a Bardic Inspiration use on rolling initiative with none left)"],
}

RESOURCE_POOLS = {}

CASTER_TYPE = "full"
SPELL_SLOTS = FULL_CASTER_SPELL_SLOTS
WEAPON_PROFICIENCIES = ["Simple"]
