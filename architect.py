"""The hidden, one-time "adventure architect" LLM call.

Turns adventure.draft_outline()'s raw random picks into one cohesive,
well-written adventure skeleton. Never shown to the player -- it's the DM's
private planning notes, consumed by dm.py via adventure.adventure_prompt_block().
"""

import json
import re

import adventure
import ollama_client

REQUIRED_TOP_LEVEL_KEYS = ("title", "tone", "setting", "hook", "antagonist", "beats", "climax", "resolution_options")
REQUIRED_ANTAGONIST_KEYS = {"name", "role", "motivation", "plan"}

_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _build_messages(draft: dict, character_name: str, classes: list, blurb: str, n_beats: int) -> list:
    classes_text = "/".join(classes)
    system = (
        "You are an adventure architect for a solo, text-based tabletop-style game. "
        "You will be given randomly chosen story building blocks that may not "
        "naturally fit together. Your job is to reconcile them into ONE cohesive, "
        "well-written adventure outline -- reinterpret a clashing element rather "
        "than ignoring it (e.g. 'a flooded coastal ruin' + 'a corrupt church "
        "official' could become a sea-flooded, half-drowned theocracy).\n\n"
        "This outline is never shown to the player directly -- it is the Dungeon "
        "Master's private planning notes, so it can be blunt and utilitarian as "
        "long as it is usable. The character's name, classes, and personality "
        "blurb should flavor the hook (a Rogue's hook should differ from a "
        "Paladin's). Beats are a flexible plan, not a script -- the DM running "
        "the actual game will adapt them as needed.\n\n"
        "Respond with ONLY a single valid JSON object (no markdown code fences, "
        "no commentary before or after) with exactly this shape:\n"
        "{\n"
        '  "title": string,\n'
        '  "tone": string,\n'
        '  "setting": string,\n'
        '  "hook": string,\n'
        '  "antagonist": {"name": string, "role": string, "motivation": string, "plan": string},\n'
        f'  "beats": [string, ... exactly {n_beats} entries],\n'
        '  "climax": string,\n'
        '  "resolution_options": [string, string]\n'
        "}"
    )
    user = (
        f"SETTING: {draft['setting_archetype']}\n"
        f"ANTAGONIST ARCHETYPE: {draft['antagonist_archetype']}\n"
        f"ANTAGONIST MOTIVATION: {draft['antagonist_motivation']}\n"
        f"HOOK TYPE: {draft['hook_type']}\n"
        f"TWIST TYPE (weave in as a later complication, not the hook): {draft['twist_type']}\n"
        f"CLIMAX TYPE: {draft['climax_type']}\n"
        f"TONE: {draft['tone']}\n\n"
        f"PLAYER CHARACTER: {character_name}, {classes_text}.\n"
        f'Personality/background: "{blurb}"\n\n'
        f'Write exactly {n_beats} beat(s) in "beats".'
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _extract_json_object(text: str) -> str | None:
    text = _JSON_FENCE_RE.sub("", text.strip()).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return text[start : end + 1]


def _parse_adventure_json(raw_text: str, n_beats: int) -> dict | None:
    candidate = _extract_json_object(raw_text)
    if candidate is None:
        return None
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    if any(key not in parsed for key in REQUIRED_TOP_LEVEL_KEYS):
        return None

    antagonist = parsed["antagonist"]
    if not isinstance(antagonist, dict) or not REQUIRED_ANTAGONIST_KEYS.issubset(antagonist):
        return None

    beats = parsed["beats"]
    if not isinstance(beats, list) or not beats:
        return None
    beats = [str(b) for b in beats]
    if len(beats) < n_beats:
        beats = beats + [beats[-1]] * (n_beats - len(beats))
    elif len(beats) > n_beats:
        beats = beats[:n_beats]
    parsed["beats"] = beats

    resolution_options = parsed["resolution_options"]
    if not isinstance(resolution_options, list) or not resolution_options:
        return None
    parsed["resolution_options"] = [str(r) for r in resolution_options]

    return parsed


def _fallback_adventure(draft: dict, n_beats: int) -> dict:
    """Deterministic, no-prose-polish assembly used only if the model fails
    to produce valid JSON twice in a row. Never crashes the game."""
    setting = draft["setting_archetype"]
    antagonist_desc = draft["antagonist_archetype"]
    motivation = draft["antagonist_motivation"]
    beats = [
        f"Act {i}: the party investigates {setting} and uncovers signs of {antagonist_desc}."
        for i in range(1, n_beats + 1)
    ]
    return {
        "title": f"Trouble in {setting}",
        "tone": draft["tone"],
        "setting": setting,
        "hook": f"In {setting}, {draft['hook_type']}.",
        "antagonist": {
            "name": "The Unnamed Foe",
            "role": antagonist_desc,
            "motivation": motivation,
            "plan": f"Driven by being {motivation}, they are moving toward {draft['climax_type']}.",
        },
        "beats": beats,
        "climax": draft["climax_type"],
        "resolution_options": [
            "The party stops the plot in time.",
            "The party arrives too late and must contain the damage.",
        ],
    }


def build_adventure(
    draft: dict,
    character_name: str,
    classes: list,
    blurb: str,
    preset: str,
    model: str = None,
) -> dict:
    model = model or ollama_client.DEFAULT_MODEL
    n_beats = adventure.PRESETS[preset]["beats"]
    messages = _build_messages(draft, character_name, classes, blurb, n_beats)

    raw = ollama_client.call_ollama(messages, model)
    parsed = _parse_adventure_json(raw, n_beats)

    if parsed is None:
        retry_messages = messages + [
            {"role": "assistant", "content": raw},
            {
                "role": "user",
                "content": (
                    "That was not valid JSON. Respond with ONLY a single valid "
                    "JSON object matching the schema above -- no commentary, "
                    "no markdown code fences."
                ),
            },
        ]
        raw2 = ollama_client.call_ollama(retry_messages, model)
        parsed = _parse_adventure_json(raw2, n_beats)

    if parsed is None:
        parsed = _fallback_adventure(draft, n_beats)

    parsed["total_beats"] = n_beats
    parsed["current_beat"] = 0
    parsed.setdefault("adaptations", [])
    return parsed
