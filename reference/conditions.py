"""SRD conditions -- one-line mechanical/narrative effects, for the DM's own
consistency (a "restrained" enemy should behave differently than a "prone"
one). Never quoted to the player as rules text."""

CONDITIONS = {
    "Blinded": "Can't see; automatically fails sight-based checks; attacks against it have advantage, its own attacks have disadvantage.",
    "Charmed": "Can't attack the charmer or target them with harmful abilities; the charmer has advantage on social checks against it.",
    "Deafened": "Can't hear; automatically fails hearing-based checks.",
    "Frightened": "Disadvantage on checks/attacks while the source of its fear is in sight; can't willingly move closer to it.",
    "Grappled": "Speed becomes 0; ends if the grappler is incapacitated or the target is removed from their reach.",
    "Incapacitated": "Can't take actions or reactions.",
    "Invisible": "Can't be seen without magic/special sense; treated as heavily obscured; attacks against it have disadvantage, its own attacks have advantage.",
    "Paralyzed": "Incapacitated and can't move or speak; auto-fails Strength/Dexterity saves; attacks against it have advantage and any hit within 5 feet is a critical.",
    "Petrified": "Transformed to stone; incapacitated, can't move or speak, unaware of surroundings; resistant to all damage; immune to poison and disease.",
    "Poisoned": "Disadvantage on attack rolls and ability checks.",
    "Prone": "Can only crawl to move (or stand, ending the condition); melee attacks against it have advantage if the attacker is within 5 feet, otherwise disadvantage; its own attacks have disadvantage.",
    "Restrained": "Speed becomes 0; attacks against it have advantage, its own attacks have disadvantage; disadvantage on Dexterity saves.",
    "Stunned": "Incapacitated, can't move, can speak only falteringly; auto-fails Strength/Dexterity saves; attacks against it have advantage.",
    "Unconscious": "Incapacitated, can't move or speak, unaware of surroundings, drops what it's holding, falls prone; auto-fails Strength/Dexterity saves; attacks against it have advantage and any hit within 5 feet is a critical.",
    "Exhaustion": "Six cumulative levels, each worsening (disadvantage on ability checks, speed halved, disadvantage on attacks/saves, HP maximum halved, speed reduced to 0); level 6 is death.",
}


def conditions_block() -> str:
    lines = ["CONDITIONS REFERENCE (mechanical effects -- for your own consistency, never read aloud as rules text):"]
    for name, effect in CONDITIONS.items():
        lines.append(f"  {name}: {effect}")
    return "\n".join(lines)
