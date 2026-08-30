"""
Handles the daily achievement rotation: which achievements from the
full pool (achievements/daily_achievements/) are active today, and
re-rolling that selection whenever the calendar date changes. Also owns
daily_seconds - today's accumulated playtime - since it resets on
exactly the same day-rollover lifecycle as the achievement selection.

Detects a date rollover two ways: on load() (called at addon register,
comparing the saved date against today), and via check_for_new_day(),
called every tick by playtime.py (which is already running on a short
interval) so a rollover is caught live while Blender stays open across
midnight, not just on next launch. No dedicated timer of its own.
"""



import bpy
import random
import datetime
import json
import os

from .achievements.daily_achievements import DAILY_ACHIEVEMENT_CLASSES

SAVE_FILENAME: str = "achievement_daily.json"
DAILY_ACHIEVEMENT_COUNT: int = 10   # how many of the pool are active per day

seed: int = 0
date: str = ""                # ISO date string, e.g. "2026-08-28"
active_ids: list[str] = []    # IDs of today's selected daily achievements
daily_seconds: float = 0.0    # accumulated playtime today, added to by playtime.py



def get_save_path() -> str:
    cfg_dir = bpy.utils.user_resource('CONFIG')
    return os.path.join(cfg_dir, SAVE_FILENAME)

def _today_str() -> str:
    return datetime.date.today().isoformat()

def get_rng() -> random.Random:
    """A Random instance seeded for today - used to pick goal variants
    deterministically (same picks all session, and again if the addon
    is reloaded the same day)."""

    return random.Random(seed)

def is_active_today(achievement_id: str) -> bool:
    return achievement_id in active_ids

def get_daily_seconds() -> float:
    return daily_seconds

def add_daily_seconds(amount: float) -> None:
    """Called by playtime.py each tick with however much real time just
    elapsed. Kept here (rather than in playtime.py) since it resets on
    the same day-rollover as everything else in this module."""

    global daily_seconds
    daily_seconds += amount
    save()

def _roll_new_day() -> None:
    """Picks a new seed, selects today's active achievements, resets
    today's playtime, and clears saved progress for every daily
    achievement (not just today's selection - yesterday's chosen ones no
    longer apply either)."""

    global seed, date, active_ids, daily_seconds

    seed = random.randint(0, 2**31 - 1)
    date = _today_str()
    daily_seconds = 0.0

    rng = random.Random(seed)
    pool = list(DAILY_ACHIEVEMENT_CLASSES)
    rng.shuffle(pool)
    chosen = pool[:DAILY_ACHIEVEMENT_COUNT]
    active_ids = [cls.ID for cls in chosen]

    from . import state
    for cls in DAILY_ACHIEVEMENT_CLASSES:
        state.progress.pop(cls.ID, None)
    state.save()

    save()

def check_for_new_day() -> bool:
    """Checks whether the calendar date has changed since the last roll,
    and re-rolls immediately if so (re-instantiating achievements too,
    so the new selection takes effect right away rather than only on
    next restart). Returns True if a rollover happened.

    Called from load() at startup, and from playtime.py's tick while
    Blender stays open."""

    if date != _today_str():
        _roll_new_day()

        from . import manager
        manager.init_achievements()

        return True

    return False

def load() -> None:
    """Load the saved seed/date/selection/daily_seconds, rolling a new
    day if the saved date doesn't match today. Must run before
    manager.init_achievements(), so today's selection is known before
    achievements get instantiated."""

    global seed, date, active_ids, daily_seconds

    path = get_save_path()
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
        seed = data.get("seed", 0)
        date = data.get("date", "")
        active_ids = data.get("active_ids", [])
        daily_seconds = data.get("daily_seconds", 0.0)
    else:
        seed, date, active_ids, daily_seconds = 0, "", [], 0.0

    check_for_new_day()

def save() -> None:
    with open(get_save_path(), "w") as f:
        json.dump({
            "seed": seed,
            "date": date,
            "active_ids": active_ids,
            "daily_seconds": daily_seconds,
        }, f, indent=2)