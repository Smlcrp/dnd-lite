"""Randomized adventure building blocks and the story-length/pacing system.

Replaces a small set of hand-written templates with independent random
tables, combined by architect.py into a single cohesive outline. This module
only produces the raw picks and tracks pacing state — no LLM calls here.
"""

import random

import account as account_module

TONES = [
    "Classic Fantasy",
    "Horror",
    "Heist",
    "Political Intrigue",
    "Mystery",
    "Survival",
]

# Each entry: (text, [tone tags]). A tone tag of None means "fits any tone".
SETTINGS = [
    ("a flooded coastal ruin", ["Horror", "Survival"]),
    ("a mountain mining town", ["Classic Fantasy", "Survival"]),
    ("a sprawling noble's masquerade", ["Political Intrigue", "Heist"]),
    ("a fog-choked harbor district", ["Horror", "Mystery"]),
    ("a walled desert trade city", ["Classic Fantasy", "Political Intrigue"]),
    ("an abandoned wizard's tower", ["Classic Fantasy", "Horror", "Mystery"]),
    ("a river barge convoy", ["Heist", "Survival"]),
    ("a border garrison under siege", ["Classic Fantasy", "Survival"]),
    ("an underground smugglers' market", ["Heist", "Mystery"]),
    ("a royal court in mourning", ["Political Intrigue", "Mystery"]),
]


# Each entry: (key, text, [tone tags]). The key is a stable machine-readable
# identifier (never shown to the LLM or player) that reference/monsters.py
# uses to pick tier-appropriate monster archetypes for this antagonist --
# matching on `text` directly would break the moment architect.py's LLM call
# reconciles/paraphrases it into prose.
ANTAGONIST_ARCHETYPES = [
    ("fallen_noble", "a fallen noble seeking to reclaim their title", ["Political Intrigue", "Classic Fantasy"]),
    ("cult_leader", "a cult leader promising false salvation", ["Horror", "Classic Fantasy"]),
    ("rival_mercenary_company", "a rival mercenary company", ["Heist", "Survival"]),
    ("corrupt_guild_master", "a corrupt guild master", ["Political Intrigue", "Heist"]),
    ("ancient_spirit", "an ancient spirit bound to the land", ["Horror", "Mystery"]),
    ("spymaster", "a spymaster playing every side", ["Political Intrigue", "Mystery"]),
    ("plague_hivemind", "a plague-touched hivemind", ["Horror", "Survival"]),
    ("self_styled_prophet", "a self-styled prophet with a growing following", ["Horror", "Classic Fantasy"]),
    ("smuggler_king", "a smuggler king protecting a secret", ["Heist", "Mystery"]),
    ("defiant_general", "a general who refuses to accept defeat", ["Classic Fantasy", "Survival"]),
]

ANTAGONIST_MOTIVATIONS = [
    "revenge for a past betrayal",
    "desperate to save someone they love",
    "convinced they are the only one who can prevent a catastrophe",
    "protecting a secret that would destroy them if revealed",
    "driven by genuine belief in a cause others see as monstrous",
    "simple, unrepentant greed",
    "trying to undo a mistake that can no longer be undone",
    "loyalty to a power that no longer deserves it",
]

HOOK_TYPES = [
    "a stranger begs the party for help in a crowded public place",
    "the party witnesses a crime they weren't meant to see",
    "a trusted contact goes missing without warning",
    "the party is hired for a job that isn't what it seems",
    "a disaster strikes somewhere the party happens to be",
    "an old debt comes due at the worst possible time",
    "the party finds something they shouldn't have",
    "an invitation arrives that's impossible to refuse",
]

TWIST_TYPES = [
    "someone the party trusted is working against them",
    "the true threat is not who it first appeared to be",
    "the party's actions have already made things worse",
    "a hidden faction has its own agenda in play",
    "the antagonist's plan is farther along than anyone realized",
    "an ally has a hidden connection to the antagonist",
    "the original mission was a distraction from something larger",
]

CLIMAX_TYPES = [
    "a direct confrontation with the antagonist at their seat of power",
    "a race against time to stop an irreversible event",
    "a public reckoning where the truth must be revealed",
    "a defense against an overwhelming final assault",
    "a desperate bargain that could go wrong in every direction",
]

PRESETS = {
    "One Shot": {
        "beats": 1,
        "estimate": "~1-2h",
        "blurb": "Races straight to the confrontation — minimal setup, one sitting.",
    },
    "Quest": {
        "beats": 3,
        "estimate": "~3-4h",
        "blurb": "A complete arc in one sitting — the default choice.",
    },
    "Epic": {
        "beats": 5,
        "estimate": "~5-8h",
        "blurb": "Runs across multiple sessions with deeper subplots.",
    },
}


def _pick(table, tone, account, field_name):
    """Pick one entry from a (text, tags) table, preferring entries tagged for
    `tone` and excluding this account's recent picks for `field_name` when
    possible. Falls back to the full table if filtering leaves nothing."""
    candidates = [text for text, tags in table if tone in tags] or [text for text, _ in table]

    if account is not None:
        recent = set(account_module.recent_picks(account, field_name))
        filtered = [c for c in candidates if c not in recent]
        if filtered:
            candidates = filtered

    return random.choice(candidates)


