"""
"""



from datetime import date

import bpy

from .. import manager
from ..events import AchievementEvent



def _on_animation_playback_post(dummy) -> None:
    manager.handle_event(AchievementEvent(type="animation_playback"))

def _on_frame_change(dummy) -> None:
    manager.handle_event(AchievementEvent(type="frame_change", extra={"frame", bpy.context.scene.frame_current}))



def register():
    """Register the load_post/save_pre/save_post handlers."""

    if _on_animation_playback_post not in bpy.app.handlers.animation_playback_post:
        bpy.app.handlers.animation_playback_post.append(_on_animation_playback_post)

    if _on_frame_change not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(_on_frame_change)

def unregister():
    """Unregister the load_post/save_pre/save_post handlers."""

    if _on_animation_playback_post in bpy.app.handlers.animation_playback_post:
        bpy.app.handlers.animation_playback_post.remove(_on_animation_playback_post)

    if _on_frame_change in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(_on_frame_change)