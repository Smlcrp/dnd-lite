"""D&D 5e's death & dying rules -- reference only. The app never tracks HP
or rolls a death save itself; the player reports their own result, exactly
like any other self-reported roll (see dm.SELF_REPORTED_DICE_BLOCK)."""

DEATH_AND_DYING_BLOCK = (
    "DEATH & DYING REFERENCE (the player's own sheet tracks actual HP -- "
    "never compute this yourself): at 0 HP a character falls unconscious "
    "and is dying. On each of their turns they report a death save result "
    "of their own roll, same as any other self-reported roll -- 10 or "
    "higher is a success, below 10 a failure; 3 successes stabilizes them "
    "(unconscious but no longer dying), 3 failures means death. A natural "
    "20 on a death save regains 1 HP and consciousness immediately; a "
    "natural 1 counts as two failures. Taking any damage while at 0 HP "
    "counts as a failure (two failures on a critical hit), and damage at "
    "0 HP equal to or exceeding the character's hit point maximum kills "
    "them outright. Ask the player to report these rolls just like any "
    "other check -- never invent or calculate the outcome yourself."
)