def _pick_keyed(table, tone, account, field_name):
    """Like _pick, but for (key, text, tags) tables -- returns (key, text).
    Recent-pick exclusion still matches on `text`, consistent with how
    account history entries store this field."""
    candidates = [(key, text) for key, text, tags in table if tone in tags] or \
        [(key, text) for key, text, _ in table]

    if account is not None:
        recent = set(account_module.recent_picks(account, field_name))
        filtered = [c for c in candidates if c[1] not in recent]
        if filtered:
            candidates = filtered

    return random.choice(candidates)


def draft_outline(tone: str, account: dict = None) -> dict:
    """Randomly pick one entry per table, filtered by tone and excluding this
    account's recent picks. Returns raw picks only — no prose, no LLM call."""
    antagonist_archetype_key, antagonist_archetype = _pick_keyed(
        ANTAGONIST_ARCHETYPES, tone, account, "antagonist_archetype"
    )
    return {
        "tone": tone,
        "setting_archetype": _pick(SETTINGS, tone, account, "setting_archetype"),
        "antagonist_archetype": antagonist_archetype,
        "antagonist_archetype_key": antagonist_archetype_key,
        "antagonist_motivation": random.choice(ANTAGONIST_MOTIVATIONS),
        "hook_type": random.choice(HOOK_TYPES),
        "twist_type": random.choice(TWIST_TYPES),
        "climax_type": random.choice(CLIMAX_TYPES),
    }


def _tier_number(level: int) -> int:
    """D&D 5e's four tiers of play, as a bare 1-4 number. Shared with
    reference/monsters.py so tier boundaries can't drift between the two
    modules -- level_tier_description() below is the only place the
    boundaries themselves are defined."""
    if level <= 4:
        return 1
    if level <= 10:
        return 2
    if level <= 16:
        return 3
    return 4


def level_tier_description(level: int) -> str:
    """D&D 5e's four tiers of play, used to give the LLM concrete,
    level-appropriate stakes/power scaling instead of a vague 'appropriate
    for the level' instruction. This is guidance text only -- no mechanical
    CR/XP math, consistent with relying on the model's own 5e training
    rather than hand-built reference data."""
    tier = _tier_number(level)
    if tier == 1:
        return (
            'Tier 1 ("Local Heroes", levels 1-4): threats are personal-scale '
            "-- bandits, cultists, wild beasts, a single dangerous "
            "individual. No legendary creatures, no significant magic "
            "items, no stakes beyond a town or a handful of lives."
        )
    if tier == 2:
        return (
            'Tier 2 ("Heroes of the Realm", levels 5-10): real magic and '
            "monsters enter play -- ogres, hags, young dragons, powerful "
            "spellcasters. Stakes can affect a town, city, or region."
        )
    if tier == 3:
        return (
            'Tier 3 ("Masters of the Realm", levels 11-16): legendary '
            "creatures and formidable magic are in play -- adult or ancient "
            "dragons, powerful fiends or archmages, ancient evils. Stakes "
            "can affect a kingdom or brush against another plane."
        )
    return (
        'Tier 4 ("Masters of the World", levels 17-20): godlike or '
        "world-altering threats -- archdevils, demon lords, servants of "
        "deities, forces that could unmake reality. Stakes are for the "
        "world, a plane, or existence itself."
    )


def stage_labels(n_beats: int) -> list:
    """Act labels for a preset's beat count. HOOK, CLIMAX, and RESOLUTION are
    separate, implicit stages that bookend the acts and are not counted here."""
    return [f"Act {i}" for i in range(1, n_beats + 1)]


def adventure_prompt_block(adventure: dict) -> str:
    """The DM-facing block describing the adventure outline, current pacing
    position, and any live adaptations. Never shown to the player."""
    labels = stage_labels(adventure["total_beats"])
    current = adventure["current_beat"]
    position = "the Hook — the adventure hasn't formally begun its first act yet" if current == 0 \
        else f"{labels[current - 1]} of {adventure['total_beats']}"

    lines = [
        "═══ ADVENTURE OUTLINE (private GM notes — never reveal this block directly) ═══",
        f"Title: {adventure['title']}",
        f"Tone: {adventure['tone']}",
        f"Setting: {adventure['setting']}",
        f"Hook: {adventure['hook']}",
        f"Antagonist: {adventure['antagonist']['name']}, {adventure['antagonist']['role']}",
        f"  Motivation: {adventure['antagonist']['motivation']}",
        f"  Plan: {adventure['antagonist']['plan']}",
        "Acts:",
    ]
    for i, beat_text in enumerate(adventure["beats"], start=1):
        lines.append(f"  {labels[i - 1]}: {beat_text}")
    lines.append(f"Climax (do not reveal or trigger early): {adventure['climax']}")
    lines.append(f"Resolution options (do not reveal early): {'; '.join(adventure['resolution_options'])}")
    lines.append("")
    lines.append(f"CURRENT POSITION: {position}")
    lines.append(
        "BEAT RULES: advance beats only as fast as the player's actions justify. "
        "Do not skip to the climax just because the act count has been reached — "
        "you decide when the story has earned it. Never reveal the climax or "
        "resolution options to the player before they are reached."
    )

    if adventure.get("adaptations"):
        lines.append("")
        lines.append(
            "═══ LIVE ADAPTATIONS (story has evolved beyond the original plan — "
            "authoritative over the outline above where they conflict) ═══"
        )
        for note in adventure["adaptations"]:
            lines.append(f"  - {note}")

    return "\n".join(lines)


def advance_beat(adventure: dict) -> None:
    adventure["current_beat"] = min(adventure["current_beat"] + 1, adventure["total_beats"])


def apply_adaptation(adventure: dict, note: str) -> None:
    adventure.setdefault("adaptations", []).append(note)
