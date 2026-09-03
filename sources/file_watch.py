"""
Watches for various file-related actions.

## Events Fired

### file_new
A new project was started.

### file_open
A project file was opened.

### file_save
A project file was saved.

### file_blend_import
A project's assets were appended to the active project.
"""



import os

import bpy
from bpy.app.handlers import persistent

from .. import manager
from ..events import AchievementEvent

# Track save path ans dave time to determine whetehr a project was saved as a copy
_filepath_before_save: str = ""
_mtime_before_save: float | None = None

# Track the first startup to avoid double-calling _on_load_post()
_first_startup: bool = False



@persistent
def _on_load_post(dummy) -> None:
    """Fires whenever the suer starts a new project or opens a project file."""

    global _first_startup

    # Skip once
    if _first_startup == False:
        _first_startup == True
        return

    # If a filepath is specified, we have opened a file
    if bpy.data.filepath:
        manager.handle_event(AchievementEvent(type="file_open"))
        return

    # Otherwise, we've started a new project
    manager.handle_event(AchievementEvent(type="file_new"))

@persistent
def _on_save_pre(dummy) -> None:
    """Fires BEFORE the user saves a project file or saves a copy of a project file. This prepares variables to identify exactly which of the two saves the user made."""

    global _filepath_before_save, _mtime_before_save

    # Determine current file path before saving
    _filepath_before_save = bpy.data.filepath

    # Set the time before saved
    if _filepath_before_save and os.path.exists(_filepath_before_save):
        _mtime_before_save = os.path.getmtime(_filepath_before_save)
        return

    # Reset time before saved
    _mtime_before_save = None

@persistent
def _on_save_post(dummy) -> None:
    """Fires AFTER the user saves a project file or saves a copy of a project file."""

    global _filepath_before_save

    # Get current filepath after save
    filepath_after = bpy.data.filepath

    is_copy: bool = False
    is_new_save: bool = False

    # If there's no filepath, then a copy of a new, unsaved project was saved
    if not filepath_after:
        is_copy = True
        is_new_save = True

    # If the filepath before saving is different from the filepath after saving, it was saved normally
    elif filepath_after != _filepath_before_save:
        is_copy = False
        is_new_save = True

    # Otherwise, a copy of a saved project was saved because the time wouldn't have changed.
    else:
        current_mtime = os.path.getmtime(filepath_after) if os.path.exists(filepath_after) else None
        result: bool = (current_mtime == _mtime_before_save)
        is_copy = result
        is_new_save = result

    # Emit event
    manager.handle_event(AchievementEvent(type="file_save", extra={"is_copy": is_copy, "is_new_save": is_new_save}))

def _on_blend_import_post(dummy) -> None:
    """Fires when the user appends data to the active project file."""

    manager.handle_event(AchievementEvent(type="file_blend_import"))



def register():
    """Register all handlers."""

    global _first_startup
    _first_startup = False

    if _on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load_post)

    if _on_save_pre not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(_on_save_pre)

    if _on_save_post not in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.append(_on_save_post)

    if _on_blend_import_post not in bpy.app.handlers.blend_import_post:
        bpy.app.handlers.blend_import_post.append(_on_blend_import_post)

def unregister():
    """Unregister all handlers."""

    if _on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load_post)

    if _on_save_pre in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(_on_save_pre)

    if _on_save_post in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(_on_save_post)

    if _on_blend_import_post in bpy.app.handlers.blend_import_post:
        bpy.app.handlers.blend_import_post.remove(_on_blend_import_post)