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



# Achievement toast settings
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

# Level-up toast settings
LEVELUP_BASE_WIDTH: int = 320
LEVELUP_BASE_ICON_SIZE: int = BASE_ICON_SIZE * 2
LEVELUP_BASE_PADDING_TOP: int = 18
LEVELUP_BASE_PADDING_BOTTOM: int = 16
LEVELUP_BASE_ICON_TEXT_GAP: int = 12
LEVELUP_BASE_LINE_GAP: int = 8
LEVELUP_BASE_TOP_FONT_SIZE: int = 20
LEVELUP_BASE_BOTTOM_FONT_SIZE: int = 15

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
ICON_PATH = os.path.join(ASSETS_DIR, "img", "default", "award.png")
LEVELUP_ICON_PATH = os.path.join(ASSETS_DIR, "img", "default", "levelup.png")

# Toast state
_active_toasts: list[dict] = []
_draw_handle = None
_shader = None
_image_shader = None
_icon_image = None
_icon_texture = None
_levelup_icon_image = None
_levelup_icon_texture = None
_levelup_queue: int = 0



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
    """Returns the current width of the 3D viewport's N-panel."""

    area = context.area
    if area is None:
        return 0.0

    for region in area.regions:
        if region.type == 'UI':
            return float(region.width) if region.width > 1 else 0.0

    return 0.0

def _load_texture_from_path(path: str, label: str):
    """Loads an image from disk and builds a GPU texture from it."""

    if not os.path.exists(path):
        print(f"[toast] Icon not found at {path} ({label}), toasts will draw without it.")
        return None, None

    image = bpy.data.images.load(path, check_existing=True)
    texture = gpu.texture.from_image(image)
    return image, texture

def _load_icons() -> None:
    """Load both the achievement icon and the level-up icon."""

    global _icon_image, _icon_texture, _levelup_icon_image, _levelup_icon_texture

    _icon_image, _icon_texture = _load_texture_from_path(ICON_PATH, "achievement")
    _levelup_icon_image, _levelup_icon_texture = _load_texture_from_path(LEVELUP_ICON_PATH, "level-up")

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

    # Shift left by however much space the N-panel is currently taking up
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

    font_id = 0

    for toast in _active_toasts:
        elapsed = now - toast["start"]
        if elapsed > DURATION:
            continue

        alpha = _compute_alpha(elapsed)
        kind = toast.get("kind", "achievement")

        if kind == "levelup":
            # -- Level-up toast: bigger, icon centered on top, two centered lines below --

            levelup_width = LEVELUP_BASE_WIDTH * scale
            levelup_icon_size = LEVELUP_BASE_ICON_SIZE * scale
            padding_top = LEVELUP_BASE_PADDING_TOP * scale
            padding_bottom = LEVELUP_BASE_PADDING_BOTTOM * scale
            icon_text_gap = LEVELUP_BASE_ICON_TEXT_GAP * scale
            line_gap = LEVELUP_BASE_LINE_GAP * scale
            top_font_size = round(LEVELUP_BASE_TOP_FONT_SIZE * scale)
            bottom_font_size = round(LEVELUP_BASE_BOTTOM_FONT_SIZE * scale)

            # Height is derived from its parts, rather than a separate
            # fixed constant, so it can't quietly drift out of sync with
            # the actual content as those parts get tuned
            levelup_height = (
                padding_top + levelup_icon_size + icon_text_gap
                + top_font_size + line_gap + bottom_font_size + padding_bottom
            )

            x = region.width - levelup_width - margin - n_panel_width
            box_center_x = x + levelup_width / 2

            verts = (
                (x, y), (x + levelup_width, y),
                (x + levelup_width, y + levelup_height), (x, y + levelup_height),
            )
            indices = ((0, 1, 2), (2, 3, 0))
            batch = batch_for_shader(_shader, 'TRIS', {"pos": verts}, indices=indices)
            _shader.bind()
            _shader.uniform_float("color", (0.08, 0.08, 0.08, 0.85 * alpha))
            batch.draw(_shader)

            # Icon, centered horizontally, anchored to the top of the box
            if _levelup_icon_texture is not None:
                icon_x = box_center_x - levelup_icon_size / 2
                icon_y = y + levelup_height - padding_top - levelup_icon_size

                icon_verts = (
                    (icon_x, icon_y), (icon_x + levelup_icon_size, icon_y),
                    (icon_x + levelup_icon_size, icon_y + levelup_icon_size), (icon_x, icon_y + levelup_icon_size),
                )
                uvs = ((0, 0), (1, 0), (1, 1), (0, 1))
                icon_batch = batch_for_shader(
                    _image_shader, 'TRI_FAN', {"pos": icon_verts, "texCoord": uvs}
                )
                _image_shader.bind()
                _image_shader.uniform_sampler("image", _levelup_icon_texture)
                _image_shader.uniform_float("color", (1.0, 1.0, 1.0, alpha))
                icon_batch.draw(_image_shader)

                text_top_y = icon_y - icon_text_gap - top_font_size
            else:
                text_top_y = y + levelup_height - padding_top - top_font_size

            # Show congratulations text
            top_text = toast["top_text"]
            blf.size(font_id, top_font_size)
            top_text_width, _ = blf.dimensions(font_id, top_text)
            blf.position(font_id, box_center_x - top_text_width / 2, text_top_y, 0)
            r1, g1, b1 = accent_color
            blf.color(font_id, r1, g1, b1, alpha)
            blf.draw(font_id, top_text)

            # Show level text
            bottom_text = toast["bottom_text"]
            bottom_text_y = text_top_y - line_gap - bottom_font_size
            blf.size(font_id, bottom_font_size)
            bottom_text_width, _ = blf.dimensions(font_id, bottom_text)
            blf.position(font_id, box_center_x - bottom_text_width / 2, bottom_text_y, 0)
            r2, g2, b2 = normal_color
            blf.color(font_id, r2, g2, b2, alpha)
            blf.draw(font_id, bottom_text)

            y += levelup_height + spacing
            continue

        # -- Achievement toast (unchanged) --

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
    """Display an achievement toast."""

    # Get the active toasts
    global _active_toasts

    # Add to active toasts
    _active_toasts.append({
        "kind": "achievement",
        "heading": heading,
        "name": name,
        "start": time.time() + start_offset,
    })

    # Register the toast ticker if it isn't already
    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=0.0, persistent=True)

    # Redraw UI
    _tag_redraw()

