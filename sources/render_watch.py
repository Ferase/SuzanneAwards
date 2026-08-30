"""
"""



import os

import bpy

from .. import manager
from ..events import AchievementEvent

_frame_count: int = 0
_render_engine: str = ""
_render_format: str = ""
_resolution_percentage: int = 100



def _on_render_init(dummy) -> None:
    global _frame_count, _render_engine, _render_format, _resolution_percentage

    render_settings = bpy.context.scene.render.image_settings

    _frame_count = 0
    _render_engine = bpy.context.scene.render.engine
    _render_format = render_settings.file_format
    _resolution_percentage = bpy.context.scene.render.resolution_percentage

    manager.handle_event(AchievementEvent(type="render_start"))

def _on_render_write(dummy) -> None:
    global _frame_count

    _frame_count += 1
    manager.handle_event(AchievementEvent(type="render_write"))

def _on_render_complete(dummy) -> None:
    global _frame_count, _render_engine, _render_format, _resolution_percentage

    manager.handle_event(AchievementEvent(type="render_complete", extra={
        "frames": _frame_count,
        "render_engine": _render_engine,
        "render_format": _render_format,
        "resolution_percentage": _resolution_percentage
    }))
    _frame_count = 0

def _on_render_cancel(dummy) -> None:
    global _frame_count, _render_engine, _render_format, _resolution_percentage

    manager.handle_event(AchievementEvent(type="render_complete", extra={
        "frames": _frame_count,
        "render_engine": _render_engine,
        "render_format": _render_format,
        "resolution_percentage": _resolution_percentage
    }))
    _frame_count = 0

def _on_composite_pre(dummy) -> None:
    manager.handle_event(AchievementEvent(type="composite_start"))

def _on_composite_post(dummy) -> None:
    manager.handle_event(AchievementEvent(type="composite_complete"))

def _on_composite_cancel(dummy) -> None:
    manager.handle_event(AchievementEvent(type="composite_cancel"))

def register():
    """Register the load_post/save_pre/save_post handlers."""

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
    """Unregister the load_post/save_pre/save_post handlers."""

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