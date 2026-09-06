"""SRD 9th-level spells -- the highest tier, reached only by a full caster
at character level 17-20. Authored incrementally -- see cantrips.py."""

SPELLS_LEVEL_9 = {
    "Meteor Swarm": {
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "1 mile",
        "duration": "Instantaneous",
        "classes": ["Sorcerer", "Wizard"],
        "description": "Four blazing orbs streak down onto chosen points; each creature within 40 feet of a point makes a Dexterity save, taking 20d6 fire + 20d6 bludgeoning damage (half on success) -- one of the most devastating spells in the game.",
    },
    "Power Word Kill": {
        "school": "Enchantment",
        "casting_time": "1 action",
        "range": "60 feet",
        "duration": "Instantaneous",
        "classes": ["Sorcerer", "Warlock", "Wizard"],
        "description": "If the target has 100 hit points or fewer, it dies instantly -- no saving throw. No effect on tougher creatures.",
    },
    "Wish": {
        "school": "Conjuration",
        "casting_time": "1 action",
        "range": "Self",
        "duration": "Instantaneous",
        "classes": ["Sorcerer", "Wizard"],
        "description": "The most powerful spell a mortal can cast: duplicates any spell of 8th level or lower without needing its usual components, or creates a nearly unlimited effect at the DM's discretion and real personal risk to the caster.",
    },
    "Mass Heal": {
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "60 feet",
        "duration": "Instantaneous",
        "classes": ["Cleric"],
        "description": "Up to six creatures in an area regain 700 hit points total (distributed as the caster chooses) and are cured of blindness and disease.",
    },
    "Storm of Vengeance": {
        "school": "Conjuration",
        "casting_time": "1 action",
        "range": "Sight",
        "duration": "Concentration, up to 1 minute",
        "classes": ["Druid"],
        "description": "A massive storm cloud forms overhead, each round bringing a new escalating effect (deafening thunder, acid rain, lightning bolts, hail, gale-force winds) across a huge radius.",
    },
}
