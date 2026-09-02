"""
Subsystem that manages achievement instances.
"""



import bpy

from . import state
from . import daily
from . import exp
from .events import AchievementEvent
from .achievements._base import BlenderAchievement
from .achievements.global_achievements import GLOBAL_ACHIEVEMENT_CLASSES
from .achievements.daily_achievements import DAILY_ACHIEVEMENT_CLASSES

# Track achievements and listeners
_instances: dict[str, BlenderAchievement] = {}
_unlock_listeners = []



def init_achievements() -> None:
    """Instantiates and initializes all achievements"""

    global _instances

    # Initialize instance container dictionary
    _instances = {}

    # Instantiate and initialize global achievements
    for cls in GLOBAL_ACHIEVEMENT_CLASSES:
        # Create achievement instance
        instance = cls()

        # Load achievement progress
        instance.load_progress(state.progress.get(cls.ID))

        # Hook functions to the achievement
        instance._on_persist = _persist
        instance._on_unlock = _notify_unlock

        # Add the instance to the instance dict
        _instances[cls.ID] = instance

    # Grab the random seed for today
    rng = daily.get_rng()

    # Instantiate adn initialize all eligable daily achievements
    for cls in DAILY_ACHIEVEMENT_CLASSES:
        # If the achievement wasn't chosen for today, skip it
        if not daily.is_active_today(cls.ID):
            continue

        # Create achievement instance
        instance = cls()

        # Randomly pick a goal if the achievement uses GOAL_VARIANTS
        instance.pick_goal(rng)

        # Set the description of the achievement, replace any instance of goal_label
        instance.get_desc()

        # Load achievement progress
        instance.load_progress(state.progress.get(cls.ID))

        # Hook functions to the achievement
        instance._on_persist = _persist
        instance._on_unlock = _notify_unlock

        # Add the instance to the instance dict
        _instances[cls.ID] = instance

def get_instances() -> dict:
    """Get all loaded achievement instances."""

    return _instances

def add_unlock_listener(func) -> None:
    """When an achievement unlock is triggered, func(achievement_instance, current_level, levels_gained) will be run."""

    _unlock_listeners.append(func)

def handle_event(event: AchievementEvent) -> None:
    """Runs when an event is heard.
    
    Does nothing on unlocked achievements."""

    # Iterate through each achievement
    for instance in _instances.values():
        # If teh achievement is unlocked, do nothing
        if instance.unlocked:
            continue

        # Otherwise, run progression logic
        instance.triggered(event)

def _persist(instance: BlenderAchievement) -> None:
    """Save achievement progress and redraw N-panel data for that achievement."""

    # Convert current achievement state to a dictionary
    state.progress[instance.ID] = instance.to_dict()

    # Save achievement progress to the save file
    state.save()

    # Redraw the N-panel UI
    _tag_redraw()

def _notify_unlock(instance: BlenderAchievement) -> None:
    """Runs when an achievement meets the criteria to be unlocked. Awards EXP, then runs all unlock listeners."""

    # Add EXP and determine levels gained
    levels_gained: list[str] = exp.add_exp(instance.EXP)

    # Get current level
    current_level: int = exp.get_current_level()

    # Run assigned unlock listeners
    for listener in _unlock_listeners:
        listener(instance, current_level, levels_gained)

    # Redraw N-panel UI
    _tag_redraw()

def _tag_redraw() -> None:
    """Called whenever achievement or EXP state changes, forces the N-panel display to redraw so it accurately updates."""

    # Get Blender's window manager
    wm: bpy.types.WindowManager = bpy.context.window_manager
    if wm is None:
        return

    # Redraw areas within the window
    for window in wm.windows:
        for area in window.screen.areas:
            area.tag_redraw()
