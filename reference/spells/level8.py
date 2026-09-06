"""SRD 8th-level spells. Authored incrementally -- see cantrips.py. Only
full casters (Bard/Cleric/Druid/Sorcerer/Wizard) reach 8th-level slots."""

SPELLS_LEVEL_8 = {
    "Sunburst": {
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "Self (60-foot radius)",
        "duration": "Instantaneous",
        "classes": ["Druid", "Sorcerer", "Wizard"],
        "description": "Brilliant sunlight fills a large radius; each creature there makes a Constitution save, taking 12d6 radiant damage (half on success) and being blinded for 1 minute on a fail.",
    },
    "Power Word Stun": {
        "school": "Enchantment",
        "casting_time": "1 action",
        "range": "60 feet",
        "duration": "Instantaneous",
        "classes": ["Bard", "Sorcerer", "Warlock", "Wizard"],
        "description": "If the target has 150 hit points or fewer, it is stunned outright -- no saving throw. No effect on tougher creatures.",
    },
    "Earthquake": {
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "500 feet",
        "duration": "Concentration, up to 1 minute",
        "classes": ["Cleric", "Druid", "Sorcerer"],
        "description": "The ground in a large radius churns and cracks; creatures there make a Dexterity save each round or fall prone, and structures can collapse.",
    },
    "Incendiary Cloud": {
        "school": "Conjuration",
        "casting_time": "1 action",
        "range": "150 feet",
        "duration": "Concentration, up to 1 minute",
        "classes": ["Sorcerer", "Wizard"],
        "description": "A cloud of roiling smoke and embers fills an area; each creature there makes a Dexterity save each turn, taking 10d8 fire damage (half on success).",
    },
    "Holy Aura": {
        "school": "Abjuration",
        "casting_time": "1 action",
        "range": "Self (30-foot radius)",
        "duration": "Concentration, up to 1 minute",
        "classes": ["Cleric"],
        "description": "Allies in the radius gain advantage on saving throws and attackers against them have disadvantage, while concentration holds -- a powerful defensive capstone effect.",
    },
}
