"""SRD cantrips. Authored incrementally, broadest coverage first (the
levels/classes actually played most) -- see class_lists.py for who gets
which."""

SPELLS_CANTRIPS = {
    "Fire Bolt": {
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "120 feet",
        "duration": "Instantaneous",
        "classes": ["Artificer", "Sorcerer", "Wizard"],
        "description": (
            "Ranged spell attack hurling a mote of fire; on a hit deals "
            "1d10 fire damage (more dice at higher character levels)."
        ),
    },
    "Mage Hand": {
        "school": "Conjuration",
        "casting_time": "1 action",
        "range": "30 feet",
        "duration": "1 minute",
        "classes": ["Artificer", "Bard", "Sorcerer", "Warlock", "Wizard"],
        "description": (
            "Conjures a spectral hand that can manipulate objects, open "
            "unlocked doors/containers, or carry a small item at range."
        ),
    },
    "Prestidigitation": {
        "school": "Transmutation",
        "casting_time": "1 action",
        "range": "10 feet",
        "duration": "Up to 1 hour",
        "classes": ["Bard", "Sorcerer", "Warlock", "Wizard"],
        "description": (
            "A minor magic trick -- a harmless sensory effect, lighting or "
            "snuffing a small flame, cleaning/soiling an object, or a "
            "similar trivial effect. No combat utility."
        ),
    },
    "Ray of Frost": {
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "60 feet",
        "duration": "Instantaneous",
        "classes": ["Sorcerer", "Wizard"],
        "description": (
            "Ranged spell attack of freezing air; on a hit deals 1d8 cold "
            "damage and reduces the target's speed by 10 feet until the "
            "start of your next turn."
        ),
    },
    "Eldritch Blast": {
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "120 feet",
        "duration": "Instantaneous",
        "classes": ["Warlock"],
        "description": (
            "The Warlock's signature attack: a beam of crackling energy, "
            "ranged spell attack for 1d10 force damage. Fires an "
            "additional beam (its own attack roll) at 5th, 11th, and 17th "
            "level -- 2/3/4 beams total, which can target the same or "
            "different creatures."
        ),
    },
    "Sacred Flame": {
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "60 feet",
        "duration": "Instantaneous",
        "classes": ["Cleric"],
        "description": (
            "Flame-like radiance descends on a target; it must succeed on "
            "a Dexterity save or take 1d8 radiant damage. Ignores cover."
        ),
    },
    "Guidance": {
        "school": "Divination",
        "casting_time": "1 action",
        "range": "Touch",
        "duration": "Concentration, up to 1 minute",
        "classes": ["Artificer", "Cleric", "Druid"],
        "description": "A touched creature adds 1d4 to one ability check of its choice before the spell ends. No combat use.",
    },
    "Vicious Mockery": {
        "school": "Enchantment",
        "casting_time": "1 action",
        "range": "60 feet",
        "duration": "Instantaneous",
        "classes": ["Bard"],
        "description": (
            "An insulting string of words; on a failed Wisdom save the "
            "target takes 1d4 psychic damage and has disadvantage on its "
            "next attack roll before the end of its next turn."
        ),
    },
    "Minor Illusion": {
        "school": "Illusion",
        "casting_time": "1 action",
        "range": "30 feet",
        "duration": "1 minute",
        "classes": ["Artificer", "Bard", "Sorcerer", "Warlock", "Wizard"],
        "description": "Creates a harmless sound or image illusion in an unoccupied space -- a distraction, not direct damage.",
    },
    "Produce Flame": {
        "school": "Conjuration",
        "casting_time": "1 action",
        "range": "Self",
        "duration": "10 minutes",
        "classes": ["Druid"],
        "description": (
            "A flickering flame sits harmlessly in the caster's hand "
            "(usable as a torch) and can be hurled: ranged spell attack "
            "for 1d8 fire damage."
        ),
    },
    "Shillelagh": {
        "school": "Transmutation",
        "casting_time": "1 bonus action",
        "range": "Touch",
        "duration": "1 minute",
        "classes": ["Druid"],
        "description": (
            "Imbues a club or quarterstaff with nature magic: the wielder "
            "can use Wisdom for its attack/damage rolls, and its damage "
            "die becomes 1d8."
        ),
    },
    "Thaumaturgy": {
        "school": "Transmutation",
        "casting_time": "1 action",
        "range": "30 feet",
        "duration": "Up to 1 minute",
        "classes": ["Cleric"],
        "description": "Minor supernatural manifestations (a booming voice, flickering light, trembling ground) -- intimidation flavor, no direct damage.",
    },
    "Spare the Dying": {
        "school": "Necromancy",
        "casting_time": "1 action",
        "range": "Touch",
        "duration": "Instantaneous",
        "classes": ["Artificer", "Cleric"],
        "description": "A touched creature at 0 HP becomes stable, ending the dying condition without healing it.",
    },
    "Light": {
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "Touch",
        "duration": "1 hour",
        "classes": ["Artificer", "Bard", "Cleric", "Sorcerer", "Wizard"],
        "description": "An object sheds bright light in a 20-foot radius. No combat use, but useful narration color for dark scenes.",
    },
    "True Strike": {
        "school": "Divination",
        "casting_time": "1 action",
        "range": "30 feet",
        "duration": "Concentration, up to 1 round",
        "classes": ["Bard", "Sorcerer", "Warlock", "Wizard"],
        "description": "Briefly glimpse a target's defenses; the caster's next attack roll against it (before the spell ends) has advantage.",
    },
    "Resistance": {
        "school": "Abjuration",
        "casting_time": "1 action",
        "range": "Touch",
        "duration": "Concentration, up to 1 minute",
        "classes": ["Artificer", "Cleric", "Druid"],
        "description": "A touched creature adds 1d4 to one saving throw of its choice before the spell ends.",
    },
    "Poison Spray": {
        "school": "Conjuration",
        "casting_time": "1 action",
        "range": "10 feet",
        "duration": "Instantaneous",
        "classes": ["Artificer", "Druid", "Sorcerer", "Warlock", "Wizard"],
        "description": "A puff of noxious gas; the target makes a Constitution save or takes 1d12 poison damage.",
    },
    "Blade Ward": {
        "school": "Abjuration",
        "casting_time": "1 action",
        "range": "Self",
        "duration": "1 round",
        "classes": ["Bard", "Sorcerer", "Warlock", "Wizard"],
        "description": "Resistance to bludgeoning, piercing, and slashing damage from weapon attacks until the start of the caster's next turn.",
    },
    "Message": {
        "school": "Transmutation",
        "casting_time": "1 action",
        "range": "120 feet",
        "duration": "1 round",
        "classes": ["Artificer", "Bard", "Sorcerer", "Wizard"],
        "description": "A whispered message and reply travel to/from a chosen creature. No combat use, but useful for quiet coordination.",
    },
}
