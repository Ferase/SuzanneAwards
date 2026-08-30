"""
Tracks the user's level and EXP. The EXP required to advance from a
given level to the next increases linearly with level. EXP is stored
as "progress within the current level" (it resets to 0 on level-up),
not as a lifetime cumulative total - that's what both the N-panel bar
and the toast bar will represent a fraction of.
"""



import bpy
import json
import os

# Tuning: EXP needed to go from level 1 to level 2, and how much more
# each subsequent level requires than the last
BASE_EXP_TO_LEVEL: int = 100
EXP_INCREMENT_PER_LEVEL: int = 25

SAVE_FILENAME: str = "achievement_exp.json"

level: int = 1
exp: int = 0  # progress within the current level, NOT a lifetime total



def exp_required_for_level(lvl: int) -> int:
    """EXP required to advance FROM the given level TO the next one."""

    return BASE_EXP_TO_LEVEL + EXP_INCREMENT_PER_LEVEL * (lvl - 1)

def get_save_path() -> str:
    cfg_dir = bpy.utils.user_resource('CONFIG')
    return os.path.join(cfg_dir, SAVE_FILENAME)

def load() -> None:
    """Load level/EXP from disk."""

    global level, exp

    path = get_save_path()
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
        level = data.get("level", 1)
        exp = data.get("exp", 0)
    else:
        level = 1
        exp = 0

def save() -> None:
    """Save level/EXP to disk."""

    with open(get_save_path(), "w") as f:
        json.dump({"level": level, "exp": exp}, f, indent=2)

def add_exp(amount: int) -> list[int]:
    """Adds EXP, applying as many level-ups as the amount covers (in
    case a single achievement's EXP is enough to cross more than one
    threshold at once). Returns the list of levels reached, in order -
    empty if no level-up happened."""

    global level, exp

    levels_gained: list[int] = []
    exp += amount

    threshold = exp_required_for_level(level)
    while exp >= threshold:
        exp -= threshold
        level += 1
        levels_gained.append(level)
        threshold = exp_required_for_level(level)

    save()
    return levels_gained

def get_progress_fraction() -> float:
    """0.0-1.0 fraction of the way through the current level. Used to
    drive both the N-panel bar and the toast bar."""

    threshold = exp_required_for_level(level)
    return exp / threshold if threshold > 0 else 0.0
