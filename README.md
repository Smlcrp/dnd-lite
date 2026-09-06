# DND Lite

A lightweight, text-based AI Dungeon Master. It narrates a D&D adventure for a character you already have — no in-app character creation or stat management.

**Status: implemented**, including accounts/login and character leveling. All modules described below are built, with 93 unit tests (Ollama mocked) and manually-verified end-to-end playthroughs against a real local Ollama server. This README doubles as the architecture reference for the design it was built from.

## Context

[dndgame](https://github.com/Smlcrp/dndgame) grew into a full MVC D&D 5e game — [character builder](https://github.com/Smlcrp/dndgame/tree/0a79c9d5ff6002fff8c8d1f515818f06e8b26afe/character_builder), [combat engine](https://github.com/Smlcrp/dndgame/blob/0a79c9d5ff6002fff8c8d1f515818f06e8b26afe/models/combat.py), [XP/leveling](https://github.com/Smlcrp/dndgame/blob/0a79c9d5ff6002fff8c8d1f515818f06e8b26afe/models/progression.py#L17-L20), [companions](https://github.com/Smlcrp/dndgame/blob/0a79c9d5ff6002fff8c8d1f515818f06e8b26afe/models/companions.py#L219-L419), [Flask+JS web frontend](https://github.com/Smlcrp/dndgame/tree/0a79c9d5ff6002fff8c8d1f515818f06e8b26afe/views/web), [Electron shell](https://github.com/Smlcrp/dndgame/blob/0a79c9d5ff6002fff8c8d1f515818f06e8b26afe/electron/main.js#L16), [TTS](https://github.com/Smlcrp/dndgame/blob/0a79c9d5ff6002fff8c8d1f515818f06e8b26afe/models/narrator.py) — and became too much scope for one person, compounded by local GPU limits (a 6–7B Ollama model already strains an 8GB card).

DND Lite is a deliberate reset: a lightweight, text-based AI Dungeon Master. The player brings their own D&D character from outside the app (paper or D&D Beyond) and just plays — no character creation, no stat tracking, no combat engine, no leveling, no companions. v1 is a CLI where a local Ollama model narrates an adventure, the player self-reports dice rolls in plain language, and sessions save/resume to disk.

A key design goal, adapted from concepts in dndgame: that project used [8 hand-written, fixed adventure templates](https://github.com/Smlcrp/dndgame/blob/0a79c9d5ff6002fff8c8d1f515818f06e8b26afe/models/adventure.py#L29-L206) — fine for a demo, but a repeat player would eventually recognize and memorize all 8, killing the surprise. The player also shouldn't have to hand-author their own plot (that would spoil it for themselves). The design below generates a different, hidden adventure skeleton every time, keeps it secret from the player (revealed only through play), and lets the story adapt when the player goes off-script.

## Design Plan

### Confirmed decisions
- **LLM backend**: local Ollama, no provider-abstraction layer.
- **Interface**: CLI first. Web UI is an explicit future phase — no Flask/web scaffolding now.
- **Dice**: self-reported by the player in natural language; the DM narrates qualitative outcomes, never does arithmetic.
- **Persistence**: sessions (one adventure's live state) save/resume via JSON. Additionally, **accounts** persist across many adventures (see below). **Only one unfinished adventure can exist per account at a time** — starting a new adventure while one is pending replaces it. Manual `save` plus autosave-per-turn let the player stop and resume anytime.
- **Adventure generation**: randomized building blocks, reconciled into cohesive prose by a hidden one-time LLM "architect" call, with the DM able to adapt the plan mid-story via an explicit tag.
- **Player input at setup**: character name + class(es) (multiclass-aware) + starting level (1–20) + a short freeform blurb, plus a broad tone/genre pick. No plot details are ever chosen by the player.
- **Accounts**: multiple named accounts, each gated by a username + password (hashed, stdlib-only). Character details are asked fresh at the start of every new adventure — unless the account opted into a saved **default character** at creation time, which skips that prompt every time (used for the `test` account, but any account can opt in).
- **D&D 5e knowledge**: no hand-built class/level reference data. The DM prompt tells the LLM it has full working 5e knowledge and to draw on that directly for flavor and encounter calibration — zero data tables, zero added token cost. A short 13-class name list validates input client-side only (never sent to the model).
- **Leveling**: narrated, not tracked. The player brings a starting level as a flavor/calibration snapshot; the DM may narrate level-ups paced like a real campaign, but the app never stores or recalculates a level number — the player's own physical/external character sheet stays authoritative, exactly like self-reported dice.

### File structure

```
DND-Lite/
├── main.py            # entry point: python main.py
├── cli.py             # game loop, login/account-creation menus, streaming display
├── dm.py              # DungeonMaster: main narration prompt, tag parsing (incl. [ADAPT:])
├── architect.py        # hidden one-time LLM call: reconciles random picks into a cohesive adventure skeleton
├── adventure.py        # building-block tables, draft_outline(), adventure_prompt_block(), advance_beat(), apply_adaptation()
├── account.py           # account CRUD, login verification, default-character storage, adventure history (for repeat-avoidance)
├── auth.py              # password hashing/verification (stdlib pbkdf2_hmac, no new dependency)
├── ollama_client.py     # shared call_ollama()/warmup() used by dm.py and architect.py; resolves DEFAULT_MODEL (fallback / DND_LITE_MODEL env var)
├── session.py          # per-adventure session dict schema + JSON persistence (one active file per account)
├── sessions/           # one file per account: sessions/<account_slug>.json (gitignored, created at runtime)
├── accounts/            # account files (gitignored, created at runtime)
├── tests/
│   ├── conftest.py
│   ├── test_session.py
│   ├── test_account.py
│   ├── test_auth.py
│   ├── test_adventure.py
│   ├── test_architect.py   # JSON parsing/fallback logic, Ollama mocked
│   ├── test_cli.py         # login/account-creation flow, class/level validation, tag filter
│   └── test_dm.py          # prompt assembly + tag parsing (incl. [ADAPT:]), Ollama mocked
├── requirements.txt   # requests>=2.31.0, pytest>=7.0.0 — nothing else
├── .gitignore          # sessions/, accounts/, __pycache__/, *.pyc
├── CLAUDE.md
└── README.md
```

Rationale for the two new small modules: `ollama_client.py` exists only because now *two* things call Ollama (the main DM and the one-time architect pass) — factoring the HTTP/streaming plumbing out avoids duplicating it. `architect.py` is kept separate from `dm.py` because it's a fundamentally different call: one-shot, structured-output (JSON), no streaming, no player-facing narration — mixing it into the `DungeonMaster` class would blur two different responsibilities.

### Authentication (`auth.py`)

Pure stdlib password hashing — no new dependency:
```python
def hash_password(password: str) -> tuple[str, str]:
    """Returns (salt_hex, hash_hex). os.urandom(16) salt,
    hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 200_000)."""

def verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    """Recomputes the hash and compares with hmac.compare_digest
    (constant-time)."""
```

This is a local, single-player CLI tool, not a networked service — the goal is "don't store plaintext passwords," not defending against a sophisticated attacker with file access. No password complexity rules, no lockout policy.

### Player accounts (`account.py`)

An account is a persistent record of one person's credentials and play history, separate from any single adventure's session file. Multiple named accounts are supported so more than one player/character history can be tracked on the same machine.

```python
def slugify(name: str) -> str
def create_account(account_name: str, password: str) -> dict
def verify_login(account: dict, password: str) -> bool
def set_default_character(account: dict, name: str, classes: list[str], level: int, blurb: str) -> None
def get_default_character(account: dict) -> dict | None
def load_account(account_name: str) -> dict
def save_account(account: dict) -> None
def list_accounts() -> list[str]
def start_new_adventure(account: dict, entry: dict) -> None
def complete_current_adventure(account: dict) -> None
def current_adventure_entry(account: dict) -> dict | None
def recent_picks(account: dict, field: str, n: int = 5) -> list[str]
```

`start_new_adventure` enforces the one-active-adventure invariant on the *history* side: if the account's most recent adventure entry has `status == "in_progress"`, it's flipped to `"abandoned"` (its metadata is kept for repeat-avoidance — only the live playthrough is discarded, not the historical record), then the new entry is appended as `"in_progress"` and the account is saved. `complete_current_adventure` flips the current in-progress entry to `"completed"` (called by the CLI on `[CLIMAX]`→`[BREAK]`). `current_adventure_entry` returns the in-progress entry if one exists, else `None` — used by the CLI to show "Resume '<title>'..." without needing to open the session file.

**`default_character`** is optional and `None` unless the account opted in at creation time. If set, the CLI skips the character-detail prompts on every new adventure and reuses it — this is a general feature any account can use, not a special case hardcoded to one account name. Its immediate purpose is the `test` account (see "Running" below): username `test`, password `test`, default character `Adventurer` the `Fighter`, level 3.

Schema (`accounts/<slug>.json`):
```python
{
    "account_name": "Sam",
    "created_at": ...,
    "password_salt": "<hex>",
    "password_hash": "<hex>",
    "default_character": {                    # or None
        "name": "Adventurer",
        "classes": ["Fighter"],
        "level": 3,
        "blurb": "",
    },
    "adventures": [
        {
            "title": "...",
            "character_name": "Kessa",
            "classes": ["Ranger", "Rogue"],   # list, not stat-leveled — multiclass is just a flavor list here
            "level": 5,                        # starting level for this adventure, never updated afterward
            "blurb": "cautious but kind, grew up on the road",
            "tone": "Horror",
            "setting_archetype": "...",
            "antagonist_archetype": "...",
            "hook_type": "...",
            "twist_type": "...",
            "climax_type": "...",
            "started_at": ...,
            "status": "in_progress" | "completed" | "abandoned",
        },
        ...
    ],
}
```

`recent_picks(account, "antagonist_archetype", n=5)` — used by `adventure.draft_outline()` to exclude a table category's last N picks across this account's adventures, so back-to-back sessions for the same player don't reuse the same antagonist type, setting, hook, twist, or climax shape. If every option in a table has been used recently (small table, prolific player), fall back to the full table rather than raising an error.

`start_new_adventure` is called once at adventure creation, so repeat-avoidance works even for adventures that later get abandoned. `complete_current_adventure` is called when the DM emits `[CLIMAX]` followed by `[BREAK]`, or the player explicitly ends the story.

### Session schema (`session.py`)

**Only one unfinished adventure can exist per account at a time.** Rather than a list of named saves, each account has a single active-session slot: `sessions/<account_slug>.json`. Starting a new adventure while one is pending overwrites this file (after the CLI confirms with the player — see CLI flow below); there is no session-name picker to maintain, since there's never more than one file to choose from.

```python
def empty_session(account_name, character_name, classes, level, blurb) -> dict:
    return {
        "account_name": account_name,
        "character_name": character_name,
        "classes": classes,          # list[str], e.g. ["Ranger", "Rogue"]
        "level": level,               # starting level (1-20), a flavor/calibration snapshot -- never updated
        "blurb": blurb,               # freeform flavor text
        "location": "",
        "scene": "",                  # last raw DM narration, feeds the scene anchor
        "history": [],                # [{"role": "player"|"dm", "text": str}]
        "flags": {},                  # arbitrary story-state
        "adventure": None,            # from architect.build_adventure()
        "story_mode": False,
        "created_at": ...,
        "updated_at": ...,
    }

def session_path(account_name) -> Path
def save_session(session) -> None              # overwrites sessions/<account_slug>.json
def load_active_session(account_name) -> dict | None   # None if no unfinished adventure
def has_active_session(account_name) -> bool
def delete_session(account_name) -> None       # called right before a replacement is created
def add_history(session, role, text) -> None
def set_flag(session, key, value=True) / get_flag(session, key, default=False)
```

The adventure's own generated `title` (from the architect pass, once it runs) is what the CLI displays when offering to resume — there's no separate player-chosen session name to collect at setup, since it would be redundant with the single-slot design.

### Adventure building blocks & draft outline (`adventure.py`)

Replaces dndgame's [8 fixed templates](https://github.com/Smlcrp/dndgame/blob/0a79c9d5ff6002fff8c8d1f515818f06e8b26afe/models/adventure.py#L29-L206) with independent random tables, so combinations vastly outnumber any hand-written set:

```python
SETTINGS = [...]              # e.g. "a flooded coastal ruin", "a mountain mining town", ...
ANTAGONIST_ARCHETYPES = [...] # e.g. "a fallen noble", "a cult leader", "a rival mercenary company", ...
ANTAGONIST_MOTIVATIONS = [...]
HOOK_TYPES = [...]            # e.g. "a stranger begs for help", "a crime the party witnesses", ...
TWIST_TYPES = [...]           # a mid-story complication/reveal
CLIMAX_TYPES = [...]
TONES = ["Classic Fantasy", "Horror", "Heist", "Political Intrigue", ...]  # player-facing picker

PRESETS = {
    "One Shot": {"beats": 1, "estimate": "~1-2h", "blurb": "Races straight to the confrontation — minimal setup, one sitting."},
    "Quest":    {"beats": 3, "estimate": "~3-4h", "blurb": "A complete arc in one sitting — the default choice."},
    "Epic":     {"beats": 5, "estimate": "~5-8h", "blurb": "Runs across multiple sessions with deeper subplots."},
}

def draft_outline(tone: str, account: dict) -> dict:
    """Randomly pick one entry per table, filtered by tone tags and excluding
    this account's recent picks (via account.recent_picks). Returns the RAW
    picks only — no prose yet. This is pure Python, fully unit-testable,
    no LLM call."""

def level_tier_description(level: int) -> str:
    """D&D 5e's four tiers of play (see "Tier-of-play scaling" below) --
    guidance text only, no CR/XP math. Used by both architect.py and
    dm.py to give the LLM concrete, level-appropriate stakes/power scaling."""

def stage_labels(n_beats: int) -> list[str]:
    """Maps a preset's beat count to act labels, e.g. n=1 -> ["Act 1"],
    n=3 -> ["Act 1", "Act 2", "Act 3"], n=5 -> 5 acts. HOOK, CLIMAX, and
    RESOLUTION are separate, implicit stages that bookend the acts —
    they are not counted in n_beats."""

def adventure_prompt_block(adventure: dict) -> str
def advance_beat(adventure: dict) -> None   # increments current_beat, capped at total_beats
def apply_adaptation(adventure: dict, note: str) -> None   # appends to adventure["adaptations"]
```

Each table entry can optionally carry tone tags (e.g. an antagonist archetype tagged `["Horror", "Classic Fantasy"]`) so `draft_outline` filters candidates to the player's chosen tone before randomizing — keeps the tone picker meaningful without the player ever seeing the underlying tables.

#### Adventure length & pacing

Adapted from concepts in dndgame's [One Shot / Quest / Epic system](https://github.com/Smlcrp/dndgame/blob/0a79c9d5ff6002fff8c8d1f515818f06e8b26afe/models/adventure.py#L212-L216), updated for the new randomized-outline design:

- The preset picked at setup determines `total_beats` (1, 3, or 5) — this is the number of **acts** the architect writes into `adventure["beats"]`. The overall arc is always `HOOK → Act 1 … Act N → CLIMAX → RESOLUTION`; hook/climax/resolution are separate fields, not counted among the acts.
- `adventure["current_beat"]` starts at `0` (still in the hook) and increments by 1 each time the DM emits `[BEAT]`, capped at `total_beats`. Reaching `total_beats` doesn't auto-trigger the climax — the DM decides when the story has earned it and emits `[CLIMAX]` explicitly.
- `adventure_prompt_block()` tells the DM its current position using `stage_labels()` (e.g. "You are in **Act 2 of 3**") plus explicit **beat rules**: don't advance beats faster than the player's actions justify, don't skip straight to the climax just because `current_beat == total_beats`, and don't reveal the climax or resolution options to the player before they're reached.
- One Shot's single beat means the "act" is really just a short rising-action stretch before the climax — the architect is told to write a punchier, more urgent single beat rather than a full 3-part arc compressed into one entry.
- Epic's 5 beats are explicitly flagged to the architect as spanning **multiple play sessions** (i.e., expect save/resume between acts) — its beat descriptions should each be substantial enough to sustain a full sitting on their own, and subplots (a secondary thread not required for the main climax) are encouraged for beats 2–4.

### Adventure architect pass (`architect.py`)

A single hidden LLM call made once, at adventure creation, that turns the raw random picks into one cohesive, well-written outline — and is explicitly told to reconcile any picks that don't naturally fit together (reinterpreting rather than ignoring a table entry, e.g. "a flooded coastal ruin" + "a corrupt church official" becomes a sea-flooded, half-drowned theocracy).

```python
def build_adventure(draft: dict, character_name: str, classes: list[str],
                     level: int, blurb: str, preset: str) -> dict:
    """One-shot, non-streaming Ollama call via ollama_client.call_ollama().
    Prompts for a JSON object:
      {
        "title": str,
        "tone": str,
        "setting": str,
        "hook": str,               # the opening scenario, read/paraphrased in the DM's first turn
        "antagonist": {"name": str, "role": str, "motivation": str, "plan": str},
        "beats": [str, ...],       # length == preset's beat count (the acts; see "Adventure length & pacing")
        "climax": str,
        "resolution_options": [str, str],
        "adaptations": []          # starts empty; filled in during play via [ADAPT:]
      }
    build_adventure() also sets "total_beats" (= len(beats)) and "current_beat" = 0
    on the returned dict once parsed, so adventure.py's stage-tracking helpers
    have state to work with immediately (the LLM is not asked to produce these
    two — they're derived/initialized in code, not prompted for).
    Parses the response as JSON. On parse failure: retry once with a stricter
    'output ONLY valid JSON' reminder; on second failure, fall back to a
    deterministic plain-sentence assembly directly from the raw picks (no
    prose polish, but never crashes the game).
    """
```

The system prompt for this call is explicit that: (1) the character's name/classes/blurb should flavor the hook (e.g. a Rogue's hook differs from a Paladin's), (2) the output is never shown to the player directly — it's the DM's private notes — so it can be as blunt/mechanical as needed as long as it's usable, (3) beats are a flexible plan, not a script — the main DM will adapt them as needed, (4) **encounter scaling** — the antagonist's true power and the climax's stakes must match the character's D&D 5e tier of play (see below), and must agree with the reconciled setting: the setting stays the stage, but what's really happening within it should scale to the tier (a mountain mining town can hide a mundane bandit crew at Tier 1, or a noble's pact with an ancient horror at Tier 3 — same location, different truth).

#### Tier-of-play scaling (`adventure.level_tier_description()`)

The one deliberately hand-written piece of D&D-specific text in the whole app — four short, well-known tier descriptions from the 5e Dungeon Master's Guide, used as concrete prompt scaffolding rather than a lookup table for mechanical math (no CR/XP computed anywhere):

| Level range | Tier |
|---|---|
| 1–4 | Tier 1, "Local Heroes" — personal-scale threats, no legendary creatures |
| 5–10 | Tier 2, "Heroes of the Realm" — real magic/monsters, town-to-region stakes |
| 11–16 | Tier 3, "Masters of the Realm" — legendary creatures, kingdom-to-planar stakes |
| 17–20 | Tier 4, "Masters of the World" — godlike threats, world/planar stakes |

Both `architect.py` (adventure creation) and `dm.py` (ongoing narration, via `_encounter_scaling_block(session["level"])`) inject the matching tier description directly into their prompts, with an explicit instruction to be concrete about the escalation (real magical/supernatural power, consequences beyond a single life or building) rather than just scaling up a mundane plan. This was tightened after a real-Ollama test showed a vaguer "escalate appropriately" instruction wasn't reliably producing a difference between a level 1 and a level 15 outline — naming the actual tier fixed it.

### DM design (`dm.py`)

```python
class DungeonMaster:
    def _build_system_prompt(self, session) -> str
    def _messages_for_ollama(self, session, player_input) -> list[dict]
    def _parse_tags(self, raw_text) -> tuple[str, list[dict]]
    def respond(self, session, player_input) -> dict
    def respond_stream(self, session, player_input) -> Generator
    def recap(self, session) -> str
```

`_call_ollama`/`warmup` move to `ollama_client.py`, shared with `architect.py`.

System prompt blocks, in order:

1. **Absolute rule header** — never write the player's dialogue/decisions/emotions for them.
2. **Character block** — name, **level**, classes (multiclass listed as-is), and blurb, at face value, no invented stats.
3. **Narration rules** — second person, vivid, 3–5 sentences, end each turn at a choice point.
4. **Player-agency rules** — never write the player's dialogue, emotions, or unstated decisions; always end at a natural pause.
5. **Self-reported dice block** — qualitative bands, no DC spoken, no arithmetic (see below).
6. **5e knowledge block** — tells the model it has full working D&D 5e knowledge (classes, leveling, class features) and should draw on that training directly for flavor and encounter calibration. No hand-built data — this is a couple of sentences, zero added token cost.
7. **Encounter scaling block** — `dm._encounter_scaling_block(session["level"])`, injecting the concrete tier-of-play description (see "Tier-of-play scaling" above) plus an instruction to escalate the *truth* of the setting to match the tier rather than swapping in a mechanically-right-but-tonally-wrong threat.
8. **Level progression block** — the DM may narrate level-ups paced like a real campaign ("should happen all the time," per design intent, just kept realistic), but this is flavor only: the app never stores or recalculates a level number. The player's own physical/external character sheet is authoritative, exactly like self-reported dice.
9. **Tag rules** — the tag set below, including `[ADAPT:]`.
10. **Adventure block** — `adventure.adventure_prompt_block(session["adventure"])`: the **original outline** (title/setting/hook/antagonist/beats/climax), the **current stage** (`stage_labels()` position + beat rules — don't rush, don't skip to the climax early, don't reveal climax/resolution), and, if any exist, a **live adaptations** section listed last and marked as authoritative over the original where they conflict.
11. **Story Mode block** — only if `session["story_mode"]`.
12. **Scene anchor** — last ~400 chars of the prior DM turn, truncated on a sentence boundary, "SCENE IN PROGRESS — DO NOT RESET." This is the key trick that keeps a small local model from losing the thread.
13. **Opening vs. continuing instruction** — no history → open with the adventure hook + character blurb; scene anchor present → never re-establish setting.
14. **Final reminder footer** — one-line reiteration of the absolute rule.

No new tag or session/adventure state field was introduced for level-ups — deliberately. Continuity relies on the same history-window + scene-anchor mechanism already used for everything else, consistent with "shouldn't be tracked by the game."

#### Self-reported dice

The app has no character sheet, so it can't compute real DCs or apply modifiers. The prompt teaches the model to:
- Decide when a roll is warranted (common knowledge/willing NPCs/already-established info need no roll; obscure lore, deception, hidden perception, risky physical action need a roll).
- Call for it in natural language, naming the skill but **never a DC**: *"Give me a Perception check"*, not *"Roll a DC 15 Perception check."*
- Emit `[CHECK: SkillName]` before the in-motion narration (outcome not yet revealed).
- Treat whatever number the player reports as their final, already-modified result — never do arithmetic, never ask them to add anything.
- Map the reported number to fixed qualitative bands: **20/"nat 20"** → great success; **15–19** → success; **10–14** → partial success with a complication; **5–9** → failure (interesting, not a dead end); **1–4/"nat 1"** → critical failure (fair, not punishing). If no clear number is given, ask for it before narrating.
- Never say "DC," "band," or "tier" in the actual narration.

#### Tag set

| Tag | Purpose |
|---|---|
| `[SCENE: Location]` | location changed |
| `[CHECK: SkillName]` | a roll was called for (no DC) |
| `[BEAT]` | current story beat complete |
| `[CLIMAX]` | story reached final confrontation |
| `[BREAK]` | natural session pause point |
| `[ADAPT: short note]` | the player's choice meaningfully diverged from the planned direction; the enclosed 1–2 sentence note describes how the story now bends. Hidden from the player. Stripped from display and passed to `adventure.apply_adaptation()`, which appends it to `session["adventure"]["adaptations"]` so every future prompt sees the up-to-date direction. |

The prompt instructs the model to use `[ADAPT:]` sparingly — only on a genuine, meaningful divergence, not every minor choice — and to preserve the antagonist/theme where still plausible rather than discarding the whole outline.

Dropped (mechanics-only, not applicable here): `[COMBAT:]`, `[XP:]`, `[GOLD:]`, `[ITEM:]`, `[COMPANION:]`, `[ACTION:]`, `[BONUS:]`.

History windowing: system prompt + last ~12 turns + current input.

### CLI flow (`cli.py`, `main.py`)

**Startup — login or create an account**:
1. Prompt for account name.
2. **Existing account**: prompt for password via `getpass.getpass` (masked, no echo), verify with `account.verify_login`. Wrong password → re-prompt or bail back to the account-name prompt; no hard lockout (local single-player tool, not a networked service).
3. **No such account**: confirm — *"No account named '<name>' — create one? [y/N]"*. If yes: password + a confirmation retype (must match), then *"Save a default character for this account, so you skip character setup on every adventure? [y/N]"* — if yes, collect name/class(es)/level/blurb once via `account.set_default_character`.

Then the menu depends on whether the account has an unfinished adventure (`session.has_active_session(account_name)`, backed by `account.current_adventure_entry(account)` for the display title/date):

- **Unfinished adventure exists**: `1) Resume "<title>" (started <date>)`, `2) Start a new adventure`, `3) Quit`. Choosing (2) prompts a confirmation — *"This will discard your unfinished adventure '<title>'. Continue? [y/N]"* — before proceeding, since replacing it is destructive and irreversible.
- **No unfinished adventure**: `1) New adventure`, `2) Quit`.

**New adventure** (after any confirmation above):
- **If the account has a `default_character`**: skip straight to the tone/length pickers, printing *"Using your saved character: <name> the <classes> (Level <level>)"*.
- **Otherwise**:
  1. Character name.
  2. Class(es) — a single prompt accepting multiclass input (e.g. `Fighter/Rogue`), validated against the 13 official 5e classes (case-insensitive, re-prompts on an unrecognized name) and stored as a list.
  3. Starting level (1–20), re-prompts on non-numeric or out-of-range input.
  4. Freeform blurb (a sentence or two of flavor/personality).
- Then, for every new adventure regardless of path: tone picker (Classic Fantasy / Horror / Heist / Political Intrigue / …), length preset — One Shot / Quest / Epic, shown with each preset's `blurb` + `estimate` from `adventure.PRESETS`.
- `adventure.draft_outline(tone, account)` → raw picks (instant, no LLM call).
- `architect.build_adventure(draft, character_name, classes, blurb, preset)` → full skeleton. Print a "The DM is preparing your adventure…" message while this call runs (it's a real, possibly multi-second, Ollama call).
- If a previous unfinished adventure existed: `session.delete_session(account_name)` first. Then `account.start_new_adventure(account, {...})` (marks any prior in-progress entry `abandoned`, appends the new one as `in_progress`, now also carrying `level`), `session.save_session(session)` immediately.
- `dm.warmup()`, then an opening DM call with a synthetic `"[BEGIN ADVENTURE]"` input.

**Resume**: `session.load_active_session(account_name)` → `dm.recap(session)`. No picker needed — there is at most one file to load.

**Main loop**: `save`/`quit`/`exit` handled locally, everything else sent to `respond_stream` with tokens printed as they arrive **through a live tag filter** (`_TagFilter` — strips `[TAG: ...]` sequences character-by-character from the streamed tokens, since `respond_stream` only strips tags from the final assembled text, not the individual tokens it yields), **autosave after every turn** (this plus the explicit `save` command is what lets the player stop and resume at any point, not just at `quit`), `RuntimeError` around dropped-Ollama-server errors. On `[CLIMAX]` followed by `[BREAK]` (or explicit quit-after-climax), call `account.complete_current_adventure(account)` — the session file itself is left in place (a completed adventure can still be replayed/reviewed via `resume` until the player starts a new one, at which point it's replaced like any other unfinished-vs-new transition).

### Build order

1. `session.py` and `account.py` — schemas + persistence, unit-testable in isolation with `tmp_path`. No interdependency between them beyond `session["account_name"]` being a plain string. Tests cover the replace-on-new-adventure path explicitly (`save_session` → `delete_session` → `save_session` again leaves exactly one file) and `account.start_new_adventure` correctly flipping a prior `in_progress` entry to `abandoned`.
2. `auth.py` — password hash/verify round-trip, wrong-password rejection, unique salt per call.
3. `adventure.py` — building-block tables, `draft_outline` (including recent-picks exclusion via a mocked/fake account), `stage_labels` (all 3 preset beat counts), `adventure_prompt_block`, `advance_beat` (capping at `total_beats`), `apply_adaptation`.
4. `ollama_client.py` — thin shared HTTP/streaming wrapper, tested with `requests` mocked.
5. `architect.py` — prompt construction + JSON parsing + retry + deterministic fallback; all three paths (valid JSON, one retry then success, fallback) tested with Ollama mocked.
6. `dm.py` prompt builder — all blocks including the character/level block, 5e-knowledge and level-progression blocks, and the adventure/adaptations split; block presence/absence tested.
7. `dm.py` tag parser — all 6 tags (including `[ADAPT:]`) plus no-tags and whitespace/casing variants.
8. `dm.py` streaming/respond/recap — Ollama mocked in tests.
9. `cli.py` + `main.py` — login/account-creation flow (`getpass` mocked in tests alongside `input`), class/level validation, default-character skip path, new/resume flows, main loop, autosave, completion status updates.
10. The `test` account created (via the normal CLI flow, not a special script): username `test`, password `test`, default character Adventurer/Fighter/level 3.
11. Manual + real playtests against local Ollama: two fresh adventures with the same tone don't reuse the same antagonist archetype; the architect pass produces coherent output even when picks clash; an off-script player choice produces a sensible `[ADAPT:]` that persists across subsequent turns; quit-and-resume recap continuity; starting a new adventure with one already pending shows the confirmation and correctly discards the old one; the `test` account skips character entry and shows the saved character; a normal account still asks for character + level each adventure; wrong password rejected, correct password accepted; class validation rejects a bogus name and accepts valid multiclass input; the DM's narration reflects the character's level appropriately.
12. `CLAUDE.md`, `README.md`, `requirements.txt`, `.gitignore` — finalized last.

### Explicit non-goals

No combat engine, no character stats/HP, no companions, no XP counter, no mechanical class-feature engine, no hand-built 5e reference data, no TTS, no D&D Beyond import, no Flask/web/Electron, no provider-abstraction layer, no password complexity rules or account lockout policy (unnecessary for a local single-player tool). Level is a stored *snapshot*, set once per adventure (or inherited from a default character) and never mechanically recalculated by this app. A future web phase could reuse dndgame's [SSE-streaming](https://github.com/Smlcrp/dndgame/blob/0a79c9d5ff6002fff8c8d1f515818f06e8b26afe/views/web/api.py#L375-L409) + [live tag-filtering](https://github.com/Smlcrp/dndgame/blob/0a79c9d5ff6002fff8c8d1f515818f06e8b26afe/views/web/static/js/scenes/GameScene.js#L173-L190) approach conceptually, but no scaffolding for it now.

### Verification

- `pytest tests/` — 93 unit tests pass (session/account persistence round-trips, password hashing, one-active-adventure replace behavior, draft-outline repeat-avoidance, architect JSON parsing + fallback, prompt block assembly, tag parsing incl. `[ADAPT:]`, login/account-creation flow, class/level validation) without a live Ollama server.
- Manual + real playtests per build-order step 11, all passing against a real local Ollama server.

## Running

```
python -m venv .venv && .venv/bin/pip install -r requirements.txt
ollama pull llama3.1:8b   # the default -- see "Choosing a model" below
ollama serve
.venv/bin/python main.py
```

Run the test suite (Ollama mocked, no live server needed) with:
```
.venv/bin/python -m pytest tests/
```

### Test account

A `test`/`test` account exists for quick manual testing, with a saved default character (Adventurer, Fighter, level 3) that skips character setup on every new adventure. It's created the same way any account is — via the normal login flow's "create one?" prompt — not by a special script; if `accounts/test.json` doesn't exist on your machine, log in as `test`, say yes to creating it, use password `test`, and say yes to saving a default character with those values.

### Choosing a model

`llama3.1:8b` is the built-in default -- it runs acceptably (~30-60s/turn) on an 8-core CPU with no GPU, and reliably follows the tag/JSON instructions the game depends on. If you have a capable GPU, a larger model (e.g. `nous-hermes2:10.7b`) will be both faster and higher quality. Three ways to switch, in increasing precedence:

1. **Edit the fallback** — change `_FALLBACK_MODEL` in `ollama_client.py`.
2. **Environment variable** — set `DND_LITE_MODEL` before launching:
   ```
   DND_LITE_MODEL=nous-hermes2:10.7b .venv/bin/python main.py
   ```
3. **`--model` flag** — overrides everything else for a single run:
   ```
   .venv/bin/python main.py --model nous-hermes2:10.7b
   ```

Whichever model you pick, `ollama pull` it first. The chosen model applies to both the main narration (`dm.py`) and the one-time adventure architect pass (`architect.py`).
