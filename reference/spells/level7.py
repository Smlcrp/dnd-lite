"""SRD 7th-level spells. Authored incrementally -- see cantrips.py. Only
full casters (Bard/Cleric/Druid/Sorcerer/Wizard) reach 7th-level slots."""

SPELLS_LEVEL_7 = {
    "Finger of Death": {
        "school": "Necromancy",
        "casting_time": "1 action",
        "range": "60 feet",
        "duration": "Instantaneous",
        "classes": ["Sorcerer", "Warlock", "Wizard"],
        "description": "A target makes a Constitution save, taking 7d8+30 necrotic damage (half on success); a humanoid slain this way rises as a zombie under the caster's control.",
    },
    "Delayed Blast Fireball": {
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "150 feet",
        "duration": "Concentration, up to 1 minute",
        "classes": ["Sorcerer", "Wizard"],
        "description": "A fiery orb hangs in place, growing more dangerous the longer it's left (up to 12d6 fire damage) before detonating in a 20-foot radius (Dexterity save for half).",
    },
    "Fire Storm": {
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "150 feet",
        "duration": "Instantaneous",
        "classes": ["Cleric", "Druid"],
        "description": "Roaring flames fill up to ten connected 10-foot cubes; creatures there make a Dexterity save, taking 7d10 fire damage (half on success).",
    },
    "Reverse Gravity": {
        "school": "Transmutation",
        "casting_time": "1 action",
        "range": "100 feet",
        "duration": "Concentration, up to 1 minute",
        "classes": ["Druid", "Sorcerer", "Wizard"],
        "description": "Gravity reverses in a large cylinder, sending unsecured creatures and objects falling upward -- a battlefield-control option, no direct damage on its own.",
    },
    "Resurrection": {
        "school": "Necromancy",
        "casting_time": "1 hour",
        "range": "Touch",
        "duration": "Instantaneous",
        "classes": ["Cleric"],
        "description": "Returns a creature dead no more than a century to life, fully restored and free of lingering afflictions, aging the caster slightly.",
    },
    "Regenerate": {
        "school": "Transmutation",
        "casting_time": "1 minute",
        "range": "Touch",
        "duration": "1 hour",
        "classes": ["Bard", "Cleric", "Druid"],
        "description": "A touched creature regrows severed body parts and regains 4d8+15 hit points immediately, then 1 hit point at the start of each of its turns for the duration.",
    },
}
