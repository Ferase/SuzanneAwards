"""
The toast UI shown at the bottom-right of the 3D viewport when the user receives an achievement. Utilizes manager.add_unlock_listener() to hitchhike on the unlock event.
"""



import bpy
import blf
import gpu
from gpu_extras.batch import batch_for_shader

import os
import time

from . import manager
from .achievements._base import BlenderAchievement



# Settings
DURATION: float = 3.0
FADE_IN: float = 0.25
FADE_OUT: float = 0.75
BASE_TOAST_WIDTH: int = 280
BASE_TOAST_HEIGHT: int = 60
BASE_MARGIN: int = 20
BASE_SPACING: int = 10
BASE_PADDING_X: int = 14
BASE_HEADER_FONT_SIZE: int = 16
BASE_NAME_FONT_SIZE: int = 13
BASE_HEADER_Y_OFFSET: int = 30
BASE_NAME_Y_OFFSET: int = 14
TICK_INTERVAL: float = 0.05
BASE_ICON_SIZE: int = 40
BASE_ICON_TEXT_GAP: int = 12

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
ICON_PATH = os.path.join(ASSETS_DIR, "img", "default", "award.png")

# Toast state
_active_toasts: list[dict] = []
_draw_handle = None
_shader = None
_image_shader = None
_icon_image = None
_icon_texture = None



def _get_ui_scale() -> float:
    """Get the user's UI scale from their preferences and their OS pxiel density value."""

    system = bpy.context.preferences.system
    view = bpy.context.preferences.view
    return view.ui_scale * system.pixel_size

def _get_theme_colors():
    """Get the user's theme colors from their currently active theme."""

    ui_theme = bpy.context.preferences.themes[0].user_interface
    accent = ui_theme.wcol_tool.inner_sel[:3]
    normal = ui_theme.wcol_text.text[:3]
    return accent, normal

def _get_n_panel_width(context: bpy.types.Context) -> float:
    """Returns the current width of the 3D viewport's N-panel (the 'UI'
    region), or 0.0 if it's closed or can't be found.

    The N-panel isn't a separate region that shrinks the main viewport -
    it floats on top of it, drawn after the WINDOW region we draw the
    toast in. So region.width in _draw() stays full-width regardless of
    whether the N-panel is open, and doesn't help us avoid it - we have
    to look up the sidebar's own region directly from the area to know
    how much space it's actually occupying right now.

    A closed sidebar still exists in area.regions, but reports a
    width of 1 rather than 0 - treated as "closed" here."""

    area = context.area
    if area is None:
        return 0.0

    for region in area.regions:
        if region.type == 'UI':
            return float(region.width) if region.width > 1 else 0.0

    return 0.0

def _load_icon() -> None:
    """Load tha icon for the achievement."""

    global _icon_image, _icon_texture

    if not os.path.exists(ICON_PATH):
        print(f"[toast] Icon not found at {ICON_PATH}, toasts will draw without it.")
        return

    _icon_image = bpy.data.images.load(ICON_PATH, check_existing=True)
    _icon_texture = gpu.texture.from_image(_icon_image)

def _compute_alpha(elapsed: float) -> float:
    """Calculate the toast's alpha when fading in/out."""

    # Fade in calculation (runs if we're within the fade in time)
    if elapsed < FADE_IN:
        return elapsed / FADE_IN

    # Fade out calculation (runs if we're within the fade out time)
    if elapsed > DURATION - FADE_OUT:
        return max(0.0, (DURATION - elapsed) / FADE_OUT)

    # Full opacity during DURATION
    return 1.0

