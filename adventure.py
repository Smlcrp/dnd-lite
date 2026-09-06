"""Randomized adventure building blocks and the story-length/pacing system.

Replaces a small set of hand-written templates with independent random
tables, combined by architect.py into a single cohesive outline. This module
only produces the raw picks and tracks pacing state — no LLM calls here.
"""

import random

import profile as profile_module

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

ANTAGONIST_ARCHETYPES = [
    ("a fallen noble seeking to reclaim their title", ["Political Intrigue", "Classic Fantasy"]),
    ("a cult leader promising false salvation", ["Horror", "Classic Fantasy"]),
    ("a rival mercenary company", ["Heist", "Survival"]),
    ("a corrupt guild master", ["Political Intrigue", "Heist"]),
    ("an ancient spirit bound to the land", ["Horror", "Mystery"]),
    ("a spymaster playing every side", ["Political Intrigue", "Mystery"]),
    ("a plague-touched hivemind", ["Horror", "Survival"]),
    ("a self-styled prophet with a growing following", ["Horror", "Classic Fantasy"]),
    ("a smuggler king protecting a secret", ["Heist", "Mystery"]),
    ("a general who refuses to accept defeat", ["Classic Fantasy", "Survival"]),
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


def _pick(table, tone, profile, field_name):
    """Pick one entry from a (text, tags) table, preferring entries tagged for
    `tone` and excluding this profile's recent picks for `field_name` when
    possible. Falls back to the full table if filtering leaves nothing."""
    candidates = [text for text, tags in table if tone in tags] or [text for text, _ in table]

    if profile is not None:
        recent = set(profile_module.recent_picks(profile, field_name))
        filtered = [c for c in candidates if c not in recent]
        if filtered:
            candidates = filtered

    return random.choice(candidates)


def draft_outline(tone: str, profile: dict | None = None) -> dict:
    """Randomly pick one entry per table, filtered by tone and excluding this
    profile's recent picks. Returns raw picks only — no prose, no LLM call."""
    return {
        "tone": tone,
        "setting_archetype": _pick(SETTINGS, tone, profile, "setting_archetype"),
        "antagonist_archetype": _pick(ANTAGONIST_ARCHETYPES, tone, profile, "antagonist_archetype"),
        "antagonist_motivation": random.choice(ANTAGONIST_MOTIVATIONS),
        "hook_type": random.choice(HOOK_TYPES),
        "twist_type": random.choice(TWIST_TYPES),
        "climax_type": random.choice(CLIMAX_TYPES),
    }


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
