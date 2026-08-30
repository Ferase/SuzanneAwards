"""
Watches for undo completions using bpy.app.handlers.undo_post. This exists because bpy.ops.ed.undo never gets recorded into wm.operators - Blender's undo stack is managed separately from the normal operator history, so operator_poll.py can never see it fire, no matter how it's triggered (Ctrl+Z, menu, etc).

Also filters out a specific false positive: editing a value in the "adjust last operation" (redo) panel and confirming it fires undo_post too. Three earlier approaches to telling the two apart didn't hold up:
  1. Pairing undo_post with an expected redo_post - doesn't fire for this path at all, since the redo panel re-executes the operator rather than performing a genuine redo.
  2. Watching for any depsgraph_update_post in a short window after - false-triggered on the undo's OWN settling update, which lands in that window just as reliably as a real re-execution would.
  3. Comparing bpy.context.window_manager.operators counts before/after, read directly inside these handlers - unreliable, since wm.operators isn't trustworthy from inside undo_pre/undo_post callbacks at all (same category of restricted-context issue as the _RestrictData problem toast.py hit during register()).

Current approach: operator_poll.py reads wm.operators from a bpy.app.timers callback, which IS reliable, and already detects in-place edits to the top-of-history entry (see its get_last_redo_panel_adjustment_time()). This module just asks operator_poll whether it saw one recently, rather than reading wm.operators itself.
"""



import time

import bpy
from bpy.app.handlers import persistent

from .. import manager
from ..events import AchievementEvent
from . import operator_poll

# True from the moment undo_post fires until we've confirmed (a short
# while later) whether it was actually a redo-panel edit
_pending_undo: bool = False

# Has to comfortably outlast operator_poll's own POLL_INTERVAL, since
# operator_poll needs at least one of its own poll ticks to notice a
# redo-panel edit before we can ask it about one
PENDING_UNDO_WINDOW: float = operator_poll.POLL_INTERVAL + 0.2



@persistent
def _on_undo_post(scene) -> None:
    """Runs after any undo completes - genuine or as the first half of a redo-panel edit. Don't emit the achievement-facing event yet; wait out PENDING_UNDO_WINDOW so operator_poll has a chance to notice a possible in-place edit first."""

    global _pending_undo

    _pending_undo = True

    if not bpy.app.timers.is_registered(_resolve_pending_undo):
        bpy.app.timers.register(_resolve_pending_undo, first_interval=PENDING_UNDO_WINDOW, persistent=True)

def _resolve_pending_undo() -> None:
    """Runs after PENDING_UNDO_WINDOW. Asks operator_poll whether it saw a redo-panel-style in-place edit during that window - if so, this was a redo-panel edit, suppress. Otherwise it's a genuine undo - emit it now."""

    global _pending_undo

    if _pending_undo:
        adjustment_age = time.time() - operator_poll.get_last_redo_panel_adjustment_time()

        if adjustment_age < PENDING_UNDO_WINDOW:
            print("undo suppressed (adjust-last-operation panel)")
        else:
            print("undo")
            manager.handle_event(AchievementEvent(type="undo"))

    _pending_undo = False
    return None  # one-shot, don't reschedule

@persistent
def _on_redo_post(scene) -> None:
    """Runs after a genuine redo (Ctrl+Shift+Z / Redo menu)."""

    print("redo")
    manager.handle_event(AchievementEvent(type="redo"))

def register():
    """Register the undo and redo handlers."""

    global _pending_undo
    _pending_undo = False

    if _on_undo_post not in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.append(_on_undo_post)

    if _on_redo_post not in bpy.app.handlers.redo_post:
        bpy.app.handlers.redo_post.append(_on_redo_post)

def unregister():
    """Unregister the undo and redo handlers."""

    if _on_undo_post in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.remove(_on_undo_post)

    if _on_redo_post in bpy.app.handlers.redo_post:
        bpy.app.handlers.redo_post.remove(_on_redo_post)

    if bpy.app.timers.is_registered(_resolve_pending_undo):
        bpy.app.timers.unregister(_resolve_pending_undo)