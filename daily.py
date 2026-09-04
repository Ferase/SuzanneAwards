"""
Subsystem responsible for handling the daily achievements and their RNG.
"""



import bpy
import random
import datetime
import json
import os

from . import manager
from . import state
from . import exp
from .events import AchievementEvent
from .achievements._base import BlenderAchievement
from .achievements.daily_achievements import DAILY_ACHIEVEMENT_CLASSES

# The name of the file saved to Blender's config
SAVE_FILENAME: str = "achievement_daily.json"

# How many daily achievements will be chosen
DAILY_ACHIEVEMENT_COUNT: int = 10

# RNG seed
seed: int = 0

# ISO date string, e.g. "2026-08-28"
date: str = ""

# Dictionary of daily achievements active today plus their unlock status
active_ids: dict[str, bool] = dict()

# Accomulated playtime today, sent to playtime.py
daily_seconds: float = 0.0

# Whether today's daily-boost offer is currently available to claim -
# True only after all of today's daily achievements are complete, and
# only until either claimed or the day rolls over (whichever first)
boost_available: bool = False

# Called with no arguments the moment boost_available first flips True
# for the day - ui.py hooks this to show the completion popup
_daily_complete_listeners = []



def get_save_path() -> str:
    """Returns the path of the daily achievement save file in Blender's config folder."""

    # Get Blender config folder
    cfg_dir = bpy.utils.user_resource("CONFIG")
    return os.path.join(cfg_dir, SAVE_FILENAME)

def _today_str() -> str:
    """Get the current date in ISO string format."""

    return datetime.date.today().isoformat()

def _get_seed() -> int:
    """Generates a random seed."""

    return random.randint(0, 2**31 - 1)

def get_rng() -> random.Random:
    """Retruns an RNG object that will be used to pick random achievements and goals for the day."""

    return random.Random(seed)

def is_active_today(achievement_id: str) -> bool:
    """Checks whether a daily achievement is chosen on the current date."""

    global active_ids

    return achievement_id in active_ids.keys()

def get_daily_seconds() -> float:
    """Returns how many seconds have passed in the day."""

    return daily_seconds

def add_daily_seconds(amount: float) -> None:
    """Add daily seconds. Called by playtime.py to track how much time is spent in Blender."""

    global daily_seconds
    daily_seconds += amount
    save()

def _roll_new_day() -> None:
    """Generates a new seed, grabs the current date in ISO format, picks achievements, and resets daily seconds.
    
    Runs when a new day begins or when Blender is started on a new day."""

    global seed, date, active_ids, daily_seconds, boost_available

    # Generate seed and grab date
    seed = _get_seed()
    date = _today_str()

    # Reset seconds
    daily_seconds = 0.0

    # Clear yesterday's selection entirely before repopulating - without
    # this, old entries never go away, and a single stale False left
    # over from a past incomplete day would permanently block
    # all(active_ids.values()) from ever being True again
    active_ids = dict()

    # Today's boost offer (if any) doesn't carry over - "if they skip
    # out on it until the next day, it will be unavailable"
    boost_available = False

    # Generate RNG object and pick achievements from pool
    rng = get_rng()
    pool = list(DAILY_ACHIEVEMENT_CLASSES)
    rng.shuffle(pool)
    chosen = pool[:DAILY_ACHIEVEMENT_COUNT]
    for cls in chosen:
        active_ids[cls.ID] = False

    # Reset progress on new day
    for cls in DAILY_ACHIEVEMENT_CLASSES:
        state.progress.pop(cls.ID, None)

    # Save the current states
    state.save()

    # Save the daily acheivements file
    save()

def check_for_new_day() -> bool:
    """Checks whether the calendar date has changed since the last roll.
    
    Returns True if the date has changed, also rolls the new RNG and achievements automatically. Returns false if it's still today."""

    # If the loaded date still today, do nothing
    if date == _today_str():
        return False

    # Otherwise, roll new RNG and achievements
    _roll_new_day()

    # Reinitialize
    manager.init_achievements()

    return True

def add_daily_complete_listener(func) -> None:
    """func() will be called (no arguments) the moment all of today's daily achievements become complete - once per day, at most."""

    _daily_complete_listeners.append(func)

def _check_todays_progress(instance: BlenderAchievement, current_level: int, levels_gained: int) -> None:
    """Marks today's completion for a given achievement, and flags the boost offer as available (once) when all of today's selection are done."""

    global boost_available

    if instance.ID not in active_ids:
        return

    active_ids[instance.ID] = True
    save()

    # Guard with "not boost_available" so this can't re-fire the popup
    # every time this function runs after the day's already complete -
    # in practice each achievement only calls this once anyway (manager
    # skips already-unlocked instances), but this keeps the intent explicit
    if all(active_ids.values()) and not boost_available:
        boost_available = True
        save()

        for listener in _daily_complete_listeners:
            listener()

def is_boost_available() -> bool:
    return boost_available

def claim_boost() -> bool:
    """Claims today's boost offer, if one is available: increments the
    EXP multiplier and consumes the offer for the rest of today. Returns
    True if a boost was actually claimed, False if none was available
    (e.g. the button was clicked twice in a row)."""

    global boost_available

    if not boost_available:
        return False

    exp.increase_multiplier(1)
    boost_available = False
    save()

    return True

def load() -> None:
    """Load the save file for daily achievements containing seed, date, active achievement IDs, and daily seconds."""

    global seed, date, active_ids, daily_seconds, boost_available

    # Get save file path
    path = get_save_path()

    # If no file exists, use default values and check for new day
    if not os.path.exists(path):
        seed = 0
        date = ""
        active_ids = dict()
        daily_seconds = 0.0
        boost_available = False
    else:
        # Open the JSON save file
        with open(path, "r") as f:
            data = json.load(f)

        # Set all values from the JSON file's saved information
        seed = data.get("seed", 0)
        date = data.get("date", "")
        active_ids = data.get("active_ids", dict())
        daily_seconds = data.get("daily_seconds", 0.0)
        boost_available = data.get("boost_available", False)

    # Check for new day - this must run regardless of which branch
    # above was taken
    check_for_new_day()

    # This must also run regardless of which branch was taken above -
    # previously this was only reached on the "save file already
    # exists" path, so on a brand new install (no save file yet) the
    # listener never got registered at all, and daily-completion
    # detection silently never worked for that first session
    manager.add_unlock_listener(_check_todays_progress)

def save() -> None:
    """Save the daily achievements save file."""

    # Write JSON
    with open(get_save_path(), "w") as f:
        json.dump({
            "seed": seed,
            "date": date,
            "active_ids": active_ids,
            "daily_seconds": daily_seconds,
            "boost_available": boost_available,
        }, f, indent=2)