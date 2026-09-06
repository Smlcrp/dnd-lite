"""Paladin combat-relevant features and spell-slot progression by level (SRD
core class, half caster). Lay on Hands's healing pool (5 x paladin level)
scales by a simple formula, described qualitatively rather than enumerated."""

from ._shared import HALF_CASTER_SPELL_SLOTS

FEATURES = {
    1: ["Divine Sense (detect celestials/fiends/undead nearby)", "Lay on Hands (touch-heal from a pool of 5 x paladin level HP, refills on long rest)"],
    2: ["Fighting Style (a chosen combat specialty)", "Spellcasting (Charisma-based)", "Divine Smite (expend a spell slot on a melee hit for extra radiant damage)"],
    3: ["Divine Health (immune to disease)", "Sacred Oath feature (subclass-specific)", "Channel Divinity (1/rest: oath-specific effect)"],
    5: ["Extra Attack (attack twice whenever you take the Attack action)"],
    6: ["Aura of Protection (bonus to saving throws for you and nearby allies)"],
    7: ["Sacred Oath feature"],
    10: ["Aura of Courage (immune to being frightened, extends to nearby allies)"],
    11: ["Improved Divine Smite (all melee weapon hits deal extra radiant damage)"],
    14: ["Cleansing Touch (spend an action to end one spell affecting you or a willing target)"],
    15: ["Sacred Oath feature"],
    18: ["Aura of Protection/Courage range increases"],
    20: ["Sacred Oath capstone feature"],
}

RESOURCE_POOLS = {
    3: {"channel_divinity_uses_per_rest": 1},
}

CASTER_TYPE = "half"
SPELL_SLOTS = HALF_CASTER_SPELL_SLOTS
WEAPON_PROFICIENCIES = ["Simple", "Martial"]
