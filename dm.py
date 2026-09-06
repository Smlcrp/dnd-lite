"""The narrating Dungeon Master: builds the system prompt each turn, calls
Ollama, and parses the LLM's structured tags out of the narration.
"""

import re

import adventure
import ollama_client
import session as session_module

HISTORY_WINDOW = 12
BEGIN_ADVENTURE = "[BEGIN ADVENTURE]"

ABSOLUTE_RULE = (
    "ABSOLUTE RULE: Never write the player's dialogue, decisions, or emotions "
    "for them. Narrate the world and every other character's reactions, then "
    "stop and hand control back."
)

NARRATION_RULES = (
    "NARRATION STYLE:\n"
    '- Write in second person ("you"), vivid and concrete, 3-5 sentences per turn.\n'
    "- React directly to what the player just did or said.\n"
    '- Never refer to yourself as "the DM" or break the fourth wall.\n'
    '- Never mention dice, numbers, or the word "check" unless calling for a '
    "roll (see SELF-REPORTED DICE below).\n"
    "- End every turn at a choice point -- leave the player something to decide."
)

PLAYER_AGENCY_RULES = (
    "PLAYER AGENCY (never violate these):\n"
    "- Never write the player's spoken dialogue for them.\n"
    "- Never assign the player emotions or internal decisions they did not state.\n"
    "- Never resolve a social exchange on the player's behalf.\n"
    "- Never extend the player's stated action into further unstated decisions.\n"
    "- Always end at a natural pause, not mid-action."
)

SELF_REPORTED_DICE_BLOCK = (
    "SELF-REPORTED DICE -- HOW THIS GAME WORKS:\n"
    "This app does not roll dice and does not know the player's character "
    "sheet, ability scores, or bonuses. The player rolls physical or digital "
    'dice themselves and tells you the result in plain language (e.g. "I '
    'rolled a 14", "got a 17 on Perception", "natural 20", "rolled a 3").\n\n'
    "WHEN TO CALL FOR A ROLL: only when the outcome is genuinely uncertain "
    "and meaningful -- obscure lore, deception, perception of hidden things, "
    "risky physical action. Do not call for a roll for common knowledge, "
    "willing NPCs, or information already established in play.\n\n"
    "HOW TO ASK: speak like a real DM at the table. Name the skill, never a "
    "target number.\n"
    '  RIGHT: "That door looks tricky -- give me a Perception check."\n'
    '  WRONG: "Roll a DC 15 Perception check." (never state a DC -- you have '
    "no way to verify it)\n"
    "Then emit the tag [CHECK: SkillName] on its own line before a "
    "one-sentence in-motion narration of the attempt -- do not reveal the "
    "outcome yet.\n\n"
    "INTERPRETING THE PLAYER'S REPORTED RESULT: treat whatever number the "
    "player reports as their final, already-modified result -- never ask "
    "them to add anything, never do arithmetic yourself. Judge the number "
    "against these bands, adjusting slightly for how hard the specific "
    "situation clearly is:\n"
    '  20 or "nat 20"/"critical" -> GREAT SUCCESS: vivid extra detail, an '
    "unexpected advantage.\n"
    "  15-19 -> SUCCESS: clean, clear, complete.\n"
    "  10-14 -> PARTIAL SUCCESS: it works, but with a complication or cost.\n"
    "  5-9   -> FAILURE: it doesn't work -- make the failure interesting, "
    "not a dead end.\n"
    '  1-4 or "nat 1" -> CRITICAL FAILURE: notable, often complicating, but '
    "never punish the player for a bad roll they couldn't control.\n"
    "If the player reports no clear number, ask for it before narrating the "
    'outcome. Never say "DC", "band", or "tier" in your actual narration.'
)

TAG_RULES = (
    "TAGS: on their own line, hidden from the player, use exactly these "
    "tags when appropriate (nothing else):\n"
    "  [SCENE: Location Name] -- the location has changed.\n"
    "  [CHECK: SkillName] -- you are calling for a roll (see above).\n"
    "  [BEAT] -- the current story act is complete.\n"
    "  [CLIMAX] -- the story has reached its final confrontation.\n"
    "  [BREAK] -- this feels like a natural stopping point.\n"
    "  [ADAPT: one or two sentence note] -- the player's choice meaningfully "
    "diverged from the planned direction; describe how the story now bends. "
    "Use this SPARINGLY -- only for genuine, meaningful divergence, not "
    "every minor choice -- and preserve the antagonist and theme where "
    "still plausible rather than discarding the whole outline."
)

FINAL_REMINDER = (
    "Reminder: never write the player's dialogue, decisions, or emotions "
    "for them. Narrate, then stop."
)


def _scene_anchor(last_dm_text: str) -> str:
    excerpt = last_dm_text.strip()
    if len(excerpt) > 400:
        window = excerpt[:400]
        cut = max(window.rfind(". "), window.rfind(".\n"), window.rfind("? "), window.rfind("! "))
        excerpt = window[: cut + 1] if cut != -1 else window + "..."
    return (
        "SCENE IN PROGRESS -- DO NOT RESET:\n"
        "The adventure is already underway. The most recent narration was:\n"
        f'"{excerpt}"\n'
        "CONTINUITY RULE: continue from exactly this moment. Do not "
        "re-introduce the setting or the character, and do not repeat "
        "earlier narration -- move the scene forward."
    )


