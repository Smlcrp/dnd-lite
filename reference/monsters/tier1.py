"""Tier 1 (levels 1-4, "Local Heroes") curated monster/NPC archetypes.
Bounded, curated set -- not a full SRD bestiary. Each entry's
antagonist_archetype_keys ties it to adventure.ANTAGONIST_ARCHETYPES so the
DM's monster reference narrows to what's actually relevant to the current
adventure's antagonist, falling back to the full tier list otherwise."""

MONSTERS = [
    {
        "name": "Bandit",
        "ac": 12,
        "hp": "11 (2d8+2)",
        "attack": "+3 to hit, 1d6+1 slashing (scimitar) or 1d6+1 piercing (light crossbow)",
        "signature_ability": "None -- a straightforward melee/ranged skirmisher.",
        "antagonist_archetype_keys": ["defiant_general", "rival_mercenary_company", "smuggler_king"],
    },
    {
        "name": "Bandit Captain",
        "ac": 15,
        "hp": "65 (10d8+20)",
        "attack": "+5 to hit, 1d6+3 slashing (scimitar), two attacks per round",
        "signature_ability": "Parry: adds 2 to AC against one melee attack that would hit, if wielding a weapon and aware of the attacker.",
        "antagonist_archetype_keys": ["defiant_general", "rival_mercenary_company", "smuggler_king", "fallen_noble"],
    },
    {
        "name": "Cultist",
        "ac": 12,
        "hp": "9 (2d8)",
        "attack": "+3 to hit, 1d6+1 slashing (scimitar)",
        "signature_ability": "None -- fights in groups, flees if isolated.",
        "antagonist_archetype_keys": ["cult_leader", "self_styled_prophet"],
    },
    {
        "name": "Cult Fanatic",
        "ac": 13,
        "hp": "33 (6d8+6)",
        "attack": "+4 to hit, 1d4+2 piercing (dagger); casts minor spells (e.g. command, hold person)",
        "signature_ability": "Dark Devotion: advantage on saves against being charmed or frightened.",
        "antagonist_archetype_keys": ["cult_leader", "self_styled_prophet"],
    },
    {
        "name": "Thug",
        "ac": 11,
        "hp": "32 (5d8+10)",
        "attack": "+4 to hit, 1d6+2 bludgeoning (mace), two attacks per round",
        "signature_ability": "Pack Tactics: advantage on attack rolls if an ally is adjacent to the target.",
        "antagonist_archetype_keys": ["corrupt_guild_master", "smuggler_king"],
    },
    {
        "name": "Spy",
        "ac": 12,
        "hp": "27 (6d8)",
        "attack": "+3 to hit, 1d4+1 piercing (dagger)",
        "signature_ability": "Cunning Action: can Dash, Disengage, or Hide as a bonus action.",
        "antagonist_archetype_keys": ["spymaster", "corrupt_guild_master"],
    },
    {
        "name": "Guard",
        "ac": 16,
        "hp": "11 (2d8+2)",
        "attack": "+3 to hit, 1d6+1 slashing (spear)",
        "signature_ability": "None -- disciplined, holds formation.",
        "antagonist_archetype_keys": ["fallen_noble", "corrupt_guild_master"],
    },
    {
        "name": "Wolf Pack",
        "ac": 13,
        "hp": "11 (2d8+2) each",
        "attack": "+4 to hit, 2d4+2 piercing (bite)",
        "signature_ability": "Pack Tactics; if it hits a Medium or smaller target, the target must succeed on a Strength save or be knocked prone.",
        "antagonist_archetype_keys": ["ancient_spirit", "plague_hivemind"],
    },
    {
        "name": "Giant Rat Swarm",
        "ac": 12,
        "hp": "7 (2d6)",
        "attack": "+4 to hit, 1d3 piercing (bite)",
        "signature_ability": "Keen Smell: advantage on Wisdom (Perception) checks relying on smell.",
        "antagonist_archetype_keys": ["plague_hivemind"],
    },
    {
        "name": "Apprentice Cultist Spellcaster",
        "ac": 11,
        "hp": "18 (4d8)",
        "attack": "Casts firebolt (+4 to hit, 1d10 fire) or minor buffs on allies",
        "signature_ability": "None -- fragile, stays at range.",
        "antagonist_archetype_keys": ["cult_leader", "ancient_spirit"],
    },
]
