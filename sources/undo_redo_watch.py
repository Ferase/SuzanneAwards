"""
Watches for various undo/redo-related actions.

## Events Fired

### undo
An action was undone.

### redo
An action was redone.
"""



import time

import bpy
from bpy.app.handlers import persistent

from .. import manager
from ..events import AchievementEvent
from . import operator_poll

# Used to check timing and ensure an undo doesn't get lumped in with the modify panel's undo-redo logic
_pending_undo: bool = False

# The window used for the timer to detect whether the undo was a real undo and not a result of the modify panel's undo-redo logic
PENDING_UNDO_WINDOW: float = operator_poll.POLL_INTERVAL + 0.2



@persistent
def _on_undo_post(scene) -> None:
    """Firues when an undo is processed in any way, including by the modify last action panel."""

    global _pending_undo

    # We're waiting for an undo
    _pending_undo = True

    # Set up the timer if it isn't set up already
    if not bpy.app.timers.is_registered(_resolve_pending_undo):
        bpy.app.timers.register(_resolve_pending_undo, first_interval=PENDING_UNDO_WINDOW, persistent=True)

def _resolve_pending_undo() -> None:
    """The actual emitter for an undo event."""

    global _pending_undo

    # If we're waiting for an undo, check whether it is valid to emit it.
    if _pending_undo:
        # Check the age of the action to see whetehr or not it is safe to emit the event
        adjustment_age = time.time() - operator_poll.get_last_redo_panel_adjustment_time()

        # If we're too early for our window, do nothing
        if adjustment_age < PENDING_UNDO_WINDOW:
            return

        # Emit event otherwise
        manager.handle_event(AchievementEvent(type="undo"))

    # Reset the pending undo tracker
    _pending_undo = False
    return

@persistent
def _on_redo_post(scene) -> None:
    """Fires whenevr a redo is processed."""

    # Emit event
    manager.handle_event(AchievementEvent(type="redo"))

def register():
    """Register handlers."""

    global _pending_undo
    _pending_undo = False

    if _on_undo_post not in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.append(_on_undo_post)

    if _on_redo_post not in bpy.app.handlers.redo_post:
        bpy.app.handlers.redo_post.append(_on_redo_post)

def unregister():
    """Unregister handlers."""

    if _on_undo_post in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.remove(_on_undo_post)

    if _on_redo_post in bpy.app.handlers.redo_post:
        bpy.app.handlers.redo_post.remove(_on_redo_post)

    if bpy.app.timers.is_registered(_resolve_pending_undo):
        bpy.app.timers.unregister(_resolve_pending_undo)