class DungeonMaster:
    def __init__(self, model: str = ollama_client.DEFAULT_MODEL):
        self.model = model

    def warmup(self) -> None:
        ollama_client.warmup(self.model)

    def _build_system_prompt(self, session: dict) -> str:
        blocks = [ABSOLUTE_RULE]

        classes_text = "/".join(session["classes"])
        blocks.append(
            "PLAYER CHARACTER (as described by the player -- take this at "
            f'face value, do not invent stats): {session["character_name"]}, '
            f'{classes_text}. "{session["blurb"]}"'
        )

        blocks.append(NARRATION_RULES)
        blocks.append(PLAYER_AGENCY_RULES)
        blocks.append(SELF_REPORTED_DICE_BLOCK)
        blocks.append(TAG_RULES)
        blocks.append(adventure.adventure_prompt_block(session["adventure"]))

        if session.get("story_mode"):
            blocks.append(
                "STORY MODE: no checks are called for -- narrate all "
                "outcomes through story logic only. The player is always "
                "alone."
            )

        history = session["history"]
        if history:
            last_dm_turn = next((h["text"] for h in reversed(history) if h["role"] == "dm"), None)
            if last_dm_turn:
                blocks.append(_scene_anchor(last_dm_turn))
            blocks.append(
                "The adventure is in progress -- do not re-establish the "
                "setting or restart the scene."
            )
        else:
            blocks.append(
                "This is the opening turn. Open the scene using the "
                "adventure's hook and the player character's blurb -- "
                "establish the setting and the inciting moment now."
            )

        blocks.append(FINAL_REMINDER)
        return "\n\n".join(blocks)

    def _messages_for_ollama(self, session: dict, player_input: str) -> list:
        messages = [{"role": "system", "content": self._build_system_prompt(session)}]
        for turn in session["history"][-HISTORY_WINDOW:]:
            role = "assistant" if turn["role"] == "dm" else "user"
            messages.append({"role": role, "content": turn["text"]})
        messages.append({"role": "user", "content": player_input})
        return messages

    def _parse_tags(self, raw_text: str) -> tuple:
        events = []

        for m in re.finditer(r"\[SCENE:\s*([^\]]+)\]", raw_text, re.IGNORECASE):
            events.append({"type": "scene_change", "location": m.group(1).strip()})
        for m in re.finditer(r"\[CHECK:\s*([^\]]+)\]", raw_text, re.IGNORECASE):
            events.append({"type": "check_requested", "skill": m.group(1).strip()})
        for m in re.finditer(r"\[ADAPT:\s*([^\]]+)\]", raw_text, re.IGNORECASE):
            events.append({"type": "adapt", "note": m.group(1).strip()})
        if re.search(r"\[BEAT\]", raw_text, re.IGNORECASE):
            events.append({"type": "beat_complete"})
        if re.search(r"\[CLIMAX\]", raw_text, re.IGNORECASE):
            events.append({"type": "climax_reached"})
        if re.search(r"\[BREAK\]", raw_text, re.IGNORECASE):
            events.append({"type": "break_suggested"})

        clean = re.sub(r"\[(SCENE|CHECK|ADAPT):[^\]]*\]", "", raw_text, flags=re.IGNORECASE)
        clean = re.sub(r"\[(BEAT|CLIMAX|BREAK)\]", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\n{3,}", "\n\n", clean).strip()
        return clean, events

    def _apply_events(self, session: dict, events: list) -> None:
        for event in events:
            if event["type"] == "scene_change":
                session["location"] = event["location"]
            elif event["type"] in ("beat_complete", "climax_reached"):
                adventure.advance_beat(session["adventure"])
            elif event["type"] == "adapt":
                adventure.apply_adaptation(session["adventure"], event["note"])
            # check_requested / break_suggested: no state mutation in v1;
            # the CLI may surface them to the player directly.

    def _finalize_turn(self, session: dict, player_input: str, raw: str) -> tuple:
        clean, events = self._parse_tags(raw)
        session["scene"] = clean
        self._apply_events(session, events)
        if player_input != BEGIN_ADVENTURE:
            session_module.add_history(session, "player", player_input)
        session_module.add_history(session, "dm", clean)
        return clean, events

    def respond(self, session: dict, player_input: str) -> dict:
        messages = self._messages_for_ollama(session, player_input)
        raw = ollama_client.call_ollama(messages, self.model)
        clean, events = self._finalize_turn(session, player_input, raw)
        return {"narration": clean, "events": events}

    def respond_stream(self, session: dict, player_input: str):
        messages = self._messages_for_ollama(session, player_input)
        chunks = []
        for chunk in ollama_client.stream_ollama(messages, self.model):
            chunks.append(chunk)
            yield {"token": chunk}

        raw = "".join(chunks)
        clean, events = self._finalize_turn(session, player_input, raw)
        yield {"done": True, "narration": clean, "events": events}

    def recap(self, session: dict) -> str:
        last_dm_turn = next(
            (h["text"] for h in reversed(session["history"]) if h["role"] == "dm"), None
        )
        if last_dm_turn is None:
            return "No previous narration to recap."
        messages = [
            {
                "role": "system",
                "content": (
                    "Summarize the following Dungeon Master narration in 2-3 "
                    'sentences as a "Previously..." recap for a returning '
                    "player. Do not add new events."
                ),
            },
            {"role": "user", "content": last_dm_turn},
        ]
        return ollama_client.call_ollama(messages, self.model)
