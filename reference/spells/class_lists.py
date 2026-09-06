"""Which spells appear on which class's list, by spell level -- just a name
index (not full spell text) so canonical spell content in cantrips.py/
level1.py/etc. is never duplicated per class. Authored incrementally,
alongside reference/classes/'s per-class modules.

Generated from (and must stay consistent with) each spell's own "classes"
field across cantrips.py/level1.py/.../level9.py -- when adding a new
spell, add it there first, then regenerate/extend this index to match.

Warlock's entries stop at spell level 5 even though the SRD Warlock list
technically extends further, because get_spells_for_class() filters by
SPELL_SLOTS's max spell level and Warlock's Pact Magic caps there -- higher
Warlock spells are accessed one-per-day via Mystic Arcanum (see
classes/warlock.py's FEATURES), a separate mechanic this app doesn't model
through the slot system. Listing them here would just be dead data."""

CLASS_SPELL_LISTS = {
    "Artificer": {
        0: ["Fire Bolt", "Mage Hand", "Guidance", "Minor Illusion", "Spare the Dying", "Light", "Resistance", "Poison Spray", "Message"],
        1: ["Detect Magic", "Cure Wounds", "Thunderwave", "Feather Fall"],
        2: ["Invisibility", "Hold Person", "Aid", "Lesser Restoration", "Flaming Sphere", "Blindness/Deafness", "Enhance Ability", "Heat Metal", "Shatter"],
        3: ["Fly", "Haste", "Revivify", "Dispel Magic", "Daylight"],
        4: ["Freedom of Movement", "Stoneskin"],
    },
    "Bard": {
        0: ["Mage Hand", "Prestidigitation", "Vicious Mockery", "Minor Illusion", "Light", "True Strike", "Blade Ward", "Message"],
        1: ["Detect Magic", "Cure Wounds", "Healing Word", "Thunderwave", "Charm Person", "Sleep", "Heroism", "Dissonant Whispers", "Feather Fall"],
        2: ["Invisibility", "Hold Person", "Lesser Restoration", "Suggestion", "Blindness/Deafness", "Enhance Ability", "Heat Metal", "Shatter"],
        3: ["Dispel Magic", "Hypnotic Pattern"],
        4: ["Greater Invisibility", "Polymorph", "Freedom of Movement", "Confusion"],
        5: ["Hold Monster", "Mass Cure Wounds", "Dominate Person"],
        6: ["True Seeing", "Eyebite"],
        7: ["Regenerate"],
        8: ["Power Word Stun"],
    },
    "Cleric": {
        0: ["Sacred Flame", "Guidance", "Thaumaturgy", "Spare the Dying", "Light", "Resistance"],
        1: ["Detect Magic", "Cure Wounds", "Healing Word", "Bless", "Guiding Bolt", "Command", "Sanctuary", "Bane", "Inflict Wounds", "Shield of Faith"],
        2: ["Hold Person", "Spiritual Weapon", "Aid", "Lesser Restoration", "Blindness/Deafness", "Enhance Ability"],
        3: ["Spirit Guardians", "Revivify", "Dispel Magic", "Animate Dead", "Daylight"],
        4: ["Guardian of Faith", "Death Ward", "Freedom of Movement", "Banishment"],
        5: ["Mass Cure Wounds", "Raise Dead", "Flame Strike", "Insect Plague", "Contagion", "Commune"],
        6: ["Heal", "Harm", "True Seeing"],
        7: ["Fire Storm", "Resurrection", "Regenerate"],
        8: ["Earthquake", "Holy Aura"],
        9: ["Mass Heal"],
    },
    "Druid": {
        0: ["Guidance", "Produce Flame", "Shillelagh", "Resistance", "Poison Spray"],
        1: ["Detect Magic", "Cure Wounds", "Healing Word", "Entangle", "Faerie Fire", "Goodberry", "Thunderwave", "Charm Person"],
        2: ["Lesser Restoration", "Moonbeam", "Flaming Sphere", "Enhance Ability", "Heat Metal", "Spike Growth"],
        3: ["Dispel Magic", "Call Lightning", "Conjure Animals", "Daylight"],
        4: ["Ice Storm", "Wall of Fire", "Polymorph", "Dominate Beast", "Freedom of Movement", "Confusion", "Stoneskin"],
        5: ["Mass Cure Wounds", "Insect Plague", "Contagion"],
        6: ["Heal", "Sunbeam"],
        7: ["Fire Storm", "Reverse Gravity", "Regenerate"],
        8: ["Sunburst", "Earthquake"],
        9: ["Storm of Vengeance"],
    },
    "Paladin": {
        1: ["Detect Magic", "Cure Wounds", "Bless", "Command", "Heroism", "Shield of Faith", "Divine Favor"],
        2: ["Aid", "Lesser Restoration", "Branding Smite", "Find Steed"],
        3: ["Revivify", "Dispel Magic", "Daylight"],
        4: ["Death Ward"],
        5: ["Raise Dead"],
    },
    "Ranger": {
        1: ["Detect Magic", "Cure Wounds", "Entangle", "Goodberry", "Hunter's Mark"],
        2: ["Lesser Restoration", "Spike Growth"],
        3: ["Conjure Animals"],
        4: ["Freedom of Movement"],
        5: ["Swift Quiver"],
    },
    "Sorcerer": {
        0: ["Fire Bolt", "Mage Hand", "Prestidigitation", "Ray of Frost", "Minor Illusion", "Light", "True Strike", "Poison Spray", "Blade Ward", "Message"],
        1: ["Magic Missile", "Shield", "Burning Hands", "Detect Magic", "Thunderwave", "Charm Person", "Sleep", "Chromatic Orb", "Witch Bolt", "Feather Fall"],
        2: ["Scorching Ray", "Misty Step", "Invisibility", "Web", "Mirror Image", "Hold Person", "Suggestion", "Blindness/Deafness", "Enhance Ability", "Shatter", "Darkness"],
        3: ["Fireball", "Lightning Bolt", "Counterspell", "Fly", "Haste", "Dispel Magic", "Daylight", "Hypnotic Pattern", "Slow"],
        4: ["Ice Storm", "Wall of Fire", "Greater Invisibility", "Polymorph", "Dominate Beast", "Banishment", "Confusion", "Stoneskin", "Fire Shield"],
        5: ["Cone of Cold", "Hold Monster", "Insect Plague", "Dominate Person"],
        6: ["Disintegrate", "Chain Lightning", "True Seeing", "Circle of Death", "Eyebite", "Sunbeam"],
        7: ["Finger of Death", "Delayed Blast Fireball", "Reverse Gravity"],
        8: ["Sunburst", "Power Word Stun", "Earthquake", "Incendiary Cloud"],
        9: ["Meteor Swarm", "Power Word Kill", "Wish"],
    },
    "Warlock": {
        0: ["Mage Hand", "Prestidigitation", "Eldritch Blast", "Minor Illusion", "True Strike", "Poison Spray", "Blade Ward"],
        1: ["Charm Person", "Witch Bolt", "Hex", "Armor of Agathys", "Hellish Rebuke"],
        2: ["Misty Step", "Invisibility", "Mirror Image", "Hold Person", "Suggestion", "Shatter", "Darkness"],
        3: ["Counterspell", "Fly", "Dispel Magic", "Vampiric Touch", "Hypnotic Pattern"],
        4: ["Banishment"],
        5: ["Hold Monster"],
    },
    "Wizard": {
        0: ["Fire Bolt", "Mage Hand", "Prestidigitation", "Ray of Frost", "Minor Illusion", "Light", "True Strike", "Poison Spray", "Blade Ward", "Message"],
        1: ["Magic Missile", "Shield", "Burning Hands", "Detect Magic", "Thunderwave", "Charm Person", "Sleep", "Chromatic Orb", "Witch Bolt", "Feather Fall"],
        2: ["Scorching Ray", "Misty Step", "Invisibility", "Web", "Mirror Image", "Hold Person", "Flaming Sphere", "Suggestion", "Blindness/Deafness", "Shatter", "Darkness"],
        3: ["Fireball", "Lightning Bolt", "Counterspell", "Fly", "Haste", "Dispel Magic", "Vampiric Touch", "Animate Dead", "Hypnotic Pattern", "Slow"],
        4: ["Ice Storm", "Wall of Fire", "Greater Invisibility", "Polymorph", "Banishment", "Confusion", "Stoneskin", "Fire Shield"],
        5: ["Cone of Cold", "Wall of Force", "Hold Monster", "Dominate Person"],
        6: ["Disintegrate", "Chain Lightning", "True Seeing", "Circle of Death", "Eyebite", "Sunbeam"],
        7: ["Finger of Death", "Delayed Blast Fireball", "Reverse Gravity"],
        8: ["Sunburst", "Power Word Stun", "Incendiary Cloud"],
        9: ["Meteor Swarm", "Power Word Kill", "Wish"],
    },
}
