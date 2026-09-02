"""
Subsystem that tracks usage time and emits an event on slow intervals to announce how much the user has used Blender.

Tracks both a daily usage amount and lifetime usage amount.
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

# Play time save file name
SAVE_FILENAME: str = "achievement_playtime.json"

# Seconds between ticks and day rollver checks
TICK_INTERVAL: float = 60.0

# Persistent lifetime total usage
total_seconds: float = 0.0

# Time of the last tick
_last_tick_time: float = 0.0

# Persistent ISO date string of the last day the user logged in, for startup streak achievements
last_login_date: str = ""

# Persistent streak of days the user has opened Blender
current_streak: int = 0



def get_save_path() -> str:
    """Get the play time save fiel path within Blender's config directory."""

    # Get the Blender config
    cfg_dir = bpy.utils.user_resource('CONFIG')
    return os.path.join(cfg_dir, SAVE_FILENAME)

def load() -> None:
    """Load the play time save file."""

    global total_seconds, last_login_date, current_streak

    # Get the play time save file path
    path = get_save_path()

    # If the file doesn't exist, use default values
    if not os.path.exists(path):
        total_seconds = 0.0
        last_login_date = ""
        current_streak = 0
        return

    # Otherwise, open the JSON file and read its data
    with open(path, "r") as f:
        data = json.load(f)

    # Set global values based on JSON data
    total_seconds = data.get("total_seconds", 0.0)
    last_login_date = data.get("last_login_date", "")
    current_streak = data.get("current_streak", 0)

def save() -> None:
    """Save the play time save file."""

    # Write JSON file
    with open(get_save_path(), "w") as f:
        json.dump({
            "total_seconds": total_seconds,
            "last_login_date": last_login_date,
            "current_streak": current_streak,
        }, f, indent=2)

def get_total_hours() -> float:
    """Convert global total seconds to hours."""

    global total_seconds

    return total_seconds / 3600.0

def get_current_streak() -> int:
    """Get the current daily startup streak."""

    global current_streak

    return current_streak

def _set_streak(today_iso: str, value: int = 1) -> None:
    """Sets the uer's startup streak."""

    global last_login_date, current_streak

    current_streak = max(value, 1)
    last_login_date = today_iso
    save()

def _update_login_streak() -> None:
    """Called once on registration of the addon, checks the current streak and updates it if the day ahs turned over."""

    global last_login_date, current_streak

    # Get the current date in ISO format
    today_str = datetime.date.today().isoformat()

    # If there is no last startup date, start fresh
    if not last_login_date:
        _set_streak(today_str)
        return

    # Otherwise, if there is a last startup date and it's today, do nothing
    if last_login_date == today_str:
        return

    # Otherwise, if today's date differs from the last startup date, check the gap
    last = datetime.date.fromisoformat(last_login_date)
    gap_days = (datetime.date.today() - last).days

    # If there was no gap, do nothing
    if gap_days <= 0:
        return

    # If it's been more than one day, reset the streak
    if gap_days > 1:
        _set_streak(today_str)
        return

    # Otherwise set the new streak total
    new_streak: int = current_streak + 1
    _set_streak(today_str, new_streak)

    # Emit event
    bpy.app.timers.register(_emit_startup_event, first_interval=0.3)

def _emit_startup_event() -> None:
    global current_streak

    manager.handle_event(AchievementEvent(
        type="startup",
        extra={"streak": current_streak},
    ))

def _on_process_exit() -> None:
    """Additional safety net to ensure progress is saved on Blender exit."""

    global total_seconds

    # Get the current time and calculate usage seconds, then save
    now = time.time()
    total_seconds += now - _last_tick_time
    save()

def _tick() -> float:
    """Fires a play time eevent and day rollver event for rerolling daily achievements."""
 
    global total_seconds, _last_tick_time
 
    # Get the current time
    now = time.time()
 
    # Check how much time has elapsed since the last tick
    elapsed = now - _last_tick_time
 
    # Now it's safe to update the stored tick time for next time
    _last_tick_time = now
 
    # Add elapsed time to total seconds, then save
    total_seconds += elapsed
    save()
 
    # Force the daily achievements to check the current day and update accordingly
    daily.check_for_new_day()
 
    # Add daily seconds for daily achievements to use
    daily.add_daily_seconds(elapsed)
 
    # Emit play time event
    manager.handle_event(AchievementEvent(
        type="playtime",
        extra={
            "total_seconds": total_seconds,
            "daily_seconds": daily.get_daily_seconds(),
        },
    ))
 
    return TICK_INTERVAL




def register():
    """Load save file and register timers."""

    global _last_tick_time

    load()
    _update_login_streak()
    _last_tick_time = time.time()

    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=TICK_INTERVAL, persistent=True)

    atexit.register(_on_process_exit)

def unregister():
    """Save total usage time and unregister timers."""

    global total_seconds, _last_tick_time

    # Flush whatever's accumulated since the last tick before shutting down
    now = time.time()
    total_seconds += now - _last_tick_time
    save()

    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)

    atexit.unregister(_on_process_exit)