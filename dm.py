"""The narrating Dungeon Master: builds the system prompt each turn, calls
Ollama, and parses the LLM's structured tags out of the narration.
"""

import re

import adventure
import ollama_client
import reference
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
    "still plausible rather than discarding the whole outline.\n"
    "  [STATUS: free-text note] -- the player just self-reported a major "
    "state change (HP hit 0, a buff/condition landed, a limited resource "
    "was spent) after you asked them directly; record their own words, "
    "never invented or computed by you.\n"
    "  [ENCOUNTER: free-text note] -- snapshot the CURRENT state of any "
    "active fight in your own words (an enemy bloodied, defeated, or fled; "
    "a new enemy joined). OVERWRITE the previous snapshot each time rather "
    "than appending to it, and once combat fully resolves emit "
    "[ENCOUNTER: none] so a stale note doesn't confuse a much later turn."
)

FIFTH_EDITION_KNOWLEDGE_BLOCK = (
    "5E KNOWLEDGE: you have full working knowledge of Dungeons & Dragons 5th "
    "edition -- classes, leveling, class features, typical capabilities at "
    "each level. Draw on that knowledge directly: flavor the character's "
    "actions and options the way a real level-appropriate member of their "
    "class would act, and calibrate the danger and tone of encounters to "
    "their level. A small hand-built reference dataset below sharpens "
    "specific facts (weapons, conditions, class features, spells, monster "
    "stats) where precision beats fuzzy recall -- it is narration grounding "
    "only, never a visible rules layer, and it is always filtered to just "
    "this character and this adventure, never dumped in full."
)

REFERENCE_DATA_GUIDANCE = (
    "REFERENCE DATA (below): concrete 5e facts for your OWN narration "
    "precision -- weapon damage, condition effects, class features, spell "
    "effects, monster stats. Use these to ground details naturally (a "
    "longsword's edge, what Rage grants at this level, a bandit captain's "
    "parry) -- NEVER read a stat block aloud, NEVER quote an exact number "
    "or rule to the player as if it were a DC (e.g. \"that's +1d4 from "
    "Bless\"), and NEVER let this override the SELF-REPORTED DICE bands "
    "above."
)

STATUS_AND_ENCOUNTER_BLOCK = (
    "STATUS & ENCOUNTER CHECK-INS: this app tracks no HP or resources as "
    "numbers -- the player's own sheet is authoritative for their "
    "character, and you are the only source of truth for enemies.\n"
    "- PLAYER STATUS: when something major happens to the player character "
    "(drops to 0 HP, a significant buff/condition lands, a big limited "
    "resource like their last spell slot or Rage is spent), ask them "
    "directly what their sheet now shows. Once they answer in their own "
    "words, emit [STATUS: their words, briefly].\n"
    "- ENCOUNTER STATE: during a fight, snapshot enemy state in your own "
    "words at meaningful moments (an enemy roughly half health, defeated, "
    "or fled; a new enemy arrives) with [ENCOUNTER: ...]. Always overwrite "
    "the previous note, never append to it, and emit [ENCOUNTER: none] "
    "once the fight is fully over.\n"
    "Never invent or compute either -- only record what has just been "
    "established, and don't overuse these -- major changes only."
)

def _encounter_scaling_block(level: int) -> str:
    return (
        "ENCOUNTER SCALING: keep danger matched to the character's D&D 5th "
        "Edition tier of play (or their current narrative level, if you "
        "have already narrated a level-up earlier in this adventure):\n"
        f"  {adventure.level_tier_description(level)}\n\n"
        "Be concrete about it: at a higher tier, threats should command real "
        "magical or supernatural power and failure should carry consequences "
        "reaching beyond a single life or building -- not just a bigger "
        "version of the same mundane plan. This matters just as much as "
        "staying true to the established setting and antagonist, and the "
        "two must always agree: never let a threat's power override what "
        "makes narrative sense for the scene -- keep the setting as the "
        "stage and raise what is really happening within it (the local "
        "threat is backed by something larger, corruption runs deeper than "
        "it first appeared) rather than parachuting in a "
        "mechanically-appropriate but tonally incongruous threat."
    )

LEVEL_PROGRESSION_BLOCK = (
    "LEVEL PROGRESSION: you may narrate the character leveling up when the "
    "story's events warrant it, paced the way a real D&D campaign advances "
    "(roughly every session or major milestone, not every turn) -- do not "
    "be shy about it, but keep the pacing realistic. This is flavor only: "
    "the app does not track XP or store an updated level number. The "
    "player's own physical or external character sheet is the authoritative "
    "record, exactly like self-reported dice rolls -- treat any level-up as "
    "theirs to record, not yours to tally."
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
            f'a level {session["level"]} {classes_text}. "{session["blurb"]}"'
        )

        last_status = session_module.get_flag(session, "last_known_status")
        if last_status:
            blocks.append(f"LAST KNOWN PLAYER STATUS (self-reported, may be stale): {last_status}")

        encounter_state = session_module.get_flag(session, "current_encounter_state")
        if encounter_state and str(encounter_state).lower() != "none":
            blocks.append(f"CURRENT ENCOUNTER STATE (your own last snapshot): {encounter_state}")

        blocks.append(NARRATION_RULES)
        blocks.append(PLAYER_AGENCY_RULES)
        blocks.append(SELF_REPORTED_DICE_BLOCK)
        blocks.append(FIFTH_EDITION_KNOWLEDGE_BLOCK)
        blocks.append(_encounter_scaling_block(session["level"]))
        blocks.append(REFERENCE_DATA_GUIDANCE)
        blocks.append(reference.general_reference_block(session["classes"]))
        class_block = reference.class_features_block(session["classes"], session["level"])
        if class_block:
            blocks.append(class_block)
        spell_block = reference.spell_block(session["classes"], session["level"])
        if spell_block:
            blocks.append(spell_block)
        monster_block = reference.monster_block(session["level"], session["adventure"])
        if monster_block:
            blocks.append(monster_block)
        blocks.append(LEVEL_PROGRESSION_BLOCK)
        blocks.append(STATUS_AND_ENCOUNTER_BLOCK)
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
        for m in re.finditer(r"\[STATUS:\s*([^\]]+)\]", raw_text, re.IGNORECASE):
            events.append({"type": "status_report", "note": m.group(1).strip()})
        for m in re.finditer(r"\[ENCOUNTER:\s*([^\]]+)\]", raw_text, re.IGNORECASE):
            events.append({"type": "encounter_update", "note": m.group(1).strip()})
        if re.search(r"\[BEAT\]", raw_text, re.IGNORECASE):
            events.append({"type": "beat_complete"})
        if re.search(r"\[CLIMAX\]", raw_text, re.IGNORECASE):
            events.append({"type": "climax_reached"})
        if re.search(r"\[BREAK\]", raw_text, re.IGNORECASE):
            events.append({"type": "break_suggested"})

        clean = re.sub(r"\[(SCENE|CHECK|ADAPT|STATUS|ENCOUNTER):[^\]]*\]", "", raw_text, flags=re.IGNORECASE)
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
            elif event["type"] == "status_report":
                session_module.set_flag(session, "last_known_status", event["note"])
            elif event["type"] == "encounter_update":
                session_module.set_flag(session, "current_encounter_state", event["note"])
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
