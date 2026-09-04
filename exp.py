"""
Subsystem for tracking and incrementing the user's EXP as they earn achievements.
"""



import os
import bpy
import json
from typing import Any

from .achievements._base import BlenderAchievement, AchievementKind

# Required EXP to level up to level 2
BASE_EXP_TO_LEVEL: int = 100

# The amount by which the requried EXP to level up increases linearly
EXP_INCREMENT_PER_LEVEL: int = 25

# EXP state save file name
SAVE_FILENAME: str = "achievement_exp.json"

# Current level
level: int = 1

# EXP within the current level
exp: int = 0

# EXP all-time total
exp_total: int = 0

# Boost multiplier
daily_boost_multiplier: int = 1



def exp_required_for_level(lvl: int) -> int:
    """Calculate EXP threshold required to advance from the given level to the next one."""

    return BASE_EXP_TO_LEVEL + EXP_INCREMENT_PER_LEVEL * (lvl - 1)

def get_save_path() -> str:
    """Get the EXP state save fiel path within Blender's config directory."""

    # Get the Blender config
    cfg_dir = bpy.utils.user_resource("CONFIG")
    return os.path.join(cfg_dir, SAVE_FILENAME)

def load() -> None:
    """Load EXP and level from the EXP save file."""

    global level, exp, exp_total, daily_boost_multiplier

    # Get the EXP save file path
    path = get_save_path()

    # If the save file doesn't exist, set to default values
    if not os.path.exists(path):
        level = 1
        exp = 0
        exp_total = 0
        daily_boost_multiplier = 1
        return

    # Otherwise, open the save file and get the JSON data
    with open(path, "r") as f:
        data: dict[str, Any] = json.load(f)

    # Set the level and EXP
    level = data.get("level", 1)
    exp = data.get("exp", 0)
    exp_total = data.get("exp_total", 0)
    daily_boost_multiplier = data.get("daily_boost_multiplier", 1)

def save() -> None:
    """Save EXP and level to the EXP save file."""

    # Write JSON file
    with open(get_save_path(), "w") as f:
        json.dump({
            "level": level,
            "exp": exp,
            "exp_total": exp_total,
            "daily_boost_multiplier": daily_boost_multiplier
        }, f, indent=2)

def get_current_level() -> int:
    return level

def increase_multiplier(amount: int = 1):
    """Increases the daily boost multiplier."""

    global daily_boost_multiplier

    daily_boost_multiplier += amount
    save()

def calculate_multiplied_exp(base_amount: int) -> int:
    return base_amount * daily_boost_multiplier

def add_exp(instance: BlenderAchievement) -> list[int]:
    """Add EXP to the user's current EXP. Level up the user if the EXP exceeds the level threshold, do so for as many levels the user surpasses."""

    global level, exp, exp_total

    # Initialize a list of levels gained
    levels_gained: list[int] = []

    # Get amount
    amount: int = instance.EXP

    # If the achievement is a daily achievement, apply the multiplier
    if instance.KIND == AchievementKind.DAILY:
        amount = calculate_multiplied_exp(amount)

    # Increment EXP counters
    exp += amount
    exp_total += amount

    # Get the threshold of EXP for the next level
    threshold = exp_required_for_level(level)

    # If the EXP is greater than the threshold, continuously subtract the threshold, add levels, and redefine the threshold until the EXP falls below the new threshold
    while exp >= threshold:
        exp -= threshold
        level += 1
        levels_gained.append(level)
        threshold = exp_required_for_level(level)

    # Save the EXP save file
    save()
    return levels_gained

def get_progress_fraction() -> float:
    """Calculates a normalized 0.0-1.0 value to represent how far along the user is on their current level. Used for the UI progress bar."""

    # Get the current threshold and calculate the current EXP value's percentage of it
    threshold = exp_required_for_level(level)
    return exp / threshold if threshold > 0 else 0.0