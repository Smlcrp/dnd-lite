"""Curated tier-based monster/NPC archetypes -- combat stats for the DM's
own narration, never a full SRD bestiary. Split one file per tier (mirrors
reference/spells/'s per-spell-level split) since each tier is authored and
sized independently and tiers 2-4 fill in over time."""

import adventure

from . import tier1, tier2, tier3, tier4

MONSTER_ARCHETYPES = {
    1: tier1.MONSTERS,
    2: tier2.MONSTERS,
    3: tier3.MONSTERS,
    4: tier4.MONSTERS,
}


def get_monster_archetypes(level: int, antagonist_archetype_key: str = None) -> list:
    """Returns the current tier's curated monster list, narrowed to entries
    matching antagonist_archetype_key when at least one matches, otherwise
    the full (already-bounded) tier list."""
    tier_list = MONSTER_ARCHETYPES.get(adventure._tier_number(level), [])
    if antagonist_archetype_key:
        filtered = [m for m in tier_list if antagonist_archetype_key in m.get("antagonist_archetype_keys", [])]
        if filtered:
            return filtered
    return tier_list


def build_monster_prompt_block(level: int, adventure_dict: dict = None) -> str:
    key = (adventure_dict or {}).get("antagonist_archetype_key")
    entries = get_monster_archetypes(level, key)
    if not entries:
        return ""
    lines = [
        "MONSTER/NPC REFERENCE (tier-appropriate combat stats for enemies "
        "you narrate -- never read aloud as a stat block):"
    ]
    for m in entries:
        lines.append(f"  {m['name']}: AC {m['ac']}, HP {m['hp']}, {m['attack']}. {m['signature_ability']}")
    return "\n".join(lines)
