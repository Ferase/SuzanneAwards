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
from .achievements.daily_achievements import DAILY_ACHIEVEMENT_CLASSES

# The name of the file saved to Blender's config
SAVE_FILENAME: str = "achievement_daily.json"

# How many daily achievements will be chosen
DAILY_ACHIEVEMENT_COUNT: int = 10

# RNG seed
seed: int = 0

# ISO date string, e.g. "2026-08-28"
date: str = ""

# List of daily achievements active today
active_ids: list[str] = []

# Accomulated playtime today, sent to playtime.py
daily_seconds: float = 0.0



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

    return achievement_id in active_ids

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

    global seed, date, active_ids, daily_seconds

    # Generate seed and grab date
    seed = _get_seed()
    date = _today_str()

    # Reset seconds
    daily_seconds = 0.0

    # Generate RNG object and pick achievements from pool
    rng = get_rng()
    pool = list(DAILY_ACHIEVEMENT_CLASSES)
    rng.shuffle(pool)
    chosen = pool[:DAILY_ACHIEVEMENT_COUNT]
    active_ids = [cls.ID for cls in chosen]

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

def load() -> None:
    """Load the save file for daily achievements containing seed, date, active achievement IDs, and daily seconds."""

    global seed, date, active_ids, daily_seconds

    # Get save file path
    path = get_save_path()

    # If no file exists, use default values and check for new day
    if not os.path.exists(path):
        seed, date, active_ids, daily_seconds = 0, "", [], 0.0
        check_for_new_day()
        return

    # Open teh JSON save file
    with open(path, "r") as f:
        data = json.load(f)

    # Set all values from the JSON file's saved information
    seed = data.get("seed", 0)
    date = data.get("date", "")
    active_ids = data.get("active_ids", [])
    daily_seconds = data.get("daily_seconds", 0.0)

    # Check for new day
    check_for_new_day()

def save() -> None:
    """Save the daily achievements save file."""

    # Write JSON
    with open(get_save_path(), "w") as f:
        json.dump({
            "seed": seed,
            "date": date,
            "active_ids": active_ids,
            "daily_seconds": daily_seconds,
        }, f, indent=2)