def _draw():
    """Draw the toast in the 3D viewport."""

    if not _active_toasts:
        return

    region = bpy.context.region
    if region is None:
        return

    now = time.time()

    scale = _get_ui_scale()
    accent_color, normal_color = _get_theme_colors()

    # Shift left by however much space the N-panel is currently taking
    # up, so the toast never ends up drawn underneath it. Read fresh
    # every draw call - resizing the sidebar takes effect immediately.
    n_panel_width = _get_n_panel_width(bpy.context)

    toast_width = BASE_TOAST_WIDTH * scale
    toast_height = BASE_TOAST_HEIGHT * scale
    margin = BASE_MARGIN * scale
    spacing = BASE_SPACING * scale
    padding_x = BASE_PADDING_X * scale
    header_font_size = round(BASE_HEADER_FONT_SIZE * scale)
    name_font_size = round(BASE_NAME_FONT_SIZE * scale)
    header_y_offset = BASE_HEADER_Y_OFFSET * scale
    name_y_offset = BASE_NAME_Y_OFFSET * scale
    icon_size = BASE_ICON_SIZE * scale
    icon_text_gap = BASE_ICON_TEXT_GAP * scale

    y = margin

    gpu.state.blend_set("ALPHA")

    for toast in _active_toasts:
        elapsed = now - toast["start"]
        if elapsed > DURATION:
            continue

        alpha = _compute_alpha(elapsed)
        x = region.width - toast_width - margin - n_panel_width

        verts = (
            (x, y), (x + toast_width, y),
            (x + toast_width, y + toast_height), (x, y + toast_height),
        )
        indices = ((0, 1, 2), (2, 3, 0))
        batch = batch_for_shader(_shader, 'TRIS', {"pos": verts}, indices=indices)
        _shader.bind()
        _shader.uniform_float("color", (0.08, 0.08, 0.08, 0.85 * alpha))
        batch.draw(_shader)

        # Award icon, vertically centered, fading with everything else
        if _icon_texture is not None:
            icon_x = x + padding_x
            icon_y = y + (toast_height - icon_size) / 2

            icon_verts = (
                (icon_x, icon_y), (icon_x + icon_size, icon_y),
                (icon_x + icon_size, icon_y + icon_size), (icon_x, icon_y + icon_size),
            )
            uvs = ((0, 0), (1, 0), (1, 1), (0, 1))
            icon_batch = batch_for_shader(
                _image_shader, 'TRI_FAN', {"pos": icon_verts, "texCoord": uvs}
            )
            _image_shader.bind()
            _image_shader.uniform_sampler("image", _icon_texture)
            _image_shader.uniform_float("color", (1.0, 1.0, 1.0, alpha))
            icon_batch.draw(_image_shader)

            text_x = icon_x + icon_size + icon_text_gap
        else:
            text_x = x + padding_x

        font_id = 0
        r1, g1, b1 = normal_color
        blf.position(font_id, text_x, y + toast_height - header_y_offset, 0)
        blf.size(font_id, header_font_size)
        blf.color(font_id, r1, g1, b1, alpha)
        blf.draw(font_id, toast["heading"])

        r2, g2, b2 = accent_color
        blf.position(font_id, text_x, y + name_y_offset, 0)
        blf.size(font_id, name_font_size)
        blf.color(font_id, r2, g2, b2, alpha)
        blf.draw(font_id, toast["name"])

        y += toast_height + spacing

    gpu.state.blend_set("NONE")

def _tick():
    """Handles redrawing the viewport and toasts if any are active, does nothing if no toasts are present."""

    # Get the active toasts
    global _active_toasts

    # Get the current time
    now = time.time()

    # Rebuild the list to clear out completed toasts
    _active_toasts = [t for t in _active_toasts if now - t["start"] <= DURATION]

    # Redraw
    _tag_redraw()

    return TICK_INTERVAL if _active_toasts else None

def _tag_redraw():
    """Handle redrawing when toasts are shown."""

    # Get the window manager
    wm = bpy.context.window_manager

    # If the window manager couldn't be retrieved, fail silently
    if wm is None:
        return

    # Redraw the 3D viewport tag
    for window in wm.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()

def show_toast(heading: str, name: str, start_offset: float = 0.0) -> None:
    """Display a toast."""

    # Get the active toasts
    global _active_toasts

    # Add to active toasts
    _active_toasts.append({"heading": heading, "name": name, "start": time.time() + start_offset})

    # Register the toast ticker if it isn't already
    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=0.0, persistent=True)

    # Redraw UI
    _tag_redraw()

def _on_unlock(instance: BlenderAchievement, current_level, levels_gained: int):
    """Shows toast on unlock, attached to the manager using manager.add_unlock_listener()."""

    show_toast(
        "You got an award!",
        instance.NAME
    )

    if levels_gained:
        heading: str = "You levelled up!"
        num_levels_earned: int = len(levels_gained)
        if num_levels_earned > 1:
            heading = f"You earned {num_levels_earned} levels!"

        bpy.app.timers.register(
            lambda: show_toast(
                heading,
                f"Level {current_level}"),
                first_interval=2.0,
                persistent=True
            )



def register():
    """Register the toast and its shaders."""

    global _shader, _image_shader, _draw_handle

    _shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    _image_shader = gpu.shader.from_builtin("IMAGE_COLOR")
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(_draw, (), 'WINDOW', 'POST_PIXEL')

    # Deferred - see _load_icon() docstring
    bpy.app.timers.register(_load_icon, first_interval=0.0, persistent=True)

    manager.add_unlock_listener(_on_unlock)

def unregister():
    """Unregister the toast and its shaders."""

    global _draw_handle, _icon_image, _icon_texture

    if _draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, "WINDOW")
        _draw_handle = None

    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)

    if _icon_image is not None:
        bpy.data.images.remove(_icon_image)
        _icon_image = None
    _icon_texture = None

    _active_toasts.clear()