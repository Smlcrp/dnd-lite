"""SRD 6th-level spells. Authored incrementally -- see cantrips.py. Only
full casters (Bard/Cleric/Druid/Sorcerer/Wizard) reach 6th-level slots;
half-casters (Paladin/Ranger/Artificer) cap at 5th, Warlock's Pact Magic
caps its actual slots at 5th too (Mystic Arcanum is a separate once-per-day
mechanic noted in warlock.py's FEATURES, not fed through this spell list)."""

SPELLS_LEVEL_6 = {
    "Disintegrate": {
        "school": "Transmutation",
        "casting_time": "1 action",
        "range": "60 feet",
        "duration": "Instantaneous",
        "classes": ["Sorcerer", "Wizard"],
        "description": "A thin green ray; on a failed Dexterity save the target takes 10d6+40 force damage, and is disintegrated into dust if this reduces it to 0 HP.",
    },
    "Chain Lightning": {
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "150 feet",
        "duration": "Instantaneous",
        "classes": ["Sorcerer", "Wizard"],
        "description": "A bolt of lightning arcs to a primary target and up to three others; each makes a Dexterity save, taking 10d8 lightning damage (half on success).",
    },
    "Heal": {
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "60 feet",
        "duration": "Instantaneous",
        "classes": ["Cleric", "Druid"],
        "description": "A target regains 70 hit points and is cured of blindness and any disease.",
    },
    "Harm": {
        "school": "Necromancy",
        "casting_time": "1 action",
        "range": "60 feet",
        "duration": "Instantaneous",
        "classes": ["Cleric"],
        "description": "A target makes a Constitution save, taking 14d6 necrotic damage (half on success) and having its hit point maximum reduced by the damage taken.",
    },
    "True Seeing": {
        "school": "Divination",
        "casting_time": "1 action",
        "range": "Touch",
        "duration": "1 hour",
        "classes": ["Bard", "Cleric", "Sorcerer", "Warlock", "Wizard"],
        "description": "A touched creature sees through illusions and invisibility and gains darkvision for the duration -- strips away many enemy defensive tricks.",
    },
    "Circle of Death": {
        "school": "Necromancy",
        "casting_time": "1 action",
        "range": "150 feet",
        "duration": "Instantaneous",
        "classes": ["Sorcerer", "Warlock", "Wizard"],
        "description": "A sphere of negative energy; creatures in a 60-foot radius make a Constitution save, taking 8d6 necrotic damage (half on success).",
    },
    "Eyebite": {
        "school": "Necromancy",
        "casting_time": "1 action",
        "range": "60 feet",
        "duration": "Concentration, up to 1 minute",
        "classes": ["Bard", "Sorcerer", "Warlock", "Wizard"],
        "description": "Each turn, locks eyes with one target: on a failed Wisdom save it falls asleep, becomes panicked and flees, or is sickened (disadvantage on attacks/checks) -- caster's choice.",
    },
    "Sunbeam": {
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "Self (60-foot line)",
        "duration": "Concentration, up to 1 minute",
        "classes": ["Druid", "Sorcerer", "Wizard"],
        "description": "A beam of radiant light; each creature in the line makes a Constitution save, taking 6d8 radiant damage (half on success) and being blinded until the caster's next turn on a fail.",
    },
}
