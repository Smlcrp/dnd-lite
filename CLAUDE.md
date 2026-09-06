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
adventure narrated by a local LLM. No character creation, no stat tracking,
no combat engine, no leveling, no companions. Dice are self-reported by the
player in natural language; the DM narrates qualitative outcomes, never DC
math.

Adventures are generated fresh every time from randomized building blocks,
reconciled into cohesive prose by a hidden one-time LLM "architect" call, and
kept secret from the player — revealed only through play. The DM can adapt
the plan mid-story via `[ADAPT:]` when the player goes off-script.

v1 is a CLI app only. A minimal web UI is a possible future phase — do not
scaffold Flask/web/Electron code until that phase is explicitly started.

## File Structure
- `main.py` — entry point
- `cli.py` — game loop, profile/startup menus, streaming display
- `dm.py` — DungeonMaster: main narration prompt, tag parsing
- `architect.py` — hidden one-time LLM call: reconciles random picks into a cohesive adventure skeleton
- `adventure.py` — building-block tables, draft_outline(), adventure_prompt_block(), advance_beat(), apply_adaptation()
- `profile.py` — player profile CRUD + adventure history (repeat-avoidance)
- `ollama_client.py` — shared call_ollama()/warmup(), used by dm.py and architect.py
- `session.py` — per-adventure session schema + JSON persistence (one active file per profile)

## Conventions
- No character/stat model anywhere in this codebase. Classes are a flavor
  list on the profile/session (multiclass-aware), never leveled or given
  stats. If you find yourself adding an ability score, HP, or DC-by-level
  table, stop — that's dndgame's job, not this one.
- Tag set emitted by the LLM: `[SCENE:]`, `[CHECK:]`, `[BEAT]`, `[CLIMAX]`,
  `[BREAK]`, `[ADAPT:]`. Do not add mechanics tags (`[COMBAT:]`, `[XP:]`,
  `[GOLD:]`, `[ITEM:]`, `[COMPANION:]`, `[ACTION:]`).
- Self-reported dice: the app never rolls dice and never does arithmetic on
  a player-reported number. The DM maps reported results to fixed
  qualitative bands (see dm.py's self-reported dice prompt block) — never
  states a DC.
- One unfinished adventure per profile, enforced by design, not just
  convention: `sessions/<profile_slug>.json` is a single file, never a list.
  Starting a new adventure always replaces the pending one (after CLI
  confirmation) and marks its profile history entry `abandoned`. Do not
  reintroduce a session-name picker or multi-save list.
- Ollama call plumbing lives in `ollama_client.py` only; no
  provider-abstraction layer until a second provider actually exists.
- Sessions autosave after every turn; profiles are updated at adventure
  start and on completion (`[CLIMAX]` → `[BREAK]`).
- No comments unless the WHY is non-obvious.

## Running
```
ollama pull <model>
ollama serve
python main.py
```
