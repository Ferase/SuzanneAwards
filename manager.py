"""
Owns the live achievement instances - both global (always active) and
daily (only today's selected subset gets instantiated at all; anything
not chosen today never appears in _instances, so dispatch doesn't need
to special-case kind). Sources call handle_event() for every normalized
event; dispatches to every not-yet-unlocked instance.
"""



import bpy

from . import state
from . import daily
from . import exp
from .achievements._base import BlenderAchievement
from .achievements.global_achievements import GLOBAL_ACHIEVEMENT_CLASSES
from .achievements.daily_achievements import DAILY_ACHIEVEMENT_CLASSES

_instances: dict[str, BlenderAchievement] = {}
_unlock_listeners = []



def init_achievements() -> None:
    """Instantiate every global achievement, plus only today's selected
    daily achievements. Called on addon register, and again whenever
    daily.py detects a new day."""

    global _instances
    _instances = {}

    # Global - always active
    for cls in GLOBAL_ACHIEVEMENT_CLASSES:
        instance = cls()
        instance.load_progress(state.progress.get(cls.ID))
        instance._on_persist = _persist
        instance._on_unlock = _notify_unlock
        _instances[cls.ID] = instance

    # Daily - only today's selection gets an instance at all
    rng = daily.get_rng()
    for cls in DAILY_ACHIEVEMENT_CLASSES:
        if not daily.is_active_today(cls.ID):
            continue

        instance = cls()
        instance.pick_goal(rng)
        instance.get_desc()
        instance.load_progress(state.progress.get(cls.ID))
        instance._on_persist = _persist
        instance._on_unlock = _notify_unlock
        _instances[cls.ID] = instance

def get_instances() -> dict:
    """Get all loaded achievement instances."""

    return _instances

def add_unlock_listener(func) -> None:
    """When an achievement unlock is triggered, func(achievement_instance, levels_gained) will be run. levels_gained is a list of levels reached (empty if the EXP awarded didn't cross a level threshold)."""

    _unlock_listeners.append(func)

def handle_event(event) -> None:
    """Runs when an event is heard, checks through locked achievements and triggers them so they can evaluate progress."""

    for instance in _instances.values():
        if instance.unlocked:
            continue
        instance.triggered(event)

def _persist(instance) -> None:
    """Save achievement progress and redraw N-panel data for that achievement."""

    state.progress[instance.ID] = instance.to_dict()
    state.save()
    _tag_redraw()

def _notify_unlock(instance) -> None:
    """Award EXP, then notify all unlock listeners. EXP is awarded
    regardless of achievement kind - a daily achievement resetting its
    unlock state tomorrow doesn't take back EXP already earned today."""

    levels_gained = exp.add_exp(instance.EXP)

    for listener in _unlock_listeners:
        listener(instance, levels_gained)

    _tag_redraw()

def _tag_redraw() -> None:
    """Called whenever achievement or EXP state changes, forces the N-panel display to redraw so it accurately updates."""

    wm = bpy.context.window_manager
    if wm is None:
        return

    for window in wm.windows:
        for area in window.screen.areas:
            area.tag_redraw()
