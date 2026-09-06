# DND Lite — Project Context

## Security Constraint (NEVER SKIP)
This project currently talks only to a local Ollama server (free, no metered
cost). Before wiring in any paid/metered API (Anthropic, OpenAI, or anything
billed per token) in a future phase, you MUST warn the user and get explicit
confirmation before making that call, and before running any test/script that
would invoke it.

## Project Vision
A lightweight, text-based AI Dungeon Master. The player brings their own D&D
character (paper or D&D Beyond, external to this app) and plays a text
adventure narrated by a local LLM. No combat engine, no companions, no
mechanical class-feature engine, no hand-built 5e reference data. Dice are
self-reported by the player in natural language; the DM narrates qualitative
outcomes, never DC math.

Accounts require a username + password (hashed, stdlib-only). Character
details (name, class(es), starting level, blurb) are asked fresh at the
start of every new adventure — unless the account opted into a saved
"default character" at creation, which skips that prompt every time. The
DM has full working D&D 5e knowledge via its own training (no data tables
stored by this app) and may narrate the character leveling up during play,
paced like a real campaign — but the app never stores or recalculates a
level number; the player's own physical/external character sheet is
authoritative, exactly like self-reported dice.

Adventures are generated fresh every time from randomized building blocks,
reconciled into cohesive prose by a hidden one-time LLM "architect" call, and
kept secret from the player — revealed only through play. The DM can adapt
the plan mid-story via `[ADAPT:]` when the player goes off-script.

v1 is a CLI app only. A minimal web UI is a possible future phase — do not
scaffold Flask/web/Electron code until that phase is explicitly started.

## File Structure
- `main.py` — entry point
- `cli.py` — game loop, login/account-creation menus, streaming display
- `dm.py` — DungeonMaster: main narration prompt, tag parsing
- `architect.py` — hidden one-time LLM call: reconciles random picks into a cohesive adventure skeleton
- `adventure.py` — building-block tables, draft_outline(), adventure_prompt_block(), advance_beat(), apply_adaptation()
- `account.py` — account CRUD, login verification, default-character storage, adventure history (repeat-avoidance)
- `auth.py` — password hashing/verification (stdlib pbkdf2_hmac, no new dependency)
- `ollama_client.py` — shared call_ollama()/warmup(), used by dm.py and architect.py; resolves DEFAULT_MODEL (fallback constant, overridable via DND_LITE_MODEL env var)
- `session.py` — per-adventure session schema + JSON persistence (one active file per account)

## Conventions
- No character/stat model anywhere in this codebase. Classes are a flavor
  list on the account/session (multiclass-aware), never given ability
  scores or HP. Level is a stored *snapshot* (set once per adventure, or
  inherited from an account's default character) — never mechanically
  recalculated. If you find yourself adding an ability score, HP, a
  DC-by-level table, or an XP counter, stop — that's dndgame's job, not
  this one.
- 5e knowledge lives in the LLM's own training, not in this codebase. Do
  not add a class-features/hit-dice/spell-list data file. The only two
  pieces of hand-maintained D&D-specific data allowed are `cli.CLASSES` (a
  13-name list for input validation, never sent to the model) and
  `adventure.level_tier_description()` (D&D 5e's four tiers of play — guidance
  text injected into prompts for concrete encounter scaling, not a lookup
  table used to compute anything). Both are prompt scaffolding, not a rules
  engine — keep it that way.
- Encounter scaling must respect BOTH the character's level/tier AND the
  established setting/antagonist — never let one override the other. A
  higher tier should raise what's really going on inside a setting (a
  bandit crew becomes a noble's pact with an ancient horror), not replace
  the setting with an unrelated, more "impressive" one. This was a real bug
  caught in manual testing: a vague "escalate appropriately" instruction
  produced near-identical stakes for a level 1 and a level 15 character
  until the concrete tier text was added — don't revert to vague phrasing.
- Leveling is narrated, not tracked: the DM may declare a level-up as story
  flavor, paced like real D&D advancement, but no tag or state field
  records it — continuity relies on conversation history + the scene
  anchor, same as everything else. Do not add an `[XP:]`/`[LEVELUP:]` tag
  or a mutable level field on the session/account — this was a deliberate
  choice, not an oversight.
- Tag set emitted by the LLM: `[SCENE:]`, `[CHECK:]`, `[BEAT]`, `[CLIMAX]`,
  `[BREAK]`, `[ADAPT:]`. Do not add mechanics tags (`[COMBAT:]`, `[XP:]`,
  `[GOLD:]`, `[ITEM:]`, `[COMPANION:]`, `[ACTION:]`).
- Self-reported dice: the app never rolls dice and never does arithmetic on
  a player-reported number. The DM maps reported results to fixed
  qualitative bands (see dm.py's self-reported dice prompt block) — never
  states a DC.
- One unfinished adventure per account, enforced by design, not just
  convention: `sessions/<account_slug>.json` is a single file, never a list.
  Starting a new adventure always replaces the pending one (after CLI
  confirmation) and marks its account history entry `abandoned`. Do not
  reintroduce a session-name picker or multi-save list.
- Passwords are hashed via `auth.py` (pbkdf2_hmac + per-account salt,
  stdlib only). Never store or log a plaintext password. No password
  complexity rules or lockout policy — this is a local single-player tool,
  not a networked service; don't add auth infrastructure sized for one.
- `default_character` on an account is optional and general-purpose (any
  account can opt in), not a special case hardcoded to the `test` account
  specifically — even though that's its primary use today.
- Ollama call plumbing lives in `ollama_client.py` only; no
  provider-abstraction layer until a second provider actually exists.
- Model selection has three layers, in increasing precedence:
  `ollama_client._FALLBACK_MODEL` → `DND_LITE_MODEL` env var → `--model` CLI
  flag (threaded through `main.py` → `cli.main(model=...)` →
  `DungeonMaster(model)`). Don't add a config file on top of this — it's
  deliberately just these three, matching the "no config.py" call made
  earlier in the project.
- Sessions autosave after every turn; accounts are updated at adventure
  start and on completion (`[CLIMAX]` → `[BREAK]`).
- No comments unless the WHY is non-obvious.

## Running
```
python -m venv .venv && .venv/bin/pip install -r requirements.txt
ollama pull llama3.1:8b   # the default -- see README.md "Choosing a model"
                          # for the env var / --model override options
ollama serve
.venv/bin/python main.py
```

A `test`/`test` account with a saved default character (Adventurer, Fighter,
level 3) exists for quick manual testing — see README.md "Test account".
