"""
Watches for various render-related actions.

## Events Fired

### render_start
A render job has begun.

### render_write
A render job has saved a rendered frame, fires after each frame renders regardless of if the final file is a single image, image sequence, or FFMpeg movie.

### render_complete
A render job has completed successfully. Contains the properties of the render job extra values.

### render_cancel
A render job has been cancelled by the user. Contains the properties of the render job in the extra values.

### composite_start
A render job's compositing phase has started for one of its frames.

### composite_complete
A render job's compositing phase completed successfully.

### composite_cancel
A render job's compositing phase was cancelled by the user.
"""



import bpy

from .. import manager
from ..events import AchievementEvent

# Track render properties to be set on render init
_frame_count: int = 0
_render_engine: str = ""
_render_format: str = ""
_resolution_percentage: int = 100



def _reset_properties() -> None:
    """Resets tracked render properties. Used after a render has completed to avoid storing stale values."""

    global _frame_count, _render_engine, _render_format, _resolution_percentage

    _frame_count = 0
    _render_engine = ""
    _render_format = ""
    _resolution_percentage = 100

def _on_render_init(dummy) -> None:
    """Fires whenever a render job starts."""

    global _frame_count, _render_engine, _render_format, _resolution_percentage

    # Grab current render properties
    _frame_count = 0
    _render_engine = bpy.context.scene.render.engine
    _render_format = bpy.context.scene.render.image_settings.file_format
    _resolution_percentage = bpy.context.scene.render.resolution_percentage

    # Emit event
    manager.handle_event(AchievementEvent(type="render_start"))

def _on_render_write(dummy) -> None:
    """Fires whenever a render job writes an image. Fires regardless of if the render is a single image or FFMpeg movie render."""

    global _frame_count

    # Add a frame to the frame count since we would be incrementing to the next frame
    _frame_count += 1
    manager.handle_event(AchievementEvent(type="render_write"))

def _on_render_complete(dummy) -> None:
    """Fires whenever a render job completes successfully.
    
    Also sends the render's properties in the extra values. """

    global _frame_count, _render_engine, _render_format, _resolution_percentage

    # Emit event with properties
    manager.handle_event(AchievementEvent(type="render_complete", extra={
        "frames": _frame_count,
        "render_engine": _render_engine,
        "render_format": _render_format,
        "resolution_percentage": _resolution_percentage
    }))

    # Revert values
    _reset_properties()

def _on_render_cancel(dummy) -> None:
    """Fires whenever a render job is cancelled by the user.
    
    Also sends the render's properties in the extra values. """

    global _frame_count, _render_engine, _render_format, _resolution_percentage

    # Emit event with properties
    manager.handle_event(AchievementEvent(type="render_cancel", extra={
        "frames": _frame_count,
        "render_engine": _render_engine,
        "render_format": _render_format,
        "resolution_percentage": _resolution_percentage
    }))

    # Revert values
    _reset_properties()

def _on_composite_pre(dummy) -> None:
    """Fires whenever the render job's compositing phase has started."""

    # Emit event
    manager.handle_event(AchievementEvent(type="composite_start"))

def _on_composite_post(dummy) -> None:
    """Fires whenever the render job's compositing phase has completed successfully."""

    # Emit event
    manager.handle_event(AchievementEvent(type="composite_complete"))

def _on_composite_cancel(dummy) -> None:
    """Fires whenever the render job's compositing phase was cancelled by the user."""

    # Emit event
    manager.handle_event(AchievementEvent(type="composite_cancel"))



def register():
    """Register handlers."""

    if _on_render_init not in bpy.app.handlers.render_init:
        bpy.app.handlers.render_init.append(_on_render_init)

    if _on_render_write not in bpy.app.handlers.render_write:
        bpy.app.handlers.render_write.append(_on_render_write)

    if _on_render_complete not in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.append(_on_render_complete)

    if _on_render_cancel not in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.append(_on_render_cancel)

    if _on_composite_pre not in bpy.app.handlers.composite_pre:
        bpy.app.handlers.composite_pre.append(_on_composite_pre)

    if _on_composite_post not in bpy.app.handlers.composite_post:
        bpy.app.handlers.composite_post.append(_on_composite_post)

    if _on_composite_cancel not in bpy.app.handlers.composite_cancel:
        bpy.app.handlers.composite_cancel.append(_on_composite_cancel)

def unregister():
    """Unregister handlers."""

    if _on_render_init in bpy.app.handlers.render_init:
        bpy.app.handlers.render_init.remove(_on_render_init)

    if _on_render_write in bpy.app.handlers.render_write:
        bpy.app.handlers.render_write.remove(_on_render_write)

    if _on_render_complete in bpy.app.handlers.render_complete:
        bpy.app.handlers.render_complete.remove(_on_render_complete)

    if _on_render_cancel in bpy.app.handlers.render_cancel:
        bpy.app.handlers.render_cancel.remove(_on_render_cancel)

    if _on_composite_pre in bpy.app.handlers.composite_pre:
        bpy.app.handlers.composite_pre.remove(_on_composite_pre)

    if _on_composite_post in bpy.app.handlers.composite_post:
        bpy.app.handlers.composite_post.remove(_on_composite_post)

    if _on_composite_cancel in bpy.app.handlers.composite_cancel:
        bpy.app.handlers.composite_cancel.remove(_on_composite_cancel)