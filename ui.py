import os

import bpy
import bpy.utils.previews

from . import manager
from . import exp
from .achievements._base import AchievementKind

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

ICON_FILES = {
    "unlocked": os.path.join(ASSETS_DIR, "img", "default", "award.png"),
    "locked": os.path.join(ASSETS_DIR, "img", "default", "locked_award.png"),
}

# bpy.utils.previews.ImagePreviewCollection, populated by _load_icons()
_icons = None



def _load_icons() -> None:
    """Load and cache achievement icons."""

    global _icons

    pcoll = bpy.utils.previews.new()

    for key, path in ICON_FILES.items():
        
        if not os.path.exists(path):
            print(f"[UI] Icon not found at {path}, falling back to a builtin icon for '{key}'.")
            continue
        
        pcoll.load(key, path, "IMAGE")

    _icons = pcoll

def _icon_kwargs_for(instance) -> dict:
    """Returns the right kwarg (icon_value=... or icon=...) for a template_icon/label call."""

    key = "unlocked" if instance.unlocked else "locked"

    if _icons is not None and key in _icons:
        return {"icon_value": _icons[key].icon_id}

    return {"icon": "CHECKMARK" if instance.unlocked else "LOCKED"}

def _draw_achievement_box(layout, instance) -> None:
    """Draw one achievement's box - shared by both the Daily and Global sections."""

    box = layout.box()
    row = box.row()

    icon_col = row.column()
    icon_kwargs = _icon_kwargs_for(instance)
    if "icon_value" in icon_kwargs:
        icon_col.template_icon(scale=3.0, **icon_kwargs)
    else:
        icon_col.label(**icon_kwargs)

    text_col = row.column()
    text_col.label(text=instance.NAME)
    text_col.label(text=instance.DESC)

    status = instance.status_text()
    if status:
        text_col.label(text=status)



class ACHIEVEMENT_PT_panel(bpy.types.Panel):
    bl_label = "Achievements"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Achievements"

    def draw(self, context: bpy.types.Context):
        """Draw the N-panel tab."""

        layout = self.layout

        # EXP/level header
        threshold = exp.exp_required_for_level(exp.level)
        header = layout.box()
        header.label(text=f"Level {exp.level}")
        header.progress(
            factor=exp.get_progress_fraction(),
            text=f"{exp.exp}/{threshold}",
        )

        # Slit achievement instances into their repsective types
        instances = manager.get_instances().values()
        daily_instances = [i for i in instances if getattr(i, "KIND", None) == AchievementKind.DAILY]
        global_instances = [i for i in instances if getattr(i, "KIND", None) == AchievementKind.GLOBAL]

        # Collapsable section for daily achievements
        daily_header, daily_body = layout.panel("suzanne_awards_daily", default_closed=False)
        daily_header.label(text="Daily Awards")
        if daily_body is not None:
            for instance in daily_instances:
                _draw_achievement_box(daily_body, instance)

        # Collapsable section for global achievements
        global_header, global_body = layout.panel("suzanne_awards_global", default_closed=False)
        global_header.label(text="Global Awards")
        if global_body is not None:
            for instance in global_instances:
                _draw_achievement_box(global_body, instance)



classes = (ACHIEVEMENT_PT_panel,)



def register():
    """Register the N-panel."""

    for cls in classes:
        bpy.utils.register_class(cls)

    # Deferred - see _load_icons() docstring
    bpy.app.timers.register(_load_icons, first_interval=0.0, persistent=True)

def unregister():
    """Unregister the N-panel."""

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    if bpy.app.timers.is_registered(_load_icons):
        bpy.app.timers.unregister(_load_icons)

    if _icons is not None:
        bpy.utils.previews.remove(_icons)
        _icons = None