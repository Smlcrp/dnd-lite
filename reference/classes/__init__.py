"""Per-class combat-feature/spell-slot data, filtered to the player's own
class(es) and level before injection into the DM's prompt. Classes with no
authored module yet return None/'' gracefully -- a partial rollout across
the 13 D&D 5e classes must never break play for the others."""

from . import (
    artificer, barbarian, bard, cleric, druid, fighter, monk, paladin,
    ranger, rogue, sorcerer, warlock, wizard,
)

CLASS_MODULES = {
    "Artificer": artificer,
    "Barbarian": barbarian,
    "Bard": bard,
    "Cleric": cleric,
    "Druid": druid,
    "Fighter": fighter,
    "Monk": monk,
    "Paladin": paladin,
    "Ranger": ranger,
    "Rogue": rogue,
    "Sorcerer": sorcerer,
    "Warlock": warlock,
    "Wizard": wizard,
}

_ORDINALS = {1: "st", 2: "nd", 3: "rd"}


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}{_ORDINALS.get(n % 10, 'th')}"


def get_class_block(class_name: str, level: int, headroom: int = 2) -> str | None:
    """Returns a text block of this class's features from level 1 up to
    min(level + headroom, 20), its current resource pool sizes, and its
    spell-slot table at `level` if it's a caster. None if class_name has no
    authored module yet."""
    module = CLASS_MODULES.get(class_name)
    if module is None:
        return None

    cap = min(level + headroom, 20)
    lines = [f"{class_name.upper()} COMBAT FEATURES (through level {cap}):"]
    for lvl in sorted(module.FEATURES):
        if lvl > cap:
            break
        for feature in module.FEATURES[lvl]:
            lines.append(f"  Level {lvl}: {feature}")

    if module.RESOURCE_POOLS:
        # Cumulative, not just the highest applicable level's entry -- e.g.
        # Fighter's action_surge (introduced level 2) must still show at
        # level 10 even though indomitable (level 9) is the most recent add.
        merged_pools = {}
        for lvl in sorted(module.RESOURCE_POOLS):
            if lvl > level:
                break
            merged_pools.update(module.RESOURCE_POOLS[lvl])
        if merged_pools:
            pool_text = ", ".join(f"{k}: {v}" for k, v in merged_pools.items())
            lines.append(f"  Current resource pools (at level {level}): {pool_text}")

    if module.CASTER_TYPE and module.SPELL_SLOTS:
        applicable = [lvl for lvl in module.SPELL_SLOTS if lvl <= level]
        if applicable:
            slots = module.SPELL_SLOTS[max(applicable)]
            slots_text = ", ".join(f"{_ordinal(k)}: {v}" for k, v in sorted(slots.items()))
            lines.append(f"  Spell slots at level {level}: {slots_text}")

    return "\n".join(lines)


def build_class_features_prompt_block(classes: list, level: int) -> str:
    blocks = [b for b in (get_class_block(c, level) for c in classes) if b]
    return "\n\n".join(blocks)


def get_weapon_proficiencies(classes: list) -> set:
    """Union of each listed class's weapon-group proficiencies (Simple/
    Martial), used to filter reference.weapons' tables. A class with no
    authored module yet defaults to Simple only -- a conservative
    fallback, not a claim about its actual proficiencies."""
    proficiencies = set()
    for class_name in classes:
        module = CLASS_MODULES.get(class_name)
        if module is None:
            proficiencies.add("Simple")
            continue
        proficiencies.update(getattr(module, "WEAPON_PROFICIENCIES", ["Simple"]))
    return proficiencies
