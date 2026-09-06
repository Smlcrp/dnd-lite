"""SRD weapon table -- damage dice/type and properties only, for the DM's
narration precision. No to-hit bonuses or arithmetic here; the player's own
sheet is authoritative for that.

Split into Simple/Martial x Melee/Ranged tables (rather than one flat 37-
entry table) so injection can filter to just the proficiency groups a
class actually has, mirroring real 5e weapon-proficiency rules -- a Wizard
session never needs the Martial tables in its prompt."""

SIMPLE_MELEE_WEAPONS = {
    "Club": {"damage": "1d4 bludgeoning", "properties": ["Light"]},
    "Dagger": {"damage": "1d4 piercing", "properties": ["Finesse", "Light", "Thrown (20/60)"]},
    "Greatclub": {"damage": "1d8 bludgeoning", "properties": ["Two-Handed"]},
    "Handaxe": {"damage": "1d6 slashing", "properties": ["Light", "Thrown (20/60)"]},
    "Javelin": {"damage": "1d6 piercing", "properties": ["Thrown (30/120)"]},
    "Light Hammer": {"damage": "1d4 bludgeoning", "properties": ["Light", "Thrown (20/60)"]},
    "Mace": {"damage": "1d6 bludgeoning", "properties": []},
    "Quarterstaff": {"damage": "1d6 bludgeoning (1d8 two-handed)", "properties": ["Versatile"]},
    "Sickle": {"damage": "1d4 slashing", "properties": ["Light"]},
    "Spear": {"damage": "1d6 piercing (1d8 two-handed)", "properties": ["Thrown (20/60)", "Versatile"]},
}

SIMPLE_RANGED_WEAPONS = {
    "Light Crossbow": {"damage": "1d8 piercing", "properties": ["Ammunition (80/320)", "Loading", "Two-Handed"]},
    "Dart": {"damage": "1d4 piercing", "properties": ["Finesse", "Thrown (20/60)"]},
    "Shortbow": {"damage": "1d6 piercing", "properties": ["Ammunition (80/320)", "Two-Handed"]},
    "Sling": {"damage": "1d4 bludgeoning", "properties": ["Ammunition (30/120)"]},
}

MARTIAL_MELEE_WEAPONS = {
    "Battleaxe": {"damage": "1d8 slashing (1d10 two-handed)", "properties": ["Versatile"]},
    "Flail": {"damage": "1d8 bludgeoning", "properties": []},
    "Glaive": {"damage": "1d10 slashing", "properties": ["Heavy", "Reach", "Two-Handed"]},
    "Greataxe": {"damage": "1d12 slashing", "properties": ["Heavy", "Two-Handed"]},
    "Greatsword": {"damage": "2d6 slashing", "properties": ["Heavy", "Two-Handed"]},
    "Halberd": {"damage": "1d10 slashing", "properties": ["Heavy", "Reach", "Two-Handed"]},
    "Lance": {"damage": "1d12 piercing", "properties": ["Reach", "Special (disadvantage vs. targets within 5 ft. while mounted)"]},
    "Longsword": {"damage": "1d8 slashing (1d10 two-handed)", "properties": ["Versatile"]},
    "Maul": {"damage": "2d6 bludgeoning", "properties": ["Heavy", "Two-Handed"]},
    "Morningstar": {"damage": "1d8 piercing", "properties": []},
    "Pike": {"damage": "1d10 piercing", "properties": ["Heavy", "Reach", "Two-Handed"]},
    "Rapier": {"damage": "1d8 piercing", "properties": ["Finesse"]},
    "Scimitar": {"damage": "1d6 slashing", "properties": ["Finesse", "Light"]},
    "Shortsword": {"damage": "1d6 piercing", "properties": ["Finesse", "Light"]},
    "Trident": {"damage": "1d6 piercing (1d8 two-handed)", "properties": ["Thrown (20/60)", "Versatile"]},
    "War Pick": {"damage": "1d8 piercing", "properties": []},
    "Warhammer": {"damage": "1d8 bludgeoning (1d10 two-handed)", "properties": ["Versatile"]},
    "Whip": {"damage": "1d4 slashing", "properties": ["Finesse", "Reach"]},
}

MARTIAL_RANGED_WEAPONS = {
    "Blowgun": {"damage": "1 piercing", "properties": ["Ammunition (25/100)", "Loading"]},
    "Hand Crossbow": {"damage": "1d6 piercing", "properties": ["Ammunition (30/120)", "Light", "Loading"]},
    "Heavy Crossbow": {"damage": "1d10 piercing", "properties": ["Ammunition (100/400)", "Heavy", "Loading", "Two-Handed"]},
    "Longbow": {"damage": "1d8 piercing", "properties": ["Ammunition (150/600)", "Heavy", "Two-Handed"]},
    "Net": {"damage": "none (restrains target)", "properties": ["Special", "Thrown (5/15)"]},
}

WEAPON_CATEGORIES = {
    "Simple Melee": SIMPLE_MELEE_WEAPONS,
    "Simple Ranged": SIMPLE_RANGED_WEAPONS,
    "Martial Melee": MARTIAL_MELEE_WEAPONS,
    "Martial Ranged": MARTIAL_RANGED_WEAPONS,
}


def weapon_reference_block(proficiencies: set) -> str:
    """proficiencies is a set of {"Simple", "Martial"} -- only categories in
    at least one of those groups are included, so a Simple-only class never
    gets the Martial tables injected into its prompt."""
    lines = ["WEAPONS REFERENCE (damage dice/type -- narration precision only, never read aloud as a stat block):"]
    included = False
    for category_name, table in WEAPON_CATEGORIES.items():
        group = "Martial" if category_name.startswith("Martial") else "Simple"
        if group not in proficiencies:
            continue
        for name, info in table.items():
            props = f" -- {', '.join(info['properties'])}" if info["properties"] else ""
            lines.append(f"  {name} ({category_name}): {info['damage']}{props}")
            included = True
    return "\n".join(lines) if included else ""
