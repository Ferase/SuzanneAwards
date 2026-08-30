"""
Detects two things operator_poll.py structurally can't: opening a
project, and saving one - testing confirms wm.save_mainfile, like
ed.undo, never gets recorded into wm.operators (likely for the same
reason: there's no "adjust last operation" panel for either, so
Blender doesn't bother tracking them in the operator-redo history).

OPEN: bpy.app.handlers.load_post fires after ANY file load, including
File > New. Filtered down to genuine opens by checking bpy.data.filepath:
a brand new, unsaved file always has an empty filepath, an opened
.blend always has its real one.

SAVE: bpy.app.handlers.save_post fires after any save completes -
regular, Save As, or Save Copy - but its callback doesn't say which,
and losing wm.operators means the "copy" property isn't reachable
either. bpy.data.is_dirty does NOT work as a substitute - it just means
"unsaved changes exist" and gets cleared by ANY successful save, copy
included (confirmed by testing).

What actually distinguishes Save Copy: it deliberately does NOT write
to bpy.data.filepath - the copy goes to a different path entirely,
leaving the currently-open document's own file completely untouched.
So: snapshot that file's mtime in save_pre, compare it in save_post.
  - Regular save/re-save: bpy.data.filepath's file WAS just rewritten.
  - Save As: bpy.data.filepath changes to the new path, and THAT file
    was just written.
  - Save Copy: bpy.data.filepath is unchanged, and its file's mtime is
    unchanged too, since nothing was written there this time.
  - First-ever save of a never-saved file: bpy.data.filepath goes from
    empty to populated for a real save; a Save Copy on a never-saved
    file leaves it empty even after completing.

Known limitation: relies on filesystem mtime resolution being finer
than how long a save takes. True on effectively all filesystems in
common use today, but a very coarse-grained filesystem clock could
theoretically make a fast genuine resave look unchanged.

All three handlers need @persistent to survive a subsequent
File>New/Open themselves, same reasoning as undo_redo_watch.py.
"""



import os

import bpy
from bpy.app.handlers import persistent

from .. import manager
from ..events import AchievementEvent

# Snapshot taken in save_pre, read back in save_post
_filepath_before_save: str = ""
_mtime_before_save: float | None = None



@persistent
def _on_load_post(dummy) -> None:
    """Runs after any file load. Only counted as a genuine "project
    opened" event if the loaded file actually has a path."""

    if bpy.data.filepath:
        manager.handle_event(AchievementEvent(type="file_open"))

@persistent
def _on_save_pre(dummy) -> None:
    """Snapshot the current filepath and its on-disk mtime before the
    save happens, so save_post can tell whether that specific file
    actually got rewritten."""

    global _filepath_before_save, _mtime_before_save

    _filepath_before_save = bpy.data.filepath

    if _filepath_before_save and os.path.exists(_filepath_before_save):
        _mtime_before_save = os.path.getmtime(_filepath_before_save)
    else:
        _mtime_before_save = None

@persistent
def _on_save_post(dummy) -> None:
    """Runs after any save completes - regular, Save As, or Save Copy.
    See module docstring for how is_copy is determined."""

    filepath_after = bpy.data.filepath

    if not filepath_after:
        # Still no real filepath even after a completed save - only
        # happens via Save Copy on a file that's never been saved
        is_copy = True
    elif filepath_after != _filepath_before_save:
        # Save As - filepath changed, meaning a brand new file was
        # just written at the new path
        is_copy = False
    else:
        # Same filepath as before - only a genuine save/re-save
        # actually rewrites it; Save Copy leaves it untouched
        current_mtime = os.path.getmtime(filepath_after) if os.path.exists(filepath_after) else None
        is_copy = (current_mtime == _mtime_before_save)

    manager.handle_event(AchievementEvent(type="file_save", extra={"is_copy": is_copy}))

def _on_blend_import_post(dummy) -> None:
    manager.handle_event(AchievementEvent(type="file_blend_import"))

def register():
    """Register the load_post/save_pre/save_post handlers."""

    if _on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load_post)

    if _on_save_pre not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(_on_save_pre)

    if _on_save_post not in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.append(_on_save_post)

    if _on_blend_import_post not in bpy.app.handlers.blend_import_post:
        bpy.app.handlers.blend_import_post.append(_on_blend_import_post)

def unregister():
    """Unregister the load_post/save_pre/save_post handlers."""

    if _on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load_post)

    if _on_save_pre in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(_on_save_pre)

    if _on_save_post in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(_on_save_post)

    if _on_blend_import_post in bpy.app.handlers.blend_import_post:
        bpy.app.handlers.blend_import_post.remove(_on_blend_import_post)