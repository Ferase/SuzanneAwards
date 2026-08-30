"""
Tracks total accumulated Blender usage time and emits a "playtime"
AchievementEvent on a slow interval - both for global achievements
(lifetime total) and daily ones (today's total, owned by daily.py since
it resets on the same lifecycle as the rest of that module's state).

Time is accumulated from real elapsed wall-clock time between ticks
(not a simple per-tick counter), so it stays accurate even if a tick is
delayed. Only written to disk once per tick (TICK_INTERVAL, default one
minute) rather than continuously, to avoid needless disk I/O - at most
one tick's worth of playtime can be lost if Blender is killed rather
than closed normally; unregister() flushes immediately on a clean
shutdown or addon disable to avoid losing anything then. atexit is a
second, redundant safety net for the same reason - a normal Blender
quit doesn't always guarantee every addon's unregister() actually runs.

Also doubles as the live day-rollover check for daily.py: since this is
already ticking on a short interval, there's no need for daily.py to
run a second, near-identical timer just to catch midnight while
Blender stays open.

Also owns the consecutive-day login streak. A streak only cares about
*when a session started*, never when it ended, so this is handled
entirely in register() - no exit-side logic needed, unlike playtime
itself.
"""



import time
import json
import os
import datetime
import atexit

import bpy

from . import manager
from . import daily
from .events import AchievementEvent

SAVE_FILENAME: str = "achievement_playtime.json"
TICK_INTERVAL: float = 60.0   # seconds between ticks - also the day-rollover check cadence

total_seconds: float = 0.0   # lifetime total, persisted
_last_tick_time: float = 0.0  # time.time() as of the last tick - NOT persisted, reset each session

last_login_date: str = ""    # ISO date string of the last session's start, persisted
current_streak: int = 0      # consecutive days with at least one session start, persisted



def get_save_path() -> str:
    cfg_dir = bpy.utils.user_resource('CONFIG')
    return os.path.join(cfg_dir, SAVE_FILENAME)

def load() -> None:
    global total_seconds, last_login_date, current_streak

    path = get_save_path()
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
        total_seconds = data.get("total_seconds", 0.0)
        last_login_date = data.get("last_login_date", "")
        current_streak = data.get("current_streak", 0)
    else:
        total_seconds = 0.0
        last_login_date = ""
        current_streak = 0

def save() -> None:
    with open(get_save_path(), "w") as f:
        json.dump({
            "total_seconds": total_seconds,
            "last_login_date": last_login_date,
            "current_streak": current_streak,
        }, f, indent=2)

def get_total_hours() -> float:
    return total_seconds / 3600.0

def get_current_streak() -> int:
    return current_streak

def _update_login_streak() -> None:
    """Called once per Blender session, from register(). Compares
    today's date against the last recorded session-start date to
    advance or reset the consecutive-day streak, then emits a "login"
    event carrying the current streak length."""

    global last_login_date, current_streak

    today_str = datetime.date.today().isoformat()

    if last_login_date != today_str:
        if last_login_date:
            last = datetime.date.fromisoformat(last_login_date)
            gap_days = (datetime.date.today() - last).days
            if gap_days == 1:
                current_streak += 1
            else:
                current_streak = 1  # gap of 2+ days (or a date going backwards) breaks the streak
        else:
            current_streak = 1  # first session ever

        last_login_date = today_str
        save()

    manager.handle_event(AchievementEvent(
        type="startup",
        extra={"streak": current_streak},
    ))

def _on_process_exit() -> None:
    """Registered via atexit as a redundant safety net alongside
    unregister()'s own flush - a normal Blender quit doesn't always
    guarantee addon unregister() functions actually run. Deliberately
    pure file I/O only: doesn't touch bpy.context or fire achievement
    events, since Blender's own Python/UI state can't be trusted to
    still be valid by the time atexit callbacks run."""

    global total_seconds

    now = time.time()
    total_seconds += now - _last_tick_time
    save()

def _tick() -> float:
    """Accumulates elapsed real time since the last tick, persists it,
    checks for a day rollover (see module docstring), and emits a
    "playtime" event carrying both the lifetime and today's totals."""

    global total_seconds, _last_tick_time

    now = time.time()
    elapsed = now - _last_tick_time
    _last_tick_time = now

    total_seconds += elapsed
    save()

    # Check for rollover BEFORE adding today's elapsed time, so a
    # midnight crossing resets daily_seconds to 0 first and this tick's
    # elapsed time is credited to the new day, not the one that just ended
    daily.check_for_new_day()
    daily.add_daily_seconds(elapsed)

    manager.handle_event(AchievementEvent(
        type="playtime",
        extra={
            "total_seconds": total_seconds,
            "daily_seconds": daily.get_daily_seconds(),
        },
    ))

    return TICK_INTERVAL

def register():
    global _last_tick_time

    load()
    _update_login_streak()
    _last_tick_time = time.time()

    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=TICK_INTERVAL, persistent=True)

    atexit.register(_on_process_exit)

def unregister():
    global total_seconds, _last_tick_time

    # Flush whatever's accumulated since the last tick before shutting down
    now = time.time()
    total_seconds += now - _last_tick_time
    save()

    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)

    atexit.unregister(_on_process_exit)