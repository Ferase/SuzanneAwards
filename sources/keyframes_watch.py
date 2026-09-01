"""
Watches for various animation-related actions.

## Events Fired

### animation_playback_start
The animation play back was started.

### animation_playback_stop
The animation play back was stopped.

### frame_change
The active frame on the timeline was changed.
"""



import bpy

from .. import manager
from ..events import AchievementEvent



def _on_animation_playback_pre(dummy) -> None:
    """Fires whenever the user starts playing an animation."""

    manager.handle_event(AchievementEvent(type="animation_playback_start"))

def _on_animation_playback_post(dummy) -> None:
    """Fires whenever the user stops playing an animation."""

    manager.handle_event(AchievementEvent(type="animation_playback_stop"))

def _on_frame_change(dummy) -> None:
    """Fires whenever the active animation frame index changes."""

    manager.handle_event(AchievementEvent(type="frame_change", extra={"frame": bpy.context.scene.frame_current}))



def register():
    """Register handlers."""

    if _on_animation_playback_pre not in bpy.app.handlers.animation_playback_pre:
        bpy.app.handlers.animation_playback_pre.append(_on_animation_playback_pre)

    if _on_animation_playback_post not in bpy.app.handlers.animation_playback_post:
        bpy.app.handlers.animation_playback_post.append(_on_animation_playback_post)

    if _on_frame_change not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(_on_frame_change)

def unregister():
    """Unregister handlers."""

    if _on_animation_playback_pre in bpy.app.handlers.animation_playback_pre:
        bpy.app.handlers.animation_playback_pre.remove(_on_animation_playback_pre)

    if _on_animation_playback_post in bpy.app.handlers.animation_playback_post:
        bpy.app.handlers.animation_playback_post.remove(_on_animation_playback_post)

    if _on_frame_change in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(_on_frame_change)