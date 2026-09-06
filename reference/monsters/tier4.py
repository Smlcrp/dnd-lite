"""Tier 4 (levels 17-20, "Masters of the World") curated monster/NPC
archetypes. Bounded, curated set -- not a full SRD bestiary."""

MONSTERS = [
    {
        "name": "Ancient Dragon",
        "ac": 22,
        "hp": "546 (28d20+252)",
        "attack": "+17 to hit, 2d10+10 (bite), plus a world-shaking breath weapon (recharges on 5-6) that can devastate an entire battlefield",
        "signature_ability": "Legendary Actions and a Legendary Resistance (auto-succeeds on failed saves a few times per day); Frightful Presence affects an entire area.",
        "antagonist_archetype_keys": ["defiant_general", "self_styled_prophet"],
    },
    {
        "name": "Pit Fiend (Archdevil's Herald)",
        "ac": 19,
        "hp": "300 (24d10+168)",
        "attack": "+14 to hit, 4d6+8 piercing (bite, poison) plus a mace and a fiery whip",
        "signature_ability": "Magic Resistance, innate spellcasting (wall of fire, hold monster), commands legions of lesser devils.",
        "antagonist_archetype_keys": ["cult_leader"],
    },
    {
        "name": "Balor (Demon Lord's Herald)",
        "ac": 19,
        "hp": "262 (21d12+126)",
        "attack": "+16 to hit, 3d8+9 slashing (flaming longsword) plus 3d8+9 lightning (lightning whip)",
        "signature_ability": "Death Throes: explodes in fire on death, devastating the area; wreathed in fire and lightning.",
        "antagonist_archetype_keys": ["plague_hivemind", "ancient_spirit"],
    },
    {
        "name": "Fallen Celestial",
        "ac": 21,
        "hp": "230 (20d12+100)",
        "attack": "+15 to hit, 3d8+8 radiant-turned-necrotic (corrupted greatsword), plus divine-twisted spellcasting",
        "signature_ability": "Once served a higher power; commands unnerving, reality-bending presence over mortals.",
        "antagonist_archetype_keys": ["self_styled_prophet", "cult_leader"],
    },
    {
        "name": "Elder Aboleth-Kin",
        "ac": 20,
        "hp": "280 (24d12+120)",
        "attack": "+14 to hit, 2d8+7 slashing (tentacles) spreading a mind-altering affliction across a whole settlement",
        "signature_ability": "Dominates entire communities over time; nearly impossible to fully destroy once entrenched.",
        "antagonist_archetype_keys": ["plague_hivemind", "ancient_spirit", "smuggler_king"],
    },
    {
        "name": "Archlich",
        "ac": 19,
        "hp": "250 (20d8+160)",
        "attack": "+16 to hit, disintegrating touch or the highest tier of prepared spells",
        "signature_ability": "Multiple hidden phylacteries; commands legions of undead across a kingdom.",
        "antagonist_archetype_keys": ["ancient_spirit", "cult_leader", "self_styled_prophet", "spymaster", "corrupt_guild_master"],
    },
    {
        "name": "Storm Giant Sovereign",
        "ac": 20,
        "hp": "230 (20d12+100)",
        "attack": "+16 to hit, 3d8+9 bludgeoning (greatsword) plus command over lightning and thunder",
        "signature_ability": "Commands storms and lesser giants; strikes with the authority of a monarch.",
        "antagonist_archetype_keys": ["defiant_general", "fallen_noble", "rival_mercenary_company"],
    },
]