def show_levelup_toast(top_text: str, bottom_text: str, current_level: int, start_offset: float = 0.0) -> None:
    """Display a level-up toast."""

    global _active_toasts, _levelup_queue

    if current_level < _levelup_queue:
        return

    _active_toasts.append({
        "kind": "levelup",
        "top_text": top_text,
        "bottom_text": bottom_text,
        "start": time.time() + start_offset,
    })

    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=0.0, persistent=True)

    _levelup_queue = 0

    _tag_redraw()

def _on_unlock(instance: BlenderAchievement, current_level, levels_gained: int):
    """Shows toast on unlock, attached to the manager using manager.add_unlock_listener()."""

    show_toast(
        "You got an award!",
        instance.NAME
    )

    if levels_gained:
        _on_levelup(current_level)

def _on_levelup(current_level: int) -> None:
    """A queue for level up that cancels outdated level ups if the user earns multiple achievements at once that grant them enough EXP to level up both times."""

    global _levelup_queue

    if current_level < _levelup_queue:
        return

    _levelup_queue = current_level

    bpy.app.timers.register(
        lambda: show_levelup_toast(
            "Congratulations!",
            f"You reached level {current_level}!",
            current_level
        ),
        first_interval=2.0,
        persistent=True
    )



def register():
    """Register the toast and its shaders."""

    global _shader, _image_shader, _draw_handle

    _shader = gpu.shader.from_builtin("UNIFORM_COLOR")
    _image_shader = gpu.shader.from_builtin("IMAGE_COLOR")
    _draw_handle = bpy.types.SpaceView3D.draw_handler_add(_draw, (), 'WINDOW', 'POST_PIXEL')

    # Deferred - see _load_icons() docstring
    bpy.app.timers.register(_load_icons, first_interval=0.0, persistent=True)

    manager.add_unlock_listener(_on_unlock)

def unregister():
    """Unregister the toast and its shaders."""

    global _draw_handle, _icon_image, _icon_texture, _levelup_icon_image, _levelup_icon_texture

    if _draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, "WINDOW")
        _draw_handle = None

    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)

    if _icon_image is not None:
        bpy.data.images.remove(_icon_image)
        _icon_image = None
    _icon_texture = None

    if _levelup_icon_image is not None:
        bpy.data.images.remove(_levelup_icon_image)
        _levelup_icon_image = None
    _levelup_icon_texture = None

    _active_toasts.clear()