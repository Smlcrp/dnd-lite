# DND Lite

A lightweight, text-based AI Dungeon Master. It narrates a D&D adventure for a character you already have — no in-app character creation or stat management.

**Status: v1 implemented.** All modules described below are built, with 69 unit tests (Ollama mocked) and a manually-verified end-to-end playthrough against a real local Ollama server. This README doubles as the architecture reference for the design it was built from.

## Context

[dndgame](https://github.com/Smlcrp/dndgame) grew into a full MVC D&D 5e game — character builder, combat engine, XP/leveling, companions, Flask+JS web frontend, Electron shell, TTS — and became too much scope for one person, compounded by local GPU limits (a 6–7B Ollama model already strains an 8GB card).

DND Lite is a deliberate reset: a lightweight, text-based AI Dungeon Master. The player brings their own D&D character from outside the app (paper or D&D Beyond) and just plays — no character creation, no stat tracking, no combat engine, no leveling, no companions. v1 is a CLI where a local Ollama model narrates an adventure, the player self-reports dice rolls in plain language, and sessions save/resume to disk.

A key design goal, adapted from concepts in dndgame: that project used 8 hand-written, fixed adventure templates — fine for a demo, but a repeat player would eventually recognize and memorize all 8, killing the surprise. The player also shouldn't have to hand-author their own plot (that would spoil it for themselves). The design below generates a different, hidden adventure skeleton every time, keeps it secret from the player (revealed only through play), and lets the story adapt when the player goes off-script.

## Design Plan

### Confirmed decisions
- **LLM backend**: local Ollama, no provider-abstraction layer.
- **Interface**: CLI first. Web UI is an explicit future phase — no Flask/web scaffolding now.
- **Dice**: self-reported by the player in natural language; the DM narrates qualitative outcomes, never does arithmetic.
- **Persistence**: sessions (one adventure's live state) save/resume via JSON. Additionally, **player profiles** persist across many adventures (see below). **Only one unfinished adventure can exist per profile at a time** — starting a new adventure while one is pending replaces it. Manual `save` plus autosave-per-turn let the player stop and resume anytime.
- **Adventure generation**: randomized building blocks, reconciled into cohesive prose by a hidden one-time LLM "architect" call, with the DM able to adapt the plan mid-story via an explicit tag.
- **Player input at setup**: character name + class(es) (multiclass-aware) + a short freeform blurb, plus a broad tone/genre pick. No plot details are ever chosen by the player.
- **Profiles**: multiple named profiles supported (not a single default) — a lightweight local profile picker, no passwords, tracking each profile's adventure history for repeat-avoidance and flavor.

### File structure

```
DND-Lite/
├── main.py            # entry point: python main.py
├── cli.py             # game loop, profile/startup menus, streaming display
├── dm.py              # DungeonMaster: main narration prompt, tag parsing (incl. [ADAPT:])
├── architect.py        # hidden one-time LLM call: reconciles random picks into a cohesive adventure skeleton
├── adventure.py        # building-block tables, draft_outline(), adventure_prompt_block(), advance_beat(), apply_adaptation()
├── profile.py           # player profile CRUD + adventure history (for repeat-avoidance)
├── ollama_client.py     # shared call_ollama()/warmup() used by dm.py and architect.py
├── session.py          # per-adventure session dict schema + JSON persistence (one active file per profile)
├── sessions/           # one file per profile: sessions/<profile_slug>.json (gitignored, created at runtime)
├── profiles/           # profile files (gitignored, created at runtime)
├── tests/
│   ├── conftest.py
│   ├── test_session.py
│   ├── test_profile.py
│   ├── test_adventure.py
│   ├── test_architect.py   # JSON parsing/fallback logic, Ollama mocked
│   └── test_dm.py          # prompt assembly + tag parsing (incl. [ADAPT:]), Ollama mocked
├── requirements.txt   # requests>=2.31.0, pytest>=7.0.0 — nothing else
├── .gitignore          # sessions/, profiles/, __pycache__/, *.pyc
├── CLAUDE.md
└── README.md
```

Rationale for the two new small modules: `ollama_client.py` exists only because now *two* things call Ollama (the main DM and the one-time architect pass) — factoring the HTTP/streaming plumbing out avoids duplicating it. `architect.py` is kept separate from `dm.py` because it's a fundamentally different call: one-shot, structured-output (JSON), no streaming, no player-facing narration — mixing it into the `DungeonMaster` class would blur two different responsibilities.

### Player profiles (`profile.py`)

A profile is a persistent record of one person's play history, separate from any single adventure's session file. Multiple named profiles are supported (no passwords) so more than one player/character history can be tracked on the same machine.

```python
def slugify(name: str) -> str
def create_profile(profile_name: str) -> dict
def load_profile(profile_name: str) -> dict
def save_profile(profile: dict) -> None
def list_profiles() -> list[str]
def start_new_adventure(profile: dict, entry: dict) -> None
def complete_current_adventure(profile: dict) -> None
def current_adventure_entry(profile: dict) -> dict | None
def recent_picks(profile: dict, field: str, n: int = 5) -> list[str]
```

`start_new_adventure` enforces the one-active-adventure invariant on the *history* side: if the profile's most recent adventure entry has `status == "in_progress"`, it's flipped to `"abandoned"` (its metadata is kept for repeat-avoidance — only the live playthrough is discarded, not the historical record), then the new entry is appended as `"in_progress"` and the profile is saved. `complete_current_adventure` flips the current in-progress entry to `"completed"` (called by the CLI on `[CLIMAX]`→`[BREAK]`). `current_adventure_entry` returns the in-progress entry if one exists, else `None` — used by the CLI to show "Resume '<title>'..." without needing to open the session file.

Schema (`profiles/<slug>.json`):
```python
{
    "profile_name": "Sam",
    "created_at": ...,
    "adventures": [
        {
            "session_name": "...",
            "character_name": "Kessa",
            "classes": ["Ranger", "Rogue"],   # list, not stat-leveled — multiclass is just a flavor list here
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

`recent_picks(profile, "antagonist_archetype", n=5)` — used by `adventure.draft_outline()` to exclude a table category's last N picks across this profile's adventures, so back-to-back sessions for the same player don't reuse the same antagonist type, setting, hook, twist, or climax shape. If every option in a table has been used recently (small table, prolific player), fall back to the full table rather than raising an error.

`start_new_adventure` is called once at adventure creation, so repeat-avoidance works even for adventures that later get abandoned. `complete_current_adventure` is called when the DM emits `[CLIMAX]` followed by `[BREAK]`, or the player explicitly ends the story.

### Session schema (`session.py`)

**Only one unfinished adventure can exist per profile at a time.** Rather than a list of named saves, each profile has a single active-session slot: `sessions/<profile_slug>.json`. Starting a new adventure while one is pending overwrites this file (after the CLI confirms with the player — see CLI flow below); there is no session-name picker to maintain, since there's never more than one file to choose from.

```python
def empty_session(profile_name, character_name, classes, blurb) -> dict:
    return {
        "profile_name": profile_name,
        "character_name": character_name,
        "classes": classes,          # list[str], e.g. ["Ranger", "Rogue"]
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

def session_path(profile_name) -> Path
def save_session(session) -> None              # overwrites sessions/<profile_slug>.json
def load_active_session(profile_name) -> dict | None   # None if no unfinished adventure
def has_active_session(profile_name) -> bool
def delete_session(profile_name) -> None       # called right before a replacement is created
def add_history(session, role, text) -> None
def set_flag(session, key, value=True) / get_flag(session, key, default=False)
```

The adventure's own generated `title` (from the architect pass, once it runs) is what the CLI displays when offering to resume — there's no separate player-chosen session name to collect at setup, since it would be redundant with the single-slot design.

### Adventure building blocks & draft outline (`adventure.py`)

Replaces dndgame's 8 fixed templates with independent random tables, so combinations vastly outnumber any hand-written set:

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

def draft_outline(tone: str, profile: dict) -> dict:
    """Randomly pick one entry per table, filtered by tone tags and excluding
    this profile's recent picks (via profile.recent_picks). Returns the RAW
    picks only — no prose yet. This is pure Python, fully unit-testable,
    no LLM call."""

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

Adapted from concepts in dndgame's One Shot / Quest / Epic system, updated for the new randomized-outline design:

- The preset picked at setup determines `total_beats` (1, 3, or 5) — this is the number of **acts** the architect writes into `adventure["beats"]`. The overall arc is always `HOOK → Act 1 … Act N → CLIMAX → RESOLUTION`; hook/climax/resolution are separate fields, not counted among the acts.
- `adventure["current_beat"]` starts at `0` (still in the hook) and increments by 1 each time the DM emits `[BEAT]`, capped at `total_beats`. Reaching `total_beats` doesn't auto-trigger the climax — the DM decides when the story has earned it and emits `[CLIMAX]` explicitly.
- `adventure_prompt_block()` tells the DM its current position using `stage_labels()` (e.g. "You are in **Act 2 of 3**") plus explicit **beat rules**: don't advance beats faster than the player's actions justify, don't skip straight to the climax just because `current_beat == total_beats`, and don't reveal the climax or resolution options to the player before they're reached.
- One Shot's single beat means the "act" is really just a short rising-action stretch before the climax — the architect is told to write a punchier, more urgent single beat rather than a full 3-part arc compressed into one entry.
- Epic's 5 beats are explicitly flagged to the architect as spanning **multiple play sessions** (i.e., expect save/resume between acts) — its beat descriptions should each be substantial enough to sustain a full sitting on their own, and subplots (a secondary thread not required for the main climax) are encouraged for beats 2–4.

### Adventure architect pass (`architect.py`)

A single hidden LLM call made once, at adventure creation, that turns the raw random picks into one cohesive, well-written outline — and is explicitly told to reconcile any picks that don't naturally fit together (reinterpreting rather than ignoring a table entry, e.g. "a flooded coastal ruin" + "a corrupt church official" becomes a sea-flooded, half-drowned theocracy).

```python
def build_adventure(draft: dict, character_name: str, classes: list[str],
                     blurb: str, preset: str) -> dict:
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

The system prompt for this call is explicit that: (1) the character's name/classes/blurb should flavor the hook (e.g. a Rogue's hook differs from a Paladin's), (2) the output is never shown to the player directly — it's the DM's private notes — so it can be as blunt/mechanical as needed as long as it's usable, (3) beats are a flexible plan, not a script — the main DM will adapt them as needed.

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
2. **Character block** — name, classes (multiclass listed as-is, no levels/stats), and blurb, at face value, no invented stats.
3. **Narration rules** — second person, vivid, 3–5 sentences, end each turn at a choice point.
4. **Player-agency rules** — never write the player's dialogue, emotions, or unstated decisions; always end at a natural pause.
5. **Self-reported dice block** — qualitative bands, no DC spoken, no arithmetic (see below).
6. **Tag rules** — the tag set below, including `[ADAPT:]`.
7. **Adventure block** — `adventure.adventure_prompt_block(session["adventure"])`: the **original outline** (title/setting/hook/antagonist/beats/climax), the **current stage** (`stage_labels()` position + beat rules — don't rush, don't skip to the climax early, don't reveal climax/resolution), and, if any exist, a **live adaptations** section listed last and marked as authoritative over the original where they conflict.
8. **Story Mode block** — only if `session["story_mode"]`.
9. **Scene anchor** — last ~400 chars of the prior DM turn, truncated on a sentence boundary, "SCENE IN PROGRESS — DO NOT RESET." This is the key trick that keeps a small local model from losing the thread.
10. **Opening vs. continuing instruction** — no history → open with the adventure hook + character blurb; scene anchor present → never re-establish setting.
11. **Final reminder footer** — one-line reiteration of the absolute rule.

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

**Startup**: profile picker first — list existing profiles (`profile.list_profiles()`) or create a new one by typing a name. Then the menu depends on whether that profile has an unfinished adventure (`session.has_active_session(profile_name)`, backed by `profile.current_adventure_entry(profile)` for the display title/date):

- **Unfinished adventure exists**: `1) Resume "<title>" (last played <date>)`, `2) Start a new adventure`, `3) Quit`. Choosing (2) prompts a confirmation — *"This will discard your unfinished adventure '<title>'. Continue? [y/N]"* — before proceeding, since replacing it is destructive and irreversible.
- **No unfinished adventure**: `1) New adventure`, `2) Quit`.

**New adventure** (after any confirmation above):
1. Character name.
2. Class(es) — a single prompt accepting multiclass input (e.g. `Ranger/Rogue`), split and stored as a list.
3. Freeform blurb (a sentence or two of flavor/personality).
4. Tone picker (Classic Fantasy / Horror / Heist / Political Intrigue / …).
5. Length preset — One Shot / Quest / Epic, shown with each preset's `blurb` + `estimate` from `adventure.PRESETS`.
6. `adventure.draft_outline(tone, profile)` → raw picks (instant, no LLM call).
7. `architect.build_adventure(draft, character_name, classes, blurb, preset)` → full skeleton. Print a "The DM is preparing your adventure…" message while this call runs (it's a real, possibly multi-second, Ollama call).
8. If a previous unfinished adventure existed: `session.delete_session(profile_name)` first. Then `profile.start_new_adventure(profile, {...})` (marks any prior in-progress entry `abandoned`, appends the new one as `in_progress`), `session.save_session(session)` immediately.
9. `dm.warmup()`, then an opening DM call with a synthetic `"[BEGIN ADVENTURE]"` input.

**Resume**: `session.load_active_session(profile_name)` → `dm.recap(session)`. No picker needed — there is at most one file to load.

**Main loop**: `save`/`quit`/`exit` handled locally, everything else sent to `respond_stream` with tokens printed as they arrive, **autosave after every turn** (this plus the explicit `save` command is what lets the player stop and resume at any point, not just at `quit`), `RuntimeError` around dropped-Ollama-server errors. On `[CLIMAX]` followed by `[BREAK]` (or explicit quit-after-climax), call `profile.complete_current_adventure(profile)` — the session file itself is left in place (a completed adventure can still be replayed/reviewed via `resume` until the player starts a new one, at which point it's replaced like any other unfinished-vs-new transition).

### Build order

1. `session.py` and `profile.py` — schemas + persistence, unit-testable in isolation with `tmp_path`. No interdependency between them beyond `session["profile_name"]` being a plain string. Test the replace-on-new-adventure path explicitly: `save_session` → `delete_session` → `save_session` again leaves exactly one file, and `profile.start_new_adventure` correctly flips a prior `in_progress` entry to `abandoned`.
2. `adventure.py` — building-block tables, `draft_outline` (including recent-picks exclusion via a mocked/fake profile), `stage_labels` (test all 3 preset beat counts), `adventure_prompt_block`, `advance_beat` (test capping at `total_beats`), `apply_adaptation`.
3. `ollama_client.py` — thin shared HTTP/streaming wrapper, tested with `requests` mocked.
4. `architect.py` — prompt construction + JSON parsing + retry + deterministic fallback; test all three paths (valid JSON, one retry then success, fallback) with Ollama mocked.
5. `dm.py` prompt builder — assemble all blocks including the adventure/adaptations split; test block presence/absence.
6. `dm.py` tag parser — test all 6 tags (including `[ADAPT:]`) plus no-tags and whitespace/casing variants.
7. `dm.py` streaming/respond/recap — Ollama mocked in tests.
8. `cli.py` + `main.py` — profile picker, new/resume flows, main loop, autosave, completion status updates.
9. Manual playtest against real local Ollama: verify two fresh adventures with the same tone don't reuse the same antagonist archetype, verify the architect pass produces coherent output even when picks clash, verify an off-script player choice produces a sensible `[ADAPT:]` and that the new direction persists across subsequent turns, verify quit-and-resume recap continuity, and verify that starting a new adventure with one already pending shows the confirmation and correctly discards the old one.
10. `CLAUDE.md`, `README.md`, `requirements.txt`, `.gitignore` — finalized last.

### Explicit non-goals

No combat engine, no character stats/HP, no companions, no XP/leveling, no TTS, no D&D Beyond import, no Flask/web/Electron, no provider-abstraction layer, no password/auth on profiles. A future web phase could reuse dndgame's SSE-streaming + live tag-filtering approach conceptually, but no scaffolding for it now.

### Verification

- `pytest tests/` — all unit tests pass (session/profile persistence round-trips, one-active-adventure replace behavior, draft-outline repeat-avoidance, architect JSON parsing + fallback, prompt block assembly, tag parsing incl. `[ADAPT:]`) without a live Ollama server.
- Manual playtest per build-order step 9.

## Running

```
python -m venv .venv && .venv/bin/pip install -r requirements.txt
ollama pull llama3.1:8b   # the default in ollama_client.py -- runs
                          # acceptably (~30-60s/turn) on an 8-core CPU with
                          # no GPU, and reliably follows the tag/JSON
                          # instructions the game depends on. If you have a
                          # capable GPU, a larger model (e.g.
                          # nous-hermes2:10.7b) will be faster and better --
                          # just change DEFAULT_MODEL in ollama_client.py.
ollama serve
.venv/bin/python main.py
```

Run the test suite (Ollama mocked, no live server needed) with:
```
.venv/bin/python -m pytest tests/
```
